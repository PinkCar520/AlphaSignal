import psycopg2
from datetime import datetime, timedelta
import json
import sys
import yfinance as yf
import pandas as pd

# Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "alphasignal_core",
    "user": "alphasignal",
    "password": "secure_password"
}

INITIAL_CAPITAL = 10000.0

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

def get_daily_open_prices(start_date_str, end_date_str):
    """
    Fetch daily Open prices for GC=F to calculate daily market change.
    Returns: dict { 'YYYY-MM-DD': open_price }
    """
    print(f"Fetching daily market data for {start_date_str} to {end_date_str}...")
    try:
        # Buffer dates to ensure coverage
        start_dt = datetime.strptime(start_date_str, '%Y-%m-%d') - timedelta(days=5)
        end_dt = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=5)
        
        ticker = yf.Ticker("GC=F")
        df = ticker.history(start=start_dt.strftime('%Y-%m-%d'), end=end_dt.strftime('%Y-%m-%d'), interval="1d")
        
        price_map = {}
        for idx, row in df.iterrows():
            date_str = idx.strftime('%Y-%m-%d')
            price_map[date_str] = row['Open']
            
        return price_map
    except Exception as e:
        print(f"Warning: Failed to fetch market data: {e}")
        return {}

def parse_sentiment(sentiment_json, score):
    """
    Determine trade direction based on sentiment text.
    Returns: 'Long', 'Short', or 'Neutral'
    """
    try:
        if isinstance(sentiment_json, str):
            # Try to parse stringified JSON
            try:
                data = json.loads(sentiment_json.replace("'", '"')) # Simple fix for single quotes
            except:
                data = {'en': sentiment_json}
        else:
            data = sentiment_json
            
        text = str(data.get('en', '')).lower()
        
        if 'bullish' in text or 'safe-haven' in text or 'positive' in text or 'upward' in text:
            return 'Long'
        if 'bearish' in text or 'negative' in text or 'downward' in text or 'pressure' in text:
            return 'Short'
            
        # Fallback to score if text is ambiguous but score is strong (if score logic was known)
        # For now, default to Neutral
        return 'Neutral'
    except:
        return 'Neutral'

