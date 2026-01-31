import asyncio
import requests
import os
from collections import deque
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive  # Must have keep_alive.py in same folder

# ======================= CONFIGURATION ZONE ======================= #

# 1. TELEGRAM API
API_ID = 30367926
API_HASH = '3f846e3ad96fcc9dc7c4121cc94a1542'

# 2. LOGIN SESSION
# Leave empty '' for Laptop/PC testing.
# PASTE the long string here for Cloud (Render/Heroku)
STRING_SESSION = '1BVtsOHsBu2FA_Nk6gcqPweoks9SGyCJfLU5Qg3ByNplVWoKzigtRwR2HRXZZB0GaWR1gMFW2P30sHebC45RLiPmubr4dtBboBFCpFfIq_FnoEX1e5pOvc9mcyBgLkLFa2EgCOYJDDcKm3mZwEm7a-2-ek4T2SnGZb62svAlcBfiM_Wir9xa7hNwDU0Utm3xX4Z2vU8Gzf39hX0VpeWYf0ukcqwjaeWnleOYqDJARouTtRJ2bTJQc5_q9esTluCfI0R4vgPrOpNY5elfCXD6kf3H496KUvDthfeJ7FN74APuX--evGUM9xRC9Olw2G4fOtB0apQrOSgtdjQjgtMx2w79tvzRwRzY=' 

# 3. CHANNELS SETUP
SOURCE_CHANNELS = [
    -1001410164119,
    -1001688606932,
    'Premiumhe',            # Username (Must have quotes)
    -1001540295873,
    -1001711689402,
    -1001155027715,
    -1001235338108,
    -1001550332157,
    -1001646406064,
    -1001468395451,
    -1002949969373,
    -1001534858685,
    -1001426693150,
    -1001554352838,
    -1002487807424
]

MAIN_CHANNEL = 'get_premium_mod'      # Your Public Channel Username
STORAGE_CHANNEL_ID = -1003709968314   # Your Private Database ID

# 4. MONETIZATION SETUP
API_URL = 'https://gplinks.in/api'
API_KEY = '3bad720a8ab1500ee1ed2f5de825e296cd813acb'

# ================================================================== #

# Initialize Client
if STRING_SESSION:
    # Mode A: Cloud (Uses String)
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
else:
    # Mode B: Laptop (Uses File)
    client = TelegramClient('moneybot_laptop', API_ID, API_HASH)

# --- DUPLICATE CHECKER SYSTEM ---
recent_files = deque(maxlen=50) 

def get_money_link(long_url):
    """Generates the monetized link."""
    try:
        params = {'api': API_KEY, 'url': long_url, 'format': 'text'}
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            link = response.text.strip()
            return link if "http" in link else long_url
        return long_url
    except Exception as e:
        print(f"⚠️ Link Error: {e}")
        return long_url

def is_duplicate(message):
    """Checks if file is a duplicate."""
    if not message.file:
        return False
        
    file_name = message.file.name or "unknown_apk"
    file_size = message.file.size
    signature = f"{file_name}_{file_size}"
    
    if signature in recent_files:
        return True
    
    recent_files.append(signature)
    return False

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    # Filter: Only process if it has a file
    if not event.message.file:
        return

    print(f"\n👀 Detected File in {event.chat_id}...")

    # 1. DUPLICATE CHECK
    if is_duplicate(event.message):
        print(f"❌ Duplicate Skipped: {event.message.file.name}")
        return

    print(f"📥 Processing: {event.message.file.name}")

    try:
        # 2. COPY TO STORAGE (Private)
        stored_msg = await client.send_file(
            STORAGE_CHANNEL_ID,
            event.message.media,
            caption=event.message.text
        )

        # 3. GENERATE LINKS
        clean_id = str(STORAGE_CHANNEL_ID).replace("-100", "")
        direct_link = f"https://t.me/c/{clean_id}/{stored_msg.id}"
        money_link = get_money_link(direct_link)
        
        # 4. CREATE CAPTION
        original_text = event.message.text or "Premium App"
        title = original_text.split('\n')[0][:50] 
        
        caption_text = (
            f"🔥 **{title}**\n\n"
            f"📥 **Download Link:**\n{money_link}\n\n"
            f"⚙️ _Tutorial: Click link -> Wait 10s -> Get Link_"
        )

        # 5. POST TO MAIN CHANNEL
        await client.send_message(
            MAIN_CHANNEL,
            caption_text,
            file=event.message.media if hasattr(event.message, 'photo') else None
        )
        print(f"✅ Posted Successfully to {MAIN_CHANNEL}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

print("🚀 Ultimate Money Bot is Running...")

# --- CRITICAL FOR 24/7 HOSTING ---
keep_alive()  # Starts the fake web server
# ---------------------------------

client.start()
client.run_until_disconnected()