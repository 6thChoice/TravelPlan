import asyncio
import json
import re
import ast
import os
from typing import Optional, List, Dict, Any
from translations_backend import TRANSLATIONS
from fastapi import FastAPI, HTTPException, Response
import logging
import time
from functools import lru_cache
from contextlib import asynccontextmanager

# LangChain and LangGraph imports
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

# LightRAG imports
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.kg.shared_storage import initialize_share_data  # 新增导入

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
AZURE_API_VERSION = "2024-12-01-preview"
AZURE_DEPLOYMENT_NAME = "gpt-4o"
AZURE_ENDPOINT = "https://ai-14911520644664ai275106389756.openai.azure.com/"
AZURE_API_KEY = "5YzhcN3wCRnFORXYl9SPWpzb7RIPRQmew0V71y0chvR6g6j8hcFOJQQJ99BDACHYHv6XJ3w3AAAAACOGFi3L"
MAX_TOKENS = 4096
MCP_URL = "http://localhost:8000/sse"
WORKING_DIR = "/Volumes/extenal/lvyou_agent/trip_planing_agents/LightRAG/database"
os.environ['OPENAI_API_BASE'] = 'https://api.chatanywhere.tech/v1'
os.environ['OPENAI_API_KEY'] = 'sk-wuWBBLbmdMgyPkCHA8URU6Zv1BT2EkMWfAQWyppRm1u9jByJ'

# --- Global variables and initialization ---
model = AzureChatOpenAI(
    openai_api_version=AZURE_API_VERSION,
    deployment_name=AZURE_DEPLOYMENT_NAME,
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    max_tokens=MAX_TOKENS,
)
rag_instance: Optional[LightRAG] = None

def get_translation(key: str, lang: str, **kwargs) -> str:
    """Get translated prompt or message"""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text

# --- Lifecycle management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_instance
    logger.info("Initializing RAG on app startup")
    rag_instance = await initialize_rag_instance()
    if rag_instance:
        logger.info("RAG initialized successfully")
    else:
        logger.error("RAG initialization failed")
    yield
    logger.info("Cleaning up RAG resources on app shutdown")
    rag_instance = None

app = FastAPI(lifespan=lifespan)

# --- Data models (Pydantic) ---
from pydantic import BaseModel, Field
async def extract_locations_from_input(user_input: str, lang: str) -> Dict[str, List[str]]:
    """
    使用Agent从用户输入中提取景点、饭店和旅馆的详细地址
    """
    system_message = get_translation(
        "extract_locations_system",
        lang,
        default=(
            "You are an assistant specializing in Chinese place addressing. "
            "Before anything else, you **must** call the `search_from_web` tool to look up each place’s detailed address information. "
            "For every attraction, restaurant or hotel mentioned in the user’s text, "
            "you must supply a full address string that includes at least: city + "
            "district (or neighborhood) + street name + building number (if known). "
            "Output exactly one JSON object with three arrays—‘attractions’, ‘restaurants’, "
            "‘hotels’—each containing those full-address strings. "
            "If any detail is uncertain, omit that field rather than returning a generic name. "
            "Before returning, you **must** call the `geocode` tool on each place name to fetch its complete address."
            "Output format: {\"attractions\": [], \"restaurants\": [], \"hotels\": []}"
        )
    )
    human_message = get_translation(
        "extract_locations_human",
        lang,
        default="Extract the names of attractions, restaurants, and hotels from the following input: {input}",
        input=user_input
    )
    messages = [
        SystemMessage(system_message),
        HumanMessage(human_message),
    ]
    parser = JsonOutputParser()

    try:
        # 使用带工具的 Agent
        async with MultiServerMCPClient(
            {
                "gaode": {
                    "url": "http://localhost:8000/sse",
                    "transport": "sse",
                }
            }
        ) as client:
            tools = client.get_tools()
            agent = create_react_agent(model, tools)
            result = await agent.ainvoke({"messages": messages})
            # 从 agent 返回中取最后一条 AI 消息进行解析
            locations = parser.parse(result["messages"][-1].content)

        logger.info(f"Extracted locations: {locations}")
        return locations

    except Exception as e:
        logger.error(f"Failed to extract locations: {e}", exc_info=True)
        return {"attractions": [], "restaurants": [], "hotels": []}
    
class Attraction(BaseModel):
    name: str = Field(..., description="景点名称，可用于地理编码")
    address: Optional[str] = Field(None, description="景点详细地址（如有）")
    city: Optional[str] = Field(None, description="所属城市，可提高命中率")

class AttractionsRequest(BaseModel):
    attractions: List[Attraction] = Field(..., description="要查询的景点列表")

class CityInfo(BaseModel):
    name: str = Field(..., description="City name")
    days: int = Field(..., gt=0, description="Number of days")
    preferences: Optional[str] = Field("", description="User preferences for this city")

