# 📺 Mira Play 全自动订阅源采集系统

> ✅ 输出格式: `index.js.md5`（Mira Play 可直接订阅）  
> ✅ 支持链接: `http://user:pass@host/index.js.md5`（Basic Auth 认证）  
> ✅ 中文保证: 100% 保留原始中文名（UTF-8 编码 + ensure_ascii=False）  
> ✅ 全自动: 从 GitHub 发现全网公开接口 → 测试 → 滚雪球合并 → 生成订阅文件  

## ⚠️ 法律声明
本系统仅检索 **GitHub 公开开源仓库** 中的接口配置文件。所有数据来自社区分享，仅供技术研究、接口调试与个人学习。请严格遵守《网络安全法》《著作权法》及平台服务条款。

## 📦 核心能力
- 🔍 **零配置发现**：自动搜索 `.js` / `.md5` / `.json` / `.m3u8` + Basic Auth 链接
- 🧪 **智能测试**：异步并发验证接口可用性，自动识别点播/直播/音乐/有声小说
- 🔤 **中文无损**：全链路 `ensure_ascii=False` + UTF-8，`"name": "电影天堂"` 不转义
- ❄️ **滚雪球归档**：每次读取最近 10 个存档 + 本轮新数据 → 严格去重 → 持续增长
- 🎯 **标准输出**：生成 `data/index.js.md5`，内容符合 TVBox/Mira Play 配置规范：
  ```javascript
  var config = {
    "sites": [  // 点播接口
      {"key":"abc123","name":"🔥 高清影视","type":3,"api":"http://user:pass@host/api","searchable":1,...}
    ],
    "lives": [  // 直播源
      {"name":"📺 CCTV 直播","url":"http://xxx/live.m3u8","type":0,"playerType":1}
    ],
    "parses": [],
    "flags": ["youku","qq","iqiyi",...]
  };
