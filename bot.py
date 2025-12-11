import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import os
import requests
import re

# --- CONFIGURATION ---
API_TOKEN = '8392015081:AAH7kW0EtCUTQDgOLM3OEloiEJfQBjMoDec' # သင့် Token ထည့်ပါ
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
    # ကော်မာ၊ Space များကို ဖယ်ရှားခြင်း
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
        
    # ဂဏန်းသီးသန့် ဆွဲထုတ်ခြင်း
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

# --- MAIN MENU ---
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    btn1 = InlineKeyboardButton("💰 ယခုငွေဈေး", callback_data="check_rate")
    btn2 = InlineKeyboardButton("📱 ဖုန်းဘေဈေး", callback_data="check_bill")
    btn3 = InlineKeyboardButton("💸 ငွေလွှဲမယ်", callback_data="transfer")
    
    # App Link ရှာခြင်း
    data = get_data()
    link = data.get('link', 'https://play.google.com/store/apps/details?id=com.svpnmm.mmdev') if data else 'https://google.com'
    btn4 = InlineKeyboardButton("📥 Download App", url=link)
    
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ MWD Zay မှ ကြိုဆိုပါတယ်။", reply_markup=main_menu())

# --- BUTTON ACTIONS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    data = get_data()
    if not data:
        bot.answer_callback_query(call.id, "Error loading data")
        return

    th_rate = data.get('thRate', 815)
    mm_rate = data.get('mmRate', 795)

    if call.data == "check_rate":
        text = (f"📅 <b>ယခုငွေဈေးနှုန်းများ</b>\n\n"
                f"🇹🇭 <b>ကျပ်ယူ (1 သိန်း)</b> = {th_rate} ဘတ်\n"
                f"🇲🇲 <b>ဘတ်ယူ (1 သိန်း)</b> = {mm_rate} ဘတ်\n"
                f"(Wave Password/ဆိုင်ထုတ် +15)")
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')

    elif call.data == "check_bill":
        items = data.get('items', [])
        text = "📱 <b>ဖုန်းဘေဈေးနှုန်းများ</b>\n\n"
        for item in items:
            text += f"▪️ {item.get('mmkBill')} Ks = {item.get('thbBill')} B\n"
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')

    elif call.data == "transfer":
        text = f"💸 ငွေလွှဲလိုပါက Admin သို့ တိုက်ရိုက်ဆက်သွယ်နိုင်ပါသည်။\n\n👤 Admin: @{ADMIN_USERNAME}"
        bot.send_message(call.message.chat.id, text)

