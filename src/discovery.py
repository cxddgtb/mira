import time
import random
import requests
from typing import List, Dict
from loguru import logger

SEARCH_CONFIGS = [
    {"query": "filename:index.js tvbox 影视", "category": "vod"},
    {"query": "filename:api.js.md5 直播", "category": "live"},
    {"query": "ext:js basic auth 云播", "category": "vod"},
    {"query": "filename:live.json m3u8 直播源", "category": "live"},
    {"query": "filename:music.js audio 音乐", "category": "music"},
    {"query": "filename:book.md5 有声小说", "category": "book"},
    {"query": "extension:json \"vod\" \"list\" tvbox", "category": "vod"},
    {"query": "filename:iptv.m3u8 直播", "category": "live"},
]

def fetch_github_results(query: str) -> List[Dict]:
    url = f"https://api.github.com/search/code?q={query}&per_page=30"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MiraPlay-Collector/1.0"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        logger.info(f"🔍 搜索 '{query}' → {len(items)} 个结果")
        return items
    except Exception as e:
        logger.warning(f"GitHub 搜索失败 '{query}': {e}")
        return []

def build_raw_url(item: dict) -> str:
    repo = item.get("repository", {})
    full_name = repo.get("full_name", "")
    if not full_name:
        return ""
    owner, repo_name = full_name.split("/", 1)
    path = item.get("path", "")
    return f"https://raw.githubusercontent.com/{owner}/{repo_name}/main/{path}"

def run_discovery() -> List[Dict]:
    logger.info("🌐 启动 Mira Play 专用发现引擎...")
    candidates = []
    
    for cfg in SEARCH_CONFIGS:
        items = fetch_github_results(cfg["query"])
        for item in items:
            url = build_raw_url(item)
            if not url:
                continue
            filename = item.get("name", "").lower()
            file_type = "json"
            if any(filename.endswith(ext) for ext in [".js", ".md5"]):
                file_type = "js"
            elif filename.endswith(".m3u8") or filename.endswith(".m3u"):
                file_type = "m3u"
            elif filename.endswith(".json"):
                file_type = "json"
                
            candidates.append({
                "url": url,
                "category": cfg["category"],  # vod/live/music/book
                "file_type": file_type,
                "source": "github_auto",
                "added_at": time.time(),
                "original_filename": filename
            })
        time.sleep(random.uniform(9, 13))
    
    seen = set()
    unique = []
    for c in candidates:
        if c["url"] not in seen:
            seen.add(c["url"])
            unique.append(c)
            
    logger.success(f"✨ 发现引擎结束: {len(unique)} 个候选接口")
    return unique
