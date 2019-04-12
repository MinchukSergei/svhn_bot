import logging
import os
from pathlib import Path
import threading
from queue import Queue

from lab4.util import Util
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = os.environ['BOT_TOKEN']
TEST_IMAGE_PATH = Path('../data/topredict.jpg')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

images_to_recognize = Queue()
recognized_images = Queue()


def predict():
    util = Util()
    util.build_model()

    while True:
        path = images_to_recognize.get()
        recognized_images.put(util.predict(path))


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Help!')


def text_handler(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Please, send photo with house number.')


def photo_handler(bot, update):
    file = bot.getFile(update.message.photo[-1].file_id)

    file_path = str(TEST_IMAGE_PATH.absolute())
    file.download(file_path)
    images_to_recognize.put(file_path)
    predicted = recognized_images.get()

    bot.send_message(chat_id=update.message.chat_id, text=''.join(map(str, predicted)))


def error(bot, update):
    logger.warning('Update "%s" caused error "%s"', bot, update.error)


def main():
    image_recognize_thread = threading.Thread(target=predict)
    image_recognize_thread.start()

    updater = Updater(BOT_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, text_handler))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
