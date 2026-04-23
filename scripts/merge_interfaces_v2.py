#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 整合脚本 v2
生成 index.config.js 和 index.js 两套文件
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

OUTPUT_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent

def generate_md5(content: str) -> str:
    """生成 MD5 校验值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_local_configs() -> List[Dict[str, Any]]:
    """加载本地配置文件"""
    configs = []
    for config_file in sorted(SCRIPTS_DIR.glob("test_config*.json")):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            configs.append({
                "name": config_file.stem,
                "config": config,
                "priority": 100 - len(configs) * 10,
            })
            print(f" ✅ 加载 {config_file.name}")
        except Exception as e:
            print(f" ⚠️ 加载 {config_file.name} 失败: {e}")
    return configs

def merge_configs(configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """合并多个配置"""
    merged = {
        "sites": [], "parses": [], "flags": [], "ijk": [],
        "ads": [], "wallpaper": "", "spider": "", "lives": [],
    }
    seen_sites = {}
    seen_parses = {}
    seen_flags = set()

    for source in configs:
        config = source.get("config", {})
        priority = source.get("priority", 0)

        for site in config.get("sites", []):
            key = site.get("key")
            if key and key not in seen_sites:
                seen_sites[key] = (priority, site)

        for parse in config.get("parses", []):
            name = parse.get("name")
            if name and name not in seen_parses:
                seen_parses[name] = (priority, parse)

        for flag in config.get("flags", []):
            try:
                flag_str = json.dumps(flag, sort_keys=True)
                if flag_str not in seen_flags:
                    seen_flags.add(flag_str)
                    merged["flags"].append(flag)
            except (TypeError, ValueError):
                merged["flags"].append(flag)

    merged["sites"] = [site for _, site in sorted(seen_sites.values(), key=lambda x: x[0], reverse=True)]
    merged["parses"] = [parse for _, parse in sorted(seen_parses.values(), key=lambda x: x[0], reverse=True)]
    return merged

def main():
    print("=" * 70)
    print("🚀 MiraPlay 接口整合工作流启动")
    print("=" * 70)
    print(f"📅 时间: {datetime.now().isoformat()}\n")

    print("📥 第1步: 加载本地配置文件...")
    configs = load_local_configs()

    if not configs:
        print("❌ 没有找到任何配置文件！")
        print("💡 请确保 scripts/ 目录下有 test_config*.json 文件")
        return False

    print(f"✅ 成功加载 {len(configs)} 个配置文件\n")

    print("🔀 第2步: 合并配置...")
    merged = merge_configs(configs)
    print(f" - 合并后共有 {len(merged['sites'])} 个源")
    print(f" - 合并后共有 {len(merged['parses'])} 个解析器\n")

    print("💾 第3步: 生成输出文件...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 生成 index.config.js
    config_js_content = f"""// MiraPlay Interface Aggregator
// 生成时间: {datetime.now().isoformat()}
// 合并源数: {len(configs)}

var index_config_default = {json.dumps(merged, ensure_ascii=False, indent=2)};

module.exports = index_config_default;
"""

    config_js_path = OUTPUT_DIR / "index.config.js"
    with open(config_js_path, "w", encoding="utf-8") as f:
        f.write(config_js_content)
    print(f" ✅ 生成 {config_js_path}")

    # 生成 index.config.js.md5
    config_md5 = generate_md5(config_js_content)
    config_md5_path = OUTPUT_DIR / "index.config.js.md5"
    with open(config_md5_path, "w") as f:
        f.write(config_md5)
    print(f" ✅ 生成 {config_md5_path}")

    # 生成 index.js (兼容格式)
    index_js_content = f"""// MiraPlay Interface Aggregator
// 生成时间: {datetime.now().isoformat()}

var index_config_default = {json.dumps(merged, ensure_ascii=False, indent=2)};

module.exports = index_config_default;
"""

    index_js_path = OUTPUT_DIR / "index.js"
    with open(index_js_path, "w", encoding="utf-8") as f:
        f.write(index_js_content)
    print(f" ✅ 生成 {index_js_path}")

    # 生成 index.js.md5
    index_md5 = generate_md5(index_js_content)
    index_md5_path = OUTPUT_DIR / "index.js.md5"
    with open(index_md5_path, "w") as f:
        f.write(index_md5)
    print(f" ✅ 生成 {index_md5_path}")

    # 生成元数据
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "merged_sources": len(configs),
        "total_sites": len(merged["sites"]),
        "total_parses": len(merged["parses"]),
        "config_md5": config_md5,
        "index_md5": index_md5,
    }
    metadata_path = OUTPUT_DIR / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f" ✅ 生成 {metadata_path}\n")

    print("✅ 第4步: 验证生成的文件...")
    with open(config_js_path, "r", encoding="utf-8") as f:
        verify_content = f.read()
    if generate_md5(verify_content) == config_md5:
        print(f" ✅ index.config.js MD5 验证成功")
    else:
        print(f" ❌ MD5 验证失败")
        return False

    print()
    print("=" * 70)
    print("📊 整合完成")
    print("=" * 70)
    print(f"✅ 成功生成 4 个文件:")
    print(f"  1. index.config.js ({len(config_js_content)} 字节)")
    print(f"  2. index.config.js.md5")
    print(f"  3. index.js ({len(index_js_content)} 字节)")
    print(f"  4. index.js.md5")
    print()
    print(f"🔗 订阅链接 (任选其一):")
    print(f"  - https://cxddgtb.github.io/mira/index.config.js.md5")
    print(f"  - https://cxddgtb.github.io/mira/index.js.md5")
    print(f"  - https://raw.githubusercontent.com/cxddgtb/mira/main/index.config.js.md5")
    print(f"  - https://raw.githubusercontent.com/cxddgtb/mira/main/index.js.md5")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
