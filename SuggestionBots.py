token = '7793367712:AAGRXyOLyrF5v2FEzi5NawzKtFHDmJMlrtg'

import csv
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Menu: Only one option
main_menu_keyboard = [
    [KeyboardButton("💬 ثبت پیشنهاد / شکایت")]
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

# Save feedback to CSV
def save_feedback(username, message):
    with open("feedback.csv", "a", encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            username,
            message
        ])

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! خوشحال می‌شیم نظرات، پیشنهادات یا شکایت‌های خودتون رو با ما در میون بذارید 📝",
        reply_markup=main_menu_markup
    )

# Main message handler
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data
    username = update.effective_user.username or "بدون_نام‌کاربری"

    if user_data.get("feedback_mode"):
        save_feedback(username, text)
        await update.message.reply_text("✅ پیام شما با موفقیت ذخیره شد. ممنون از بازخورد شما 🙏", reply_markup=main_menu_markup)
        user_data.clear()
    elif text == "💬 ثبت پیشنهاد / شکایت":
        user_data["feedback_mode"] = True
        await update.message.reply_text("لطفاً پیشنهاد یا شکایت خود را وارد کنید:")
    else:
        await update.message.reply_text("لطفاً از منوی موجود استفاده کنید.", reply_markup=main_menu_markup)

# Error handler (optional)
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Unhandled exception:", exc_info=context.error)

# Main function
def main():
    application = Application.builder().token(token).concurrent_updates(True).read_timeout(30).write_timeout(30).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    application.add_error_handler(error_handler)
    print("Feedback-only Telegram Bot started!", flush=True)
    application.run_polling()

if __name__ == '__main__':
    main()