class PlanRequest(BaseModel):
    mode: str = Field(..., description="Travel mode ('单城市'/'single_city' or '多城市'/'multi_city')")
    user_input: str = Field(..., description="User's raw requirements text")
    city: Optional[str] = None
    days: Optional[int] = None
    cities: Optional[List[CityInfo]] = None
    selected_draft: Optional[Dict] = None
    feedback: Optional[List[str]] = None
    draft_index: Optional[int] = None
    final_feedback: Optional[List[str]] = None
    language: str = Field("zh", description="Response language ('zh' or 'en')")

class NotesRequest(BaseModel):
    travel_plan: str
    style_preference: str
    language: str = Field("zh", description="Response language ('zh' or 'en')")

# --- Helper functions ---
async def get_mcp_client_and_tools():
    try:
        client = MultiServerMCPClient({"gaode": {"url": MCP_URL, "transport": "sse"}})
        async with client:
            tools = client.get_tools()
            logger.info(f"🚀 MCP client initialized successfully, tools: {len(tools)}")
            return tools
    except Exception as e:
        logger.warning(f"😓 MCP client initialization failed: {e}", exc_info=True)
        return []

async def initialize_rag_instance():
    global rag_instance
    logger.info(f"🌟 Initializing LightRAG with working directory: {WORKING_DIR}")
    try:
        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=gpt_4o_mini_complete,
            embedding_func=EmbeddingFunc(
                embedding_dim=768,
                max_token_size=8192,
                func=lambda texts: ollama_embed(
                    texts, embed_model="nomic-embed-text", host="http://localhost:11434"
                ),
            ),
        )
        if not os.path.exists(WORKING_DIR):
            logger.warning(f"⚠️ LightRAG working directory '{WORKING_DIR}' does not exist. Creating it.")
            os.makedirs(WORKING_DIR)
        elif not os.path.isdir(WORKING_DIR):
            raise ValueError(f"😓 LightRAG working directory '{WORKING_DIR}' is not a directory.")
        # 跳过 initialize_share_data，依靠 LightRAG 内部初始化
        # 初始化 pipeline 状态
        logger.info("Starting pipeline status initialization...")
        await initialize_pipeline_status()
        # 添加 2 秒延迟以确保 Shared-Data 初始化
        logger.info("Waiting for Shared-Data initialization...")
        await asyncio.sleep(2)
        # 初始化存储
        logger.info("Starting storage initialization...")
        await rag.initialize_storages()
        rag_instance = rag
        logger.info("🎉 LightRAG initialized successfully.")
        return rag
    except Exception as e:
        logger.error(f"😓 LightRAG initialization failed: {e}", exc_info=True)
        return None

async def get_rag_context(query: str, lang: str) -> str:
    rag = await initialize_rag_instance()
    if not rag:
        return "[😓 RAG initialization failed, unable to fetch knowledge base]" if lang == "en" else "[😓 RAG 初始化失败，无法获取知识库参考]"
    try:
        response = await rag.aquery(
            query,
            param=QueryParam(mode="naive", only_need_context=False)
        )
        context = str(response)
        prefix = "📚 Related travel knowledge base reference" if lang == "en" else "📚 相关旅行知识库参考"
        return f"\n[{prefix}]\n{context}\n"
    except Exception as e:
        logger.error(f"😓 RAG query failed: {e}", exc_info=True)
        return "[😓 RAG query failed]" if lang == "en" else "[😓 RAG 查询时出错]"

async def get_location_info(address: str, city: str = "") -> dict:
    """Get location info using geocode tool"""
    try:
        async with MultiServerMCPClient(
                {
                    "gaode": {
                        "url": "http://localhost:8000/sse",
                        "transport": "sse",
                    }
                }
        ) as client:
            tools = client.get_tools()
            if not tools:
                raise ValueError("MCP service provided no tools")
            geocode_tool = next((tool for tool in tools if tool.name == "geocode"), None)
            location_info = await geocode_tool.ainvoke({"address": address, "city": city})
            print(f"Location info for {address} in {city}: {location_info}")
            return location_info
    except Exception as e:
        logger.error(f"😓 Geocode query failed: {e}", exc_info=True)
        return {"error": str(e)}

