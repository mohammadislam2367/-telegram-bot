import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
TOKEN = os.environ["TOKEN"]
# =========================
# جواب‌ها
# =========================
GREETINGS = [
    "سلاممم 👋😎 فعلاً صاحب ربات اینجا نیست، ولی پیامت رسید 🤖📩",
    "سلام رفیق! 👋✨ صاحب ربات فعلاً آفلاینه، پیامت رو بذار.",
    "سلام 😎🤖 فعلاً من نگهبان اینجام؛ پیامت محفوظ می‌مونه!",
    "سلام داش 😂👋 فعلاً صاحب ربات نیست، ولی من حواسم به پیامته."
]
GOODBYES = [
    "فعلاً رفیق 👋😎 پیامت رسید!",
    "به امید دیدار ✌️🤖",
    "فعلاً داش 🌙✨ بعداً می‌بینیمت!"
]
THANKS = [
    "خواهش می‌کنم رفیق 😎🤝",
    "قابلی نداشت! ✨🤖",
    "خواهش داش 😂✌️",
    "دمت گرم که گفتی 😎🔥"
]
WHERE = [
    "فعلاً صاحب ربات در دسترس نیست 😄📵 پیامت رو بذار، بعداً می‌بینتش.",
    "فعلاً غایبه 😎🤖 ولی پیامت اینجا محفوظ می‌مونه.",
    "کجاست؟ 😂 فعلاً خبر ندارم، ولی پیامت رو نگه می‌دارم!",
    "فعلاً مأموریت رفته 😂🤖 پیامت رو بذار."
]
FUNNY = [
    "😂😂 داداش اینو دیگه باید صاحب ربات خودش ببینه! پیامت ثبت شد 🤖📩",
    "🤣 این یکی قشنگ بود! پیامت رسید 😂🤖",
    "😂😂 منم خندیدم! ولی صاحب ربات باید اینو ببینه 😎",
    "خخخ 😂🤖 این یکی رفت توی پرونده!"
]
MORNING = [
    "صبح قشنگت بخیر! ☀️☕️ الان نیستم، یه پیام بنداز اینجا تا بعداً ببینمش.",
    "صبح بخیر رفیق ☀️😎 فعلاً آفلاینه، ولی پیامت گم نمی‌شه 📩",
    "صبح بخیر! 🌤️ فعلاً صاحب ربات در دسترس نیست؛ پیامت رو بذار.",
    "صبحه و نگهبان ربات سر پسته 😂☀️ پیامت رسید!"
]
NOON = [
    "ظهر بخیر داش! 😎☀️ فعلاً آفلاینه، ولی پیام تو رسید 📩",
    "وسط روز رسیدی 😄☀️ پیامت رو بفرست، بعداً دیده می‌شه.",
    "ظهر به‌خیر! 🌞 صاحب ربات فعلاً غایبه، ولی پیام محفوظ می‌مونه 🤖",
    "ظهره داش 😎☀️ فعلاً نیست، ولی من حواسم به پیامته."
]
AFTERNOON = [
    "عصرت قشنگ! ✨ فعلاً صاحب ربات در دسترس نیست، ولی پیام رسید 📩",
    "عصر بخیر رفیق 🌇😎 فعلاً آفلاینه، پیامت رو بذار.",
    "عصر رسیدی 😄🌆 صاحب ربات فعلاً نیست، ولی من اینجام 🤖",
    "عصر بخیر داش 😎🔥 پیامت ثبت شد."
]
NIGHT = [
    "اوه، شب رسیدی 😄🌙 من فعلاً در دسترس نیستم؛ پیام رو بنداز اینجا.",
    "شب بخیر رفیق 🌙✨ فعلاً آفلاینه، ولی پیامت اینجا می‌مونه.",
    "شب آروم 🌌🤖 صاحب ربات فعلاً نیست؛ بعداً پیامت رو می‌بینه.",
    "شب بخیر داش 🌙😎 من نگهبان شبم، پیامت رسید!"
]
DEFAULT = [
    "🤖 پیام رسید! فعلاً صاحب ربات در دسترس نیست، ولی پیامت محفوظ شد 📩",
    "پیامت رسید رفیق 😎📩 بعداً صاحب ربات می‌بینتش.",
    "دریافت شد 🤖✨ فعلاً آفلاینه، ولی پیام اینجا می‌مونه.",
    "پیامت ثبت شد داش 😎🔥 وقتی صاحب ربات بیاد می‌بینتش."
]
ENGLISH = [
    "Hey! 👋😎 The owner is currently away. Leave your message and he'll see it later. 🤖📩",
    "Hello! 🤖✨ The owner isn't available right now, but your message has been received.",
    "Got your message! 😎📩 The owner will see it later.",
    "Hey there! 👋 The owner is away for now, but your message is safe."
]
EMOJI = [
    "😎🤝 پیامت رسید داش!",
    "😂🔥 دریافت شد!",
    "🤖✨ ربات در خدمت است!",
    "👀📩 دیدم که پیام دادی!",
    "😎✌️ ثبت شد رفیق!"
]
# =========================
# جلوگیری از تکرار
# =========================
last_replies = {}
def choose_reply(options, user_id):
    previous = last_replies.get(user_id)
    choices = [x for x in options if x != previous]
    if not choices:
        choices = options
    response = random.choice(choices)
    last_replies[user_id] = response
    return response
