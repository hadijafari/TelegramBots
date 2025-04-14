
token = '7793367712:AAGRXyOLyrF5v2FEzi5NawzKtFHDmJMlrtg'

import csv
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

# Optional: enable logging
logging.basicConfig(level=logging.INFO)

# Main menu
main_menu_keyboard = [
    [KeyboardButton("📅 مشاهده رویدادهای آینده")],
    [KeyboardButton("☎️ تماس با پشتیبانی")],
    [KeyboardButton("ℹ️ درباره ما")],
    [KeyboardButton("❌ لغو")]
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

# Events submenu
events_menu_keyboard = [
    [KeyboardButton("🎉 رویداد 1")],
    [KeyboardButton("🎲 رویداد 2")],
    [KeyboardButton("🎤 رویداد 3")],
    [KeyboardButton("🔙 بازگشت به منو")]
]
events_menu_markup = ReplyKeyboardMarkup(events_menu_keyboard, resize_keyboard=True)

# Confirmation buttons
register_keyboard = [
    [KeyboardButton("✅ بله"), KeyboardButton("❌ خیر")]
]
register_markup = ReplyKeyboardMarkup(register_keyboard, resize_keyboard=True)

# Costs
ADULT_COST = 13
CHILD_COST = 9
DISCOUNT_THRESHOLD = 3
DISCOUNT_PERCENT = 10

# Event details with working placeholder images
event_details = {
    "🎉 رویداد 1": {
        "photo": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Boardgame.jpg",
        "description": """سلام!

اولین برنامه‌ای که بعد از ورودمون به استرالیا رفتیم و یک جمع ایرانی گرم دیدیم، «گیم‌نایت» خانواده شاد بود.

بازی‌های متنوع برای همه سنین + شام، دسر و کلی خوش‌گذرونی!

🗓 شنبه ۱۲ اپریل ۲۰۲۵
⏰ ۱۸:۳۰ تا ۲۲
📍 72 Luckie Street, Nunawading
💵 بزرگسال ۱۳$، کودک ۹$
"""
    },
    "🎲 رویداد 2": {
        "photo": "https://upload.wikimedia.org/wikipedia/commons/7/70/Board_Game_Night.jpg",
        "description": """🎲 مسابقه بوردگیم با جوایز جذاب!

📅 جمعه ۱۹ اپریل
🕕 ۱۷ تا ۲۱
🏠 Book Cafe Melbourne
💰 ۱۵ دلار (با پذیرایی)
"""
    },
    "🎤 رویداد 3": {
        "photo": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Music_Performance.jpg",
        "description": """🎤 شب شعر و موسیقی ایرانی

📅 پنج‌شنبه ۲۵ اپریل
🕖 ۱۹ تا ۲۳
🏠 Persian Hall - Melbourne
💵 ۱۰ دلار (با چای و کیک)
"""
    }
}

# Save registration to CSV
def save_registration(username, event, adults, children, total):
    with open("registrations.csv", "a", encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            username,
            event,
            adults,
            children,
            total
        ])

# Start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به ربات خوش اومدی 😊\nاز منوی زیر گزینه مورد نظرت رو انتخاب کن:",
        reply_markup=main_menu_markup
    )

# Reply handler
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data
    username = update.effective_user.username or "بدون_نام‌کاربری"

    if user_data.get("registering_step") == "awaiting_adults":
        if text.isdigit():
            user_data["adults"] = int(text)
            user_data["registering_step"] = "awaiting_children"
            await update.message.reply_text("چند کودک (۳ تا ۷ سال) هستید؟")
        else:
            await update.message.reply_text("لطفاً فقط یک عدد وارد کنید (مثلاً: 2)")

    elif user_data.get("registering_step") == "awaiting_children":
        if text.isdigit():
            user_data["children"] = int(text)
            adults = user_data["adults"]
            children = user_data["children"]

            total_price = adults * ADULT_COST + children * CHILD_COST
            if adults >= DISCOUNT_THRESHOLD:
                discount = total_price * DISCOUNT_PERCENT / 100
                total_price -= discount
                discount_note = f"(با {DISCOUNT_PERCENT}٪ تخفیف برای بیش از {DISCOUNT_THRESHOLD} بزرگسال)"
            else:
                discount_note = ""

            save_registration(username, user_data['selected_event'], adults, children, total_price)

            await update.message.reply_text(
                f"""✅ خلاصه ثبت‌نام:

رویداد: {user_data['selected_event']}
تعداد بزرگسال: {adults}
تعداد کودک: {children}
💰 مبلغ قابل پرداخت: {total_price:.2f} دلار {discount_note}

💳 لطفاً مبلغ بالا را به شماره کارت زیر واریز کنید:
6037-9911-2345-6789
به نام: جامعه ایرانیان

و سپس رسید پرداخت را به پشتیبانی ارسال نمایید:
@SupportYourBot
""",
                reply_markup=main_menu_markup
            )

            user_data.clear()
        else:
            await update.message.reply_text("لطفاً فقط یک عدد وارد کنید (مثلاً: 1 یا 0)")

    elif text == "📅 مشاهده رویدادهای آینده":
        await update.message.reply_text("لطفاً یکی از رویدادهای زیر را انتخاب کنید:", reply_markup=events_menu_markup)

    elif text in event_details:
        event = event_details[text]
        user_data["selected_event"] = text
        try:
            await update.message.reply_photo(
                photo=event["photo"],
                caption=event["description"]
            )
        except Exception as e:
            logging.error(f"خطا در ارسال عکس: {e}")
            await update.message.reply_text(event["description"])
        await update.message.reply_text("آیا مایل به ثبت‌نام در این رویداد هستید؟", reply_markup=register_markup)

    elif text == "✅ بله":
        if "selected_event" in user_data:
            user_data["registering_step"] = "awaiting_adults"
            await update.message.reply_text("چند نفر بزرگسال هستید؟")
        else:
            await update.message.reply_text("لطفاً ابتدا یک رویداد را انتخاب کنید.", reply_markup=main_menu_markup)

    elif text == "❌ خیر":
        await update.message.reply_text("ثبت‌نام لغو شد. برای ادامه از منوی اصلی استفاده کن.", reply_markup=main_menu_markup)
        user_data.clear()

    elif text == "☎️ تماس با پشتیبانی":
        await update.message.reply_text("برای تماس با پشتیبانی، لطفاً به آیدی زیر پیام دهید:\n@SupportYourBot")

    elif text == "ℹ️ درباره ما":
        await update.message.reply_text("ما یک جامعه ایرانی فعال در ملبورن هستیم که با برگزاری رویدادهای فرهنگی، تفریحی و آموزشی، به دنبال ایجاد فضای دوستی و یادگیری هستیم.")

    elif text == "❌ لغو" or text == "🔙 بازگشت به منو":
        await update.message.reply_text("به منوی اصلی برگشتید.", reply_markup=main_menu_markup)
        user_data.clear()

    else:
        await update.message.reply_text("لطفاً از گزینه‌های منو استفاده کنید.", reply_markup=main_menu_markup)

# Error handler (optional, to catch any crash info)
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Unhandled exception:", exc_info=context.error)

# Main runner
def main():
    application = Application.builder().token(token).concurrent_updates(True).read_timeout(30).write_timeout(30).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    application.add_error_handler(error_handler)
    print("Telegram Bot started!", flush=True)
    application.run_polling()

if __name__ == '__main__':
    main()
