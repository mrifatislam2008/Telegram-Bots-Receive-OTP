# -*- coding: utf-8 -*-
# Importing necessary libraries
import asyncio
import re
import httpx
from bs4 import BeautifulSoup
import time
import json
import os
import traceback
from urllib.parse import urljoin
from datetime import datetime, timedelta
# New library added
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# --- Configuration (Fill in your details) ---
# Your Telegram Bot Token here. You can get it from BotFather.
# Example: YOUR_BOT_TOKEN = "8509088099:AAGIG_F-mqsZhHmEEY7zB-2eP20dq3w6p0s"
YOUR_BOT_TOKEN = "8649379795:AAGebKLEEm02f0i3kmBjMaG2UX_fh-qqF8o" # <--- This line needs to be changed

# ==================== New Addition: Multiple Admin IDs ====================
# Add your and other admins' Telegram User IDs to the list below
ADMIN_CHAT_IDS = ["7355153180"] # Example: ["YOUR_ADMIN_USER_ID_1", "YOUR_ADMIN_USER_ID_2"]
# =================================================================

# Old chat IDs kept for the first run
INITIAL_CHAT_IDS = ["-1002241783741"] 

LOGIN_URL = "https://www.ivasms.com/login"
BASE_URL = "https://www.ivasms.com/"
SMS_API_ENDPOINT = "https://www.ivasms.com/portal/sms/received/getsms"

USERNAME = "mrifatislam2008@gmail.com"
PASSWORD = "@MDRiFAT0025"

# Reduced interval to 2 seconds to keep the bot responsive and reduce server load
POLLING_INTERVAL_SECONDS = 2 
# STATE_FILE name changed
STATE_FILE = "processed_sms_ids.json" 
CHAT_IDS_FILE = "chat_ids.json" # New file for saving chat IDs

