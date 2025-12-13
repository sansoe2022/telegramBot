import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread
import os
import requests
import re

# --- CONFIGURATION ---
# ⚠️ သင့် Token အမှန်ကို ပြန်ထည့်ပါ
API_TOKEN = '8392015081:AAH7kW0EtCUTQDgOLM3OEloiEJfQBjMoDec'
JSON_URL = 'https://raw.githubusercontent.com/sansoe2022/mwd-web/refs/heads/main/api.json'
ADMIN_USERNAME = "sansoe2021"

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

# --- DATA FETCHING ---
def get_data():
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

# --- TEXT PARSING HELPER ---
def parse_amount(text):
    text = text.replace(',', '').replace(' ', '')
    multiplier = 1
    
    if 'သိန်း' in text:
        multiplier = 100000
        text = text.replace('သိန်း', '')
    elif 'သောင်း' in text:
        multiplier = 10000
        text = text.replace('သောင်း', '')
    elif 'ထောင်' in text:
        multiplier = 1000
        text = text.replace('ထောင်', '')
        
    match = re.search(r"(\d+(\.\d+)?)", text)
    if match:
        return float(match.group(1)) * multiplier
    return None

# --- FLASK KEEP-ALIVE ---
@app.route('/')
def home(): return "MWD Zay Bot is Running!"

def run_http():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- MENUS ---
def get_reply_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💰 ယခုငွေဈေး", "📱 ဖုန်းဘေဈေး", "💸 ငွေလွှဲမယ်", "📥 MWD Zay ဒေါင်းရန်", "❓ အကူအညီ")
    return markup

# --- HELPERS FOR FALLBACK ---
def send_fallback(message):
    text = (
        "ကျွန်တော်က ငွေစျေးတွက်ပေးတဲ့ bot ဖြစ်ပါတယ် တခြားအကြောင်းအရာတွေ မဖြေဆိုနိုင်ပါခင်ဗျာ ငွေစျေး အသေးစိတ်သိလိုပါက Admin ကို တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ\n\n"
    "<b>အသုံးပြုပုံ လမ်းညွှန်</b>\n\n"
        "🇲🇲 <b>ကျပ်ငွေလိုချင်ပါက \nဘတ်ပေး (ပမာဏ) သို့မဟုတ် ကျပ်ယူ (ပမာဏ) ရေးပါ</b>\n"
        "ဥပမာ - \n• ဘတ်ပေး 1000 ဘတ် \n• ကျပ်ယူ 1သိန်းကျပ်\n\n"
        "🇹🇭 <b>ဘတ်ငွေလိုချင်ပါက \nကျပ်ပေး (ပမာဏ) သို့မဟုတ် ဘတ်ယူ (ပမာဏ) ရေးပါ</b>\n"
        "ဥပမာ - \n• ကျပ်ပေး 1သိန်းကျပ် \n• ဘတ်ယူ 1000 ဘတ်\n\n"
        "လိုချင်သော ပမာဏကို ပြင်ပြီး တွက်ချက်နိုင်ပါသည်။"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Adminကို ဆက်သွယ်ရန်", url=f"https://t.me/{ADMIN_USERNAME}"))
    bot.reply_to(message, text, reply_markup=markup)

# --- COMMAND HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "မင်္ဂလာပါ MWD Zay Bot မှ ကြိုဆိုပါတယ်။", reply_markup=get_reply_menu())

# --- MENU ACTIONS ---

# 1. ယခုငွေဈေး
@bot.message_handler(func=lambda message: message.text == "💰 ယခုငွေဈေး")
def menu_rate(message):
    data = get_data()
    if data:
        th_rate = data.get('thRate', 815)
        mm_rate = data.get('mmRate', 795)
        text = (f"📅 <b>ယခုငွေဈေး</b>\n\n"
                f"🇹🇭➡️🇲🇲 <b>ဘတ်ပေးကျပ်ယူ (1 သိန်းကျပ်) = {th_rate} ဘတ်</b>\n"
                f"🇲🇲➡️🇹🇭 <b>ကျပ်ပေးဘတ်ယူ (1 သိန်းကျပ်) = {mm_rate} ဘတ်</b>\n\n\n\n"
                f"ဝန်ဆောင်ခများ👇👇👇\n\n"
                f"Kpay|WavePay|ဘဏ်အကောင့်အားလုံး \nပေါက်စျေးအတိုင်းရပါတယ်\n\n"
                f"Wave password(ဆိုင်ထုတ်) \nဝန်ဆောင်ခ 15 ဘတ်\n\n"
                f"ဘဏ်မှတ်ပုံတင်ထုတ် ဝန်ဆောင်ခ 5ဘတ်\n\n"
                f"1သိန်းကျပ်အောက် ဖြစ်ပါက ဖုန်းဘေစျေးနှုန်းအတိုင်း တွက်ပါတယ်\n")
        bot.reply_to(message, text, parse_mode='HTML')

# 2. ဖုန်းဘေဈေး
@bot.message_handler(func=lambda message: message.text == "📱 ဖုန်းဘေဈေး")
def menu_bill(message):
    data = get_data()
    if data:
        items = data.get('items', [])
        text = "📱 <b>မြန်မာဖုန်းဘေဈေးနှုန်းများ</b>\n\n"
        for item in items:
            text += f"🇲🇲 {item.get('mmkBill')} Ks = 🇹🇭 {item.get('thbBill')} B\n"
        bot.reply_to(message, text, parse_mode='HTML')

# 3. ငွေလွှဲမယ်
@bot.message_handler(func=lambda message: message.text == "💸 ငွေလွှဲမယ်")
def menu_transfer(message):
    text = "ငွေလွှဲလိုပါက Adminကို တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Admin ကိုဆက်သွယ်ရန်", url=f"https://t.me/{ADMIN_USERNAME}"))
    bot.reply_to(message, text, reply_markup=markup)

