import asyncio
import aiohttp
import json
import re
from typing import List, Dict
from loguru import logger
from src.utils import extract_json_from_js, extract_chinese_name, generate_unique_key

VALID_KEYS = {"vod", "data", "channels", "list", "tracks", "music", "audio", "title", "url", "play_url", "api", "source", "stream", "epg"}

async def test_single_api(session: aiohttp.ClientSession, api: Dict) -> Dict:
    url = api["url"]
    file_type = api.get("file_type", "json")
    category = api.get("category", "vod")
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=12), ssl=False) as resp:
            if resp.status == 404:
                alt_url = url.replace("/main/", "/master/")
                async with session.get(alt_url, timeout=aiohttp.ClientTimeout(total=12), ssl=False) as resp2:
                    if resp2.status == 200:
                        text = await resp2.text()
                        url = alt_url
                    else:
                        raise ValueError("分支不可用")
            elif resp.status != 200:
                raise ValueError(f"HTTP {resp.status}")
            else:
                text = await resp.text()
        
        if len(text.strip()) < 30:
            raise ValueError("响应内容过短")
        
        # 解析内容
        if file_type == "js":
            data = extract_json_from_js(text)
            if not 
                raise ValueError("无法从 JS/MD5 提取有效 JSON")
        elif file_type == "m3u":
            # M3U8 直播源，直接返回
            data = {"type": "m3u8", "content": text, "url": url, "category": "live"}
        else:
            data = json.loads(text)
        
        valid_items = []
        
        if isinstance(data, dict) and data.get("type") == "m3u8":
            # M3U8 直播源 → 转为 Mira Play live 格式
            valid_items.append({
                "name": extract_chinese_name(api),
                "url": url,
                "category": "live",
                "source": api["source"],
                "added_at": api["added_at"],
                "file_type": "m3u8",
                "status": "alive"
            })
        elif isinstance(data, dict):
            content = json.dumps(data, ensure_ascii=False)
            if not any(k in content for k in VALID_KEYS):
                raise ValueError("缺少媒体接口特征字段")
            
            items = []
            for key in ["vod", "data", "list", "channels", "sites", "api_list", "live"]:
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            if not items and (data.get("url") or data.get("api")):
                items = [data]
                
            for item in items:
                if not isinstance(item, dict):
                    continue
                item_url = item.get("url") or item.get("api") or item.get("play_url") or item.get("stream") or item.get("link")
                if not item_url or not isinstance(item_url, str) or not item_url.startswith("http"):
                    continue
                    
                # 智能分类：根据关键词判断是点播还是直播
                item_cat = category
                url_lower = item_url.lower()
                if any(k in url_lower for k in ["m3u", "m3u8", "live", "iptv", "channel"]):
                    item_cat = "live"
                elif any(k in url_lower for k in ["music", "audio", "song"]):
                    item_cat = "music"
                elif any(k in url_lower for k in ["book", "audiobook", "novel"]):
                    item_cat = "book"
                    
                chinese_name = extract_chinese_name(item)
                valid_items.append({
                    "name": chinese_name,
                    "url": item_url.strip(),
                    "category": item_cat,
                    "source": api["source"],
                    "added_at": api["added_at"],
                    "file_type": file_type,
                    "status": "alive"
                })
        elif isinstance(data, list):
            for item in 
                if not isinstance(item, dict):
                    continue
                item_url = item.get("url") or item.get("api") or item.get("play_url")
                if not item_url or not item_url.startswith("http"):
                    continue
                item_cat = category
                url_lower = item_url.lower()
                if any(k in url_lower for k in ["m3u", "m3u8", "live", "iptv"]):
                    item_cat = "live"
                chinese_name = extract_chinese_name(item)
                valid_items.append({
                    "name": chinese_name,
                    "url": item_url.strip(),
                    "category": item_cat,
                    "source": api["source"],
                    "added_at": api["added_at"],
                    "file_type": file_type,
                    "status": "alive"
                })
        
        if not valid_items:
            raise ValueError("未提取到有效子接口")
            
        api["url"] = valid_items[0]["url"]
        api["name"] = valid_items[0]["name"]
        api["status"] = "alive"
        api["extracted_count"] = len(valid_items)
        api["sub_items"] = valid_items
        return api
        
    except Exception as e:
        logger.debug(f"❌ 接口失效: {url} | {e}")
    
    api["status"] = "dead"
    return api

async def run_tester(raw_apis: List[Dict]) -> List[Dict]:
    if not raw_apis:
        logger.warning("⚠️ 无待测试数据")
        return []
    
    logger.info(f"🧪 开始异步测试 {len(raw_apis)} 个接口文件...")
    connector = aiohttp.TCPConnector(limit=25, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [test_single_api(session, api) for api in raw_apis]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_valid = []
    for res in results:
        if isinstance(res, dict) and res.get("status") == "alive":
            sub_items = res.get("sub_items", [])
            all_valid.extend(sub_items)
    
    logger.success(f"✅ 测试完成: 共提取 {len(all_valid)} 个有效接口（中文名称 100% 保留）")
    return all_valid