# List of countries
COUNTRY_FLAGS = {
    "Afghanistan": "ðŸ‡¦ðŸ‡«", "Albania": "ðŸ‡¦ðŸ‡±", "Algeria": "ðŸ‡©ðŸ‡¿", "Andorra": "ðŸ‡¦ðŸ‡©", "Angola": "ðŸ‡¦ðŸ‡´",
    "Argentina": "ðŸ‡¦ðŸ‡·", "Armenia": "ðŸ‡¦ðŸ‡²", "Australia": "ðŸ‡¦ðŸ‡º", "Austria": "ðŸ‡¦ðŸ‡¹", "Azerbaijan": "ðŸ‡¦ðŸ‡¿",
    "Bahrain": "ðŸ‡§ðŸ‡­", "Bangladesh": "ðŸ‡§ðŸ‡©", "Belarus": "ðŸ‡§ðŸ‡¾", "Belgium": "ðŸ‡§ðŸ‡ª", "Benin": "ðŸ‡§ðŸ‡¯",
    "Bhutan": "ðŸ‡§ðŸ‡¹", "Bolivia": "ðŸ‡§ðŸ‡´", "Brazil": "ðŸ‡§ðŸ‡·", "Bulgaria": "ðŸ‡§ðŸ‡¬", "Burkina Faso": "ðŸ‡§ðŸ‡«",
    "Cambodia": "ðŸ‡°ðŸ‡­", "Cameroon": "ðŸ‡¨ðŸ‡²", "Canada": "ðŸ‡¨ðŸ‡¦", "Chad": "ðŸ‡¹ðŸ‡©", "Chile": "ðŸ‡¨ ",
    "China": "ðŸ‡¨ðŸ‡³", "Colombia": "ðŸ‡¨ðŸ‡´", "Congo": "ðŸ‡¨ðŸ‡¬", "Croatia": "ðŸ‡­ðŸ‡·", "Cuba": "ðŸ‡¨ðŸ‡º",
    "Cyprus": "ðŸ‡¨ðŸ‡¾", "Czech Republic": "ðŸ‡¨ðŸ‡¿", "Denmark": "ðŸ‡©ðŸ‡°", "Egypt": "ðŸ‡ªðŸ‡¬", "Estonia": "ðŸ‡ªðŸ‡ª",
    "Ethiopia": "ðŸ‡ªðŸ‡¹", "Finland": "ðŸ‡«ðŸ‡®", "France": "ðŸ‡«ðŸ‡·", "Gabon": "ðŸ‡¬ðŸ‡¦", "Gambia": "ðŸ‡¬ðŸ‡²",
    "Georgia": "ðŸ‡¬ðŸ‡ª", "Germany": "ðŸ‡©ðŸ‡ª", "Ghana": "ðŸ‡¬ðŸ‡­", "Greece": "ðŸ‡¬ðŸ‡·", "Guatemala": "ðŸ‡¬ðŸ‡¹",
    "Guinea": "ðŸ‡¬ðŸ‡³", "Haiti": "ðŸ‡­ðŸ‡¹", "Honduras": "ðŸ‡­ðŸ‡³", "Hong Kong": "ðŸ‡­ðŸ‡°", "Hungary": "ðŸ‡­ðŸ‡º",
    "Iceland": "ðŸ‡®ðŸ‡¸", "India": "ðŸ‡®ðŸ‡³", "Indonesia": "ðŸ‡®ðŸ‡©", "Iran": "ðŸ‡®ðŸ‡·", "Iraq": "ðŸ‡®ðŸ‡¶",
    "Ireland": "ðŸ‡®ðŸ‡ª", "Israel": "ðŸ‡®ðŸ‡±", "Italy": "ðŸ‡®ðŸ‡¹", "IVORY COAST": "ðŸ‡¨ðŸ‡®", "Ivory Coast": "ðŸ‡¨ðŸ‡®", "Jamaica": "ðŸ‡¯ðŸ‡²",
    "Japan": "ðŸ‡¯ðŸ‡µ", "Jordan": "ðŸ‡¯ðŸ‡´", "Kazakhstan": "ðŸ‡°ðŸ‡¿", "Kenya": "ðŸ‡°ðŸ‡ª", "Kuwait": "ðŸ‡°ðŸ‡¼",
    "Kyrgyzstan": "ðŸ‡°ðŸ‡¬", "Laos": "ðŸ‡±ðŸ‡¦", "Latvia": "ðŸ‡±ðŸ‡»", "Lebanon": "ðŸ‡±ðŸ‡§", "Liberia": "ðŸ‡±ðŸ‡·",
    "Libya": "ðŸ‡±ðŸ‡¾", "Lithuania": "ðŸ‡±ðŸ‡¹", "Luxembourg": "ðŸ‡±ðŸ‡º", "Madagascar": "ðŸ‡²ðŸ‡¬", "Malaysia": "ðŸ‡²ðŸ‡¾",
    "Mali": "ðŸ‡²ðŸ‡±", "Malta": "ðŸ‡²ðŸ‡¹", "Mexico": "ðŸ‡²ðŸ‡½", "Moldova": "ðŸ‡²ðŸ‡©", "Monaco": "ðŸ‡²ðŸ‡¨",
    "Mongolia": "ðŸ‡²ðŸ‡³", "Montenegro": "ðŸ‡²ðŸ‡ª", "Morocco": "ðŸ‡²ðŸ‡¦", "Mozambique": "ðŸ‡²ðŸ‡¿", "Myanmar": "ðŸ‡²ðŸ‡²",
    "Namibia": "ðŸ‡³ðŸ‡¦", "Nepal": "ðŸ‡³ðŸ‡µ", "Netherlands": "ðŸ‡³ðŸ‡±", "New Zealand": "ðŸ‡³ðŸ‡¿", "Nicaragua": "ðŸ‡³ðŸ‡®",
    "Niger": "ðŸ‡³ðŸ‡ª", "Nigeria": "ðŸ‡³ðŸ‡¬", "North Korea": "ðŸ‡°ðŸ‡µ", "North Macedonia": "ðŸ‡²ðŸ‡°", "Norway": "ðŸ‡³ðŸ‡´",
    "Oman": "ðŸ‡´ðŸ‡²", "Pakistan": "ðŸ‡µðŸ‡°", "Panama": "ðŸ‡µðŸ‡¦", "Paraguay": "ðŸ‡µðŸ‡¾", "Peru": "ðŸ‡µðŸ‡ª",
    "Philippines": "ðŸ‡µðŸ‡­", "Poland": "ðŸ‡µðŸ‡±", "Portugal": "ðŸ‡µðŸ‡¹", "Qatar": "ðŸ‡¶ðŸ‡¦", "Romania": "ðŸ‡·ðŸ‡´",
    "Russia": "ðŸ‡·ðŸ‡º", "Rwanda": "ðŸ‡·ðŸ‡¼", "Saudi Arabia": "ðŸ‡¸ðŸ‡¦", "Senegal": "ðŸ‡¸ðŸ‡³", "Serbia": "ðŸ‡·ðŸ‡¸",
    "Sierra Leone": "ðŸ‡¸ðŸ‡±", "Singapore": "ðŸ‡¸ðŸ‡¬", "Slovakia": "ðŸ‡¸ðŸ‡°", "Slovenia": "ðŸ‡¸ðŸ‡®", "Somalia": "ðŸ‡¸ðŸ‡´",
    "South Africa": "ðŸ‡¿ðŸ‡¦", "South Korea": "ðŸ‡°ðŸ‡·", "Spain": "ðŸ‡ªðŸ‡¸", "Sri Lanka": "ðŸ‡±ðŸ‡°", "Sudan": "ðŸ‡¸ðŸ‡©",
    "Sweden": "ðŸ‡¸ðŸ‡ª", "Switzerland": "ðŸ‡¨ðŸ‡­", "Syria": "ðŸ‡¸ðŸ‡¾", "Taiwan": "ðŸ‡¹ðŸ‡¼", "Tajikistan": "ðŸ‡¹ðŸ‡¯",
    "Tanzania": "ðŸ‡¹ðŸ‡¿", "Thailand": "ðŸ‡¹ðŸ‡­", "TOGO": "ðŸ‡¹ðŸ‡¬", "Tunisia": "ðŸ‡¹ðŸ‡³", "Turkey": "ðŸ‡¹ðŸ‡·",
    "Turkmenistan": "ðŸ‡¹ðŸ‡²", "Uganda": "ðŸ‡ºðŸ‡¬", "Ukraine": "ðŸ‡ºðŸ‡¦", "United Arab Emirates": "ðŸ‡¦ðŸ‡ª", "United Kingdom": "ðŸ‡¬ðŸ‡§",
    "United States": "ðŸ‡ºðŸ‡¸", "Uruguay": "ðŸ‡ºðŸ‡¾", "Uzbekistan": "ðŸ‡ºðŸ‡¿", "Venezuela": "ðŸ‡»ðŸ‡ª", "Vietnam": "ðŸ‡»ðŸ‡³",
    "Yemen": "ðŸ‡¾ðŸ‡ª", "Zambia": "ðŸ‡¿ðŸ‡²", "Zimbabwe": "ðŸ‡¿ðŸ‡¼", "Unknown Country": "ðŸ´â€â˜ ï¸"
}

