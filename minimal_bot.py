#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
import logging
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def read_telegram_api_key():
    with open("telegram-api-key.txt", "r") as api_key_file:
        api_key = api_key_file.readline().strip()
        return api_key

def start(bot, update):
    update.message.reply_text("Hi")


def publish(bot, job):
    bot.send_message(chat_id=job.context, text="hello")


def subscribe(bot, update, job_queue, chat_data):
    chat_id = update.message.chat_id
    time = 1
    job = job_queue.run_once(publish, time, context=chat_id)
    chat_data["job"] = job
    update.message.reply_text("Subscribed!") 


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Run bot."""
    telegram_api_key = read_telegram_api_key()
    # logger.info("API key:%s" % (api_key))

    updater = Updater(telegram_api_key)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("subscribe", subscribe,
                                  pass_job_queue=True,
                                  pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    logger.info("Bot started")

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
