import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Sayfa başlığı ve düzen
st.set_page_config(page_title="Kripto Sinyal Paneli", layout="wide")

# Telegram Ayarları
TELEGRAM_TOKEN = "7757372996:AAGOzECzHvllRSWBZ_1h-JTmU4i58yMrDBA"
CHAT_ID = "694298537"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Telegram mesajı gönderilemedi: {e}")

def get_price(coin_id, vs_currency="usd"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get(coin_id, {}).get(vs_currency, 0)
    except Exception as e:
        st.error(f"Fiyat alınamadı: {e}")
    return 0

def get_history(coin_id, days):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        r = requests.get(url)
        if r.status_code == 200:
            prices = r.json().get("prices", [])
            if prices:
                df = pd.DataFrame(prices, columns=["timestamp", "price"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
    except Exception as e:
        st.error(f"Veri alınamadı: {e}")
    return pd.DataFrame()

# Uygulama başlığı
st.title("📊 Kripto Sinyal Paneli – AI + Teknik + Telegram")

coins = {
    "pepe": "PEPE",
    "floki": "FLOKI",
    "dogecoin": "DOGE",
    "zk-token": "ZK",
    "ripple": "XRP",
    "wifi": "WIF"
}

coin_id = st.selectbox("Coin Seç", list(coins.keys()))
fetch_prices = st.checkbox("CoinGecko'dan fiyat verisi çek", value=True)

# Fiyat Verisi
if fetch_prices:
    price = get_price(coin_id)
    st.metric("🔹 Şu anki fiyat", f"${price}")
    df_day = get_history(coin_id, 1)
    df_week = get_history(coin_id, 7)

    if not df_day.empty:
        st.line_chart(df_day.set_index("timestamp"))
        open_price = df_day["price"].iloc[0]
        close_price = df_day["price"].iloc[-1]
    else:
        st.warning("📉 Günlük veri alınamadı.")
        open_price = 0
        close_price = 0

    if not df_week.empty:
        st.area_chart(df_week.set_index("timestamp"))
    else:
        st.warning("📉 Haftalık veri alınamadı.")
else:
    open_price = st.number_input("Açılış Fiyatı", min_value=0.0)
    close_price = st.number_input("Kapanış Fiyatı", min_value=0.0)

# Teknik Göstergeler
rsi = st.slider("RSI", 0, 100, 50)
macd = st.number_input("MACD")
ao = st.number_input("Awesome Oscillator")
wt = st.number_input("WaveTrend")
supertrend = st.selectbox("Supertrend", ["Buy", "Sell", "None"])
chandelier = st.selectbox("Chandelier Exit", ["Buy", "Sell", "None"])

# Sinyal Mantığı
signal = "BEKLE"
explanation = ""
strategy = ""

if rsi < 30 and macd > 0 and ao > 0 and supertrend == "Buy":
    signal = "AL"
    explanation = "RSI düşük, MACD ve AO pozitif. Supertrend Buy."
    strategy = "Yükseliş teyitli. Giriş fırsatı olabilir."
elif rsi > 70 and macd < 0 and ao < 0 and chandelier == "Sell":
    signal = "SAT"
    explanation = "RSI yüksek, MACD ve AO negatif. Chandelier Sell."
    strategy = "Düşüş riski. Kâr alımı yapılabilir."
else:
    explanation = "Kararsız görünüm. Net sinyal yok."
    strategy = "Beklemede kalmak mantıklı."

change_pct = ((close_price - open_price) / open_price * 100) if open_price else 0
st.metric("📊 Günlük % Değişim", f"{change_pct:.2f}%")

# Sinyal ve Notlar
st.subheader(f"📍 Sinyal: {signal}")
st.info(f"🧠 AI Açıklama: {explanation}")
st.success(f"🎯 Strateji: {strategy}")

note = st.text_area("🗒️ Notlar")

# Telegram Gönderimi
if st.button("📨 Telegram'a Gönder"):
    message = f"""
📌 {coins[coin_id]} SINYALİ: {signal}
📈 Açılış: ${open_price:.4f}
📉 Kapanış: ${close_price:.4f}
🔁 Değişim: {change_pct:.2f}%
🧠 Açıklama: {explanation}
🎯 Strateji: {strategy}
📒 Not: {note}
"""
    send_telegram(message)
    st.success("Telegram’a gönderildi ✅")
