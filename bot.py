#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Simple Bot to retrieve FHICT Canvas announcements.
# This program is dedicated to the public domain under the CC0 license.
Run `python bot.py` to run the bot.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

"""

from telegram.ext import Updater, CommandHandler
import logging
import requests
import json
from pprint import pprint
from operator import itemgetter
import datetime
from dateutil import parser
import sys
import canvas
from html.parser import HTMLParser


fhict_canvas_url = "https://fhict.instructure.com"


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def read_canvas_api_key():
    with open("canvas-api-key.txt", "r") as api_key_file:
        api_key = api_key_file.readline().strip()
        return api_key


def read_telegram_api_key():
    with open("telegram-api-key.txt", "r") as api_key_file:
        api_key = api_key_file.readline().strip()
        return api_key

announcement_reader = canvas.Canvas(fhict_canvas_url, read_canvas_api_key())

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def start(bot, update):
    update.message.reply_text("Hi, I\'m a Canvas announcement bot!")


def retrieve_announcements_after_yesterday():
    previous_day = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    ok, announcements_or_error = announcement_reader.get_announcements_after(previous_day)
    return ok, announcements_or_error


def get(bot, update):
    logger.info("Received request for data")
    ok, announcements_or_error = retrieve_announcements_after_yesterday()
    if not ok:
        update.message.reply_text("error: {}".format(announcements_or_error))
        return
    announcements = announcements_or_error
    announcement_texts = []
    announcement_texts.append("Recent announcements\n")
    for announcement in announcements:
        title = announcement["title"]
        author = announcement["author"]["display_name"]
        post_time = announcement["posted_at"]
        message = strip_tags(announcement["message"])
        announcement_texts.append("Title: {}\n\tAuthor: {}\n\tTime: {}\n\tMessage: {}\n".format(title, author, post_time, message))
    text_to_send = '\n'.join(announcement_texts)
    update.message.reply_text(text_to_send)


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
    dp.add_handler(CommandHandler("get", get))

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
