import telebot
import json
import os
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7538234149:AAHwNSjd28Toog9CPh2Ez6mHQCgNfyaOwWo"
ADMIN_ID = 123456789  # Ganti dengan ID Telegram kamu
bot = telebot.TeleBot(TOKEN)
DATA_FILE = "users.json"
QR_IMAGE = "qris_aan_store.jpg"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    users = load_users()
    uid = str(message.from_user.id)
    if uid not in users:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Sudah Bayar", callback_data="sudah_bayar"))
        bot.send_photo(message.chat.id, open(QR_IMAGE, "rb"),
            caption="🔐 Untuk akses bot, silakan scan QRIS dan bayar.
Nama: *Aan Store*",
            reply_markup=markup, parse_mode="Markdown")
        return
    bot.send_message(message.chat.id, "✅ Akses diterima.
Kirim multiplier untuk prediksi.")

@bot.callback_query_handler(func=lambda call: call.data == "sudah_bayar")
def handle_payment(call):
    user = call.from_user
    text = f"💰 *User Bayar*
Nama: `{user.first_name}`
ID: `{user.id}`
Username: @{user.username}"
    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    bot.answer_callback_query(call.id, "Admin akan segera mengaktifkan akses.")

@bot.message_handler(commands=["aktifkan"])
def activate_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Gunakan: /aktifkan user_id")
        return
    uid = parts[1]
    users = load_users()
    users[uid] = {"active": True, "since": str(datetime.now())}
    save_users(users)
    bot.reply_to(message, f"✅ User {uid} diaktifkan.")

@bot.message_handler(commands=["penyewa"])
def list_users(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    if not users:
        bot.send_message(message.chat.id, "Belum ada penyewa.")
        return
    text = "📋 Daftar Penyewa:
"
    for uid, info in users.items():
        text += f"- `{uid}` sejak {info.get('since')}
"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text.replace('.', '', 1).isdigit())
def prediksi_handler(message):
    uid = str(message.from_user.id)
    users = load_users()
    if uid not in users:
        bot.send_message(message.chat.id, "🔒 Akses ditolak. Silakan bayar dulu.")
        return
    try:
        nilai = float(message.text)
        import random
        prediksi = random.choices(["🟢 Aman", "🔴 Crash"], weights=[0.7, 0.3])[0]
        winrate = random.randint(68, 93)
        bot.reply_to(message, f"🎯 Prediksi untuk {nilai}x:
{prediksi}
📈 Winrate: {winrate}%")
    except:
        bot.reply_to(message, "Format tidak dikenali. Kirim multiplier saja.")

bot.infinity_polling()
