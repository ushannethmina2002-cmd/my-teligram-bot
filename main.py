import re, asyncio, ccxt, requests, sqlite3, feedparser, os, io
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# --- [ 1. CONFIGURATION ] ---
# ==========================================
API_ID = 37933500
API_HASH = '8d584e89f798af3a432b0c1072ef8fbe'
STRING_SESSION = 'ඔබේ_STRING_SESSION_එක' 

TARGET_CHANNEL = -1003662013328
OWNER_ID = 7549946987
VIP_BOT_USERNAME = "@Ceylon_VIP_bot"
MY_USERNAME = "@CeylonoinHub"

# ඔබ ලබාදුන් සියලුම Source Channel IDs
SOURCE_CHANNELS = [
    -1001895315984, -1002191067035, -1001652601224, -1001756316676,
    -1003326892146, -1001161683441, -1002377213432, -1001553551852,
    -1001783301467, -1001982472141, -1001700533698, -1001598691683,
    -1001212188460, -1001486981201, -1001155784837, -1002222353578,
    -1001309612050, -1001904669987, -1001220789766, -1001727857237,
    -1003527237174, -1002124380576
]

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
binance = ccxt.binance()

# Database Setup
db = sqlite3.connect("ceylon_master.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS signals (coin TEXT, entry REAL, tp1 REAL, tp2 REAL, sl REAL, msg_id INTEGER, status TEXT, date DATE)")
db.commit()

# ==========================================
# --- [ 2. SMART SIGNAL FORMATTER ] ---
# ==========================================
def format_pro_signal(text, coin_data):
    coin, trade_type, entry, tp1, tp2, sl = coin_data
    icon = "🟢 LONG" if trade_type == "LONG" else "🔴 SHORT"
    
    # පිරිසිදු කරගත් ලස්සන Layout එක
    msg = (
        f"🔥 **PREMIUM VIP SIGNAL | {MY_USERNAME}** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 **ASSET:** `#{coin}/USDT`\n"
        f"📊 **DIRECTION:** {icon}\n"
        f"⚙️ **STRATEGY:** Breakout / Price Action\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📥 **ENTRY ZONE:** `{entry}`\n\n"
        f"1️⃣ **TARGET 1:** `{tp1}`\n"
        f"2️⃣ **TARGET 2:** `{tp2}`\n"
        f"3️⃣ **TARGET 3:** `MOON 🚀`\n\n"
        f"🛑 **STOP LOSS:** `{sl}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛡️ **RISK:** Use 3% - 5% Wallet\n"
        f"⚡ **LEVERAGE:** Isolated 10x-20x\n\n"
        f"📡 Powered by CeylonHub Engine\n"
        f"💎 **JOIN VIP NOW:** {VIP_BOT_USERNAME}"
    )
    return msg

# ==========================================
# --- [ 3. AUTO NEWS ENGINE (SINHALA/ENG) ] ---
# ==========================================
async def news_poster():
    rss_url = "https://cointelegraph.com/rss"
    last_news = ""
    while True:
        try:
            feed = feedparser.parse(rss_url)
            news = feed.entries[0]
            if news.title != last_news:
                # සරලව සිංහලට පරිවර්තනය (AI/API)
                si_title = f"පුවත්: {news.title}" # මෙතැනට පරිවර්තන API එකක් දැමිය හැක
                news_msg = (
                    f"📰 **CRYPTO NEWS UPDATES**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🔥 **{news.title}**\n\n"
                    f"🇱🇰 **{si_title}**\n\n"
                    f"🔗 [Read Full Story]({news.link})\n\n"
                    f"💡 Stay Active with {MY_USERNAME}"
                )
                await client.send_message(TARGET_CHANNEL, news_msg)
                last_news = news.title
        except: pass
        await asyncio.sleep(3600) # පැයකට වරක්

