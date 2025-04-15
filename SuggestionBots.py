token = '7793367712:AAGRXyOLyrF5v2FEzi5NawzKtFHDmJMlrtg'

import os
import csv
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# ==== Setup ====
# Universal feedback file path (local = data/, Render = /tmp/data/)
if os.environ.get('RENDER') == 'true':  # You can set this manually in Render env vars if needed
    FEEDBACK_DIR = "/tmp/data"
else:
    FEEDBACK_DIR = "data"

FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback.csv")
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# ==== Menu ====
main_menu_keyboard = [
    [KeyboardButton("🍽 پیشنهاد برای شام")],
    [KeyboardButton("🎲 پیشنهاد بازی جدید")],
    [KeyboardButton("💬 سایر پیشنهادات / شکایات")]
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

# ==== Save Feedback ====
def save_feedback(username, category, message):
    with open(FEEDBACK_FILE, "a", encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            username,
            category,
            message
        ])
    print(f"✅ Feedback saved to: {FEEDBACK_FILE}")

# ==== /start ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=main_menu_markup
    )

# ==== Main message handler ====
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data
    username = update.effective_user.username or "بدون‌نام‌کاربری"

    if user_data.get("feedback_mode"):
        category = user_data["feedback_mode"]
        save_feedback(username, category, text)

        if category == "Dinner":
            await update.message.reply_text("ممنون بابت پیشنهاد خوشمزه‌ات! 😋", reply_markup=main_menu_markup)
        elif category == "Game":
            await update.message.reply_text("مرسی! این بازی رو بررسی می‌کنیم تا شادی‌مون بیشتر شه 🎉", reply_markup=main_menu_markup)
        elif category == "General":
            await update.message.reply_text("از پیام شما سپاسگزاریم. تیم ما بررسی خواهد کرد. 🙏", reply_markup=main_menu_markup)

        user_data.clear()
        return

    if text == "🍽 پیشنهاد برای شام":
        user_data["feedback_mode"] = "Dinner"
        await update.message.reply_text("چه غذایی دوست دارید در برنامه برای شام سرو شود؟")
    elif text == "🎲 پیشنهاد بازی جدید":
        user_data["feedback_mode"] = "Game"
        await update.message.reply_text("چه بازی سرگرم‌کننده‌ای پیشنهاد می‌کنید به جمع‌مون اضافه کنیم؟")
    elif text == "💬 سایر پیشنهادات / شکایات":
        user_data["feedback_mode"] = "General"
        await update.message.reply_text("لطفاً پیشنهاد یا شکایت خود را وارد کنید:")
    else:
        await update.message.reply_text("لطفاً یکی از گزینه‌های منو را انتخاب کنید.", reply_markup=main_menu_markup)

# ==== Error logger ====
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Unhandled exception:", exc_info=context.error)

# ==== Main app ====
def main():
    application = Application.builder().token(token).concurrent_updates(True).read_timeout(30).write_timeout(30).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    application.add_error_handler(error_handler)
    print("Telegram Bot started!", flush=True)
    application.run_polling()

if __name__ == '__main__':
    main()
