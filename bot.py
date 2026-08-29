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
# تنظیمات
# =========================================================
TOKEN = os.environ["TOKEN"]
TIMEZONE = "Asia/Kabul"
# برای هر چت، جواب قبلی جدا نگهداری می‌شود
last_replies = {}
# =========================================================
# ابزارهای کمکی
# =========================================================
def normalize(text):
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
def is_english(text):
    english = len(re.findall(r"[a-zA-Z]", text))
    persian = len(re.findall(r"[\u0600-\u06FF]", text))
    return english > persian
def random_no_repeat(chat_id, items):
    if not items:
        return ""
    previous = last_replies.get(chat_id)
    choices = [item for item in items if item != previous]
    if not choices:
        choices = items
    result = random.choice(choices)
    last_replies[chat_id] = result
    return result
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
        "چیستان:\nچه چیزی همیشه جلو می‌رود ولی هیچ‌وقت برنمی‌گردد؟",
        "جواب: زمان ⏳"
    ),
    (
        "چیستان:\nهرچه بیشتر خشک می‌کند، خودش خیس‌تر می‌شود. چیست؟",
        "جواب: حوله 😂"
    ),
    (
        "چیستان:\nچه چیزی دهان دارد ولی غذا نمی‌خورد؟",
        "جواب: رودخانه 🌊"
    ),
    (
        "چیستان:\nچه چیزی پا دارد ولی راه نمی‌رود؟",
        "جواب: میز 🪑"
    ),
    (
        "چیستان:\nچه چیزی پر از سوراخ است ولی آب را نگه می‌دارد؟",
        "جواب: اسفنج 🧽"
    ),
    (
        "چیستان:\nچه چیزی وقتی اسمش را می‌گویی، می‌شکند؟",
        "جواب: سکوت 🤫"
    ),
    (
        "چیستان:\nچه چیزی بالا می‌رود ولی پایین نمی‌آید؟",
        "جواب: سن آدم 😎"
    ),
    (
        "چیستان:\nچه چیزی چشم دارد ولی نمی‌بیند؟",
        "جواب: سوزن 🪡"
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
        "Riddle:\nWhat has a mouth but never eats?",
        "Answer: A river 🌊"
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
    "داستان:\nیک ربات تصمیم گرفت یک روز کامل استراحت کند. "
    "پنج دقیقه بعد صاحبش پیام داد: «کجایی؟» "
    "ربات گفت: «داش استراحتم هم کنسل شد 😂🤖»",
    "داستان:\nیک نفر از ربات پرسید: «تو همه‌چیز رو بلدی؟» "
    "ربات گفت: «نه داش، رمز وای‌فای رو هنوز بهم نگفتن 😂📡»",
    "داستان:\nربات منتظر پیام صاحبش بود. "
    "بالاخره گوشی زنگ خورد. "
    "ربات گفت: «می‌دونستم! شیفتم تموم نشده 😂🤖»",
    "داستان:\nیک نفر گفت: «امروز خیلی کار دارم.» "
    "ربات گفت: «منم همین‌طور.» "
    "گفت: «چه کاری؟» "
    "ربات گفت: «منتظر موندن برای پیام بعدی تو 😂»",
    "داستان:\nربات یک روز تصمیم گرفت شوخی نکند. "
    "سه دقیقه بعد خودش خندید و گفت: "
    "«این تصمیم هم مثل بقیه تصمیم‌هام موفق نبود 😂🤖»",
]
# =========================================================
# داستان انگلیسی
# =========================================================
STORIES_EN = [
    "Story:\nA robot decided to take a full day off. "
    "Five minutes later, its owner asked: 'Where are you?' "
    "The robot replied: 'My vacation is already cancelled 😂🤖'",
    "Story:\nSomeone asked a robot: 'Do you know everything?' "
    "The robot said: 'No bro, they still haven't told me the Wi-Fi password 😂📡'",
    "Story:\nA robot was waiting for a message. "
    "The phone finally buzzed. "
    "The robot said: 'I knew it! My shift isn't over 😂🤖'",
    "Story:\nSomeone said: 'I have so much work today.' "
    "The robot replied: 'Same.' "
    "They asked: 'What work?' "
    "The robot said: 'Waiting for your next message 😂'",
]
# =========================================================
# شوخی فارسی
# =========================================================
JOKES_FA = [
    "چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود! 💻🤣",
    "به وای‌فای گفتم حالت چطوره؟ گفت: «اتصال ندارم!» 📡😂",
    "ربات گفت من هیچ‌وقت خسته نمی‌شم؛ پنج دقیقه بعد رفت Sleep Mode. 🤖💤",
    "به کامپیوتر گفتن چرا ساکتی؟ گفت: «دارم پردازش می‌کنم داش!» 🤖😂",
    "یکی به ربات گفت چرا دیر جواب میدی؟ گفت: «داش داشتم فکر می‌کردم!» 😂🤖",
    "گفتم اینترنت چرا اینقدر کندی؟ گفت: «منم مثل تو حوصله ندارم!» 😂📡",
    "کامپیوتر گفت حافظه‌ام پر شده. گفتم چی توش ریختی؟ گفت: «خاطرات بدت رو!» 😂💻",
    "ربات رفت باشگاه که قوی بشه؛ برگشت گفت: «آپدیت شدم!» 🤖💪😂",
]
# =========================================================
# شوخی انگلیسی
# =========================================================
JOKES_EN = [
    "Why did the computer go to the doctor? Because it had a virus! 💻🤣",
    "I asked Wi-Fi how it was doing. It said: 'No connection!' 📡😂",
    "The robot said it never gets tired. Five minutes later: Sleep Mode. 🤖💤",
    "Someone asked the computer why it was quiet. It said: 'I'm processing!' 🤖😂",
    "I asked the internet why it was slow. It said: 'I'm tired too!' 😂📡",
]
# =========================================================
# جواب‌های عمومی فارسی
# =========================================================
GENERAL_FA = [
    "😂 داش اینو دیگه باید صاحب ربات خودش ببینه! پیامت ثبت شد 🤖📩",
    "😎 پیامت با موفقیت رسید. من فعلاً نگهبان اینجام 🤖",
    "😂 دریافت شد رفیق! فعلاً صاحب ربات آفلاینه 📩",
    "🤖 پیامت وارد سیستم شد؛ بعداً صاحب ربات می‌بینتش 😎",
    "🤣 داش پیام رسید، نگران نباش گم نمی‌شه!",
    "😎 ثبت شد رفیق. ربات همچنان سر پسته 🤖🔥",
]
# =========================================================
# جواب‌های عمومی انگلیسی
# =========================================================
GENERAL_EN = [
    "😂 Got your message bro! The owner is currently away. 🤖📩",
    "😎 Message received! The owner will see it later.",
    "🤖 Your message has been registered successfully!",
    "😂 Got it! The robot is still on duty.",
    "😎 Message received and safely delivered to the robot system.",
]
# =========================================================
# جواب سلام
# =========================================================
HELLO_FA = [
    "سلاممم داش 👋😎 فعلاً صاحب ربات اینجا نیست، ولی من هستم 🤖",
    "به‌به سلام رفیق 😂🤝 پیامت رسید!",
    "سلام داش! 🤖🔥 فعلاً من نگهبان اینجام.",
    "سلام رفیق 👋😎 صاحب ربات فعلاً آفلاینه.",
]
HELLO_EN = [
    "Hey bro! 👋😎 The owner is away right now.",
    "Hello! 🤖🔥 Your message has been received.",
    "Hey! 👋 The robot is currently on duty.",
    "Hello bro! 😎📩 The owner will see your message later.",
]
# =========================================================
# جواب تشکر
# =========================================================
THANKS_FA = [
    "خواهش می‌کنم داش 😎🤝",
    "قابلی نداشت رفیق 😂✌️",
    "دمت گرم داش 🔥",
    "خواهش داش! ربات در خدمتته 🤖😂",
]
THANKS_EN = [
    "You're welcome bro! 😎🤝",
    "Anytime! 🤖🔥",
    "No problem! 😂✌️",
    "You're welcome! The robot is always on duty 🤖",
]
# =========================================================
# جواب کجایی
# =========================================================
WHERE_FA = [
    "فعلاً صاحب ربات در دسترس نیست 😎📵",
    "کجاست؟ 😂 داش خبر ندارم!",
    "فعلاً غایبه رفیق 🤖📩 ولی پیامت رسید.",
    "صاحب ربات فعلاً بیرونه؛ من نگهبانی میدم 😎🤖",
]
WHERE_EN = [
    "The owner is currently away 😎📵",
    "Where is he? 😂 I have no idea!",
    "He's currently unavailable, but your message arrived 🤖📩",
    "The owner is away. I'm keeping watch 😎🤖",
]
# =========================================================
# واکنش‌های چیستان
# =========================================================
RIDDLE_REACTIONS_FA = [
    "😂 داش هنوز داری فکر می‌کنی؟ ",
    "🤣 خب رفیق، مغزت جواب رو پیدا کرد؟ ",
    "😎 وقتشه جواب رو لو بدیم! ",
    "😂 جوابو پیدا نکردی؟ نگران نباش، ربات نجاتت میده! ",
    "🤣 داش این یکی سخت بود، قبول دارم! ",
]
RIDDLE_REACTIONS_EN = [
    "😂 Still thinking bro? ",
    "🤣 Did you figure it out? ",
    "😎 Time to reveal the answer! ",
    "😂 Couldn't solve it? No worries! ",
]
# =========================================================
# واکنش داستان
# =========================================================
STORY_REACTIONS_FA = [
    "😂 خب داش، داستان هم تموم شد!",
    "🤣 قسمت بعدی فعلاً در دست تولیده!",
    "😎 پایان داستان؛ ربات برگشت سر پست! 🤖",
    "😂 بودجه قسمت دوم هنوز نرسیده!",
]
STORY_REACTIONS_EN = [
    "😂 Story complete!",
    "🤣 Part two is still in production!",
    "😎 Story finished. Back to robot duty! 🤖",
]
# =========================================================
# واکنش شوخی
# =========================================================
JOKE_REACTIONS_FA = [
    "😂 خندیدی یا فقط ربات خندید؟",
    "🤣 این یکی رفت تو آرشیو جوک‌های ربات!",
    "😎 شوخی با موفقیت تحویل داده شد!",
    "😂 سیستم خنده فعال شد! 🤖🔥",
]
JOKE_REACTIONS_EN = [
    "😂 Did you laugh or was it just me?",
    "🤣 Adding that one to the robot joke archive!",
    "😎 Joke successfully delivered!",
]
# =========================================================
# واکنش شانسی
# =========================================================
RANDOM_REACTIONS_FA = [
    "😂 شانست بد نبود داش!",
    "🤣 حتی خود ربات هم نمی‌دونست چی درمیاد!",
    "😎 انتخاب کاملاً شانسی بود!",
    "🤖🎲 سیستم شانس تصمیم گرفت!",
]
RANDOM_REACTIONS_EN = [
    "😂 Not bad luck this time!",
    "🤣 Even the robot didn't know what would appear!",
    "😎 Totally random!",
    "🤖🎲 The random system has spoken!",
]
# =========================================================
# پیام بعد از ۵ ثانیه
# =========================================================
async def delayed_message(
    context,
    chat_id,
    kind,
    answer,
    english,
):
    await asyncio.sleep(5)
    if kind == "riddle":
        if english:
            prefix = random.choice(RIDDLE_REACTIONS_EN)
        else:
            prefix = random.choice(RIDDLE_REACTIONS_FA)
        response = prefix + answer
    elif kind == "story":
        if english:
            response = random.choice(STORY_REACTIONS_EN)
        else:
            response = random.choice(STORY_REACTIONS_FA)
    elif kind == "joke":
        if english:
            response = random.choice(JOKE_REACTIONS_EN)
        else:
            response = random.choice(JOKE_REACTIONS_FA)
    else:
        if english:
            response = random.choice(RANDOM_REACTIONS_EN)
        else:
            response = random.choice(RANDOM_REACTIONS_FA)
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=response,
        )
    except Exception as error:
        print("Delayed message error:", error)
