import psycopg2
from datetime import datetime, timedelta
import json
import sys

# Configuration - Assuming the same as generate_monthly_report.py
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "alphasignal_core",
    "user": "alphasignal",
    "password": "secure_password"
}

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

def fetch_intelligence_data(start_date_str, end_date_str):
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT 
            id, 
            timestamp, 
            author,
            url,
            content,
            summary,
            sentiment, 
            sentiment_score,
            urgency_score,
            gold_price_snapshot, 
            price_1h,
            price_24h
        FROM intelligence 
        WHERE timestamp >= '{start_date_str}' AND timestamp < '{end_date_str}'
        ORDER BY timestamp ASC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Get column names from cursor description
    col_names = [desc[0] for desc in cursor.description]

    conn.close()
    return [dict(zip(col_names, row)) for row in rows]

def main():
    start_date = '2026-02-01'
    end_date = '2026-02-03' # Fetch up to but not including Feb 3rd to get all of Feb 1st and 2nd

    print(f"Fetching intelligence data from {start_date} to {end_date}...")
    
    intelligence_data = fetch_intelligence_data(start_date, end_date)

    if not intelligence_data:
        print("No intelligence data found for the specified period.")
        return

    print(f"\n--- Intelligence Data ({len(intelligence_data)} records) ---")
    for item in intelligence_data:
        print(f"ID: {item.get('id')}")
        print(f"Timestamp: {item.get('timestamp')}")
        print(f"Author (Source): {item.get('author')}")
        print(f"URL: {item.get('url')}")
        
        # Display sentiment from JSONB and the score
        sentiment_json = item.get('sentiment')
        sentiment_display = sentiment_json.get('en') if isinstance(sentiment_json, dict) and sentiment_json.get('en') else str(sentiment_json)
        print(f"Sentiment: {sentiment_display}")
        print(f"Sentiment Score: {item.get('sentiment_score')}")
        print(f"Urgency Score: {item.get('urgency_score')}")

        # Truncate content and summary for display to avoid overwhelming output
        content = item.get('content', '')
        summary_json = item.get('summary')
        summary_display = summary_json.get('en') if isinstance(summary_json, dict) and summary_json.get('en') else str(summary_json)

        print(f"Summary (first 100 chars): {summary_display[:100]}...")
        print(f"Content (first 200 chars): {content[:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    main()