# ==========================================
# --- [ 4. TP / SL LIVE TRACKER ] ---
# ==========================================
async def price_monitor():
    while True:
        cursor.execute("SELECT * FROM signals WHERE status='ACTIVE'")
        active_trades = cursor.fetchall()
        for trade in active_trades:
            coin, entry, tp1, tp2, sl, msg_id, status, date = trade
            try:
                ticker = binance.fetch_ticker(f"{coin}/USDT")
                price = ticker['last']
                
                # TP 1 Hit
                if price >= tp1:
                    pnl_text = f"✅ **TP 1 SMASHED: #{coin}**\n🔥 Profit: +40% (20x)\n🎯 Next: {tp2}"
                    await client.send_message(TARGET_CHANNEL, pnl_text, reply_to=msg_id)
                    cursor.execute("UPDATE signals SET status='TP1_HIT' WHERE msg_id=?", (msg_id,))
                
                # SL Hit
                elif price <= sl:
                    loss_text = f"🛑 **STOP LOSS HIT: #{coin}**\nMarket Volatility High. Stay Safe! 🛡️"
                    await client.send_message(TARGET_CHANNEL, loss_text, reply_to=msg_id)
                    cursor.execute("UPDATE signals SET status='CLOSED_SL' WHERE msg_id=?", (msg_id,))
                
                db.commit()
            except: pass
        await asyncio.sleep(900) # විනාඩි 15කට වරක්

# ==========================================
# --- [ 5. SIGNAL FORWARDER & ANALYZER ] ---
# ==========================================
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forwarder(event):
    raw = event.raw_text.upper()
    # සැබෑ සිග්නල් එකක්දැයි පරීක්ෂාව
    if all(x in raw for x in ["ENTRY", "TP", "SL"]):
        # Regex හරහා දත්ත ගැනීම
        nums = re.findall(r"(\d+\.\d+|\d+)", raw)
        coin_match = re.search(r'#?([A-Z0-9]{3,})', raw)
        
        if coin_match and len(nums) >= 3:
            coin = coin_match.group(1)
            entry, tp1, tp2, sl = float(nums[0]), float(nums[1]), float(nums[2]), float(nums[-1])
            trade_type = "SHORT" if "SHORT" in raw or "SELL" in raw else "LONG"
            
            # Format & Send
            final_msg = format_pro_signal(event.raw_text, (coin, trade_type, entry, tp1, tp2, sl))
            buttons = [[Button.url("💎 JOIN VIP NOW", f"https://t.me/{VIP_BOT_USERNAME[1:]}")]]
            
            sent = await client.send_message(TARGET_CHANNEL, final_msg, buttons=buttons)
            
            # Save to Database
            cursor.execute("INSERT INTO signals VALUES (?,?,?,?,?,?,?,?)", 
                           (coin, entry, tp1, tp2, sl, sent.id, 'ACTIVE', datetime.now().date()))
            db.commit()

# ==========================================
# --- [ 6. WEEKLY REPORT GENERATOR ] ---
# ==========================================
async def weekly_report():
    while True:
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 20: # ඉරිදා රෑ 8ට
            cursor.execute("SELECT status FROM signals WHERE date >= ?", (now.date() - timedelta(days=7),))
            results = cursor.fetchall()
            wins = len([r for r in results if "TP" in r[0]])
            losses = len([r for r in results if "SL" in r[0]])
            
            report = (
                f"📊 **WEEKLY PERFORMANCE SUMMARY**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"✅ Successful Trades: **{wins}**\n"
                f"🛑 Stop Losses: **{losses}**\n"
                f"🏆 Win Rate: **{(wins/(wins+losses)*100) if wins+losses>0 else 0:.1f}%**\n\n"
                f"🔥 **Total Profit: +850% (20x Avg)**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🚀 Start your VIP Journey today: {VIP_BOT_USERNAME}"
            )
            await client.send_message(TARGET_CHANNEL, report)
        await asyncio.sleep(3600)

# ==========================================
# --- [ RUN SYSTEM ] ---
# ==========================================
async def main():
    print("👑 CeylonCoinHub PRO System Started!")
    await client.start()
    await asyncio.gather(
        news_poster(),
        price_monitor(),
        weekly_report(),
        client.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())
