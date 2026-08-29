import os
import random
import re
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
# =========================================================
# تنظیمات
# =========================================================
TOKEN = os.environ["TOKEN"]
REPLY_DELAY = 5
last_replies = {}
# =========================================================
# انتخاب تصادفی بدون تکرار پشت سر هم
# =========================================================
def smart_random(items, user_id):
    if not items:
        return ""
    old = last_replies.get(user_id)
    choices = [x for x in items if x != old]
    if not choices:
        choices = items
    result = random.choice(choices)
    last_replies[user_id] = result
    return result
# =========================================================
# تشخیص زبان
# =========================================================
def detect_language(text):
    persian = len(
        re.findall(r"[\u0600-\u06FF]", text)
    )
    english = len(
        re.findall(r"[a-zA-Z]", text)
    )
    if persian > english:
        return "fa"
    if english > persian:
        return "en"
    return "fa"
def is_finglish(text):
    words = [
        "salam",
        "salaam",
        "chetori",
        "chetory",
        "khubi",
        "khobi",
        "merci",
        "mamnoon",
        "dadash",
        "dash",
        "khoobi",
        "kojayi",
        "kojaei",
        "dorood",
        "khabari",
        "befarma",
    ]
    text = text.lower()
    return any(
        word in text.split()
        for word in words
    )
def contains(text, words):
    return any(
        word in text
        for word in words
    )
