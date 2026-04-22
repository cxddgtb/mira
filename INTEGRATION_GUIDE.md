# MiraPlay 接口整合工作流 - 深度技术指南

本文档详细说明了如何使用本项目将多个 CatPawOpen 协议的影视接口源整合为一个统一的订阅接口。

## 📚 目录

1. [CatPawOpen 协议基础](#catpawopen-协议基础)
2. [整合原理](#整合原理)
3. [部署步骤](#部署步骤)
4. [高级配置](#高级配置)
5. [故障排查](#故障排查)

---

## CatPawOpen 协议基础

### 什么是 CatPawOpen？

**CatPawOpen** 是一个开源的影视聚合协议，由 **猫影视（CatVod）** 项目定义。它允许应用通过加载外部 JavaScript 规则文件来动态获取影视资源。

### 核心文件结构

CatPawOpen 接口通常包含以下文件：

| 文件名 | 说明 | 格式 |
| :--- | :--- | :--- |
| `index.js` | 核心逻辑文件，包含爬虫规则和解析器 | JavaScript (打包后) |
| `index.config.js` | 配置文件，定义影视源和解析器列表 | JavaScript 对象 |
| `index.js.md5` | `index.js` 的 MD5 校验值 | 32 位十六进制字符串 |
| `index.config.js.md5` | `index.config.js` 的 MD5 校验值 | 32 位十六进制字符串 |

### index.config.js 的结构

```javascript
var index_config_default = {
  "sites": [
    {
      "key": "源唯一标识",
      "name": "源显示名称",
      "type": 0,  // 0=网址, 1=本地, 2=未知, 3=插件
      "api": "爬虫规则名称或 URL",
      "searchable": 1,  // 是否支持搜索
      "quickSearch": 1,  // 是否支持快速搜索
      "filterable": 1   // 是否支持筛选
    }
  ],
  "parses": [
    {
      "name": "解析器名称",
      "type": 0,  // 0=网址, 1=插件
      "url": "解析器地址",
      "ua": "User-Agent (可选)"
    }
  ],
  "flags": [
    {
      "flag": "标志名",
      "name": "标志显示名"
    }
  ],
  "ijk": [],        // IJKPlayer 配置
  "ads": [],        // 广告过滤规则
  "wallpaper": "",  // 壁纸 URL
  "spider": "",     // 爬虫规则 URL
  "lives": []       // 直播源
};
```

### MD5 校验机制

MiraPlay 等客户端的工作流程：

```
1. 客户端下载 index.config.js.md5 文件
2. 计算本地 index.config.js 的 MD5 值
3. 比较两个 MD5 值
   - 如果不同 → 下载新的 index.config.js
   - 如果相同 → 使用本地缓存
```

这种机制确保了增量更新，节省带宽。

---

## 整合原理

### 为什么需要整合？

单个接口源可能存在以下问题：

- **资源不完整**：某些源缺少特定类型的影视资源
- **稳定性差**：单个源可能随时失效
- **更新不及时**：不同源的更新频率不同
- **功能不全**：某些源缺少特定的解析器或功能

通过整合多个源，可以实现：

- ✅ **资源互补**：获得更多的影视资源
- ✅ **容错机制**：某个源失效时自动切换
- ✅ **性能优化**：选择最快的源和解析器
- ✅ **功能完整**：汇聚所有源的功能

### 整合流程

```
┌─────────────────────────────────────────────────────────────┐
│ 步骤1: 获取上游源                                            │
│ 从配置的多个源下载 index.config.js 文件                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤2: 解析配置                                              │
│ 使用正则表达式和 JSON 解析器提取配置对象                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤3: 合并配置                                              │
│ 去重、按优先级排序、解决冲突                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤4: 生成输出                                              │
│ 生成新的 index.config.js 和 MD5 文件                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤5: 部署                                                  │
│ 上传到 GitHub Pages，生成订阅链接                           │
└─────────────────────────────────────────────────────────────┘
```

### 去重和优先级管理

**去重策略**：

- **Sites**：按 `key` 去重，保留优先级最高的版本
- **Parses**：按 `name` 去重，保留优先级最高的版本
- **其他**：使用 JSON 序列化后的字符串去重

**优先级**：

在 `UPSTREAM_SOURCES` 中配置的 `priority` 值决定了源的优先级。数字越大优先级越高。

```python
UPSTREAM_SOURCES = [
    {
        "name": "王二小 (蓝光首选)",
        "priority": 100,  # 最高优先级
    },
    {
        "name": "9280 公益源",
        "priority": 80,   # 较低优先级
    },
]
```

---

## 部署步骤

### 第1步：Fork 项目

1. 访问 [本项目的 GitHub 页面](https://github.com/your-username/miraplay-aggregator)
2. 点击右上角的 **Fork** 按钮
3. 在您的账户中创建副本

### 第2步：启用 GitHub Pages

1. 进入您 Fork 的仓库
2. 点击 **Settings** 标签页
3. 在左侧菜单找到 **Pages**
4. 在 **Source** 下拉菜单中选择 **Deploy from a branch**
5. 选择分支为 **gh-pages**
6. 点击 **Save**

等待几分钟后，您会看到类似的提示：

```
Your site is live at https://<your-username>.github.io/miraplay-aggregator/
```

### 第3步：手动运行工作流

1. 进入 **Actions** 标签页
2. 在左侧找到 **MiraPlay Interface Aggregator** 工作流
3. 点击 **Run workflow** 按钮
4. 选择 **main** 分支
5. 点击 **Run workflow**

等待工作流完成（通常需要 1-2 分钟）。

### 第4步：获取订阅链接

工作流完成后，您的订阅链接为：

```
https://<your-username>.github.io/miraplay-aggregator/index.config.js.md5
```

例如：

```
https://john-doe.github.io/miraplay-aggregator/index.config.js.md5
```

### 第5步：在 MiraPlay 中添加订阅

1. 打开 MiraPlay 应用
2. 进入 **设置** → **订阅管理**
3. 点击 **添加订阅**
4. 粘贴上述链接
5. 等待加载完成

---

## 高级配置

### 修改上游源列表

编辑 `scripts/merge_interfaces_v2.py` 中的 `UPSTREAM_SOURCES` 列表：

```python
UPSTREAM_SOURCES = [
    {
        "name": "源名称",
        "config_url": "https://example.com/index.config.js",
        "priority": 100,
    },
    # 添加更多源...
]
```

**注意**：
- `config_url` 应该指向 `index.config.js` 文件（不是 `.md5` 文件）
- `priority` 值越大优先级越高
- 建议为最强的源设置最高优先级

### 自定义更新频率

编辑 `.github/workflows/merge-interfaces.yml` 中的 `cron` 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天 UTC 0 点运行
```

**Cron 表达式格式**：`分 小时 日 月 周`

常见示例：

| 表达式 | 说明 |
| :--- | :--- |
| `0 0 * * *` | 每天 UTC 0 点 |
| `0 */6 * * *` | 每 6 小时 |
| `0 9 * * 1` | 每周一上午 9 点 |
| `0 0 1 * *` | 每月 1 号 |

### 添加自定义过滤逻辑

在 `merge_interfaces_v2.py` 的 `merge_sources()` 函数中添加过滤条件：

```python
def merge_sources(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    # ... 现有代码 ...
    
    for source in sources:
        config = source.get("config", {})
        priority = source.get("priority", 0)
        
        # 添加自定义过滤：只保留包含 "4K" 的源
        for site in config.get("sites", []):
            if "4K" in site.get("name", ""):
                # 只添加包含 "4K" 的源
                if site.get("key") not in seen_sites:
                    seen_sites[site.get("key")] = (priority, site)
```

### 集成自定义源

如果您有自己的影视源，可以添加到列表中：

```python
UPSTREAM_SOURCES = [
    # ... 现有源 ...
    {
        "name": "我的自定义源",
        "config_url": "https://my-server.com/index.config.js",
        "priority": 150,  # 设置最高优先级
    },
]
```

---

## 故障排查

### 工作流失败

**症状**：Actions 页面显示红色 ❌

**原因**：
- 上游源无法访问
- 网络连接问题
- 配置文件格式错误

**解决方案**：
1. 检查工作流日志（点击失败的工作流查看详情）
2. 确认上游源 URL 是否有效
3. 尝试手动访问上游源的 `index.config.js` 文件

### MD5 不匹配

**症状**：MiraPlay 显示"配置校验失败"

**原因**：这通常是正常的，表示配置已更新

**解决方案**：
1. 在 MiraPlay 中删除订阅
2. 重新添加订阅链接
3. 等待重新加载

### GitHub Pages 无法访问

**症状**：访问 `https://<username>.github.io/miraplay-aggregator/` 显示 404

**原因**：GitHub Pages 未正确启用

**解决方案**：
1. 进入仓库 Settings → Pages
2. 确保 Source 设置为 **Deploy from a branch**
3. 确保选择了 **gh-pages** 分支
4. 等待 1-2 分钟后重试

### 源数量减少

**症状**：合并后的源数量少于预期

**原因**：
- 去重移除了重复的源
- 优先级过滤
- 上游源无法访问

**解决方案**：
1. 查看 `dist/metadata.json` 了解详情
2. 检查工作流日志中的警告信息
3. 确认上游源是否仍然可用

### 解析器无法使用

**症状**：MiraPlay 中某些视频无法播放

**原因**：
- 解析器地址已失效
- 解析器不兼容
- 网络连接问题

**解决方案**：
1. 在 MiraPlay 中尝试其他解析器
2. 检查 `dist/index.config.js` 中的 `parses` 列表
3. 考虑添加备用解析器

---

## 📊 监控和维护

### 定期检查

建议每周检查一次：

1. 工作流是否正常运行
2. 源数量是否有明显变化
3. MiraPlay 中是否能正常加载资源

### 更新上游源

当发现新的高质量源时，可以添加到 `UPSTREAM_SOURCES` 列表中：

```python
{
    "name": "新源名称",
    "config_url": "https://new-source.com/index.config.js",
    "priority": 85,  # 根据质量设置优先级
},
```

### 备份配置

定期备份生成的配置文件：

```bash
# 备份到本地
git clone https://github.com/<username>/miraplay-aggregator.git backup/
```

---

## 🔗 参考资源

- [CatVod 官方仓库](https://github.com/catvod/CatVodTVSpider)
- [MiraPlay 官方](https://apps.apple.com/us/app/miraplay/id1669201695)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Cron 表达式参考](https://crontab.guru/)

---

**最后更新**: 2026-04-22  
**文档版本**: 1.0  
**维护者**: Manus AI
