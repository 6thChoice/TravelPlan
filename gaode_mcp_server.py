# from fastapi import FastAPI, HTTPException
from mcp.server.fastmcp import FastMCP
import httpx
from search_engine import search
# import os

# os.environ["SSL_CERT_FILE"] = ""

app = FastMCP('gaode')

# 高德API配置
AMAP_KEY = "d9aaf03856e11f50e121a504a55f6efd"
AMAP_BASE_URL = "https://restapi.amap.com/v3"
AMAP_ADVANCE_URL = "https://restapi.amap.com/v5"

@app.tool()
async def search_from_web(query: str) -> str:
    """
    谷歌搜索引擎，用于搜集既有规划方案，支持决策

    Args:
        query: 搜索关键词

    Returns:
        网络搜索结果，以 markdown 格式整合
    """
    text = search(query)
    # print(text)
    return text


@app.tool()
async def geocode(address: str, city: str = "") -> dict:
    """
    地理编码API

    Args:
        address: 结构化地址信息 (例如 "北京市朝阳区阜通东大街6号")
        city: 指定查询的城市 (例如 "北京")

    Returns:
        地理编码结果，包括经纬度和其他详细信息
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AMAP_BASE_URL}/geocode/geo",
            params={
                "key": AMAP_KEY,
                "address": address,
                "city": city,
                "output": "json"
            }
        )
        data = response.json()
        if data["status"] == "1":
            return data["geocodes"][0]
        else:
            raise Exception(f"Geocode failed: {data['info']}")

@app.tool()
async def reverse_geocode(location: str, output: str = "json") -> dict:
    """
    逆地理编码API

    Args:
        location: 经纬度坐标 (例如 "116.480881,39.989410")
        output: 返回数据格式 (默认 "json")

    Returns:
        逆地理编码结果，包括详细地址和其他信息
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AMAP_BASE_URL}/geocode/regeo",
            params={
                "key": AMAP_KEY,
                "location": location,
                "output": output
            }
        )
        data = response.json()
        if data["status"] == "1":
            return data["regeocode"]
        else:
            raise Exception(f"Reverse geocode failed: {data['info']}")

