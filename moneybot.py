import asyncio
import requests
import re
from collections import deque
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive 

# ======================= CONFIGURATION ZONE ======================= #

# 1. TELEGRAM API
API_ID = 30367926
API_HASH = '3f846e3ad96fcc9dc7c4121cc94a1542'

# 2. USER LOGIN (The Spy)
# Your existing session string
STRING_SESSION = '1BVtsOHsBu2FA_Nk6gcqPweoks9SGyCJfLU5Qg3ByNplVWoKzigtRwR2HRXZZB0GaWR1gMFW2P30sHebC45RLiPmubr4dtBboBFCpFfIq_FnoEX1e5pOvc9mcyBgLkLFa2EgCOYJDDcKm3mZwEm7a-2-ek4T2SnGZb62svAlcBfiM_Wir9xa7hNwDU0Utm3xX4Z2vU8Gzf39hX0VpeWYf0ukcqwjaeWnleOYqDJARouTtRJ2bTJQc5_q9esTluCfI0R4vgPrOpNY5elfCXD6kf3H496KUvDthfeJ7FN74APuX--evGUM9xRC9Olw2G4fOtB0apQrOSgtdjQjgtMx2w79tvzRwRzY=' 

# 3. BOT SETTINGS (The Delivery Boy)
# PASTE YOUR NEW BOT TOKEN HERE!
BOT_TOKEN = '8539809736:AAF88cdpzmOnC2GGBPgFAB9WAI-cbMSEz7Y' 
BOT_USERNAME = 'Deals_Loader_Bot' # e.g., 'Deals_Loader_Bot' (No @ symbol)

# 4. CHANNELS
SOURCE_CHANNELS = [
    -1001410164119, -1001688606932, 'Premiumhe', -1001540295873,
    -1001711689402, -1001155027715, -1001235338108, -1001550332157,
    -1001646406064, -1001468395451, -1002949969373, -1001534858685,
    -1001426693150, -1001554352838, -1002487807424
]

MAIN_CHANNEL = 'get_premium_mod'      
STORAGE_CHANNEL_ID = -1003709968314   

# 5. MONETIZATION
API_URL = 'https://gplinks.in/api'
API_KEY = '3bad720a8ab1500ee1ed2f5de825e296cd813acb'

# ================================================================== #

# Client 1: The User (Spy)
user_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# Client 2: The Bot (Delivery)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

recent_files = deque(maxlen=50) 

# --- HELPER FUNCTIONS ---

def get_money_link(destination_link):
    """Converts the Bot Link into a Money Link"""
    try:
        params = {'api': API_KEY, 'url': destination_link, 'format': 'text'}
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            link = response.text.strip()
            return link if "http" in link else destination_link
        return destination_link
    except Exception as e:
        print(f"⚠️ Link Error: {e}")
        return destination_link

def clean_description(text):
    """Removes junk lines from description."""
    if not text: return ""
    lines = text.split('\n')
    cleaned = []
    forbidden = ['join', 'download', 'click', 'http', 't.me', 'bit.ly', 'share', '@']
    for line in lines:
        if not any(bad in line.lower() for bad in forbidden):
            cleaned.append(line)
    return "\n".join(cleaned)

# --- PART A: THE SPY (User Client) ---
@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def user_handler(event):
    if not event.message.file:
        return

    # Check Duplicate
    f_name = event.message.file.name or "unknown"
    f_size = event.message.file.size
    sig = f"{f_name}_{f_size}"
    if sig in recent_files:
        return
    recent_files.append(sig)

    print(f"📥 New File Detected: {f_name}")

    try:
        # 1. Upload to Storage (Private)
        stored_msg = await user_client.send_file(
            STORAGE_CHANNEL_ID,
            event.message.media,
            caption=event.message.text
        )

        # 2. Create Link to OUR BOT (Not the channel)
        # Link format: https://t.me/MyBot?start=12345
        bot_start_link = f"https://t.me/{BOT_USERNAME}?start={stored_msg.id}"
        money_link = get_money_link(bot_start_link)

        # 3. Clean Text & Post
        clean_name = (event.message.file.name or "App.apk").replace(".apk", "").replace("_", " ")
        size_mb = f"{event.message.file.size / (1024 * 1024):.1f} MB"
        desc = clean_description(event.message.text)
        
        caption = (
            f"🌀 **{clean_name}**\n"
            f"📦 **Size:** {size_mb}\n\n"
            f"💠 **Mod Info:**\n{desc[:800]}\n\n"
            f"⭕️ ➡️ [Click here to Download]({money_link})\n\n"
            f"☑️ **Direct Mod Apk File** ➡️ [Join Link](https://t.me/get_premium_mod)"
        )

        await user_client.send_message(MAIN_CHANNEL, caption, link_preview=False)
        print("✅ Posted to Main Channel")

    except Exception as e:
        print(f"⚠️ Error: {e}")

# --- PART B: THE DELIVERY BOY (Bot Client) ---
@bot_client.on(events.NewMessage(pattern='/start'))
async def bot_handler(event):
    # User sends: /start 12345
    # We extract "12345" to know which file they want
    try:
        args = event.message.text.split()
        if len(args) < 2:
            await event.reply("👋 Welcome! Please use the links from our channel to get files.")
            return

        message_id = int(args[1])
        print(f"📤 Delivery Request for File ID: {message_id}")

        # Fetch file from Storage Channel and send to User
        # NOTE: Bot must be Admin in Storage Channel to do this!
        post = await bot_client.get_messages(STORAGE_CHANNEL_ID, ids=message_id)
        
        if post and post.file:
            await event.reply(file=post.media, caption="✅ **Here is your file!**\n🚀 @get_premium_mod")
        else:
            await event.reply("❌ File not found. It might have been deleted.")

    except Exception as e:
        print(f"⚠️ Bot Delivery Error: {e}")
        await event.reply("❌ An error occurred.")

# --- RUNNER ---
print("🚀 Double-Agent Bot is Running...")
keep_alive()

# Start both clients
loop = asyncio.get_event_loop()
loop.create_task(bot_client.start(bot_token=BOT_TOKEN))
loop.create_task(user_client.start())
loop.run_forever()
