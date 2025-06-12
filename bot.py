from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from professions import city_areas

TOKEN = "7549868964:AAHN6SkbcGhwpQGisdYgwFu8WmUaS5fMH9w"
# Сначала определяем start
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("▶️ Начать", callback_data="start_button")]]
    await update.message.reply_text("👋 Привет! Добро пожаловать!", reply_markup=InlineKeyboardMarkup(keyboard))

    with open("images/welcome.jpg", "rb") as photo:
        await update.message.reply_photo(photo)


async def start_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(area["name"], callback_data=key)]
        for key, area in city_areas.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        "Выбери район для изучения профессий:",
        reply_markup=reply_markup
        )

# Потом вызываем start  в другой функции
async def start_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# Обработка выбора района — показать профессии + кнопку "Назад"
async def handle_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    area_key = query.data
    area = city_areas[area_key]

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"prof|{area_key}|{name}")]
        for name in area["professions"]
    ]
    # Кнопка назад к районам
    keyboard.append([InlineKeyboardButton("⬅️ Назад к районам", callback_data="back_to_areas")])

    await query.edit_message_text(
        f"📍 Ты в районе {area['name']}\nВыбери профессию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка выбора профессии — показать описание
async def handle_profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, area_key, prof_name = query.data.split("|")

    prof_data = city_areas[area_key]["professions"][prof_name]
    description = prof_data["description"]
    image_path = f"images/{prof_name}.jpg"

    # Отправка фото и краткого описания
    try:
        with open(image_path, "rb") as img:
            await query.message.reply_photo(img, caption=description)
    except FileNotFoundError:
        await query.message.reply_text(description)

    # Форматированная карточка профессии
    card_text = (
        f"📌 *Чем занимается:\n* {prof_data.get('what_makes', '—')}\n\n"
        f"🚀 *Перспективы:\n* {prof_data.get('perspectives', '—')}\n\n"
        f"🧠 *Что нужно уметь:\n* {prof_data.get('skills', '—')}\n\n"
        f"🏢 *Где можно учиться:\n* {prof_data.get('where_study', '—')}"
    )

    # Кнопки навигации после показа профессии
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад к профессиям", callback_data=area_key)],
        [InlineKeyboardButton("⬅️ Назад к районам", callback_data="back_to_areas")],
        [InlineKeyboardButton("🎤📷 Интервью с профессионалом",
                              callback_data=f"interview|{area_key}|{prof_name}")]
    ]

    await query.message.reply_text(
        card_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
#показ интревью
async def handle_interview_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, area_key, prof_name = query.data.split("|")

    prof_data = city_areas[area_key]["professions"][prof_name]
    video_url = prof_data.get("video")

    if video_url:
        text = f"🎬 Интервью с профессионалом: [смотреть видео]({video_url})"
    else:
        text = "❗ Видео пока недоступно."

    await query.message.reply_text(text, parse_mode="Markdown")

    # Повторить клавиатуру выбора профессии
    area = city_areas[area_key]
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"prof|{area_key}|{name}")]
        for name in area["professions"]
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Назад к районам", callback_data="back_to_areas")])

    await query.message.reply_text(
        f"📍 Ты в районе {area['name']}\nВыбери следующую профессию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка кнопки "Назад к районам" — показать список районовz
async def handle_back_to_areas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(area["name"], callback_data=key)]
        for key, area in city_areas.items()
    ]

    await query.edit_message_text(
        "👋 Привет! Добро пожаловать в Город профессий АПК.\nВыбери район, чтобы исследовать профессии:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", greet))
    app.add_handler(CallbackQueryHandler(start_from_button, pattern="^start_button$"))
    app.add_handler(CallbackQueryHandler(handle_area, pattern="^(fields|lab|vet|tech)$"))
    app.add_handler(CallbackQueryHandler(handle_profession, pattern=r"^prof\|"))
    app.add_handler(CallbackQueryHandler(handle_back_to_areas, pattern="^back_to_areas$"))
    app.add_handler(CallbackQueryHandler(handle_interview_prompt, pattern=r"^interview\|"))
    app.run_polling()

if __name__ == '__main__':
    main()
