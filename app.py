import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Kripto Sinyal Paneli", layout="wide")
st.title("📊 Kripto Sinyal Paneli – AI + Teknik + Fiyat + Telegram")

TELEGRAM_TOKEN = "7757372996:AAGOzECzHvllRSWBZ_1h-JTmU4i58yMrDBA"
CHAT_ID = "694298537"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except:
        pass

def get_price(coin_id, vs_currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get(coin_id, {}).get(vs_currency, 0)
    return 0

def get_history(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    r = requests.get(url)
    if r.status_code == 200:
        prices = r.json().get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    return pd.DataFrame()



coins = {
    "pepe": "PEPE",
    "floki": "FLOKI",
    "dogecoin": "DOGE",
    "zk-token": "ZK",
    "ripple": "XRP",
    "wifi": "WIF"
}

coin_id = st.selectbox("Coin Seç", list(coins.keys()))
fetch_prices = st.checkbox("Canlı fiyat verisi (CoinGecko)", value=True)

if fetch_prices:
    price = get_price(coin_id)
    st.metric("Şu anki fiyat", f"${price}")
    df_day = get_history(coin_id, 1)
    df_week = get_history(coin_id, 7)
    if not df_day.empty:
        st.line_chart(df_day.set_index("timestamp"))
    if not df_week.empty:
        st.area_chart(df_week.set_index("timestamp"))
    open_price = df_day["price"].iloc[0]
    close_price = df_day["price"].iloc[-1]
else:
    open_price = st.number_input("Açılış", min_value=0.0)
    close_price = st.number_input("Kapanış", min_value=0.0)

rsi = st.slider("RSI", 0, 100, 50)
macd = st.number_input("MACD")
ao = st.number_input("Awesome Oscillator")
wt = st.number_input("WaveTrend")
supertrend = st.selectbox("Supertrend", ["Buy", "Sell", "None"])
chandelier = st.selectbox("Chandelier Exit", ["Buy", "Sell", "None"])

signal = "BEKLE"
if rsi < 30 and macd > 0 and ao > 0 and supertrend == "Buy":
    signal = "AL"
elif rsi > 70 and macd < 0 and ao < 0 and chandelier == "Sell":
    signal = "SAT"

st.subheader(f"📍 Sinyal: {signal}")
note = st.text_area("Notlar")

if st.button("Telegram'a Gönder"):
    message = f"{coins[coin_id]} SINYAL: {signal}\nRSI: {rsi} | MACD: {macd}\nAO: {ao} | WT: {wt}\nSupertrend: {supertrend} | Chandelier: {chandelier}\nAçılış: {open_price} Kapanış: {close_price}"
    send_telegram(message)
    st.success("📨 Telegram’a gönderildi.")
