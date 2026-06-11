<div align="center">

# 🔍 盘搜助手

<i>🤖 网盘资源搜索，一站直达</i>

![License](https://img.shields.io/badge/license-AGPL--3.0-green?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![AstrBot](https://img.shields.io/badge/framework-AstrBot-ff6b6b?style=flat-square)

</div>

## 📖 简介

一款为 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 设计的网盘资源搜索插件，对接 [PanSou](https://github.com/fish2018/pansou) 搜索引擎，聚合 Telegram 频道和搜索插件的网盘资源，支持百度、夸克、阿里云盘等十余种盘类型。

---

## ✨ 功能特性

### 🔍 资源搜索

* **多源聚合**: 同时搜索 Telegram 频道和多个网盘搜索插件，结果一站式呈现。
* **盘类型筛选**: 配置 `筛选盘类型` 后，对返回结果执行过滤，确保结果仅包含指定类型的条目。

### ✅️ 链接验证

* **自动验链**: 启用 `自动检测链接有效性` 配置后，列表页会自动检测链接有效性并隐藏完全失效的结果，详情页继续检测剩余未检测的链接。
* **无检测时**: 未启用时列表页不进行检测，进入详情页后检测但不隐藏失效链接，仅显示状态标记。

### ⚡️ 便捷操作

* **详情查看**: 输入编号查看单条结果的完整信息（标题、标签、内容、所有链接、配图）。
* **全局排除**: 配置排除关键词，自动过滤无关结果。

---

## 💿 安装

1. 下载本插件文件夹，放入 AstrBot 的 `data/plugins/` 目录下。
2. 重启 AstrBot。

---

## ⚙️ 配置

首次加载后，请在 AstrBot 后台 -> 插件 页面找到本插件进行设置。所有配置项都有详细的说明和介绍。

> [!IMPORTANT]
> 仅建议使用自建服务时开启 `自动检测链接有效性` 功能。

---

## 📖 使用指南

### 📋 指令列表

| 指令 | 作用 | 别名 |
| :--- | :--- | :--- |
| `/ps <关键词>` | 搜索网盘资源 | — |
| `/ps <编号>` | 查看单条详情 | — |
| `/ps n` | 下一页 | `next`, `下一页` |
| `/ps p` | 上一页 | `prev`, `上一页` |
| `/ps f <盘类型>` | 按盘类型过滤当前结果 | `filter`, `过滤` |
| `/ps help` | 显示帮助信息 | `帮助` |

### 💡 使用示例

**搜索资源**:
```
/ps 速度与激情
```

**查看详情**:
```
/ps 1
```

**翻页浏览**:
```
/ps n
/ps p
/ps next
/ps 下一页
```

**筛选盘类型**:
```
/ps f baidu
/ps filter kk
/ps filter 夸克
```

### 🔗 盘类型对照

| 参数 | 别名 | 盘类型 |
| :--- | :--- | :--- |
| `baidu` | `bd`, `百度` | 百度网盘 |
| `aliyun` | `ali`, `阿里` | 阿里云盘 |
| `quark` | `kk`, `夸克` | 夸克网盘 |
| `tianyi` | `ty`, `天翼` | 天翼云盘 |
| `115` | — | 115 网盘 |
| `xunlei` | `xl`, `迅雷` | 迅雷云盘 |
| `uc` | — | UC 网盘 |
| `123` | `123pan` | 123 云盘 |
| `pikpak` | `pk` | PikPak |
| `mobile` | `yd`, `移动`, `139` | 移动云盘 |
| `magnet` | `cl`, `磁力` | 磁力链接 |
| `ed2k` | `dl`, `电驴` | 电驴链接 |
| `guangya` | `gy`, `光鸭` | 光鸭网盘 |

---

## 🧭 链接状态说明

| 标记 | 含义 |
| :--- | :--- |
| ✅ | 链接有效 |
| ⚠️ | 链接已锁定、不支持检测或无法确定状态 |
| ❌ | 链接已失效 |
| 📎 | 未检测（超出检测范围或未启用自动验链） |


> [!TIP]
> 列表页仅检测前 5 条链接，详情页检测前 10 条。超出的链接不会检测，照常显示。

---

## 📝 更新日志

详见 [CHANGELOG](CHANGELOG.md)

---

## ❤️ 支持

* [AstrBot 帮助文档](https://astrbot.app)
* 如果您在使用中遇到问题，欢迎在本仓库提交 [Issue](https://github.com/Foolllll-J/astrbot_plugin_pansou/issues)。

---

<div align="center">

**如果本插件对你有帮助，欢迎点个 ⭐ Star 支持一下！**

</div>
