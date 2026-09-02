import os
import random
import ast
import operator as op
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
TOKEN = os.getenv("BOT_TOKEN")
# =========================================================
# 🎭 CONTENT
# =========================================================
JOKES = [
    "معلم گفت چرا مشقتو با مداد نوشتی؟ گفت چون با خودکار پاک نمی‌شه 😂",
    "رفیقم گفت من خیلی باهوشم؛ گفتم پس چرا وای‌فای رو خاموش کردی؟ گفت صرفه‌جویی در اینترنت! 😂",
    "به کامپیوتر گفتم چرا هنگ کردی؟ گفت منم مثل تو نیاز به استراحت دارم 🤣",
    "گفتم امروز رژیم دارم؛ یخچال گفت باشه، ولی من موافق نیستم 😂",
    "یکی رفت دکتر گفت حافظه‌ام ضعیف شده؛ دکتر گفت از کی؟ گفت چی؟ 😂",
    "گوشی‌ام گفت حافظه پر است؛ گفتم داداش منم همین مشکلو دارم 😭😂",
    "به ساعت گفتم چرا همیشه عجله داری؟ گفت چون وقت ندارم! 😂",
    "کامپیوترم خیلی مودبه؛ هر بار خاموشش می‌کنم می‌گه Goodbye 😎",
    "گفتم اینترنت چرا کندی؟ گفت چون دارم فکر می‌کنم 😂",
    "رفیقم گفت من هیچ‌وقت اشتباه نمی‌کنم؛ گفتم همین حرفت اشتباهه 🤣",
]
STORIES = [
    "یک شب Spixle تصمیم گرفت از اتاقش بیرون بره... ولی اینترنت قطع شد و دوباره برگشت 😂",
    "روزی یک ربات تصمیم گرفت قهرمان شود. اولین مأموریتش پیدا کردن شارژر بود 🔋😂",
    "یک گیمر گفت فقط پنج دقیقه بازی می‌کنم... سه ساعت بعد هنوز در مرحله اول بود 🎮🤣",
    "یک روز ماه به زمین گفت چرا همه به تو نگاه می‌کنند؟ زمین گفت چون اینترنت دارم 🌍😂",
    "یک ربات وارد کتابخانه شد و گفت: کتابی درباره هوش مصنوعی دارید؟ کتابدار گفت: خودت بخون! 🤖",
    "Spixle یک در مخفی پیدا کرد. در را باز کرد و پشت آن... یک یخچال بود. مأموریت شکست خورد 😂",
    "یک قهرمان بزرگ وارد جنگل شد؛ اولین چیزی که پیدا کرد یک پشه بود و فرار کرد 🦟🤣",
    "در آینده همه ماشین‌ها پرواز می‌کنند؛ به‌جز ماشین من که هنوز بنزین می‌خواهد 😂",
    "یک جادوگر گفت من همه‌چیز را می‌توانم جادو کنم؛ بعد رمز وای‌فای را فراموش کرد 🧙‍♂️",
    "روزی یک نفر گفت من شانس ندارم؛ همان لحظه برنده قرعه‌کشی شد... ولی بلیت مال دوستش بود 😂",
]
RIDDLES = [
    ("آن چیست که هرچه بیشتر از آن برداری، بزرگ‌تر می‌شود؟", "چاله"),
    ("چه چیزی پا دارد ولی راه نمی‌رود؟", "میز"),
    ("چه چیزی زبان دارد ولی حرف نمی‌زند؟", "کفش"),
    ("چه چیزی همیشه جلوی توست ولی نمی‌توانی ببینیش؟", "آینده"),
    ("چه چیزی وقتی خیس می‌شود، بیشتر خشک می‌کند؟", "حوله"),
    ("چه چیزی کلید دارد ولی قفل ندارد؟", "پیانو"),
    ("چه چیزی پر دارد ولی پرواز نمی‌کند؟", "بالش"),
    ("چه چیزی سر دارد ولی بدن ندارد؟", "سکه"),
    ("چه چیزی بالا می‌رود ولی پایین نمی‌آید؟", "سن"),
    ("چه چیزی بدون پا سفر می‌کند؟", "صدا"),
]
# =========================================================
# 🧮 SAFE CALCULATOR
# =========================================================
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}
def safe_calculate(expression):
    if len(expression) > 100:
        raise ValueError("عبارت خیلی طولانی است.")
    tree = ast.parse(expression, mode="eval")
    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError()
        if isinstance(node, ast.BinOp):
            if type(node.op) not in ALLOWED_OPERATORS:
                raise ValueError()
            return ALLOWED_OPERATORS[type(node.op)](
                evaluate(node.left),
                evaluate(node.right),
            )
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in ALLOWED_OPERATORS:
                raise ValueError()
            return ALLOWED_OPERATORS[type(node.op)](
                evaluate(node.operand)
            )
        raise ValueError()
    result = evaluate(tree)
    if abs(result) > 10**100:
        raise ValueError()
    return result
