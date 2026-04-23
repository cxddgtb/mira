# 项目文件清单

## 📁 目录结构

```
miraplay-aggregator/
├── .github/
│   └── workflows/
│       └── merge-interfaces.yml          # GitHub Actions 工作流配置
├── scripts/
│   ├── merge_interfaces_v2.py            # ⭐ 核心整合脚本（推荐使用）
│   ├── merge_interfaces.py               # 整合脚本初始版本
│   ├── test_merge_demo.py                # 演示脚本（本地测试）
│   ├── test_config.json                  # 测试配置文件 1
│   └── test_config_2.json                # 测试配置文件 2
├── dist/                                 # 输出目录（自动生成）
│   ├── index.config.js                   # 合并后的配置文件
│   ├── index.config.js.md5               # MD5 校验值
│   └── metadata.json                     # 整合元数据
├── 📄 README.md                          # 项目主文档
├── 📄 QUICKSTART.md                      # 快速开始指南（推荐新手阅读）
├── 📄 INTEGRATION_GUIDE.md               # 深度技术指南
├── 📄 TECHNICAL_SUMMARY.md               # 技术总结
├── 📄 PROJECT_FILES.md                   # 本文件
└── 📄 LICENSE                            # MIT 许可证
```

## 📄 文档说明

### 核心文档

| 文件 | 用途 | 推荐读者 |
| :--- | :--- | :--- |
| **QUICKSTART.md** | 5 分钟快速部署指南 | 新手用户 |
| **README.md** | 项目完整说明 | 所有用户 |
| **INTEGRATION_GUIDE.md** | 深度技术指南 | 进阶用户、开发者 |
| **TECHNICAL_SUMMARY.md** | 技术架构总结 | 开发者、贡献者 |

### 阅读建议

**第一次使用？**
1. 先读 [QUICKSTART.md](QUICKSTART.md) - 5 分钟快速上手
2. 再读 [README.md](README.md) - 了解完整功能

**想深入了解？**
1. 读 [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - 协议和整合原理
2. 读 [TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md) - 技术架构

**想贡献代码？**
1. 读 [TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md) - 了解架构
2. 查看 [scripts/merge_interfaces_v2.py](scripts/merge_interfaces_v2.py) - 核心代码

## 🔧 脚本说明

### merge_interfaces_v2.py（推荐）

**用途**：生产环境中的核心整合脚本

**特点**：
- ✅ 支持多种编码格式
- ✅ 完善的错误处理
- ✅ 测试模式支持
- ✅ 详细的日志输出

**使用方法**：
```bash
# 生产模式（从上游源获取）
python scripts/merge_interfaces_v2.py

# 测试模式（使用本地配置）
TEST_MODE=true python scripts/merge_interfaces_v2.py
```

### test_merge_demo.py（演示）

**用途**：本地演示和测试

**特点**：
- 加载两个本地测试配置
- 演示合并过程
- 生成 MD5 校验值
- 输出详细的统计信息

**使用方法**：
```bash
python scripts/test_merge_demo.py
```

### merge_interfaces.py（初始版本）

**用途**：初始实现版本

**状态**：已被 v2 版本替代，保留用于参考

## 📊 配置文件说明

### test_config.json

包含示例源：
- 豆瓣电影
- CCTV
- 哔哩哔哩

包含示例解析器：
- 官方解析
- 备用解析 1
- 备用解析 2

### test_config_2.json

包含示例源：
- 腾讯视频
- 爱奇艺
- 优酷
- 芒果 TV

包含示例解析器：
- 高清解析
- 极速解析

## 🚀 GitHub Actions 工作流

### merge-interfaces.yml

**触发条件**：
- 每天 UTC 0 点自动运行
- 手动触发（Workflow Dispatch）
- Push 到 main 分支时运行

**执行步骤**：
1. 检出代码
2. 设置 Python 环境
3. 安装依赖
4. 运行整合脚本
5. 生成报告
6. 部署到 GitHub Pages
7. 提交更改

## 📦 输出文件说明

### index.config.js

**内容**：合并后的配置文件

**格式**：JavaScript 对象

**示例**：
```javascript
var index_config_default = {
  "sites": [...],
  "parses": [...],
  "flags": [...],
  ...
};
module.exports = index_config_default;
```

### index.config.js.md5

**内容**：32 位十六进制 MD5 校验值

**用途**：客户端验证文件完整性

**示例**：
```
ca5029b388610b07fc33818fb1c435bd
```

### metadata.json

**内容**：整合元数据

**包含信息**：
- 生成时间
- 源数量统计
- 解析器数量
- MD5 校验值
- 文件大小

**示例**：
```json
{
  "generated_at": "2026-04-22T09:53:46.308702",
  "merged_sources": 2,
  "total_sites": 7,
  "total_parses": 5,
  "config_md5": "ca5029b388610b07fc33818fb1c435bd"
}
```

## 🔗 快速链接

- [快速开始](QUICKSTART.md)
- [完整文档](README.md)
- [技术指南](INTEGRATION_GUIDE.md)
- [技术总结](TECHNICAL_SUMMARY.md)
- [许可证](LICENSE)

---

**最后更新**：2026-04-22  
**版本**：1.0
