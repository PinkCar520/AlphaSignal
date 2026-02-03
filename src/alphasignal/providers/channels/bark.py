import requests
from src.alphasignal.config import settings
from src.alphasignal.core.logger import logger
from src.alphasignal.providers.channels.base import BaseChannel

class BarkChannel(BaseChannel):
    def send(self, title, message):
        if not settings.BARK_URL or "YOUR_TOKEN" in settings.BARK_URL:
            logger.warning("Bark 推送未配置，跳过")
            return

        try:
            # Bark 支持 GET 请求: URL/title/body
            # 简单处理，实际可能需要更严谨的 URL 拼接
            url = f"{settings.BARK_URL.rstrip('/')}/{title}/{message}"
            requests.get(url)
            logger.info("Bark 推送已发送")
        except Exception as e:
            logger.error(f"Bark 发送失败: {e}")
