# MiraPlay 接口整合项目 - 完整文件清单

## 📋 项目结构总览

```
miraplay-aggregator/
├── 🔧 核心脚本 (scripts/)
├── 📚 文档 (*.md)
├── ⚙️ 配置文件 (config files)
├── 🌐 前端代码 (client/)
├── 🔌 后端代码 (server/)
├── 🚀 工作流 (.github/)
└── 📦 依赖配置 (package.json, etc.)
```

---

## 🔧 核心脚本文件

### 1. `scripts/merge_interfaces_v2.py` ⭐ **推荐使用**

**用途**：生产环境中的核心整合脚本

**功能**：
- 从多个上游源获取配置
- 支持多种编码格式（UTF-8, GBK, GB2312, Latin-1）
- 智能解析 JSON 和 JavaScript 对象
- 去重和优先级管理
- 生成 MD5 校验值
- 详细的日志输出

**关键代码片段**：

```python
#!/usr/bin/env python3
"""
MiraPlay 接口整合脚本 v2
支持多个上游源的自动合并和 MD5 生成
"""

import json
import hashlib
import urllib.request
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 上游源配置
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
        "config_url": "https://raw.githubusercontent.com/9280017028/TVSpider/master/index.config.js",
        "priority": 80,
    },
    {
        "name": "Jadehh 爬虫源",
        "config_url": "https://gitee.com/jadehh_743/TVSpider/raw/master/dist/index.config.js",
        "priority": 70,
    },
]

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

def fetch_config(url: str, timeout: int = 10) -> Optional[str]:
    """从 URL 获取配置文件"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            
            # 尝试多种编码
            for encoding in ["utf-8", "gbk", "gb2312", "latin-1"]:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            return None
    except Exception as e:
        print(f"⚠️  获取 {url} 失败: {e}")
        return None

def parse_js_config(content: str) -> Optional[Dict[str, Any]]:
    """解析 JavaScript 配置对象"""
    try:
        # 尝试直接 JSON 解析
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # 提取 JavaScript 对象
    import re
    match = re.search(r'var\s+\w+\s*=\s*(\{.*?\});', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None

def generate_md5(content: str) -> str:
    """生成 MD5 校验值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def merge_sources(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """合并多个源配置"""
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
    
    seen_sites = {}
    seen_parses = {}
    seen_flags = set()
    
    for source in sources:
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
    
    # 按优先级排序并添加到结果
    merged["sites"] = [site for _, site in sorted(
        seen_sites.values(), key=lambda x: x[0], reverse=True
    )]
    merged["parses"] = [parse for _, parse in sorted(
        seen_parses.values(), key=lambda x: x[0], reverse=True
    )]
    
    return merged

def main():
    print("🚀 MiraPlay 接口整合工作流启动...")
    print(f"📅 时间: {datetime.now().isoformat()}")
    print(f"🧪 测试模式: {'启用' if TEST_MODE else '禁用'}\n")
    
    # 获取上游源
    print("📥 第1步: 从上游源获取配置...")
    sources_with_config = []
    
    for source in UPSTREAM_SOURCES:
        print(f"  - 正在获取 {source['name']}...")
        config_content = fetch_config(source["config_url"])
        
        if config_content:
            config = parse_js_config(config_content)
            if config:
                sources_with_config.append({
                    "name": source["name"],
                    "config": config,
                    "priority": source["priority"],
                })
                print(f"    ✅ 成功加载")
            else:
                print(f"    ⚠️  解析失败")
        else:
            print(f"    ⚠️  获取失败")
    
    if not sources_with_config:
        print("❌ 没有成功获取任何源配置！")
        if not TEST_MODE:
            sys.exit(1)
        else:
            # 测试模式：加载本地配置
            test_config_path = Path(__file__).parent / "test_config.json"
            if test_config_path.exists():
                with open(test_config_path, "r", encoding="utf-8") as f:
                    test_config = json.load(f)
                sources_with_config.append({
                    "name": "本地测试配置",
                    "config": test_config,
                    "priority": 100,
                })
                print("✅ 加载本地测试配置成功\n")
    
    print(f"✅ 成功获取 {len(sources_with_config)} 个源\n")
    
    # 合并配置
    print("🔀 第2步: 合并配置...")
    merged = merge_sources(sources_with_config)
    print(f"  - 合并后共有 {len(merged['sites'])} 个源")
    print(f"  - 合并后共有 {len(merged['parses'])} 个解析器\n")
    
    # 生成输出
    print("💾 第3步: 生成输出文件...")
    
    config_js_content = f"""// MiraPlay Interface Aggregator
// 生成时间: {datetime.now().isoformat()}
// 源数量: {len(sources_with_config)}

var index_config_default = {json.dumps(merged, ensure_ascii=False, indent=2)};

module.exports = index_config_default;
"""
    
    output_dir = Path(__file__).parent.parent / "dist"
    output_dir.mkdir(exist_ok=True)
    
    # 保存配置
    config_js_path = output_dir / "index.config.js"
    with open(config_js_path, "w", encoding="utf-8") as f:
        f.write(config_js_content)
    print(f"  ✅ 生成 {config_js_path}")
    
    # 生成 MD5
    config_md5 = generate_md5(config_js_content)
    config_md5_path = output_dir / "index.config.js.md5"
    with open(config_md5_path, "w") as f:
        f.write(config_md5)
    print(f"  ✅ 生成 {config_md5_path} (MD5: {config_md5})")
    
    # 生成元数据
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "sources": [{"name": s["name"], "priority": s["priority"]} for s in sources_with_config],
        "merged_stats": {
            "total_sites": len(merged["sites"]),
            "total_parses": len(merged["parses"]),
        },
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 生成 {metadata_path}\n")
    
    print("✅ 整合完成！")
    print(f"📍 输出目录: {output_dir}")

if __name__ == "__main__":
    main()
```

