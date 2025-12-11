import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import os
import requests

# --- CONFIGURATION ---
API_TOKEN = '8392015081:AAH7kW0EtCUTQDgOLM3OEloiEJfQBjMoDec' # သင့် Token ထည့်ပါ
# သင့် JSON Link အမှန်
JSON_URL = 'https://raw.githubusercontent.com/sansoe2022/mwd-web/refs/heads/main/api.json'

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

# --- HELPER FUNCTIONS ---

def get_data():
    """GitHub JSON မှ Data များကို လှမ်းယူသည့် Function"""
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error: {e}")
    return None

# --- FLASK SERVER (Render Keep-Alive) ---
@app.route('/')
def home():
    return "Bot is running with JSON API!"

def run_http():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    
    # JSON မှ App Link ကို ဆွဲထုတ်ရန် ကြိုးစားခြင်း
    data = get_data()
    app_link = data.get('link', 'https://google.com') if data else 'https://google.com'
    
    btn1 = InlineKeyboardButton("📅 Today Rate (ယနေ့ပေါက်ဈေး)", callback_data="check_rate")
    btn2 = InlineKeyboardButton("📥 Download App", url=app_link)
    markup.add(btn1, btn2)
    
    bot.reply_to(message, "မင်္ဂလာပါ! ဈေးနှုန်းကြည့်ရန် ခလုတ်ကို နှိပ်ပါ (သို့မဟုတ်) တွက်ချက်လိုသော ငွေပမာဏ (ကျပ်) ကို ရိုက်ထည့်ပါ။", reply_markup=markup)

# --- CALLBACK QUERY (Button Action) ---
@bot.callback_query_handler(func=lambda call: call.data == "check_rate")
def callback_query(call):
    data = get_data()
    if data:
        th_rate = data.get('thRate', 0)
        mm_rate = data.get('mmRate', 0)
        
        text = (
            f"📅 <b>ယနေ့ ငွေဈေးနှုန်းများ</b>\n\n"
            f"🇹🇭 <b>ကျပ်ယူ (1 သိန်း)</b> = {th_rate} ဘတ်\n"
            f"🇲🇲 <b>ဘတ်ယူ (1 သိန်း)</b> = {mm_rate} ဘတ်\n\n"
            f"💡 <i>၃ သောင်းအောက် ပမာဏများကို Phone Bill ဈေးနှုန်းဖြင့် တွက်ပေးပါမည်။</i>"
        )
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "Connection Error: ဈေးနှုန်း ဆွဲမရပါ")

# --- MESSAGE HANDLER (Calculation Logic) ---
@bot.message_handler(func=lambda message: True)
def calculate_money(message):
    user_text = message.text.strip()
    
    if user_text.isdigit():
        amount = float(user_text)
        data = get_data()
        
        if not data:
            bot.reply_to(message, "Error: ဈေးနှုန်း update မရရှိပါ။")
            return

        result_text = ""
        th_rate = float(data.get('thRate', 815)) # Default 815 if missing
        
        # --- Logic စတင်ခြင်း ---
        
        # ၁။ ပမာဏ ၁ သိန်း နှင့်အထက် (မူရင်းဈေး)
        if amount >= 100000:
            thb = (amount / 100000) * th_rate
            result_text = (
                f"💰 <b>{amount:,.0f} ကျပ်</b> အတွက်\n"
                f"✅ <b>{thb:,.2f} ဘတ်</b> ရရှိပါမယ်။\n"
                f"(Rate: {th_rate})"
            )
            
        # ၂။ ၃ သောင်း နှင့် ၁ သိန်း ကြား (ဈေး ၅ ကျပ်လျော့, Fee ၅ ဘတ်နုတ်)
        elif 30000 <= amount < 100000:
            calc_rate = th_rate - 5
            fee = 5
            thb = ((amount / 100000) * calc_rate) - fee
            
            result_text = (
                f"💰 <b>{amount:,.0f} ကျပ်</b> (1 သိန်းအောက်) အတွက်\n"
                f"✅ <b>{thb:,.2f} ဘတ်</b> ရရှိပါမယ်။\n"
                f"(Rate: {calc_rate}, Fee: -{fee} THB)"
            )
            
        # ၃။ ၃ သောင်း အောက် (Phone Bill List ထဲက ရှာမယ်)
        else:
            items = data.get('items', [])
            found = False
            
            # JSON items ထဲမှာ တိုက်ဆိုင်တာ ရှိမရှိ ရှာမယ်
            for item in items:
                # JSON ထဲမှာ string နဲ့မို့ int/float ပြောင်းစစ်ရမယ်
                bill_mmk = float(item.get('mmkBill', 0))
                bill_thb = float(item.get('thbBill', 0))
                
                if bill_mmk == amount:
                    result_text = (
                        f"📱 <b>{amount:,.0f} ကျပ် (Phone Bill)</b> အတွက်\n"
                        f"✅ <b>{bill_thb:,.0f} ဘတ်</b> ကျသင့်ပါမယ်။"
                    )
                    found = True
                    break
            
            # တိုက်ဆိုင်တာ မရှိရင် (ဥပမာ ၁၅၀၀ လိုမျိုး)
            if not found:
                 result_text = (
                    f"⚠️ <b>{amount:,.0f} ကျပ်</b> အတွက် Package မရှိပါ။\n"
                    f"ကျေးဇူးပြု၍ သတ်မှတ်ထားသော ပမာဏများကိုသာ ရိုက်ထည့်ပါ\n"
                    f"(ဥပမာ - 1000, 3000, 5000, 10000...)"
                )

        bot.reply_to(message, result_text, parse_mode='HTML')

    else:
        # ဂဏန်းမဟုတ်ရင် ဘာမှ မလုပ်ပါ
        pass

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
