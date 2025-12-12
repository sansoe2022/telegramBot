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
    # Menu 5 ခု ဖြစ်သွားပါပြီ ("အကူအညီ" အသစ်တိုးထားသည်)
    markup.add("💰 ယခုငွေဈေး", "📱 ဖုန်းဘေဈေး", "💸 ငွေလွှဲမယ်", "📥 MWD Zay ဒေါင်းရန်", "❓ အကူအညီ")
    return markup

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
                f"🇹🇭➡️🇲🇲 <b>ဘတ်ပေးကျပ်ယူစျေး (1 သိန်းကျပ်)</b> = {th_rate} ဘတ်\n"
                f"🇲🇲➡️🇹🇭 <b>ကျပ်ပေးဘတ်ယူစျေး (1 သိန်းကျပ်)</b> = {mm_rate} ဘတ်\n")
        bot.reply_to(message, text, parse_mode='HTML')

# 2. ဖုန်းဘေဈေး
@bot.message_handler(func=lambda message: message.text == "📱 ဖုန်းဘေဈေး")
def menu_bill(message):
    data = get_data()
    if data:
        items = data.get('items', [])
        text = "📱 <b>ဖုန်းဘေဈေးနှုန်းများ</b>\n\n"
        for item in items:
            text += f"🇲🇲 {item.get('mmkBill')} Ks = 🇹🇭 {item.get('thbBill')} B\n"
        bot.reply_to(message, text, parse_mode='HTML')

# 3. ငွေလွှဲမယ် (Button ပါသော VERSION အသစ်)
@bot.message_handler(func=lambda message: message.text == "💸 ငွေလွှဲမယ်")
def menu_transfer(message):
    text = "ငွေလွှဲလိုပါက Adminကို တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်"
    markup = InlineKeyboardMarkup()
    # Admin Link Button
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

# 5. အကူအညီ (MENU အသစ်)
@bot.message_handler(func=lambda message: message.text == "❓ အကူအညီ")
def menu_help(message):
    text = (
        "<b>အသုံးပြုပုံ လမ်းညွှန်</b>\n\n"
        "🇲🇲 <b>ကျပ်ငွေလိုချင်ပါက</b>\n"
        "<code>/ကျပ်ယူ 100000</code> သို့မဟုတ် <code>/ကျပ်ယူ 500ဘတ်</code>\n"
        "လို့ ရေးပေးပါခင်ဗျာ။\n\n"
        "🇹🇭 <b>ဘတ်ငွေလိုချင်ပါက</b>\n"
        "<code>/ဘတ်ယူ 100000</code> သို့မဟုတ် <code>/ဘတ်ယူ 500ဘတ်</code>\n"
        "လို့ ရေးပေးပါခင်ဗျာ။"
    )
    bot.reply_to(message, text, parse_mode='HTML')

# --- COMMAND BASED CALCULATION (/ကျပ်ယူ & /ဘတ်ယူ) ---
@bot.message_handler(commands=['ကျပ်ယူ', 'ဘတ်ယူ'])
def command_calculation(message):
    msg = message.text
    command = msg.split()[0] # /ကျပ်ယူ or /ဘတ်ယူ
    
    # Command နောက်က စာသားကို ယူမည် (ဥပမာ: "100000" or "500ဘတ်")
    content = msg.replace(command, "").strip()
    
    if not content:
        bot.reply_to(message, "ကျေးဇူးပြု၍ ပမာဏတစ်ခုခု ရေးပေးပါ\n(ဥပမာ: /ကျပ်ယူ 1သိန်း)")
        return

    # Check Intention based on command
    is_buying_mmk = (command == "/ကျပ်ယူ") # User wants Kyat
    is_buying_thb = (command == "/ဘတ်ယူ") # User wants Baht
    
    # Process Calculation
    process_calculation(message, content, force_buy_mmk=is_buying_mmk, force_buy_thb=is_buying_thb)


# --- GENERAL TEXT ANALYZER ---
@bot.message_handler(func=lambda message: True)
def analyze_message(message):
    msg = message.text
    
    # Skip Menu Texts
    if msg in ["💰 ယခုငွေဈေး", "📱 ဖုန်းဘေဈေး", "💸 ငွေလွှဲမယ်", "📥 MWD Zay ဒေါင်းရန်", "❓ အကူအညီ"]:
        return

    # Fallback to general calculation
    process_calculation(message, msg)