---

### 2. `scripts/test_merge_demo.py`

**用途**：本地演示脚本，展示合并过程

**功能**：
- 加载两个本地测试配置
- 演示合并算法
- 生成 MD5 校验值
- 输出详细统计信息

```python
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
    else:
        print(f"  ❌ MD5 验证失败！")
    print()
    
    # 总结
    print("=" * 70)
    print("📊 整合总结")
    print("=" * 70)
    print(f"✅ 成功合并 2 个配置文件")
    print(f"  - 源总数: {len(merged['sites'])} 个")
    print(f"  - 解析器: {len(merged['parses'])} 个")
    print()

if __name__ == "__main__":
    main()
```

---

### 3. `scripts/merge_interfaces.py`

**用途**：初始实现版本（已被 v2 替代）

```python
#!/usr/bin/env python3
"""
MiraPlay 接口整合脚本 - 初始版本
已被 merge_interfaces_v2.py 替代
"""

import json
import hashlib
import urllib.request
from pathlib import Path
from datetime import datetime

# 上游源配置
UPSTREAM_SOURCES = [
    {
        "name": "王二小",
        "url": "http://tvbox.王二小放牛娃.top/index.config.js",
    },
    {
        "name": "Jsnzkpg",
        "url": "https://raw.githubusercontent.com/Jsnzkpg/stymei/Jsnzkpg/index.config.js",
    },
]

def fetch_and_merge():
    """获取并合并所有源"""
    merged_config = {
        "sites": [],
        "parses": [],
        "flags": [],
    }
    
    for source in UPSTREAM_SOURCES:
        try:
            with urllib.request.urlopen(source["url"], timeout=10) as response:
                content = response.read().decode("utf-8")
                # 解析并合并...
        except Exception as e:
            print(f"获取 {source['name']} 失败: {e}")
    
    return merged_config

if __name__ == "__main__":
    config = fetch_and_merge()
    print(json.dumps(config, indent=2))
```

---

## 📊 测试配置文件

### 4. `scripts/test_config.json`

```json
{
  "sites": [
    {
      "key": "douban",
      "name": "豆瓣电影",
      "type": 3,
      "api": "csp_DoubanMovie",
      "searchable": 0,
      "quickSearch": 0,
      "filterable": 1
    },
    {
      "key": "cctv",
      "name": "CCTV",
      "type": 0,
      "api": "https://api.cctv.com/v1/",
      "searchable": 0,
      "quickSearch": 0,
      "filterable": 0
    },
    {
      "key": "bilibili",
      "name": "哔哩哔哩",
      "type": 3,
      "api": "csp_Bilibili",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1
    }
  ],
  "parses": [
    {
      "name": "官方解析",
      "type": 0,
      "url": "https://jx.jsonplayer.com/player/?url=",
      "ua": ""
    },
    {
      "name": "备用解析1",
      "type": 0,
      "url": "https://jx.xmflv.com/?url=",
      "ua": ""
    },
    {
      "name": "备用解析2",
      "type": 0,
      "url": "https://jx.playerjy.com/?url=",
      "ua": ""
    }
  ],
  "flags": [
    {
      "flag": "youku",
      "name": "优酷"
    },
    {
      "flag": "qq",
      "name": "腾讯"
    },
    {
      "flag": "iqiyi",
      "name": "爱奇艺"
    }
  ],
  "ijk": [],
  "ads": [],
  "wallpaper": "",
  "spider": "",
  "lives": []
}
```