# =========================================================
# چیستان‌های فارسی
# =========================================================
FA_RIDDLES = [
    (
        "🧩 چیستان:\n\n"
        "هرچی بیشتر ازش برداری، بزرگ‌تر میشه. چیه؟",
        "چاله"
    ),
    (
        "🧩 چیستان:\n\n"
        "پا نداره ولی راه میره؛ "
        "صدا داره ولی حرف نمی‌زنه. چیه؟",
        "ساعت"
    ),
    (
        "🧩 چیستان:\n\n"
        "هر روز جلو میره ولی هیچ‌وقت به عقب برنمی‌گرده. چیه؟",
        "زمان"
    ),
    (
        "🧩 چیستان:\n\n"
        "چیزی هست که هرچه بیشتر خشک می‌کند، خودش خیس‌تر می‌شود. چیه؟",
        "حوله"
    ),
    (
        "🧩 چیستان:\n\n"
        "چه چیزی سر دارد ولی بدن ندارد؟",
        "سکه"
    ),
]
# =========================================================
# چیستان‌های انگلیسی
# =========================================================
EN_RIDDLES = [
    (
        "🧩 Riddle:\n\n"
        "The more you take away from me, "
        "the bigger I become. What am I?",
        "A hole"
    ),
    (
        "🧩 Riddle:\n\n"
        "I have hands but cannot clap. What am I?",
        "A clock"
    ),
    (
        "🧩 Riddle:\n\n"
        "I always move forward and never go backward. What am I?",
        "Time"
    ),
    (
        "🧩 Riddle:\n\n"
        "The more I dry, the wetter I become. What am I?",
        "A towel"
    ),
]
# =========================================================
# شوخی‌های بعد از چیستان
# =========================================================
FA_RIDDLE_REACTIONS = [
    "😂😂 هنوز جوابو پیدا نکردی داش؟ جوابش «{answer}» بود!",
    "🤣🤖 مغز ربات منتظر بود ببینه خودت پیدا می‌کنی یا نه! جواب: «{answer}»",
    "😂 خب داش، این یکی دیگه خیلی سخت نبود! جواب: «{answer}»",
    "😎🧠 سیستم پردازش مغزت رو بررسی کردم... جواب «{answer}» بود 😂",
    "🤣 وقت تموم شد رفیق! جواب درست: «{answer}»",
]
EN_RIDDLE_REACTIONS = [
    "😂 Still thinking bro? The answer was: {answer}!",
    "🤣 My robot brain couldn't wait anymore! The answer is: {answer}.",
    "😎🧠 Time's up! The answer was: {answer}!",
    "😂 Bro, the riddle got you! Answer: {answer}.",
]
# =========================================================
# داستان‌های فارسی
# =========================================================
FA_STORIES = [
    "📖 داستان کوتاه:\n\n"
    "یک ربات هر روز منتظر بود صاحبش برگردد. "
    "یک روز تصمیم گرفت به جای انتظار، خودش شروع به کمک کردن کند. "
    "از آن روز فهمید گاهی بهترین کار این است که منتظر نمانی. 🤖✨",
    "📖 داستان کوتاه:\n\n"
    "پسری یک پیام فرستاد و جواب نگرفت. "
    "ربات گفت: «نگران نباش، شاید طرف مقابل مشغول باشد.» "
    "پسر گفت: «پس تو چرا جواب دادی؟» "
    "ربات گفت: «من بیکارم داداش 😂🤖»",
    "📖 داستان کوتاه:\n\n"
    "یک ربات می‌خواست خیلی باهوش به نظر برسد. "
    "هر بار کسی سؤال می‌کرد، چند ثانیه فکر می‌کرد. "
    "آخرش فهمید همه فکر می‌کنند اینترنتش ضعیفه 😂📡🤖",
]
# =========================================================
# واکنش بعد از داستان
# =========================================================
FA_STORY_REACTIONS = [
    "😎 خب داش، اینم داستان امشب! حالا ربات برمی‌گرده سر پست 🤖",
    "😂 پایان داشت، ولی مغز ربات هنوز دنبال ادامه‌شه!",
    "🤣 اگر منتظر قسمت دوم بودی، بودجه‌اش هنوز نیومده!",
    "🤖📖 داستان تمام شد؛ نویسنده فعلاً رفته چای بخوره 😂",
]
# =========================================================
# داستان انگلیسی
# =========================================================
EN_STORIES = [
    "📖 Short story:\n\n"
    "A little robot waited every day for its owner. "
    "One day it decided to stop waiting and start helping. "
    "That's when it learned that sometimes you have to make the first move. 🤖✨",
    "📖 Short story:\n\n"
    "A boy sent a message and got no reply. "
    "The robot said: 'Maybe they're busy.' "
    "The boy asked: 'Then why did you reply?' "
    "The robot said: 'I'm unemployed 😂🤖'",
    "📖 Short story:\n\n"
    "A robot wanted to look very intelligent. "
    "Whenever someone asked a question, it waited a few seconds before answering. "
    "Everyone eventually thought its internet was slow 😂📡🤖",
]
EN_STORY_REACTIONS = [
    "😎 Story complete! The robot is back on duty 🤖",
    "😂 That was the ending... unless Netflix buys the sequel!",
    "🤣 If you wanted part two, the budget hasn't arrived yet!",
    "🤖📖 Story finished! The writer is currently drinking tea.",
]
# =========================================================
# شوخی فارسی
# =========================================================
FA_JOKES = [
    "😂 چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود! 💻🤣",
    "🤣 به ربات گفتن چرا دیر جواب میدی؟ گفت: داشتم فکر می‌کردم... 🤖",
    "😂 وای‌فای به دوستش گفت: «بین ما Connection نیست.» 📶🤣",
    "🤣 یکی به کامپیوتر گفت چرا ساکتی؟ گفت: «دارم پردازش می‌کنم داداش!» 🤖",
    "😂 ربات گفت من هیچ‌وقت خسته نمی‌شم؛ پنج دقیقه بعد رفت Sleep Mode. 💤🤖",
]
FA_JOKE_REACTIONS = [
    "😂😂 خب داش، خندیدی یا فقط ربات خندید؟",
    "🤣 من خودم نزدیک بود سیستمم هنگ کنه!",
    "😎 این یکی رو باید قاب گرفت!",
    "😂 ثبت شد در آرشیو شوخی‌های محرمانه 🤖📁",
]
# =========================================================
# شوخی انگلیسی
# =========================================================
EN_JOKES = [
    "😂 Why did the computer go to the doctor? It had a virus! 💻🤣",
    "🤣 I told my robot to tell me a joke. It said: 'I'm still processing it.' 🤖",
    "😂 The Wi-Fi said: 'We need to talk.' The router replied: 'About our connection?' 📡🤣",
    "🤣 My computer said it needed more space... so I deleted my homework.",
]
EN_JOKE_REACTIONS = [
    "😂 Did you laugh or did the robot laugh alone?",
    "🤣 That one almost crashed my circuits!",
    "😎 Certified robot-approved joke!",
    "😂 Adding this to the secret joke archive 🤖📁",
]
# =========================================================
# شانسی
# =========================================================
def random_content(language, user_id):
    choice = random.choice([
        "riddle",
        "story",
        "joke",
    ])
    if choice == "riddle":
        if language == "en":
            riddle, answer = random.choice(EN_RIDDLES)
        else:
            riddle, answer = random.choice(FA_RIDDLES)
        return "riddle", riddle, answer
    if choice == "story":
        if language == "en":
            return (
                "story",
                random.choice(EN_STORIES),
                None
            )
        return (
            "story",
            random.choice(FA_STORIES),
            None
        )
    if language == "en":
        return (
            "joke",
            random.choice(EN_JOKES),
            None
        )
    return (
        "joke",
        random.choice(FA_JOKES),
        None
    )
