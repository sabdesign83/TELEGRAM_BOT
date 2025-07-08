import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import asyncio # Импортируем asyncio для асинхронной работы

# --- Настройка логирования ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.WARNING)

# --- Получаем токены из переменных окружения ---
# !!! ВАЖНО: НЕ ВСТАВЛЯЙТЕ СЮДА ВАШИ КЛЮЧИ НАПРЯМУЮ !!!
# Они будут установлены как переменные окружения на Railway.

# Ваш токен Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 

# Ваш API-ключ Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# Проверка наличия токенов
if not TELEGRAM_BOT_TOKEN:
    logging.error("Ошибка: Переменная окружения TELEGRAM_BOT_TOKEN не установлена!")
    exit(1) 
if not GEMINI_API_KEY:
    logging.error("Ошибка: Переменная окружения GEMINI_API_KEY не установлена!")
    exit(1) 

# --- Инициализация Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- Функции для команд бота ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start. Приветствует пользователя."""
    await update.message.reply_text(
        'Привет! Я бот, работающий на основе Gemini. Просто напиши мне что-нибудь, и я попробую ответить.'
    )
    logging.info(f"Получена команда /start от {update.effective_user.username}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /help. Дает краткую справку."""
    await update.message.reply_text(
        'Я могу отвечать на твои вопросы, генерировать тексты и многое другое. Просто задай мне вопрос!'
    )
    logging.info(f"Получена команда /help от {update.effective_user.username}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает все текстовые сообщения от пользователя, отправляя их в Gemini
    и возвращая ответ обратно в Telegram.
    """
    user_message = update.message.text
    user_username = update.effective_user.username or update.effective_user.first_name
    logging.info(f"Получено сообщение от {user_username}: '{user_message}'")

    if not user_message: 
        return

    # Отправляем сообщение "Печатаю..."
    await update.message.chat.send_action("typing")

    try:
        # Отправляем сообщение пользователя в Gemini
        response = await model.generate_content_async(user_message)
        gemini_response_text = response.text
        logging.info(f"Ответ от Gemini: '{gemini_response_text}'")

        # Отправляем ответ от Gemini обратно пользователю
        await update.message.reply_text(gemini_response_text)

    except Exception as e:
        logging.error(f"Ошибка при работе с Gemini для пользователя {user_username}: {e}", exc_info=True)
        await update.message.reply_text(
            "Извините, произошла ошибка при обработке вашего запроса. Возможно, вы задали слишком сложный вопрос или что-то пошло не так на моей стороне. Пожалуйста, попробуйте еще раз."
        )

# --- Основная функция запуска бота ---

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен. Ожидание сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
