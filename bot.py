import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import os

# Telegram Bot Setup
API_TOKEN = '8392015081:AAH7kW0EtCUTQDgOLM3OEloiEJfQBjMoDec' # သင့် Token ထည့်ပါ
bot = telebot.TeleBot(API_TOKEN)

# --- FLASK SERVER SETUP (Render အတွက်) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run_http():
    # Render က ပေးတဲ့ Port ကို ယူသုံးမယ်၊ မရှိရင် 8080 ကိုသုံးမယ်
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run_http)
    t.start()
# ---------------------------------------

# Bot Commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    btn1 = InlineKeyboardButton("Download App", url="https://play.google.com/store/apps/details?id=com.sksdev.mwdcalculator")
    btn2 = InlineKeyboardButton("Contact Admin", url="https://t.me/sansoe2021")
    markup.add(btn1, btn2)
    bot.reply_to(message, "မင်္ဂလာပါ! ကြိုဆိုပါတယ်", reply_markup=markup)

# Main Execution
if __name__ == "__main__":
    keep_alive()  # Web Server ကို အရင် run မယ်
    print("Bot is running...")
    bot.infinity_polling() # ပြီးမှ Bot ကို run မယ်
