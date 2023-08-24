import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence, ConversationHandler
from langdetect import detect
import requests

# Ваши реальные токены
BOT_TOKEN = "6618031334:AAFjvTB7bBP9cglEAafoxG3r5UnbYPECZMg"
PIXABAY_KEY = "38992252-ad12100b7de3501e393b45a6e"

START, CHOOSING = range(2)

def start(update, context):
    update.message.reply_text("Здравствуйте! Я бот, готовый помочь вам найти красивые фотографии на разные темы. Введите запрос для поиска фотографий:")
    return CHOOSING

def send_content(update, context):
    query = update.message.text.strip()
    if not query:
        update.message.reply_text("Извините, но для того чтобы найти фотографии, вам нужно указать, по какой теме.")
        return

    user_data = context.user_data
    user_data['query'] = query

    lang = detect(query)

    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={query}&per_page=5&lang={lang}&image_type=photo&orientation=horizontal&min_width=1920&min_height=1080"

    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            if "hits" in data:
                hits = data["hits"]
                if hits:
                    for item in hits:
                        media_url = item["fullHDURL"] if "fullHDURL" in item else item["webformatURL"]
                        context.bot.send_photo(chat_id=update.message.chat_id, photo=media_url)
                    user_data['page'] = 2
                    
                    keyboard = [
                        ["/more"]
                    ]
                    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                    update.message.reply_text("Хотите найти больше фотографий? Нажмите /more", reply_markup=reply_markup)
                else:
                    update.message.reply_text("Извините, но я не смог найти фотографии по вашему запросу.")
            else:
                update.message.reply_text("Извините, но я не смог найти фотографии по вашему запросу.")
        except requests.exceptions.JSONDecodeError:
            update.message.reply_text("Произошла ошибка при обработке данных от сервера.")
    else:
        update.message.reply_text("Извините, произошла ошибка при обращении к серверу.")

def more(update, context):
    user_data = context.user_data
    query = user_data.get('query')

    if not query:
        update.message.reply_text("Произошла ошибка. Пожалуйста, повторите запрос.")
        return ConversationHandler.END

    lang = detect(query)

    page = user_data.get('page', 2)
    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={query}&page={page}&per_page=5&lang={lang}&image_type=photo&orientation=horizontal&min_width=1920&min_height=1080"

    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            if "hits" in data:
                hits = data["hits"]
                if hits:
                    for item in hits:
                        media_url = item["fullHDURL"] if "fullHDURL" in item else item["webformatURL"]
                        context.bot.send_photo(chat_id=update.message.chat_id, photo=media_url)
                    user_data['page'] = page + 1
                    
                    keyboard = [
                        ["/more"]
                    ]
                    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                    update.message.reply_text("Хотите найти больше фотографий? Нажмите /more", reply_markup=reply_markup)
                else:
                    update.message.reply_text("Извините, но я не смог найти дополнительные фотографии по вашему запросу.")
            else:
                update.message.reply_text("Извините, но я не смог найти дополнительные фотографии по вашему запросу.")
        except requests.exceptions.JSONDecodeError:
            update.message.reply_text("Произошла ошибка при обработке данных от сервера.")
    else:
        update.message.reply_text("Извините, произошла ошибка при обращении к серверу.")

def help(update, context):
    update.message.reply_text("Этот бот поможет вам найти красивые фотографии. Просто введите запрос для поиска.")

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    persistence = PicklePersistence(filename='bot_data.pkl')
    updater = Updater(BOT_TOKEN, persistence=persistence, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.text & ~Filters.command, send_content),
                CommandHandler('more', more),
                CommandHandler('help', help)
            ]
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()









