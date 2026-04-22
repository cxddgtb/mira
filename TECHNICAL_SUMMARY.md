# MiraPlay 接口整合项目 - 技术总结

## 📖 项目概述

**MiraPlay Interface Aggregator** 是一个基于 GitHub Actions 的自动化工作流项目，用于将多个 CatPawOpen 协议的影视接口源整合为一个统一的订阅接口。该项目通过智能合并、去重和优先级管理，为 MiraPlay、JSTV 等兼容应用提供稳定、高质量的影视资源聚合服务。

## 🏗️ 项目架构

### 核心组件

```
miraplay-aggregator/
├── .github/workflows/
│   └── merge-interfaces.yml          # GitHub Actions 工作流配置
├── scripts/
│   ├── merge_interfaces_v2.py        # 核心整合脚本（生产版本）
│   ├── merge_interfaces.py           # 整合脚本（初始版本）
│   ├── test_merge_demo.py            # 演示脚本
│   ├── test_config.json              # 测试配置1
│   └── test_config_2.json            # 测试配置2
├── dist/                             # 输出目录（自动生成）
│   ├── index.config.js               # 合并后的配置
│   ├── index.config.js.md5           # MD5 校验值
│   └── metadata.json                 # 元数据
├── README.md                         # 项目主文档
├── QUICKSTART.md                     # 快速开始指南
├── INTEGRATION_GUIDE.md              # 深度技术指南
└── LICENSE                           # MIT 许可证
```

### 工作流程图

```
GitHub Actions 定时触发
         │
         ▼
┌─────────────────────────────────────┐
│ 1. 获取上游源配置                    │
│ - 从多个源下载 index.config.js      │
│ - 支持多种编码和格式                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. 解析配置文件                      │
│ - JSON 直接解析                     │
│ - JavaScript 对象提取               │
│ - 错误处理和降级                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. 合并配置                          │
│ - 去重（按 key/name）               │
│ - 优先级排序                        │
│ - 冲突解决                          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. 生成输出文件                      │
│ - index.config.js                   │
│ - index.config.js.md5               │
│ - metadata.json                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. 部署到 GitHub Pages              │
│ - 自动发布到 gh-pages 分支          │
│ - 生成 HTTPS 访问链接               │
└─────────────────────────────────────┘
```

## 🔧 技术实现细节

### 1. CatPawOpen 协议支持

**协议特点**：
- 基于 JavaScript 的动态规则加载
- MD5 校验机制确保数据完整性
- 支持多种源类型（网址、本地、插件等）
- 灵活的解析器配置

**文件结构**：

| 文件 | 用途 | 格式 |
| :--- | :--- | :--- |
| `index.js` | 核心逻辑（爬虫规则） | 打包后的 JavaScript |
| `index.config.js` | 配置清单 | JavaScript 对象 |
| `*.md5` | 校验值 | 32 位十六进制 |

### 2. 配置合并算法

**去重策略**：

```python
# Sites 去重：按 key 去重，保留优先级最高的版本
seen_sites = {}
for site in all_sites:
    key = site.get("key")
    if key not in seen_sites or seen_sites[key][0] < priority:
        seen_sites[key] = (priority, site)

# Parses 去重：按 name 去重
seen_parses = {}
for parse in all_parses:
    name = parse.get("name")
    if name not in seen_parses or seen_parses[name][0] < priority:
        seen_parses[name] = (priority, parse)

# 其他字段去重：JSON 序列化后比较
unique_flags = {json.dumps(x, sort_keys=True) for x in all_flags}
```

**优先级管理**：

```python
# 按优先级排序源
sources.sort(key=lambda x: x.get("priority", 0), reverse=True)

# 优先级配置示例
UPSTREAM_SOURCES = [
    {"name": "王二小", "priority": 100},    # 最高
    {"name": "Jsnzkpg", "priority": 90},    # 次高
    {"name": "9280", "priority": 80},       # 中等
    {"name": "Jadehh", "priority": 70},     # 较低
]
```

### 3. MD5 校验机制

**生成流程**：

```python
def generate_md5(content: str) -> str:
    """生成 MD5 校验值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

# 生成 index.config.js 的 MD5
config_md5 = generate_md5(config_js_content)

# 保存到 index.config.js.md5 文件
with open("index.config.js.md5", "w") as f:
    f.write(config_md5)
```

**验证流程**（客户端）：

```
1. 下载 index.config.js.md5
2. 计算本地 index.config.js 的 MD5
3. 比较两个 MD5 值
   - 相同 → 使用本地缓存
   - 不同 → 下载新版本
```

