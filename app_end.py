import streamlit as st
import requests
import json
import logging
import datetime
import os
from translations_app import TRANSLATIONS
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Optional
import re
# Add map-related imports
from streamlit_folium import st_folium
import folium

# Configure logging 📜
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration 🐶
st.set_page_config(page_icon="🐶", layout="wide")
            # min-height: 100vh; /* 确保页面高度至少为视口高度 */
            # height: 100%; /* 确保 .stApp 高度填充整个父容器 */
            # display: flex;
            # flex-direction: column;
# Custom CSS and JavaScript with added .stFolium style
st.markdown("""
<style>
    .stApp {
            background-color: rgba(255, 250, 205, 0.7); /* Light yellow background */
    }
    .appview-container, .main > div {
        background-color: transparent !important;
    }
    .card {
        border: 2px solid #d4a017;
        border-radius: 12px;
        padding: 20px;
        margin: 15px;
        background-color: #fff8e1;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card-title {
        font-size: 1.4em;
        font-weight: bold;
        margin-bottom: 15px;
        color: #d4a017;
        text-align: center;
    }
    .card-content {
        flex-grow: 1;
        margin-bottom: 15px;
        font-size: 1.1em;
    }
    .stButton > button {
        width: 100%;
        margin-top: 10px;
        background-color: #f7c948;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1.1em;
        padding: 10px;
    }
    .stButton > button:hover {
        background-color: #e0b428;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    .sidebar .sidebar-content {
        background-color: #ffe4b5 !important;
        color: #333;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 3px 3px 8px #d4a017;
    }
    .sidebar h2, .sidebar h3, .sidebar h4, .sidebar h5, .sidebar h6, .sidebar p, .sidebar label {
        color: #54450d;
    }
    h1 {
        color: #d4a017;
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        text-shadow: 2px 2px 4px #ffffff, -2px -2px 4px #ffffff;
    }
    h2 {
        color: #e0b428;
        text-align: center;
        text-shadow: 2px 2px 4px #ffffff, -2px -2px 4px #ffffff;
    }
    .stTextArea > div > div > textarea {
        background-color: #fff8e1;
        border: 2px solid #d4a017;
        border-radius: 8px;
        font-size: 1.1em;
    }
    .stTextInput > div > div > input {
        background-color: #fff8e1;
        border: 2px solid #d4a017;
        border-radius: 8px;
    }
    .stNumberInput > div > div > input {
        background-color: #fff8e1;
        border: 2px solid #d4a017;
        border-radius: 8px;
    }
    .xiaohongshu-card {
        background-color: #fff0f5;
        border: 2px solid #ff69b4;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease;
    }
    .xiaohongshu-card:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    .xiaohongshu-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(rgba(255, 245, 247, 0.7), rgba(255, 245, 247, 0.7)), url('https://via.placeholder.com/300x300.png?text=Travel+Memory');
        background-size: cover;
        background-position: center;
        opacity: 0.8;
        z-index: 0;
    }
    .xiaohongshu-card-content {
        position: relative;
        z-index: 1;
        color: #333;
        font-size: 1.1em;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        padding: 10px;
        max-height: 260px;
        width: 100%;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .xiaohongshu-card-content::-webkit-scrollbar {
        width: 5px;
    }
    .xiaohongshu-card-content::-webkit-scrollbar-thumb {
        background: #ff69b4;
        border-radius: 10px;
    }
    /* 弹窗样式 */
    .popup-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .popup-content {
        background-color: #fff8e1;
        border: 2px solid #d4a017;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        max-width: 400px;
        width: 90%;
    }
    .popup-content p {
        font-size: 1.2em;
        color: #d4a017;
        margin-bottom: 20px;
    }
    .popup-content button {
        background-color: #f7c948;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1.1em;
        cursor: pointer;
    }
    .popup-content button:hover {
        background-color: #e0b428;
    }
    .popup-content button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    /* 加载动画 */
    .loader {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #d4a017;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    /* 成功提示框 */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
        text-align: center;
        font-size: 1.1em;
    }
    /* Add Folium map styling */
    .stFolium {
        width: 100% !important;
        aspect-ratio: 1 / 1;
        border: 2px solid #d4a017;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin: 15px 0;
    }
</style>
<script>
    // 禁用页面滚动
    function disableScroll() {
        document.body.style.overflow = 'hidden';
    }
    // 启用页面滚动并滚动到顶部
    function enableScroll() {
        document.body.style.overflow = '';
        window.scrollTo(0, 0);
    }
    .stTextInput, .stNumberInput {
        height: 50px;
        display: flex;
        align-items: center;
    }
    .stTextInput > div, .stNumberInput > div {
        width: 100%;
    }
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        height: 40px;
        padding: 8px;
        box-sizing: border-box;
    }
</script>
""", unsafe_allow_html=True)

def get_translation(key: str, lang: str, **kwargs) -> str:
    """获取翻译文本，支持格式化，并处理加粗标记"""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)
    try:
        formatted_text = text.format(**kwargs)
    except (KeyError, ValueError):
        formatted_text = text
    # 修改：对翻译文本中的 ** 加粗标记进行处理，转换为 HTML <strong> 标签
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_text)

def generate_user_input(city_inputs: list, lang: str) -> str:
    result = []
    if city_inputs:
        city_details = []
        for city in city_inputs:
            name = city.get("name", get_translation("city_name", lang).split(" ")[0])
            days = city.get("days", 1)
            preferences = city.get("preferences", get_translation("preferences_placeholder", lang).split("，")[0])
            if not preferences.strip():
                preferences = get_translation("preferences_placeholder", lang).split("，")[0]
            city_details.append(f"{name} ({days} days, preferences: {preferences})" if lang == "en" else
                                f"{name} ({days}天，偏好：{preferences})")
        cities_text = "; ".join(city_details)
        result.append(f"{'Travel cities' if lang == 'en' else '行程城市'}: {cities_text}")
    if not result:
        return "Multi-city trip: No specific requirements 🌍" if lang == "en" else "多城市行程：无具体需求 🌍"
    return ". ".join(result) + "."

