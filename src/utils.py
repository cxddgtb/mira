import os
import json
import re
import hashlib
from pathlib import Path
from loguru import logger
from datetime import datetime

DATA_DIR = Path("data")
ARCHIVE_DIR = DATA_DIR / "archives"

def ensure_dirs():
    """自动创建数据目录"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path: Path) -> list:
    """安全读取 JSON，失败返回空列表"""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning(f"读取 {path} 失败: {e}")
        return []

def save_json(path: Path,  list):
    """保存 JSON，确保中文不转义"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已保存: {path} (共 {len(data)} 条)")

def generate_archive_name() -> str:
    return f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def extract_json_from_js(content: str):
    """从 JS/MD5 文件中提取 JSON 数据"""
    try:
        data = json.loads(content.strip())
        if isinstance(data, (list, dict)):
            return data
    except:
        pass
    
    patterns = [
        r'\{[\s\S]*"vod"[^}]*\}',
        r'\[[\s\S]*"name"[^\]]*\]',
        r'var\s+\w+\s*=\s*(\{[\s\S]*\});',
        r'export\s+default\s+(\{[\s\S]*\});',
        r'JSON\.parse\s*\(\s*`([\s\S]*?)`\s*\)',
        r'JSON\.parse\s*\(\s*"([\s\S]*?)"\s*\)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            try:
                json_str = match.group(1) if match.lastindex else match.group(0)
                data = json.loads(json_str)
                if isinstance(data, (list, dict)):
                    return data
            except:
                continue
    return None

def extract_chinese_name(item: dict) -> str:
    """优先提取原始中文字段作为接口名称"""
    for key in ["name", "title", "备注", "名称", "站点", "source_name", "desc", "label"]:
        if key in item and isinstance(item[key], str) and item[key].strip():
            if re.search(r'[\u4e00-\u9fff]', item[key]):
                return item[key].strip()
    url = item.get("url", "")
    if url:
        domain = re.search(r'@?([^/@:\?#]+)(?:[:/]|$)', url)
        if domain:
            return domain.group(1)
    return "未命名接口"

def generate_unique_key(name: str, url: str) -> str:
    """生成 TVBox 兼容的唯一 key（MD5 哈希）"""
    raw = f"{name}:{url}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]

def format_js_config(sites: list, lives: list) -> str:
    """
    生成 Mira Play / TVBox 标准 JS 配置格式
    输出内容可直接被 index.js.md5 订阅解析
    """
    # 构建标准配置对象
    config = {
        "sites": sites,
        "lives": lives,
        "parses": [],  # 解析接口（可扩展）
        "flags": ["youku", "qq", "iqiyi", "qiyi", "letv", "sohu", "tudou", "pptv", "mgtv", "wasu", "bilibili", "renrenmi"],
        "wallpaper": "https://api.likepoems.com/img/bing",  # 可选壁纸
        "spider": ""  # 可选爬虫插件
    }
    
    # 转为紧凑 JSON（Mira Play 兼容性更好）
    json_str = json.dumps(config, ensure_ascii=False, separators=(',', ':'))
    
    # 包装为 JS 模块格式（兼容 export default / module.exports）
    js_content = f'''// MiraPlay Config - Auto Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 接口总数: {len(sites)} 点播 + {len(lives)} 直播
// 滚雪球存档 | 中文无损 | Basic Auth 支持

var config = {json_str};

// 兼容多种导出方式
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = config;
}}
if (typeof export !== 'undefined') {{
    export default config;
}}
'''
    return js_content