# Service Keywords (for identifying service from SMS text)
SERVICE_KEYWORDS = {
    "Facebook": ["facebook"],
    "Google": ["google", "gmail"],
    "WhatsApp": ["whatsapp"],
    "Telegram": ["telegram"],
    "Instagram": ["instagram"],
    "Amazon": ["amazon"],
    "Netflix": ["netflix"],
    "LinkedIn": ["linkedin"],
    "Microsoft": ["microsoft", "outlook", "live.com"],
    "Apple": ["apple", "icloud"],
    "Twitter": ["twitter"],
    "Snapchat": ["snapchat"],
    "TikTok": ["tiktok"],
    "Discord": ["discord"],
    "Signal": ["signal"],
    "Viber": ["viber"],
    "IMO": ["imo"],
    "PayPal": ["paypal"],
    "Binance": ["binance"],
    "Uber": ["uber"],
    "Bolt": ["bolt"],
    "Airbnb": ["airbnb"],
    "Yahoo": ["yahoo"],
    "Steam": ["steam"],
    "Blizzard": ["blizzard"],
    "Foodpanda": ["foodpanda"],
    "Pathao": ["pathao"],
    # Newly added service keywords
    "Messenger": ["messenger", "meta"],
    "Gmail": ["gmail", "google"],
    "YouTube": ["youtube", "google"],
    "X": ["x", "twitter"],
    "eBay": ["ebay"],
    "AliExpress": ["aliexpress"],
    "Alibaba": ["alibaba"],
    "Flipkart": ["flipkart"],
    "Outlook": ["outlook", "microsoft"],
    "Skype": ["skype", "microsoft"],
    "Spotify": ["spotify"],
    "iCloud": ["icloud", "apple"],
    "Stripe": ["stripe"],
    "Cash App": ["cash app", "square cash"],
    "Venmo": ["venmo"],
    "Zelle": ["zelle"],
    "Wise": ["wise", "transferwise"],
    "Coinbase": ["coinbase"],
    "KuCoin": ["kucoin"],
    "Bybit": ["bybit"],
    "OKX": ["okx"],
    "Huobi": ["huobi"],
    "Kraken": ["kraken"],
    "MetaMask": ["metamask"],
    "Epic Games": ["epic games", "epicgames"],
    "PlayStation": ["playstation", "psn"],
    "Xbox": ["xbox", "microsoft"],
    "Twitch": ["twitch"],
    "Reddit": ["reddit"],
    "ProtonMail": ["protonmail", "proton"],
    "Zoho": ["zoho"],
    "Quora": ["quora"],
    "StackOverflow": ["stackoverflow"],
    "LinkedIn": ["linkedin"],
    "Indeed": ["indeed"],
    "Upwork": ["upwork"],
    "Fiverr": ["fiverr"],
    "Glassdoor": ["glassdoor"],
    "Airbnb": ["airbnb"],
    "Booking.com": ["booking.com", "booking"],
    "Careem": ["careem"],
    "Swiggy": ["swiggy"],
    "Zomato": ["zomato"],
    "McDonald's": ["mcdonalds", "mcdonald's"],
    "KFC": ["kfc"],
    "Nike": ["nike"],
    "Adidas": ["adidas"],
    "Shein": ["shein"],
    "OnlyFans": ["onlyfans"],
    "Tinder": ["tinder"],
    "Bumble": ["bumble"],
    "Grindr": ["grindr"],
    "Line": ["line"],
    "WeChat": ["wechat"],
    "VK": ["vk", "vkontakte"],
    "Unknown": ["unknown"] # Fallback, likely won't have specific keywords
}

