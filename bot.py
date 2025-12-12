import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread
import os
import requests
import re

# --- CONFIGURATION ---
# ⚠️ ဒီနေရာမှာ မိတ်ဆွေရဲ့ Token အမှန်ကို ပြန်ထည့်ပါ
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
    markup.add("💰 ယခုငွေဈေး", "📱 ဖုန်းဘေဈေး", "💸 ငွေလွှဲမယ်", "📥 MWD Zay ဒေါင်းရန်")
    return markup

# --- COMMAND HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "မင်္ဂလာပါ MWD Zay Bot မှ ကြိုဆိုပါတယ်။", reply_markup=get_reply_menu())

# --- MENU ACTIONS ---
@bot.message_handler(func=lambda message: message.text == "💰 ယခုငွေဈေး")
def menu_rate(message):
    data = get_data()
    if data:
        th_rate = data.get('thRate', 815)
        mm_rate = data.get('mmRate', 795)
        text = (f"📅 <b>ယခုငွေဈေး</b>\n\n"
                f"🇹🇭➡️🇲🇲 <b>ဘတ်ပေးကျပ်ယူ (1 သိန်း)</b> = {th_rate} ဘတ်\n"
                f"🇲🇲➡️🇹🇭 <b>ကျပ်ပေးဘတ်ယူ (1 သိန်း)</b> = {mm_rate} ဘတ်\n"
                )
        bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "📱 ဖုန်းဘေဈေး")
def menu_bill(message):
    data = get_data()
    if data:
        items = data.get('items', [])
        text = "📱 <b>ဖုန်းဘေဈေးနှုန်းများ</b>\n\n"
        for item in items:
            text += f"🇲🇲 {item.get('mmkBill')} Ks = 🇹🇭 {item.get('thbBill')} B\n"
        bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "💸 ငွေလွှဲမယ်")
def menu_transfer(message):
    text = f"💸 ငွေလွှဲလိုပါက Admin သို့ တိုက်ရိုက်ဆက်သွယ်နိုင်ပါသည်။\n\n👤 Admin: @{ADMIN_USERNAME}"
    bot.reply_to(message, text)