# --- INTELLIGENT TEXT HANDLER ---
@bot.message_handler(func=lambda message: True)
def analyze_message(message):
    msg = message.text.lower()
    data = get_data()
    
    if not data: return

    th_rate = float(data.get('thRate', 815))
    mm_rate = float(data.get('mmRate', 795))
    items = data.get('items', [])

    # ၁. စကားလုံး Keywords စစ်ဆေးခြင်း (FIXED ERROR HERE)
    keywords = ['wave acc', 'kpay acc', 'ငွေလွှဲ', 'wave password', 'ဆိုင်ထုတ်']
    if any(k in msg for k in keywords):
        
        # Wave Pass / Shop Special Rate check
        if 'password' in msg or 'ဆိုင်ထုတ်' in msg or 'pass' in msg:
             if 'ကျပ်ယူ' in msg or 'kpay' in msg or 'wave' in msg: # Buying MMK with Wave Pass
                  special_rate = th_rate + 15
                  bot.reply_to(message, f"💸 Wave Password/ဆိုင်ထုတ်ဖြင့် ကျပ်ယူပါက\n1 သိန်းလျှင် {special_rate} ဘတ် ကျသင့်ပါမည်။\n(Admin သို့ ဆက်သွယ်ရန်: @{ADMIN_USERNAME})")
                  return
             elif 'ဘတ်ယူ' in msg:
                  bot.reply_to(message, f"❌ Wave Password ဖြင့် ဘတ်ယူ၍ မရပါ။\nAdmin သို့ မေးမြန်းပါ: @{ADMIN_USERNAME}")
                  return
        
        # General Admin Contact
        bot.reply_to(message, f"💁‍♂️ ငွေလွှဲကိစ္စများအတွက် Admin ကို တိုက်ရိုက်ဆက်သွယ်ပေးပါခင်ဗျာ။\n@{ADMIN_USERNAME}")
        return

    # ဈေးမေးခြင်းများ
    if 'ဘယ်ဈေးလဲ' in msg:
        if 'ဘတ်ယူ' in msg or 'ဘတ်လိုချင်' in msg:
             bot.reply_to(message, f"🇲🇲 ဘတ်ယူ (1 သိန်း) = {mm_rate} ဘတ် ဖြစ်ပါသည်။")
        elif 'ကျပ်ယူ' in msg or 'kpay' in msg or 'wave' in msg:
             bot.reply_to(message, f"🇹🇭 ကျပ်ယူ (1 သိန်း) = {th_rate} ဘတ် ဖြစ်ပါသည်။")
        else:
             bot.reply_to(message, f"🇹🇭 ကျပ်ယူ (1 သိန်း) = {th_rate} ဘတ်\n🇲🇲 ဘတ်ယူ (1 သိန်း) = {mm_rate} ဘတ်")
        return

    # ၂. တွက်ချက်မှု Logic (Calculation)
    amount = parse_amount(msg)
    
    if amount:
        # User က "ဘတ်" လို့ ပြောလာရင် (THB Input)
        is_thb_input = any(x in msg for x in ['ဘတ်', 'b', 'thb'])
        # User က "ရမလဲ" လို့မေးရင် (Buying THB / Selling MMK)
        wants_thb = 'ရမလဲ' in msg or 'ရလဲ' in msg
        
        result_text = ""

        # SCENARIO A: User Wants MMK (Kyat) / User Inputs Kyat Amount
        if not wants_thb and not is_thb_input:
            mmk_amount = amount
            
            # --- ကျပ်ယူမည့် Logic ---
            if mmk_amount < 30000:
                # ၃ သောင်းအောက် (ဖုန်းဘေဈေး)
                found = False
                for item in items:
                    if float(item['mmkBill']) == mmk_amount:
                        result_text = f"📱 {mmk_amount:,.0f} ကျပ် (Ph Bill) = {item['thbBill']} ဘတ်"
                        found = True; break
                if not found: result_text = f"⚠️ {mmk_amount:,.0f} အတွက် ဖုန်းဘေ Package မရှိပါ။\n(ဥပမာ 1000, 3000, 5000... ရိုက်ထည့်ပါ)"

            elif 30000 <= mmk_amount < 100000:
                # ၃ သောင်း - ၁ သိန်း (Rate - 5, Fee + 10)
                calc_rate = th_rate - 5
                thb_cost = ((mmk_amount / 100000) * calc_rate) + 10
                result_text = f"💰 {mmk_amount:,.0f} ကျပ်ယူလျှင်\n✅ {thb_cost:,.0f} ဘတ် ကျသင့်ပါမည်။"

            else:
                # ၁ သိန်း နှင့်အထက် (Tiered Pricing)
                rate = th_rate
                # Wave Password Check inside calculation
                if 'password' in msg or 'pass' in msg: rate += 15
                else:
                    if mmk_amount >= 30000000: rate -= 5    # 300 Lakh
                    elif mmk_amount >= 10000000: rate -= 4  # 100 Lakh
                    elif mmk_amount >= 5000000: rate -= 3   # 50 Lakh
                    elif mmk_amount >= 3000000: rate -= 2   # 30 Lakh
                    elif mmk_amount >= 1000000: rate -= 1   # 10 Lakh
                
                thb_cost = (mmk_amount / 100000) * rate
                result_text = f"💰 {mmk_amount:,.0f} ကျပ်ယူလျှင်\n✅ {thb_cost:,.2f} ဘတ် ကျသင့်ပါမည်။\n(Rate: {rate})"

        # SCENARIO B: User Inputs THB (Reverse Calc for Kyat)
        elif not wants_thb and is_thb_input:
            thb_amount = amount
            # 260 ဘတ်အောက် (Phone Bill Reverse)
            if thb_amount <= 260:
                 # Find closest bill
                 if items:
                     closest_item = min(items, key=lambda x: abs(float(x['thbBill']) - thb_amount))
                     result_text = f"📱 {thb_amount} ဘတ်ဝန်းကျင်ဆိုရင်\n✅ {closest_item['mmkBill']} ကျပ် (Ph Bill Rate) ရပါမယ်ခင်ဗျာ။"
            else:
                 # 30k - 100k Logic Reverse: (THB - 10) / Rate * 100000
                 calc_rate = th_rate - 5
                 mmk_get = ((thb_amount - 10) / calc_rate) * 100000
                 mmk_clean = round(mmk_get / 100) * 100 
                 result_text = f"💰 {thb_amount} ဘတ် ဆိုရင်\n✅ {mmk_clean:,.0f} ကျပ်ဝန်းကျင် ရပါမယ်ခင်ဗျာ။"

        # SCENARIO C: User Wants THB (User inputs MMK and asks "ရမလဲ")
        elif wants_thb or (not is_thb_input and 'ရမလဲ' in msg):
            mmk_amount = amount
            
            # --- ဘတ်ယူမည့် Logic ---
            if mmk_amount < 100000:
                thb_get = ((mmk_amount / 100000) * mm_rate) - 10
                result_text = f"🇲🇲 {mmk_amount:,.0f} ကျပ် (ဘတ်ယူ) ဆိုရင်\n✅ {thb_get:,.0f} ဘတ် ရပါမယ်။"
            else:
                rate = mm_rate
                if mmk_amount >= 10000000: rate += 5
                elif mmk_amount >= 5000000: rate += 4
                elif mmk_amount >= 3000000: rate += 3
                elif mmk_amount >= 1000000: rate += 2
                
                thb_get = (mmk_amount / 100000) * rate
                result_text = f"🇲🇲 {mmk_amount:,.0f} ကျပ် (ဘတ်ယူ) ဆိုရင်\n✅ {thb_get:,.2f} ဘတ် ရပါမယ်။\n(Rate: {rate})"
        
        if result_text:
            bot.reply_to(message, result_text, parse_mode='HTML')

# --- RUN ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