# =========================================================
# 🏠 MAIN MENU
# =========================================================
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎮 بازی‌ها", callback_data="games"),
            InlineKeyboardButton("😂 سرگرمی", callback_data="fun"),
        ],
        [
            InlineKeyboardButton("🧠 چیستان", callback_data="riddle"),
            InlineKeyboardButton("🎲 شانسی", callback_data="random_menu"),
        ],
        [
            InlineKeyboardButton("🧮 ماشین حساب", callback_data="calc_menu"),
            InlineKeyboardButton("🕐 ساعت ایران", callback_data="time"),
        ],
        [
            InlineKeyboardButton("ℹ️ راهنما", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
# =========================================================
# 🚀 COMMANDS
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔥 به **Spixle** خوش اومدی!\n\n"
        "🤖 من یه ربات سرگرمی‌ام و کلی چیز برای ور رفتن دارم.\n\n"
        "🎮 بازی\n"
        "😂 شوخی\n"
        "📖 داستان\n"
        "🧠 چیستان\n"
        "🎲 شانس\n"
        "🧮 ماشین حساب\n"
        "🕐 ساعت ایران\n\n"
        "👇 از منو انتخاب کن!"
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **راهنمای Spixle**\n\n"
        "/start — شروع ربات\n"
        "/help — راهنما\n"
        "/joke — شوخی\n"
        "/story — داستان\n"
        "/riddle — چیستان\n"
        "/coin — شیر یا خط\n"
        "/dice — تاس\n"
        "/random — عدد شانسی\n"
        "/time — ساعت ایران\n"
        "/guess — حدس عدد\n"
        "/calc 25*4 — ماشین حساب\n"
        "/games — بازی‌ها",
        parse_mode="Markdown",
    )
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "😂 " + random.choice(JOKES)
    )
async def story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 " + random.choice(STORIES)
    )
async def riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question, answer = random.choice(RIDDLES)
    context.user_data["riddle_answer"] = answer
    await update.message.reply_text(
        f"🧠 **چیستان**\n\n{question}\n\n"
        "جوابت رو بفرست 😈",
        parse_mode="Markdown",
    )
async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["🦁 شیر", "🪙 خط"])
    await update.message.reply_text(
        f"🪙 **نتیجه:**\n\n{result}",
        parse_mode="Markdown",
    )
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 6)
    await update.message.reply_text(
        f"🎲 **تاس انداختم...**\n\n"
        f"عدد: **{number}**",
        parse_mode="Markdown",
    )
async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    await update.message.reply_text(
        f"🎰 **عدد شانسی تو:**\n\n"
        f"**{number}**",
        parse_mode="Markdown",
    )
async def iran_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(ZoneInfo("Asia/Tehran"))
    await update.message.reply_text(
        "🇮🇷 **ساعت ایران**\n\n"
        f"🕐 {now.strftime('%H:%M:%S')}\n"
        f"📅 {now.strftime('%Y/%m/%d')}",
        parse_mode="Markdown",
    )
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🧮 **ماشین حساب**\n\n"
            "مثال:\n"
            "`/calc 25*4`\n"
            "`/calc 100/5+7`\n"
            "`/calc 2**8`",
            parse_mode="Markdown",
        )
        return
    expression = " ".join(context.args)
    try:
        result = safe_calculate(expression)
        await update.message.reply_text(
            f"🧮 `{expression}`\n\n"
            f"= **{result}**",
            parse_mode="Markdown",
        )
    except Exception:
        await update.message.reply_text(
            "❌ عبارت ریاضی نامعتبره."
        )
async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    context.user_data["guess_number"] = number
    context.user_data["guess_attempts"] = 0
    await update.message.reply_text(
        "🎯 **بازی حدس عدد**\n\n"
        "من یک عدد بین **1 تا 100** انتخاب کردم.\n"
        "حدس بزن 😈",
        parse_mode="Markdown",
    )
async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 **بازی‌های Spixle**",
        parse_mode="Markdown",
        reply_markup=games_menu(),
    )
