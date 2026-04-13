#!/usr/bin/env python3
"""
NEPSE Stock Alert Agent
Monitors NEPSE stocks and sends alerts when prices hit your buy/SL/target levels
Supports: Telegram, Gmail, Discord
"""

import requests
import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============================================================================
# CONFIGURATION
# ============================================================================

# Alert state file (tracks what alerts we already sent)
STATE_FILE = "alert_state.json"

# Notification channels
NOTIFY_TELEGRAM = os.getenv("TELEGRAM_BOT_TOKEN") is not None
NOTIFY_GMAIL = os.getenv("GMAIL_APP_PASSWORD") is not None
NOTIFY_DISCORD = os.getenv("DISCORD_WEBHOOK_URL") is not None

# Get secrets from GitHub Actions secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
GMAIL_SENDER = os.getenv("GMAIL_SENDER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GMAIL_RECIPIENT = os.getenv("GMAIL_RECIPIENT", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")

# ============================================================================
# NEPSE PRICE FETCHING (Web Scraping)
# ============================================================================

def fetch_nepse_prices():
    """
    Scrape live NEPSE prices from NEPSE.COM.NP
    Returns dict: {"SYMBOL": {"price": 1234.5, "change": 12.3}, ...}
    """
    try:
        url = "https://www.nepse.com.np/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        prices = {}
        
        # NEPSE page structure: look for table rows with stock data
        # This is a best-effort parse; structure may change
        table_rows = soup.find_all("tr")
        
        for row in table_rows:
            cells = row.find_all("td")
            if len(cells) >= 4:
                try:
                    # Typical structure: Symbol | LTP | Change | %Change
                    symbol = cells[0].text.strip()
                    ltp = float(cells[1].text.strip().replace(",", ""))
                    change = float(cells[2].text.strip().replace(",", ""))
                    
                    if symbol and ltp > 0:
                        prices[symbol] = {"price": ltp, "change": change}
                except (ValueError, IndexError):
                    continue
        
        return prices if prices else None
        
    except Exception as e:
        print(f"❌ Error fetching NEPSE prices: {e}")
        return None


# ============================================================================
# GOOGLE SHEETS (Read Watchlist)
# ============================================================================

def read_google_sheet():
    """
    Read watchlist from Google Sheet
    Format: | Symbol | Buy Point | Sell Target | Stop Loss |
    Returns list of dicts
    """
    try:
        if not GOOGLE_SHEET_ID or not GOOGLE_CREDENTIALS_JSON:
            print("⚠️  Google Sheets not configured, skipping...")
            return []
        
        # Parse credentials JSON
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        records = sheet.get_all_records()
        
        watchlist = []
        for rec in records:
            if rec.get("Symbol"):
                watchlist.append({
                    "symbol": rec.get("Symbol", "").strip().upper(),
                    "buy_point": float(rec.get("Buy Point", 0) or 0),
                    "sell_target": float(rec.get("Sell Target", 0) or 0),
                    "stop_loss": float(rec.get("Stop Loss", 0) or 0),
                })
        
        return watchlist
        
    except Exception as e:
        print(f"⚠️  Error reading Google Sheet: {e}")
        return []


# ============================================================================
# ALERT STATE MANAGEMENT
# ============================================================================

def load_alert_state():
    """Load which alerts we already sent (avoid spam)"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️  Could not load alert state: {e}")
    return {}


def save_alert_state(state):
    """Save alert state so we don't resend"""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save alert state: {e}")


def has_alert_been_sent(state, symbol, alert_type, price):
    """
    Check if we already sent this alert
    alert_type: "buy" | "sell" | "stoploss"
    """
    key = f"{symbol}_{alert_type}"
    if key not in state:
        return False
    
    # If price changes by more than 2%, resend alert
    last_price = state[key].get("price", 0)
    price_diff_pct = abs(price - last_price) / last_price * 100 if last_price > 0 else 100
    
    return price_diff_pct < 2


def mark_alert_sent(state, symbol, alert_type, price):
    """Record that we sent this alert"""
    key = f"{symbol}_{alert_type}"
    state[key] = {"price": price, "timestamp": datetime.now().isoformat()}


# ============================================================================
# NOTIFICATIONS
# ============================================================================

