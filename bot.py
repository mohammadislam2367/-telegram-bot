import os
import ast
import math
import random
import operator as op
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
# CONFIG
# =========================================================

TOKEN = os.environ["TOKEN"]
IRAN_TZ = ZoneInfo("Asia/Tehran")

# اطلاعات موقت بازی‌ها
games = {}

# امتیاز کاربران
scores = {}

# جلوگیری از پاسخ تکراری
last_answers = {}


# =========================================================
# RANDOM HELPER
# =========================================================

def random_unique(user_id, items):
    previous = last_answers.get(user_id)

    choices = [x for x in items if x != previous]

    if not choices:
        choices = items

    result = random.choice(choices)
    last_answers[user_id] = result

    return result


def add_score(user_id, amount):
    scores[user_id] = scores.get(user_id, 0) + amount


# =========================================================
# RIDDLES - 10
# =========================================================

RIDDLES = [
    ("هرچی بیشتر ازش برداری، بزرگ‌تر میشه. چیه؟", "چاله"),
    ("چه چیزی دست دارد ولی نمی‌تواند دست بزند؟", "ساعت"),
    ("چه چیزی هرچه بیشتر خشک می‌کند، خودش خیس‌تر می‌شود؟", "حوله"),
    ("چه چیزی سوراخ‌های زیادی دارد ولی آب را نگه می‌دارد؟", "اسفنج"),
    ("چه چیزی چشم دارد ولی نمی‌بیند؟", "سوزن"),
    ("چه چیزی پا دارد ولی راه نمی‌رود؟", "میز"),
    ("چه چیزی بالا می‌رود ولی پایین نمی‌آید؟", "سن"),
    ("چه چیزی کلید دارد ولی قفل باز نمی‌کند؟", "پیانو"),
    ("چه چیزی می‌دود ولی پا ندارد؟", "آب"),
    ("چه چیزی وقتی می‌شکند، صدا ندارد؟", "قول"),
]


# =========================================================
# STORIES - 10
# =========================================================

STORIES = [
    "یک ربات تصمیم گرفت یک روز استراحت کند. پنج دقیقه بعد پیام آمد: «کجایی؟» ربات گفت: «داش استراحتم هم کنسل شد!» 😂",

    "یکی از ربات پرسید: «همه‌چیز بلدی؟» گفت: «نه داش، رمز وای‌فای رو هنوز بهم نگفتن!» 😂📡",

    "ربات منتظر پیام بود. گوشی زنگ خورد و گفت: «می‌دونستم! شیفتم تموم نشده!» 🤖",

    "یکی گفت: «امروز خیلی کار دارم.» ربات گفت: «منم.» گفت: «چه کاری؟» گفت: «منتظر پیام بعدی تو!» 😂",

    "ربات رفت بخوابه. درست وقتی خوابش برد، یک پیام آمد. گفت: «باشه، خواب هم کنسل شد!» 😂",

    "یکی پرسید: «تو هیچ‌وقت خسته نمی‌شی؟» ربات گفت: «از کار نه، از سؤال تکراری چرا!» 😂",

    "ربات تصمیم گرفت امروز هیچ جوابی ندهد. سه ثانیه بعد خودش گفت: «نه بابا، نمی‌تونم!» 🤖😂",

    "ربات وارد مهمانی شد. همه گفتند: «رقص بلدی؟» گفت: «نه، ولی می‌تونم سیستم رو ری‌استارت کنم!» 😂",

    "یکی گفت: «چرا همیشه آنلاینی؟» ربات گفت: «هنوز کسی دکمه خاموش رو پیدا نکرده!» 🤖",

    "ربات گفت: «امروز خیلی آرامم.» همان لحظه ده پیام آمد. گفت: «خب... حرفم رو پس می‌گیرم!» 😂",
]


# =========================================================
# JOKES - 10
# =========================================================

JOKES = [
    "چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود! 😂💻",
    "به وای‌فای گفتم حالت چطوره؟ گفت: «اتصال ندارم!» 😂📡",
    "ربات گفت خسته نمی‌شم؛ پنج دقیقه بعد رفت Sleep Mode! 🤖",
    "به کامپیوتر گفتن چرا ساکتی؟ گفت: «دارم پردازش می‌کنم داش!» 😂",
    "گفتم اینترنت چرا کندی؟ گفت: «منم مثل تو حوصله ندارم!» 😂",
    "ربات رفت باشگاه؛ برگشت گفت: «آپدیت شدم!» 🤖😂",
    "گوشی به شارژر گفت: «بدون تو نمی‌تونم.» شارژر گفت: «این رابطه وابستگیه!» 😂",
    "کامپیوتر گفت من حافظه خوبی دارم. گفتن: «پس رمزمو بگو!» ساکت شد 😂",
    "ربات گفت امروز رژیم گرفتم؛ بعد یک فایل ۵۰۰ مگابایتی خورد 😂",
    "اینترنت گفت: «الان میام.» پنج دقیقه بعد هنوز داشت می‌اومد 😂📡",
]