def icon(emoji: str):
    st.markdown(
        f'<span style="font-size: 80px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    return session

# Add create_map function from app_map.py
def create_map(final_plan, lang: str) -> folium.Map:
    """
    Create a Folium map with markers for city and location coordinates
    Args:
        final_plan: The final plan data (dict for single city, list for multi-city)
        lang: Language ('zh' or 'en')
    Returns:
        folium.Map: A Folium map with markers for cities and locations
    """
    default_center = [0, 0]
    zoom_start = 2
    valid_coordinates = []

    # Determine if single or multi-city mode
    is_single_city = isinstance(final_plan, dict)
    plans = [final_plan] if is_single_city else final_plan

    # Collect all coordinates
    for plan in plans:
        city_name = plan.get('city', 'Unknown') if not is_single_city else st.session_state.city
        # City coordinates
        city_coords = plan.get('city_coordinates', {})
        if "latitude" in city_coords and "longitude" in city_coords:
            try:
                lat = float(city_coords["latitude"])
                lon = float(city_coords["longitude"])
                valid_coordinates.append((lat, lon, city_name, "city"))
            except (ValueError, TypeError):
                logger.warning(f"Invalid city coordinates for {city_name}: {city_coords}")
                continue

        # Location coordinates (attractions, restaurants, hotels)
        location_coords = plan.get('location_coordinates', {})
        for category in ["attractions", "restaurants", "hotels"]:
            for name, coords in location_coords.get(category, {}).items():
                if "latitude" in coords and "longitude" in coords:
                    try:
                        lat = float(coords["latitude"])
                        lon = float(coords["longitude"])
                        valid_coordinates.append((lat, lon, name, category))
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid coordinates for {category} {name} in {city_name}: {coords}")
                        continue
                elif "error" in coords:
                    logger.warning(f"Coordinates error for {category} {name} in {city_name}: {coords['error']}")

    # Create map
    if not valid_coordinates:
        m = folium.Map(location=default_center, zoom_start=zoom_start)
        st.warning(get_translation("no_valid_coordinates", lang))
        return m

    if len(valid_coordinates) == 1:
        center = [valid_coordinates[0][0], valid_coordinates[0][1]]
        zoom_start = 10 if valid_coordinates[0][3] == "city" else 15
    else:
        avg_lat = sum(coord[0] for coord in valid_coordinates) / len(valid_coordinates)
        avg_lon = sum(coord[1] for coord in valid_coordinates) / len(valid_coordinates)
        center = [avg_lat, avg_lon]
        zoom_start = 5 if is_single_city else 4

    m = folium.Map(location=center, zoom_start=zoom_start)

    # Add markers with different styles for cities and locations
    for lat, lon, name, category in valid_coordinates:
        if category == "city":
            icon = folium.Icon(color="blue", icon="star", prefix="fa")
            tooltip = get_translation("city_marker", lang, city=name)
            popup = f"<strong>{name}</strong><br>{get_translation('city', lang)}"
        elif category == "attractions":
            icon = folium.Icon(color="green", icon="camera", prefix="fa")
            tooltip = get_translation("attraction_marker", lang, name=name)
            popup = f"<strong>{name}</strong><br>{get_translation('attraction', lang)}"
        elif category == "restaurants":
            icon = folium.Icon(color="red", icon="cutlery", prefix="fa")
            tooltip = get_translation("restaurant_marker", lang, name=name)
            popup = f"<strong>{name}</strong><br>{get_translation('restaurant', lang)}"
        else:  # hotels
            icon = folium.Icon(color="purple", icon="bed", prefix="fa")
            tooltip = get_translation("hotel_marker", lang, name=name)
            popup = f"<strong>{name}</strong><br>{get_translation('hotel', lang)}"

        folium.Marker(
            [lat, lon],
            popup=popup,
            tooltip=tooltip,
            icon=icon
        ).add_to(m)

    # Fit map to bounds if there are multiple points
    if len(valid_coordinates) > 1:
        bounds = [
            [min(coord[0] for coord in valid_coordinates), min(coord[1] for coord in valid_coordinates)],
            [max(coord[0] for coord in valid_coordinates), max(coord[1] for coord in valid_coordinates)]
        ]
        m.fit_bounds(bounds)

    return m

def convert_markdown_headers(text: str) -> str:
    """将Markdown标题（#）和加粗（**）转换为HTML标签"""
    if not text:
        return text
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            processed_lines.append(f'<h{level}>{content}</h{level}>')
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines)

def select_draft(draft, lang: str, plan_number: int):
    try:
        session = create_session()
        logger.info(f"📩 Sending draft selection request: draft={draft['content'][:50]}...")
        if st.session_state.mode in ["单城市", "single_city"]:
            request_data = {
                "mode": "single_city" if lang == "en" else "单城市",
                "city": st.session_state.city,
                "days": st.session_state.days,
                "user_input": st.session_state.submitted_user_input or "",
                "selected_draft": draft,
                "language": lang
            }
        else:
            request_data = {
                "mode": "multi_city" if lang == "en" else "多城市",
                "cities": st.session_state.city_inputs,
                "user_input": st.session_state.submitted_user_input or "",
                "selected_draft": draft,
                "language": lang
            }
        response = session.post(
            "http://localhost:8001/plan",
            json=request_data,
            timeout=300
        )
        logger.info(f"📬 Received response: status={response.status_code}, content={response.text}")
        st.session_state.last_response = response.text
        response_data = response.json()
        if response.status_code != 200:
            st.error(get_translation("backend_error", lang, code=response.status_code,
                                     detail=response_data.get('detail', response.text)))
            return
        if response_data.get("error"):
            st.error(get_translation("backend_error", lang, code=response.status_code, detail=response_data['error']))
            return
        if response_data.get("final_plan"):
            st.session_state.final_plan = response_data["final_plan"]
            if st.session_state.mode in ["多城市", "multi_city"]:
                st.session_state.cities = response_data["final_plan"]
            st.session_state.stage = "final"
            st.session_state.show_success_message = True
            st.rerun()
        else:
            st.error(get_translation("invalid_response", lang, response=json.dumps(response_data, ensure_ascii=False)))
            logger.error(f"Invalid backend response: {response.text}")
    except requests.Timeout:
        st.error(get_translation("timeout_error", lang))
        logger.error("Request timed out", exc_info=True)
    except requests.ConnectionError:
        st.error(get_translation("connection_error", lang))
        logger.error("Cannot connect to backend", exc_info=True)
    except requests.RequestException as e:
        st.error(get_translation("request_error", lang, error=str(e)))
        logger.error(f"Request failed: {str(e)}", exc_info=True)
    except ValueError as e:
        st.error(get_translation("parse_error", lang, error=str(e), response=st.session_state.last_response))
        logger.error(f"Response parsing failed: {str(e)}", exc_info=True)
    finally:
        st.session_state.show_popup = False
        st.markdown(
            """
            <script>
                enableScroll();
            </script>
            """,
            unsafe_allow_html=True
        )