# =========================================================
# 🎮 MENUS
# =========================================================
def games_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎯 حدس عدد", callback_data="guess"),
        ],
        [
            InlineKeyboardButton("🪙 شیر یا خط", callback_data="coin"),
            InlineKeyboardButton("🎲 تاس", callback_data="dice"),
        ],
        [
            InlineKeyboardButton("🎰 عدد شانسی", callback_data="random"),
        ],
        [
            InlineKeyboardButton("🔙 منوی اصلی", callback_data="home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
def fun_menu():
    keyboard = [
        [
            InlineKeyboardButton("😂 شوخی", callback_data="joke"),
        ],
        [
            InlineKeyboardButton("📖 داستان", callback_data="story"),
        ],
        [
            InlineKeyboardButton("🧠 چیستان", callback_data="riddle"),
        ],
        [
            InlineKeyboardButton("🔙 برگشت", callback_data="home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
def random_menu():
    keyboard = [
        [
            InlineKeyboardButton("🪙 شیر یا خط", callback_data="coin"),
            InlineKeyboardButton("🎲 تاس", callback_data="dice"),
        ],
        [
            InlineKeyboardButton("🎰 عدد شانسی", callback_data="random"),
        ],
        [
            InlineKeyboardButton("🔙 برگشت", callback_data="home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
def calc_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "🧮 راهنما",
                callback_data="calc_help",
            )
        ],
        [
            InlineKeyboardButton("🔙 برگشت", callback_data="home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
# =========================================================
# 🔘 BUTTON HANDLER
# =========================================================
async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "home":
        await query.edit_message_text(
            "🔥 **منوی اصلی Spixle**",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
    elif data == "games":
        await query.edit_message_text(
            "🎮 **بازی‌های Spixle**",
            parse_mode="Markdown",
            reply_markup=games_menu(),
        )
    elif data == "fun":
        await query.edit_message_text(
            "😂 **بخش سرگرمی**",
            parse_mode="Markdown",
            reply_markup=fun_menu(),
        )
    elif data == "random_menu":
        await query.edit_message_text(
            "🎲 **بخش شانس**",
            parse_mode="Markdown",
            reply_markup=random_menu(),
        )
    elif data == "calc_menu":
        await query.edit_message_text(
            "🧮 **ماشین حساب**\n\n"
            "برای محاسبه در چت بنویس:\n"
            "`/calc 25*4`",
            parse_mode="Markdown",
            reply_markup=calc_menu(),
        )
    elif data == "calc_help":
        await query.edit_message_text(
            "🧮 **ماشین حساب امن**\n\n"
            "مثال:\n"
            "`/calc 25*4`\n"
            "`/calc 100/5+7`\n"
            "`/calc 2**8`",
            parse_mode="Markdown",
            reply_markup=calc_menu(),
        )
    elif data == "help":
        await query.edit_message_text(
            "🤖 **راهنمای Spixle**\n\n"
            "/start\n"
            "/help\n"
            "/joke\n"
            "/story\n"
            "/riddle\n"
            "/coin\n"
            "/dice\n"
            "/random\n"
            "/time\n"
            "/guess\n"
            "/calc",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
    elif data == "joke":
        await query.edit_message_text(
            "😂 " + random.choice(JOKES),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "😂 یکی دیگه",
                        callback_data="joke",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 برگشت",
                        callback_data="fun",
                    )
                ],
            ]),
        )
    elif data == "story":
        await query.edit_message_text(
            "📖 " + random.choice(STORIES),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📖 یکی دیگه",
                        callback_data="story",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 برگشت",
                        callback_data="fun",
                    )
                ],
            ]),
        )
    elif data == "riddle":
        question, answer = random.choice(RIDDLES)
        context.user_data["riddle_answer"] = answer
        await query.edit_message_text(
            f"🧠 **چیستان**\n\n"
            f"{question}\n\n"
            "جوابت رو همینجا بفرست 😈",
            parse_mode="Markdown",
        )
    elif data == "coin":
        result = random.choice(["🦁 شیر", "🪙 خط"])
        await query.edit_message_text(
            f"🪙 **نتیجه:**\n\n{result}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔄 دوباره",
                        callback_data="coin",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 برگشت",
                        callback_data="random_menu",
                    )
                ],
            ]),
        )
    elif data == "dice":
        number = random.randint(1, 6)
        await query.edit_message_text(
            f"🎲 **نتیجه تاس:**\n\n**{number}**",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎲 دوباره",
                        callback_data="dice",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 برگشت",
                        callback_data="random_menu",
                    )
                ],
            ]),
        )
    elif data == "random":
        number = random.randint(1, 100)
        await query.edit_message_text(
            f"🎰 **عدد شانسی:**\n\n**{number}**",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎰 دوباره",
                        callback_data="random",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 برگشت",
                        callback_data="random_menu",
                    )
                ],
            ]),
        )
    elif data == "time":
        now = datetime.now(ZoneInfo("Asia/Tehran"))
        await query.edit_message_text(
            "🇮🇷 **ساعت ایران**\n\n"
            f"🕐 {now.strftime('%H:%M:%S')}\n"
            f"📅 {now.strftime('%Y/%m/%d')}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔄 بروزرسانی",
                        callback_data="time",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 برگشت",
                        callback_data="home",
                    )
                ],
            ]),
        )
    elif data == "guess":
        number = random.randint(1, 100)
        context.user_data["guess_number"] = number
        context.user_data["guess_attempts"] = 0
        await query.edit_message_text(
            "🎯 **بازی حدس عدد**\n\n"
            "یک عدد بین **1 تا 100** انتخاب کردم.\n\n"
            "حدست رو بفرست 😈",
            parse_mode="Markdown",
        )
