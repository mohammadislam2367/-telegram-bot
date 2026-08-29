import os
import random
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
TOKEN = os.environ["TOKEN"]
# =========================================================
# حافظه کوتاه ربات
# =========================================================
memory = {}
last_answers = {}
def remember(user_id, text):
    memory[user_id] = text
def get_memory(user_id):
    return memory.get(user_id, "")
def smart_random(items, user_id):
    old = last_answers.get(user_id)
    choices = [x for x in items if x != old]
    if not choices:
        choices = items
    answer = random.choice(choices)
    last_answers[user_id] = answer
    return answer
# =========================================================
# تشخیص زبان
# =========================================================
def detect_language(text):
    persian = len(re.findall(r"[\u0600-\u06FF]", text))
    english = len(re.findall(r"[a-zA-Z]", text))
    if persian > english:
        return "fa"
    if english > persian:
        return "en"
    return "fa"
def is_finglish(text):
    words = text.lower().split()
    common = [
        "salam",
        "chetori",
        "khubi",
        "khobi",
        "merci",
        "mamnoon",
        "dadash",
        "dash",
        "khosh",
        "khab",
        "chi",
        "khabari",
        "kojayi",
        "kojaei",
        "bia",
        "baba",
        "eyval",
    ]
    return sum(word in common for word in words) >= 1
# =========================================================
# تشخیص حالت پیام
# =========================================================
def contains(text, words):
    return any(word in text for word in words)
# =========================================================
# جواب‌های سلام
# =========================================================
FA_GREETINGS = [
    "سلاممم داش 😎🔥 فعلاً صاحب ربات نیست، ولی من نگهبان اینجام 🤖",
    "سلام رفیق 👋😂 پیامت رسید؛ صاحب ربات فعلاً در دسترس نیست.",
    "به‌به سلام 😎🤝 خوش اومدی به قلمرو ربات!",
    "سلام داداش 👋🤖 فعلاً من اینجام؛ پیامت هم محفوظ شد.",
]
EN_GREETINGS = [
    "Hey! 👋😎 The owner is away right now, but I'm here.",
    "Hello bro! 🤖🔥 Your message has been received.",
    "Hey there! 👋 The owner isn't available right now.",
    "Welcome! 😎🤖 Leave your message here.",
]
# =========================================================
# تشکر
# =========================================================
FA_THANKS = [
    "خواهش می‌کنم داش 😎🤝",
    "قابلی نداشت رفیق 😂✌️",
    "دمت گرم 😎🔥",
    "خواهش داش 🤖❤️",
]
EN_THANKS = [
    "You're welcome! 😎🤝",
    "No problem bro! 🔥",
    "Anytime! 🤖✌️",
    "You're welcome! 👋😎",
]
# =========================================================
# شوخی
# =========================================================
FA_FUNNY = [
    "😂😂 این یکی رو باید صاحب ربات خودش ببینه!",
    "خخخخ 😂🤖 منم نزدیک بود از سیستم خارج بشم!",
    "🤣🔥 این پیام رفت توی پرونده‌های محرمانه ربات!",
    "😂 داش تو اومدی اینجا فقط برای خرابکاری!",
]
EN_FUNNY = [
    "😂😂 The owner definitely needs to see this!",
    "LOL 🤣🤖 That was actually funny!",
    "😂🔥 This one goes into the secret robot files!",
    "🤣 Bro, you're making my circuits laugh!",
]
# =========================================================
# کجایی؟
# =========================================================
FA_WHERE = [
    "فعلاً صاحب ربات در دسترس نیست 😎📵 پیامت رو بذار.",
    "کجاست؟ 😂 نمی‌دونم داش، ولی پیامت رو نگه می‌دارم.",
    "فعلاً غایبه 🤖📩 بعداً خودش پیامت رو می‌بینه.",
]
EN_WHERE = [
    "The owner is currently away 😎📵 Leave your message.",
    "I don't know where he is 😂 but your message is safe.",
    "He's currently unavailable 🤖📩 He'll see your message later.",
]
# =========================================================
# پیام معمولی
# =========================================================
FA_DEFAULT = [
    "🤖 پیام دریافت شد! فعلاً صاحب ربات نیست، ولی من حواسم هست 😎📩",
    "پیامت رسید داش 🔥 بعداً صاحب ربات می‌بینتش.",
    "دریافت شد 🤖✨ چیزی از دستم در نمی‌ره!",
    "اوکی رفیق 😎📩 پیامت ثبت شد.",
    "پیامت وارد سیستم شد 😂🤖",
]
EN_DEFAULT = [
    "🤖 Message received! The owner is currently away.",
    "Got it bro 😎📩 The owner will see it later.",
    "Message received! 🤖✨",
    "Your message has been safely received 😎",
]
# =========================================================
# صبح / ظهر / عصر / شب
# =========================================================
FA_MORNING = [
    "صبح بخیر داش ☀️☕ فعلاً صاحب ربات نیست؛ پیامت رو بذار.",
    "صبح قشنگت بخیر 😎🌤️ پیامت رسید!",
    "صبحه و نگهبان ربات سر پسته 😂☕🤖",
]
FA_NOON = [
    "ظهر بخیر داش ☀️😎 فعلاً صاحب ربات نیست.",
    "وسط روز رسیدی 😂☀️ پیامت ثبت شد.",
    "ظهر به‌خیر رفیق 🌞🤖 بعداً دیده می‌شه.",
]
FA_AFTERNOON = [
    "عصر بخیر داش 🌇😎 پیامت رسید!",
    "عصرت قشنگ ✨🤖 فعلاً صاحب ربات نیست.",
    "عصر رسیدی رفیق 😂🌆 پیامت محفوظ شد.",
]
FA_NIGHT = [
    "شب بخیر داش 🌙😎 فعلاً صاحب ربات نیست.",
    "شب آروم 🌌🤖 پیامت رسید.",
    "نگهبان شب در خدمته 😂🌙 پیامت ثبت شد.",
]
# =========================================================
# چیستان
# =========================================================
RIDDLES = [
    (
        "🧩 چیستان:\n\n"
        "هرچی بیشتر ازش برداری، بزرگ‌تر میشه. چیه؟",
        "💡 جواب: چاله 😎"
    ),
    (
        "🧩 چیستان:\n\n"
        "چیزی که پا نداره ولی راه میره چیه؟",
        "💡 جواب: ساعت ⏰"
    ),
    (
        "🧩 چیستان:\n\n"
        "چی هست که وقتی می‌شکنه صدایی نداره؟",
        "💡 جواب: قول 🤝"
    ),
]
# =========================================================
# داستان کوتاه
# =========================================================
STORIES = [
    "📖 داستان کوتاه:\n\n"
    "یک ربات کوچک هر روز منتظر صاحبش بود. "
    "یک روز فهمید لازم نیست همیشه منتظر بماند؛ "
    "گاهی خودش می‌تواند چراغ اتاق را روشن کند و بگوید: "
    "«خوش اومدی رفیق.» 🤖✨",
    "📖 داستان کوتاه:\n\n"
    "پسری یک پیام برای دوستش فرستاد و منتظر جواب ماند. "
    "جواب نیامد؛ اما ربات گفت: "
    "«نگران نباش، بعضی پیام‌ها دیر جواب داده می‌شوند، "
    "ولی ارزششان کم نمی‌شود.» 🤖🌙",
]
# =========================================================
# چیزهای خنده‌دار
# =========================================================
JOKES = [
    "😂 می‌دونی چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود! 💻🤣",
    "🤣 به ربات گفتن چرا دیر جواب میدی؟ گفت: داشتم فکر می‌کردم... 🤖😂",
    "😂 ربات گفت من هیچ‌وقت خسته نمی‌شم؛ بعدش رفت روی Sleep Mode. 💤🤖",
    "🤣 یکی به وای‌فای گفت چرا سردی؟ گفت: چون Connection نداریم! 📶😂",
]
# =========================================================
# پاسخ زمان
# =========================================================
def time_reply(hour):
    if 5 <= hour < 11:
        return "morning"
    if 11 <= hour < 15:
        return "noon"
    if 15 <= hour < 19:
        return "afternoon"
    return "night"
