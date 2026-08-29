import os
import random
import asyncio
import re
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
# تنظیمات اصلی
# =========================================================
TOKEN = os.environ["TOKEN"]
TIMEZONE = "Asia/Kabul"
# برای جلوگیری از جواب کاملاً تکراری
last_replies = {}
# =========================================================
# ابزارهای کمکی
# =========================================================
def normalize(text: str) -> str:
    """تمیز کردن متن فارسی و انگلیسی."""
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
def is_english(text: str) -> bool:
    """تشخیص ساده زبان پیام."""
    english_chars = len(re.findall(r"[a-zA-Z]", text))
    persian_chars = len(re.findall(r"[\u0600-\u06FF]", text))
    return english_chars > persian_chars
def choose_random(chat_id, options):
    """انتخاب جواب تصادفی بدون تکرار پشت سر هم."""
    if not options:
        return ""
    previous = last_replies.get(chat_id)
    available = [
        item for item in options
        if item != previous
    ]
    if not available:
        available = options
    result = random.choice(available)
    last_replies[chat_id] = result
    return result
def kabul_hour():
    """گرفتن ساعت افغانستان."""
    return datetime.now(
        ZoneInfo(TIMEZONE)
    ).hour
# =========================================================
# سلام فارسی
# =========================================================
HELLO_FA = [
    "سلاممم داش 👋😎 فعلاً صاحب ربات اینجا نیست، ولی من سر پستم 🤖",
    "به‌به سلام رفیق 😂🤝 پیامت سالم رسید!",
    "سلام داش 🔥🤖 فعلاً من نگهبان اینجام.",
    "سلام رفیق 😎📩 صاحب ربات فعلاً در دسترس نیست.",
    "سلاممم 😂 من زودتر از صاحب ربات جواب دادم!",
]
# =========================================================
# سلام انگلیسی
# =========================================================
HELLO_EN = [
    "Hey bro! 👋😎 The owner is currently away, but I'm on duty. 🤖",
    "Hello! 🤖🔥 Your message has been received.",
    "Hey! 😂📩 The owner isn't available right now.",
    "Hello bro! 😎 The robot is watching the inbox.",
]
# =========================================================
# تشکر
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
# کجایی؟
# =========================================================
WHERE_FA = [
    "فعلاً صاحب ربات در دسترس نیست 😎📵 پیامت رو بذار.",
    "کجاست؟ 😂 داش منم خبر ندارم!",
    "فعلاً غایبه رفیق 🤖📩 ولی پیامت رسید.",
    "صاحب ربات فعلاً نیست؛ من جای خالی‌شو پر کردم 😂",
]
WHERE_EN = [
    "The owner is currently away 😎📵 Leave your message here.",
    "Where is he? 😂 I have no idea!",
    "He's currently unavailable, but your message arrived 🤖📩",
    "The owner is away, so I'm covering the inbox 😂",
]
# =========================================================
# پاسخ‌های عمومی فارسی
# =========================================================
GENERAL_FA = [
    "😂 داش اینو دیگه باید صاحب ربات خودش ببینه! پیامت ثبت شد 🤖📩",
    "😎 پیامت رسید رفیق؛ فعلاً من نگهبان اینجام 🤖",
    "🤣 دریافت شد داش! پیام گم نمی‌شه.",
    "🤖 پیام وارد سیستم شد؛ بعداً صاحب ربات می‌بینتش.",
    "😂 گرفتم رفیق! فعلاً ربات سر پسته.",
    "📩 پیامت رسید؛ من تحویلش گرفتم 😎🤖",
    "😂 صاحب ربات نیست، ولی صندوق پیام‌ها بیکار نیست!",
]
# =========================================================
# پاسخ‌های عمومی انگلیسی
# =========================================================
GENERAL_EN = [
    "😂 Got your message bro! The owner is currently away. 🤖📩",
    "😎 Message received! The owner will see it later.",
    "🤖 Your message has been received.",
    "😂 Got it bro! The robot is still on duty.",
    "📩 Message received and safely delivered.",
]
# =========================================================
# صبح / ظهر / عصر / شب
# =========================================================
MORNING_FA = [
    "صبح قشنگت بخیر داش ☀️😎 فعلاً صاحب ربات نیست؛ یه پیام بنداز اینجا!",
    "صبح بخیر رفیق ☀️🤖 من فعلاً نگهبان صندوق پیامم.",
    "صبح بخیر داش 😂☕️ صاحب ربات فعلاً نیست، ولی پیامت رسید.",
]
NOON_FA = [
    "ظهر بخیر داش 🌞😎 فعلاً صاحب ربات در دسترس نیست، پیامت رو بذار.",
    "وسط روز رسیدی 😂☀️ پیامت ثبت شد، بعداً دیده می‌شه.",
    "ظهر به‌خیر رفیق 🌞🤖 فعلاً من سر پستم!",
]
AFTERNOON_FA = [
    "عصرت قشنگ داش 🌇😎 فعلاً صاحب ربات نیست، ولی پیام رسید.",
    "عصر بخیر رفیق 🌆🤖 پیامت اینجا محفوظ شد.",
    "عصر رسیدی 😂🌇 من فعلاً جای صاحب ربات وایسادم!",
]
NIGHT_FA = [
    "شب بخیر داش 🌙😎 فعلاً صاحب ربات در دسترس نیست.",
    "اوه، شب رسیدی 😂🌙 پیامت رسید رفیق!",
    "شب آروم رفیق 🌌🤖 فعلاً من نگهبانم.",
]
MORNING_EN = [
    "Good morning! ☀️😎 The owner is currently away.",
    "Morning bro! ☕️🤖 Your message has been received.",
]
NOON_EN = [
    "Good afternoon! 🌞😎 The owner is currently away.",
    "Afternoon bro! 🤖📩 Your message has been received.",
]
AFTERNOON_EN = [
    "Good evening! 🌇😎 The owner is currently away.",
    "Evening bro! 🤖📩 Your message is safe.",
]
NIGHT_EN = [
    "Good night! 🌙😎 The owner is currently away.",
    "Night bro! 🌌🤖 Your message has been received.",
]
def time_message(english=False):
    hour = kabul_hour()
    if english:
        if 5 <= hour < 11:
            return choose_random("time-en-morning", MORNING_EN)
        if 11 <= hour < 15:
            return choose_random("time-en-noon", NOON_EN)
        if 15 <= hour < 19:
            return choose_random("time-en-afternoon", AFTERNOON_EN)
        return choose_random("time-en-night", NIGHT_EN)
    else:
        if 5 <= hour < 11:
            return choose_random("time-fa-morning", MORNING_FA)
        if 11 <= hour < 15:
            return choose_random("time-fa-noon", NOON_FA)
        if 15 <= hour < 19:
            return choose_random("time-fa-afternoon", AFTERNOON_FA)
        return choose_random("time-fa-night", NIGHT_FA)