# Service Emojis (for display in Telegram messages)
SERVICE_EMOJIS = {
    "Telegram": "ðŸ“©", "WhatsApp": "ðŸŸ¢", "Facebook": "ðŸ“˜", "Instagram": "ðŸ“¸", "Messenger": "ðŸ’¬",
    "Google": "ðŸ”", "Gmail": "âœ‰ï¸", "YouTube": "â–¶ï¸", "Twitter": "ðŸ¦", "X": "âŒ",
    "TikTok": "ðŸŽµ", "Snapchat": "ðŸ‘»", "Amazon": "ðŸ›’", "eBay": "ðŸ“¦", "AliExpress": "ðŸ“¦",
    "Alibaba": "ðŸ­", "Flipkart": "ðŸ“¦", "Microsoft": "ðŸªŸ", "Outlook": "ðŸ“§", "Skype": "ðŸ“ž",
    "Netflix": "ðŸŽ¬", "Spotify": "ðŸŽ¶", "Apple": "ðŸ", "iCloud": "â˜ï¸", "PayPal": "ðŸ’°",
    "Stripe": "ðŸ’³", "Cash App": "ðŸ’µ", "Venmo": "ðŸ’¸", "Zelle": "ðŸ¦", "Wise": "ðŸŒ",
    "Binance": "ðŸª™", "Coinbase": "ðŸª™", "KuCoin": "ðŸª™", "Bybit": "ðŸ“ˆ", "OKX": "ðŸŸ ",
    "Huobi": "ðŸ”¥", "Kraken": "ðŸ™", "MetaMask": "ðŸ¦Š", "Discord": "ðŸ—¨ï¸", "Steam": "ðŸŽ®",
    "Epic Games": "ðŸ•¹ï¸", "PlayStation": "ðŸŽ®", "Xbox": "ðŸŽ®", "Twitch": "ðŸ“º", "Reddit": "ðŸ‘½",
    "Yahoo": "ðŸŸ£", "ProtonMail": "ðŸ”", "Zoho": "ðŸ“¬", "Quora": "â“", "StackOverflow": "ðŸ§‘â€ðŸ’»",
    "LinkedIn": "ðŸ’¼", "Indeed": "ðŸ“‹", "Upwork": "ðŸ§‘â€ðŸ’»", "Fiverr": "ðŸ’»", "Glassdoor": "ðŸ”Ž",
    "Airbnb": "ðŸ ", "Booking.com": "ðŸ›ï¸", "Uber": "ðŸš—", "Lyft": "ðŸš•", "Bolt": "ðŸš–",
    "Careem": "ðŸš—", "Swiggy": "ðŸ”", "Zomato": "ðŸ½ï¸", "Foodpanda": "ðŸ±",
    "McDonald's": "ðŸŸ", "KFC": "ðŸ—", "Nike": "ðŸ‘Ÿ", "Adidas": "ðŸ‘Ÿ", "Shein": "ðŸ‘—",
    "OnlyFans": "ðŸ”ž", "Tinder": "ðŸ”¥", "Bumble": "ðŸ", "Grindr": "ðŸ˜ˆ", "Signal": "ðŸ”",
    "Viber": "ðŸ“ž", "Line": "ðŸ’¬", "WeChat": "ðŸ’¬", "VK": "ðŸŒ", "Unknown": "â“"
}

