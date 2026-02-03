import smtplib
from email.mime.text import MIMEText
from email.header import Header
from src.alphasignal.config import settings
from src.alphasignal.core.logger import logger
from src.alphasignal.providers.channels.base import BaseChannel

class EmailChannel(BaseChannel):
    def send(self, title, message):
        if not settings.EMAIL_SENDER or not settings.EMAIL_PASSWORD:
            logger.warning("邮件配置缺失，跳过发送")
            return

        try:
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['Subject'] = Header(title, 'utf-8')
            msg['From'] = settings.EMAIL_SENDER
            msg['To'] = settings.EMAIL_RECEIVER

            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_SENDER, [settings.EMAIL_RECEIVER], msg.as_string())
            server.quit()
            logger.info(f"邮件已发送至 {settings.EMAIL_RECEIVER}")
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