async def get_city_coordinates(city: str, lang: str = "zh", max_attempts: int = 5) -> dict:
    """
    获取指定城市的经纬度坐标，支持多次查询重试

    Args:
        city (str): 城市名称
        lang (str): 语言（'zh' 或 'en'），用于错误信息翻译
        max_attempts (int): 最大查询尝试次数，默认为 5

    Returns:
        dict: 包含 'latitude' 和 'longitude' 的字典

    Raises:
        HTTPException: 如果所有查询尝试失败或未找到坐标
    """
    logger.info(f"开始查询 {city} 的经纬度（语言：{lang}，最大尝试次数：{max_attempts}）")

    for attempt in range(1, max_attempts + 1):
        try:
            # 第一次尝试：带 city 上下文
            try:
                logger.info(f"尝试 {attempt}/{max_attempts}：带 city 上下文查询 {city}")
                location_info = await get_location_info(address=city, city=city)
            except Exception as e:
                logger.warning(f"尝试 {attempt}/{max_attempts}：带 city 上下文查询 {city} 失败: {e}. 重试不带 city 上下文。")
                location_info = await get_location_info(address=city, city="")

            # 检查是否返回错误
            if isinstance(location_info, dict) and "error" in location_info:
                logger.warning(f"尝试 {attempt}/{max_attempts}：查询 {city} 返回错误: {location_info['error']}")
                if attempt < max_attempts:
                    continue
                raise HTTPException(
                    status_code=500,
                    detail=get_translation(
                        "coordinates_error", lang, error=location_info["error"]
                    )
                )

            # 解析 JSON 或转换为 dict
            try:
                if isinstance(location_info, str):
                    location_info = json.loads(location_info)
                else:
                    location_info = dict(location_info)
            except Exception as e:
                logger.warning(f"尝试 {attempt}/{max_attempts}：解析 {city} 的返回数据失败: {e}")
                if attempt < max_attempts:
                    continue
                raise HTTPException(
                    status_code=500,
                    detail=get_translation(
                        "coordinates_error", lang, error="地理编码数据格式错误"
                    )
                )

            # 检查 location 字段
            if not isinstance(location_info, dict):
                logger.warning(f"尝试 {attempt}/{max_attempts}：{city} 的返回数据不是字典")
                if attempt < max_attempts:
                    continue
                raise HTTPException(
                    status_code=500,
                    detail=get_translation(
                        "coordinates_error", lang, error="地理编码数据格式错误"
                    )
                )

            if "location" in location_info:
                location = location_info["location"]
                try:
                    longitude, latitude = map(float, location.split(","))
                    logger.info(f"✅ 成功查询 {city} 经纬度：(纬度: {latitude}, 经度: {longitude})，尝试次数：{attempt}")
                    return {"latitude": latitude, "longitude": longitude}
                except ValueError as ve:
                    logger.warning(f"尝试 {attempt}/{max_attempts}：{city} 的经纬度格式错误: {ve}")
                    if attempt < max_attempts:
                        continue
                    raise HTTPException(
                        status_code=500,
                        detail=get_translation(
                            "coordinates_error", lang, error="经纬度格式错误"
                        )
                    )
            else:
                logger.warning(f"尝试 {attempt}/{max_attempts}：{city} 的返回数据缺少 location 字段")
                if attempt < max_attempts:
                    continue
                raise HTTPException(
                    status_code=404,
                    detail=get_translation("coordinates_unavailable", lang)
                )

        except Exception as e:
            logger.warning(f"尝试 {attempt}/{max_attempts}：查询 {city} 失败: {str(e)}")
            if attempt < max_attempts:
                continue
            raise HTTPException(
                status_code=500,
                detail=get_translation("coordinates_error", lang, error=str(e))
            )

    # 所有尝试失败
    raise HTTPException(
        status_code=500,
        detail=get_translation("coordinates_error", lang, error=f"查询 {city} 失败，已尝试 {max_attempts} 次")
    )

async def get_weather_info(city_name: str, lang: str) -> str:
    messages_weather = [
        SystemMessage(get_translation("weather_query", lang, city=city_name)),
        HumanMessage(get_translation("weather_human", lang, city=city_name)),
    ]
    weather_info = None
    for attempt in range(3):
        try:
            async with MultiServerMCPClient(
                    {
                        "gaode": {
                            "url": "http://localhost:8000/sse",
                            "transport": "sse",
                        }
                    }
            ) as client:
                tools = client.get_tools()
                logger.debug(f"Weather query attempt {attempt + 1}, available tools: {[tool.name for tool in tools]}")
                if not tools:
                    logger.warning(f"Weather query attempt {attempt + 1}, no tools available")
                    raise ValueError("MCP service provided no tools")
                temp_agent = create_react_agent(model, tools)
                response_weather = await temp_agent.ainvoke({"messages": messages_weather})
                weather_content = response_weather['messages'][-1].content
                if isinstance(weather_content, str) and weather_content.strip():
                    weather_info = weather_content
                    logger.info(f"🌤️ Weather info retrieved for {city_name}: {weather_info[:100]}...")
                    break
                else:
                    logger.warning(f"Weather query attempt {attempt + 1} returned empty or invalid response")
        except Exception as e:
            logger.error(f"😓 Weather query attempt {attempt + 1} failed: {e}", exc_info=True)
            if attempt == 2:
                weather_info = get_translation("weather_error", lang, error=str(e))
    if not weather_info:
        weather_info = get_translation("weather_unavailable", lang)
    return weather_info