# --- Chat ID Management Functions ---
def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, 'w') as f:
            json.dump(INITIAL_CHAT_IDS, f)
        return INITIAL_CHAT_IDS
    try:
        with open(CHAT_IDS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return INITIAL_CHAT_IDS

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, 'w') as f:
        json.dump(chat_ids, f, indent=4)

# --- New Telegram Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) in ADMIN_CHAT_IDS:
        await update.message.reply_text(
            "Welcome Admin!\n"
            "You can use the following commands:\n"
            "/add_chat <chat_id> - Add a new chat ID\n"
            "/remove_chat <chat_id> - Remove a chat ID\n"
            "/list_chats - List all chat IDs"
        )
    else:
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")

async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    try:
        new_chat_id = context.args[0]
        chat_ids = load_chat_ids()
        if new_chat_id not in chat_ids:
            chat_ids.append(new_chat_id)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"âœ… Chat ID {new_chat_id} successfully added.")
        else:
            await update.message.reply_text(f"âš ï¸ This chat ID ({new_chat_id}) is already in the list.")
    except (IndexError, ValueError):
        await update.message.reply_text("âŒ Invalid format. Use: /add_chat <chat_id>")

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    try:
        chat_id_to_remove = context.args[0]
        chat_ids = load_chat_ids()
        if chat_id_to_remove in chat_ids:
            chat_ids.remove(chat_id_to_remove)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"âœ… Chat ID {chat_id_to_remove} successfully removed.")
        else:
            await update.message.reply_text(f"ðŸ¤” This chat ID ({chat_id_to_remove}) was not found in the list.")
    except (IndexError, ValueError):
        await update.message.reply_text("âŒ Invalid format. Use: /remove_chat <chat_id>")

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    
    chat_ids = load_chat_ids()
    if chat_ids:
        message = "ðŸ“œ Currently registered chat IDs are:\n"
        for cid in chat_ids:
            message += f"- `{escape_markdown(str(cid))}`\n"
        try:
            await update.message.reply_text(message, parse_mode='MarkdownV2')
        except Exception as e:
            plain_message = "ðŸ“œ Currently registered chat IDs are:\n" + "\n".join(map(str, chat_ids))
            await update.message.reply_text(plain_message)
    else:
        await update.message.reply_text("No chat IDs registered.")

# --- Core Functions ---
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def load_processed_ids():
    if not os.path.exists(STATE_FILE): return set()
    try:
        with open(STATE_FILE, 'r') as f: return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError): return set()

def save_processed_id(sms_id):
    processed_ids = load_processed_ids()
    processed_ids.add(sms_id)
    with open(STATE_FILE, 'w') as f: json.dump(list(processed_ids), f)

