import asyncio
import requests
import re
from collections import deque
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive 

# ======================= CONFIGURATION ZONE ======================= #

# 1. TELEGRAM API (Your Data)
API_ID = 30367926
API_HASH = '3f846e3ad96fcc9dc7c4121cc94a1542'

# 2. USER LOGIN (The Spy - Your String Session)
STRING_SESSION = '1BVtsOHsBu2FA_Nk6gcqPweoks9SGyCJfLU5Qg3ByNplVWoKzigtRwR2HRXZZB0GaWR1gMFW2P30sHebC45RLiPmubr4dtBboBFCpFfIq_FnoEX1e5pOvc9mcyBgLkLFa2EgCOYJDDcKm3mZwEm7a-2-ek4T2SnGZb62svAlcBfiM_Wir9xa7hNwDU0Utm3xX4Z2vU8Gzf39hX0VpeWYf0ukcqwjaeWnleOYqDJARouTtRJ2bTJQc5_q9esTluCfI0R4vgPrOpNY5elfCXD6kf3H496KUvDthfeJ7FN74APuX--evGUM9xRC9Olw2G4fOtB0apQrOSgtdjQjgtMx2w79tvzRwRzY='

# 3. BOT SETTINGS (The Delivery Boy)
BOT_TOKEN = '8539809736:AAF88cdpzmOnC2GGBPgFAB9WAI-cbMSEz7Y'
BOT_USERNAME = 'Deals_Loader_Bot'

# 4. CHANNELS
SOURCE_CHANNELS = [
    -1001410164119, -1001688606932, 'Premiumhe', -1001540295873,
    -1001711689402, -1001155027715, -1001235338108, -1001550332157,
    -1001646406064, -1001468395451, -1002949969373, -1001534858685,
    -1001426693150, -1001554352838, -1002487807424, 'century_universe'
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

def clean_text_laser(text):
    """
    AGGRESSIVE CLEANER: Removes ANY line with links or 'Join'/'Click'.
    This deletes the old 'shortxlinks' from the source.
    """
    if not text: return ""
    lines = text.split('\n')
    cleaned_lines = []
    
    # 1. Regex to catch hidden URLs (http, www, .com, .in)
    url_pattern = re.compile(r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])')
    
    # 2. Words that mean "Trash Line"
    bad_words = ['join', 'click', 'download', 'link', 'share', 'subscribe', 'shortxlinks', 'bit.ly', 't.me', '@']

    for line in lines:
        lower_line = line.lower()
        
        # Rule A: If it has a URL, kill it.
        if url_pattern.search(line):
            continue
            
        # Rule B: If it has bad words, kill it.
        if any(bad in lower_line for bad in bad_words):
            continue
            
        # If it survived, keep it.
        if line.strip(): # Skip empty lines
            cleaned_lines.append(line)
            
    return "\n".join(cleaned_lines)

# --- PART A: THE SPY (User Client) ---
@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def user_handler(event):
    if not event.message.file:
        return

    # 1. SMART NAME DETECTION
    original_name = event.message.file.name
    
    if not original_name:
        if event.message.text:
            # Take the first line of text
            first_line = event.message.text.split('\n')[0]
            clean_first_line = re.sub(r'[^\w\s-]', '', first_line).strip()
            original_name = f"{clean_first_line[:30]}.apk"
        else:
            original_name = "Premium_App.apk"

    # Check Duplicate
    f_size = event.message.file.size
    sig = f"{original_name}_{f_size}"
    if sig in recent_files:
        print(f"❌ Duplicate Skipped: {original_name}")
        return
    recent_files.append(sig)

    print(f"📥 Processing New File: {original_name}")

    try:
        # 1. Upload to Storage (Private)
        stored_msg = await user_client.send_file(
            STORAGE_CHANNEL_ID,
            event.message.media,
            caption=event.message.text
        )

        # 2. Create Link to OUR BOT
        bot_start_link = f"https://t.me/{BOT_USERNAME}?start={stored_msg.id}"
        money_link = get_money_link(bot_start_link)

        # 3. Clean Text
        original_text = event.message.text or ""
        clean_desc = clean_text_laser(original_text)
        
        # 4. Build New Caption
        clean_name = original_name.replace(".apk", "").replace("_", " ")
        size_mb = f"{event.message.file.size / (1024 * 1024):.1f} MB"
        
        caption = (
            f"🌀 **{clean_name}**\n"
            f"📦 **Size:** {size_mb}\n\n"
            f"💠 **Mod Info:**\n{clean_desc[:800]}\n\n"
            f"⭕️ ➡️ [Click here to Download]({money_link})\n\n"
            f"☑️ **Direct Mod Apk File** ➡️ [Join Link](https://t.me/get_premium_mod)"
        )

        # 5. Post to Main Channel
        await user_client.send_file(
            MAIN_CHANNEL,
            event.message.media,
            caption=caption
        )
        print("✅ Posted to Main Channel")

    except Exception as e:
        print(f"⚠️ Error: {e}")

# --- PART B: THE DELIVERY BOY (Bot Client) ---
@bot_client.on(events.NewMessage(pattern='/start'))
async def bot_handler(event):
    try:
        args = event.message.text.split()
        if len(args) < 2:
            await event.reply("👋 Welcome! Please use the links from our channel.")
            return

        message_id = int(args[1])
        print(f"📤 Bot delivering file ID: {message_id}")

        post = await bot_client.get_messages(STORAGE_CHANNEL_ID, ids=message_id)
        if post and post.file:
            await event.reply(file=post.media, caption="✅ **Here is your file!**\n🚀 @get_premium_mod")
        else:
            await event.reply("❌ File not found.")

    except Exception as e:
        print(f"⚠️ Bot Error: {e}")

# --- RUNNER ---
print("🚀 Double-Agent Bot is Starting...")
keep_alive() # Essential for Render

async def main():
    # 1. Start the User Client (The Spy)
    print("⏳ Starting User Client...")
    await user_client.start()
    print("✅ User Client Started!")

    # 2. Start the Bot Client (The Delivery Boy)
    print("⏳ Starting Bot Client...")
    await bot_client.start(bot_token=BOT_TOKEN)
    print("✅ Bot Client Started!")

    # 3. Run both forever
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

# Standard Asyncio Boilerplate
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
