
import logging
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

START_DATE = datetime.datetime(2025, 4, 21)
END_DATE = datetime.datetime(2025, 6, 13)

MOTIVATIONAL_QUOTES = [
    "Ты монстр силы! 🚀",
    "Твоя энергия растет! 🔥",
    "Продолжаем побеждать! 🌟",
    "Шаг за шагом к победе! 🏆",
    "Сила внутри тебя! 💪",
    "Ты вдохновение для других! ✨"
]

BONUS_MESSAGES = {
    3: "Маленький герой! 🥉 3 дня без сахара!",
    7: "Первая неделя — железная воля! 🥈",
    14: "Две недели — как скала! 🥇",
    21: "Три недели! Ты герой! 🏅",
    30: "Месяц без сахара! Легенда! 🏆"
}

checkins = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Сегодня без сахара", callback_data='checkin')],
        [InlineKeyboardButton("Посмотреть прогресс", callback_data='progress')],
        [InlineKeyboardButton("Сколько держусь", callback_data='time')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Начинаем день без сахара! Выбирай кнопку:",
        reply_markup=reply_markup
    )

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    delta = now - START_DATE
    remaining = END_DATE - now

    if remaining.total_seconds() <= 0:
        await update.message.reply_text("Поздравляю! Вы завершили челендж без сахара! 🎉")
    else:
        days = delta.days
        await update.message.reply_text(
            f"Вы держитесь без сахара уже {days} дней! 🔥\n"
            f"До конца челенджа осталось {remaining.days} дней."
        )

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    today = datetime.datetime.now().date()

    if user_id not in checkins:
        checkins[user_id] = []

    if today in checkins[user_id]:
        await update.message.reply_text("Ты уже сегодня отмечался! Продолжай в том же духе! 🌟")
    else:
        checkins[user_id].append(today)
        streak = calculate_streak(checkins[user_id])
        phrase = random.choice(MOTIVATIONAL_QUOTES)

        bonus_message = ""
        if streak in BONUS_MESSAGES:
            bonus_message = f"\n\n{BONUS_MESSAGES[streak]}"

        await update.message.reply_text(
            f"Отлично, {user_name}! {phrase}\nТвой текущий стрик: {streak} дней подряд!{bonus_message}"
        )

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not checkins:
        await update.message.reply_text("Пока никто не отмечался.")
        return

    text = "📈 Прогресс участников:\n"
    for user_id, dates in checkins.items():
        streak = calculate_streak(dates)
        user_name = (await context.bot.get_chat(user_id)).first_name
        text += f"\n{user_name}: {streak} дней подряд"

    text += f"\n\nВсего участников: {len(checkins)}"
    await update.message.reply_text(text)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # перенаправляем по действиям
    if data == 'checkin':
        update.effective_user = query.from_user
        await checkin(update, context)
    elif data == 'progress':
        update.effective_user = query.from_user
        await progress(update, context)
    elif data == 'time':
        update.effective_user = query.from_user
        await time(update, context)

def calculate_streak(dates):
    if not dates:
        return 0
    dates = sorted(dates)
    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
        else:
            break
    return streak

if __name__ == '__main__':
    app = ApplicationBuilder().token('7410992932:AAFqZR1QNUHBYzdQi5fSXghIDfem-6JRuSw').build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button))

    print("Бот запущен...")
    app.run_polling()
