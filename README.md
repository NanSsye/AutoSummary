# 🎉 XYBotV2 自动总结插件 (AutoSummary) 🎉


快速总结文本内容和卡片消息，让你的 XYBotV2 瞬间变身效率助手！🚀

<img src="https://github.com/user-attachments/assets/a2627960-69d8-400d-903c-309dbeadf125" width="400" height="600">

## ✍️ 插件描述

`AutoSummary` 是一款为 XYBotV2 设计的插件，旨在帮助用户**快速总结**微信聊天中的**文本内容**和**卡片消息**。它能够：

* ✨ **自动提取文本消息中的链接**，并抓取网页内容进行总结。
* 📰 **解析微信卡片消息 (XML 消息)**，例如公众号文章分享等，并进行内容概括。
* 🤖 **集成 Dify API**，利用强大的 AI 能力生成高质量的摘要。
* 🛡️ **支持黑名单和白名单**，灵活控制插件处理的链接范围。

无论是快速了解群内分享的文章内容，还是概括长篇对话的重点，`AutoSummary` 都能帮你节省宝贵的时间！

## 👨‍💻 作者

* 老夏的金库

## 🌟 插件特性

* **多种内容总结**:
    * **文本消息 📝**: 自动检测文本消息中的 URL 链接，并进行网页内容总结。
    * **卡片消息 📰**:  支持解析和总结微信卡片消息 (XML 格式)，例如微信公众号文章分享、小程序卡片等。