# =========================================================
# چیستان فارسی
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
# =========================================================
# چیستان انگلیسی
# =========================================================
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
# داستان فارسی
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
# =========================================================
# داستان انگلیسی
# =========================================================
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
# شوخی فارسی
# =========================================================
JOKES_FA = [
    "چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود! 💻🤣",
    "به وای‌فای گفتم حالت چطوره؟ گفت: «اتصال ندارم!» 📡😂",
    "ربات گفت خسته نمی‌شم؛ پنج دقیقه بعد رفت Sleep Mode 🤖💤",
    "به کامپیوتر گفتن چرا ساکتی؟ گفت: «دارم پردازش می‌کنم داش!» 😂",
    "گفتم اینترنت چرا کندی؟ گفت: «منم مثل تو حوصله ندارم!» 😂📡",
    "ربات رفت باشگاه؛ برگشت گفت: «آپدیت شدم!» 🤖😂",
]
# =========================================================
# شوخی انگلیسی
# =========================================================
JOKES_EN = [
    "Why did the computer go to the doctor? Because it had a virus! 💻🤣",
    "I asked Wi-Fi how it was doing. It said: 'No connection!' 📡😂",
    "The robot said it never gets tired. Five minutes later: Sleep Mode 🤖💤",
    "I asked the internet why it was slow. It said: 'I'm tired too!' 😂📡",
]
# =========================================================
# پیام بعد از ۵ ثانیه
# =========================================================
async def delayed_response(
    context,
    chat_id,
    business_connection_id,
    kind,
    answer,
    english,
):
    """
    این تابع ۵ ثانیه صبر می‌کند.
    از asyncio.sleep استفاده شده، بنابراین ربات در این مدت
    گیر نمی‌کند و می‌تواند پیام‌های دیگر را هم دریافت کند.
    """
    await asyncio.sleep(5)
    if kind == "riddle":
        if english:
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
    elif kind == "story":
        if english:
            final_text = random.choice([
                "😂 Story complete!",
                "🤣 And that's the end!",
                "😎 End of story!",
            ])
        else:
            final_text = random.choice([
                "😂 خب داش، داستان هم تموم شد!",
                "🤣 قسمت بعدی فعلاً در دست تولیده!",
                "😎 پایان داستان؛ ربات برگشت سر پست!",
            ])
    else:
        if english:
            final_text = random.choice([
                "😂 Did you laugh?",
                "🤣 Joke successfully delivered!",
                "😎 Robot comedy system completed!",
            ])
        else:
            final_text = random.choice([
                "😂 خندیدی یا فقط ربات خندید؟",
                "🤣 شوخی با موفقیت تحویل داده شد!",
                "😎 سیستم خنده فعال شد!",
            ])
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
            "ERROR delayed_response:",
            repr(error)
        )