async def generate_single_city_draft(city: str, days: int, user_input: str, style: str, weather_info: str,
                                     lang: str) -> Dict:
    prompt_key = f"draft_{style}"
    system_message = get_translation("draft_system", lang, city=city, days=days, user_input=user_input,
                                     weather=weather_info,
                                     prompt=get_translation(prompt_key, lang, user_input=user_input, city=city,
                                                            days=days, weather=weather_info))
    human_message = get_translation("draft_human", lang, num=style.capitalize(), city=city, days=days,
                                    user_input=user_input, weather=weather_info)
    messages = [
        SystemMessage(system_message),
        HumanMessage(human_message),
    ]
    try:
        response = await model.ainvoke(messages)
        content = response.content
        return {"content": content, "weather_info": weather_info}
    except Exception as e:
        logger.error(f"😓 Draft generation failed for style {style}: {e}", exc_info=True)
        return {"content": f"[Error generating {style} draft: {str(e)}]", "weather_info": weather_info}

async def generate_multi_city_draft(cities: List[CityInfo], user_input: str, style: str, weather_infos: Dict[str, str],
                                    lang: str) -> Dict:
    cities_str = "; ".join([
        f"{city.name} ({city.days} days, preferences: {city.preferences or 'none'})" if lang == "en" else f"{city.name} ({city.days}天，偏好：{city.preferences or '无'})"
        for city in cities])
    system_message = get_translation("multi_draft_system", lang)
    prompt = get_translation("multi_draft_prompt", lang, style=style, cities=cities_str)
    messages = [
        SystemMessage(system_message),
        HumanMessage(prompt),
    ]
    try:
        response = await model.ainvoke(messages)
        content = response.content
        return {"content": content, "weather_infos": weather_infos}
    except Exception as e:
        logger.error(f"😓 Multi-city draft generation failed for style {style}: {e}", exc_info=True)
        return {"content": f"[Error generating {style} draft: {str(e)}]", "weather_infos": weather_infos}

async def generate_single_city_final_plan(city: str, days: int, user_input: str, selected_draft: Dict,
                                          final_feedback: Optional[List[str]], lang: str) -> Dict:
    weather_info = selected_draft.get("weather_info", "No weather info available" if lang == "en" else "无天气信息")
    require = get_translation("single_require", lang, city=city, days=days, user_input=user_input)
    draft_reference = get_translation("draft_reference", lang, draft=selected_draft.get("content", ""))
    feedback_str = ""
    if final_feedback:
        feedback_str = get_translation("final_feedback", lang, feedback="\n".join(final_feedback))

