#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 最终修复版
生成与参考项目完全一致的简单配置格式
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
    """生成纯32位MD5哈希（无换行，小写）"""
    return hashlib.md5(content.encode("utf-8")).hexdigest().lower()

def load_local_configs() -> List[Dict[str, Any]]:
    """加载本地 test_config*.json 文件"""
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

def merge_simple_config(configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """合并为简单配置格式（与参考项目一致）"""
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

def generate_config_content(merged: Dict[str, Any]) -> str:
    """生成配置文件内容（简单格式，与参考项目一致）"""
    js_obj = json.dumps(merged, ensure_ascii=False, indent=2)
    return f"var index_config_default = {js_obj};\n"

def write_md5_file(filepath: Path, content: str):
    """写入.md5文件：纯32位哈希，无换行"""
    md5_hash = generate_md5(content)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(md5_hash)  # 只写哈希，不换行
    return md5_hash

def main():
    print("=" * 70)
    print("🚀 MiraPlay 接口整合（最终修复版）")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. 加载配置
    print("📥 加载配置文件...")
    configs = load_local_configs()
    if not configs:
        print("❌ 未找到 test_config*.json 文件")
        return False
    print(f"✅ 加载 {len(configs)} 个配置\n")
    
    # 2. 合并配置
    print("🔀 合并配置...")
    merged = merge_simple_config(configs)
    print(f"  📺 Sites: {len(merged['sites']['list'])}")
    print(f"  🎬 CMS: {len(merged['cms']['list'])}")
    print(f"  🎯 T4: {len(merged['t4']['list'])}\n")
    
    # 3. 生成文件
    print("💾 生成文件...\n")
    
    # index.config.js
    config_content = generate_config_content(merged)
    config_path = OUTPUT_DIR / "index.config.js"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"  ✅ index.config.js")
    
    # index.config.js.md5
    config_md5 = write_md5_file(OUTPUT_DIR / "index.config.js.md5", config_content)
    print(f"  ✅ index.config.js.md5 ({config_md5})")
    
    # index.js（与 index.config.js 内容相同）
    index_path = OUTPUT_DIR / "index.js"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"  ✅ index.js")
    
    # index.js.md5
    index_md5 = write_md5_file(OUTPUT_DIR / "index.js.md5", config_content)
    print(f"  ✅ index.js.md5 ({index_md5})")
    
    # metadata.json
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "merged_sources": len(configs),
        "total_sites": len(merged["sites"]["list"]),
        "config_md5": config_md5,
        "index_md5": index_md5
    }
    with open(OUTPUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ metadata.json\n")
    
    # 4. 验证
    print("✅ 验证文件...")
    with open(config_path, "r", encoding="utf-8") as f:
        verify = f.read()
    if generate_md5(verify) == config_md5:
        print("  ✅ MD5 校验通过")
    else:
        print("  ❌ MD5 校验失败")
        return False
    
    print()
    print("=" * 70)
    print("✨ 完成！")
    print("=" * 70)
    print(f"\n🔗 订阅链接（任选其一）:")
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