# =========================================================
# جواب بر اساس ساعت
# =========================================================
def time_reply(english):
    hour = datetime.now(
        ZoneInfo(TIMEZONE)
    ).hour
    if english:
        if 5 <= hour < 11:
            return (
                "Good morning! ☀️🤖 "
                "The owner is currently away. "
                "Leave your message and he'll see it later."
            )
        if 11 <= hour < 15:
            return (
                "Good afternoon! 🌞😎 "
                "The owner is away right now. "
                "Your message has been received."
            )
        if 15 <= hour < 19:
            return (
                "Good evening! 🌇🤖 "
                "The owner isn't available right now."
            )
        return (
            "Good night! 🌙🤖 "
            "The owner is currently away. "
            "Your message has been received."
        )
    if 5 <= hour < 11:
        return (
            "☀️ صبح بخیر داش! "
            "فعلاً صاحب ربات نیست، "
            "پیامت رو بذار؛ بعداً می‌بینتش 🤖📩"
        )
    if 11 <= hour < 15:
        return (
            "🌞 ظهر بخیر رفیق! "
            "صاحب ربات فعلاً نیست، "
            "ولی پیامت رسید 😎📩"
        )
    if 15 <= hour < 19:
        return (
            "🌇 عصر بخیر داش! "
            "فعلاً صاحب ربات در دسترس نیست، "
            "پیامت محفوظ شد 🤖📩"
        )
    return (
        "🌙 شب بخیر رفیق! "
        "صاحب ربات فعلاً نیست، "
        "ولی پیامت رسید 🤖📩"
    )