def send_telegram_alert(message):
    """Send alert via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False


def send_gmail_alert(subject, body):
    """Send alert via Gmail"""
    if not GMAIL_SENDER or not GMAIL_PASSWORD or not GMAIL_RECIPIENT:
        return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = GMAIL_SENDER
        msg["To"] = GMAIL_RECIPIENT
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_SENDER, GMAIL_RECIPIENT, msg.as_string())
        
        return True
    except Exception as e:
        print(f"❌ Gmail error: {e}")
        return False


def send_discord_alert(message):
    """Send alert via Discord webhook"""
    if not DISCORD_WEBHOOK_URL:
        return False
    
    try:
        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"❌ Discord error: {e}")
        return False


def send_alerts(symbol, alert_type, price, target_price):
    """
    Send to all configured channels
    alert_type: "buy" | "sell" | "stoploss"
    """
    emoji = "🟢" if alert_type == "buy" else ("🔴" if alert_type == "stoploss" else "🟡")
    
    alert_msg = f"{emoji} <b>{symbol}</b> hit {alert_type.upper()}!\nPrice: {price}\nTarget: {target_price}"
    
    if NOTIFY_TELEGRAM:
        send_telegram_alert(alert_msg)
        print(f"✅ Telegram alert sent: {symbol}")
    
    if NOTIFY_GMAIL:
        send_gmail_alert(
            f"{symbol} - {alert_type.upper()} Alert",
            f"{symbol} just hit your {alert_type} level!\n\nPrice: {price}\nTarget: {target_price}"
        )
        print(f"✅ Gmail alert sent: {symbol}")
    
    if NOTIFY_DISCORD:
        send_discord_alert(f"{alert_msg}")
        print(f"✅ Discord alert sent: {symbol}")


# ============================================================================
# MAIN LOGIC
# ============================================================================

def check_alerts():
    """Main function: fetch prices, check targets, send alerts"""
    
    print(f"🚀 NEPSE Alert Check @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load state
    state = load_alert_state()
    
    # Fetch prices
    prices = fetch_nepse_prices()
    if not prices:
        print("❌ Could not fetch NEPSE prices")
        return
    
    print(f"✅ Fetched {len(prices)} stocks from NEPSE")
    
    # Read watchlist
    watchlist = read_google_sheet()
    if not watchlist:
        print("⚠️  No watchlist configured")
        return
    
    print(f"📋 Monitoring {len(watchlist)} stocks from watchlist")
    print("=" * 60)
    
    # Check each stock
    alerts_sent = 0
    
    for watch in watchlist:
        symbol = watch["symbol"]
        buy_point = watch["buy_point"]
        sell_target = watch["sell_target"]
        stop_loss = watch["stop_loss"]
        
        if symbol not in prices:
            print(f"⚠️  {symbol}: Not found in NEPSE data")
            continue
        
        current_price = prices[symbol]["price"]
        change = prices[symbol]["change"]
        
        print(f"\n📊 {symbol}: {current_price} ({change:+.2f})")
        
        # BUY ALERT
        if buy_point > 0 and current_price <= buy_point:
            if not has_alert_been_sent(state, symbol, "buy", current_price):
                send_alerts(symbol, "buy", current_price, buy_point)
                mark_alert_sent(state, symbol, "buy", current_price)
                alerts_sent += 1
            else:
                print(f"   ↪ Buy alert already sent (price unchanged)")
        
        # SELL ALERT
        if sell_target > 0 and current_price >= sell_target:
            if not has_alert_been_sent(state, symbol, "sell", current_price):
                send_alerts(symbol, "sell", current_price, sell_target)
                mark_alert_sent(state, symbol, "sell", current_price)
                alerts_sent += 1
            else:
                print(f"   ↪ Sell alert already sent (price unchanged)")
        
        # STOPLOSS ALERT
        if stop_loss > 0 and current_price <= stop_loss:
            if not has_alert_been_sent(state, symbol, "stoploss", current_price):
                send_alerts(symbol, "stoploss", current_price, stop_loss)
                mark_alert_sent(state, symbol, "stoploss", current_price)
                alerts_sent += 1
            else:
                print(f"   ↪ Stoploss alert already sent (price unchanged)")
    
    # Save state
    save_alert_state(state)
    
    print("\n" + "=" * 60)
    print(f"✅ Check complete. Alerts sent: {alerts_sent}")


if __name__ == "__main__":
    check_alerts()
