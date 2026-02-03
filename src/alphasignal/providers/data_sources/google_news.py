import json
import os
import time
import re
import urllib.parse
import feedparser
import dateparser
from src.alphasignal.config import settings
from src.alphasignal.core.logger import logger
from src.alphasignal.providers.data_sources.base import BaseDataSource

class GoogleNewsSource(BaseDataSource):
    """
    Google News Source using RSS feed for more reliable timestamps and stability.
    """
    # Quant-Grade Source Tiering
    SOURCE_TIERS = {
        'TIER_1': [ # Market Movers (Instant Alpha)
            'Bloomberg', 'Reuters', 'Wall Street Journal', 'WSJ', 'Financial Times', 'CNBC', 
            'Dow Jones', 'Barron\'s', 'Fox Business'
        ],
        'TIER_2': [ # Reliable Context (Confirmation)
            'The New York Times', 'Washington Post', 'Politico', 'Associated Press', 'AP News',
            'BBC', 'MarketWatch', 'Forbes', 'Fortune', 'Business Insider'
        ],
        'BLOCKED': [ # Noise / Tabloids / Opinion
            'Daily Mail', 'New York Post', 'Express', 'Sun', 'Mirror', 'Opinion', 'Blog', 'Substack'
        ]
    }

    # Noise Keywords (Skip these titles)
    NOISE_TITLES = ['Opinion:', 'Analysis:', 'Fact Check:', 'Podcast:', 'Watch:', 'Review:', 'Editorial:']

    def __init__(self):
        self.processed_ids = set()
        self.processed_hashes = {} 
        self._load_state()

    def _get_simhash(self, text):
        from simhash import Simhash
        width = 3
        text = text.lower()
        text = re.sub(r'[^\w]+', '', text)
        features = [text[i:i + width] for i in range(max(len(text) - width + 1, 1))]
        return Simhash(features)

    def _get_source_rank(self, source_name):
        """Return (Tier Level, Score Multiplier)"""
        for s in self.SOURCE_TIERS['TIER_1']:
            if s.lower() in source_name.lower(): return (1, 1.5)
        for s in self.SOURCE_TIERS['TIER_2']:
            if s.lower() in source_name.lower(): return (2, 1.0)
        for s in self.SOURCE_TIERS['BLOCKED']:
            if s.lower() in source_name.lower(): return (-1, 0.0)
        return (3, 0.8)

    def fetch(self, query: str = "Donald Trump (Truth Social OR Economy OR Tariff)", start_date: str = None, end_date: str = None):
        """
        Fetch news using Google News RSS.
        start_date/end_date should be in MM/DD/YYYY format for compatibility with search query.
        Example: query + ' after:2025-05-01 before:2025-06-01'
        """
        try:
            # 1. Build Search Query with Date Restrictions
            search_query = query
            
            # Google News RSS supports 'after:YYYY-MM-DD' and 'before:YYYY-MM-DD'
            def format_date_for_rss(date_str):
                if not date_str: return None
                try:
                    # Input is MM/DD/YYYY from historical importer
                    dt = datetime.strptime(date_str, '%m/%d/%Y')
                    return dt.strftime('%Y-%m-%d')
                except:
                    return date_str # Assume already formatted or handled by dateparser

            from datetime import datetime
            rss_after = format_date_for_rss(start_date)
            rss_before = format_date_for_rss(end_date)

            if rss_after: search_query += f" after:{rss_after}"
            if rss_before: search_query += f" before:{rss_before}"

            # 2. Encode URL
            encoded_query = urllib.parse.quote(search_query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            logger.info(f"Fetching Google News RSS: {rss_url}")
            
            # 3. Parse RSS Feed
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                logger.info("No new entries found in RSS.")
                return None

            new_items = []
            for entry in feed.entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                # Google News RSS title format is usually "Title - Source"
                source_name = "Unknown"
                clean_title = title
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    clean_title = parts[0]
                    source_name = parts[1]
                
                # --- FILTER 1: Source Quality Check ---
                tier, multiplier = self._get_source_rank(source_name)
                if tier == -1: continue
                    
                # --- FILTER 2: Content Type Check ---
                if any(x in clean_title for x in self.NOISE_TITLES): continue

                # ID for deduplication
                news_id = getattr(entry, 'id', link)

                if news_id in self.processed_ids: continue

                # SimHash Dedupe
                text_content = f"{clean_title}. {entry.get('summary', '')}"
                # Remove HTML from summary if present
                text_content = re.sub(r'<[^>]+>', '', text_content)
                
                current_hash = self._get_simhash(text_content)
                is_duplicate = False
                for existing_hash_str, _ in self.processed_hashes.items():
                    from simhash import Simhash
                    existing_hash = Simhash(int(existing_hash_str))
                    if current_hash.distance(existing_hash) < 3:
                        is_duplicate = True
                        break
                
                if is_duplicate: continue
                
                self._save_state(news_id, str(current_hash.value))
                
                # Handle Timestamps (RSS provides structured parsed time)
                timestamp = entry.get('published_parsed')
                if not timestamp:
                    # Fallback to parsing string
                    parsed = dateparser.parse(entry.get('published', ''))
                    timestamp = parsed.timetuple() if parsed else time.gmtime()

                new_items.append({
                    "source": f"Google News ({source_name})",
                    "author": source_name,
                    "timestamp": timestamp,
                    "content": text_content,
                    "url": link,
                    "id": news_id,
                    "title": clean_title,
                    "source_tier": tier,
                    "urgency_multiplier": multiplier
                })
            
            logger.info(f"Parsed {len(new_items)} items from RSS.")
            return new_items
            
        except Exception as e:
            logger.error(f"Failed to fetch Google News RSS: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _load_state(self):
        if os.path.exists(settings.STATE_FILE):
            try:
                with open(settings.STATE_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.processed_ids = set(data)
                        self.processed_hashes = {}
                    else:
                        self.processed_ids = set(data.get('ids', []))
                        self.processed_hashes = data.get('hashes', {})
            except: pass
        else:
             self.processed_ids = set()
             self.processed_hashes = {}

    def _save_state(self, new_id, new_hash_val):
        self.processed_ids.add(new_id)
        if len(self.processed_ids) > 1000:
             self.processed_ids = set(list(self.processed_ids)[-1000:])
        self.processed_hashes[new_hash_val] = time.time()
        if len(self.processed_hashes) > 1000:
            sorted_hashes = sorted(self.processed_hashes.items(), key=lambda item: item[1])
            self.processed_hashes = dict(sorted_hashes[-1000:])
        with open(settings.STATE_FILE, 'w') as f:
            json.dump({
                'ids': list(self.processed_ids),
                'hashes': self.processed_hashes
            }, f)