# =========================================================
# دستور شروع
# =========================================================
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🤖🔥 سلام رفیق!\n\n"
        "صاحب ربات فعلاً در دسترس نیست.\n"
        "ولی من اینجام و نگهبانی میدم 😎\n\n"
        "می‌تونی بنویسی:\n\n"
        "چیستان\n"
        "داستان\n"
        "شوخی\n"
        "شانسی\n\n"
        "یا هرچی خواستی پیام بده 📩"
    )
# =========================================================
# پردازش پیام
# =========================================================
async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return
    if not update.message.text:
        return
    original = update.message.text.strip()
    if not original:
        return
    text = normalize(original)
    english = is_english(original)
    chat_id = update.effective_chat.id
    # =====================================================
    # چیستان
    # =====================================================
    if (
        text.startswith("چیستان")
        or text.startswith("معما")
        or text.startswith("riddle")
    ):
        if english:
            question, answer = random.choice(
                RIDDLES_EN
            )
        else:
            question, answer = random.choice(
                RIDDLES_FA
            )
        await update.message.reply_text(
            question
        )
        asyncio.create_task(
            delayed_message(
                context=context,
                chat_id=chat_id,
                kind="riddle",
                answer=answer,
                english=english,
            )
        )
        return
    # =====================================================
    # داستان
    # =====================================================
    if (
        text.startswith("داستان")
        or text.startswith("قصه")
        or text.startswith("story")
    ):
        if english:
            story = random_no_repeat(
                chat_id,
                STORIES_EN
            )
        else:
            story = random_no_repeat(
                chat_id,
                STORIES_FA
            )
        await update.message.reply_text(
            story
        )
        asyncio.create_task(
            delayed_message(
                context=context,
                chat_id=chat_id,
                kind="story",
                answer=None,
                english=english,
            )
        )
        return
    # =====================================================
    # شوخی
    # =====================================================
    if (
        text.startswith("شوخی")
        or text.startswith("جوک")
        or text.startswith("joke")
    ):
        if english:
            joke = random_no_repeat(
                chat_id,
                JOKES_EN
            )
        else:
            joke = random_no_repeat(
                chat_id,
                JOKES_FA
            )
        await update.message.reply_text(
            joke
        )
        asyncio.create_task(
            delayed_message(
                context=context,
                chat_id=chat_id,
                kind="joke",
                answer=None,
                english=english,
            )
        )
        return
    # =====================================================
    # شانسی
    # =====================================================
    if (
        text.startswith("شانسی")
        or text.startswith("تصادفی")
        or text.startswith("random")
    ):
        kind = random.choice([
            "riddle",
            "story",
            "joke",
        ])
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
            answer = None
            if english:
                content = random_no_repeat(
                    chat_id,
                    STORIES_EN
                )
            else:
                content = random_no_repeat(
                    chat_id,
                    STORIES_FA
                )
        else:
            answer = None
            if english:
                content = random_no_repeat(
                    chat_id,
                    JOKES_EN
                )
            else:
                content = random_no_repeat(
                    chat_id,
                    JOKES_FA
                )
        await update.message.reply_text(
            content
        )
        asyncio.create_task(
            delayed_message(
                context=context,
                chat_id=chat_id,
                kind=kind,
                answer=answer,
                english=english,
            )
        )
        return
    # =====================================================
    # سلام
    # =====================================================
    if (
        text.startswith("سلام")
        or text.startswith("درود")
        or text.startswith("salam")
        or text.startswith("hello")
        or text.startswith("hi")
        or text.startswith("hey")
    ):
        if english:
            response = random_no_repeat(
                chat_id,
                HELLO_EN
            )
        else:
            response = random_no_repeat(
                chat_id,
                HELLO_FA
            )
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # تشکر
    # =====================================================
    if (
        "مرسی" in text
        or "ممنون" in text
        or "تشکر" in text
        or "دمت گرم" in text
        or "thanks" in text
        or "thank you" in text
    ):
        if english:
            response = random_no_repeat(
                chat_id,
                THANKS_EN
            )
        else:
            response = random_no_repeat(
                chat_id,
                THANKS_FA
            )
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # کجایی
    # =====================================================
    if (
        "کجایی" in text
        or "کجاست" in text
        or "where are you" in text
    ):
        if english:
            response = random_no_repeat(
                chat_id,
                WHERE_EN
            )
        else:
            response = random_no_repeat(
                chat_id,
                WHERE_FA
            )
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # خنده و شوخی کاربر
    # =====================================================
    if (
        "😂" in original
        or "🤣" in original
        or "😆" in original
        or "هههه" in text
        or "خخخ" in text
        or "haha" in text
        or "hahaha" in text
        or "lol" in text
    ):
        if english:
            response = random_no_repeat(
                chat_id,
                JOKES_EN
            )
        else:
            response = random_no_repeat(
                chat_id,
                [
                    "😂😂 منم خندیدم داش!",
                    "🤣 رفیق سیستم خنده فعال شد!",
                    "😂 این دیگه رسماً رفت تو آرشیو ربات!",
                    "😎😂 خوب بود داش، قبول!",
                ]
            )
        await update.message.reply_text(
            response
        )
        return
    # =====================================================
    # پیام معمولی
    # =====================================================
    if english:
        response = random_no_repeat(
            chat_id,
            GENERAL_EN
        )
    else:
        response = random_no_repeat(
            chat_id,
            GENERAL_FA
        )
    # اگر پیام معمولی بود، حال‌وهوای ساعت را هم اضافه می‌کنیم
    await update.message.reply_text(
        response
        + "\n\n"
        + time_reply(english)
    )
# =========================================================
# ساخت برنامه
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
        handle_message
    )
)
print("🤖🔥 BOT IS RUNNING...")
app.run_polling()
