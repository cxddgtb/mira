# 🚀 MiraPlay 接口整合项目 - 快速开始

欢迎使用 **MiraPlay Interface Aggregator**！本指南将帮助您在 5 分钟内完成部署。

## 📋 前置要求

- GitHub 账户（免费）
- MiraPlay 应用（iOS）或 JSTV（iOS）
- 基本的网络连接

## ⚡ 5 分钟快速部署

### 第 1 步：Fork 项目（1 分钟）

1. 访问 [项目 GitHub 页面](https://github.com/your-repo/miraplay-aggregator)
2. 点击右上角的 **Fork** 按钮
3. 等待 Fork 完成

### 第 2 步：启用 GitHub Pages（2 分钟）

1. 进入您 Fork 的仓库
2. 点击 **Settings** 标签页
3. 在左侧菜单找到 **Pages**
4. 在 **Source** 下拉菜单中选择 **Deploy from a branch**
5. 选择分支为 **gh-pages**
6. 点击 **Save**

### 第 3 步：运行工作流（1 分钟）

1. 进入 **Actions** 标签页
2. 选择 **MiraPlay Interface Aggregator** 工作流
3. 点击 **Run workflow** → **Run workflow**
4. 等待工作流完成（通常 1-2 分钟）

### 第 4 步：获取订阅链接（1 分钟）

工作流完成后，您的订阅链接为：

```
https://<your-username>.github.io/miraplay-aggregator/index.config.js.md5
```

**示例**：
```
https://john-doe.github.io/miraplay-aggregator/index.config.js.md5
```

### 第 5 步：在 MiraPlay 中添加订阅

1. 打开 **MiraPlay** 应用
2. 进入 **设置** → **订阅管理**
3. 点击 **添加订阅**
4. 粘贴上述链接
5. 等待加载完成

**完成！** 🎉 现在您可以享受整合的影视资源了。

---

## 🎯 核心功能

| 功能 | 说明 |
| :--- | :--- |
| **自动更新** | 每天自动从多个源抓取最新配置 |
| **智能去重** | 自动移除重复的源和解析器 |
| **优先级管理** | 按照配置的优先级排序源 |
| **MD5 校验** | 确保数据完整性和增量更新 |
| **GitHub Pages** | 提供稳定的 HTTPS 访问链接 |

---

## 📊 包含的源

本项目默认整合以下高质量源：

| 源名称 | 优先级 | 说明 |
| :--- | :--- | :--- |
| 王二小 (蓝光首选) | ⭐⭐⭐⭐⭐ | 4K 蓝光，更新最快 |
| Jsnzkpg 开发者源 | ⭐⭐⭐⭐ | 开发者维护，质量稳定 |
| 9280 公益源 | ⭐⭐⭐ | 公益项目，资源丰富 |
| Jadehh 爬虫源 | ⭐⭐⭐ | 爬虫规则完整 |

---

## 🔧 常见问题

### Q: 工作流失败了怎么办？

**A**: 检查工作流日志：
1. 进入 **Actions** 标签页
2. 点击失败的工作流
3. 查看 **Run workflow** 步骤的日志
4. 确认上游源是否可访问

### Q: 如何添加自己的源？

**A**: 编辑 `scripts/merge_interfaces_v2.py` 中的 `UPSTREAM_SOURCES` 列表，添加您的源信息。

### Q: 更新频率是多少？

**A**: 默认每天 UTC 0 点自动更新。可在 `.github/workflows/merge-interfaces.yml` 中修改 `cron` 表达式。

### Q: 如何验证 MD5？

**A**: MiraPlay 会自动验证。如果 MD5 不匹配，说明配置已更新，应用会自动下载新版本。

### Q: 支持哪些应用？

**A**: 支持所有兼容 CatPawOpen 协议的应用，包括：
- MiraPlay（iOS）
- JSTV（iOS）
- 其他兼容应用

---

## 📚 深入学习

- **[完整技术指南](INTEGRATION_GUIDE.md)**：详细的技术说明和高级配置
- **[GitHub Actions 文档](https://docs.github.com/en/actions)**：了解工作流的工作原理
- **[CatVod 官方仓库](https://github.com/catvod/CatVodTVSpider)**：了解 CatPawOpen 协议

---

## 🆘 需要帮助？

如有问题，请：

1. 查看 [完整技术指南](INTEGRATION_GUIDE.md) 中的故障排查部分
2. 在 GitHub Issues 中提出问题
3. 检查工作流日志了解具体错误信息

---

## 📝 许可证

本项目采用 **MIT 许可证**。详见 [LICENSE](LICENSE) 文件。

---

**准备好了吗？现在就 [开始部署](#5-分钟快速部署) 吧！** 🚀

---

**最后更新**: 2026-04-22  
**版本**: 1.0  
**维护者**: Manus AI