def main():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query data for Jan 2026
    start_date = '2026-01-01'
    end_date = '2026-02-01'
    
    query = f"""
        SELECT 
            id, 
            timestamp, 
            sentiment, 
            sentiment_score, 
            gold_price_snapshot, 
            price_1h,
            price_24h
        FROM intelligence 
        WHERE timestamp >= '{start_date}' AND timestamp < '{end_date}'
        ORDER BY timestamp ASC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Fetch Market Data
    daily_opens = get_daily_open_prices(start_date, end_date)
    
    print(f"{'序号':<4} | {'交易方向':<8} | {'时间 (UTC)':<18} | {'持仓成本价':<10} | {'平仓价格':<10} | {'持有金额($)':<12} | {'日涨跌幅(%)':<12} | {'累计总收益率(%)':<14} | {'当日收益($)':<12} | {'AI情绪分':<8} | {'结果':<6}")
    print("-" * 160)
    
    total_return_pct = 0.0
    total_pnl_amount = 0.0
    valid_trades = 0
    winning_trades = 0
    
    current_capital = INITIAL_CAPITAL
    day_start_capital = INITIAL_CAPITAL
    current_day = None
    
    open_positions = [] 

    last_trade_exit_time = None
    last_trade_direction = None
    
    display_index = 0 # New variable for correct serial numbering

    for i, row in enumerate(rows, 1):
        rid, timestamp, sentiment, score, entry_price, exit_price_1h, exit_price_24h = row
        
        # Determine Direction
        direction = parse_sentiment(sentiment, score)
        dir_cn = "做多" if direction == 'Long' else "做空" if direction == 'Short' else "中性"

        if direction == 'Neutral':
            continue
            
        # Parse timestamp to datetime object for comparison
        if isinstance(timestamp, str):
            try:
                # Handle potential timezone offsets in string if present, or naive
                if "+" in timestamp:
                    ts_dt = datetime.strptime(timestamp.split("+")[0], "%Y-%m-%d %H:%M:%S.%f") # rough fix
                else:
                    ts_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except:
                # Fallback for simple format
                ts_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            ts_str = timestamp
        else:
            ts_dt = timestamp
            ts_str = timestamp.strftime('%Y-%m-%d %H:%M')

        # --- DEDUPLICATION LOGIC (Active Trade Filter) ---
        # If we have an active trade (current time < last exit time) AND direction is same, SKIP.
        if last_trade_exit_time and ts_dt < last_trade_exit_time:
            if direction == last_trade_direction:
                continue # Skip duplicate signal during active trade
        # -------------------------------------------------

        if not entry_price:
            continue

        entry_price = float(entry_price)
        
        trade_day = ts_dt.strftime('%Y-%m-%d')
        
        # New Day Logic
        if current_day != trade_day:
            day_start_capital = current_capital
            current_day = trade_day

        # Check if trade is closed
        if not exit_price_1h:
            open_positions.append({
                'id': rid,
                'direction': dir_cn,
                'time': ts_str,
                'cost': entry_price,
                'score': score
            })
            # Even if open, mark as active for deduplication? 
            # Assume standard 1h duration for deduplication purposes
            last_trade_exit_time = ts_dt + timedelta(hours=1)
            last_trade_direction = direction
            continue
            
        # Calculate Return
        exit_price = float(exit_price_1h)
        trade_capital = current_capital 
        
        # Market Change
        daily_open = daily_opens.get(trade_day)
        if daily_open:
            market_change_pct = (exit_price - daily_open) / daily_open * 100
        else:
            market_change_pct = (exit_price - entry_price) / entry_price * 100

        # Strategy Return
        if direction == 'Long':
            ret = (exit_price - entry_price) / entry_price
        else: # Short
            ret = (entry_price - exit_price) / entry_price
            
        ret_pct = ret * 100
        pnl_amt = trade_capital * ret
        
        # Update Stats
        total_return_pct += ret_pct
        total_pnl_amount += pnl_amt
        current_capital += pnl_amt 
        valid_trades += 1
        
        # Update Deduplication State
        last_trade_exit_time = ts_dt + timedelta(hours=1)
        last_trade_direction = direction

        # Calculate Cumulative Return
        cum_ret_pct = (current_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
        
        # Calculate Daily PnL Amount
        daily_pnl = current_capital - day_start_capital
        
        result_str = "盈利" if ret > 0 else "亏损"
        if ret > 0: winning_trades += 1
        
        # AI Score display
        score_display = f"{score:.2f}" if score is not None else "N/A"
        
        display_index += 1 # Increment only when a trade is about to be displayed
        print(f"{display_index:<4} | {dir_cn:<8} | {ts_str:<18} | {entry_price:<10.2f} | {exit_price:<10.2f} | {trade_capital:<12.2f} | {f'{market_change_pct:.2f}%':<12} | {f'{cum_ret_pct:.2f}%':<14} | {daily_pnl:<12.2f} | {score_display:<8} | {result_str:<6}")

    print("-" * 120)
    print(f"【2026年1月 交易月报】")
    print(f"1. 交易统计:")
    print(f"   - 总交易次数: {valid_trades}")
    if valid_trades > 0:
        print(f"   - 胜率: {(winning_trades/valid_trades)*100:.1f}%")
        print(f"   - 平均单笔收益: {total_return_pct/valid_trades:.2f}%")
    
    monthly_return_amt = current_capital - INITIAL_CAPITAL
    monthly_return_pct = (monthly_return_amt / INITIAL_CAPITAL) * 100
    
    print(f"\n2. 资金表现 (关键因素):")
    print(f"   - 初始本金: ${INITIAL_CAPITAL:.2f}")
    print(f"   - 期末权益: ${current_capital:.2f}")
    print(f"   - 月收益金额: ${monthly_return_amt:.2f} (Profit)")
    print(f"   - 月收益率: {monthly_return_pct:.2f}%")

    print(f"\n3. 当前持仓 (截至月底):")
    if open_positions:
        print(f"   警告: 发现 {len(open_positions)} 笔未平仓/数据缺失交易:")
        for op in open_positions[:5]: # Show max 5
            print(f"   - [{op['time']}] {op['direction']} @ {op['cost']:.2f} (AI分: {op['score']})")
        if len(open_positions) > 5: print(f"   ... 等共 {len(open_positions)} 笔")
    else:
        print(f"   - 无持仓 (所有交易已结清)")


if __name__ == "__main__":
    main()