# =========================================================
# ارسال پیام با Business یا معمولی
# =========================================================
async def send_reply(
    context,
    message,
    text,
    business_connection_id=None,
):
    """یک تابع مشترک برای ارسال پاسخ."""
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
            "ERROR send_reply:",
            repr(error)
        )
# =========================================================
# پردازش پیام
# =========================================================
async def process_message(
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
    text = normalize(original)
    english = is_english(original)
    chat_id = message.chat_id
    # -----------------------------------------------------
    # چیستان
    # -----------------------------------------------------
    riddle_words = [
        "چیستان",
        "معما",
        "riddle",
    ]
    if any(word in text for word in riddle_words):
        if english:
            question, answer = random.choice(RIDDLES_EN)
        else:
            question, answer = random.choice(RIDDLES_FA)
        await send_reply(
            context,
            message,
            question,
            business_connection_id,
        )
        asyncio.create_task(
            delayed_response(
                context,
                chat_id,
                business_connection_id,
                "riddle",
                answer,
                english,
            )
        )
        return
    # -----------------------------------------------------
    # داستان
    # -----------------------------------------------------
    story_words = [
        "داستان",
        "قصه",
        "story",
    ]
    if any(word in text for word in story_words):
        if english:
            story = choose_random(
                chat_id,
                STORIES_EN,
            )
        else:
            story = choose_random(
                chat_id,
                STORIES_FA,
            )
        await send_reply(
            context,
            message,
            story,
            business_connection_id,
        )
        asyncio.create_task(
            delayed_response(
                context,
                chat_id,
                business_connection_id,
                "story",
                None,
                english,
            )
        )
        return
    # -----------------------------------------------------
    # شوخی
    # -----------------------------------------------------
    joke_words = [
        "شوخی",
        "جوک",
        "لطیفه",
        "joke",
        "funny",
    ]
    if any(word in text for word in joke_words):
        if english:
            joke = choose_random(
                chat_id,
                JOKES_EN,
            )
        else:
            joke = choose_random(
                chat_id,
                JOKES_FA,
            )
        await send_reply(
            context,
            message,
            joke,
            business_connection_id,
        )
        asyncio.create_task(
            delayed_response(
                context,
                chat_id,
                business_connection_id,
                "joke",
                None,
                english,
            )
        )
        return
    # -----------------------------------------------------
    # شانسی
    # -----------------------------------------------------
    random_words = [
        "شانسی",
        "تصادفی",
        "random",
        "surprise",
    ]
    if any(word in text for word in random_words):
        kind = random.choice([
            "riddle",
            "story",
            "joke",
        ])
        answer = None
        if kind == "riddle":
            if english:
                content, answer = random.choice(
                    RIDDLES_EN
                )
            else:
                content, answer = random.choice(
                    RIDDLES_FA
                )
        elif kind == "story":
            if english:
                content = choose_random(
                    chat_id,
                    STORIES_EN,
                )
            else:
                content = choose_random(
                    chat_id,
                    STORIES_FA,
                )
        else:
            if english:
                content = choose_random(
                    chat_id,
                    JOKES_EN,
                )
            else:
                content = choose_random(
                    chat_id,
                    JOKES_FA,
                )
        await send_reply(
            context,
            message,
            content,
            business_connection_id,
        )
        asyncio.create_task(
            delayed_response(
                context,
                chat_id,
                business_connection_id,
                kind,
                answer,
                english,
            )
        )
        return
    # -----------------------------------------------------
    # سلام
    # -----------------------------------------------------
    hello_words = [
        "سلام",
        "سلاممم",
        "درود",
        "salam",
        "hello",
        "hi",
        "hey",
    ]
    if any(word in text for word in hello_words):
        if english:
            response = choose_random(
                chat_id,
                HELLO_EN,
            )
        else:
            response = choose_random(
                chat_id,
                HELLO_FA,
            )
        await send_reply(
            context,
            message,
            response,
            business_connection_id,
        )
        return
    # -----------------------------------------------------
    # تشکر
    # -----------------------------------------------------
    thanks_words = [
        "مرسی",
        "ممنون",
        "تشکر",
        "سپاس",
        "دمت گرم",
        "thanks",
        "thank you",
    ]
    if any(word in text for word in thanks_words):
        if english:
            response = choose_random(
                chat_id,
                THANKS_EN,
            )
        else:
            response = choose_random(
                chat_id,
                THANKS_FA,
            )
        await send_reply(
            context,
            message,
            response,
            business_connection_id,
        )
        return
    # -----------------------------------------------------
    # کجایی؟
    # -----------------------------------------------------
    where_words = [
        "کجایی",
        "کجاست",
        "کجاستی",
        "where are you",
        "where is he",
    ]
    if any(word in text for word in where_words):
        if english:
            response = choose_random(
                chat_id,
                WHERE_EN,
            )
        else:
            response = choose_random(
                chat_id,
                WHERE_FA,
            )
        await send_reply(
            context,
            message,
            response,
            business_connection_id,
        )
        return
    # -----------------------------------------------------
    # پاسخ عمومی
    # -----------------------------------------------------
    if english:
        response = choose_random(
            chat_id,
            GENERAL_EN,
        )
        response += "\n\n" + time_message(True)
    else:
        response = choose_random(
            chat_id,
            GENERAL_FA,
        )
        response += "\n\n" + time_message(False)
    await send_reply(
        context,
        message,
        response,
        business_connection_id,
    )
# =========================================================
# پیام معمولی Bot
# =========================================================
async def normal_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return
    await process_message(
        update.message,
        context,
        None,
    )
# =========================================================
# پیام Chat Automation / Business
# =========================================================
async def business_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.business_message
    if not message:
        return
    connection_id = message.business_connection_id
    print(
        "BUSINESS MESSAGE:",
        message.chat_id,
        connection_id,
    )
    await process_message(
        message,
        context,
        connection_id,
    )
# =========================================================
# دستور Start
# =========================================================
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🤖🔥 Spixle Bot فعال شد!\n\n"
        "می‌تونی بنویسی:\n\n"
        "چیستان\n"
        "داستان\n"
        "شوخی\n"
        "شانسی\n\n"
        "یا هر پیام معمولی دیگه‌ای 😎"
    )
# =========================================================
# ساخت Application
# =========================================================
app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)
# =========================================================
# Handler دستور Start
# =========================================================
app.add_handler(
    CommandHandler(
        "start",
        start,
    )
)
# =========================================================
# پیام‌های معمولی خود Bot
# =========================================================
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        normal_message,
    )
)
# =========================================================
# پیام‌های Business / Chat Automation
# =========================================================
app.add_handler(
    MessageHandler(
        filters.UpdateType.BUSINESS_MESSAGE,
        business_message,
    )
)
# =========================================================
# شروع
# =========================================================
print(
    "===================================="
)
print(
    "🤖🔥 Spixle Bot is starting..."
)
print(
    "Business Automation: ENABLED"
)
print(
    "Persian/English detection: ENABLED"
)
print(
    "Riddle / Story / Joke / Random: ENABLED"
)
print(
    "5 second delayed answers: ENABLED"
)
print(
    "Timezone: Asia/Kabul"
)
print(
    "===================================="
)
app.run_polling(
    allowed_updates=[
        "message",
        "business_connection",
        "business_message",
        "edited_business_message",
    ]
)