async def fetch_sms_from_api(client: httpx.AsyncClient, headers: dict, csrf_token: str):
    all_messages = []
    try:
        today = datetime.utcnow() # Using UTC time
        start_date = today - timedelta(days=1) # Data for the last 24 hours
        from_date_str, to_date_str = start_date.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y')
        first_payload = {'from': from_date_str, 'to': to_date_str, '_token': csrf_token}
        summary_response = await client.post(SMS_API_ENDPOINT, headers=headers, data=first_payload)
        summary_response.raise_for_status()
        summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
        group_divs = summary_soup.find_all('div', {'class': 'pointer'})
        if not group_divs: return []
        
        group_ids = [re.search(r"getDetials\('(.+?)'\)", div.get('onclick', '')).group(1) for div in group_divs if re.search(r"getDetials\('(.+?)'\)", div.get('onclick', ''))]
        numbers_url = urljoin(BASE_URL, "portal/sms/received/getsms/number")
        sms_url = urljoin(BASE_URL, "portal/sms/received/getsms/number/sms")

        for group_id in group_ids:
            numbers_payload = {'start': from_date_str, 'end': to_date_str, 'range': group_id, '_token': csrf_token}
            numbers_response = await client.post(numbers_url, headers=headers, data=numbers_payload)
            numbers_soup = BeautifulSoup(numbers_response.text, 'html.parser')
            number_divs = numbers_soup.select("div[onclick*='getDetialsNumber']")
            if not number_divs: continue
            phone_numbers = [div.text.strip() for div in number_divs]
            
            for phone_number in phone_numbers:
                sms_payload = {'start': from_date_str, 'end': to_date_str, 'Number': phone_number, 'Range': group_id, '_token': csrf_token}
                sms_response = await client.post(sms_url, headers=headers, data=sms_payload)
                sms_soup = BeautifulSoup(sms_response.text, 'html.parser')
                final_sms_cards = sms_soup.find_all('div', class_='card-body')
                
                for card in final_sms_cards:
                    sms_text_p = card.find('p', class_='mb-0')
                    if sms_text_p:
                        sms_text = sms_text_p.get_text(separator='\n').strip()
                        date_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') # Using UTC time
                        
                        country_name_match = re.match(r'([a-zA-Z\s]+)', group_id)
                        if country_name_match: country_name = country_name_match.group(1).strip()
                        else: country_name = group_id.strip()
                        
                        service = "Unknown"
                        lower_sms_text = sms_text.lower()
                        for service_name, keywords in SERVICE_KEYWORDS.items():
                            if any(keyword in lower_sms_text for keyword in keywords):
                                service = service_name
                                break
                        code_match = re.search(r'(\d{3}-\d{3})', sms_text) or re.search(r'\b(\d{4,8})\b', sms_text)
                        code = code_match.group(1) if code_match else "N/A"
                        unique_id = f"{phone_number}-{sms_text}"
                        flag = COUNTRY_FLAGS.get(country_name, "ðŸ´â€â˜ ï¸")
                        
                        # Using 'sms_text' instead of 'full_sms_text'
                        all_messages.append({"id": unique_id, "time": date_str, "number": phone_number, "country": country_name, "flag": flag, "service": service, "code": code, "full_sms": sms_text}) 
        return all_messages
    except httpx.RequestError as e:
        print(f"âŒ Network issue (httpx): {e}")
        return []
    except Exception as e:
        print(f"âŒ Error fetching or processing API data: {e}")
        traceback.print_exc()
        return []

