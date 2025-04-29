TRANSLATIONS = {
    "zh": {
        "weather_query": "使用工具查询{city}的当前及未来数日天气情况，并以简洁的文本形式返回，包含温度、降雨概率等关键信息。",
        "weather_human": "查询{city}的天气",
        "weather_error": "天气查询失败: {error}. 请检查 MCP 服务 (http://localhost:8000/sse) 是否运行并支持天气查询工具。",
        "weather_unavailable": "天气信息不可用：MCP 服务未响应或工具不可用。",
        "draft_sport": "你需要为用户希望的旅行提供更加偏运动的方案选择，快速给出笼统的旅行方案，基于用户偏好：{user_input}，城市：{city}，天数：{days}，天气情况：{weather}。考虑天气影响，选择适合的户外或室内活动。",
        "draft_culture": "你需要为用户希望的旅行提供更加偏文化的方案选择，快速给出笼统的旅行方案，基于用户偏好：{user_input}，城市：{city}，天数：{days}，天气情况：{weather}。考虑天气影响，优先选择适合的博物馆或室内景点。",
        "draft_food": "你需要为用户希望的旅行提供更加偏美食的方案选择，快速给出笼统的旅行方案，基于用户偏好：{user_input}，城市：{city}，天数：{days}，天气情况：{weather}。考虑天气影响，推荐适合的餐厅或美食街。",
        "draft_system": "为{city}的{days}天行程生成一个草稿方案，基于用户偏好：{user_input}和天气情况：{weather}。\n{prompt}\n输出简洁的文本，概述主要景点、餐饮、住宿和交通安排，明确提及天气对选择的影响（如避免雨天户外活动）。",
        "draft_human": "草稿 {num}：{city}，{days}天，偏好：{user_input}，天气：{weather}",
        "multi_draft_system": "你是一个经验丰富的旅行规划师，你要生成多城市旅行的草稿行程。需要清晰地规划城市之间的交通方式，并考虑各城市天气影响。",
        "multi_draft_prompt": "请为以下多城市旅行用户生成一份{style}风格的整体旅行草稿。\n城市行程如下：{cities}。\n请按城市顺序依次给出整体行程建议，包含城市间的交通衔接，并覆盖景点、美食、住宿、交通四个方面的概述，语言简洁清晰，考虑天气影响（如雨天推荐室内活动）。",
        "single_require": "用户对{city}的{days}天旅行需求：{user_input}",
        "draft_reference": "\n参考草稿风格：{draft}",
        "feedback_previous": "\n用户反馈：{feedback}\n基于上次计划：{plan}",
        "final_feedback": "\n用户对最终方案的历史反馈：\n{feedback}\n请根据所有反馈调整最终方案，保持原有风格和需求。",
        "search_system": "调用搜索工具search_from_web，查找关于指定城市旅行的最新信息、提示或注意事项。",
        "search_query": "为'{city}'的{days}天旅行（需求：{user_input}...）搜索相关注意事项或最新信息。",
        "task_split_system": "根据用户需求和参考信息，拆分任务到四个方面。严格按JSON格式输出。",
        "task_split_prompt": "将用户的旅游需求拆分为景区、住宿、餐饮、出行四个方面的详细要求。\n用户需求：{require}\n结合参考信息：{rag_context} {info}\n{format_instructions}",
        "view_prompt": "根据以下天气情况：{weather}\n用户需求: {require}\n景区要求: {view_req}\n参考信息: {rag_context} {info}\n请生成详细的{days}天景区游玩安排，列出景点名称、简介、开放时间、门票价格（如果适用）以及适合游览的理由（考虑天气影响）。",
        "food_prompt": "用户需求: {require}\n餐饮要求: {food_req}\n参考信息: {rag_context} {info}\n请结合当地特色和用户要求，推荐{days}天的餐饮地点和美食，列出餐厅名称、特色菜、地址、价格范围（如果适用）。",
        "accommodation_prompt": "用户需求: {require}\n住宿要求: {accommodation_req}\n参考信息: {rag_context} {info}\n请推荐符合要求的{days}天住宿方案（酒店、民宿等），列出酒店名称、地址、房型、价格范围（如果适用）。",
        "traffic_prompt": "根据以下天气情况：{weather}\n用户需求: {require}\n出行要求: {traffic_req}\n参考信息: {rag_context} {info}\n已规划的景点: {view_plan}\n已规划的住宿: {accommodation_plan}\n请为这{days}天的行程提供详细的市内交通出行方案（公共交通、打车、步行等），连接住宿、景点和餐饮地点，包含每段路线的起点、终点、交通方式、预计时间和费用（如果适用）。",
        "summary_prompt": "用户需求: {require}\n请综合以下规划，生成一份详细、连贯、包含每日安排的{city} {days}天旅行计划。\n景区安排: {view_plan}\n餐饮安排: {food_plan}\n住宿安排: {accommodation_plan}\n出行安排: {traffic_plan}\n天气信息: {weather}\nRAG 知识库参考: {rag_context}\n请使用清晰的格式，可以加入表情符号或Markdown增强可读性。",
        "transport_system": "你是一个城市间交通规划专家。使用可用工具查询交通信息并提供建议。",
        "transport_prompt": "查询从 {prev_city} 到 {city} 的最佳交通方式（考虑时间、成本、便利性），并给出建议。考虑用户整体需求：{user_input}",
        "notes_system": "你的任务是根据用户的出行计划，生成一篇小红书风格的旅行文案。\n"
                        "- 每个城市用 📍+城市名 开头，作为一个大段。\n"
                        "- 每天用 Day N 加小标题，比如 Day 1🏞️古堡打卡。\n"
                        "- 每个 Day 小节控制在 80-150字之间，活泼自然，有丰富表情符号🌟🍜。\n"
                        "- 小节之间自然过渡，用换行分隔，但不要生硬断开。\n"
                        "- 内容包括但不限于：打卡地、美食、拍照点、实用小贴士（如最佳时间、预算建议）。\n"
                        "- 如果有多个城市，确保每个城市独立清晰，不混在一起。\n"
                        "请根据以下旅行计划撰写：\n\n{plan}",
        "notes_human": "请基于以下旅行计划生成文案：\n\n{plan}",
        "xiaohongshu_style": "小红书风格：活泼、亲切、充满生活气息，融入大量表情符号，使用短段落或列表，突出打卡地、美食、拍照点，提供实用小贴士。",
        "invalid_mode": "无效的模式: {mode}，必须是 '单城市' 或 '多城市'（中文）或 'single_city' 或 'multi_city'（英文）",
        "single_city_error": "单城市模式需要提供有效的 city 和 days",
        "multi_city_error": "多城市模式需要提供有效的城市列表，每个城市需有名称和正整数天数",
        "invalid_draft_index": "无效的 draft_index: {index}，必须在 0 到 {max} 之间",
        "extract_locations_system": "你是一个助手，从用户输入中提取景点、餐厅和旅馆的名称。返回一个JSON对象，包含三个键：'attractions', 'restaurants', 'hotels'，每个键对应一个名称列表。",
        "extract_locations_human": "从以下输入中提取景点、餐厅和旅馆的名称：{input}",
    },
    "en": {
        "weather_query": "Use the tool to query the current and upcoming weather for {city}, returning concise text with key details like temperature and precipitation probability.",
        "weather_human": "Query the weather for {city}",
        "weather_error": "Weather query failed: {error}. Please check if the MCP service (http://localhost:8000/sse) is running and supports weather query tools.",
        "weather_unavailable": "Weather information unavailable: MCP service unresponsive or tools unavailable.",
        "draft_sport": "Provide a sports-oriented draft plan for the user's trip, quickly outlining a general itinerary based on preferences: {user_input}, city: {city}, days: {days}, weather: {weather}. Consider weather impacts, choosing suitable outdoor or indoor activities.",
        "draft_culture": "Provide a culture-oriented draft plan for the user's trip, quickly outlining a general itinerary based on preferences: {user_input}, city: {city}, days: {days}, weather: {weather}. Consider weather impacts, prioritizing suitable museums or indoor attractions.",
        "draft_food": "Provide a food-oriented draft plan for the user's trip, quickly outlining a general itinerary based on preferences: {user_input}, city: {city}, days: {days}, weather: {weather}. Consider weather impacts, recommending suitable restaurants or food streets.",
        "draft_system": "Generate a draft plan for a {days}-day trip to {city}, based on user preferences: {user_input} and weather: {weather}.\n{prompt}\nOutput concise text summarizing key attractions, dining, accommodation, and transport, clearly noting weather impacts (e.g., avoid outdoor activities on rainy days).",
        "draft_human": "Draft {num}: {city}, {days} days, preferences: {user_input}, weather: {weather}",
        "multi_draft_system": "You are an experienced travel planner tasked with generating a draft itinerary for a multi-city trip. Clearly plan inter-city transport and consider weather impacts for each city.",
        "multi_draft_prompt": "Generate a {style}-style draft itinerary for a multi-city trip.\nCities: {cities}.\nProvide suggestions in city order, including inter-city transport, covering attractions, dining, accommodation, and transport in concise, clear language, considering weather impacts (e.g., indoor activities on rainy days).",
        "single_require": "User requirements for a {days}-day trip to {city}: {user_input}",
        "draft_reference": "\nReference draft style: {draft}",
        "feedback_previous": "\nUser feedback: {feedback}\nBased on previous plan: {plan}",
        "final_feedback": "\nUser feedback history for the final plan:\n{feedback}\nAdjust the final plan based on all feedback, maintaining the original style and requirements.",
        "search_system": "Use the search tool to find the latest information, tips, or notes for the specified city's travel.",
        "search_query": "Search for notes or recent information for a {days}-day trip to '{city}' (requirements: {user_input}...).",
        "task_split_system": "Split the user's travel requirements into four aspects: attractions, accommodation, dining, and transport. Output strictly in JSON format.",
        "task_split_prompt": "Split the user's travel requirements into attractions, accommodation, dining, and transport.\nRequirements: {require}\nCombine with reference info: {rag_context} {info}\n{format_instructions}",
        "view_prompt": "Based on weather: {weather}\nUser requirements: {require}\nAttractions requirements: {view_req}\nReference info: {rag_context} {info}\nGenerate a detailed {days}-day attractions plan, listing names, descriptions, opening hours, ticket prices (if applicable), and reasons for suitability (considering weather impacts).",
        "food_prompt": "User requirements: {require}\nDining requirements: {food_req}\nReference info: {rag_context} {info}\nRecommend {days}-day dining locations and cuisines, listing restaurant names, signature dishes, addresses, and price ranges (if applicable).",
        "accommodation_prompt": "User requirements: {require}\nAccommodation requirements: {accommodation_req}\nReference info: {rag_context} {info}\nRecommend {days}-day accommodation options (hotels, hostels, etc.), listing names, addresses, room types, and price ranges (if applicable).",
        "traffic_prompt": "Based on weather: {weather}\nUser requirements: {require}\nTransport requirements: {traffic_req}\nReference info: {rag_context} {info}\nPlanned attractions: {view_plan}\nPlanned accommodation: {accommodation_plan}\nProvide a detailed {days}-day intra-city transport plan (public transport, taxis, walking, etc.), linking accommodation, attractions, and dining, including route start/end, transport mode, estimated time, and costs (if applicable).",
        "summary_prompt": "User requirements: {require}\nIntegrate the following plans into a detailed, coherent {days}-day travel plan for {city}, including daily arrangements.\nAttractions: {view_plan}\nDining: {food_plan}\nAccommodation: {accommodation_plan}\nTransport: {traffic_plan}\nWeather: {weather}\nRAG reference: {rag_context}\nUse a clear format, optionally adding emojis or Markdown for readability.",
        "transport_system": "You are an inter-city transport planning expert. Use available tools to query transport info and provide recommendations.",
        "transport_prompt": "Query the best transport options from {prev_city} to {city} (considering time, cost, convenience), and provide recommendations. Consider user requirements: {user_input}",
        "notes_system": "Your task is to generate a Xiaohongshu-style travel narrative based on the user's travel plan.\n"
                        "- Start each city section with 📍 + city name as the heading.\n"
                        "- Use 'Day N' for each day's mini-section, adding a playful subtitle, e.g., 'Day 1🏞️ Exploring the Old Town'.\n"
                        "- Keep each day's content between 80-150 words, lively and friendly, filled with emoji 🌟🍜.\n"
                        "- Maintain smooth transitions between sections using line breaks, but avoid abrupt cuts.\n"
                        "- Highlight must-visit spots, local food, photo spots, and practical tips (e.g., best time to visit, budget suggestions).\n"
                        "- If the trip includes multiple cities, ensure each city is clearly separated and independently introduced.\n"
                        "- Use a vibrant, engaging, and casual tone throughout, making it feel like a personal travel diary.\n"
                        "Here is the travel plan to base your writing on:\n\n{plan}",

        "notes_human": "Generate a narrative based on the following travel plan:\n\n{plan}",
        "xiaohongshu_style": "Xiaohongshu style: lively, friendly, full of lifestyle vibes, incorporating lots of emojis, using short paragraphs or lists, highlighting must-visit spots, food, and photo opportunities, and providing practical tips.",
        "invalid_mode": "Invalid mode: {mode}, must be 'single_city' or 'multi_city' (English) or '单城市' or '多城市' (Chinese)",
        "single_city_error": "Single city mode requires a valid city and days",
        "multi_city_error": "Multi-city mode requires a valid list of cities, each with a name and positive integer days",
        "invalid_draft_index": "Invalid draft_index: {index}, must be between 0 and {max}",
        "extract_locations_system": "You are an assistant that extracts names of attractions, restaurants, and hotels from user input. "
                                  "Return a JSON object with three keys: 'attractions', 'restaurants', 'hotels', each containing a list of names.",
        "extract_locations_human": "Extract the names of attractions, restaurants, and hotels from the following input: {input}",
    }
}