# =========================================================
# منوی اصلی
# =========================================================
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🧩 چیستان", callback_data="riddle"),
            InlineKeyboardButton("😂 خنده", callback_data="joke"),
        ],
        [
            InlineKeyboardButton("📖 داستان", callback_data="story"),
            InlineKeyboardButton("🎲 شانسی", callback_data="random"),
        ],
        [
            InlineKeyboardButton("💡 جواب چیستان", callback_data="answer"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
# =========================================================
# /start
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖🔥 سلام رفیق!\n\n"
        "صاحب ربات فعلاً در دسترس نیست.\n"
        "ولی من اینجام 😎\n\n"
        "از منوی پایین یکی رو انتخاب کن 👇"
    )
    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )
# =========================================================
# دکمه‌ها
# =========================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "riddle":
        riddle, answer = random.choice(RIDDLES)
        context.user_data["riddle_answer"] = answer
        await query.message.reply_text(
            riddle,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "💡 جواب",
                        callback_data="answer"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🧩 یکی دیگه",
                        callback_data="riddle"
                    )
                ]
            ])
        )
    elif query.data == "answer":
        answer = context.user_data.get(
            "riddle_answer",
            "فعلاً اول یه چیستان بگیر 😂🧩"
        )
        await query.message.reply_text(
            answer,
            reply_markup=main_menu()
        )
    elif query.data == "joke":
        joke = random.choice(JOKES)
        await query.message.reply_text(
            joke,
            reply_markup=main_menu()
        )
    elif query.data == "story":
        story = random.choice(STORIES)
        await query.message.reply_text(
            story,
            reply_markup=main_menu()
        )
    elif query.data == "random":
        options = [
            "🧩riddle",
            "😂joke",
            "📖story",
        ]
        choice = random.choice(options)
        if choice == "🧩riddle":
            riddle, answer = random.choice(RIDDLES)
            context.user_data["riddle_answer"] = answer
            await query.message.reply_text(
                riddle,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "💡 جواب",
                            callback_data="answer"
                        )
                    ]
                ])
            )
        elif choice == "😂joke":
            await query.message.reply_text(
                random.choice(JOKES),
                reply_markup=main_menu()
            )
        else:
            await query.message.reply_text(
                random.choice(STORIES),
                reply_markup=main_menu()
            )
