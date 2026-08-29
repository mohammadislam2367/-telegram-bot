import os
import re
import random
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
# SETTINGS
# =========================================================
TOKEN = os.environ["TOKEN"]
TIMEZONE = "Asia/Kabul"
# جلوگیری از تکرار پشت سر هم برای هر چت
last_replies = {}
# =========================================================
# TEXT HELPERS
# =========================================================
def clean_text(text: str) -> str:
    text = text.strip().lower()
    replacements = {
        "ي": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
def detect_language(text: str) -> str:
    """
    تشخیص ساده فارسی / انگلیسی.
    اگر حروف فارسی بیشتر باشند فارسی،
    در غیر این صورت اگر حروف انگلیسی وجود داشته باشد انگلیسی.
    """
    fa = len(re.findall(r"[\u0600-\u06FF]", text))
    en = len(re.findall(r"[A-Za-z]", text))
    if fa > en:
        return "fa"
    if en > 0:
        return "en"
    return "fa"
def random_reply(key, options):
    """
    جواب تصادفی بدون تکرار پشت سر هم.
    """
    if not options:
        return ""
    previous = last_replies.get(key)
    available = [
        item for item in options
        if item != previous
    ]
    if not available:
        available = options
    result = random.choice(available)
    last_replies[key] = result
    return result
def kabul_hour():
    return datetime.now(
        ZoneInfo(TIMEZONE)
    ).hour
# =========================================================
# TIME RESPONSES
# =========================================================
MORNING_FA = [
    "صبح بخیر داش ☀️😎 فعلاً صاحب اکانت در دسترس نیست؛ پیامت رو بذار.",
    "صبح قشنگت بخیر رفیق ☕️🤖 فعلاً من نگهبان پیاما هستم.",
    "صبح بخیر! ☀️😂 صاحب اکانت فعلاً نیست، ولی پیامت رسید.",
]
NOON_FA = [
    "ظهر بخیر داش 🌞😎 فعلاً صاحب اکانت نیست؛ پیامت رو بذار.",
    "ظهر به‌خیر رفیق ☀️🤖 پیام شما دریافت شد.",
    "وسط روز رسیدی 😂🌞 فعلاً من سر پستم!",
]
AFTERNOON_FA = [
    "عصر بخیر داش 🌇😎 فعلاً صاحب اکانت در دسترس نیست.",
    "عصرت قشنگ رفیق 🌆🤖 پیامت رسید.",
    "عصر رسیدی 😂🌇 من فعلاً جای صاحب اکانت وایسادم!",
]
NIGHT_FA = [
    "شب بخیر داش 🌙😎 فعلاً صاحب اکانت در دسترس نیست.",
    "شب آروم رفیق 🌌🤖 پیامت رسید.",
    "اوه، شب رسیدی 😂🌙 فعلاً من نگهبان اینجام!",
]
MORNING_EN = [
    "Good morning! ☀️😎 The owner is currently unavailable.",
    "Morning bro! ☕️🤖 Your message has been received.",
]
NOON_EN = [
    "Good afternoon! 🌞😎 The owner is currently unavailable.",
    "Afternoon bro! 🤖📩 Your message has been received.",
]
AFTERNOON_EN = [
    "Good evening! 🌇😎 The owner is currently unavailable.",
    "Evening bro! 🤖📩 Your message has been received.",
]
NIGHT_EN = [
    "Good night! 🌙😎 The owner is currently unavailable.",
    "Night bro! 🌌🤖 Your message has been received.",
]
def get_time_reply(language, key):
    hour = kabul_hour()
    if language == "en":
        if 5 <= hour < 11:
            return random_reply(
                key + "-morning",
                MORNING_EN,
            )
        if 11 <= hour < 15:
            return random_reply(
                key + "-noon",
                NOON_EN,
            )
        if 15 <= hour < 19:
            return random_reply(
                key + "-afternoon",
                AFTERNOON_EN,
            )
        return random_reply(
            key + "-night",
            NIGHT_EN,
        )
    if 5 <= hour < 11:
        return random_reply(
            key + "-morning",
            MORNING_FA,
        )
    if 11 <= hour < 15:
        return random_reply(
            key + "-noon",
            NOON_FA,
        )
    if 15 <= hour < 19:
        return random_reply(
            key + "-afternoon",
            AFTERNOON_FA,
        )
    return random_reply(
        key + "-night",
        NIGHT_FA,
    )
# =========================================================
# GREETINGS
# =========================================================
HELLO_FA = [
    "سلاممم داش 👋😎 فعلاً صاحب اکانت اینجا نیست، ولی من سر پستم 🤖",
    "به‌به سلام رفیق 😂🤝 پیامت سالم رسید!",
    "سلام داش 🔥🤖 فعلاً من نگهبان پیاما هستم.",
    "سلام رفیق 😎📩 صاحب اکانت فعلاً در دسترس نیست.",
    "سلاممم 😂 من زودتر از صاحب اکانت جواب دادم!",
]
HELLO_EN = [
    "Hey bro! 👋😎 The owner is currently away, but I'm on duty. 🤖",
    "Hello! 🤖🔥 Your message has been received.",
    "Hey! 😂📩 The owner isn't available right now.",
    "Hello bro! 😎 The inbox robot is on duty.",
]
# =========================================================
# THANKS
# =========================================================
THANKS_FA = [
    "خواهش می‌کنم داش 😎🤝",
    "قابلی نداشت رفیق 😂✌️",
    "دمت گرم داش 🔥🤖",
    "خواهش داش، ربات برای همین اینجاست 😂",
]
THANKS_EN = [
    "You're welcome bro! 😎🤝",
    "Anytime! 🤖🔥",
    "No problem! 😂✌️",
    "You're good bro! 😎",
]
# =========================================================
# WHERE
# =========================================================
WHERE_FA = [
    "فعلاً صاحب اکانت در دسترس نیست 😎📵 پیامت رو بذار.",
    "کجاست؟ 😂 داش منم خبر ندارم!",
    "فعلاً غایبه رفیق 🤖📩 ولی پیامت رسید.",
    "صاحب اکانت فعلاً نیست؛ من جای خالی‌شو پر کردم 😂",
]
WHERE_EN = [
    "The owner is currently away 😎📵 Leave your message here.",
    "Where is he? 😂 I have no idea!",
    "He's currently unavailable, but your message arrived 🤖📩",
    "The owner is away, so I'm covering the inbox 😂",
]
# =========================================================
# GENERAL
# =========================================================
GENERAL_FA = [
    "😂 داش اینو دیگه باید صاحب اکانت خودش ببینه! پیامت ثبت شد 🤖📩",
    "😎 پیامت رسید رفیق؛ فعلاً من نگهبان اینجام 🤖",
    "🤣 دریافت شد داش! پیام گم نمی‌شه.",
    "🤖 پیام وارد سیستم شد؛ بعداً صاحب اکانت می‌بینتش.",
    "😂 گرفتم رفیق! فعلاً ربات سر پسته.",
    "📩 پیامت رسید؛ من تحویلش گرفتم 😎🤖",
    "😂 صاحب اکانت نیست، ولی صندوق پیام‌ها بیکار نیست!",
]
GENERAL_EN = [
    "😂 Got your message bro! The owner is currently away. 🤖📩",
    "😎 Message received! The owner will see it later.",
    "🤖 Your message has been received.",
    "😂 Got it bro! The robot is still on duty.",
    "📩 Message received and safely delivered.",
]
# =========================================================
# RIDDLES
# =========================================================
RIDDLES_FA = [
    (
        "چیستان:\nهرچی بیشتر ازش برداری، بزرگ‌تر میشه. چیه؟",
        "جواب: چاله 😎"
    ),
    (
        "چیستان:\nچه چیزی دست دارد ولی نمی‌تواند دست بزند؟",
        "جواب: ساعت ⏰"
    ),
    (
        "چیستان:\nچه چیزی همیشه جلو می‌رود ولی برنمی‌گردد؟",
        "جواب: زمان ⏳"
    ),
    (
        "چیستان:\nچه چیزی هرچه بیشتر خشک می‌کند، خودش خیس‌تر می‌شود؟",
        "جواب: حوله 😂"
    ),
    (
        "چیستان:\nچه چیزی سوراخ‌های زیادی دارد ولی آب را نگه می‌دارد؟",
        "جواب: اسفنج 🧽"
    ),
    (
        "چیستان:\nچه چیزی چشم دارد ولی نمی‌بیند؟",
        "جواب: سوزن 🪡"
    ),
    (
        "چیستان:\nچه چیزی پا دارد ولی راه نمی‌رود؟",
        "جواب: میز 😎"
    ),
    (
        "چیستان:\nچه چیزی بالا می‌رود ولی پایین نمی‌آید؟",
        "جواب: سن 😄"
    ),
]
RIDDLES_EN = [
    (
        "Riddle:\nThe more you take away from me, the bigger I become. What am I?",
        "Answer: A hole 😎"
    ),
    (
        "Riddle:\nI have hands but I cannot clap. What am I?",
        "Answer: A clock ⏰"
    ),
    (
        "Riddle:\nI always move forward but never backward. What am I?",
        "Answer: Time ⏳"
    ),
    (
        "Riddle:\nWhat gets wetter as it dries?",
        "Answer: A towel 😂"
    ),
    (
        "Riddle:\nWhat has many holes but can still hold water?",
        "Answer: A sponge 🧽"
    ),
]
# =========================================================
# STORIES
# =========================================================
STORIES_FA = [
    "داستان:\nیک ربات تصمیم گرفت یک روز استراحت کند. "
    "پنج دقیقه بعد صاحبش پیام داد: «کجایی؟» "
    "ربات گفت: «داش استراحتم هم کنسل شد 😂🤖»",
    "داستان:\nیکی از ربات پرسید: «همه‌چیز بلدی؟» "
    "گفت: «نه داش، رمز وای‌فای رو هنوز بهم نگفتن 😂📡»",
    "داستان:\nربات منتظر پیام بود. گوشی زنگ خورد و گفت: "
    "«می‌دونستم! شیفتم تموم نشده 😂🤖»",
    "داستان:\nیکی گفت امروز خیلی کار دارم. "
    "ربات گفت: «منم.» "
    "گفت: «چه کاری؟» "
    "ربات گفت: «منتظر پیام بعدی تو 😂»",
]
STORIES_EN = [
    "Story:\nA robot decided to take a day off. "
    "Five minutes later, its owner asked: 'Where are you?' "
    "The robot replied: 'My vacation is cancelled 😂🤖'",
    "Story:\nSomeone asked a robot: 'Do you know everything?' "
    "It replied: 'No bro, I still don't know the Wi-Fi password 😂📡'",
    "Story:\nThe robot was waiting for a message. "
    "The phone buzzed. "
    "The robot said: 'I knew it! My shift isn't over 😂🤖'",
]
# =========================================================
# JOKES
# =========================================================
JOKES_FA = [
    "چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود! 💻🤣",
    "به وای‌فای گفتم حالت چطوره؟ گفت: «اتصال ندارم!» 📡😂",
    "ربات گفت خسته نمی‌شم؛ پنج دقیقه بعد رفت Sleep Mode 🤖💤",
    "به کامپیوتر گفتن چرا ساکتی؟ گفت: «دارم پردازش می‌کنم داش!» 😂",
    "گفتم اینترنت چرا کندی؟ گفت: «منم مثل تو حوصله ندارم!» 😂📡",
    "ربات رفت باشگاه؛ برگشت گفت: «آپدیت شدم!» 🤖😂",
]
JOKES_EN = [
    "Why did the computer go to the doctor? Because it had a virus! 💻🤣",
    "I asked Wi-Fi how it was doing. It said: 'No connection!' 📡😂",
    "The robot said it never gets tired. Five minutes later: Sleep Mode 🤖💤",
    "I asked the internet why it was slow. It said: 'I'm tired too!' 😂📡",
]
# =========================================================
# SEND MESSAGE
# =========================================================
async def send_message(
    context,
    message,
    text,
    business_connection_id=None,
):
    """
    اگر پیام از Chat Automation آمده باشد،
    با business_connection_id پاسخ می‌دهد.
    در غیر این صورت پیام معمولی Bot است.
    """
    if not text:
        return
    try:
        if business_connection_id:
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=text,
                business_connection_id=business_connection_id,
            )
        else:
            await message.reply_text(text)
    except Exception as error:
        print(
            "SEND ERROR:",
            repr(error)
        )