# Step 1: Extract locations from user input
    locations = await extract_locations_from_input(selected_draft, lang)
    with open("locations.json", "w", encoding="utf-8") as f: json.dump(locations, f, ensure_ascii=False, indent=2)
    location_coordinates = {
        "attractions": {},
        "restaurants": {},
        "hotels": {}
    }

    # Step 2: Query coordinates for each location
    for category in ["attractions", "restaurants", "hotels"]:
        for name in locations[category]:
            try:
                location_info = await get_location_info(address=name, city=city)
                if isinstance(location_info, str):
                    # Attempt to parse JSON string
                    try:
                        location_info = json.loads(location_info)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON for {category} {name} in {city}: {location_info}")
                        location_info = {"error": "Invalid JSON format"}
                if isinstance(location_info, dict) and "location" in location_info:
                    longitude, latitude = map(float, location_info["location"].split(","))
                    location_coordinates[category][name] = {"latitude": latitude, "longitude": longitude}
                    logger.info(f"Successfully retrieved coordinates for {category} {name}: {latitude}, {longitude}")
                else:
                    location_coordinates[category][name] = {"error": "No coordinates found"}
                    logger.warning(f"No coordinates found for {category} {name}")
            except Exception as e:
                location_coordinates[category][name] = {"error": str(e)}
                logger.error(f"Failed to retrieve coordinates for {category} {name}: {e}")

    # Step 3: Get city coordinates
    city_coordinates = {}
    try:
        city_coordinates = await get_city_coordinates(city, lang)
        logger.info(f"Successfully retrieved coordinates for {city}: {city_coordinates}")
    except HTTPException as e:
        logger.error(f"😓 获取 {city} 经纬度失败: {e.detail}")
        city_coordinates = {"error": e.detail}
    except Exception as e:
        logger.error(f"😓 获取 {city} 经纬度时发生意外错误: {e}")
        city_coordinates = {"error": str(e)}
    # Step 2: Search for additional info
    search_system = get_translation("search_system", lang)
    search_query = get_translation("search_query", lang, city=city, days=days, user_input=user_input[:100])
    search_messages = [
        SystemMessage(search_system),
        HumanMessage(search_query),
    ]
    try:
        tools = await get_mcp_client_and_tools()
        search_agent = create_react_agent(model, tools)
        search_response = await search_agent.ainvoke({"messages": search_messages})
        search_info = search_response['messages'][-1].content
    except Exception as e:
        logger.error(f"😓 Search failed: {e}", exc_info=True)
        search_info = "[Search failed]" if lang == "en" else "[搜索失败]"

    # Step 3: Get RAG context
    rag_context = await get_rag_context(f"Travel tips for {city}", lang)

    # Step 4: Split tasks
    task_split_system = get_translation("task_split_system", lang)
    parser = JsonOutputParser()
    format_instructions = parser.get_format_instructions()
    task_split_prompt = get_translation("task_split_prompt", lang, require=require, rag_context=rag_context,
                                        info=search_info, format_instructions=format_instructions)
    task_messages = [
        SystemMessage(task_split_system),
        HumanMessage(task_split_prompt + draft_reference + feedback_str),
    ]
    try:
        task_response = await model.ainvoke(task_messages)
        task_output = parser.parse(task_response.content)
    except Exception as e:
        logger.error(f"😓 Task splitting failed: {e}", exc_info=True)
        task_output = {"view": "", "accommodation": "", "food": "", "traffic": ""}

    # Step 5: Generate detailed plans
    view_prompt = get_translation("view_prompt", lang, weather=weather_info, require=require,
                                  view_req=task_output.get("view", ""), rag_context=rag_context, info=search_info,
                                  days=days)
    view_response = await model.ainvoke([SystemMessage(""), HumanMessage(view_prompt + draft_reference + feedback_str)])
    view_plan = view_response.content

    food_prompt = get_translation("food_prompt", lang, require=require, food_req=task_output.get("food", ""),
                                  rag_context=rag_context, info=search_info, days=days)
    food_response = await model.ainvoke([SystemMessage(""), HumanMessage(food_prompt + draft_reference + feedback_str)])
    food_plan = food_response.content

    accommodation_prompt = get_translation("accommodation_prompt", lang, require=require,
                                           accommodation_req=task_output.get("accommodation", ""),
                                           rag_context=rag_context, info=search_info, days=days)
    accommodation_response = await model.ainvoke(
        [SystemMessage(""), HumanMessage(accommodation_prompt + draft_reference + feedback_str)])
    accommodation_plan = accommodation_response.content

    traffic_prompt = get_translation("traffic_prompt", lang, weather=weather_info, require=require,
                                     traffic_req=task_output.get("traffic", ""), rag_context=rag_context,
                                     info=search_info, view_plan=view_plan, accommodation_plan=accommodation_plan,
                                     days=days)
    traffic_response = await model.ainvoke(
        [SystemMessage(""), HumanMessage(traffic_prompt + draft_reference + feedback_str)])
    traffic_plan = traffic_response.content

    # Step 6: Summarize
    summary_prompt = get_translation("summary_prompt", lang, require=require, city=city, days=days, view_plan=view_plan,
                                     food_plan=food_plan, accommodation_plan=accommodation_plan,
                                     traffic_plan=traffic_plan, weather=weather_info, rag_context=rag_context)
    summary_response = await model.ainvoke(
        [SystemMessage(""), HumanMessage(summary_prompt + draft_reference + feedback_str)])
    summary = summary_response.content

    return {
        "summary": summary,
        "location_coordinates": location_coordinates,
        "city_coordinates": city_coordinates,
        "details": {
            "view_plan": view_plan,
            "food_plan": food_plan,
            "accommodation_plan": accommodation_plan,
            "traffic_plan": traffic_plan,
            "weather_info": weather_info
        }
    }

async def generate_multi_city_final_plan(cities: List[CityInfo], user_input: str, selected_draft: Dict,
                                         final_feedback: Optional[List[str]], lang: str) -> List[Dict]:
    final_plan = []
    weather_infos = selected_draft.get("weather_infos", {})
    feedback_str = ""
    if final_feedback:
        feedback_str = get_translation("final_feedback", lang, feedback="\n".join(final_feedback))
    draft_reference = get_translation("draft_reference", lang, draft=selected_draft.get("content", ""))

    for i, city_info in enumerate(cities):
        city = city_info.name
        days = city_info.days
        require = f"Preferences for {city}: {city_info.preferences or user_input}" if lang == "en" else f"{city}的偏好：{city_info.preferences or user_input}"
        weather_info = weather_infos.get(city, "No weather info available" if lang == "en" else "无天气信息")

