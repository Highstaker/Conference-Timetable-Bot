#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import logging
from os import path
from telegram import Updater

# The folder containing the script itself
SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN=""
BOT_TOKEN_FILENAME = "bot_token"
if path.isfile(path.join(SCRIPT_FOLDER, BOT_TOKEN_FILENAME)):
	with open(path.join(SCRIPT_FOLDER, BOT_TOKEN_FILENAME), 'r') as f:
		BOT_TOKEN = f.read().replace("\n", "")
else:
	print(BOT_TOKEN_FILENAME + " doesn't exist! Create it, please!")
	quit()

updater = Updater(token=BOT_TOKEN)

dispatcher = updater.dispatcher

def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

dispatcher.addTelegramCommandHandler('start', start)

def unknown(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
dispatcher.addUnknownTelegramCommandHandler(unknown)

def command_handler(bot, update,*args):
		bot.sendMessage(chat_id=update.message.chat_id, text="Command was " + update.message.text
																					)
dispatcher.addTelegramMessageHandler(command_handler)


def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

	# bot.sendMessage(chat_id=update.message.chat_id, text="Unknown error!")
	# print("error", error)
# log all errors
dispatcher.addErrorHandler(error)


print("Bot started!")
updater.start_polling()