def refresh_draft(draft: Dict, draft_index: int, lang: str):
    """根据用户反馈刷新指定草稿"""
    if not st.session_state.get("submitted_user_input"):
        st.error(get_translation("no_input", lang))
        return

    feedback_key = f"temp_feedback_{draft_index + 1}"
    current_feedback = st.session_state.get(feedback_key, "").strip()

    if not current_feedback:
        st.warning(get_translation("no_feedback", lang))
        return

    feedback_entry = {
        "text": current_feedback,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.session_state.draft_feedbacks[draft_index].append(feedback_entry)
    logger.info(f"📝 Added feedback to draft {draft_index + 1}: {current_feedback[:50]}...")

    request_data = {
        "mode": "single_city" if lang == "en" and st.session_state.mode in ["单城市", "single_city"] else
                "multi_city" if lang == "en" and st.session_state.mode in ["多城市", "multi_city"] else
                "单城市" if st.session_state.mode in ["单城市", "single_city"] else "多城市",
        "user_input": st.session_state.submitted_user_input,
        "feedback": [entry["text"] for entry in st.session_state.draft_feedbacks[draft_index]],
        "draft_index": draft_index,
        "language": lang
    }
    if st.session_state.mode in ["单城市", "single_city"]:
        request_data["city"] = st.session_state.city
        request_data["days"] = st.session_state.days
    else:
        request_data["cities"] = [
            {"name": city["name"], "days": city["days"], "preferences": city.get("preferences", "")}
            for city in st.session_state.city_inputs
        ]

    try:
        session = create_session()
        response = session.post("http://localhost:8001/plan", json=request_data, timeout=600)
        response.raise_for_status()
        response_data = response.json()

        if "drafts" in response_data:
            if isinstance(response_data["drafts"], list) and len(response_data["drafts"]) > draft_index:
                st.session_state.drafts[draft_index] = response_data["drafts"][draft_index]
            else:
                st.session_state.drafts[draft_index] = response_data["drafts"]
            st.session_state[f"clear_{feedback_key}"] = True
            st.session_state.show_success_message = True
            st.rerun()
        else:
            st.error(get_translation("refresh_failed", lang, error="No draft data received"))
    except requests.RequestException as e:
        st.error(get_translation("refresh_failed", lang, error=str(e)))
        logger.error(f"Refresh draft failed: {str(e)}", exc_info=True)
    finally:
        st.session_state.show_popup = False
        st.markdown(
            """
            <script>
                enableScroll();
            </script>
            """,
            unsafe_allow_html=True
        )

def submit_final_feedback(lang: str):
    """提交最终方案的反馈并触发重新生成"""
    if not st.session_state.get("submitted_user_input"):
        st.error(get_translation("no_input", lang))
        return

    feedback_key = "temp_final_feedback"
    current_feedback = st.session_state.get(feedback_key, "").strip()

    if not current_feedback:
        st.warning(get_translation("no_feedback", lang))
        return

    feedback_entry = {
        "text": current_feedback,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.session_state.final_feedback_history.append(feedback_entry)
    logger.info(f"📝 Added final plan feedback: {current_feedback[:50]}...")

    request_data = {
        "mode": "single_city" if lang == "en" and st.session_state.mode in ["单城市", "single_city"] else
                "multi_city" if lang == "en" and st.session_state.mode in ["多城市", "multi_city"] else
                "单城市" if st.session_state.mode in ["单城市", "single_city"] else "多城市",
        "user_input": st.session_state.submitted_user_input,
        "final_feedback": [entry["text"] for entry in st.session_state.final_feedback_history],
        "language": lang
    }
    if st.session_state.mode in ["单城市", "single_city"]:
        request_data["city"] = st.session_state.city
        request_data["days"] = st.session_state.days
        request_data["selected_draft"] = st.session_state.drafts[0] if st.session_state.drafts else None
    else:
        request_data["cities"] = [
            {"name": city["name"], "days": city["days"], "preferences": city.get("preferences", "")}
            for city in st.session_state.city_inputs
        ]
        request_data["selected_draft"] = st.session_state.drafts[0] if st.session_state.drafts else None

    try:
        session = create_session()
        response = session.post("http://localhost:8001/plan", json=request_data, timeout=600)
        response.raise_for_status()
        response_data = response.json()

        if "final_plan" in response_data:
            st.session_state.final_plan = response_data["final_plan"]
            if st.session_state.mode in ["多城市", "multi_city"]:
                st.session_state.cities = response_data["final_plan"]
            st.session_state[f"clear_{feedback_key}"] = True
            st.session_state.show_success_message = True
            st.session_state.travel_notes = None
            st.balloons()
            st.rerun()
        else:
            st.error(get_translation("refresh_failed", lang, error="No final plan data received"))
    except requests.RequestException as e:
        st.error(get_translation("refresh_failed", lang, error=str(e)))
        logger.error(f"Update final plan failed: {str(e)}", exc_info=True)
    finally:
        st.session_state.show_popup = False
        st.markdown(
            """
            <script>
                enableScroll();
            </script>
            """,
            unsafe_allow_html=True
        )

def generate_travel_notes(lang: str):
    """通过调用后端 /notes 端点生成小红书风格的旅游文案"""
    try:
        session = create_session()
        request_data = {
            "travel_plan": json.dumps(st.session_state.final_plan, ensure_ascii=False),
            "style_preference": "xiaohongshu",
            "language": lang
        }
        logger.info(f"📩 Sending travel notes request: plan={request_data['travel_plan'][:50]}...")
        response = session.post(
            "http://localhost:8001/notes",
            json=request_data,
            timeout=600
        )
        logger.info(f"📬 Received notes response: status={response.status_code}, content={response.text}")
        response_data = response.json()
        if response.status_code != 200:
            st.error(get_translation("backend_error", lang, code=response.status_code,
                                     detail=response_data.get('detail', response.text)))
            return
        if response_data.get("notes"):
            st.session_state.travel_notes = response_data["notes"]
            st.session_state.show_success_message = True
            st.session_state.show_popup = False
            st.rerun()
        else:
            st.error(get_translation("invalid_response", lang, response=json.dumps(response_data, ensure_ascii=False)))
    except requests.Timeout:
        st.error(get_translation("timeout_error", lang))
        logger.error("Notes request timed out", exc_info=True)
    except requests.ConnectionError:
        st.error(get_translation("connection_error", lang))
        logger.error("Cannot connect to backend for notes", exc_info=True)
    except requests.RequestException as e:
        st.error(get_translation("request_error", lang, error=str(e)))
        logger.error(f"Notes request failed: {str(e)}", exc_info=True)
    except ValueError as e:
        st.error(get_translation("parse_error", lang, error=str(e), response=response.text))
        logger.error(f"Notes response parsing failed: {str(e)}", exc_info=True)
    finally:
        st.session_state.show_popup = False
        st.markdown(
            """
            <script>
                enableScroll();
            </script>
            """,
            unsafe_allow_html=True
        )

def split_travel_notes(notes: str, lang: str) -> List[str]:
    """根据Day N和📍城市标签，合理分割并清理小红书文案卡片"""
    segments = re.split(r'(?=📍)|(?=Day\s*\d+)', notes)
    segments = [seg.strip() for seg in segments if seg.strip()]

    cards = []
    buffer = ""

    for seg in segments:
        if (seg.startswith('📍') or seg.startswith('Day')) and buffer:
            cards.append(buffer.strip())
            buffer = seg
        else:
            buffer += "\n" + seg

    if buffer:
        cards.append(buffer.strip())

    clean_cards = []
    for card in cards:
        card = re.sub(r'🌟\s*[-#]{2,}', '', card)
        card = re.sub(r'\n{2,}', '\n', card).strip()
        clean_cards.append(card)

    clean_cards = clean_cards[:9]

    while len(clean_cards) < 3:
        clean_cards.append("更多冒险正在路上！🌟" if lang == "zh" else "More adventures coming soon! 🌟")

    return clean_cards

if __name__ == "__main__":
    if st.session_state.get("needs_rerun", False):
        st.session_state.needs_rerun = False
        st.rerun()

    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = "zh"

    # Initialize popup state
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False
    if 'popup_complete' not in st.session_state:
        st.session_state.popup_complete = False
    if 'show_success_message' not in st.session_state:
        st.session_state.show_success_message = False

    # Main interface
    st.markdown(f"<h1 style='text-align: center;'>{get_translation('title', st.session_state.language)}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>{get_translation('subtitle', st.session_state.language)}</h2>",
                unsafe_allow_html=True)

    # Display success message
    if st.session_state.show_success_message:
        st.markdown(
            f'<div class="success-message">{get_translation("success_message", st.session_state.language)}</div>',
            unsafe_allow_html=True
        )
        st.session_state.show_success_message = False

    # State management 🗃️
    if 'stage' not in st.session_state:
        st.session_state.stage = "input"
        st.session_state.drafts = None
        st.session_state.final_plan = None
        st.session_state.cities = None
        st.session_state.submitted_user_input = ""
        st.session_state.city = ""
        st.session_state.days = None
        st.session_state.last_response = None
        st.session_state.num_cities = 1
        st.session_state.city_inputs = [{"name": "", "days": 1, "preferences": ""}]
        st.session_state.show_confirm = False
        st.session_state.draft_feedbacks = [[] for _ in range(3)]
        st.session_state.final_feedback_history = []
        st.session_state.mode = "单城市" if st.session_state.language == "zh" else "single_city"
        st.session_state.refresh_trigger = False
        st.session_state.travel_notes = None

    # Mode change callback 🔄
    @st.dialog(get_translation("dialog_title", st.session_state.language))
    def ask():
        st.write(get_translation("dialog_prompt", st.session_state.language))
        num_cities = st.text_input(
            get_translation("dialog_input", st.session_state.language),
            help="多城市模式需要选择 2 到 5 个城市" if st.session_state.language == "zh" else "Multi-city mode requires 2 to 5 cities",
            placeholder="请输入 2 到 5" if st.session_state.language == "zh" else "Enter 2 to 5"
        )
        if st.button(get_translation("dialog_confirm", st.session_state.language)):
            try:
                num_cities = int(num_cities)
                if num_cities < 2:
                    st.error(get_translation("dialog_error_min_cities", st.session_state.language))
                    return
                if num_cities > 5:
                    st.error(get_translation("dialog_error_max_cities", st.session_state.language))
                    return
                st.session_state.num_cities = num_cities
                st.session_state.city_inputs = [{"name": "", "days": 1, "preferences": ""} for _ in range(num_cities)]
                st.session_state.mode = "multi_city" if st.session_state.language == "en" else "多城市"
                st.session_state.city = ""
                st.session_state.days = None
                st.session_state.submitted_user_input = ""
                st.session_state.draft_feedbacks = [[] for _ in range(3)]
                st.session_state.final_feedback_history = []
                st.session_state.stage = "input"
                st.session_state.travel_notes = None
                st.session_state.final_plan = None
                st.success(get_translation("mode_switch", st.session_state.language,
                                           mode=get_translation("multi_city", st.session_state.language)))
                st.rerun()
            except ValueError:
                st.error(get_translation("dialog_error", st.session_state.language))

    def on_mode_change():
        selected_mode = st.session_state.mode_select
        if selected_mode != get_translation(st.session_state.mode, st.session_state.language):
            if selected_mode == get_translation("single_city", st.session_state.language):
                st.session_state.mode = "single_city" if st.session_state.language == "en" else "单城市"
                st.session_state.city_inputs = [{"name": "", "days": 1, "preferences": ""}]
                st.session_state.num_cities = 1
                st.session_state.city = ""
                st.session_state.days = None
            else:
                st.session_state.mode = "multi_city" if st.session_state.language == "en" else "多城市"
                ask()
                return
            st.session_state.submitted_user_input = ""
            st.session_state.drafts = None
            st.session_state.final_plan = None
            st.session_state.cities = None
            st.session_state.last_response = None
            st.session_state.draft_feedbacks = [[] for _ in range(3)]
            st.session_state.final_feedback_history = []
            st.session_state.stage = "input"
            st.session_state.refresh_trigger = False
            st.session_state.travel_notes = None
            st.info(get_translation("mode_switch", st.session_state.language, mode=selected_mode))

    def on_language_change():
        new_language = "en" if st.session_state.language_select == "English" else "zh"
        if new_language != st.session_state.language:
            confirm_text = "确认要切换语言吗？所有页面数据将会丢失。" if new_language == "zh" else "Are you sure you want to change the language? All page data will be lost."
            @st.dialog("语言切换确认" if new_language == "zh" else "Language Switch Confirmation")
            def confirm_language_switch():
                st.write(confirm_text)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("确认" if new_language == "zh" else "Confirm"):
                        st.session_state.language = new_language
                        st.session_state.mode = "single_city" if new_language == "en" else "单城市"
                        st.session_state.stage = "input"
                        st.session_state.drafts = None
                        st.session_state.final_plan = None
                        st.session_state.cities = None
                        st.session_state.submitted_user_input = ""
                        st.session_state.city = ""
                        st.session_state.days = None
                        st.session_state.last_response = None
                        st.session_state.num_cities = 1
                        st.session_state.city_inputs = [{"name": "", "days": 1, "preferences": ""}]
                        st.session_state.show_confirm = False
                        st.session_state.draft_feedbacks = [[] for _ in range(3)]
                        st.session_state.final_feedback_history = []
                        st.session_state.refresh_trigger = False
                        st.session_state.travel_notes = None
                        st.session_state.needs_rerun = True
                        st.rerun()
                with col2:
                    if st.button("取消" if new_language == "zh" else "Cancel"):
                        st.session_state.language_select = "English" if st.session_state.language == "en" else "中文"
                        st.rerun()
            confirm_language_switch()

    # Sidebar 🐾
    with st.sidebar:
        st.header(get_translation("sidebar_header", st.session_state.language))
        idx = 0 if st.session_state.language == "zh" else 1
        st.selectbox(
            get_translation("language_label", st.session_state.language),
            ["中文", "English"],
            format_func=lambda x: "中文 (Chinese)" if x == "中文" else "English",
            index=idx,
            key="language_select",
            on_change=on_language_change
        )
        st.radio(
            get_translation("select_travel_type", st.session_state.language),
            [get_translation("single_city", st.session_state.language),
             get_translation("multi_city", st.session_state.language)],
            index=0 if st.session_state.mode in ["单城市", "single_city"] else 1,
            key="mode_select",
            on_change=on_mode_change
        )
        with st.form("travel_form"):
            today = datetime.datetime.now().date()
            if st.session_state.mode in ["单城市", "single_city"]:
                city = st.text_input(
                    get_translation("city_name", st.session_state.language),
                    value=st.session_state.city or "",
                    placeholder=get_translation("city_placeholder", st.session_state.language),
                    key="single_city"
                )
                date_range = st.date_input(
                    get_translation("date_range", st.session_state.language),
                    min_value=today,
                    value=(today, today + datetime.timedelta(days=3)),
                    format="MM/DD/YYYY",
                    key="date_range"
                )
                days = None
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                    if start_date <= end_date:
                        days = (end_date - start_date).days + 1
                        if days < 1 or days > 30:
                            st.error(get_translation("invalid_days", st.session_state.language))
                            days = None
                        else:
                            st.info(get_translation("days_info", st.session_state.language, days=days))
                    else:
                        st.error(get_translation("invalid_date", st.session_state.language))
                        days = None
                else:
                    st.error(get_translation("invalid_date", st.session_state.language))
                user_input = st.text_area(
                    get_translation("user_input_label", st.session_state.language),
                    value=st.session_state.submitted_user_input or "",
                    placeholder=get_translation("user_input_placeholder", st.session_state.language),
                    height=200,
                    help="请尽量详细描述您的偏好，以获得更精准的规划！🐶" if st.session_state.language == "zh" else
                         "Please provide detailed preferences for a tailored plan! 🐶",
                    key="user_input"
                )
                submitted = st.form_submit_button(get_translation("submit_button", st.session_state.language))
            else:
                for i in range(st.session_state.num_cities):
                    st.markdown(get_translation("city_n", st.session_state.language, n=i + 1))
                    col1, col2, col3 = st.columns([3, 2, 3])
                    with col1:
                        st.session_state.city_inputs[i]["name"] = st.text_input(
                            get_translation("city_name", st.session_state.language) + f" {i + 1} 🏙️",
                            value=st.session_state.city_inputs[i]["name"],
                            placeholder=get_translation("city_placeholder", st.session_state.language),
                            key=f"city_name_{i}"
                        )
                    with col2:
                        st.session_state.city_inputs[i]["days"] = st.number_input(
                            get_translation("days_label", st.session_state.language),
                            min_value=1,
                            max_value=30,
                            value=st.session_state.city_inputs[i]["days"],
                            step=1,
                            key=f"city_days_{i}"
                        )
                    with col3:
                        st.session_state.city_inputs[i]["preferences"] = st.text_input(
                            get_translation("preferences_label", st.session_state.language),
                            value=st.session_state.city_inputs[i]["preferences"],
                            placeholder=get_translation("preferences_placeholder", st.session_state.language),
                            key=f"preferences_{i}"
                        )
                user_input = ""
                submitted = st.form_submit_button(get_translation("submit_button", st.session_state.language))
        st.markdown("<hr style='border: 2px dotted #d4a017;'>", unsafe_allow_html=True)
        st.markdown(get_translation("thanks", st.session_state.language), unsafe_allow_html=True)

    # Handle submission 🚀
    if submitted:
        logger.info(
            f"📝 Submit request: mode={st.session_state.mode}, city={city if st.session_state.mode in ['单城市', 'single_city'] else st.session_state.city_inputs}")
        validation_errors = []
        lang = st.session_state.language

        if st.session_state.mode in ["单城市", "single_city"]:
            if not city or not city.strip():
                validation_errors.append(get_translation("error_empty_city", lang))
            if not days or days <= 0:
                validation_errors.append(get_translation("error_invalid_days", lang))
            if validation_errors:
                st.error(get_translation("submit_failed", lang, errors=';'.join(validation_errors)))
                st.session_state.stage = "input"
            else:
                st.session_state.stage = "drafts"
                st.session_state.submitted_user_input = user_input or (
                    "无特定偏好 🎒" if lang == "zh" else "No specific preferences 🎒")
                st.session_state.city = city.strip()
                st.session_state.days = days
                st.session_state.draft_feedbacks = [[] for _ in range(3)]
                st.session_state.final_feedback_history = []
                st.session_state.refresh_trigger = False
                st.session_state.travel_notes = None
                st.session_state.show_popup = True
                st.session_state.popup_complete = False
        else:
            for i, city_info in enumerate(st.session_state.city_inputs):
                if not city_info.get("name") or not city_info.get("name").strip():
                    validation_errors.append(get_translation("error_city_n_empty", lang, n=i + 1))
                if not city_info.get("days") or city_info.get("days") <= 0:
                    validation_errors.append(get_translation("error_city_n_days", lang, n=i + 1))
            if validation_errors:
                st.error(get_translation("submit_failed", lang, errors=';'.join(validation_errors)))
                st.session_state.stage = "input"
            else:
                st.session_state.stage = "drafts"
                st.session_state.submitted_user_input = generate_user_input(st.session_state.city_inputs, lang)
                st.session_state.city = [city.get("name").strip() for city in st.session_state.city_inputs]
                st.session_state.cities = [city.get("name").strip() for city in st.session_state.city_inputs]
                st.session_state.days = [city.get("days") for city in st.session_state.city_inputs]
                st.session_state.draft_feedbacks = [[] for _ in range(3)]
                st.session_state.final_feedback_history = []
                st.session_state.refresh_trigger = False
                st.session_state.travel_notes = None
                st.session_state.show_popup = True
                st.session_state.popup_complete = False

        if st.session_state.stage == "drafts":
            st.markdown(
                """
                <script>
                    disableScroll();
                </script>
                """,
                unsafe_allow_html=True
            )
            with st.empty():
                st.markdown(
                    f"""
                    <div class="popup-overlay">
                        <div class="popup-content">
                            <p>{get_translation("popup_submit", lang)}</p>
                            <div class="loader"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                try:
                    session = create_session()
                    if st.session_state.mode in ["单城市", "single_city"]:
                        user_input_log = st.session_state.submitted_user_input or (
                            "无特定偏好 🎒" if lang == "zh" else "No specific preferences 🎒")
                        logger.info(
                            f"📩 Sending request: mode={st.session_state.mode}, city={st.session_state.city}, days={st.session_state.days}, user_input={user_input_log[:50]}...")
                        response = session.post(
                            "http://localhost:8001/plan",
                            json={"mode": "single_city" if lang == "en" else "单城市",
                                  "city": st.session_state.city,
                                  "days": st.session_state.days,
                                  "user_input": st.session_state.submitted_user_input,
                                  "language": lang},
                            timeout=600
                        )
                    else:
                        logger.info(
                            f"📩 Sending request: mode={st.session_state.mode}, user_input={st.session_state.submitted_user_input[:50]}...")
                        response = session.post(
                            "http://localhost:8001/plan",
                            json={"mode": "multi_city" if lang == "en" else "多城市",
                                  "cities": st.session_state.city_inputs,
                                  "user_input": st.session_state.submitted_user_input,
                                  "language": lang},
                            timeout=600
                        )
                    logger.info(f"📬 Received response: {response.status_code}, {response.text}")
                    st.session_state.last_response = response.text
                    response_data = response.json()
                    with open("response_output.json", "w", encoding="utf-8") as f:
                        json.dump(response_data, f, ensure_ascii=False, indent=4)
                    if response.status_code != 200:
                        st.error(get_translation("backend_error", lang, code=response.status_code,
                                                 detail=response_data.get('detail', response.text)))
                        st.session_state.stage = "input"
                        st.session_state.show_popup = False
                    elif response_data.get("error"):
                        st.error(get_translation("backend_error", lang, code=response.status_code,
                                                 detail=response_data['error']))
                        st.session_state.stage = "input"
                        st.session_state.show_popup = False
                    elif response_data.get("drafts"):
                        st.session_state.drafts = response_data["drafts"]
                        st.session_state.stage = "drafts"
                        st.session_state.show_success_message = True
                    elif response_data.get("cities"):
                        st.session_state.cities = response_data["cities"]
                        st.session_state.stage = "cities"
                        st.session_state.show_success_message = True
                    elif response_data.get("final_plan"):
                        st.session_state.final_plan = response_data["final_plan"]
                        st.session_state.stage = "final"
                        st.session_state.show_success_message = True
                    else:
                        st.error(get_translation("invalid_response", lang,
                                                 response=json.dumps(response_data, ensure_ascii=False)))
                        logger.error(f"Invalid backend response: {response.text}")
                        st.session_state.show_popup = False
                except requests.Timeout:
                    st.error(get_translation("timeout_error", lang))
                    logger.error("Request timed out", exc_info=True)
                    st.session_state.stage = "input"
                    st.session_state.show_popup = False
                except requests.ConnectionError:
                    st.error(get_translation("connection_error", lang))
                    logger.error("Cannot connect to backend", exc_info=True)
                    st.session_state.stage = "input"
                    st.session_state.show_popup = False
                except requests.RequestException as e:
                    st.error(get_translation("request_error", lang, error=str(e)))
                    logger.error(f"Request failed: {str(e)}", exc_info=True)
                    st.session_state.show_popup = False
                except ValueError as e:
                    st.error(
                        get_translation("parse_error", lang, error=str(e), response=st.session_state.last_response))
                    logger.error(f"Response parsing failed: {str(e)}", exc_info=True)
                    st.session_state.show_popup = False
                finally:
                    st.session_state.show_popup = False
                    st.markdown(
                        """
                        <script>
                            enableScroll();
                        </script>
                        """,
                        unsafe_allow_html=True
                    )

    # Main content
    placeholder = st.empty()

    with placeholder.container():
        lang = st.session_state.language
        if st.session_state.stage == "drafts" and st.session_state.drafts:
            if st.session_state.show_popup:
                st.session_state.show_popup = False
                st.markdown(
                    """
                    <script>
                        enableScroll();
                    </script>
                    """,
                    unsafe_allow_html=True
                )

            if 'current_draft_index' not in st.session_state:
                st.session_state.current_draft_index = 0

            total_drafts = len(st.session_state.drafts)

            def prev_draft():
                st.session_state.current_draft_index = (st.session_state.current_draft_index - 1) % total_drafts
                st.rerun()

            def next_draft():
                st.session_state.current_draft_index = (st.session_state.current_draft_index + 1) % total_drafts
                st.rerun()

            st.subheader(get_translation("drafts_header", lang), anchor=False, divider="rainbow")

            col_nav_left, col_nav_center, col_nav_right = st.columns([1, 8, 1])
            with col_nav_left:
                st.button("⬅️", on_click=prev_draft, key="prev_draft")
            with col_nav_center:
                st.markdown(
                    f'<div style="text-align: center; font-size: 1.2em; color: #d4a017;">'
                    f'{get_translation("plan_n", lang, n=st.session_state.current_draft_index + 1)} / {total_drafts}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_nav_right:
                st.button("➡️", on_click=next_draft, key="next_draft")

            draft_index = st.session_state.current_draft_index
            draft = st.session_state.drafts[draft_index]

            if not isinstance(draft, dict) or "content" not in draft:
                st.error(get_translation("draft_error", lang, n=draft_index + 1))
                logger.error(f"Draft format error: {draft}")
            else:
                with st.container():
                    st.markdown(
                        f'<div class="card" style="max-width: 80%; margin: 15px auto;">'
                        f'<div class="card-title">{get_translation("plan_n", lang, n=draft_index + 1)}</div>',
                        unsafe_allow_html=True
                    )
                    processed_content = convert_markdown_headers(draft["content"])
                    st.markdown(
                        f'<div class="card-content">{processed_content}</div>',
                        unsafe_allow_html=True
                    )
                    if st.session_state.mode in ["单城市", "single_city"] and "weather_info" in draft:
                        processed_weather = convert_markdown_headers(draft["weather_info"])
                        st.markdown(get_translation("weather_info", lang, info=processed_weather),
                                    unsafe_allow_html=True)
                    elif st.session_state.mode in ["多城市", "multi_city"] and "weather_infos" in draft:
                        weather_text = "<br>".join([f"{city}: {convert_markdown_headers(info)}" for city, info in
                                                    draft["weather_infos"].items()])
                        st.markdown(get_translation("multi_weather_info", lang, info=weather_text),
                                    unsafe_allow_html=True)

                    feedback_history = st.session_state.draft_feedbacks[draft_index]
                    if feedback_history:
                        with st.expander(get_translation("feedback_history", lang, n=draft_index + 1)):
                            for j, feedback_entry in enumerate(feedback_history, 1):
                                processed_feedback = convert_markdown_headers(feedback_entry['text'])
                                st.markdown(get_translation("feedback_n", lang, n=j, time=feedback_entry['timestamp'],
                                                            text=processed_feedback), unsafe_allow_html=True)

                    st.markdown('<div style="margin-top: 15px;">', unsafe_allow_html=True)
                    with st.form(key=f"feedback_form_{draft_index + 1}"):
                        feedback_key = f"temp_feedback_{draft_index + 1}"
                        feedback_value = "" if st.session_state.get(f"clear_{feedback_key}",
                                                                    False) else st.session_state.get(feedback_key, "")
                        feedback = st.text_area(
                            get_translation("feedback_label", lang, n=draft_index + 1),
                            value=feedback_value,
                            placeholder=get_translation("feedback_placeholder", lang),
                            height=100,
                            key=f"feedback_text_{draft_index + 1}"
                        )
                        st.session_state[feedback_key] = feedback
                        col1, col2 = st.columns(2)
                        with col1:
                            select_button = st.form_submit_button(
                                get_translation("select_plan", lang, n=draft_index + 1))
                        with col2:
                            refresh_button = st.form_submit_button(
                                get_translation("refresh_plan", lang, n=draft_index + 1))

                        if select_button:
                            st.session_state.show_popup = True
                            st.markdown(
                                f"""
                                <div class="popup-overlay">
                                    <div class="popup-content">
                                        <p>{get_translation("popup_select", lang, n=draft_index + 1)}</p>
                                        <div class="loader"></div>
                                    </div>
                                </div>
                                <script>
                                    disableScroll();
                                </script>
                                """,
                                unsafe_allow_html=True
                            )
                            select_draft(draft, lang, draft_index + 1)
                        if refresh_button:
                            st.session_state.show_popup = True
                            st.markdown(
                                f"""
                                <div class="popup-overlay">
                                    <div class="popup-content">
                                        <p>{get_translation("popup_refresh", lang, n=draft_index + 1)}</p>
                                        <div class="loader"></div>
                                    </div>
                                </div>
                                <script>
                                    disableScroll();
                                </script>
                                """,
                                unsafe_allow_html=True
                            )
                            refresh_draft(draft, draft_index, lang)

                    if st.session_state.get(f"clear_{feedback_key}", False):
                        st.session_state[feedback_key] = ""
                        st.session_state[f"clear_{feedback_key}"] = False
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            if st.session_state.get("refresh_trigger", False):
                st.session_state.refresh_trigger = False

        if st.session_state.stage == "final" and st.session_state.final_plan:
            if st.session_state.show_popup:
                st.session_state.show_popup = False
                st.markdown(
                    """
                    <script>
                        enableScroll();
                    </script>
                    """,
                    unsafe_allow_html=True
                )
            st.subheader(get_translation("final_plan_header", lang), anchor=False, divider="rainbow")
            if st.session_state.mode in ["单城市", "single_city"]:
                with st.container():
                    processed_summary = convert_markdown_headers(st.session_state.final_plan['summary'])
                    st.markdown(get_translation("summary", lang, summary=processed_summary), unsafe_allow_html=True)
                    # Add map display for single city
                    try:
                        map_obj = create_map(st.session_state.final_plan, lang)
                        st_folium(map_obj, width="100%")
                    except Exception as e:
                        st.error(get_translation("map_error", lang, error=str(e)))
                        logger.error(f"Failed to render map: {str(e)}", exc_info=True)
                    with st.expander(get_translation("details", lang)):
                        st.markdown(get_translation("attractions", lang))
                        processed_view_plan = convert_markdown_headers(st.session_state.final_plan['details']['view_plan'])
                        st.markdown(processed_view_plan, unsafe_allow_html=True)
                        st.markdown(get_translation("food", lang))
                        processed_food_plan = convert_markdown_headers(st.session_state.final_plan['details']['food_plan'])
                        st.markdown(processed_food_plan, unsafe_allow_html=True)
                        st.markdown(get_translation("accommodation", lang))
                        processed_accommodation_plan = convert_markdown_headers(st.session_state.final_plan['details']['accommodation_plan'])
                        st.markdown(processed_accommodation_plan, unsafe_allow_html=True)
                        st.markdown(get_translation("transport", lang))
                        processed_traffic_plan = convert_markdown_headers(st.session_state.final_plan['details']['traffic_plan'])
                        st.markdown(processed_traffic_plan, unsafe_allow_html=True)
                        weather_info = st.session_state.final_plan['details'].get('weather_info', None)
                        if weather_info and "天气查询失败" not in weather_info and "Weather query failed" not in weather_info:
                            processed_weather = convert_markdown_headers(weather_info)
                            st.markdown(get_translation("weather_info", lang, info=processed_weather), unsafe_allow_html=True)
                        else:
                            if 'Weather Info:' in st.session_state.final_plan['summary'] or '天气信息：' in \
                                    st.session_state.final_plan['summary']:
                                summary_weather = st.session_state.final_plan['summary'].split(
                                    'Weather Info:' if lang == "en" else '天气信息：')[-1].strip()
                                if summary_weather and "Weather query failed" not in summary_weather and "天气查询失败" not in summary_weather:
                                    processed_summary_weather = convert_markdown_headers(summary_weather)
                                    st.markdown(get_translation("weather_fallback", lang, info=processed_summary_weather), unsafe_allow_html=True)
                                else:
                                    processed_fallback = convert_markdown_headers(weather_info or summary_weather or (
                                        'Unable to fetch weather info, check logs or network' if lang == "en" else '无法获取天气信息，请检查日志或网络连接'))
                                    st.markdown(get_translation("weather_fallback", lang, info=processed_fallback), unsafe_allow_html=True)
                            else:
                                processed_fallback = convert_markdown_headers(weather_info or (
                                    'Unable to fetch weather info, check logs or network' if lang == "en" else '无法获取天气信息，请检查日志或网络连接'))
                                st.markdown(get_translation("weather_fallback", lang, info=processed_fallback), unsafe_allow_html=True)
                    if st.session_state.final_feedback_history:
                        with st.expander(get_translation("final_feedback_history", lang)):
                            for j, feedback_entry in enumerate(st.session_state.final_feedback_history, 1):
                                processed_feedback = convert_markdown_headers(feedback_entry['text'])
                                st.markdown(get_translation("feedback_n", lang, n=j, time=feedback_entry['timestamp'],
                                                            text=processed_feedback), unsafe_allow_html=True)
                    with st.form(key="final_feedback_form"):
                        feedback_key = "temp_final_feedback"
                        feedback_value = "" if st.session_state.get(f"clear_{feedback_key}",
                                                                    False) else st.session_state.get(feedback_key, "")
                        feedback = st.text_area(
                            get_translation("final_feedback_label", lang),
                            value=feedback_value,
                            placeholder=get_translation("final_feedback_placeholder", lang),
                            height=100,
                            key="final_feedback_text"
                        )
                        st.session_state[feedback_key] = feedback
                        submit_feedback = st.form_submit_button(get_translation("submit_feedback", lang))
                        if submit_feedback:
                            with st.spinner(get_translation("thinking", lang)):
                                submit_final_feedback(lang)
                        if st.session_state.get(f"clear_{feedback_key}", False):
                            st.session_state[feedback_key] = ""
                            st.session_state[f"clear_{feedback_key}"] = False
                    if st.button(get_translation("generate_notes", lang)):
                        st.session_state.show_popup = True
                        with st.container():
                            if st.session_state.show_popup:
                                st.markdown(
                                    f"""
                                    <div class="popup-overlay">
                                        <div class="popup-content">
                                            <p>{get_translation("popup_notes", lang)}</p>
                                            <div class="loader"></div>
                                        </div>
                                    </div>
                                    <script>
                                        disableScroll();
                                    </script>
                                    """,
                                    unsafe_allow_html=True
                                )
                        generate_travel_notes(lang)
                    if st.session_state.get("travel_notes"):
                        with st.expander(get_translation("notes_header", lang), expanded=True):
                            segments = split_travel_notes(st.session_state.travel_notes, lang)
                            num_cols = 3
                            for i in range(0, len(segments), num_cols):
                                cols = st.columns(num_cols)
                                for j in range(num_cols):
                                    if i + j < len(segments):
                                        with cols[j]:
                                            formatted_segment = convert_markdown_headers(segments[i + j]).replace('\n', '<br>')
                                            st.markdown(
                                                f'<div class="xiaohongshu-card">'
                                                f'<div class="xiaohongshu-card-content">{formatted_segment}</div>'
                                                f'</div>',
                                                unsafe_allow_html=True
                                            )
                    if st.button(get_translation("back_to_drafts", lang)):
                        st.session_state.stage = "drafts"
                        st.session_state.travel_notes = None
                        st.rerun()
            elif st.session_state.mode in ["多城市", "multi_city"]:
                # Add map display for multi-city
                try:
                    map_obj = create_map(st.session_state.final_plan, lang)
                    st_folium(map_obj, width="100%")
                except Exception as e:
                    st.error(get_translation("map_error", lang, error=str(e)))
                    logger.error(f"Failed to render map: {str(e)}", exc_info=True)
                for i, city_plan in enumerate(st.session_state.final_plan):
                    with st.container():
                        if i > 0 and "inter_city_traffic" in city_plan:
                            processed_traffic = convert_markdown_headers(city_plan["inter_city_traffic"])
                            st.markdown(get_translation("inter_city_transport", lang), unsafe_allow_html=True)
                            st.markdown(processed_traffic, unsafe_allow_html=True)
                        st.markdown(get_translation("city_plan", lang, city=city_plan['city'], days=city_plan['days']))
                        if city_plan.get("plan"):
                            processed_summary = convert_markdown_headers(city_plan['plan']['summary'])
                            st.markdown(get_translation("summary", lang, summary=processed_summary), unsafe_allow_html=True)
                            with st.expander(get_translation("details", lang)):
                                st.markdown(get_translation("attractions", lang))
                                processed_view_plan = convert_markdown_headers(city_plan['plan']['details']['view_plan'])
                                st.markdown(processed_view_plan, unsafe_allow_html=True)
                                st.markdown(get_translation("food", lang))
                                processed_food_plan = convert_markdown_headers(city_plan['plan']['details']['food_plan'])
                                st.markdown(processed_food_plan, unsafe_allow_html=True)
                                st.markdown(get_translation("accommodation", lang))
                                processed_accommodation_plan = convert_markdown_headers(city_plan['plan']['details']['accommodation_plan'])
                                st.markdown(processed_accommodation_plan, unsafe_allow_html=True)
                                st.markdown(get_translation("transport", lang))
                                processed_traffic_plan = convert_markdown_headers(city_plan['plan']['details']['traffic_plan'])
                                st.markdown(processed_traffic_plan, unsafe_allow_html=True)
                                weather_info = city_plan['plan']['details'].get('weather_info', None)
                                if weather_info and "天气查询失败" not in weather_info and "Weather query failed" not in weather_info:
                                    processed_weather = convert_markdown_headers(weather_info)
                                    st.markdown(get_translation("weather_info", lang, info=processed_weather), unsafe_allow_html=True)
                                else:
                                    if 'Weather Info:' in city_plan['plan']['summary'] or '天气信息：' in city_plan['plan']['summary']:
                                        summary_weather = city_plan['plan']['summary'].split(
                                            'Weather Info:' if lang == "en" else '天气信息：')[-1].strip()
                                        if summary_weather and "Weather query failed" not in summary_weather and "天气查询失败" not in summary_weather:
                                            processed_summary_weather = convert_markdown_headers(summary_weather)
                                            st.markdown(get_translation("weather_fallback", lang, info=processed_summary_weather), unsafe_allow_html=True)
                                        else:
                                            processed_fallback = convert_markdown_headers(weather_info or summary_weather or (
                                                'Unable to fetch weather info, check logs or network' if lang == "en" else '无法获取天气信息，请检查日志或网络连接'))
                                            st.markdown(get_translation("weather_fallback", lang, info=processed_fallback), unsafe_allow_html=True)
                                    else:
                                        processed_fallback = convert_markdown_headers(weather_info or (
                                            'Unable to fetch weather info, check logs or network' if lang == "en" else '无法获取天气信息，请检查日志或网络连接'))
                                        st.markdown(get_translation("weather_fallback", lang, info=processed_fallback), unsafe_allow_html=True)
                if st.session_state.final_feedback_history:
                    with st.expander(get_translation("final_feedback_history", lang)):
                        for j, feedback_entry in enumerate(st.session_state.final_feedback_history, 1):
                            processed_feedback = convert_markdown_headers(feedback_entry['text'])
                            st.markdown(get_translation("feedback_n", lang, n=j, time=feedback_entry['timestamp'],
                                                        text=processed_feedback), unsafe_allow_html=True)
                with st.form(key="final_feedback_form"):
                    feedback_key = "temp_final_feedback"
                    feedback_value = "" if st.session_state.get(f"clear_{feedback_key}",
                                                                False) else st.session_state.get(feedback_key, "")
                    feedback = st.text_area(
                        get_translation("final_feedback_label", lang),
                        value=feedback_value,
                        placeholder=get_translation("final_feedback_placeholder", lang),
                        height=100,
                        key="final_feedback_text"
                    )
                    st.session_state[feedback_key] = feedback
                    submit_feedback = st.form_submit_button(get_translation("submit_feedback", lang))
                    if submit_feedback:
                        with st.spinner(get_translation("thinking", lang)):
                            submit_final_feedback(lang)
                    if st.session_state.get(f"clear_{feedback_key}", False):
                        st.session_state[feedback_key] = ""
                        st.session_state[f"clear_{feedback_key}"] = False
                if st.button(get_translation("generate_notes", lang)):
                    st.session_state.show_popup = True
                    with st.container():
                        if st.session_state.show_popup:
                            st.markdown(
                                f"""
                                <div class="popup-overlay">
                                    <div class="popup-content">
                                        <p>{get_translation("popup_notes", lang)}</p>
                                        <div class="loader"></div>
                                    </div>
                                </div>
                                <script>
                                    disableScroll();
                                </script>
                                """,
                                unsafe_allow_html=True
                            )
                    generate_travel_notes(lang)
                if st.session_state.get("travel_notes"):
                    with st.expander(get_translation("notes_header", lang), expanded=True):
                        segments = split_travel_notes(st.session_state.travel_notes, lang)
                        num_cols = 3
                        for i in range(0, len(segments), num_cols):
                            cols = st.columns(num_cols)
                            for j in range(num_cols):
                                if i + j < len(segments):
                                    with cols[j]:
                                        formatted_segment = convert_markdown_headers(segments[i + j]).replace('\n', '<br>')
                                        st.markdown(
                                            f'<div class="xiaohongshu-card">'
                                            f'<div class="xiaohongshu-card-content">{formatted_segment}</div>'
                                            f'</div>',
                                            unsafe_allow_html=True
                                        )
                if st.button(get_translation("back_to_drafts", lang)):
                    st.session_state.stage = "drafts"
                    st.session_state.travel_notes = None
                    st.rerun()