# Step 1: Extract locations from user input
    locations = await extract_locations_from_input(selected_draft, lang)

    for i, city_info in enumerate(cities):
        city = city_info.name
        days = city_info.days
        require = f"Preferences for {city}: {city_info.preferences or user_input}" if lang == "en" else f"{city}的偏好：{city_info.preferences or user_input}"
        weather_info = weather_infos.get(city, "No weather info available" if lang == "en" else "无天气信息")

        # Step 2: Query coordinates for each location
        location_coordinates = {
            "attractions": {},
            "restaurants": {},
            "hotels": {}
        }
        for category in ["attractions", "restaurants", "hotels"]:
            for name in locations[category]:
                try:
                    location_info = await get_location_info(address=name, city=city)
                    if isinstance(location_info, str):
                        # Attempt to parse JSON string
                        try:
                            location_info = json.loads(location_info)
                        except json.JSONDecodeError:
                            logger.error(f"Failed to decode JSON for {category} {name} in {city}: {location_info}")
                            location_info = {"error": "Invalid JSON format"}
                    
                    if isinstance(location_info, dict) and "location" in location_info:
                        longitude, latitude = map(float, location_info["location"].split(","))
                        location_coordinates[category][name] = {"latitude": latitude, "longitude": longitude}
                        logger.info(f"Successfully retrieved coordinates for {category} {name} in {city}: {latitude}, {longitude}")
                    else:
                        location_coordinates[category][name] = {"error": "No coordinates found"}
                        logger.warning(f"No coordinates found for {category} {name} in {city}")
                except Exception as e:
                    location_coordinates[category][name] = {"error": str(e)}
                    logger.error(f"Failed to retrieve coordinates for {category} {name} in {city}: {e}")
        print(location_coordinates)
        # Step 3: Get city coordinates
        city_coordinates = {}
        try:
            city_coordinates = await get_city_coordinates(city, lang)
            logger.info(f"Successfully retrieved coordinates for {city}: {city_coordinates}")
        except HTTPException as e:
            logger.error(f"😓 获取 {city} 经纬度失败: {e.detail}")
            city_coordinates = {"error": e.detail}
        except Exception as e:
            logger.error(f"😓 获取 {city} 经纬度时发生意外错误: {e}")
            city_coordinates = {"error": str(e)}
        # Step 2: Search for additional info
        search_system = get_translation("search_system", lang)
        search_query = get_translation("search_query", lang, city=city, days=days, user_input=user_input[:100])
        search_messages = [
            SystemMessage(search_system),
            HumanMessage(search_query),
        ]
        try:
            tools = await get_mcp_client_and_tools()
            search_agent = create_react_agent(model, tools)
            search_response = await search_agent.ainvoke({"messages": search_messages})
            search_info = search_response['messages'][-1].content
        except Exception as e:
            logger.error(f"😓 Search failed for {city}: {e}", exc_info=True)
            search_info = "[Search failed]" if lang == "en" else "[搜索失败]"

        # Step 3: Get RAG context
        rag_context = await get_rag_context(f"Travel tips for {city}", lang)

        # Step 4: Split tasks
        task_split_system = get_translation("task_split_system", lang)
        parser = JsonOutputParser()
        format_instructions = parser.get_format_instructions()
        task_split_prompt = get_translation("task_split_prompt", lang, require=require, rag_context=rag_context,
                                            info=search_info, format_instructions=format_instructions)
        task_messages = [
            SystemMessage(task_split_system),
            HumanMessage(task_split_prompt + draft_reference + feedback_str),
        ]
        try:
            task_response = await model.ainvoke(task_messages)
            task_output = parser.parse(task_response.content)
        except Exception as e:
            logger.error(f"😓 Task splitting failed for {city}: {e}", exc_info=True)
            task_output = {"view": "", "accommodation": "", "food": "", "traffic": ""}

        # Step 5: Generate detailed plans
        view_prompt = get_translation("view_prompt", lang, weather=weather_info, require=require,
                                      view_req=task_output.get("view", ""), rag_context=rag_context, info=search_info,
                                      days=days)
        view_response = await model.ainvoke(
            [SystemMessage(""), HumanMessage(view_prompt + draft_reference + feedback_str)])
        view_plan = view_response.content

        food_prompt = get_translation("food_prompt", lang, require=require, food_req=task_output.get("food", ""),
                                      rag_context=rag_context, info=search_info, days=days)
        food_response = await model.ainvoke(
            [SystemMessage(""), HumanMessage(food_prompt + draft_reference + feedback_str)])
        food_plan = food_response.content

        accommodation_prompt = get_translation("accommodation_prompt", lang, require=require,
                                               accommodation_req=task_output.get("accommodation", ""),
                                               rag_context=rag_context, info=search_info, days=days)
        accommodation_response = await model.ainvoke(
            [SystemMessage(""), HumanMessage(accommodation_prompt + draft_reference + feedback_str)])
        accommodation_plan = accommodation_response.content

        traffic_prompt = get_translation("traffic_prompt", lang, weather=weather_info, require=require,
                                         traffic_req=task_output.get("traffic", ""), rag_context=rag_context,
                                         info=search_info, view_plan=view_plan, accommodation_plan=accommodation_plan,
                                         days=days)
        traffic_response = await model.ainvoke(
            [SystemMessage(""), HumanMessage(traffic_prompt + draft_reference + feedback_str)])
        traffic_plan = traffic_response.content

        # Step 6: Summarize
        summary_prompt = get_translation("summary_prompt", lang, require=require, city=city, days=days,
                                         view_plan=view_plan, food_plan=food_plan,
                                         accommodation_plan=accommodation_plan, traffic_plan=traffic_plan,
                                         weather=weather_info, rag_context=rag_context)
        summary_response = await model.ainvoke(
            [SystemMessage(""), HumanMessage(summary_prompt + draft_reference + feedback_str)])
        summary = summary_response.content

        # Step 7: Inter-city transport (if not the first city)
        inter_city_traffic = ""
        if i > 0:
            prev_city = cities[i - 1].name
            transport_system = get_translation("transport_system", lang)
            transport_prompt = get_translation("transport_prompt", lang, prev_city=prev_city, city=city,
                                               user_input=user_input)
            transport_messages = [
                SystemMessage(transport_system),
                HumanMessage(transport_prompt),
            ]
            try:
                tools = await get_mcp_client_and_tools()
                transport_agent = create_react_agent(model, tools)
                transport_response = await transport_agent.ainvoke({"messages": transport_messages})
                inter_city_traffic = transport_response['messages'][-1].content
            except Exception as e:
                logger.error(f"😓 Inter-city transport query failed from {prev_city} to {city}: {e}", exc_info=True)
                inter_city_traffic = f"[Error querying transport from {prev_city} to {city}]" if lang == "en" else f"[查询从{prev_city}到{city}的交通出错]"

        final_plan.append({
            "city": city,
            "days": days,
            "city_coordinates": city_coordinates,
            "location_coordinates": location_coordinates,
            "plan": {
                "summary": summary,
                "details": {
                    "view_plan": view_plan,
                    "food_plan": food_plan,
                    "accommodation_plan": accommodation_plan,
                    "traffic_plan": traffic_plan,
                    "weather_info": weather_info
                }
            },
            "inter_city_traffic": inter_city_traffic
        })

    return final_plan

