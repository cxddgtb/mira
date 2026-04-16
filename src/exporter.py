from pathlib import Path
from typing import List, Dict
from loguru import logger
from src.utils import format_js_config, generate_unique_key

def convert_to_mira_sites(apis: List[Dict]) -> List[Dict]:
    """将内部格式转换为 Mira Play / TVBox 标准 sites 格式"""
    sites = []
    for api in apis:
        if api.get("category") != "vod":
            continue  # 非点播接口跳过
        sites.append({
            "key": generate_unique_key(api["name"], api["url"]),
            "name": api["name"],  # ✅ 原始中文名
            "type": 3,  # 3=JSON 接口 (TVBox 标准)
            "api": api["url"],  # ✅ 保留 Basic Auth: http://user:pass@host/...
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
            "ext": ""
        })
    return sites

def convert_to_mira_lives(apis: List[Dict]) -> List[Dict]:
    """将内部格式转换为 Mira Play / TVBox 标准 lives 格式"""
    lives = []
    for api in apis:
        if api.get("category") != "live":
            continue
        lives.append({
            "name": api["name"],  # ✅ 原始中文名
            "url": api["url"],  # ✅ 支持 m3u8 / Basic Auth
            "type": 0,  # 0=m3u8 直播源
            "playerType": 1,  # 1=系统播放器
            "ua": "Mozilla/5.0",  # 可选 User-Agent
            "epg": ""  # 可选节目单
        })
    return lives

def generate_index_js_md5(final_ List[Dict], output_path: Path):
    """生成 Mira Play 可直接订阅的 index.js.md5 文件"""
    # 分类转换
    sites = convert_to_mira_sites(final_data)  # 点播接口
    lives = convert_to_mira_lives(final_data)  # 直播源
    
    # 生成 JS 配置内容
    js_content = format_js_config(sites, lives)
    
    # 写入文件（.js.md5 后缀，内容仍是有效 JS）
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    logger.success(f"🎯 已生成 Mira Play 订阅文件: {output_path}")
    logger.info(f"   ├─ 点播接口: {len(sites)} 个")
    logger.info(f"   ├─ 直播源: {len(lives)} 个")
    logger.info(f"   └─ 文件编码: UTF-8 (中文无损)")

def run_exporter(final_ List[Dict]):
    """执行导出流程"""
    data_dir = Path("data")
    output_file = data_dir / "index.js.md5"  # ✅ Mira Play 订阅文件名
    
    generate_index_js_md5(final_data, output_file)
    
    # 同时保留原始 JSON 备份（可选）
    save_json_path = data_dir / "latest_backup.json"
    with open(save_json_path, "w", encoding="utf-8") as f:
        import json
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 原始数据备份: {save_json_path}")
