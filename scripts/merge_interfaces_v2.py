#!/usr/bin/env python3
"""
MiraPlay Interface Aggregator - 全新重写版
生成简单清晰的配置文件，与参考项目格式一致
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

OUTPUT_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent

def generate_md5(content: str) -> str:
    """生成 MD5 校验值（纯32位哈希，无换行）"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_local_configs() -> List[Dict[str, Any]]:
    """加载本地配置文件"""
    configs = []
    print("📂 搜索配置文件...")
    
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
            print(f"  ✅ {config_file.name}")
        except Exception as e:
            print(f"  ❌ {config_file.name}: {e}")
    
    return configs

def merge_simple_config(configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    合并配置为简单格式（与参考项目一致）
    生成清晰的 JSON 结构，不是压缩代码
    """
    # 基础结构
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
    
    # 去重集合
    seen_sites = set()
    seen_cms = set()
    seen_t4 = set()
    seen_alist = set()
    
    # 合并所有配置
    for source in configs:
        config = source.get("config", {})
        
        # 合并 sites
        for site in config.get("sites", []):
            key = site.get("key") or site.get("name")
            if key and key not in seen_sites:
                seen_sites.add(key)
                merged["sites"]["list"].append(site)
        
        # 合并 cms
        for cms in config.get("cms", []):
            name = cms.get("name")
            if name and name not in seen_cms:
                seen_cms.add(name)
                merged["cms"]["list"].append(cms)
        
        # 合并 t4
        for t4 in config.get("t4", []):
            name = t4.get("name")
            if name and name not in seen_t4:
                seen_t4.add(name)
                merged["t4"]["list"].append(t4)
        
        # 合并 alist
        for alist in config.get("alist", []):
            name = alist.get("name")
            if name and name not in seen_alist:
                seen_alist.add(name)
                merged["alist"].append(alist)
        
        # 合并 color
        for color in config.get("color", []):
            merged["color"].append(color)
    
    return merged

def generate_config_js_content(merged: Dict[str, Any], comment: str = "") -> str:
    """
    生成配置文件内容
    格式：var index_config_default = {...};
    """
    # 转换为 JavaScript 对象字符串
    js_obj_str = json.dumps(merged, ensure_ascii=False, indent=2)
    
    # 添加注释
    comment_block = ""
    if comment:
        comment_block = f"// {comment}\n\n"
    
    content = f"{comment_block}var index_config_default = {js_obj_str};\n"
    return content

def main():
    print("=" * 70)
    print("🚀 MiraPlay 接口整合工作流（全新重写版）")
    print("=" * 70)
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 步骤1：加载配置
    print("📥 步骤1: 加载本地配置文件...")
    configs = load_local_configs()
    
    if not configs:
        print("\n❌ 错误：未找到任何配置文件")
        print("💡 请在 scripts/ 目录下创建 test_config*.json 文件")
        return False
    
    print(f"\n✅ 成功加载 {len(configs)} 个配置文件\n")
    
    # 步骤2：合并配置
    print("🔀 步骤2: 合并配置...")
    merged = merge_simple_config(configs)
    
    site_count = len(merged["sites"]["list"])
    cms_count = len(merged["cms"]["list"])
    t4_count = len(merged["t4"]["list"])
    alist_count = len(merged["alist"])
    
    print(f"  📺 Sites: {site_count}")
    print(f"  🎬 CMS: {cms_count}")
    print(f"  🎯 T4: {t4_count}")
    print(f"  📁 AList: {alist_count}\n")
    
    # 步骤3：生成文件
    print("💾 步骤3: 生成文件...\n")
    
    # 生成 index.config.js
    config_js_content = generate_config_js_content(
        merged,
        f"MiraPlay Interface Aggregator\n生成时间: {datetime.now().isoformat()}"
    )
    
    config_js_path = OUTPUT_DIR / "index.config.js"
    with open(config_js_path, "w", encoding="utf-8") as f:
        f.write(config_js_content)
    print(f"  ✅ index.config.js ({len(config_js_content)} 字节)")
    
    # 生成 index.config.js.md5
    config_md5 = generate_md5(config_js_content)
    config_md5_path = OUTPUT_DIR / "index.config.js.md5"
    with open(config_md5_path, "w", encoding="utf-8") as f:
        f.write(config_md5)  # 只写入纯哈希，无换行
    print(f"  ✅ index.config.js.md5")
    
    # 生成 index.js（与 index.config.js 内容相同）
    index_js_content = config_js_content
    index_js_path = OUTPUT_DIR / "index.js"
    with open(index_js_path, "w", encoding="utf-8") as f:
        f.write(index_js_content)
    print(f"  ✅ index.js ({len(index_js_content)} 字节)")
    
    # 生成 index.js.md5
    index_md5 = generate_md5(index_js_content)
    index_md5_path = OUTPUT_DIR / "index.js.md5"
    with open(index_md5_path, "w", encoding="utf-8") as f:
        f.write(index_md5)  # 只写入纯哈希，无换行
    print(f"  ✅ index.js.md5")
    
    # 生成元数据
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "merged_sources": len(configs),
        "total_sites": site_count,
        "total_cms": cms_count,
        "total_t4": t4_count,
        "total_alist": alist_count,
        "config_md5": config_md5,
        "index_md5": index_md5
    }
    
    metadata_path = OUTPUT_DIR / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ metadata.json\n")
    
    # 步骤4：验证
    print("✅ 步骤4: 验证文件...")
    with open(config_js_path, "r", encoding="utf-8") as f:
        verify_content = f.read()
    
    if generate_md5(verify_content) == config_md5:
        print("  ✅ MD5 验证通过")
    else:
        print("  ❌ MD5 验证失败")
        return False
    
    # 完成
    print()
    print("=" * 70)
    print("✨ 整合完成！")
    print("=" * 70)
    print(f"\n📊 统计信息:")
    print(f"  • 配置文件: {len(configs)} 个")
    print(f"  • 视频源: {site_count + cms_count + t4_count} 个")
    print(f"  • AList: {alist_count} 个")
    print(f"\n🔗 订阅链接（任选其一）:")
    print(f"  1. https://raw.githubusercontent.com/cxddgtb/mira/main/index.config.js.md5")
    print(f"  2. https://raw.githubusercontent.com/cxddgtb/mira/main/index.js.md5")
    print(f"  3. https://cxddgtb.github.io/mira/index.config.js.md5")
    print(f"  4. https://cxddgtb.github.io/mira/index.js.md5")
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
