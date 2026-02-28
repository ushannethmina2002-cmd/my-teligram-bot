import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import ccxt

# --- CONFIGURATION ---
api_id = 37933500
api_hash = '8d584e89f798af3a432b0c1072ef8fbe'
string_session = 'ඔබේ_STRING_SESSION_එක_මෙහි_යොදන්න' # මුලින් අංකය දී ලබාගන්නා string එක
target_channel = -1003662013328
my_username = "@CeylonoinHub"
vip_bot_link = "@Ceylon_VIP_bot"

client = TelegramClient(StringSession(string_session), api_id, api_hash)

# --- SIGNAL DETECTOR & FORMATTER ---
def format_signal(text):
    # වෙනත් අයගේ links/usernames ඉවත් කිරීම
    clean_text = re.sub(r'@\w+', '', text)
    clean_text = re.sub(r'http\S+', '', clean_text)
    
    # Signal එකක්දැයි හඳුනාගැනීම (Entry, TP, SL තිබේදැයි බැලීම)
    if "ENTRY" in text.upper() and "TP" in text.upper():
        formatted_msg = (
            f"🚀 **NEW PREMIUM SIGNAL** 🚀\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"{clean_text.strip()}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🛡 **Risk Warning:** Trade with 1-3% of your wallet.\n"
            f"🔗 **Join VIP Now:** {vip_bot_link}\n"
            f"📡 **Power by:** {my_username}"
        )
        return formatted_msg
    return None

# --- MESSAGE HANDLER ---
@client.on(events.NewMessage(chats=[
    -1001895315984, -1002191067035, -1001652601224, # අනෙකුත් සියලුම ID මෙහි දාන්න
]))
async def handler(event):
    message_text = event.raw_text
    new_signal = format_signal(message_text)
    
    if new_signal:
        await client.send_message(target_channel, new_signal)
        # මෙහිදී Live Tracking ආරම්භ කරන Function එකට දත්ත යවන්න

# --- MAIN RUN ---
print("Bot is Starting...")
client.start()
client.run_until_disconnected()
