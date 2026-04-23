#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 修复MD5计算
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
    """生成MD5（小写，无换行）"""
    return hashlib.md5(content.encode('utf-8')).hexdigest().lower()

def load_local_configs() -> List[Dict[str, Any]]:
    """加载本地配置"""
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
            print(f"  ✅ {config_file.name}")
        except Exception as e:
            print(f"  ❌ {config_file.name}: {e}")
    return configs

def merge_configs(configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """合并配置"""
    merged = {
        "ali": {"token": "", "token280": ""},
        "quark": {"cookie": ""},
        "uc": {"cookie": "", "token": "", "ut": ""},
        "y115": {"cookie": ""},
        "muou": {"url": ""},
        "wogg": {"url": ""},
        "leijing": {"url": ""},
        "tgsou": {"tgPic": False, "count": 0, "url": "", "channelUsername": ""},
        "tgchannel": {},
        "sites": {"list": []},
        "pans": {"list": []},
        "danmu": {
            "urls": [
                {"address": "https://logdanmu.dpdns.org", "name": "默认1"},
                {"address": "https://fjj0417.dpdns.org/87654321", "name": "默认2"},
                {"address": "https://dm.stardm.us.kg:443/87654321", "name": "默认3"},
                {"address": "https://danmu.14812910.xyz/87654321", "name": "默认4"},
                {"address": "https://313236.xyz/87654321", "name": "默认5"}
            ],
            "autoPush": True
        },
        "t4": {"list": []},
        "cms": {"list": []},
        "alist": [],
        "color": []
    }
    
    seen = {"sites": set(), "cms": set(), "t4": set(), "alist": set()}
    
    for source in configs:
        config = source.get("config", {})
        
        for item in config.get("sites", []):
            key = item.get("key") or item.get("name")
            if key and key not in seen["sites"]:
                seen["sites"].add(key)
                merged["sites"]["list"].append(item)
        
        for item in config.get("cms", []):
            name = item.get("name")
            if name and name not in seen["cms"]:
                seen["cms"].add(name)
                merged["cms"]["list"].append(item)
        
        for item in config.get("t4", []):
            name = item.get("name")
            if name and name not in seen["t4"]:
                seen["t4"].add(name)
                merged["t4"]["list"].append(item)
        
        for item in config.get("alist", []):
            name = item.get("name")
            if name and name not in seen["alist"]:
                seen["alist"].add(name)
                merged["alist"].append(item)
        
        for item in config.get("color", []):
            merged["color"].append(item)
    
    return merged

def main():
    print("=" * 70)
    print("🚀 MiraPlay 接口整合")
    print("=" * 70)
    
    # 1. 加载配置
    print("\n📥 加载配置...")
    configs = load_local_configs()
    if not configs:
        print("❌ 未找到配置文件")
        return False
    print(f"✅ {len(configs)} 个配置\n")
    
    # 2. 合并配置
    print("🔀 合并配置...")
    merged = merge_configs(configs)
    print(f"  Sites: {len(merged['sites']['list'])}")
    print(f"  CMS: {len(merged['cms']['list'])}\n")
    
    # 3. 生成 index.config.js
    print("💾 生成文件...\n")
    
    config_content = f"""// MiraPlay Interface Aggregator
// 生成时间: {datetime.now().isoformat()}
// 合并源数: {len(configs)}

var index_config_default = {json.dumps(merged, ensure_ascii=False, indent=1)};

module.exports = index_config_default;
"""
    
    config_path = OUTPUT_DIR / "index.config.js"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"  ✅ index.config.js")
    
    # 4. 生成 index.config.js.md5
    config_md5 = generate_md5(config_content)
    config_md5_path = OUTPUT_DIR / "index.config.js.md5"
    with open(config_md5_path, "w", encoding="utf-8", newline="") as f:
        f.write(config_md5)  # 只写MD5，无换行
    print(f"  ✅ index.config.js.md5 ({config_md5})")
    
    # 5. 生成 index.js（与 index.config.js 内容完全相同）
    index_path = OUTPUT_DIR / "index.js"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"  ✅ index.js")
    
    # 6. 生成 index.js.md5（与 index.config.js.md5 相同）
    index_md5_path = OUTPUT_DIR / "index.js.md5"
    with open(index_md5_path, "w", encoding="utf-8", newline="") as f:
        f.write(config_md5)  # 使用相同的MD5
    print(f"  ✅ index.js.md5 ({config_md5})")
    
    # 7. 生成 metadata.json
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "merged_sources": len(configs),
        "total_sites": len(merged["sites"]["list"]),
        "md5": config_md5
    }
    with open(OUTPUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ metadata.json\n")
    
    # 8. 验证
    print("✅ 验证...")
    with open(config_path, "r", encoding="utf-8") as f:
        verify_content = f.read()
    verify_md5 = generate_md5(verify_content)
    
    if verify_md5 == config_md5:
        print(f"  ✅ MD5 验证通过")
    else:
        print(f"  ❌ MD5 验证失败：{verify_md5} != {config_md5}")
        return False
    
    print("\n" + "=" * 70)
    print("✨ 完成！")
    print("=" * 70)
    print(f"\n🔗 订阅链接:")
    print(f"  https://raw.githubusercontent.com/cxddgtb/mira/main/index.config.js.md5")
    print(f"  https://raw.githubusercontent.com/cxddgtb/mira/main/index.js.md5")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
