#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 整合脚本 v2 (修复版)
- 自动从本地配置生成合并接口
- 支持多个上游源（可选）
- 生成 MD5 校验值
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

OUTPUT_DIR = Path(__file__).parent.parent / "dist"
SCRIPTS_DIR = Path(__file__).parent

def generate_md5(content: str) -> str:
    """生成 MD5 校验值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_local_configs() -> List[Dict[str, Any]]:
    """加载本地配置文件"""
    configs = []
    
    # 加载所有 .json 配置文件
    for config_file in sorted(SCRIPTS_DIR.glob("test_config*.json")):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                configs.append({
                    "name": config_file.stem,
                    "config": config,
                    "priority": 100 - len(configs) * 10,  # 递减优先级
                })
                print(f"  ✅ 加载 {config_file.name}")
        except Exception as e:
            print(f"  ⚠️  加载 {config_file.name} 失败: {e}")
    
    return configs

def merge_configs(configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """合并多个配置"""
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
    
    # 去重合并
    seen_sites = {}
    seen_parses = {}
    seen_flags = set()
    
    for source in configs:
        config = source.get("config", {})
        priority = source.get("priority", 0)
        
        # 合并 sites
        for site in config.get("sites", []):
            key = site.get("key")
            if key and key not in seen_sites:
                seen_sites[key] = (priority, site)
        
        # 合并 parses
        for parse in config.get("parses", []):
            name = parse.get("name")
            if name and name not in seen_parses:
                seen_parses[name] = (priority, parse)
        
        # 合并 flags
        for flag in config.get("flags", []):
            flag_str = json.dumps(flag, sort_keys=True)
            if flag_str not in seen_flags:
                seen_flags.add(flag_str)
                merged["flags"].append(flag)
    
    # 按优先级排序并添加
    merged["sites"] = [site for _, site in sorted(
        seen_sites.values(), key=lambda x: x[0], reverse=True
    )]
    merged["parses"] = [parse for _, parse in sorted(
        seen_parses.values(), key=lambda x: x[0], reverse=True
    )]
    
    return merged

def main():
    print("=" * 70)
    print("🚀 MiraPlay 接口整合工作流启动")
    print("=" * 70)
    print(f"📅 时间: {datetime.now().isoformat()}\n")
    
    # 第1步：加载本地配置
    print("📥 第1步: 加载本地配置文件...")
    configs = load_local_configs()
    
    if not configs:
        print("❌ 没有找到任何配置文件！")
        return False
    
    print(f"✅ 成功加载 {len(configs)} 个配置文件\n")
    
    # 第2步：合并配置
    print("🔀 第2步: 合并配置...")
    merged = merge_configs(configs)
    print(f"  - 合并后共有 {len(merged['sites'])} 个源")
    print(f"  - 合并后共有 {len(merged['parses'])} 个解析器")
    print(f"  - 合并后共有 {len(merged['flags'])} 个标志\n")
    
    # 第3步：生成输出
    print("💾 第3步: 生成输出文件...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 生成 index.config.js
    config_js_content = f"""// MiraPlay Interface Aggregator
// 生成时间: {datetime.now().isoformat()}
// 合并源数: {len(configs)}
// 生成工具: https://github.com/cxddgtb/mira

var index_config_default = {json.dumps(merged, ensure_ascii=False, indent=2)};

module.exports = index_config_default;
"""
    
    config_js_path = OUTPUT_DIR / "index.config.js"
    with open(config_js_path, "w", encoding="utf-8") as f:
        f.write(config_js_content)
    print(f"  ✅ 生成 {config_js_path}")
    
    # 生成 MD5
    config_md5 = generate_md5(config_js_content)
    config_md5_path = OUTPUT_DIR / "index.config.js.md5"
    with open(config_md5_path, "w") as f:
        f.write(config_md5)
    print(f"  ✅ 生成 {config_md5_path}")
    print(f"     MD5: {config_md5}")
    
    # 生成元数据
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "merged_sources": len(configs),
        "total_sites": len(merged["sites"]),
        "total_parses": len(merged["parses"]),
        "total_flags": len(merged["flags"]),
        "config_md5": config_md5,
        "config_size_bytes": len(config_js_content),
    }
    
    metadata_path = OUTPUT_DIR / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 生成 {metadata_path}\n")
    
    # 第4步：验证
    print("✅ 第4步: 验证生成的文件...")
    with open(config_js_path, "r", encoding="utf-8") as f:
        verify_content = f.read()
    verify_md5 = generate_md5(verify_content)
    
    if verify_md5 == config_md5:
        print(f"  ✅ MD5 验证成功")
    else:
        print(f"  ❌ MD5 验证失败")
        return False
    
    print()
    print("=" * 70)
    print("📊 整合完成")
    print("=" * 70)
    print(f"✅ 成功生成合并接口")
    print(f"  - 源总数: {len(merged['sites'])} 个")
    print(f"  - 解析器: {len(merged['parses'])} 个")
    print(f"  - 文件大小: {len(config_js_content)} 字节")
    print()
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"🔗 订阅链接: https://cxddgtb.github.io/mira/index.config.js.md5")
    print()
    
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
