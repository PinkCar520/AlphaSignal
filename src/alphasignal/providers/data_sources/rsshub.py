import json
import os
import feedparser
from src.alphasignal.config import settings
from src.alphasignal.core.logger import logger
from src.alphasignal.providers.data_sources.base import BaseDataSource

class RSSHubSource(BaseDataSource):
    def __init__(self):
        self.processed_ids = self._load_state()
        # 配置要监控的 Feed 路径
        self.feeds = [
            # 特朗普 Truth Social
            "/truthsocial/user/realDonaldTrump",
            # 彭博快讯 (如果有可用路由)
            "/bloomberg/news/terminal",
            # 路透社 宏观经济
            "/reuters/world/us"
        ]

    def fetch(self):
        """
        遍历所有配置的 RSSHub 路由
        """
        for route in self.feeds:
            rss_url = f"{settings.RSSHUB_BASE_URL.rstrip('/')}{route}"
            logger.info(f"正在扫描 RSSHub: {route}")
            
            try:
                feed = feedparser.parse(rss_url)
                if not feed.entries:
                    continue

                for entry in feed.entries:
                    # 使用 link 或 id 作为唯一标识
                    item_id = getattr(entry, 'id', entry.link)
                    
                    if item_id in self.processed_ids:
                        continue
                    
                    logger.info(f"🔥 [RSSHub] 发现新内容: {entry.title[:50]}...")
                    self._save_state(item_id)
                    
                    # 转换数据格式
                    return {
                        "source": f"RSSHub ({route})",
                        "author": "System",
                        "timestamp": getattr(entry, 'published', ""),
                        "content": f"{entry.title}. {getattr(entry, 'description', '')}",
                        "url": entry.link,
                        "id": item_id
                    }
            except Exception as e:
                logger.error(f"RSSHub 抓取失败 ({route}): {e}")
        
        return None

    def _load_state(self):
        if os.path.exists(settings.STATE_FILE):
            try:
                with open(settings.STATE_FILE, 'r') as f:
                    return set(json.load(f))
            except:
                pass
        return set()

    def _save_state(self, new_id):
        self.processed_ids.add(new_id)
        if len(self.processed_ids) > 2000: # 稍微调大点缓存
             self.processed_ids = set(list(self.processed_ids)[-2000:])
        with open(settings.STATE_FILE, 'w') as f:
            json.dump(list(self.processed_ids), f)