@app.tool()
async def walking_direction(origin: str, destination: str, output: str = "json") -> dict:
    """
    步行路径规划API

    Args:
        origin: 起点经纬度 (例如 "116.481028,39.989643")
        destination: 终点经纬度 (例如 "116.434446,39.90816")
        output: 返回数据格式 (默认 "json")

    Returns:
        步行路径规划结果，包括距离、时长和详细步骤
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AMAP_BASE_URL}/direction/walking",
            params={
                "key": AMAP_KEY,
                "origin": origin,
                "destination": destination,
                "output": output
            }
        )
        data = response.json()
        if data["status"] == "1":
            return data["route"]
        else:
            raise Exception(f"Walking direction failed: {data['info']}")

@app.tool()
async def transit_direction(origin: str, destination: str, city: str, extensions: str = "base", strategy: str = "0", nightflag: str = "0", date: str = "", time: str = "", output: str = "json") -> dict:
    """
    公交路径规划API

    Args:
        origin: 起点经纬度 (例如 "116.481028,39.989643")
        destination: 终点经纬度 (例如 "116.434446,39.90816")
        city: 起点所在城市 (例如 "北京")
        extensions: 返回信息类型 ("base" 或 "all", 默认 "base")
        strategy: 路径规划策略 (可选值: 0-最快捷模式, 1-最经济模式, 2-最少换乘模式, 3-最少步行模式, 5-不乘地铁模式)
        nightflag: 是否计算夜班车 ("0" 或 "1", 默认 "0")
        date: 出发日期 (格式: "YYYY-MM-DD", 可选)
        time: 出发时间 (格式: "HH:mm", 可选)
        output: 返回数据格式 (默认 "json")

    Returns:
        公交路径规划结果，包括换乘方案、距离、时长和详细步骤
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "origin": origin,
            "destination": destination,
            "city": city,
            "extensions": extensions,
            "strategy": strategy,
            "nightflag": nightflag,
            "output": output
        }
        if date:
            params["date"] = date
        if time:
            params["time"] = time

        response = await client.get(
            f"{AMAP_BASE_URL}/direction/transit/integrated",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["route"]
        else:
            raise Exception(f"Transit direction failed: {data['info']}")

@app.tool()
async def bicycling_direction(origin: str, destination: str, output: str = "json") -> dict:
    """
    骑行路径规划API

    Args:
        origin: 起点经纬度 (例如 "116.481028,39.989643")
        destination: 终点经纬度 (例如 "116.434446,39.90816")
        output: 返回数据格式 (默认 "json")

    Returns:
        骑行路径规划结果，包括距离、时长和详细步骤
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AMAP_BASE_URL}/direction/bicycling",
            params={
                "key": AMAP_KEY,
                "origin": origin,
                "destination": destination,
                "output": output
            }
        )
        data = response.json()
        if data["errcode"] == 0:
            return data["data"]
        else:
            raise Exception(f"Bicycling direction failed: {data['errmsg']}")

@app.tool()
async def electrobike_direction(origin: str, destination: str, show_fields: str = "", output: str = "json") -> dict:
    """
    电动车路径规划API

    Args:
        origin: 起点经纬度 (例如 "116.481028,39.989643")
        destination: 终点经纬度 (例如 "116.434446,39.90816")
        show_fields: 返回结果控制字段 (可选)
        output: 返回数据格式 (默认 "json")

    Returns:
        电动车路径规划结果，包括距离、时长和详细步骤
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "origin": origin,
            "destination": destination,
            "output": output
        }
        if show_fields:
            params["show_fields"] = show_fields

        response = await client.get(
            f"{AMAP_BASE_URL}/direction/electrobike",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["route"]
        else:
            raise Exception(f"Electrobike direction failed: {data['info']}")

@app.tool()
async def driving_direction(origin: str, destination: str, extensions: str = "base", strategy: str = "", waypoints: str = "", avoidpolygons: str = "", avoidroad: str = "", output: str = "json") -> dict:
    """
    驾车路径规划API

    Args:
        origin: 起点经纬度 (例如 "116.481028,39.989643")
        destination: 终点经纬度 (例如 "116.434446,39.90816")
        extensions: 返回信息类型 ("base" 或 "all", 默认 "base")
        strategy: 路径规划策略 (可选)
        waypoints: 途经点 (最多16个坐标点，格式："lon,lat;lon,lat")
        avoidpolygons: 避让区域 (最多32个区域，每个区域最多16个顶点)
        avoidroad: 避让道路 (仅支持一条)
        output: 返回数据格式 (默认 "json")

    Returns:
        驾车路径规划结果，包括距离、时长和详细步骤
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "origin": origin,
            "destination": destination,
            "extensions": extensions,
            "output": output
        }
        if strategy:
            params["strategy"] = strategy
        if waypoints:
            params["waypoints"] = waypoints
        if avoidpolygons:
            params["avoidpolygons"] = avoidpolygons
        if avoidroad:
            params["avoidroad"] = avoidroad

        response = await client.get(
            f"{AMAP_BASE_URL}/direction/driving",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["route"]
        else:
            raise Exception(f"Driving direction failed: {data['info']}")

@app.tool()
async def district_query(keywords: str, subdistrict: str = "0", page: str = "1", offset: str = "", extensions: str = "base", filter: str = "", output: str = "json") -> dict:
    """
    行政区域查询API

    Args:
        keywords: 查询关键字 (例如 "山东")
        subdistrict: 子级行政区级数 ("0" 不返回下级行政区；"1" 返回下一级；"2" 返回下两级；"3" 返回下三级)
        page: 数据页码 (默认 "1")
        offset: 最外层返回数据个数 (可选)
        extensions: 返回结果控制 ("base" 或 "all", 默认 "base")
        filter: 按指定行政区划过滤 (adcode, 可选)
        output: 返回数据格式 (默认 "json")

    Returns:
        行政区域查询结果，包括行政区列表和详细信息
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "keywords": keywords,
            "subdistrict": subdistrict,
            "page": page,
            "extensions": extensions,
            "output": output
        }
        if offset:
            params["offset"] = offset
        if filter:
            params["filter"] = filter

        response = await client.get(
            f"{AMAP_BASE_URL}/config/district",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["districts"]
        else:
            raise Exception(f"District query failed: {data['info']}")

@app.tool()
async def keyword_search(keywords: str, types: str, city: str = "", citylimit: str = "false", children: str = "0", offset: str = "20", page: str = "1", extensions: str = "base", output: str = "json") -> dict:
    """
    关键字搜索API

    Args:
        keywords: 查询关键字 (例如 "北京大学")
        types: 查询POI类型 (分类代码或汉字)
        city: 查询城市 (可选, 示例："北京")
        citylimit: 是否仅返回指定城市数据 ("true" 或 "false", 默认 "false")
        children: 是否按照层级展示子POI数据 ("0" 显示所有子POI；"1" 归类到父POI之中, 默认 "0")
        offset: 每页记录数据 (默认 "20")
        page: 当前页数 (默认 "1")
        extensions: 返回结果控制 ("base" 或 "all", 默认 "base")
        output: 返回数据格式 (默认 "json")

    Returns:
        关键字搜索结果，包括POI信息列表
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "keywords": keywords,
            "types": types,
            "offset": offset,
            "page": page,
            "extensions": extensions,
            "output": output
        }
        if city:
            params["city"] = city
        if citylimit:
            params["citylimit"] = citylimit
        if children:
            params["children"] = children

        response = await client.get(
            f"{AMAP_BASE_URL}/place/text",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["pois"]
        else:
            raise Exception(f"Keyword search failed: {data['info']}")

@app.tool()
async def around_search(location: str, types: str, keywords: str = "", radius: str = "1000", sortrule: str = "distance", offset: str = "20", page: str = "1", extensions: str = "base", output: str = "json") -> dict:
    """
    周边搜索API

    Args:
        location: 中心点坐标 (例如 "116.473168,39.993015")
        types: 查询POI类型 (分类代码或汉字)
        keywords: 查询关键字 (可选)
        radius: 查询半径 (默认 "1000")
        sortrule: 排序规则 ("distance" 按距离排序；"weight" 综合排序，默认 "distance")
        offset: 每页记录数据 (默认 "20")
        page: 当前页数 (默认 "1")
        extensions: 返回结果控制 ("base" 或 "all", 默认 "base")
        output: 返回数据格式 (默认 "json")

    Returns:
        周边搜索结果，包括POI信息列表
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "location": location,
            "types": types,
            "radius": radius,
            "sortrule": sortrule,
            "offset": offset,
            "page": page,
            "extensions": extensions,
            "output": output
        }
        if keywords:
            params["keywords"] = keywords

        response = await client.get(
            f"{AMAP_BASE_URL}/place/around",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["pois"]
        else:
            raise Exception(f"Around search failed: {data['info']}")

@app.tool()
async def polygon_search(polygon: str, types: str, keywords: str = "", offset: str = "20", page: str = "1", extensions: str = "base", output: str = "json") -> dict:
    """
    多边形搜索API

    Args:
        polygon: 经纬度坐标对 (例如 "116.460988,40.006919|116.48231,40.007381;116.47516,39.99713|116.472596,39.985227|116.45669,39.984989|116.460988,40.006919")
        types: 查询POI类型 (分类代码或汉字)
        keywords: 查询关键字 (可选)
        offset: 每页记录数据 (默认 "20")
        page: 当前页数 (默认 "1")
        extensions: 返回结果控制 ("base" 或 "all", 默认 "base")
        output: 返回数据格式 (默认 "json")

    Returns:
        多边形搜索结果，包括POI信息列表
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "polygon": polygon,
            "types": types,
            "offset": offset,
            "page": page,
            "extensions": extensions,
            "output": output
        }
        if keywords:
            params["keywords"] = keywords

        response = await client.get(
            f"{AMAP_BASE_URL}/place/polygon",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["pois"]
        else:
            raise Exception(f"Polygon search failed: {data['info']}")

@app.tool()
async def id_query(id: str, sig: str = "", callback: str = "", output: str = "json") -> dict:
    """
    ID查询API

    Args:
        id: POI唯一标识 (例如 "B0FFFAB6J2")
        sig: 数字签名 (可选)
        callback: 回调函数名称 (可选)
        output: 返回数据格式 (默认 "json")

    Returns:
        ID查询结果，包括POI详细信息
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "id": id,
            "output": output
        }
        if sig:
            params["sig"] = sig
        if callback:
            params["callback"] = callback

        response = await client.get(
            f"{AMAP_BASE_URL}/place/detail",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["pois"]
        else:
            raise Exception(f"ID query failed: {data['info']}")

@app.tool()
async def traffic_event_query(adcode: str, client_key: str, timestamp: str, digest: str, event_type: str, is_expressway: str, output: str = "json") -> dict:
    """
    交通事件查询API

    Args:
        adcode: 城市代码 (例如 "110000")
        client_key: 请求服务权限标识 (用户申请的Web服务API类型KEY)
        timestamp: 时间戳 (秒单位，例如 "1621243952")
        digest: 鉴权动态密钥 (计算出的动态鉴权信息)
        event_type: 事件类型 (多个类型用";"分割)
        is_expressway: 是否高速 ("1" 是；"0" 否)
        output: 返回数据格式 (默认 "json")

    Returns:
        交通事件查询结果，包括事件详细信息列表
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "adcode": adcode,
            "clientKey": client_key,
            "timestamp": timestamp,
            "digest": digest,
            "eventType": event_type,
            "isExpressway": is_expressway,
            "output": output
        }

        response = await client.get(
            f"{AMAP_BASE_URL}/event/queryByAdcode",
            params=params
        )
        data = response.json()
        if data["code"] == 1:
            return data["data"]
        else:
            raise Exception(f"Traffic event query failed: {data['msg']}")

@app.tool()
async def ip_location(ip: str = "", sig: str = "", output: str = "json") -> dict:
    """
    IP定位API

    Args:
        ip: 需要搜索的IP地址 (可选)
        sig: 签名 (选择数字签名认证的付费用户必填)
        output: 返回数据格式 (默认 "json")

    Returns:
        IP定位结果，包括省份名称、城市名称、adcode编码和所在城市矩形区域范围
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "output": output
        }
        if ip:
            params["ip"] = ip
        if sig:
            params["sig"] = sig

        response = await client.get(
            f"{AMAP_BASE_URL}/ip",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return {
                "province": data["province"],
                "city": data["city"],
                "adcode": data["adcode"],
                "rectangle": data["rectangle"]
            }
        else:
            raise Exception(f"IP location failed: {data['info']}")

@app.tool()
async def weather_query(city: str, extensions: str = "base", output: str = "json") -> dict:
    """
    天气查询API

    Args:
        city: 城市编码 (例如 "110101")
        extensions: 气象类型 ("base" 返回实况天气；"all" 返回预报天气，默认 "base")
        output: 返回数据格式 (默认 "json")

    Returns:
        天气查询结果，包括实况或预报天气信息
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "city": city,
            "extensions": extensions,
            "output": output
        }

        response = await client.get(
            f"{AMAP_BASE_URL}/weather/weatherInfo",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data.get("lives", []) if extensions == "base" else data.get("forecasts", [])
        else:
            raise Exception(f"Weather query failed: {data['info']}")

@app.tool()
async def input_tips(keywords: str, type: str = "", location: str = "", city: str = "", citylimit: str = "false", datatype: str = "all", sig: str = "", output: str = "json", callback: str = "") -> dict:
    """
    输入提示API

    Args:
        keywords: 查询关键词 (例如 "肯德基")
        type: POI分类 (服务可支持传入多个分类，多个类型用“|”分隔，可选值：POI分类名称、分类代码)
        location: 坐标 (格式："X,Y"（经度,纬度），不可以包含空格)
        city: 搜索城市 (可选值：citycode、adcode，默认为空)
        citylimit: 仅返回指定城市数据 ("true" 或 "false"，默认 "false")
        datatype: 返回的数据类型 (多种数据类型用“|”分隔，可选值：all-返回所有数据类型、poi-返回POI数据类型、bus-返回公交站点数据类型、busline-返回公交线路数据类型)
        sig: 数字签名 (可选)
        output: 返回数据格式 (默认 "json")
        callback: 回调函数名称 (可选)

    Returns:
        输入提示结果，包括建议提示列表
    """
    async with httpx.AsyncClient() as client:
        params = {
            "key": AMAP_KEY,
            "keywords": keywords,
            "datatype": datatype,
            "output": output
        }
        if type:
            params["type"] = type
        if location:
            params["location"] = location
        if city:
            params["city"] = city
        if citylimit:
            params["citylimit"] = citylimit
        if sig:
            params["sig"] = sig
        if callback and output == "json":
            params["callback"] = callback

        response = await client.get(
            f"{AMAP_BASE_URL}/assistant/inputtips",
            params=params
        )
        data = response.json()
        if data["status"] == "1":
            return data["tips"]
        else:
            raise Exception(f"Input tips failed: {data['info']}")

if __name__ == "__main__":
    app.run(transport="sse")
