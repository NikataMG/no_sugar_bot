
import logging
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, JobQueue)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

START_DATE = datetime.datetime(2025, 4, 21)
END_DATE = datetime.datetime(2025, 6, 13)

MOTIVATIONAL_QUOTES = [
    "Ты молодец! Так держать!",
    "Каждый день — это победа!",
    "Твоя сила воли вдохновляет!",
    "Шоколадки подождут, а здоровье — нет!",
    "Ты становишься сильнее с каждым днём!",
    "Без сахара — больше энергии и радости!",
    "Ты герой своего здоровья!",
    "Твоя энергия — без сахара!",
    "Один день ближе к цели!",
    "Твоя сила больше, чем любое искушение!"
]

BADGES = {
    3: "\U0001F947 Маленький герой (3 дня без сахара)",
    7: "\U0001F948 Первая неделя — железная воля!",
    14: "\U0001F949 Две недели — как скала!",
    30: "\U0001F3C6 Легенда! 30 дней!",
    50: "\U0001F3C5 Нечеловеческая сила!",
}

checkins = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Сегодня без сахара!", callback_data='checkin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Я бот для отслеживания времени без сахара!\n\nКоманды:\n/time - сколько времени прошло без сахара\n/checkin - отметить день без сахара\n/progress - посмотреть прогресс всех участников",
        reply_markup=reply_markup
    )

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    delta = now - START_DATE
    remaining = END_DATE - now

    if remaining.total_seconds() <= 0:
        await update.message.reply_text("Поздравляю! Вы завершили челендж без сахара!")
    else:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        await update.message.reply_text(
            f"Вы держитесь без сахара уже {days} дней, {hours} часов и {minutes} минут!\n"
            f"До конца челенджа осталось {remaining.days} дней."
        )

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    today = datetime.datetime.now().date()

    if user_id not in checkins:
        checkins[user_id] = []

    if today in checkins[user_id]:
        await update.message.reply_text("Ты уже сегодня отмечался! Продолжай в том же духе!")
    else:
        checkins[user_id].append(today)
        streak = calculate_streak(checkins[user_id])
        phrase = random.choice(MOTIVATIONAL_QUOTES)

        badge_message = ""
        if streak in BADGES:
            badge_message = f"\n\nПоздравляем! Ты получил бейдж: {BADGES[streak]}"

        await update.message.reply_text(
            f"Отлично, {user_name}! Отмечено на сегодня!\n{phrase}\nТвой текущий стрик: {streak} дней подряд!{badge_message}"
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'checkin':
        update.effective_user = query.from_user
        await checkin(update, context)

async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    now = datetime.datetime.now()
    for chat_id in job.data:
        if now.date() == END_DATE.date():
            await context.bot.send_message(chat_id=chat_id, text="\U0001F389 Финал! Поздравляем! Вы победили сахар! Вы прошли весь путь до 13 июня! \U0001F389")
        else:
            phrase = random.choice(MOTIVATIONAL_QUOTES)
            keyboard = [[InlineKeyboardButton("Сегодня без сахара!", callback_data='checkin')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text=f"Доброе утро! Пора отметить день без сахара! {phrase}", reply_markup=reply_markup)

async def register_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if 'chats' not in context.bot_data:
        context.bot_data['chats'] = set()
    context.bot_data['chats'].add(chat_id)
    await update.message.reply_text("Этот чат зарегистрирован для ежедневных напоминаний!")

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not checkins:
        await update.message.reply_text("Пока никто не отмечался.")
        return

    text = "\U0001F4CA Прогресс участников:\n"
    for user_id, dates in checkins.items():
        streak = calculate_streak(dates)
        user_name = (await context.bot.get_chat(user_id)).first_name
        text += f"\n{user_name}: {streak} дней подряд"

    await update.message.reply_text(text)

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
    app.add_handler(CommandHandler('time', time))
    app.add_handler(CommandHandler('checkin', checkin))
    app.add_handler(CommandHandler('register', register_chat))
    app.add_handler(CommandHandler('progress', progress))
    app.add_handler(CallbackQueryHandler(button))

    job_queue = app.job_queue
    job_queue.run_daily(daily_reminder, time=datetime.time(hour=9, minute=0), data=lambda context: context.bot_data.get('chats', set()))

    print("Бот запущен...")
    app.run_polling()
