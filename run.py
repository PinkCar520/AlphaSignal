import schedule
import time
import sys
import os

# 确保 src 目录在 path 中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.alphasignal.config import settings
from src.alphasignal.core.logger import logger
from src.alphasignal.core.engine import AlphaEngine

def main():
    logger.info("==========================================")
    logger.info("   AlphaSignal 2.0 - 智能情报监控系统启动")
    logger.info("==========================================")
    logger.info(f"监控间隔: {settings.CHECK_INTERVAL_MINUTES} 分钟")
    logger.info(f"AI 模型: {settings.GEMINI_MODEL} (备用: {settings.DEEPSEEK_MODEL})")

    engine = AlphaEngine()

    # 立即执行一次
    engine.run_once()

    # 定时任务
    schedule.every(settings.CHECK_INTERVAL_MINUTES).minutes.do(engine.run_once)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("系统停止运行")

if __name__ == "__main__":
    main()