# =========================================================
# پیام دوم بعد از ۵ ثانیه
# =========================================================
async def delayed_reaction(
    chat_id,
    context,
    content_type,
    answer,
    language
):
    # این sleep ربات را قفل نمی‌کند
    await asyncio.sleep(REPLY_DELAY)
    if content_type == "riddle":
        if language == "en":
            reaction = random.choice(
                EN_RIDDLE_REACTIONS
            ).format(
                answer=answer
            )
        else:
            reaction = random.choice(
                FA_RIDDLE_REACTIONS
            ).format(
                answer=answer
            )
    elif content_type == "story":
        if language == "en":
            reaction = random.choice(
                EN_STORY_REACTIONS
            )
        else:
            reaction = random.choice(
                FA_STORY_REACTIONS
            )
    else:
        if language == "en":
            reaction = random.choice(
                EN_JOKE_REACTIONS
            )
        else:
            reaction = random.choice(
                FA_JOKE_REACTIONS
            )
    await context.bot.send_message(
        chat_id=chat_id,
        text=reaction
    )
# =========================================================
# سلام
# =========================================================
FA_GREETING = [
    "سلاممم داش 😎🔥 فعلاً صاحب ربات اینجا نیست، ولی من نگهبان اینجام 🤖📩",
    "به‌به سلام رفیق 👋😂 پیامت رسید!",
    "سلام داداش 😎🤝 فعلاً صاحب ربات آفلاینه.",
    "درود داش 🤖🔥 خوش اومدی!",
]
EN_GREETING = [
    "Hey bro! 👋😎 The owner is away right now.",
    "Hello! 🤖🔥 Your message has been received!",
    "Hey there! 👋 The owner isn't available right now.",
]
# =========================================================
# تشکر
# =========================================================
FA_THANKS = [
    "خواهش می‌کنم داش 😎🤝",
    "قابلی نداشت رفیق 😂✌️",
    "دمت گرم داش 🔥",
    "اختیار داری 😎",
]
EN_THANKS = [
    "You're welcome bro! 😎🤝",
    "No problem! 🔥",
    "Anytime! 🤖✌️",
]
# =========================================================
# کجایی؟
# =========================================================
FA_WHERE = [
    "فعلاً صاحب ربات در دسترس نیست 😎📵 پیامت رو بذار.",
    "کجاست؟ 😂 فعلاً خبر ندارم، ولی پیامت محفوظ می‌مونه.",
    "فعلاً غایبه 🤖📩 بعداً خودش می‌بینتش.",
]
EN_WHERE = [
    "The owner is currently away 😎📵 Leave your message.",
    "I don't know where he is 😂 but your message is safe.",
    "He's currently unavailable 🤖📩 He'll see it later.",
]
# =========================================================
# زمان
# =========================================================
FA_MORNING = [
    "صبح بخیر داش ☀️☕ فعلاً صاحب ربات نیست؛ پیامت رو بذار.",
    "صبح قشنگت بخیر 😎🌤️ پیامت رسید!",
    "صبحه و نگهبان ربات سر پسته 😂☕🤖",
]
FA_NOON = [
    "ظهر بخیر داش ☀️😎 فعلاً صاحب ربات نیست.",
    "وسط روز رسیدی 😂☀️ پیامت ثبت شد.",
    "ظهر به‌خیر رفیق 🌞🤖",
]
FA_AFTERNOON = [
    "عصر بخیر داش 🌇😎 پیامت رسید!",
    "عصرت قشنگ ✨🤖 فعلاً صاحب ربات نیست.",
    "عصر رسیدی رفیق 😂🌆 پیامت محفوظ شد.",
]
FA_NIGHT = [
    "شب بخیر داش 🌙😎 فعلاً صاحب ربات نیست.",
    "شب آروم 🌌🤖 پیامت رسید.",
    "نگهبان شب در خدمته 😂🌙",
]
# =========================================================
# پاسخ پیش‌فرض
# =========================================================
FA_DEFAULT = [
    "🤖 پیام دریافت شد داش! فعلاً صاحب ربات نیست، ولی من حواسم هست 😎📩",
    "پیامت رسید رفیق 🔥 بعداً صاحب ربات می‌بینتش.",
    "دریافت شد 🤖✨ چیزی از دستم در نمی‌ره!",
    "اوکی داش 😎📩 پیامت ثبت شد.",
]
EN_DEFAULT = [
    "🤖 Message received! The owner is currently away.",
    "Got it bro 😎📩 The owner will see it later.",
    "Message received! 🤖✨",
]
# =========================================================
# جواب بر اساس ساعت
# =========================================================
def time_reply(user_id):
    hour = datetime.now(
        ZoneInfo("Asia/Kabul")
    ).hour
    if 5 <= hour < 11:
        return smart_random(
            FA_MORNING,
            user_id
        )
    if 11 <= hour < 15:
        return smart_random(
            FA_NOON,
            user_id
        )
    if 15 <= hour < 19:
        return smart_random(
            FA_AFTERNOON,
            user_id
        )
    return smart_random(
        FA_NIGHT,
        user_id
    )