@bot.message_handler(func=lambda message: message.text == "📥 MWD Zay ဒေါင်းရန်")
def menu_download(message):
    data = get_data()
    link = data.get('link', 'https://play.google.com/store/apps/details?id=com.sksdev.mwdcalculator') if data else 'https://google.com'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📥 Click here to Download", url=link))
    bot.reply_to(message, "အောက်ပါ Button ကို နှိပ်၍ MWD Zayကို Download ရယူနိုင်ပါတယ်ခင်ဗျာ။", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "check_rate": menu_rate(call.message)
    elif call.data == "check_bill": menu_bill(call.message)
    elif call.data == "transfer": menu_transfer(call.message)

# --- CALCULATION LOGIC & FALLBACK ---
@bot.message_handler(func=lambda message: True)
def analyze_message(message):
    msg = message.text.lower()
    
    # Skip Menu Texts
    if msg in ["💰 ယခုငွေဈေး", "📱 ဖုန်းဘေဈေး", "💸 ငွေလွှဲမယ်", "📥 mwd zay ဒေါင်းရန်"]:
        return

    data = get_data()
    # Data မရလျှင် ဘာမှမလုပ်ပါ (Error တက်ခြင်းမှ ကာကွယ်ရန်)
    if not data: return

    th_rate = float(data.get('thRate', 815)) # User Selling THB (Giving Baht -> Taking Kyat)
    mm_rate = float(data.get('mmRate', 795)) # User Buying THB (Giving Kyat -> Taking Baht)
    items = data.get('items', [])

    # Keywords Detection
    keywords = ['wave acc', 'kpay acc', 'ငွေလွှဲ', 'wave password', 'ဆိုင်ထုတ်']
    if any(k in msg for k in keywords):
        if 'password' in msg or 'ဆိုင်ထုတ်' in msg or 'pass' in msg:
             if 'ကျပ်ယူ' in msg or 'kpay' in msg or 'wave' in msg:
                  special_rate = th_rate + 15
                  bot.reply_to(message, f"💸 Wave Password/ဆိုင်ထုတ်ဖြင့် ကျပ်ယူပါက\n1 သိန်းလျှင် {special_rate} ဘတ် ကျသင့်ပါမည်။\n(Admin သို့ ဆက်သွယ်ရန်: @{ADMIN_USERNAME})")
                  return
             elif 'ဘတ်ယူ' in msg:
                  bot.reply_to(message, f"❌ Wave Password ဖြင့် ဘတ်ယူ၍ မရပါ။\nAdmin သို့ မေးမြန်းပါ: @{ADMIN_USERNAME}")
                  return
        bot.reply_to(message, f"💁‍♂️ ငွေလွှဲကိစ္စများအတွက် Admin ကို တိုက်ရိုက်ဆက်သွယ်ပေးပါခင်ဗျာ။\n@{ADMIN_USERNAME}")
        return
        
    # Rate Inquiry
    if 'ဘယ်ဈေးလဲ' in msg:
         bot.reply_to(message, f"🇹🇭 ကျပ်ယူ (1 သိန်း) = {th_rate} ဘတ်\n🇲🇲 ဘတ်ယူ (1 သိန်း) = {mm_rate} ဘတ်")
         return

    # --- CALCULATION CORE ---
    amount = parse_amount(msg)
    
    # အကယ်၍ ဂဏန်းပါဝင်ပြီး ငွေပမာဏတစ်ခုခု ဖြစ်နေလျှင် တွက်ပေးမည်
    if amount:
        # Check Currency Type
        is_thb_input = any(x in msg for x in ['ဘတ်', 'b', 'thb'])
        
        # Check Intention
        is_buying_thb = any(x in msg for x in ['ပေး', 'ယူ', 'buy', 'need', 'လို']) 
        
        result_text = ""

        # ==========================================
        # CASE 1: INPUT IS BAHT (e.g., "500 Baht")
        # ==========================================
        if is_thb_input:
            thb_amount = amount
            
            # Sub-case 1A: User WANTS Baht (Buying THB)
            # Example: "1500 B ယူမယ်"
            if is_buying_thb: 
                calc_rate = mm_rate / 100000
                
                # Logic: 1 သိန်း (795 ဘတ်) နှင့်အထက်ဆိုလျှင် +10 မပေါင်း
                if thb_amount >= mm_rate:
                    mmk_cost = thb_amount / calc_rate
                    fee_msg = ""
                else:
                    mmk_cost = (thb_amount + 10) / calc_rate
                    fee_msg = ", Fee +10 included"

                mmk_clean = round(mmk_cost / 100) * 100
                
                result_text = (f"🇲🇲 <b>{thb_amount:,.0f} B</b> လိုချင်ရင်\n"
                               f"✅ <b>{mmk_clean:,.0f} Ks</b> ဝန်းကျင် ကျသင့်ပါမယ်။\n"
                               f"(Rate: {mm_rate}{fee_msg})")

            # Sub-case 1B: User HAS Baht (Selling THB)
            # Example: "500 B" or "500 B ရောင်းမယ်"
            else:
                if thb_amount <= 260:
                     if items:
                         closest_item = min(items, key=lambda x: abs(float(x['thbBill']) - thb_amount))
                         result_text = f"📱 <b>{thb_amount} B</b> ဝန်းကျင်ဆိုရင်\n✅ <b>{closest_item['mmkBill']} Ks</b> (Ph Bill Rate) ရပါမယ်ခင်ဗျာ။"
                else:
                     calc_rate = (th_rate - 5) / 100000
                     mmk_get = (thb_amount - 10) / calc_rate
                     mmk_clean = round(mmk_get / 100) * 100 
                     result_text = (f"💰 <b>{thb_amount:,.0f} B</b> ရောင်းရင်\n"
                                    f"✅ <b>{mmk_clean:,.0f} Ks</b> ဝန်းကျင် ရပါမယ်ခင်ဗျာ။")

        # ==========================================
        # CASE 2: INPUT IS KYAT (e.g., "50000", "1သိန်း")
        # ==========================================
        else:
            mmk_amount = amount
            
            # Sub-case 2A: User WANTS THB (Buying THB)
            # Example: "1သိန်း ဘတ်လိုချင်" or "100000 ရမလဲ"
            wants_thb_context = any(x in msg for x in ['ရမလဲ', 'ရလဲ', 'ဘတ်ယူ', 'လို'])

            if wants_thb_context:
                if mmk_amount < 100000:
                    thb_get = ((mmk_amount / 100000) * mm_rate) - 10
                    result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> (ဘတ်ယူ) ဆိုရင်\n✅ <b>{thb_get:,.0f} B</b> ရပါမယ်။"
                else:
                    rate = mm_rate
                    # Tiered Rates for Large Amounts
                    if mmk_amount >= 10000000: rate += 5
                    elif mmk_amount >= 5000000: rate += 4
                    elif mmk_amount >= 3000000: rate += 3
                    elif mmk_amount >= 1000000: rate += 2
                    
                    thb_get = (mmk_amount / 100000) * rate
                    result_text = f"🇲🇲 <b>{mmk_amount:,.0f} Ks</b> (ဘတ်ယူ) ဆိုရင်\n✅ <b>{thb_get:,.2f} B</b> ရပါမယ်။\n(Rate: {rate})"
            
            # Sub-case 2B: User WANTS Kyat (Selling THB implied - Default for Kyat input)
            # Example: "100000" or "5000"
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
                    if 'password' in msg or 'pass' in msg: rate += 15
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
            # Calculation မလုပ်နိုင်သော်လည်း amount ပါနေလျှင် (Fallback for Logic holes)
             bot.reply_to(message, f"ကျွန်တော်က ငွေစျေးတွက်ပေးတဲ့ bot ဖြစ်ပါတယ် တခြားအကြောင်းအရာတွေ မဖြေဆိုနိုင်ပါခင်ဗျာ ငွေစျေး အသေးစိတ်သိလိုပါက Admin ကို တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ @{ADMIN_USERNAME}")

    else:
        # --- FALLBACK MESSAGE (Amount မပါ၊ Keyword မပါသော စာများအတွက်) ---
        bot.reply_to(message, f"ကျွန်တော်က ငွေစျေးတွက်ပေးတဲ့ bot ဖြစ်ပါတယ် တခြားအကြောင်းအရာတွေ မဖြေဆိုနိုင်ပါခင်ဗျာ ငွေစျေး အသေးစိတ်သိလိုပါက Admin ကို တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ @{ADMIN_USERNAME}")

# --- RUN ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