---

### 5. `scripts/test_config_2.json`

```json
{
  "sites": [
    {
      "key": "tencent",
      "name": "腾讯视频",
      "type": 0,
      "api": "https://api.v.qq.com/",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1
    },
    {
      "key": "iqiyi",
      "name": "爱奇艺",
      "type": 0,
      "api": "https://api.iqiyi.com/",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1
    },
    {
      "key": "youku",
      "name": "优酷",
      "type": 0,
      "api": "https://api.youku.com/",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1
    },
    {
      "key": "mgtv",
      "name": "芒果TV",
      "type": 0,
      "api": "https://api.mgtv.com/",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1
    }
  ],
  "parses": [
    {
      "name": "高清解析",
      "type": 0,
      "url": "https://jx.vip.qq.com/?url=",
      "ua": "Mozilla/5.0"
    },
    {
      "name": "极速解析",
      "type": 0,
      "url": "https://jx.youku.com/?url=",
      "ua": "Mozilla/5.0"
    }
  ],
  "flags": [
    {
      "flag": "mgtv",
      "name": "芒果"
    },
    {
      "flag": "bilibili",
      "name": "B站"
    }
  ],
  "ijk": [],
  "ads": [],
  "wallpaper": "",
  "spider": "",
  "lives": []
}
```

---

### 6. `scripts/test_config.js`

```javascript
// 测试用的 JavaScript 配置格式
var index_config_default = {
  "sites": [
    {
      "key": "test",
      "name": "测试源",
      "type": 0,
      "api": "https://example.com/",
      "searchable": 1,
      "quickSearch": 1,
      "filterable": 1
    }
  ],
  "parses": [
    {
      "name": "测试解析",
      "type": 0,
      "url": "https://example.com/parse?url=",
      "ua": ""
    }
  ]
};
```

---

## 🚀 GitHub Actions 工作流

### 7. `.github/workflows/merge-interfaces.yml`

```yaml
name: MiraPlay Interface Aggregator

on:
  schedule:
    - cron: '0 0 * * *'      # 每天 UTC 0 点运行
  workflow_dispatch:          # 手动触发
  push:
    branches:
      - main                  # Push 时触发

jobs:
  aggregate:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: 检出代码
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 设置 Python 环境
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 运行整合脚本
        run: python scripts/merge_interfaces_v2.py

      - name: 提交更改
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add dist/
          git commit -m "chore: 自动更新接口配置 $(date -u +'%Y-%m-%d %H:%M:%S')" || true
          git push

      - name: 部署到 GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
          cname: miraplay-aggregator.example.com
```

---

## 📚 文档文件

### 8. `README.md`

项目主文档，包含：
- 项目概述
- 功能特性
- 快速开始
- 配置说明
- 故障排查
- 贡献指南

### 9. `QUICKSTART.md`

5 分钟快速部署指南：
- 前置要求
- 快速部署步骤
- 常见问题解答

### 10. `INTEGRATION_GUIDE.md`

深度技术指南，包含：
- CatPawOpen 协议基础
- 整合原理详解
- 部署步骤
- 高级配置
- 故障排查

### 11. `TECHNICAL_SUMMARY.md`

技术架构总结：
- 项目架构
- 工作流程图
- 技术实现细节
- 性能指标
- 安全性考虑
- 未来改进方向

### 12. `PROJECT_FILES.md`

项目文件清单：
- 目录结构
- 文档说明
- 脚本说明
- 配置文件说明
- 输出文件说明

### 13. `COMPLETE_FILE_LIST.md`

完整的代码和文件清单（本文件）

---

## ⚙️ 配置文件

### 14. `package.json`

项目依赖和脚本配置

```json
{
  "name": "miraplay-aggregator",
  "version": "1.0.0",
  "type": "module",
  "license": "MIT",
  "scripts": {
    "dev": "vite --host",
    "build": "vite build",
    "preview": "vite preview --host"
  },
  "dependencies": {
    "react": "^19.2.1",
    "react-dom": "^19.2.1",
    "wouter": "^3.3.5"
  },
  "devDependencies": {
    "typescript": "5.6.3",
    "vite": "^7.1.7"
  }
}
```

### 15. `tsconfig.json`