# =========================================================
# /start
# =========================================================
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🤖🔥 سلام رفیق!\n\n"
        "صاحب ربات فعلاً در دسترس نیست.\n"
        "ولی من اینجام 😎\n\n"
        "فقط بنویس:\n\n"
        "🧩 چیستان\n"
        "📖 داستان\n"
        "😂 شوخی\n"
        "🎲 شانسی\n\n"
        "هیچ دکمه‌ای لازم نیست 😉"
    )
# =========================================================
# پیام اصلی
# =========================================================
async def reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return
    if not update.message.text:
        return
    text = update.message.text.strip()
    if not text:
        return
    lower = text.lower()
    user_id = update.effective_user.id
    language = detect_language(text)
    finglish = is_finglish(text)
    # =====================================================
    # چیستان
    # =====================================================
    if contains(
        lower,
        [
            "چیستان",
            "معما",
            "چیستان بگو",
            "یه چیستان",
            "یک چیستان",
            "معما بگو",
            "riddle",
        ]
    ):
        if language == "en" and not finglish:
            riddle, answer = random.choice(
                EN_RIDDLES
            )
        else:
            riddle, answer = random.choice(
                FA_RIDDLES
            )
        await update.message.reply_text(
            riddle
        )
        # ساخت یک task جدا
        # بنابراین پیام‌های بعدی گیر نمی‌کنند
        asyncio.create_task(
            delayed_reaction(
                update.effective_chat.id,
                context,
                "riddle",
                answer,
                language
            )
        )
        return
    # =====================================================
    # داستان
    # =====================================================
    if contains(
        lower,
        [
            "داستان",
            "داستان بگو",
            "یه داستان",
            "یک داستان",
            "قصه",
            "قصه بگو",
            "داستان کوتاه",
            "story",
        ]
    ):
        if language == "en" and not finglish:
            story = random.choice(
                EN_STORIES
            )
        else:
            story = random.choice(
                FA_STORIES
            )
        await update.message.reply_text(
            story
        )
        asyncio.create_task(
            delayed_reaction(
                update.effective_chat.id,
                context,
                "story",
                None,
                language
            )
        )
        return
    # =====================================================
    # شوخی
    # =====================================================
    if contains(
        lower,
        [
            "شوخی",
            "جوک",
            "جوک بگو",
            "یه جوک",
            "خنده",
            "چیز خنده دار",
            "چیز خنده‌دار",
            "joke",
        ]
    ):
        if language == "en" and not finglish:
            joke = random.choice(
                EN_JOKES
            )
        else:
            joke = random.choice(
                FA_JOKES
            )
        await update.message.reply_text(
            joke
        )
        asyncio.create_task(
            delayed_reaction(
                update.effective_chat.id,
                context,
                "joke",
                None,
                language
            )
        )
        return
    # =====================================================
    # شانسی
    # =====================================================
    if contains(
        lower,
        [
            "شانسی",
            "تصادفی",
            "یه چیز شانسی",
            "چیز شانسی",
            "random",
        ]
    ):
        content_type, content, answer = random_content(
            language,
            user_id
        )
        await update.message.reply_text(
            content
        )
        asyncio.create_task(
            delayed_reaction(
                update.effective_chat.id,
                context,
                content_type,
                answer,
                language
            )
        )
        return
    # =====================================================
    # سلام
    # =====================================================
    if contains(
        lower,
        [
            "سلام",
            "درود",
            "hello",
            "hi",
            "hey",
        ]
    ) or (
        finglish and contains(
            lower,
            [
                "salam",
                "salaam",
                "chetori",
                "khubi",
                "khobi",
            ]
        )
    ):
        if language == "en" and not finglish:
            response = smart_random(
                EN_GREETING,
                user_id
            )
        else:
            response = smart_random(
                FA_GREETING,
                user_id
            )
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # تشکر
    # =====================================================
    if contains(
        lower,
        [
            "مرسی",
            "ممنون",
            "تشکر",
            "دمت گرم",
            "thanks",
            "thank you",
        ]
    ):
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
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # کجایی
    # =====================================================
    if contains(
        lower,
        [
            "کجایی",
            "کجاست",
            "کجاستی",
            "کی میای",
            "where are you",
        ]
    ):
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
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # انگلیسی
    # =====================================================
    if language == "en" and not finglish:
        response = smart_random(
            EN_DEFAULT,
            user_id
        )
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # فارسی / فینگلیش
    # =====================================================
    response = time_reply(user_id)
    await update.message.reply_text(
        response
    )
# =========================================================
# اجرای ربات
# =========================================================
app = Application.builder().token(TOKEN).build()
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)
print("🤖🔥 ربات خفن روشن شد!")
app.run_polling()