# 4. Download App
@bot.message_handler(func=lambda message: message.text == "📥 MWD Zay ဒေါင်းရန်")
def menu_download(message):
    data = get_data()
    link = data.get('link', 'https://play.google.com/store/apps/details?id=com.sksdev.mwdcalculator') if data else 'https://google.com'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📥 Click here to Download", url=link))
    bot.reply_to(message, "အောက်ပါ Button ကို နှိပ်၍ MWD Zayကို Download ရယူနိုင်ပါတယ်ခင်ဗျာ။", reply_markup=markup)

# 5. အကူအညီ
@bot.message_handler(func=lambda message: message.text == "❓ အကူအညီ")
def menu_help(message):
    text = (
        "<b>အသုံးပြုပုံ လမ်းညွှန်</b>\n\n"
        "🇲🇲 <b>ကျပ်ငွေလိုချင်ပါက \nဘတ်ပေး (ပမာဏ) သို့မဟုတ် ကျပ်ယူ (ပမာဏ) ရေးပါ</b>\n"
        "ဥပမာ - \n• ဘတ်ပေး 1000 ဘတ် \n• ကျပ်ယူ 1သိန်းကျပ်\n\n"
        "🇹🇭 <b>ဘတ်ငွေလိုချင်ပါက \nကျပ်ပေး (ပမာဏ) သို့မဟုတ် ဘတ်ယူ (ပမာဏ) ရေးပါ</b>\n"
        "ဥပမာ - \n• ကျပ်ပေး 1သိန်းကျပ် \n• ဘတ်ယူ 1000 ဘတ်\n\n"
        "လိုချင်သော ပမာဏကို ပြင်ပြီး တွက်ချက်နိုင်ပါသည်။"
    )
    bot.reply_to(message, text, parse_mode='HTML')


