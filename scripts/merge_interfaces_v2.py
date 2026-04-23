#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 整合脚本 v2 (根目录输出版)
- 自动从本地配置生成合并接口
- 生成文件直接输出到仓库根目录
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# ✅ 修改点：输出路径改为父目录的父目录（即仓库根目录）
OUTPUT_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent

def generate_md5(content: str) -> str:
    """生成 MD5 校验值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_local_configs() -> List[Dict[str, Any]]:
    """加载本地配置文件"""
    configs = []
    # 加载 scripts/ 目录下所有的 test_config*.json
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
    print("🚀 MiraPlay 接口整合工作流启动 (根目录模式)")
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

    print("💾 第3步: 生成输出文件到根目录...")
    OUTPUT_DIR.mkdir(exist_ok=True)

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

    config_md5 = generate_md5(config_js_content)
    config_md5_path = OUTPUT_DIR / "index.config.js.md5"
    with open(config_md5_path, "w") as f:
        f.write(config_md5)
    print(f" ✅ 生成 {config_md5_path}")

    metadata = {
        "generated_at": datetime.now().isoformat(),
        "merged_sources": len(configs),
        "total_sites": len(merged["sites"]),
        "config_md5": config_md5,
    }
    metadata_path = OUTPUT_DIR / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f" ✅ 生成 {metadata_path}\n")

    print("✅ 第4步: 验证生成的文件...")
    with open(config_js_path, "r", encoding="utf-8") as f:
        verify_content = f.read()
    if generate_md5(verify_content) == config_md5:
        print(f" ✅ MD5 验证成功")
    else:
        print(f" ❌ MD5 验证失败")
        return False

    print()
    print("=" * 70)
    print("📊 整合完成")
    print("=" * 70)
    print(f"🔗 新订阅链接: https://cxddgtb.github.io/mira/index.config.js.md5")
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