* **强大的 AI 摘要 🧠**:  深度集成 [Dify API](https://dify.ai/)，利用先进的 AI 模型生成精准、简洁的摘要，让您快速抓住重点。
* **灵活的 URL 过滤 🔗**:
    * **白名单机制 ⚪**:  只总结白名单域名下的链接，更精准地控制插件作用范围。
    * **黑名单机制 ⚫**:  排除黑名单域名下的链接，避免总结不感兴趣的内容。
* **可配置参数 ⚙️**:  通过 `config.toml` 文件，您可以自定义 Dify API 配置、黑白名单、最大文本长度等参数，满足个性化需求。
* **异步处理 ⏱️**:  采用 `asyncio` 异步框架，保证插件高效运行，不阻塞 XYBotV2 主程序。
* **详细日志 记录 🪵**:  使用 `loguru` 记录详细日志，方便问题排查和插件监控。

## 🛠️ 安装教程

1. **下载插件**：将 `AutoSummary` 插件文件夹放入 XYBotV2 的 `plugins` 目录下。
2. **配置插件**：修改 `plugins/AutoSummary/config.toml` 文件，填入您的 Dify API 相关配置以及其他自定义设置。
3. **替换文件**：替换xybot.py到/utils/xybot.py
4. **重启 XYBotV2**：重启您的 XYBotV2 机器人，插件即可生效。

## ⚙️ 配置文件 (config.toml)

您需要在 `plugins/AutoSummary/config.toml` 文件中配置以下参数：

```toml
[AutoSummary]
enable = true

[AutoSummary.Dify]
enable = true
api-key = "app-7r0xBzXNaBEQjBJks0N6wdJO"  # 请替换为实际的 API Key
base-url = "[http://192.168.6.19:8080/v1](http://192.168.6.19:8080/v1)"  # 请替换为实际的 API URL
http-proxy = ""  # 如果需要代理可以在这里设置

[AutoSummary.Settings]
max_text_length = 8000  # 最大文本长度
black_list = [  # 黑名单URL
    "[https://support.weixin.qq.com](https://support.weixin.qq.com)",
    "[https://channels-aladin.wxqcloud.qq.com](https://channels-aladin.wxqcloud.qq.com)"
]
white_list = []  # 白名单URL，为空则允许所有非黑名单URL
```

**配置说明:**

* ​**`[AutoSummary.Dify]`**​:  Dify API 相关配置。
  * `enable`:  ​**是否启用 Dify 摘要功能**​。设置为 `true` 启用，`false` 禁用。禁用后，插件将无法生成摘要。
  * `api-key`:  ​**您的 Dify API Key**​。如果您启用了 Dify 摘要功能 (`enable = true`)，则必须填写您的 Dify API Key。
  * `base-url`:  ​**您的 Dify API Base URL**​。如果您启用了 Dify 摘要功能 (`enable = true`)，则必须填写您的 Dify API Base URL。 通常是您的 Dify 服务地址，例如 `http://localhost:8000` 或您的 Dify 云服务地址。
  * `http-proxy`:  ​**HTTP 代理设置 (可选)**​。如果您需要通过 HTTP 代理访问 Dify API，请在此处填写代理地址。
* ​**`[AutoSummary.Settings]`**​: 插件通用设置。
  * `max_text_length`:  ​**最大文本长度**​。限制发送给 Dify API 进行总结的文本长度，防止内容过长导致 API 调用失败或消耗过多资源。 默认值为 `8000` 字符。
  * `black_list`:  ​**URL 黑名单**​。  插件将不会总结黑名单列表中域名下的任何链接。  您可以根据需要添加域名到此列表，例如您不希望总结某些特定网站的内容。
  * `white_list`:  ​**URL 白名单**​。  **只有** 白名单列表中的域名下的链接才会被插件总结。  如果此列表为空，则 ​**不启用白名单**​，插件将总结所有 **非黑名单** 域名下的链接。  如果您希望插件只处理特定网站的链接，可以配置白名单。

## 💡 使用方法

1. ​**发送文本消息包含 URL 链接**​： 当你在微信群或私聊中发送包含 URL 链接的文本消息时，如果链接符合插件的过滤规则 (非黑名单，或在白名单内)，插件将自动抓取网页内容并生成摘要回复给你。
2. ​**接收到微信卡片消息**​： 当你在微信中接收到卡片消息 (例如，别人分享的微信公众号文章) 时，插件会自动解析卡片内容并尝试生成摘要回复。

**示例对话:**

**用户:**  [发送一条包含 URL 链接的文本消息]  例如：  "大家看看这篇文章 [https://example.com/amazing-article](https://www.google.com/url?sa=E&source=gmail&q=https://www.google.com/url?sa=E%26source=gmail%26q=https://example.com/amazing-article)  讲的真不错！"

**XYBotV2 机器人:**  🔍 正在为您生成内容总结，请稍候...

**XYBotV2 机器人:**  🎯 内容总结如下：

> [Dify API 生成的文章摘要内容]

**用户:**  [在微信群中接收到一张微信公众号文章卡片消息]

**XYBotV2 机器人:**  🔍 正在为您生成内容总结，请稍候...

**XYBotV2 机器人:**  🎯 卡片内容总结如下：

> [Dify API 生成的卡片消息摘要内容]

## ⚙️ 替换 `utils/xybot.py` (⚠️ 注意)


## ⚠️  重要依赖

* [XYBotV2](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/your-xybotv2-repo-link) (请替换成 XYBotV2 的实际 GitHub 仓库链接) -  本插件基于 XYBotV2 框架开发。
* `aiohttp` -  用于异步 HTTP 请求。
* `loguru` -  用于日志记录。
* `toml`  -  用于 TOML 配置文件解析。
* [Dify API](https://www.google.com/url?sa=E&source=gmail&q=https://dify.ai/) -  可选，用于 AI 摘要生成。 强烈建议使用以获得最佳摘要效果。

## 📜  免责声明

* 本插件依赖于 [Dify API](https://www.google.com/url?sa=E&source=gmail&q=https://dify.ai/)  服务进行内容摘要生成。  ​**您需要自行注册 Dify 服务并获取 API Key，并可能需要承担 Dify API 的使用费用 (如果 Dify 服务是收费的)**​。
* 插件提供的摘要结果仅供参考，不能保证完全准确和完整。
* 请遵守相关法律法规和平台使用协议，合理使用本插件。

## 🤝 联系方式

如果您有任何问题、建议或想参与插件开发，欢迎通过以下方式联系作者：

* [仓库地址](https://github.com/NanSsye)


感谢您的使用！⭐

<img src="https://github.com/user-attachments/assets/1e1b3e0f-fab8-4cc6-9011-3b0e8bf10737" width="200" height="400">

**给个 ⭐ Star 支持吧！** 😊

**开源不易，感谢打赏支持！**

![image](https://github.com/user-attachments/assets/2dde3b46-85a1-4f22-8a54-3928ef59b85f)