# --- MAIN MESSAGE ANALYZER ---
@bot.message_handler(func=lambda message: True)
def analyze_message(message):
    msg = message.text
    msg_lower = msg.lower()
    
    # 1. Skip Menu Texts (They are handled above)
    if msg in ["💰 ယခုငွေဈေး", "📱 ဖုန်းဘေဈေး", "💸 ငွေလွှဲမယ်", "📥 MWD Zay ဒေါင်းရန်", "❓ အကူအညီ"]:
        return

    # 2. Check for Amount (Calculation Trigger)
    amount = parse_amount(msg_lower)
    
    # ဂဏန်းမပါရင် (သို့) တွက်ချက်လို့မရရင် Fallback ပို့မယ်
    if not amount:
        send_fallback(message)
        return

    # 3. Data Fetching
    data = get_data()
    if not data: return # API Error fallback

    th_rate = float(data.get('thRate', 815))
    mm_rate = float(data.get('mmRate', 795))
    items = data.get('items', [])

    # 4. Determine Intent (Buying THB vs Buying MMK)
    is_thb_input = any(x in msg_lower for x in ['ဘတ်', 'b', 'thb'])
    
    # Intent Mapping
    # Buying THB (Want Baht / Give Kyat) Keywords:
    # "ကျပ်ပေး" (Give Kyat), "ဘတ်ယူ" (Take Baht), "ရမလဲ", "ဘတ်လို"
    keywords_buy_thb = ['ကျပ်ပေး', 'ဘတ်ယူ', 'ရမလဲ', 'ရလဲ', 'ဘတ်လို', 'buy', 'need']
    
    # Buying MMK (Want Kyat / Give Baht) Keywords:
    # "ဘတ်ပေး" (Give Baht), "ကျပ်ယူ" (Take Kyat)
    keywords_buy_mmk = ['ဘတ်ပေး', 'ကျပ်ယူ']

    # Logic Detection
    user_wants_thb = any(k in msg_lower for k in keywords_buy_thb)
    user_wants_mmk = any(k in msg_lower for k in keywords_buy_mmk)

    # Contextual Fallback for Plain Numbers
    if not user_wants_thb and not user_wants_mmk:
        # If user types "100000" (Kyat), usually implies Buying Baht
        if not is_thb_input: user_wants_thb = True 
        # If user types "500 B" (Baht), usually implies Selling Baht (Buying Kyat)
        else: user_wants_mmk = True

    result_text = ""

    # --- CALCULATION LOGIC ---

    # SCENARIO A: INPUT IS BAHT (Example: "500 B", "ဘတ်ပေး 500", "500 b ယူမယ်")
    if is_thb_input:
        thb_amount = amount
        
        # User WANTS Baht (Buying THB with THB Input - Rare: "I need 500 Baht")
        if user_wants_thb and not user_wants_mmk:
            calc_rate = mm_rate / 100000
            if thb_amount >= mm_rate:
                mmk_cost = thb_amount / calc_rate
                fee_msg = ""
            else:
                mmk_cost = (thb_amount + 10) / calc_rate
                fee_msg = ", Fee +10 included"
            
            mmk_clean = round(mmk_cost / 100) * 100
            result_text = (f"🇹🇭 <b>{thb_amount:,.0f} B</b> လိုချင်ရင်\n"
                           f"🇲🇲 <b>{mmk_clean:,.0f} Ks</b> ဝန်းကျင် ကျသင့်ပါမယ်။\n"
                           f"(Rate: {mm_rate}{fee_msg})")

        # User GIVES Baht (Selling THB / Buying Kyat) - Default for Baht input
        else:
            # Phone Bill Range Check
            if thb_amount <= 260:
                 if items:
                     closest_item = min(items, key=lambda x: abs(float(x['thbBill']) - thb_amount))
                     result_text = f"🇹🇭 <b>{thb_amount} B</b> ဝန်းကျင်ဆိုရင်\n🇲🇲 <b>{closest_item['mmkBill']} Ks</b> (Ph Bill Rate) ရပါမယ်ခင်ဗျာ။"
            else:
                 calc_rate = (th_rate - 5) / 100000
                 mmk_get = (thb_amount - 10) / calc_rate
                 mmk_clean = round(mmk_get / 100) * 100 
                 result_text = (f"🇹🇭 <b>{thb_amount:,.0f} B</b> ရောင်းရင်\n"
                                f"🇲🇲 <b>{mmk_clean:,.0f} Ks</b> ဝန်းကျင် ရပါမယ်ခင်ဗျာ။")

    # SCENARIO B: INPUT IS KYAT (Example: "100000", "ကျပ်ပေး 100000")
    else:
        mmk_amount = amount
        
        # User WANTS Baht (Buying THB / Giving Kyat) - Default for Kyat input
        if user_wants_thb or (not user_wants_mmk):
            # Check 10 Lakhs Logic
            rate = mm_rate
            if mmk_amount >= 10000000: rate += 5
            elif mmk_amount >= 5000000: rate += 4
            elif mmk_amount >= 3000000: rate += 3
            elif mmk_amount >= 1000000: rate += 2 # 10 Lakhs+ gets +2

            if mmk_amount < 100000:
                thb_get = ((mmk_amount / 100000) * mm_rate) - 10
                result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> (🇹🇭ဘတ်ယူ) ဆိုရင်\n🇹🇭 <b>{thb_get:,.0f} B</b> ရပါမယ်။"
            else:
                thb_get = (mmk_amount / 100000) * rate
                result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> (🇹🇭ဘတ်ယူ) ဆိုရင်\n🇹🇭 <b>{thb_get:,.2f} B</b> ရပါမယ်။\n(Rate: {rate})"
        
        # User WANTS Kyat (Selling THB / Giving Kyat Input?? - Rare: "How much is 100k Kyat worth if I sell Baht?")
        # Usually implies "ကျပ်ယူ" (Take Kyat) -> selling Baht to get this amount of Kyat
        else:
            if mmk_amount < 30000:
                found = False
                for item in items:
                    if float(item['mmkBill']) == mmk_amount:
                        result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> (Ph Bill) = <b>{item['thbBill']} B</b>"
                        found = True; break
                if not found: result_text = f"⚠️ {mmk_amount:,.0f} အတွက် ဖုန်းဘေ Package မရှိပါ။"

            elif 30000 <= mmk_amount < 100000:
                calc_rate = th_rate - 5
                thb_cost = ((mmk_amount / 100000) * calc_rate) + 10
                result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> ယူလျှင်\n🇹🇭 <b>{thb_cost:,.0f} B</b> ကျသင့်ပါမည်။"

            else:
                rate = th_rate
                # Wave Pass / Special Rate check inside calculation if keywords exist
                if 'password' in msg_lower or 'pw' in msg_lower: rate += 15
                else:
                    if mmk_amount >= 30000000: rate -= 5
                    elif mmk_amount >= 10000000: rate -= 4
                    elif mmk_amount >= 5000000: rate -= 3
                    elif mmk_amount >= 3000000: rate -= 2
                    elif mmk_amount >= 1000000: rate -= 1
                thb_cost = (mmk_amount / 100000) * rate
                result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> ယူလျှင်\n🇹🇭 <b>{thb_cost:,.2f} B</b> ကျသင့်ပါမည်။\n(Rate: {rate})"

    if result_text:
        bot.reply_to(message, result_text, parse_mode='HTML')
    else:
        send_fallback(message)

# --- RUN ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
