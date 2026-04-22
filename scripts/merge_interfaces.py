#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 整合脚本
用于从多个 CatPawOpen 协议的接口源中提取、合并配置，生成统一的 index.config.js
"""

import json
import re
import hashlib
import os
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 配置：上游接口源列表
UPSTREAM_SOURCES = [
    {
        "name": "王二小 (蓝光首选)",
        "config_url": "http://tvbox.王二小放牛娃.top/index.config.js.md5",
        "js_url": "http://tvbox.王二小放牛娃.top/index.js.md5",
        "priority": 100,
    },
    {
        "name": "Jsnzkpg 开发者源",
        "config_url": "https://raw.githubusercontent.com/Jsnzkpg/stymei/Jsnzkpg/index.config.js.md5",
        "js_url": "https://raw.githubusercontent.com/Jsnzkpg/stymei/Jsnzkpg/index.js.md5",
        "priority": 90,
    },
    {
        "name": "9280 公益源",
        "config_url": "https://9280.kstore.vip/cat/index.config.js.md5",
        "js_url": "https://9280.kstore.vip/cat/index.js.md5",
        "priority": 80,
    },
    {
        "name": "Jadehh 爬虫源",
        "config_url": "https://gitee.com/jadehh_743/TVSpider/raw/master/dist/index.config.js.md5",
        "js_url": "https://gitee.com/jadehh_743/TVSpider/raw/master/dist/index.js.md5",
        "priority": 70,
    },
]

OUTPUT_DIR = Path(__file__).parent.parent / "dist"


def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """从 URL 获取内容"""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"⚠️  获取 {url} 失败: {e}", file=sys.stderr)
        return None


def extract_config_from_js(js_content: str) -> Optional[Dict[str, Any]]:
    """
    从 index.js 中提取配置对象
    CatPawOpen 的 index.js 通常包含 globalThis.danmuBundle 和其他配置
    """
    try:
        # 尝试找到 index_config_default 或类似的配置对象
        # 这是一个简化的正则匹配，实际可能需要更复杂的 AST 解析
        pattern = r"var\s+index_config_default\s*=\s*(\{[^}]*?(?:\{[^}]*\}[^}]*)*\})"
        match = re.search(pattern, js_content, re.DOTALL)
        
        if match:
            config_str = match.group(1)
            # 简单的 JSON 化处理（可能需要手动调整）
            return json.loads(config_str)
    except Exception as e:
        print(f"⚠️  解析 JS 配置失败: {e}", file=sys.stderr)
    
    return None


def parse_config_js(content: str) -> Optional[Dict[str, Any]]:
    """
    解析 index.config.js 文件内容
    尝试多种方式提取配置对象
    """
    try:
        # 方法1：直接 JSON 解析（如果是 JSON 格式）
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 方法2：提取 JavaScript 对象
        # 寻找 module.exports = { ... } 或 export default { ... }
        patterns = [
            r"module\.exports\s*=\s*(\{.*\})",
            r"export\s+default\s+(\{.*\})",
            r"var\s+\w+\s*=\s*(\{.*\})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                obj_str = match.group(1)
                # 尝试转换为有效的 JSON
                # 移除尾部逗号、单引号等
                obj_str = re.sub(r",\s*([}\]])", r"\1", obj_str)  # 移除尾部逗号
                obj_str = obj_str.replace("'", '"')  # 单引号转双引号
                
                try:
                    return json.loads(obj_str)
                except json.JSONDecodeError:
                    pass
        
        return None
    except Exception as e:
        print(f"⚠️  解析配置失败: {e}", file=sys.stderr)
        return None


def merge_sources(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    合并多个源的配置
    去重、按优先级排序
    """
    merged_config = {
        "sites": [],
        "parses": [],
        "flags": [],
        "ijk": [],
        "ads": [],
        "wallpaper": "",
        "spider": "",
        "lives": [],
    }
    
    seen_sites = set()
    seen_parses = set()
    
    # 按优先级排序
    sources.sort(key=lambda x: x.get("priority", 0), reverse=True)
    
    for source in sources:
        config = source.get("config", {})
        
        # 合并 sites（去重）
        for site in config.get("sites", []):
            site_key = (site.get("key"), site.get("name"))
            if site_key not in seen_sites:
                merged_config["sites"].append(site)
                seen_sites.add(site_key)
        
        # 合并 parses（去重）
        for parse in config.get("parses", []):
            parse_key = parse.get("name")
            if parse_key not in seen_parses:
                merged_config["parses"].append(parse)
                seen_parses.add(parse_key)
        
        # 合并其他字段
        merged_config["flags"].extend(config.get("flags", []))
        merged_config["ijk"].extend(config.get("ijk", []))
        merged_config["ads"].extend(config.get("ads", []))
        merged_config["lives"].extend(config.get("lives", []))
    
    # 去重 flags, ijk, ads, lives
    merged_config["flags"] = list({json.dumps(x, sort_keys=True) for x in merged_config["flags"]})
    merged_config["flags"] = [json.loads(x) for x in merged_config["flags"]]
    
    merged_config["ijk"] = list({json.dumps(x, sort_keys=True) for x in merged_config["ijk"]})
    merged_config["ijk"] = [json.loads(x) for x in merged_config["ijk"]]
    
    merged_config["ads"] = list({json.dumps(x, sort_keys=True) for x in merged_config["ads"]})
    merged_config["ads"] = [json.loads(x) for x in merged_config["ads"]]
    
    merged_config["lives"] = list({json.dumps(x, sort_keys=True) for x in merged_config["lives"]})
    merged_config["lives"] = [json.loads(x) for x in merged_config["lives"]]
    
    return merged_config