# =========================================================
# پاسخ هوشمند
# =========================================================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    lower = text.lower()
    user_id = update.effective_user.id
    remember(user_id, text)
    now = datetime.now(
        ZoneInfo("Asia/Kabul")
    )
    hour = now.hour
    language = detect_language(text)
    # فینگلیش
    finglish = is_finglish(text)
    # -------------------------
    # سلام
    # -------------------------
    if contains(lower, [
        "سلام",
        "درود",
        "hello",
        "hi",
        "hey",
    ]) or finglish and contains(lower, [
        "salam",
        "chetori",
        "khubi",
        "khobi",
    ]):
        if language == "en" and not finglish:
            response = smart_random(
                EN_GREETINGS,
                user_id
            )
        else:
            response = smart_random(
                FA_GREETINGS,
                user_id
            )
    # -------------------------
    # تشکر
    # -------------------------
    elif contains(lower, [
        "مرسی",
        "ممنون",
        "تشکر",
        "دمت گرم",
        "thanks",
        "thank you",
    ]):
        if language == "en":
            response = smart_random(
                EN_THANKS,
                user_id
            )
        else:
            response = smart_random(
                FA_THANKS,
                user_id
            )
    # -------------------------
    # شوخی
    # -------------------------
    elif contains(lower, [
        "😂",
        "🤣",
        "😆",
        "هههه",
        "خخخ",
        "haha",
        "lol",
    ]):
        if language == "en":
            response = smart_random(
                EN_FUNNY,
                user_id
            )
        else:
            response = smart_random(
                FA_FUNNY,
                user_id
            )
    # -------------------------
    # کجایی
    # -------------------------
    elif contains(lower, [
        "کجایی",
        "کجاست",
        "کی میای",
        "where are you",
    ]):
        if language == "en":
            response = smart_random(
                EN_WHERE,
                user_id
            )
        else:
            response = smart_random(
                FA_WHERE,
                user_id
            )
    # -------------------------
    # خداحافظی
    # -------------------------
    elif contains(lower, [
        "خداحافظ",
        "فعلا",
        "فعلاً",
        "بای",
        "bye",
        "goodbye",
    ]):
        if language == "en":
            response = "Bye! 👋😎 See you later!"
        else:
            response = "فعلاً داش 👋😎 به امید دیدار!"
    # -------------------------
    # ساعت
    # -------------------------
    elif contains(lower, [
        "ساعت چنده",
        "ساعت چند",
        "what time",
        "time",
    ]):
        if language == "en":
            response = (
                f"🕐 It's {now.strftime('%H:%M')} "
                f"Afghanistan time 🇦🇫"
            )
        else:
            response = (
                f"🕐 الان ساعت {now.strftime('%H:%M')} "
                f"به وقت افغانستانه 🇦🇫😎"
            )
    # -------------------------
    # زمان روز
    # -------------------------
    elif contains(lower, [
        "صبح",
        "ظهر",
        "عصر",
        "شب",
        "morning",
        "afternoon",
        "evening",
        "night",
    ]):
        period = time_reply(hour)
        if period == "morning":
            response = smart_random(
                FA_MORNING,
                user_id
            )
        elif period == "noon":
            response = smart_random(
                FA_NOON,
                user_id
            )
        elif period == "afternoon":
            response = smart_random(
                FA_AFTERNOON,
                user_id
            )
        else:
            response = smart_random(
                FA_NIGHT,
                user_id
            )
    # -------------------------
    # حالت عادی
    # -------------------------
    else:
        if language == "en":
            response = smart_random(
                EN_DEFAULT,
                user_id
            )
        else:
            # اگر فارسی/فینگلیش باشد
            period = time_reply(hour)
            if period == "morning":
                response = smart_random(
                    FA_MORNING,
                    user_id
                )
            elif period == "noon":
                response = smart_random(
                    FA_NOON,
                    user_id
                )
            elif period == "afternoon":
                response = smart_random(
                    FA_AFTERNOON,
                    user_id
                )
            else:
                response = smart_random(
                    FA_NIGHT,
                    user_id
                )
    await update.message.reply_text(response)
# =========================================================
# اجرای ربات
# =========================================================
app = Application.builder().token(TOKEN).build()
app.add_handler(
    CommandHandler("start", start)
)
app.add_handler(
    CallbackQueryHandler(button_handler)
)
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)
print("🤖🔥 ربات فوق‌العاده روشن شد!")
app.run_polling()