async def refresh_draft(request: PlanRequest, lang: str) -> Dict:
    style = ["sport", "culture", "food"][request.draft_index]
    # 将 feedback 组成字符串
    feedback_str = ""
    if request.feedback:
        feedback_str = get_translation("final_feedback", lang, feedback="\n".join(request.feedback))
    # 追加到 user_input
    updated_user_input = f"{request.user_input}\n{feedback_str}" if feedback_str else request.user_input

    if request.mode in ["single_city", "单城市"]:
        weather_info = await get_weather_info(request.city, lang)
        draft = await generate_single_city_draft(
            city=request.city,
            days=request.days,
            user_input=updated_user_input,  # 使用更新后的 user_input
            style=style,
            weather_info=weather_info,
            lang=lang
        )
    else:
        weather_infos = {}
        for city_info in request.cities:
            weather_infos[city_info.name] = await get_weather_info(city_info.name, lang)
        draft = await generate_multi_city_draft(
            cities=request.cities,
            user_input=updated_user_input,  # 使用更新后的 user_input
            style=style,
            weather_infos=weather_infos,
            lang=lang
        )
    return draft
# --- API Endpoints ---
@app.post("/plan")
async def generate_plan(request: PlanRequest):
    lang = request.language
    logger.info(
        f"📩 Received plan request: mode={request.mode}, user_input={request.user_input[:50]}..., language={lang}")

    # Validate mode
    valid_modes = ["single_city", "multi_city", "单城市", "多城市"]
    if request.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=get_translation("invalid_mode", lang, mode=request.mode))

    # Handle draft refresh
    if request.feedback and request.draft_index is not None:
        if not (0 <= request.draft_index < 3):
            raise HTTPException(status_code=400,
                                detail=get_translation("invalid_draft_index", lang, index=request.draft_index, max=2))
        draft = await refresh_draft(request, lang)
        return {"drafts": draft}

    # Validate inputs
    if request.mode in ["single_city", "单城市"]:
        if not request.city or not request.days or request.days <= 0:
            raise HTTPException(status_code=400, detail=get_translation("single_city_error", lang))
    else:
        if not request.cities or not all(city.name and city.days > 0 for city in request.cities):
            raise HTTPException(status_code=400, detail=get_translation("multi_city_error", lang))

    # Handle final plan with selected draft or feedback
    if request.selected_draft or request.final_feedback:
        if request.mode in ["single_city", "单城市"]:
            final_plan = await generate_single_city_final_plan(
                city=request.city,
                days=request.days,
                user_input=request.user_input,
                selected_draft=request.selected_draft or {},
                final_feedback=request.final_feedback,
                lang=lang
            )
            return {"final_plan": final_plan}
        else:
            final_plan = await generate_multi_city_final_plan(
                cities=request.cities,
                user_input=request.user_input,
                selected_draft=request.selected_draft or {},
                final_feedback=request.final_feedback,
                lang=lang
            )
            return {"final_plan": final_plan}

    # Generate drafts
    if request.mode in ["single_city", "单城市"]:
        weather_info = await get_weather_info(request.city, lang)
        drafts = await asyncio.gather(
            generate_single_city_draft(request.city, request.days, request.user_input, "sport", weather_info, lang),
            generate_single_city_draft(request.city, request.days, request.user_input, "culture", weather_info, lang),
            generate_single_city_draft(request.city, request.days, request.user_input, "food", weather_info, lang),
        )
    else:
        weather_infos = {}
        for city_info in request.cities:
            weather_infos[city_info.name] = await get_weather_info(city_info.name, lang)
        drafts = await asyncio.gather(
            generate_multi_city_draft(request.cities, request.user_input, "sport", weather_infos, lang),
            generate_multi_city_draft(request.cities, request.user_input, "culture", weather_infos, lang),
            generate_multi_city_draft(request.cities, request.user_input, "food", weather_infos, lang),
        )

    return {"drafts": list(drafts)}

