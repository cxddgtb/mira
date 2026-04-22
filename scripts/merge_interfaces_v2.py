#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 整合脚本 v2
改进版本：支持本地测试、更好的错误处理、支持多种配置格式
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
import ssl

# 禁用 SSL 证书验证（仅用于测试）
ssl._create_default_https_context = ssl._create_unverified_context

# 配置：上游接口源列表
UPSTREAM_SOURCES = [
    {
        "name": "王二小 (蓝光首选)",
        "config_url": "http://tvbox.王二小放牛娃.top/index.config.js",
        "priority": 100,
    },
    {
        "name": "Jsnzkpg 开发者源",
        "config_url": "https://raw.githubusercontent.com/Jsnzkpg/stymei/Jsnzkpg/index.config.js",
        "priority": 90,
    },
    {
        "name": "9280 公益源",
        "config_url": "https://9280.kstore.vip/cat/index.config.js",
        "priority": 80,
    },
    {
        "name": "Jadehh 爬虫源",
        "config_url": "https://gitee.com/jadehh_743/TVSpider/raw/master/dist/index.config.js",
        "priority": 70,
    },
]

OUTPUT_DIR = Path(__file__).parent.parent / "dist"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"


def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """从 URL 获取内容"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            # 尝试多种编码
            for encoding in ["utf-8", "gbk", "gb2312", "latin-1"]:
                try:
                    return content.decode(encoding)
                except (UnicodeDecodeError, AttributeError):
                    continue
            return content.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"⚠️  获取 {url} 失败: {e}", file=sys.stderr)
        return None


def parse_js_config(content: str) -> Optional[Dict[str, Any]]:
    """
    解析 JavaScript 配置文件
    支持多种格式：
    - module.exports = {...}
    - export default {...}
    - var xxx = {...}
    """
    try:
        # 方法1：直接 JSON 解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 方法2：提取 JavaScript 对象
        patterns = [
            r"var\s+\w+\s*=\s*(\{[\s\S]*\});",
            r"module\.exports\s*=\s*(\{[\s\S]*\});",
            r"export\s+default\s+(\{[\s\S]*\});",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                obj_str = match.group(1)
                # 清理 JavaScript 对象，使其成为有效的 JSON
                obj_str = clean_js_object(obj_str)

                try:
                    return json.loads(obj_str)
                except json.JSONDecodeError as e:
                    print(f"  ⚠️  JSON 解析失败: {e}", file=sys.stderr)
                    continue

        return None
    except Exception as e:
        print(f"⚠️  解析配置失败: {e}", file=sys.stderr)
        return None


def clean_js_object(obj_str: str) -> str:
    """清理 JavaScript 对象，使其成为有效的 JSON"""
    # 移除注释
    obj_str = re.sub(r"//.*?$", "", obj_str, flags=re.MULTILINE)
    obj_str = re.sub(r"/\*[\s\S]*?\*/", "", obj_str)

    # 移除尾部逗号
    obj_str = re.sub(r",\s*([}\]])", r"\1", obj_str)

    # 单引号转双引号（简单处理）
    obj_str = re.sub(r"'([^']*)'", r'"\1"', obj_str)

    # 处理未引用的键名
    obj_str = re.sub(r'(\{|,)\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', obj_str)

    return obj_str


def merge_sources(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """合并多个源的配置"""
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

    seen_sites = {}  # key -> (priority, site)
    seen_parses = {}  # name -> (priority, parse)

    # 按优先级排序
    sources.sort(key=lambda x: x.get("priority", 0), reverse=True)

    for source in sources:
        config = source.get("config", {})
        priority = source.get("priority", 0)

        # 合并 sites（按优先级去重）
        for site in config.get("sites", []):
            key = site.get("key")
            if key:
                if key not in seen_sites or seen_sites[key][0] < priority:
                    seen_sites[key] = (priority, site)

        # 合并 parses（按优先级去重）
        for parse in config.get("parses", []):
            name = parse.get("name")
            if name:
                if name not in seen_parses or seen_parses[name][0] < priority:
                    seen_parses[name] = (priority, parse)

        # 合并其他字段
        merged_config["flags"].extend(config.get("flags", []))
        merged_config["ijk"].extend(config.get("ijk", []))
        merged_config["ads"].extend(config.get("ads", []))
        merged_config["lives"].extend(config.get("lives", []))

    # 提取去重后的 sites 和 parses
    merged_config["sites"] = [site for _, site in seen_sites.values()]
    merged_config["parses"] = [parse for _, parse in seen_parses.values()]

    # 去重其他字段
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
    print(f"📅 时间: {datetime.now().isoformat()}")
    print(f"🧪 测试模式: {'启用' if TEST_MODE else '禁用'}\n")

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
            print(f"    ⚠️  跳过 {source['name']} (获取失败)")
            continue

        # 解析配置
        config = parse_js_config(config_content)
        if not config:
            print(f"    ⚠️  跳过 {source['name']} (解析失败)")
            continue

        source["config"] = config
        sources_with_config.append(source)
        sites_count = len(config.get("sites", []))
        parses_count = len(config.get("parses", []))
        print(f"    ✅ 成功获取 {sites_count} 个源, {parses_count} 个解析器")

    if not sources_with_config:
        print("❌ 没有成功获取任何源配置！")
        if not TEST_MODE:
            sys.exit(1)
        else:
            print("⚠️  测试模式：使用本地测试配置")
            # 加载本地测试配置
            test_config_path = Path(__file__).parent / "test_config.json"
            if test_config_path.exists():
                with open(test_config_path, "r", encoding="utf-8") as f:
                    test_config = json.load(f)
                if test_config:
                    sources_with_config.append({
                        "name": "本地测试配置",
                        "config": test_config,
                        "priority": 100,
                    })
                    print(f"✅ 加载本地测试配置成功")
                else:
                    print("❌ 本地测试配置为空")
                    sys.exit(1)
            else:
                print("❌ 找不到本地测试配置文件")
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
                "parses_count": len(s.get("config", {}).get("parses", [])),
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
        sites = len(source.get("config", {}).get("sites", []))
        parses = len(source.get("config", {}).get("parses", []))
        print(f"  - {source['name']}: {sites} 个源, {parses} 个解析器")
    print(f"\n  总计: {len(merged_config['sites'])} 个源")
    print(f"  解析器: {len(merged_config['parses'])} 个")
    print(f"\n✅ 整合完成！")
    print(f"📍 输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
