#!/usr/bin/env python3
"""
MiraPlay 接口整合演示脚本
演示如何从多个本地配置文件进行合并和 MD5 生成
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

def generate_md5(content: str) -> str:
    """生成 MD5 校验值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def main():
    print("=" * 70)
    print("🎬 MiraPlay 接口整合演示")
    print("=" * 70)
    print()
    
    # 加载两个测试配置
    script_dir = Path(__file__).parent
    config1_path = script_dir / "test_config.json"
    config2_path = script_dir / "test_config_2.json"
    
    print("📥 第1步: 加载配置文件")
    print(f"  - 加载 {config1_path.name}...")
    with open(config1_path, "r", encoding="utf-8") as f:
        config1 = json.load(f)
    print(f"    ✅ 成功加载 {len(config1['sites'])} 个源")
    
    print(f"  - 加载 {config2_path.name}...")
    with open(config2_path, "r", encoding="utf-8") as f:
        config2 = json.load(f)
    print(f"    ✅ 成功加载 {len(config2['sites'])} 个源")
    print()
    
    # 合并配置
    print("🔀 第2步: 合并配置")
    merged = {
        "sites": [],
        "parses": [],
        "flags": [],
        "ijk": [],
        "ads": [],
        "wallpaper": "",
        "spider": "",
        "lives": [],
    }
    
    # 去重合并 sites
    seen_keys = {}
    for site in config1["sites"] + config2["sites"]:
        key = site.get("key")
        if key and key not in seen_keys:
            seen_keys[key] = site
            merged["sites"].append(site)
    
    # 去重合并 parses
    seen_parses = {}
    for parse in config1["parses"] + config2["parses"]:
        name = parse.get("name")
        if name and name not in seen_parses:
            seen_parses[name] = parse
            merged["parses"].append(parse)
    
    # 去重合并 flags
    seen_flags = set()
    for flag in config1["flags"] + config2["flags"]:
        flag_str = json.dumps(flag, sort_keys=True)
        if flag_str not in seen_flags:
            seen_flags.add(flag_str)
            merged["flags"].append(flag)
    
    print(f"  - 合并后共有 {len(merged['sites'])} 个源")
    print(f"  - 合并后共有 {len(merged['parses'])} 个解析器")
    print(f"  - 合并后共有 {len(merged['flags'])} 个标志")
    print()
    
    # 显示合并后的源列表
    print("📋 合并后的源列表:")
    for i, site in enumerate(merged["sites"], 1):
        print(f"  {i}. {site['name']} ({site['key']})")
    print()
    
    # 显示合并后的解析器列表
    print("🎯 合并后的解析器列表:")
    for i, parse in enumerate(merged["parses"], 1):
        print(f"  {i}. {parse['name']}")
    print()
    
    # 生成输出文件
    print("💾 第3步: 生成输出文件")
    
    # 生成 index.config.js
    config_js_content = f"""// MiraPlay Interface Aggregator - 演示版本
// 生成时间: {datetime.now().isoformat()}
// 合并源数: 2

var index_config_default = {json.dumps(merged, ensure_ascii=False, indent=2)};

module.exports = index_config_default;
"""
    
    output_dir = script_dir.parent / "dist"
    output_dir.mkdir(exist_ok=True)
    
    config_js_path = output_dir / "index.config.js"
    with open(config_js_path, "w", encoding="utf-8") as f:
        f.write(config_js_content)
    print(f"  ✅ 生成 {config_js_path}")
    
    # 生成 MD5
    config_md5 = generate_md5(config_js_content)
    config_md5_path = output_dir / "index.config.js.md5"
    with open(config_md5_path, "w") as f:
        f.write(config_md5)
    print(f"  ✅ 生成 {config_md5_path}")
    print()
    
    # 显示 MD5 信息
    print("🔐 MD5 校验信息:")
    print(f"  文件: index.config.js")
    print(f"  MD5: {config_md5}")
    print(f"  大小: {len(config_js_content)} 字节")
    print()
    
    # 生成元数据
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "merged_sources": 2,
        "total_sites": len(merged["sites"]),
        "total_parses": len(merged["parses"]),
        "total_flags": len(merged["flags"]),
        "config_md5": config_md5,
        "config_size_bytes": len(config_js_content),
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 生成 {metadata_path}")
    print()
    
    # 验证 MD5
    print("✅ 第4步: 验证 MD5")
    with open(config_js_path, "r", encoding="utf-8") as f:
        verify_content = f.read()
    verify_md5 = generate_md5(verify_content)
    
    if verify_md5 == config_md5:
        print(f"  ✅ MD5 验证成功！")
        print(f"  原始 MD5: {config_md5}")
        print(f"  验证 MD5: {verify_md5}")
    else:
        print(f"  ❌ MD5 验证失败！")
        print(f"  原始 MD5: {config_md5}")
        print(f"  验证 MD5: {verify_md5}")
    print()
    
    # 总结
    print("=" * 70)
    print("📊 整合总结")
    print("=" * 70)
    print(f"✅ 成功合并 2 个配置文件")
    print(f"  - 源总数: {len(merged['sites'])} 个")
    print(f"  - 解析器: {len(merged['parses'])} 个")
    print(f"  - 标志: {len(merged['flags'])} 个")
    print()
    print(f"📁 输出文件:")
    print(f"  - {config_js_path}")
    print(f"  - {config_md5_path}")
    print(f"  - {metadata_path}")
    print()
    print(f"🔗 订阅链接示例:")
    print(f"  https://your-github-username.github.io/miraplay-aggregator/index.config.js.md5")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