async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE, chat_id: str, message_data: dict):
    try:
        time_str, number_str = message_data.get("time", "N/A"), message_data.get("number", "N/A")
        country_name, flag_emoji = message_data.get("country", "N/A"), message_data.get("flag", "ðŸ´â€â˜ ï¸")
        service_name, code_str = message_data.get("service", "N/A"), message_data.get("code", "N/A")
        full_sms_text = message_data.get("full_sms", "N/A")
        
        # Add service emoji
        service_emoji = SERVICE_EMOJIS.get(service_name, "â“") # If service not found, show 'â“'

        # Message format reverted to previous state with extra spacing
        full_message = (f"ðŸ”” *You have successfully received OTP*\n\n" 
                        f"ðŸ“ž *Number:* `{escape_markdown(number_str)}`\n" 
                        f"ðŸ”‘ *Code:* `{escape_markdown(code_str)}`\n" 
                        f"ðŸ† *Service:* {service_emoji} {escape_markdown(service_name)}\n" 
                        f"ðŸŒŽ *Country:* {escape_markdown(country_name)} {flag_emoji}\n" 
                        f"â³ *Time:* `{escape_markdown(time_str)}`\n\n" 
                        f"ðŸ’¬ *Message:*\n" 
                        f"```\n{full_sms_text}\n```")
        
        await context.bot.send_message(chat_id=chat_id, text=full_message, parse_mode='MarkdownV2')
    except Exception as e:
        print(f"âŒ Error sending message to chat ID {chat_id}: {e}")

# --- Main Job or Task ---
async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    print(f"\n--- [{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new messages ---") # Using UTC time
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Instructing httpx client to follow redirects
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            print("â„¹ï¸ Attempting to log in...")
            login_page_res = await client.get(LOGIN_URL, headers=headers)
            soup = BeautifulSoup(login_page_res.text, 'html.parser')
            token_input = soup.find('input', {'name': '_token'})
            login_data = {'email': USERNAME, 'password': PASSWORD}
            if token_input: login_data['_token'] = token_input['value']

            login_res = await client.post(LOGIN_URL, data=login_data, headers=headers)
            
            # A 302 redirect can be a sign of successful login, so checking URL instead of raise_for_status()
            if "login" in str(login_res.url):
                print("âŒ Login failed. Check username/password.")
                return

            print("âœ… Login successful!")
            dashboard_soup = BeautifulSoup(login_res.text, 'html.parser')
            csrf_token_meta = dashboard_soup.find('meta', {'name': 'csrf-token'})
            if not csrf_token_meta:
                print("âŒ New CSRF token not found.")
                return
            csrf_token = csrf_token_meta.get('content')

            headers['Referer'] = str(login_res.url)
            messages = await fetch_sms_from_api(client, headers, csrf_token)
            if not messages: 
                print("âœ”ï¸ No new messages found.")
                return

            processed_ids = load_processed_ids()
            chat_ids_to_send = load_chat_ids()
            new_messages_found = 0
            
            for msg in reversed(messages):
                if msg["id"] not in processed_ids:
                    new_messages_found += 1
                    print(f"âœ”ï¸ New message found from: {msg['number']}.")
                    for chat_id in chat_ids_to_send:
                        await send_telegram_message(context, chat_id, msg)
                    save_processed_id(msg["id"])
            
            if new_messages_found > 0:
                print(f"âœ… Total {new_messages_found} new messages sent to Telegram.")

        except httpx.RequestError as e:
            print(f"âŒ Network or login issue (httpx): {e}")
        except Exception as e:
            print(f"âŒ A problem occurred in the main process: {e}")
            traceback.print_exc()

# --- Main part to start the bot ---
def main():
    print("ðŸš€ iVasms to Telegram Bot is starting...")

    # Not checking for 'YOUR_SECOND_ADMIN_ID_HERE' anymore,
    # as you have correctly provided the IDs in ADMIN_CHAT_IDS.
    # A warning will be shown if the ADMIN_CHAT_IDS list is empty.
    if not ADMIN_CHAT_IDS:
        print("\n!!! ðŸ”´ WARNING: You have not correctly set admin IDs in your ADMIN_CHAT_IDS list. !!!\n")
        return

    # Create the bot application
    application = Application.builder().token(YOUR_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add_chat", add_chat_command))
    application.add_handler(CommandHandler("remove_chat", remove_chat_command))
    application.add_handler(CommandHandler("list_chats", list_chats_command))

    # Set the main job to run repeatedly at a specific interval
    job_queue = application.job_queue
    job_queue.run_repeating(check_sms_job, interval=POLLING_INTERVAL_SECONDS, first=1)

    print(f"ðŸš€ Checking for new messages every {POLLING_INTERVAL_SECONDS} seconds.")
    print("ðŸ¤– Bot is now online. Ready to listen for commands.")
    print("âš ï¸ Press Ctrl+C to stop the bot.")
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()**