# --- CORE CALCULATION FUNCTION ---
def process_calculation(message, text_content, force_buy_mmk=False, force_buy_thb=False):
    data = get_data()
    if not data: return

    th_rate = float(data.get('thRate', 815))
    mm_rate = float(data.get('mmRate', 795))
    items = data.get('items', [])

    msg_lower = text_content.lower()

    # Keywords Detection
    keywords = ['wave acc', 'kpay acc', 'ငွေလွှဲ', 'wave password', 'ဆိုင်ထုတ်']
    if any(k in msg_lower for k in keywords):
        if 'password' in msg_lower or 'ဆိုင်ထုတ်' in msg_lower or 'pass' in msg_lower:
             if 'ကျပ်ယူ' in msg_lower or 'kpay' in msg_lower or 'wave' in msg_lower:
                  special_rate = th_rate + 15
                  bot.reply_to(message, f"💸 Wave Password/ဆိုင်ထုတ်ဖြင့် ကျပ်ယူပါက\n1 သိန်းလျှင် {special_rate} ဘတ် ကျသင့်ပါမည်။\n(Admin သို့ ဆက်သွယ်ရန်: @{ADMIN_USERNAME})")
                  return
             elif 'ဘတ်ယူ' in msg_lower:
                  bot.reply_to(message, f"❌ Wave Password ဖြင့် ဘတ်ယူ၍ မရပါ။\nAdmin သို့ မေးမြန်းပါ: @{ADMIN_USERNAME}")
                  return
        bot.reply_to(message, f"💁‍♂️ ငွေလွှဲကိစ္စများအတွက် Admin ကို တိုက်ရိုက်ဆက်သွယ်ပေးပါခင်ဗျာ။\n@{ADMIN_USERNAME}")
        return
        
    if 'ဘယ်ဈေးလဲ' in msg_lower:
         bot.reply_to(message, f"🇹🇭 ကျပ်ယူ (1 သိန်း) = {th_rate} ဘတ်\n🇲🇲 ဘတ်ယူ (1 သိန်း) = {mm_rate} ဘတ်")
         return

    amount = parse_amount(msg_lower)
    
    if amount:
        is_thb_input = any(x in msg_lower for x in ['ဘတ်', 'b', 'thb'])
        
        # Determine Intention (If forced by command, use that. Else detect from text)
        buying_thb = force_buy_thb or (not force_buy_mmk and any(x in msg_lower for x in ['ရမလဲ', 'ရလဲ', 'ဘတ်ယူ', 'လို']))
        buying_mmk = force_buy_mmk or (not force_buy_thb and (is_thb_input and not buying_thb)) # Giving Baht to get Kyat

        result_text = ""

        # --- LOGIC START ---

        # 1. INPUT IS BAHT
        if is_thb_input:
            thb_amount = amount
            
            # Buying THB with THB input? (Rare, usually means "I want 500 Baht")
            # Logic: Input Baht -> Output Kyat Cost
            if buying_thb: 
                # Formula: (Baht + 10) / Rate (mmRate)
                calc_rate = mm_rate / 100000
                if thb_amount >= mm_rate: # 1 Lakh equivalent
                    mmk_cost = thb_amount / calc_rate
                    fee_msg = ""
                else:
                    mmk_cost = (thb_amount + 10) / calc_rate
                    fee_msg = ", Fee +10 included"
                
                mmk_clean = round(mmk_cost / 100) * 100
                result_text = (f"🇹🇭 <b>{thb_amount:,.0f} B</b> လိုချင်ရင်\n"
                               f"✅ <b>{mmk_clean:,.0f} Ks</b> ဝန်းကျင် ကျသင့်ပါမယ်။\n"
                               f"(Rate: {mm_rate}{fee_msg})")

            # Selling THB (Input Baht -> Get Kyat)
            else:
                if thb_amount <= 260:
                     if items:
                         closest_item = min(items, key=lambda x: abs(float(x['thbBill']) - thb_amount))
                         result_text = f"📱 <b>{thb_amount} B</b> ဝန်းကျင်ဆိုရင်\n✅ <b>{closest_item['mmkBill']} Ks</b> (Ph Bill Rate) ရပါမယ်ခင်ဗျာ။"
                else:
                     calc_rate = (th_rate - 5) / 100000
                     mmk_get = (thb_amount - 10) / calc_rate
                     mmk_clean = round(mmk_get / 100) * 100 
                     result_text = (f"🇹🇭 <b>{thb_amount:,.0f} B</b> ရောင်းရင်\n"
                                    f"✅ <b>{mmk_clean:,.0f} Ks</b> ဝန်းကျင် ရပါမယ်ခင်ဗျာ။")

        # 2. INPUT IS KYAT
        else:
            mmk_amount = amount
            
            # Buying THB (Input Kyat -> Get Baht)
            if buying_thb:
                if mmk_amount < 100000:
                    thb_get = ((mmk_amount / 100000) * mm_rate) - 10
                    result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> (ဘတ်ယူ) ဆိုရင်\n✅ <b>{thb_get:,.0f} B</b> ရပါမယ်။"
                else:
                    rate = mm_rate
                    if mmk_amount >= 10000000: rate += 5
                    elif mmk_amount >= 5000000: rate += 4
                    elif mmk_amount >= 3000000: rate += 3
                    elif mmk_amount >= 1000000: rate += 2
                    thb_get = (mmk_amount / 100000) * rate
                    result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> (ဘတ်ယူ) ဆိုရင်\n✅ <b>{thb_get:,.2f} B</b> ရပါမယ်။\n(Rate: {rate})"
            
            # Selling THB (Buying Kyat / Input Kyat -> Pay Baht)
            else:
                if mmk_amount < 30000:
                    found = False
                    for item in items:
                        if float(item['mmkBill']) == mmk_amount:
                            result_text = f"📱 <b>{mmk_amount:,.0f} Ks</b> (Ph Bill) = <b>{item['thbBill']} B</b>"
                            found = True; break
                    if not found: result_text = f"⚠️ {mmk_amount:,.0f} အတွက် ဖုန်းဘေ Package မရှိပါ။"

                elif 30000 <= mmk_amount < 100000:
                    calc_rate = th_rate - 5
                    thb_cost = ((mmk_amount / 100000) * calc_rate) + 10
                    result_text = f"💰 <b>{mmk_amount:,.0f} Ks</b> ယူလျှင်\n✅ <b>{thb_cost:,.0f} B</b> ကျသင့်ပါမည်။"

                else:
                    rate = th_rate
                    if 'password' in msg_lower or 'pass' in msg_lower: rate += 15
                    else:
                        if mmk_amount >= 30000000: rate -= 5
                        elif mmk_amount >= 10000000: rate -= 4
                        elif mmk_amount >= 5000000: rate -= 3
                        elif mmk_amount >= 3000000: rate -= 2
                        elif mmk_amount >= 1000000: rate -= 1
                    thb_cost = (mmk_amount / 100000) * rate
                    result_text = f"💰 <b>{mmk_amount:,.0f} Ks</b> ယူလျှင်\n✅ <b>{thb_cost:,.2f} B</b> ကျသင့်ပါမည်။\n(Rate: {rate})"

        if result_text:
            bot.reply_to(message, result_text, parse_mode='HTML')
        else:
             bot.reply_to(message, f"ကျွန်တော်က ငွေစျေးတွက်ပေးတဲ့ bot ဖြစ်ပါတယ် တခြားအကြောင်းအရာတွေ မဖြေဆိုနိုင်ပါခင်ဗျာ ငွေစျေး အသေးစိတ်သိလိုပါက Admin ကို တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ @{ADMIN_USERNAME}")

    else:
        # Fallback for non-amount text
        bot.reply_to(message, f"ကျွန်တော်က ငွေစျေးတွက်ပေးတဲ့ bot ဖြစ်ပါတယ် တခြားအကြောင်းအရာတွေ မဖြေဆိုနိုင်ပါခင်ဗျာ ငွေစျေး အသေးစိတ်သိလိုပါက Admin ကို တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ @{ADMIN_USERNAME}")

# --- RUN ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
