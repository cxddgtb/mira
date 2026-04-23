# MiraPlay 接口整合工作流项目

一个基于 GitHub Actions 的自动化项目，用于将多个 **CatPawOpen 协议**的影视接口源整合为一个统一的订阅接口。支持 **MiraPlay**、**JSTV** 等兼容应用。

## 🎯 项目目标

将分散在全网的高质量影视接口源（王二小、9280、Jadehh 等）自动合并为一个单一的、持续更新的订阅链接，实现"一键订阅、多源聚合"的体验。

## 📋 核心特性

- **自动化整合**：GitHub Actions 定时运行，每天自动从上游源抓取最新配置
- **智能去重**：自动识别并移除重复的源和解析器
- **优先级管理**：按照配置的优先级排序，确保最强源优先加载
- **MD5 校验**：自动生成 MD5 签名文件，确保数据完整性
- **GitHub Pages 部署**：自动发布到 GitHub Pages，提供稳定的访问链接
- **实时监控**：生成详细的整合元数据，便于追踪源的状态

## 🚀 快速开始

### 1. Fork 本项目

点击 GitHub 页面右上角的 **Fork** 按钮，将本项目复制到您的账户。

### 2. 启用 GitHub Pages

在您的 Fork 仓库中：
- 进入 **Settings** → **Pages**
- 选择 **Source** 为 **Deploy from a branch**
- 选择分支为 **gh-pages**
- 点击 **Save**

### 3. 运行工作流

- 进入 **Actions** 标签页
- 选择 **MiraPlay Interface Aggregator** 工作流
- 点击 **Run workflow** 手动触发（或等待每天自动运行）

### 4. 获取订阅链接

工作流完成后，您的订阅链接为：

```
https://<your-github-username>.github.io/<your-repo-name>/index.config.js.md5
```

例如：
```
https://john-doe.github.io/miraplay-aggregator/index.config.js.md5
```

### 5. 在 MiraPlay 中添加订阅

1. 打开 MiraPlay 应用
2. 进入 **设置** → **订阅管理**
3. 点击 **添加订阅**
4. 粘贴上述链接
5. 等待加载完成

## 📁 项目结构

```
miraplay-aggregator/
├── .github/
│   └── workflows/
│       └── merge-interfaces.yml    # GitHub Actions 工作流配置
├── scripts/
│   └── merge_interfaces.py         # Python 整合脚本
├── dist/                           # 输出目录（自动生成）
│   ├── index.config.js             # 合并后的配置文件
│   ├── index.config.js.md5         # MD5 校验值
│   ├── metadata.json               # 整合元数据
│   └── README.md                   # 输出说明
├── README.md                       # 本文件
└── LICENSE                         # MIT 许可证
```

## 🔧 配置说明

### 修改上游源列表

编辑 `scripts/merge_interfaces.py` 中的 `UPSTREAM_SOURCES` 列表，添加或修改要整合的源：

```python
UPSTREAM_SOURCES = [
    {
        "name": "源名称",
        "config_url": "https://example.com/index.config.js.md5",
        "js_url": "https://example.com/index.js.md5",
        "priority": 100,  # 优先级（数字越大优先级越高）
    },
    # ... 更多源
]
```

### 自定义更新频率

编辑 `.github/workflows/merge-interfaces.yml` 中的 `cron` 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天 UTC 0 点运行
  # 其他 cron 表达式示例：
  # '0 */6 * * *'     # 每 6 小时运行一次
  # '0 9 * * 1'       # 每周一上午 9 点运行
```

## 📊 工作流程

### 第1步：获取上游源

脚本从配置的上游源列表中逐一获取 `index.config.js` 文件。

### 第2步：解析配置

使用正则表达式和 JSON 解析器提取每个源中的配置对象，特别是：
- `sites` 数组：影视源列表
- `parses` 数组：解析器列表
- `flags`、`ijk`、`ads`、`lives` 等辅助配置

### 第3步：合并配置

将所有源的配置合并为一个，同时进行：
- **去重**：移除重复的源和解析器
- **优先级排序**：按照配置的优先级排列源
- **冲突解决**：当多个源定义相同的源时，保留优先级最高的版本

### 第4步：生成输出

生成以下文件：
- `index.config.js`：合并后的配置文件
- `index.config.js.md5`：MD5 校验值
- `metadata.json`：整合元数据（包含源统计、生成时间等）

### 第5步：部署到 GitHub Pages

使用 `peaceiris/actions-gh-pages` Action 自动部署到 GitHub Pages，使配置文件可通过 HTTPS 访问。

## 🔐 安全性

- **只读操作**：脚本仅从上游源读取数据，不修改任何源
- **自动验证**：MD5 校验确保文件完整性
- **版本控制**：所有更改都通过 Git 提交记录，便于追踪
- **透明运行**：所有工作流日志都在 GitHub Actions 中可见

## 🛠️ 高级用法

### 自定义输出文件名

编辑 `scripts/merge_interfaces.py` 中的 `OUTPUT_DIR` 变量：

```python
OUTPUT_DIR = Path(__file__).parent.parent / "dist"  # 修改输出目录
```

### 添加自定义过滤逻辑

在 `merge_sources()` 函数中添加过滤条件，例如只保留特定类型的源：

```python
# 示例：只保留包含 "4K" 或 "蓝光" 的源
for site in config.get("sites", []):
    if "4K" in site.get("name", "") or "蓝光" in site.get("name", ""):
        merged_config["sites"].append(site)
```

### 集成自定义源

如果您有自己的影视源，可以将其添加到 `UPSTREAM_SOURCES` 列表中：

```python
{
    "name": "我的自定义源",
    "config_url": "https://my-server.com/index.config.js.md5",
    "js_url": "https://my-server.com/index.js.md5",
    "priority": 150,  # 设置最高优先级
},
```

## 📈 监控和调试

### 查看工作流日志

1. 进入 **Actions** 标签页
2. 选择最近的工作流运行
3. 点击 **MiraPlay Interface Aggregator** 查看详细日志

### 常见问题排查

| 问题 | 原因 | 解决方案 |
| :--- | :--- | :--- |
| 工作流失败 | 上游源不可访问 | 检查网络连接，确认上游源 URL 有效 |
| MD5 不匹配 | 文件内容变更 | 这是正常的，表示配置已更新 |
| GitHub Pages 无法访问 | Pages 未启用 | 进入 Settings → Pages，启用 GitHub Pages |
| 源数量减少 | 去重或优先级过滤 | 检查 `metadata.json` 了解详情 |

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进本项目！

## 📝 许可证

本项目采用 **MIT 许可证**。详见 [LICENSE](LICENSE) 文件。

## 🔗 相关资源

- [CatPawOpen 协议文档](https://github.com/catvod/CatVodTVSpider)
- [MiraPlay 官方](https://apps.apple.com/us/app/miraplay/id1669201695)
- [JSTV 官方](https://testflight.apple.com/join/4N2pkqa3)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

## 📞 支持

如有问题或建议，请在 GitHub Issues 中提出。

---

**最后更新**: 2026-04-22  
**维护者**: Manus AI  
**状态**: 🟢 活跃维护