# =========================================================
# FACTS - 10
# =========================================================

FACTS = [
    "اختاپوس سه قلب دارد. 🐙",
    "نور خورشید حدود ۸ دقیقه و ۲۰ ثانیه طول می‌کشد تا به زمین برسد. ☀️",
    "انسان‌ها معمولاً هفت مهره گردنی دارند.",
    "اثر انگشت هر انسان الگوی منحصربه‌فردی دارد.",
    "زمین در قطب‌ها کمی پخ‌تر از یک کره کامل است. 🌍",
    "آب می‌تواند در شرایط خاص هم‌زمان در سه حالت جامد، مایع و گاز وجود داشته باشد.",
    "زرافه هم معمولاً هفت مهره گردنی دارد. 🦒",
    "بعضی لاک‌پشت‌ها می‌توانند مدت زیادی زیر آب بمانند. 🐢",
    "عسل در شرایط مناسب می‌تواند مدت بسیار طولانی پایدار بماند. 🍯",
    "ماه نور خودش را تولید نمی‌کند و نور خورشید را بازتاب می‌دهد. 🌙",
]


# =========================================================
# FUNNY ANSWERS
# =========================================================

FUNNY = [
    "😂 داش منم موندم چی بگم!",
    "🤣 سیستم مغزم رفت روی حالت فکر کردن!",
    "😂 این یکی رو باید بذاریم برای قسمت بعد!",
    "😎 جوابش رو می‌دونم ولی فعلاً محرمانه‌ست!",
    "🤖 در حال پردازش... پردازش شکست خورد 😂",
    "🤣 داش سؤال سنگینی بود!",
    "😂 من رباتم، ولی این یکی منو گیر انداخت!",
    "😎 فعلاً این سؤال بره توی آرشیو!",
    "🤖 مغز مصنوعی نیاز به چای دارد ☕😂",
    "😂 جواب دقیق: نمی‌دونم داش!",
]


# =========================================================
# COIN
# =========================================================

async def coin(update, context):
    result = random.choice(["شیر 🪙", "خط 🪙"])

    await update.message.reply_text(
        f"🪙 انداختیم...\n\nنتیجه: {result}"
    )


# =========================================================
# DICE
# =========================================================

async def dice(update, context):
    value = random.randint(1, 6)

    await update.message.reply_text(
        f"🎲 تاس انداختیم!\n\nعدد: {value}"
    )


# =========================================================
# ROCK PAPER SCISSORS
# =========================================================

async def rps(update, context):
    choices = ["سنگ 🪨", "کاغذ 📄", "قیچی ✂️"]

    user_choice = random.choice(choices)
    bot_choice = random.choice(choices)

    if user_choice == bot_choice:
        result = "مساوی شد 😂"
    elif (
        (user_choice.startswith("سنگ") and bot_choice.startswith("قیچی"))
        or
        (user_choice.startswith("کاغذ") and bot_choice.startswith("سنگ"))
        or
        (user_choice.startswith("قیچی") and bot_choice.startswith("کاغذ"))
    ):
        result = "تو بردی! 🔥"
    else:
        result = "ربات برد 😎🤖"

    await update.message.reply_text(
        f"✊ بازی سنگ کاغذ قیچی\n\n"
        f"انتخاب تو: {user_choice}\n"
        f"انتخاب ربات: {bot_choice}\n\n"
        f"{result}"
    )


# =========================================================
# MAGIC 8 BALL
# =========================================================

MAGIC = [
    "بله 😎",
    "احتمالش زیاده!",
    "فعلاً نه 😂",
    "قطعا!",
    "شاید...",
    "بهتره صبر کنی.",
    "جواب مثبت است 🔥",
    "ربات حس خوبی داره 😎",
    "نه داش 😂",
    "هنوز مشخص نیست.",
]


async def magic(update, context):
    await update.message.reply_text(
        "🎱 توپ جادویی میگه:\n\n"
        + random.choice(MAGIC)
    )


# =========================================================
# RANDOM
# =========================================================

async def random_fun(update, context):
    category = random.choice([
        "riddle",
        "joke",
        "story",
        "fact",
        "coin",
        "dice",
    ])

    if category == "riddle":
        question, answer = random.choice(RIDDLES)

        await update.message.reply_text(
            "🎲 شانسی انتخاب شد!\n\n"
            "چیستان:\n"
            + question
        )

        await asyncio.sleep(5)

        await update.message.reply_text(
            "😂 جوابش:\n"
            + answer
        )

    elif category == "joke":
        await update.message.reply_text(
            random.choice(JOKES)
        )

    elif category == "story":
        await update.message.reply_text(
            random.choice(STORIES)
        )

    elif category == "fact":
        await update.message.reply_text(
            "🧠 دانستنی:\n"
            + random.choice(FACTS)
        )

    elif category == "coin":
        await coin(update, context)

    else:
        await dice(update, context)