TypeScript 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./client/src/*"]
    }
  },
  "include": ["client/src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 16. `vite.config.ts`

Vite 构建配置

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './client/src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
  },
})
```

### 17. `components.json`

shadcn/ui 组件配置

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "aliasPrefix": "@",
  "baseColor": "slate"
}
```

---

## 🌐 前端代码

### 18. `client/index.html`

HTML 入口文件

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MiraPlay Aggregator</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### 19. `client/src/main.tsx`

React 入口

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### 20. `client/src/App.tsx`

主应用组件

```typescript
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";

function Router() {
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/404"} component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
```

### 21. `client/src/pages/Home.tsx`

主页组件

```typescript
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { Streamdown } from 'streamdown';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <main>
        <Loader2 className="animate-spin" />
        Example Page
        <Streamdown>Any **markdown** content</Streamdown>
        <Button variant="default">Example Button</Button>
      </main>
    </div>
  );
}
```

### 22. `client/src/pages/NotFound.tsx`

404 页面

```typescript
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

export default function NotFound() {
  const [, navigate] = useLocation();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-4">404</h1>
      <p className="text-lg mb-8">Page not found</p>
      <Button onClick={() => navigate("/")}>Go Home</Button>
    </div>
  );
}
```

### 23. `client/src/index.css`

全局样式

```css
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  /* ... 更多主题变量 ... */
}

:root {
  --primary: var(--color-blue-700);
  --primary-foreground: var(--color-blue-50);
  --radius: 0.65rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.235 0.015 65);
  /* ... 更多颜色变量 ... */
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}

@layer components {
  .container {
    width: 100%;
    margin-left: auto;
    margin-right: auto;
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
```

### 24. `client/src/contexts/ThemeContext.tsx`

主题上下文

```typescript
import React, { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({
  children,
  defaultTheme = "light",
  switchable = false,
}: {
  children: React.ReactNode;
  defaultTheme?: Theme;
  switchable?: boolean;
}) {
  const [theme, setTheme] = useState<Theme>(defaultTheme);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme]);

  const toggleTheme = () => {
    if (switchable) {
      setTheme((prev) => (prev === "light" ? "dark" : "light"));
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
}
```

### 25. `client/src/components/ErrorBoundary.tsx`

错误边界组件

```typescript
import React from "react";

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Something went wrong</h1>
            <p className="text-gray-600">{this.state.error?.message}</p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## 🔌 后端代码

### 26. `server/index.ts`

Express 服务器

```typescript
import express from "express";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const server = createServer(app);

  const staticPath =
    process.env.NODE_ENV === "production"
      ? path.resolve(__dirname, "public")
      : path.resolve(__dirname, "..", "dist", "public");

  app.use(express.static(staticPath));

  app.get("*", (_req, res) => {
    res.sendFile(path.join(staticPath, "index.html"));
  });

  const port = process.env.PORT || 3000;

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
```

---

## 📦 其他配置

### 27. `shared/const.ts`

共享常量

```typescript
export const APP_NAME = "MiraPlay Aggregator";
export const APP_VERSION = "1.0.0";
export const GITHUB_REPO = "https://github.com/your-username/miraplay-aggregator";
```

### 28. `.gitignore`

Git 忽略文件

```
node_modules/
dist/
build/
.env
.env.local
.DS_Store
*.log
.vscode/
.idea/
```

### 29. `pnpm-lock.yaml`

pnpm 依赖锁定文件（自动生成）

### 30. `LICENSE`

MIT 许可证

```
MIT License

Copyright (c) 2026 Manus AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 📊 文件统计

| 类型 | 数量 | 说明 |
| :--- | :--- | :--- |
| Python 脚本 | 3 | 核心整合脚本 + 演示脚本 |
| 配置文件 | 3 | JSON/JS 测试配置 |
| 文档 | 6 | Markdown 文档 |
| 工作流 | 1 | GitHub Actions |
| 前端组件 | 50+ | React + shadcn/ui |
| 配置文件 | 5 | TypeScript, Vite, etc. |
| **总计** | **70+** | **完整项目** |

---

## 🚀 快速导航

| 用途 | 文件 |
| :--- | :--- |
| **快速开始** | [QUICKSTART.md](QUICKSTART.md) |
| **深度学习** | [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) |
| **技术架构** | [TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md) |
| **核心脚本** | [scripts/merge_interfaces_v2.py](scripts/merge_interfaces_v2.py) |
| **工作流** | [.github/workflows/merge-interfaces.yml](.github/workflows/merge-interfaces.yml) |
| **演示脚本** | [scripts/test_merge_demo.py](scripts/test_merge_demo.py) |

---

**项目完成日期**：2026-04-22  
**版本**：1.0.0  
**维护者**：Manus AI
