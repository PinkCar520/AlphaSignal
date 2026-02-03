#!/usr/bin/env python3
"""
Historical Data Import Script - Final Linear Pipeline
1. Monthly Fetch -> 2. Batch AI -> 3. Price Backfill -> 4. Save to DB
"""
import sys
import os
from datetime import datetime, timedelta
import time
import pytz
import json
import random
import yfinance as yf
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.alphasignal.config import settings
from src.alphasignal.core.logger import logger
from src.alphasignal.providers.data_sources.google_news import GoogleNewsSource
from src.alphasignal.providers.llm.gemini import GeminiLLM
from src.alphasignal.providers.llm.deepseek import DeepSeekLLM
from src.alphasignal.core.database import IntelligenceDB

class TrumpHistoryImporter:
    def __init__(self):
        self.db = IntelligenceDB()
        self.primary_llm = GeminiLLM()
        self.fallback_llm = DeepSeekLLM()
        self.google_news_source = GoogleNewsSource()
        self.progress_file = "data/import_progress.json"
        self.price_cache = {}
        self.load_progress()
    
    def load_progress(self):
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    self.progress = json.load(f)
                    logger.info(f"📂 Progress loaded: Last processed month ending {self.progress.get('last_date', 'N/A')}")
            else:
                self.progress = {"last_date": None, "total_processed": 0, "total_success": 0}
        except Exception:
            self.progress = {"last_date": None, "total_processed": 0, "total_success": 0}
    
    def save_progress(self, current_date, processed_inc=0, success_inc=0):
        try:
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            self.progress["last_date"] = current_date.strftime('%Y-%m-%d')
            self.progress["total_processed"] += processed_inc
            self.progress["total_success"] += success_inc
            self.progress["last_updated"] = datetime.now().isoformat()
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception: pass

    def get_price_data_for_month(self, start_date, end_date):
        """Pre-fetch all needed assets for the month to reduce yfinance calls"""
        assets = {"gold": "GC=F", "dxy": "DX-Y.NYB", "us10y": "^TNX", "gvz": "^GVZ"}
        data = {}
        fetch_start = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
        fetch_end = (end_date + timedelta(days=7)).strftime('%Y-%m-%d')
        
        for name, ticker_symbol in assets.items():
            try:
                logger.info(f"💰 Fetching {name} ({ticker_symbol}) for the month...")
                ticker = yf.Ticker(ticker_symbol)
                df = ticker.history(start=fetch_start, end=fetch_end, interval="1h")
                if not df.empty:
                    df.index = df.index.tz_localize('UTC') if df.index.tz is None else df.index.tz_convert('UTC')
                    data[name] = df
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to fetch {name}: {e}")
        return data

    def get_prices_at_time(self, timestamp, month_data):
        """Extract prices from pre-fetched month data"""
        try:
            if isinstance(timestamp, str): dt = date_parser.parse(timestamp)
            else: dt = timestamp
            if dt.tzinfo is None: dt = pytz.utc.localize(dt)
            else: dt = dt.astimezone(pytz.utc)

            price_df = month_data.get("gold")
            if price_df is None or price_df.empty: return None, None, None, None
            
            idx = price_df.index.searchsorted(dt)
            if idx >= len(price_df): return None, None, None, None
            snapshot_time = price_df.index[idx]
            
            # 4-day gap safety
            if (snapshot_time - dt).total_seconds() > 4 * 86400: return None, None, None, None

            def get_val(name, t_point):
                df = month_data.get(name)
                if df is None or df.empty: return None
                i = df.index.searchsorted(t_point)
                if i < len(df): return float(df.iloc[i]['Close'])
                return None

            return float(price_df.iloc[idx]['Close']), get_val("dxy", snapshot_time), get_val("us10y", snapshot_time), get_val("gvz", snapshot_time)
        except Exception: return None, None, None, None

    def run(self, start_date_str="2025-05-01", end_date_str=None, batch_size=10):
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
        
        current_date = start_date
        logger.info(f"🚀 Starting Linear Pipeline Importer: {start_date_str}")

        while current_date < end_date:
            month_end = min(current_date + relativedelta(months=1) - timedelta(days=1), end_date)
            logger.info(f"\n--- 📅 Processing Month: {current_date.strftime('%Y-%m')} ---")
            
            try:
                # STEP 1: Fetch all news for the month
                logger.info(f"1️⃣ Fetching news from {current_date.date()} to {month_end.date()}...")
                news_items = self.google_news_source.fetch(
                    query="Donald Trump (Truth Social OR Economy OR Tariff OR Fed OR Gold)",
                    start_date=current_date.strftime('%m/%d/%Y'),
                    end_date=month_end.strftime('%m/%d/%Y')
                )
                
                if not news_items:
                    logger.info("⏭️ No news found. Skipping.")
                    current_date = month_end + timedelta(days=1)
                    continue

                logger.info(f"✅ Found {len(news_items)} total items.")

                # STEP 2 & 3: Pre-fetch Market Data
                logger.info("2️⃣ Pre-fetching market data for price matching...")
                month_price_data = self.get_price_data_for_month(current_date, month_end)

                # STEP 4: Batch AI & Save
                logger.info("3️⃣ Starting Batch AI Analysis & Saving...")
                total_month_success = 0
                
                for i in range(0, len(news_items), batch_size):
                    chunk = news_items[i:i+batch_size]
                    logger.info(f"  📦 Batch [{i//batch_size + 1}/{(len(news_items)+batch_size-1)//batch_size}] ({len(chunk)} items)")
                    
                    # AI Analysis
                    analysis_results = None
                    try:
                        analysis_results = self.primary_llm.analyze_batch(chunk)
                    except Exception:
                        try: analysis_results = self.fallback_llm.analyze_batch(chunk)
                        except Exception: logger.error("    ❌ AI Batch Failed.")

                    if not analysis_results: continue

                    # Process results and Save
                    batch_success = 0
                    for j, news_item in enumerate(chunk):
                        try:
                            analysis = analysis_results[j] if j < len(analysis_results) else None
                            if not analysis: continue

                            # Match Prices
                            gold, dxy, us10y, gvz = self.get_prices_at_time(news_item['timestamp'], month_price_data)
                            
                            analysis['original_content'] = news_item['content']
                            analysis['url'] = news_item['url']
                            news_item['dxy_snapshot'] = dxy
                            news_item['us10y_snapshot'] = us10y
                            news_item['gvz_snapshot'] = gvz
                            
                            self.db.save_intelligence(news_item, analysis, gold_price_snapshot=gold)
                            batch_success += 1
                        except Exception as e:
                            logger.error(f"    ❌ Save Item Error: {e}")
                    
                    total_month_success += batch_success
                    self.save_progress(month_end, len(chunk), batch_success)
                    time.sleep(random.randint(3, 6)) # Cooldown

                logger.info(f"🏁 Month Complete. Total Saved: {total_month_success}")

            except Exception as e:
                logger.error(f"💥 Month {current_date.strftime('%Y-%m')} Failed: {e}")
                time.sleep(30)

            current_date = month_end + timedelta(days=1)
            time.sleep(5)

if __name__ == "__main__":
    importer = TrumpHistoryImporter()
    start = sys.argv[1] if len(sys.argv) > 1 else "2025-05-01"
    importer.run(start)