# =========================================================
# IRAN TIME
# =========================================================

async def iran_time(update, context):
    now = datetime.now(IRAN_TZ)

    await update.message.reply_text(
        "🇮🇷 ساعت ایران:\n\n"
        f"🕐 {now.strftime('%H:%M:%S')}\n"
        f"📅 {now.strftime('%Y-%m-%d')}"
    )


# =========================================================
# SCORE
# =========================================================

async def score(update, context):
    user_id = update.effective_user.id

    value = scores.get(user_id, 0)

    await update.message.reply_text(
        f"🏆 امتیاز تو: {value}"
    )


# =========================================================
# LEADERBOARD
# =========================================================

async def leaderboard(update, context):

    if not scores:
        await update.message.reply_text(
            "🏆 هنوز کسی امتیازی نگرفته!"
        )
        return

    top = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    lines = ["🏆 جدول برترین‌ها\n"]

    for index, (user_id, points) in enumerate(top, 1):
        lines.append(
            f"{index}. کاربر {user_id} — {points} امتیاز"
        )

    await update.message.reply_text(
        "\n".join(lines)
    )


# =========================================================
# GUESS NUMBER
# =========================================================

async def guess_start(update, context):

    user_id = update.effective_user.id

    number = random.randint(1, 20)

    games[user_id] = {
        "type": "guess",
        "number": number,
        "attempts": 0,
    }

    await update.message.reply_text(
        "🎯 حدس عدد شروع شد!\n\n"
        "من یک عدد بین ۱ تا ۲۰ انتخاب کردم.\n"
        "عددت رو بفرست."
    )


# =========================================================
# SAFE CALCULATOR
# =========================================================

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def calculate(node):

    if isinstance(node, ast.Expression):
        return calculate(node.body)

    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError

    if isinstance(node, ast.BinOp):

        if type(node.op) not in ALLOWED_OPERATORS:
            raise ValueError

        left = calculate(node.left)
        right = calculate(node.right)

        if abs(left) > 10**100 or abs(right) > 10**100:
            raise ValueError

        return ALLOWED_OPERATORS[type(node.op)](
            left,
            right
        )

    if isinstance(node, ast.UnaryOp):

        if type(node.op) not in ALLOWED_OPERATORS:
            raise ValueError

        return ALLOWED_OPERATORS[type(node.op)](
            calculate(node.operand)
        )

    raise ValueError


def safe_calculator(expression):

    expression = expression.replace(
        "×", "*"
    ).replace(
        "÷", "/"
    )

    tree = ast.parse(
        expression,
        mode="eval"
    )

    result = calculate(tree)

    if not math.isfinite(result):
        raise ValueError

    return result


# =========================================================
# CALCULATOR COMMAND
# =========================================================

async def calc(update, context):

    if not context.args:

        await update.message.reply_text(
            "🧮 ماشین حساب\n\n"
            "مثال:\n"
            "/calc 25+37\n"
            "/calc (20+5)*3\n"
            "/calc 144/12"
        )

        return

    expression = " ".join(context.args)

    try:

        result = safe_calculator(
            expression
        )

        await update.message.reply_text(
            f"🧮 نتیجه:\n\n{result}"
        )

    except Exception:

        await update.message.reply_text(
            "❌ عبارت ریاضی نامعتبره."
        )


# =========================================================
# HELP
# =========================================================

async def help_command(update, context):

    text = """
🤖 Spixle Entertainment Bot

🎮 بازی‌ها:
/guess
/coin
/dice
/rps
/magic

🧩 سرگرمی:
چیستان
داستان
شوخی
شانسی
دانستنی

🧮 ابزار:
/calc 25+37
/time

🏆 امتیاز:
/score
/top

ℹ️ راهنما:
/help
"""

    await update.message.reply_text(text)


# =========================================================
# START
# =========================================================

async def start(update, context):

    await update.message.reply_text(
        "🤖🔥 به Spixle خوش اومدی!\n\n"
        "اینجا کلی بازی و سرگرمی داری.\n\n"
        "چیستان، داستان، شوخی، شانسی، "
        "بازی، ماشین حساب و کلی چیز دیگه!\n\n"
        "برای دیدن همه قابلیت‌ها:\n"
        "/help"
    )


# =========================================================
# TEXT MESSAGE HANDLER
# =========================================================

