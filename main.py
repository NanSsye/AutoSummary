from utils.plugin_base import PluginBase
from utils.decorators import on_text_message, on_file_message
import aiohttp
import re
import os
import tomllib
from loguru import logger
from typing import Dict, Optional
import json
import html
import xml.etree.ElementTree as ET

class AutoSummary(PluginBase):
    description = "自动总结文本内容和卡片消息"
    author = "老夏的金库"
    version = "1.0.0"
    
    URL_PATTERN = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[-\w./?=&]*'
    
    def __init__(self):
        super().__init__()
        self.name = "AutoSummary"
        
        config_path = os.path.join(os.path.dirname(__file__), "config.toml")
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
            
        self.config = config.get("AutoSummary", {})
        dify_config = self.config.get("Dify", {})
        self.dify_enable = dify_config.get("enable", False)
        self.dify_api_key = dify_config.get("api-key", "")
        self.dify_base_url = dify_config.get("base-url", "")
        self.http_proxy = dify_config.get("http-proxy", "")
        
        settings = self.config.get("Settings", {})
        self.max_text_length = settings.get("max_text_length", 8000)
        self.black_list = settings.get("black_list", [])
        self.white_list = settings.get("white_list", [])
        
        self.http_session = aiohttp.ClientSession()
        
        if not self.dify_enable or not self.dify_api_key or not self.dify_base_url:
            logger.warning("Dify配置不完整，自动总结功能将被禁用")
            self.dify_enable = False

    async def close(self):
        if self.http_session:
            await self.http_session.close()
            logger.info("HTTP会话已关闭")

    def _check_url(self, url: str) -> bool:
        stripped_url = url.strip()
        if not stripped_url.startswith(('http://', 'https://')):
            return False
        if self.white_list and not any(stripped_url.startswith(white_url) for white_url in self.white_list):
            return False
        if any(stripped_url.startswith(black_url) for black_url in self.black_list):
            return False
        return True

    async def _fetch_url_content(self, url: str) -> Optional[str]:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            }
            async with self.http_session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status != 200:
                    logger.error(f"获取初始URL失败: {response.status}, URL: {url}")
                    return None
                final_url = str(response.url)
                logger.info(f"重定向后的URL: {final_url}")

            jina_url = f"https://r.jina.ai/{final_url}"
            async with self.http_session.get(jina_url, headers=headers) as jina_response:
                if jina_response.status == 200:
                    content = await jina_response.text()
                    logger.info(f"从 Jina AI 获取内容成功: {jina_url}, 内容长度: {len(content)}")
                    return content
                else:
                    logger.error(f"从 Jina AI 获取内容失败: {jina_response.status}, URL: {jina_url}")
                    return None
        except Exception as e:
            logger.error(f"获取URL内容时出错: {e}, URL: {url}")
            return None

    async def _send_to_dify(self, content: str, is_xiaohongshu: bool = False) -> Optional[str]:
        if not self.dify_enable:
            return None
        try:
            content = content[:self.max_text_length]
            if is_xiaohongshu:
                prompt = f"""请对以下小红书笔记进行总结，关注以下方面：
1. 📝 一句话概括笔记主要内容
2. 🔑 核心要点（3-5点）
3. 💡 作者的主要观点或建议
4. 🏷️ 相关标签（2-3个）

原文内容：
{content}
"""
            else:
                prompt = f"""请对以下内容进行总结：
1. 📝 一句话总结
2. 🔑 关键要点（3-5点）
3. 🏷️ 相关标签（2-3个）

原文内容：
{content}
"""
            headers = {
                "Authorization": f"Bearer {self.dify_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": {},
                "query": prompt,
                "response_mode": "blocking",
                "conversation_id": None,
                "user": "auto_summary"
            }
            url = f"{self.dify_base_url}/chat-messages"
            async with self.http_session.post(
                url=url,
                headers=headers,
                json=payload,
                proxy=self.http_proxy if self.http_proxy else None
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("answer", "")
                else:
                    error_text = await response.text()
                    logger.error(f"调用Dify API失败: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"调用Dify API时出错: {e}")
            return None

    def _process_xml_message(self, message: Dict) -> Optional[Dict]:
        try:
            content = message.get("Content", "")
            logger.info(f"插件处理XML消息: MsgId={message.get('MsgId')}")
            logger.info(f"XML内容: {content[:200]}...")
            
            root = ET.fromstring(content)
            logger.info(f"解析XML根节点: {root.tag}")
            
            appmsg = root.find('appmsg')
            if appmsg is None:
                logger.warning("未找到 appmsg 节点")
                return None
                
            logger.info("找到 appmsg 节点")
            
            title_elem = appmsg.find('title')
            des_elem = appmsg.find('des')
            url_elem = appmsg.find('url')
            
            title = title_elem.text if title_elem is not None else ""
            description = des_elem.text if des_elem is not None else ""
            url = url_elem.text if url_elem is not None else None
            
            logger.info(f"提取的标题: {title}")
            logger.info(f"提取的描述: {description}")
            logger.info(f"提取的URL: {url}")
            
            if url is None:
                logger.warning("URL为空，跳过处理")
                return None
                
            url = html.unescape(url)
            logger.info(f"处理后的URL: {url}")
            
            # 检查是否是小红书
            is_xiaohongshu = '<appname>小红书</appname>' in content
            
            result = {
                'title': title,
                'description': description,
                'url': url,
                'is_xiaohongshu': is_xiaohongshu
            }
            logger.info(f"提取的信息: {result}")
            return result
            
        except ET.ParseError as e:
            logger.error(f"XML解析错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"处理XML消息时出错: {str(e)}")
            logger.exception(e)
            return None

    async def _process_url(self, url: str) -> Optional[str]:
        try:
            url_content = await self._fetch_url_content(url)
            if not url_content:
                return None
            return await self._send_to_dify(url_content)
        except Exception as e:
            logger.error(f"处理URL时出错: {e}")
            return None

    async def _handle_card_message(self, bot: 'WechatAPIClient', chat_id: str, info: Dict) -> bool:
        try:
            url_content = await self._fetch_url_content(info['url'])
            if not url_content:
                await bot.send_text_message(chat_id, "❌ 抱歉，无法获取卡片内容")
                return False

            content_to_summarize = f"""
标题：{info['title']}
描述：{info['description']}
正文：{url_content}
"""
            await bot.send_text_message(chat_id, "🔍 正在为您生成内容总结，请稍候...")
            summary = await self._send_to_dify(content_to_summarize, is_xiaohongshu=info['is_xiaohongshu'])
            if not summary:
                await bot.send_text_message(chat_id, "❌ 抱歉，生成总结失败")
                return False
            prefix = "🎯 小红书笔记总结如下" if info['is_xiaohongshu'] else "🎯 卡片内容总结如下"
            await bot.send_text_message(chat_id, f"{prefix}：\n\n{summary}")
            return False
        except Exception as e:
            logger.error(f"处理卡片消息时出错: {e}")
            await bot.send_text_message(chat_id, "❌ 抱歉，处理卡片内容时出现错误")
            return False

    @on_text_message(priority=50)
    async def handle_text_message(self, bot: 'WechatAPIClient', message: Dict) -> bool:
        if not self.dify_enable:
            return True
            
        content = message.get("Content", "")
        chat_id = message.get("FromWxid", "")
        
        logger.info(f"收到文本消息: chat_id={chat_id}, content={content[:100]}...")
        
        content = html.unescape(content)
        urls = re.findall(self.URL_PATTERN, content)
        if urls:
            url = urls[0]
            logger.info(f"找到URL: {url}")
            if self._check_url(url):
                try:
                    await bot.send_text_message(chat_id, "🔍 正在为您生成内容总结，请稍候...")
                    summary = await self._process_url(url)
                    if summary:
                        await bot.send_text_message(chat_id, f"🎯 内容总结如下：\n\n{summary}")
                        return False
                    else:
                        await bot.send_text_message(chat_id, "❌ 抱歉，生成总结失败")
                        return False
                except Exception as e:
                    logger.error(f"处理URL时出错: {e}")
                    await bot.send_text_message(chat_id, "❌ 抱歉，处理过程中出现错误")
                    return False
        return True

    @on_file_message(priority=50)
    async def handle_file_message(self, bot: 'WechatAPIClient', message: Dict) -> bool:
        if not self.dify_enable:
            return True
            
        chat_id = message.get("FromWxid", "")
        logger.info(f"收到XML消息: type=49, chat_id={chat_id}")
        
        card_info = self._process_xml_message(message)
        if card_info:
            logger.info("识别为卡片消息，开始处理")
            return await self._handle_card_message(bot, chat_id, card_info)
        
        logger.info("非卡片XML消息或解析失败，跳过处理")
        return True