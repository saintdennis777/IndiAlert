import yfinance as yf
import pandas as pd
import requests
import time

# === CONFIGURATION ===
TICKER = "XAUUSD=X"
INTERVAL = "1m"
RSI_PERIOD = 13
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def calculate_rsi(data, period=13):
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_alert():
    df = yf.download(tickers=TICKER, interval=INTERVAL, period="2d", progress=False)
    df["RSI"] = calculate_rsi(df, RSI_PERIOD)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    rsi = latest["RSI"]
    prev_rsi = previous["RSI"]

    if pd.isna(rsi) or pd.isna(prev_rsi):
        return

    if prev_rsi <= RSI_OVERBOUGHT and rsi > RSI_OVERBOUGHT:
        send_telegram_message(f"📈 RSI Overbought Alert (XAUUSD)\nRSI: {rsi:.2f}")

    elif prev_rsi >= RSI_OVERSOLD and rsi < RSI_OVERSOLD:
        send_telegram_message(f"📉 RSI Oversold Alert (XAUUSD)\nRSI: {rsi:.2f}")

print("✅ RSI monitor started...")

while True:
    try:
        check_alert()
        time.sleep(60)
    except Exception as e:
        print("Error:", e)
        time.sleep(60)