# =========================================================
# 💬 TEXT HANDLER
# =========================================================
async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    # 🧠 RIDDLE
    if "riddle_answer" in context.user_data:
        answer = context.user_data["riddle_answer"]
        if text.casefold() == answer.casefold():
            del context.user_data["riddle_answer"]
            await update.message.reply_text(
                "🎉 درست گفتی!\n"
                "🔥 مغزت امروز روشنه!"
            )
        else:
            await update.message.reply_text(
                "❌ نه داش 😈\n"
                "دوباره تلاش کن!"
            )
        return
    # 🎯 GUESS GAME
    if "guess_number" in context.user_data:
        try:
            guess_value = int(text)
        except ValueError:
            await update.message.reply_text(
                "🎯 فقط یک عدد بین 1 تا 100 بفرست."
            )
            return
        if not 1 <= guess_value <= 100:
            await update.message.reply_text(
                "⚠️ عدد باید بین 1 تا 100 باشه."
            )
            return
        number = context.user_data["guess_number"]
        context.user_data["guess_attempts"] += 1
        if guess_value < number:
            await update.message.reply_text(
                "⬆️ بیشتره! 😈"
            )
        elif guess_value > number:
            await update.message.reply_text(
                "⬇️ کمتره! 😈"
            )
        else:
            attempts = context.user_data["guess_attempts"]
            del context.user_data["guess_number"]
            del context.user_data["guess_attempts"]
            await update.message.reply_text(
                f"🎉 **بردی!** 🔥\n\n"
                f"عدد **{number}** بود.\n"
                f"تعداد تلاش: **{attempts}**",
                parse_mode="Markdown",
            )
        return
    # 💬 NORMAL CHAT
    lower = text.casefold()
    if lower in ["سلام", "hello", "hi", "salam"]:
        await update.message.reply_text(
            random.choice([
                "سلام داش 😎🔥",
                "سلام! Spixle آماده‌ست 🤖",
                "عه سلام! بالاخره اومدی 😂",
                "سلام رفیق! 👋😎",
            ])
        )
    elif "خوبی" in lower or "how are you" in lower:
        await update.message.reply_text(
            random.choice([
                "من که همیشه آماده‌ام 😎🤖",
                "عالی‌ام! 🔥",
                "تا وقتی اینترنت باشه، من خوبم 😂",
            ])
        )
    elif "مرسی" in lower or "ممنون" in lower or "thanks" in lower:
        await update.message.reply_text(
            random.choice([
                "قربانت داش ❤️🔥",
                "خواهش می‌کنم 😎",
                "دمت گرم! 🤖🔥",
            ])
        )
    elif "جوک" in lower or "joke" in lower:
        await joke(update, context)
    elif "داستان" in lower or "story" in lower:
        await story(update, context)
    elif "چیستان" in lower or "riddle" in lower:
        await riddle(update, context)
    else:
        await update.message.reply_text(
            "🤖 هنوز اینو بلد نیستم 😅\n\n"
            "برای دیدن قابلیت‌های من `/help` رو بزن.",
            parse_mode="Markdown",
        )
# =========================================================
# ❌ ERROR HANDLER
# =========================================================
async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    print(
        "⚠️ Bot error:",
        context.error,
    )
# =========================================================
# 🚀 START BOT
# =========================================================
def main():
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )
    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("story", story))
    app.add_handler(CommandHandler("riddle", riddle))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("random", random_number))
    app.add_handler(CommandHandler("time", iran_time))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(CommandHandler("games", games))
    # Buttons
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )
    # Text
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler,
        )
    )
    app.add_error_handler(error_handler)
    print("================================")
    print("🔥 Spixle is starting...")
    print("🤖 Telegram entertainment bot")
    print("🎮 Games | 😂 Fun | 🧠 Riddles")
    print("🧮 Calculator | 🕐 Iran Time")
    print("================================")
    # Polling
    app.run_polling(
        drop_pending_updates=False,
        allowed_updates=Update.ALL_TYPES,
    )
if __name__ == "__main__":
    main()