@app.post("/notes")
async def generate_travel_notes(request: NotesRequest):
    lang = request.language
    style = request.style_preference.lower()
    logger.info(f"📝 Generating travel notes with style: {style}, language={lang}")

    # Parse travel plan to extract key details for structured prompting
    try:
        travel_plan_dict = json.loads(request.travel_plan) if request.travel_plan.startswith(
            '[') or request.travel_plan.startswith('{') else request.travel_plan
    except json.JSONDecodeError:
        travel_plan_dict = request.travel_plan

    formatted_plan = ""
    if isinstance(travel_plan_dict, dict) and "summary" in travel_plan_dict:
        # Single city plan
        formatted_plan = f"**City**: {travel_plan_dict.get('city', 'Unknown')} ({travel_plan_dict.get('days', 'Unknown')} days)\n"
        formatted_plan += f"**Summary**: {travel_plan_dict['summary']}\n"
        details = travel_plan_dict.get("details", {})
        formatted_plan += f"**Attractions**: {details.get('view_plan', 'No attractions provided')}\n"
        formatted_plan += f"**Dining**: {details.get('food_plan', 'No dining provided')}\n"
        formatted_plan += f"**Accommodation**: {details.get('accommodation_plan', 'No accommodation provided')}\n"
        formatted_plan += f"**Transport**: {details.get('traffic_plan', 'No transport provided')}\n"
        formatted_plan += f"**Weather**: {details.get('weather_info', 'No weather info')}\n"
    elif isinstance(travel_plan_dict, list):
        # Multi city plan
        for i, city_plan in enumerate(travel_plan_dict):
            formatted_plan += f"**City {i + 1}**: {city_plan.get('city', 'Unknown')} ({city_plan.get('days', 'Unknown')} days)\n"
            if city_plan.get("plan"):
                formatted_plan += f"**Summary**: {city_plan['plan'].get('summary', 'No summary provided')}\n"
                details = city_plan["plan"].get("details", {})
                formatted_plan += f"**Attractions**: {details.get('view_plan', 'No attractions provided')}\n"
                formatted_plan += f"**Dining**: {details.get('food_plan', 'No dining provided')}\n"
                formatted_plan += f"**Accommodation**: {details.get('accommodation_plan', 'No accommodation provided')}\n"
                formatted_plan += f"**Transport**: {details.get('traffic_plan', 'No transport provided')}\n"
                formatted_plan += f"**Weather**: {details.get('weather_info', 'No weather info')}\n"
            if city_plan.get("inter_city_traffic"):
                formatted_plan += f"**Inter-City Transport**: {city_plan['inter_city_traffic']}\n"
            formatted_plan += "\n"
    else:
        # Fallback to raw plan
        formatted_plan = str(travel_plan_dict)

    # Construct prompt
    system_message = get_translation("notes_system", lang, style=style)
    human_message = get_translation("notes_human", lang, plan=formatted_plan)
    messages = [
        SystemMessage(system_message),
        HumanMessage(human_message),
    ]

    try:
        response = await model.ainvoke(messages)
        notes = response.content
        # Post-process to ensure Xiaohongshu style
        if style == "xiaohongshu":
            notes = notes.replace("\n\n", "\n\n🌟 ")  # Add emojis between paragraphs
            notes = f"📖 **{'我的旅行日记' if lang == 'zh' else 'My Travel Diary'}** 🌍\n\n{notes}"
        return {"notes": notes}
    except Exception as e:
        logger.error(f"😓 Notes generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Notes generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)