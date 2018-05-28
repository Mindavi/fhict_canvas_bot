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
import datetime
from dateutil import parser
import canvas
from html.parser import HTMLParser
import subscribermanager

fhict_canvas_url = 'https://fhict.instructure.com'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log',
                    filemode='a')

logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())

def read_canvas_api_key():
    with open('canvas-api-key.txt', 'r') as api_key_file:
        api_key = api_key_file.readline().strip()
        return api_key


def read_telegram_api_key():
    with open('telegram-api-key.txt', 'r') as api_key_file:
        api_key = api_key_file.readline().strip()
        return api_key

sub_manager = subscribermanager.SubscriberManager('subscribers.txt')
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
    update.message.reply_text('Hi, I\'m a Canvas announcement bot!\n\
            use /subscribe to subscribe to new announcements')


def retrieve_announcements_after_yesterday():
    previous_day = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    ok, announcements_or_error = announcement_reader.get_announcements_after(previous_day)
    return ok, announcements_or_error


def publish_if_new_announcements(bot, job):
    subscribers = sub_manager.read_subscribers()
    if len(subscribers) == 0:
        return

    last_retrieved = job.context['last_retrieved']
    
    ok, announcements_or_error = announcement_reader.get_announcements_after(last_retrieved)
    if not ok:
        error = announcements_or_error
        for subscriber in subscribers:
            bot.send_message(chat_id=subscriber, text='error: {}'.format(error))
        return
    announcements = announcements_or_error
    if len(announcements) == 0:
        logger.info('No new announcements')
        return
    formatted_announcements = get_announcements_formatted(announcements)
    text_to_send = '\n'.join(formatted_announcements)
    for subscriber in subscribers:
        chat_id = int(subscriber)
        bot.send_message(chat_id=chat_id, text=text_to_send)
        logger.info('Publishing new info to user id: {}'.format(chat_id))

    job.context['last_retrieved'] = datetime.datetime.now(datetime.timezone.utc) 


def get_announcements_formatted(announcements):
    announcement_texts = []
    announcement_texts.append('Recent announcements\n')
    for announcement in announcements:
        title = announcement['title']
        author = announcement['author']['display_name']
        # post time is in UTC because canvas returns a timestamp in UTC
        # the telegram api doesn't seem to support retrieving a timezone for a user
        # the canvas api supports this, so that can be used to format this timezone
        # a Course object contains timezone data, and announcements are tied to a course
        post_time = parser.parse(announcement['posted_at']).ctime()
        message = strip_tags(announcement['message'])
        announcement_texts.append('Title: {}\n\tAuthor: {}\n\tTime (UTC): {}\n\tMessage: {}\n'
                .format(title, author, post_time, message))
    
    return announcement_texts


def get(bot, update):
    logger.info('Received request for data')
    ok, announcements_or_error = retrieve_announcements_after_yesterday()
    if not ok:
        error = announcements_or_error
        update.message.reply_text('error: {}'.format(error))
    announcements = announcements_or_error
    formatted_announcements = get_announcements_formatted(announcements)
    text_to_send = '\n'.join(formatted_announcements)
    update.message.reply_text(text_to_send)


def subscribe(bot, update, job_queue, chat_data):
    chat_id = update.message.chat_id
    if sub_manager.add_subscriber(chat_id):
        update.message.reply_text('You are now subscribed to new announcements!')
        logger.info('New subscriber: {}, user: {}, chat: {}'
                .format(chat_id, update.message.from_user, update.message.chat))
    else: 
        update.message.reply_text('You are already subscribed.')


def unsubscribe(bot, update, chat_data):
    chat_id = update.message.chat_id
    if sub_manager.delete_subscriber(chat_id):
        update.message.reply_text('Successfully unsubscribed.')
        logger.info('Unsubscriber: {}'.format(chat_id))
    else:
        update.message.reply_text('You were not subscribed, so unsubscribing isn\'t possible.')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update {} caused error {}'.format(update, error))


def main():
    """Run bot."""
    telegram_api_key = read_telegram_api_key()

    updater = Updater(telegram_api_key)

    # job to send notifications to subscribers
    job_queue = updater.job_queue
    last_retrieved = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
    job_queue.run_repeating(callback=publish_if_new_announcements,
            interval=datetime.timedelta(minutes=5),
            first=0,
            context={'last_retrieved': last_retrieved})

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    #dp.add_handler(CommandHandler('get', get))
    dp.add_handler(CommandHandler('subscribe', subscribe,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe,
                                  pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    logger.info('Bot started')

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
