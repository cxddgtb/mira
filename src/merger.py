import glob
from pathlib import Path
from typing import List, Dict
from loguru import logger
from src.utils import load_json, save_json, ARCHIVE_DIR, generate_archive_name

def merge_data(new_apis: List[Dict]) -> List[Dict]:
    archive_files = sorted(glob.glob(str(ARCHIVE_DIR / "archive_*.json")))
    recent_files = archive_files[-10:] if len(archive_files) >= 10 else archive_files
    
    history_data = []
    for f in recent_files:
        history_data.extend(load_json(Path(f)))
    
    logger.info(f"📂 加载历史: {len(recent_files)} 文件 → {len(history_data)} 条")
    
    combined = new_apis + history_data
    
    # 严格去重：以 url 为唯一键
    seen = {}
    for item in combined:
        key = item["url"]
        if key not in seen:
            seen[key] = item
    
    unique_data = list(seen.values())
    unique_data.sort(key=lambda x: x.get("added_at", 0), reverse=True)
    
    logger.info(f"🔄 合并去重后: {len(unique_data)} 条（中文无损）")
    return unique_data

def save_merged_data(final_ List[Dict]):
    archive_name = generate_archive_name()
    save_json(ARCHIVE_DIR / archive_name, final_data)
    save_json(Path("data/latest.json"), final_data)
    logger.success("💾 滚雪球归档完成 | latest.json 已同步")
