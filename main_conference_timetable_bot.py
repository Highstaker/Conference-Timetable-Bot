#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import os
from os import path

from languagesupport import LanguageSupport
from telegramHigh import telegramHigh
from textual_data import *
from timetable import TimetableDatabase
from usersparams import UserParams

VERSION_NUMBER = (0, 1, 3)

# The folder containing the script itself
SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

# A temporary folder where files will be saved for processing
TEMP_FOLDER = "/tmp"

INITIAL_SUBSCRIBER_PARAMS = {"lang": "EN",  # bot's langauge

							}
MAIN_MENU_KEY_MARKUP = [
	[MAP_BUTTON, GET_TIMETABLE_BUTTON],
	[HELP_BUTTON, ABOUT_BUTTON, OTHER_BOTS_BUTTON],
	[EN_LANG_BUTTON, RU_LANG_BUTTON]
]

#################
# GLOBALS###
#################
BOT_TOKEN = ""
BOT_TOKEN_FILENAME = "bot_token"
if path.isfile(path.join(SCRIPT_FOLDER, BOT_TOKEN_FILENAME)):
	with open(path.join(SCRIPT_FOLDER, BOT_TOKEN_FILENAME), 'r') as f:
		BOT_TOKEN = f.read().replace("\n", "")
else:
	print(BOT_TOKEN_FILENAME + " doesn't exist! Create it, please!")
	quit()

class ConferenceTimetableBot(object):
	"""docstring for ConferenceTimetableBot"""
	def __init__(self):
		super(ConferenceTimetableBot, self).__init__()
		self.bot = telegramHigh(BOT_TOKEN)
		self.user_params = UserParams(filename="conference_timetable_userparams", initial=INITIAL_SUBSCRIBER_PARAMS)
		self.timetable_db = TimetableDatabase("timetable")

		# starts the main loop
		self.bot.start(processingFunction=self.processUpdate
					# ,periodicFunction=self.periodicFunction
					# ,termination_function=self.termination_function
					)

	def assignBotLanguage(self, chat_id, language):
		"""
		Assigns bot language to a subscribers list and saves to disk
		:param language:
		:param chat_id:
		:return: None
		"""
		self.user_params.setEntry(chat_id=chat_id, param="lang", value=language)

	def processUpdate(self, u):
		bot = self.bot
		Message = u.message
		message = Message.text
		message_id = Message.message_id
		chat_id = Message.chat_id

		subs = self.user_params

		subs.initializeUser(chat_id=chat_id, data=INITIAL_SUBSCRIBER_PARAMS)

		# language support class for convenience
		LS = LanguageSupport(subs.getEntry(chat_id=chat_id, param="lang"))
		lS = LS.languageSupport
		allv = LS.allVariants
		MMKM = lS(MAIN_MENU_KEY_MARKUP)

		if message == "/start":
			bot.sendMessage(chat_id=chat_id
							, message=lS(START_MESSAGE)
							, key_markup=MMKM
							)
		elif message == "/help" or message in allv(HELP_BUTTON):
			bot.sendMessage(chat_id=chat_id
							, message=lS(HELP_MESSAGE)
							, key_markup=MMKM
							, markdown=True
							)
		elif message == "/about" or message in allv(ABOUT_BUTTON):
			bot.sendMessage(chat_id=chat_id
							, message=lS(ABOUT_MESSAGE)
							, key_markup=MMKM
							, markdown=True
							)
		elif message == "/otherbots" or message in allv(OTHER_BOTS_BUTTON):
			bot.sendMessage(chat_id=chat_id
							, message=lS(OTHER_BOTS_MESSAGE)
							, key_markup=MMKM
							)
		elif message == "/map" or message in allv(MAP_BUTTON):
			if path.isfile(path.join(SCRIPT_FOLDER, MAP_FILENAME)):
				bot.sendPic(chat_id=chat_id
						, pic=open(path.join(SCRIPT_FOLDER, MAP_FILENAME), "rb")
						, caption=MAP_MESSAGE
								)
			else:
				# There is no map file, notify user
				bot.sendMessage(chat_id=chat_id
							, message=lS(NO_MAP_FILE_MESSAGE)
							, key_markup=MMKM
							)
		elif message == "/timetable" or message in allv(GET_TIMETABLE_BUTTON):
			bot.sendMessage(chat_id=chat_id
							, message=lS(GET_TIMETABLE_MESSAGE)
							, key_markup=self.timetable_db.getTimetableMarkup()
							)
		elif TimetableDatabase.isDate(message):
			# it is a date, show day timetable
			bot.sendMessage(chat_id=chat_id
							, message=self.timetable_db.getDayTimetable(message)
							, key_markup=MMKM
							)
		elif message in allv(ALL_DAYS_BUTTON):
			# it is a date, show day timetable
			bot.sendMessage(chat_id=chat_id
							, message=self.timetable_db.getAllDaysTimetable()
							, key_markup=MMKM
							)
		elif message == RU_LANG_BUTTON:
			self.assignBotLanguage(chat_id, 'RU')
			LS = LanguageSupport(subs.getEntry(chat_id=chat_id, param="lang"))
			key_markup = LS.languageSupport(message=MAIN_MENU_KEY_MARKUP)
			bot.sendMessage(chat_id=chat_id
							, message="Сообщения бота будут отображаться на русском языке."
							, key_markup=key_markup
							)
		elif message == EN_LANG_BUTTON:
			self.assignBotLanguage(chat_id, 'EN')
			LS = LanguageSupport(subs.getEntry(chat_id=chat_id, param="lang"))
			key_markup = LS.languageSupport(message=MAIN_MENU_KEY_MARKUP)
			bot.sendMessage(chat_id=chat_id
							, message="Bot messages will be shown in English."
							, key_markup=key_markup
							)

		# admin tools
		elif bot.isDocument(u):
			# check if it is a timetable
			if bot.getDocumentFileName(u) == EVENT_TIMETABLE_FILENAME:
				full_path = path.join(TEMP_FOLDER, EVENT_TIMETABLE_FILENAME)
				bot.downloadFile(bot.getFileID(u), full_path)

				with open(full_path, "r") as f:
					data = f.read()
					print(data)
					self.timetable_db.parseTimetable(data)

				os.remove(full_path)

				bot.sendMessage(chat_id=chat_id
							, message="Events added!"
							, key_markup=MMKM
							)
		else:
			bot.sendMessage(chat_id=chat_id
							, message="Unknown command!"
							, key_markup=MMKM
							)
	

def main():
	BOT = ConferenceTimetableBot()

if __name__ == '__main__':
	main()