# =========================================================
# DELAYED ANSWER
# =========================================================
async def delayed_riddle_answer(
    context,
    chat_id,
    business_connection_id,
    answer,
    language,
):
    """
    ۵ ثانیه صبر می‌کند بدون اینکه ربات قفل شود.
    پیام‌های دیگر در این مدت همچنان پردازش می‌شوند.
    """
    await asyncio.sleep(5)
    if language == "en":
        prefix = random.choice([
            "😂 Still thinking bro?",
            "🤣 Time's up!",
            "😎 Let's reveal it!",
        ])
    else:
        prefix = random.choice([
            "😂 داش هنوز داری فکر می‌کنی؟",
            "🤣 خب رفیق، جوابو لو بدیم!",
            "😎 وقتشه جواب رو بفهمی!",
            "😂 این یکی سخت بود داش!",
        ])
    final_text = prefix + "\n\n" + answer
    try:
        if business_connection_id:
            await context.bot.send_message(
                chat_id=chat_id,
                text=final_text,
                business_connection_id=business_connection_id,
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=final_text,
            )
    except Exception as error:
        print(
            "DELAYED ANSWER ERROR:",
            repr(error)
        )
# =========================================================
# MAIN MESSAGE PROCESSOR
# =========================================================
async def handle_text(
    message,
    context,
    business_connection_id=None,
):
    if not message:
        return
    if not message.text:
        return
    original = message.text.strip()
    if not original:
        return
    text = clean_text(original)
    language = detect_language(original)
    chat_id = message.chat_id
    # =====================================================
    # RIDDLE
    # =====================================================
    if any(word in text for word in [
        "چیستان",
        "معما",
        "riddle",
    ]):
        if language == "en":
            question, answer = random.choice(RIDDLES_EN)
        else:
            question, answer = random.choice(RIDDLES_FA)
        await send_message(
            context,
            message,
            question,
            business_connection_id,
        )
        asyncio.create_task(
            delayed_riddle_answer(
                context,
                chat_id,
                business_connection_id,
                answer,
                language,
            )
        )
        return
    # =====================================================
    # STORY
    # =====================================================
    if any(word in text for word in [
        "داستان",
        "قصه",
        "story",
    ]):
        if language == "en":
            story = random_reply(
                str(chat_id) + "-story-en",
                STORIES_EN,
            )
        else:
            story = random_reply(
                str(chat_id) + "-story-fa",
                STORIES_FA,
            )
        await send_message(
            context,
            message,
            story,
            business_connection_id,
        )
        return
    # =====================================================
    # JOKE
    # =====================================================
    if any(word in text for word in [
        "شوخی",
        "جوک",
        "لطیفه",
        "joke",
        "funny",
    ]):
        if language == "en":
            joke = random_reply(
                str(chat_id) + "-joke-en",
                JOKES_EN,
            )
        else:
            joke = random_reply(
                str(chat_id) + "-joke-fa",
                JOKES_FA,
            )
        await send_message(
            context,
            message,
            joke,
            business_connection_id,
        )
        return
    # =====================================================
    # RANDOM
    # =====================================================
    if any(word in text for word in [
        "شانسی",
        "تصادفی",
        "random",
        "surprise",
    ]):
        category = random.choice([
            "riddle",
            "story",
            "joke",
        ])
        if category == "riddle":
            if language == "en":
                question, answer = random.choice(RIDDLES_EN)
            else:
                question, answer = random.choice(RIDDLES_FA)
            await send_message(
                context,
                message,
                question,
                business_connection_id,
            )
            asyncio.create_task(
                delayed_riddle_answer(
                    context,
                    chat_id,
                    business_connection_id,
                    answer,
                    language,
                )
            )
        elif category == "story":
            if language == "en":
                result = random.choice(STORIES_EN)
            else:
                result = random.choice(STORIES_FA)
            await send_message(
                context,
                message,
                result,
                business_connection_id,
            )
        else:
            if language == "en":
                result = random.choice(JOKES_EN)
            else:
                result = random.choice(JOKES_FA)
            await send_message(
                context,
                message,
                result,
                business_connection_id,
            )
        return
    # =====================================================
    # HELLO
    # =====================================================
    if any(word in text for word in [
        "سلام",
        "سلاممم",
        "درود",
        "salam",
        "hello",
        "hi",
        "hey",
    ]):
        if language == "en":
            response = random_reply(
                str(chat_id) + "-hello-en",
                HELLO_EN,
            )
        else:
            response = random_reply(
                str(chat_id) + "-hello-fa",
                HELLO_FA,
            )
        await send_message(
            context,
            message,
            response,
            business_connection_id,
        )
        return
    # =====================================================
    # THANKS
    # =====================================================
    if any(word in text for word in [
        "مرسی",
        "ممنون",
        "تشکر",
        "سپاس",
        "دمت گرم",
        "thanks",
        "thank you",
    ]):
        if language == "en":
            response = random_reply(
                str(chat_id) + "-thanks-en",
                THANKS_EN,
            )
        else:
            response = random_reply(
                str(chat_id) + "-thanks-fa",
                THANKS_FA,
            )
        await send_message(
            context,
            message,
            response,
            business_connection_id,
        )
        return
    # =====================================================
    # WHERE
    # =====================================================
    if any(word in text for word in [
        "کجایی",
        "کجاست",
        "کجاستی",
        "where are you",
        "where is he",
    ]):
        if language == "en":
            response = random_reply(
                str(chat_id) + "-where-en",
                WHERE_EN,
            )
        else:
            response = random_reply(
                str(chat_id) + "-where-fa",
                WHERE_FA,
            )
        await send_message(
            context,
            message,
            response,
            business_connection_id,
        )
        return
    # =====================================================
    # NORMAL MESSAGE
    # =====================================================
    if language == "en":
        response = random_reply(
            str(chat_id) + "-general-en",
            GENERAL_EN,
        )
        response += "\n\n" + get_time_reply(
            "en",
            str(chat_id),
        )
    else:
        response = random_reply(
            str(chat_id) + "-general-fa",
            GENERAL_FA,
        )
        response += "\n\n" + get_time_reply(
            "fa",
            str(chat_id),
        )
    await send_message(
        context,
        message,
        response,
        business_connection_id,
    )