async def text_handler(update, context):

    if not update.message:
        return

    text = update.message.text.strip().lower()
    user_id = update.effective_user.id

    # ---------------------------------------------
    # GUESS GAME
    # ---------------------------------------------

    if user_id in games:

        game = games[user_id]

        if game["type"] == "guess":

            try:
                number = int(text)
            except ValueError:
                number = None

            if number is not None:

                game["attempts"] += 1

                target = game["number"]

                if number == target:

                    add_score(user_id, 10)

                    del games[user_id]

                    await update.message.reply_text(
                        "🎯 درست گفتی! 🔥\n\n"
                        f"عدد {target} بود.\n"
                        "🏆 +10 امتیاز"
                    )

                    return

                if number < target:

                    await update.message.reply_text(
                        "📈 عدد بزرگ‌تره!"
                    )

                else:

                    await update.message.reply_text(
                        "📉 عدد کوچک‌تره!"
                    )

                return

    # ---------------------------------------------
    # RIDDLE
    # ---------------------------------------------

    if any(x in text for x in [
        "چیستان",
        "معما",
    ]):

        question, answer = random.choice(
            RIDDLES
        )

        await update.message.reply_text(
            "چیستان:\n\n"
            + question
        )

        async def reveal():

            await asyncio.sleep(5)

            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=(
                        "😂 خب داش، جوابو لو بدیم!\n\n"
                        "جواب: "
                        + answer
                    )
                )
            except Exception as error:
                print(
                    "RIDDLE ERROR:",
                    repr(error)
                )

        asyncio.create_task(reveal())

        return

    # ---------------------------------------------
    # STORY
    # ---------------------------------------------

    if any(x in text for x in [
        "داستان",
        "قصه",
    ]):

        await update.message.reply_text(
            random_unique(
                user_id,
                STORIES
            )
        )

        return

    # ---------------------------------------------
    # JOKE
    # ---------------------------------------------

    if any(x in text for x in [
        "شوخی",
        "جوک",
        "لطیفه",
    ]):

        await update.message.reply_text(
            random_unique(
                user_id,
                JOKES
            )
        )

        return

    # ---------------------------------------------
    # RANDOM
    # ---------------------------------------------

    if any(x in text for x in [
        "شانسی",
        "رندوم",
        "تصادفی",
    ]):

        await random_fun(
            update,
            context
        )

        return

    # ---------------------------------------------
    # FACT
    # ---------------------------------------------

    if any(x in text for x in [
        "دانستنی",
        "فکت",
        "اطلاعات",
    ]):

        await update.message.reply_text(
            "🧠 دانستنی:\n\n"
            + random_unique(
                user_id,
                FACTS
            )
        )

        return

    # ---------------------------------------------
    # HELLO
    # ---------------------------------------------

    if any(x in text for x in [
        "سلام",
        "درود",
        "سلاممم",
    ]):

        greetings = [
            "سلام داش 😎🤖",
            "به‌به سلام رفیق 😂",
            "سلاممم 🔥",
            "درود بر تو 😎",
            "سلام رفیق! 🤝",
        ]

        await update.message.reply_text(
            random.choice(greetings)
        )

        return

    # ---------------------------------------------
    # FUNNY DEFAULT
    # ---------------------------------------------

    await update.message.reply_text(
        random_unique(
            user_id,
            FUNNY
        )
    )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(update, context):

    print(
        "BOT ERROR:",
        repr(context.error)
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "======================================"
    )

    print(
        "Spixle Entertainment Bot"
    )

    print(
        "Status: STARTING"
    )

    print(
        "Persian: ENABLED"
    )

    print(
        "Games: ENABLED"
    )

    print(
        "Calculator: ENABLED"
    )

    print(
        "Iran Time: ENABLED"
    )

    print(
        "Riddles: ENABLED"
    )

    print(
        "Stories: ENABLED"
    )

    print(
        "Jokes: ENABLED"
    )

    print(
        "Random: ENABLED"
    )

    print(
        "======================================"
    )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # Commands
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    app.add_handler(
        CommandHandler(
            "coin",
            coin
        )
    )

    app.add_handler(
        CommandHandler(
            "dice",
            dice
        )
    )

    app.add_handler(
        CommandHandler(
            "rps",
            rps
        )
    )

    app.add_handler(
        CommandHandler(
            "magic",
            magic
        )
    )

    app.add_handler(
        CommandHandler(
            "guess",
            guess_start
        )
    )

    app.add_handler(
        CommandHandler(
            "calc",
            calc
        )
    )

    app.add_handler(
        CommandHandler(
            "time",
            iran_time
        )
    )

    app.add_handler(
        CommandHandler(
            "score",
            score
        )
    )

    app.add_handler(
        CommandHandler(
            "top",
            leaderboard
        )
    )

    # Normal text
    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            text_handler
        )
    )

    app.add_error_handler(
        error_handler
    )

    print(
        "Spixle is LIVE..."
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