# =========================
# تشخیص پیام
# =========================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip().lower()
    user_id = update.effective_user.id
    # زمان افغانستان
    now = datetime.now(ZoneInfo("Asia/Kabul"))
    hour = now.hour
    # -------------------------
    # خداحافظی
    # -------------------------
    if any(word in text for word in [
        "خداحافظ",
        "فعلا",
        "فعلاً",
        "بای",
        "bye",
        "goodbye"
    ]):
        response = choose_reply(GOODBYES, user_id)
    # -------------------------
    # سلام
    # -------------------------
    elif any(word in text for word in [
        "سلام",
        "سلاممم",
        "درود",
        "hello",
        "hi",
        "hey"
    ]):
        response = choose_reply(GREETINGS, user_id)
    # -------------------------
    # تشکر
    # -------------------------
    elif any(word in text for word in [
        "مرسی",
        "ممنون",
        "تشکر",
        "دمت گرم",
        "thanks",
        "thank you"
    ]):
        response = choose_reply(THANKS, user_id)
    # -------------------------
    # پرسیدن کجایی
    # -------------------------
    elif any(word in text for word in [
        "کجایی",
        "کجاست",
        "کجاستی",
        "کی میای",
        "where are you"
    ]):
        response = choose_reply(WHERE, user_id)
    # -------------------------
    # شوخی و خنده
    # -------------------------
    elif any(word in text for word in [
        "😂",
        "🤣",
        "😆",
        "😹",
        "هههه",
        "خخخ",
        "haha",
        "hahaha",
        "lol"
    ]):
        response = choose_reply(FUNNY, user_id)
    # -------------------------
    # پیام انگلیسی ساده
    # -------------------------
    elif any(word in text.split() for word in [
        "what",
        "where",
        "how",
        "when",
        "good",
        "morning",
        "evening",
        "hello"
    ]):
        response = choose_reply(ENGLISH, user_id)
    # -------------------------
    # فقط ایموجی
    # -------------------------
    elif all(not char.isalnum() for char in text) and text:
        response = choose_reply(EMOJI, user_id)
    # -------------------------
    # صبح
    # 05:00 تا 11:00
    # -------------------------
    elif 5 <= hour < 11:
        response = choose_reply(MORNING, user_id)
    # -------------------------
    # ظهر
    # 11:00 تا 15:00
    # -------------------------
    elif 11 <= hour < 15:
        response = choose_reply(NOON, user_id)
    # -------------------------
    # عصر
    # 15:00 تا 19:00
    # -------------------------
    elif 15 <= hour < 19:
        response = choose_reply(AFTERNOON, user_id)
    # -------------------------
    # شب
    # 19:00 تا 05:00
    # -------------------------
    elif hour >= 19 or hour < 5:
        response = choose_reply(NIGHT, user_id)
    # -------------------------
    # پیام معمولی
    # -------------------------
    else:
        response = choose_reply(DEFAULT, user_id)
    await update.message.reply_text(response)
# =========================
# اجرای ربات
# =========================
app = Application.builder().token(TOKEN).build()
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)
print("ربات خفن روشن شد 🤖🔥")
app.run_polling()