def generate_md5(content: str) -> str:
    """生成 MD5 校验值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def main():
    """主流程"""
    print("🚀 MiraPlay 接口整合工作流启动...")
    print(f"📅 时间: {datetime.now().isoformat()}\n")
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 第1步：从上游源获取配置
    print("📥 第1步: 从上游源获取配置...")
    sources_with_config = []
    
    for source in UPSTREAM_SOURCES:
        print(f"  - 正在获取 {source['name']}...")
        
        # 获取配置文件
        config_content = fetch_url(source["config_url"])
        if not config_content:
            print(f"    ⚠️  跳过 {source['name']} (配置获取失败)")
            continue
        
        # 解析配置
        config = parse_config_js(config_content)
        if not config:
            print(f"    ⚠️  跳过 {source['name']} (配置解析失败)")
            continue
        
        source["config"] = config
        sources_with_config.append(source)
        print(f"    ✅ 成功获取 {len(config.get('sites', []))} 个源")
    
    if not sources_with_config:
        print("❌ 没有成功获取任何源配置！")
        sys.exit(1)
    
    print(f"\n✅ 成功获取 {len(sources_with_config)} 个源\n")
    
    # 第2步：合并配置
    print("🔀 第2步: 合并配置...")
    merged_config = merge_sources(sources_with_config)
    print(f"  - 合并后共有 {len(merged_config['sites'])} 个源")
    print(f"  - 合并后共有 {len(merged_config['parses'])} 个解析器\n")
    
    # 第3步：生成输出文件
    print("💾 第3步: 生成输出文件...")
    
    # 生成 index.config.js
    config_js_content = f"""// MiraPlay Interface Aggregator
// 生成时间: {datetime.now().isoformat()}
// 源数量: {len(sources_with_config)}

var index_config_default = {json.dumps(merged_config, ensure_ascii=False, indent=2)};

module.exports = index_config_default;
"""
    
    config_js_path = OUTPUT_DIR / "index.config.js"
    with open(config_js_path, "w", encoding="utf-8") as f:
        f.write(config_js_content)
    print(f"  ✅ 生成 {config_js_path}")
    
    # 生成 index.config.js.md5
    config_md5 = generate_md5(config_js_content)
    config_md5_path = OUTPUT_DIR / "index.config.js.md5"
    with open(config_md5_path, "w") as f:
        f.write(config_md5)
    print(f"  ✅ 生成 {config_md5_path} (MD5: {config_md5})")
    
    # 生成元数据文件
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "sources": [
            {
                "name": s["name"],
                "priority": s["priority"],
                "sites_count": len(s.get("config", {}).get("sites", [])),
            }
            for s in sources_with_config
        ],
        "merged_stats": {
            "total_sites": len(merged_config["sites"]),
            "total_parses": len(merged_config["parses"]),
            "total_flags": len(merged_config["flags"]),
            "total_ijk": len(merged_config["ijk"]),
            "total_ads": len(merged_config["ads"]),
            "total_lives": len(merged_config["lives"]),
        },
    }
    
    metadata_path = OUTPUT_DIR / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 生成 {metadata_path}\n")
    
    # 第4步：输出统计信息
    print("📊 整合统计:")
    for source in sources_with_config:
        print(f"  - {source['name']}: {source.get('config', {}).get('sites', []).__len__()} 个源")
    print(f"\n  总计: {len(merged_config['sites'])} 个源")
    print(f"  解析器: {len(merged_config['parses'])} 个")
    print(f"\n✅ 整合完成！")
    print(f"📍 输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