# =========================================================
# NORMAL BOT MESSAGE
# =========================================================
async def normal_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message:
        await handle_text(
            update.message,
            context,
            None,
        )
# =========================================================
# TELEGRAM BUSINESS / CHAT AUTOMATION
# =========================================================
async def business_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.business_message
    if not message:
        return
    connection_id = (
        message.business_connection_id
    )
    print(
        "BUSINESS MESSAGE RECEIVED:",
        message.chat_id,
        connection_id,
    )
    await handle_text(
        message,
        context,
        connection_id,
    )
# =========================================================
# START
# =========================================================
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return
    await update.message.reply_text(
        "🤖🔥 Spixle Bot فعال است!\n\n"
        "چیستان = چیستان\n"
        "داستان = داستان\n"
        "شوخی = جوک\n"
        "شانسی = یک چیز تصادفی\n\n"
        "فارسی یا English، خودم زبان پیام رو تشخیص می‌دم 😎"
    )
# =========================================================
# APPLICATION
# =========================================================
app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)
# دستور /start
app.add_handler(
    CommandHandler(
        "start",
        start,
    )
)
# پیام‌های عادی Bot
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        normal_message,
    )
)
# پیام‌های Telegram Business / Chat Automation
app.add_handler(
    MessageHandler(
        filters.UpdateType.BUSINESS_MESSAGE,
        business_message,
    )
)
# =========================================================
# START BOT
# =========================================================
print("====================================")
print("🤖🔥 SPIXLE BOT STARTING")
print("Business / Chat Automation: ON")
print("Persian / English: ON")
print("Riddle 5-second answer: ON")
print("Story: ON")
print("Jokes: ON")
print("Random mode: ON")
print("Timezone: Asia/Kabul")
print("====================================")
app.run_polling(
    allowed_updates=[
        "message",
        "business_connection",
        "business_message",
        "edited_business_message",
    ]
)
