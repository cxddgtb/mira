// MiraPlay Interface Aggregator
// 生成时间: 2026-04-23T10:01:47.390420
// 合并源数: 2
// 生成工具: https://github.com/cxddgtb/mira

var index_config_default = {
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
    },
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
    },
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
    },
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
};

module.exports = index_config_default;