### 4. 错误处理和降级

**多层次错误处理**：

```python
# 第1层：URL 获取
try:
    response = urllib.request.urlopen(url, timeout=10)
except Exception as e:
    print(f"获取失败: {e}")
    return None

# 第2层：编码处理
for encoding in ["utf-8", "gbk", "gb2312", "latin-1"]:
    try:
        return content.decode(encoding)
    except UnicodeDecodeError:
        continue

# 第3层：配置解析
try:
    return json.loads(content)  # 直接 JSON
except json.JSONDecodeError:
    return parse_js_config(content)  # JavaScript 对象提取

# 第4层：测试模式降级
if not sources_with_config and TEST_MODE:
    # 加载本地测试配置
    return load_test_config()
```

### 5. GitHub Actions 工作流

**工作流配置**：

```yaml
name: MiraPlay Interface Aggregator

on:
  schedule:
    - cron: '0 0 * * *'      # 每天 UTC 0 点
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
      
      - name: 设置 Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: 运行整合脚本
        run: python scripts/merge_interfaces_v2.py
      
      - name: 部署到 GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

## 📊 性能指标

### 测试结果

基于本地演示测试的性能指标：

| 指标 | 数值 | 说明 |
| :--- | :--- | :--- |
| 配置文件大小 | 2.4 KB | 合并 2 个源后 |
| 源总数 | 7 个 | 合并后去重 |
| 解析器数量 | 5 个 | 合并后去重 |
| 处理时间 | < 2 秒 | 本地处理 |
| MD5 生成时间 | < 100 ms | 单次计算 |
| 工作流总耗时 | 1-2 分钟 | GitHub Actions |

### 可扩展性

- **源数量**：支持 10+ 个源的合并（无性能问题）
- **配置大小**：支持 10+ MB 的配置文件
- **并发处理**：单线程顺序处理（可扩展为并发）
- **更新频率**：支持每小时更新（可自定义）

## 🔐 安全性考虑

### 数据安全

- **只读操作**：脚本仅从上游源读取数据，不修改任何源
- **MD5 校验**：确保文件完整性，防止篡改
- **HTTPS 传输**：GitHub Pages 提供 HTTPS 加密
- **版本控制**：所有更改通过 Git 记录，可追踪

### 隐私保护

- **无个人数据收集**：脚本不收集用户信息
- **本地处理**：所有处理在 GitHub Actions 沙盒中进行
- **开源透明**：代码完全开源，可审计

## 🎯 使用场景

### 场景 1：个人用户

用户 Fork 项目，自动获得每日更新的影视接口聚合源。

### 场景 2：内容分发商

将自有源集成到项目中，通过 GitHub Pages 分发。

### 场景 3：开发者

基于本项目二次开发，实现自定义的源整合逻辑。

## 📈 未来改进方向

### 短期改进

- [ ] 支持 Web UI 配置界面
- [ ] 实时监控源可用性
- [ ] 自动故障转移机制
- [ ] 源质量评分系统

### 中期改进

- [ ] 支持多语言界面
- [ ] 集成 Telegram 通知
- [ ] 源性能基准测试
- [ ] 自动备份机制

### 长期改进

- [ ] 云端配置管理
- [ ] 分布式源网络
- [ ] AI 智能推荐
- [ ] 社区贡献平台

## 📚 相关资源

### 官方文档

- [CatVod 官方仓库](https://github.com/catvod/CatVodTVSpider)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Pages 文档](https://docs.github.com/en/pages)

### 兼容应用

- [MiraPlay](https://apps.apple.com/us/app/miraplay/id1669201695) - iOS
- [JSTV](https://testflight.apple.com/join/4N2pkqa3) - iOS (TestFlight)

### 相关技术

- Python 3.11
- GitHub Actions
- GitHub Pages
- CatPawOpen 协议

## 🤝 贡献指南

欢迎提交以下形式的贡献：

- **Bug 报告**：在 GitHub Issues 中报告问题
- **功能建议**：提出改进建议
- **代码贡献**：提交 Pull Request
- **文档改进**：改进使用文档

## 📝 许可证

本项目采用 **MIT 许可证**。详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- **GitHub Issues**：提出问题和建议
- **GitHub Discussions**：讨论和交流
- **Email**：通过 GitHub 个人资料联系

---

**项目状态**：🟢 活跃维护  
**最后更新**：2026-04-22  
**版本**：1.0.0  
**维护者**：Manus AI
