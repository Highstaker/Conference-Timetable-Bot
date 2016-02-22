#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import os
import re
from os import path
# from datetime import datetime

from languagesupport import LanguageSupport
from serverparams import ServerParameters
from telegramHigh import telegramHigh
from textual_data import *
from timetable import TimetableDatabase
from tracebackprinter import full_traceback
from usersparams import UserParams

VERSION_NUMBER = (0, 3, 1)

# The folder containing the script itself
SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

# A temporary folder where files will be saved for processing
TEMP_FOLDER = "/tmp"

INITIAL_SUBSCRIBER_PARAMS = {"lang": "EN",  # bot's langauge
							"admin": 0,
							 "remind_period": 0, # remind this amount of minutes before the event
							 "subscribed": 0 # is the user subscribed to event reminders?
							}

INITIAL_SERVER_PARAMS = {
						"timezone": 0
						}

MAIN_MENU_KEY_MARKUP = [
	[MAP_BUTTON, GET_TIMETABLE_BUTTON],
	[SUBSCRIBE_BUTTON, UNSUBSCRIBE_BUTTON, MY_EVENTS_BUTTON],
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
		self.server_params = ServerParameters(savefile_name=SERVER_PARAMS_SAVEFILE_NAME,
											  initial_params=INITIAL_SERVER_PARAMS
											  )
		self.bot = telegramHigh(BOT_TOKEN)
		self.user_params = UserParams(filename="conference_timetable_userparams", initial=INITIAL_SUBSCRIBER_PARAMS)
		self.timetable_db = TimetableDatabase("timetable",self.server_params)

		# starts the main loop
		self.bot.start(processingFunction=self.processUpdate
					, periodicFunction=self.periodicFunction
					# , termination_function=self.termination_function
					)

	def assignBotLanguage(self, chat_id, language):
		"""
		Assigns bot language to a subscribers list and saves to disk
		:param language:
		:param chat_id:
		:return: None
		"""
		self.user_params.setEntry(chat_id=chat_id, param="lang", value=language)

	def periodicFunction(self):
		bot = self.bot

		# process reminders
		# Get reminder data from DB
		reminders = self.timetable_db.getUnnotifiedSubscriptions()

		for event in reminders:
			chat_id = event[0]
			event_id = event[1]
			status = event[2]
			event_time = TimetableDatabase.stringTimeToDatetime(event[3])
			cur_time = self.timetable_db.getOffsetTime()

			if status < 2:
				# this event still has reminders
				if (cur_time-event_time).days >= 0:
					# Remind when an event starts
					if self.user_params.getEntry(chat_id, 'subscribed') == 1:
						bot.sendMessage(chat_id=chat_id
									, message="Event {0} is starting now!".format(event_id)
									, key_markup="Same"
							)
					self.timetable_db.setReminderStatus(chat_id, event_id, 2)
			if status < 1:
				# preliminary reminder is not triggered yet
				remind_period = self.user_params.getEntry(chat_id,'remind_period')
				till_event_delta = event_time-cur_time
				# print("till_event_delta",till_event_delta)#debug
				if self.user_params.getEntry(chat_id,'subscribed') == 1 \
					and till_event_delta.days >= 0 \
					and till_event_delta.seconds <= remind_period * 60:
					# Set status to 1 and trigger preliminary reminder
					self.timetable_db.setReminderStatus(chat_id, event_id, 1)
					bot.sendMessage(chat_id=chat_id
									, message="Event {0} is starting in {1} minutes!".format(event_id,till_event_delta.seconds//60)
									, key_markup="Same"
							)


			#Cleanup of all status 2


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
			print('message', message)
			response = lS(CURRENT_TIME_MESSAGE).format(self.timetable_db.getOffsetTime().strftime("%H:%M")) \
			+ "\n\n" \
			+ self.timetable_db.getDayTimetable(message)
			bot.sendMessage(chat_id=chat_id
							, message=response
							, key_markup=MMKM
							)
			#If a graphical file in format YYYY-MM-DD.png exists, send it as well
			try:
				filepath = path.join(SCRIPT_FOLDER, message) + ".png"
				with open(filepath, "rb") as pic:
						bot.sendPic(chat_id=chat_id
						, pic=pic
						, caption=message
								)
			except FileNotFoundError as e:
				print("Graph file not found")
				print(full_traceback())

		elif message in allv(ALL_DAYS_BUTTON):
			# it is a date, show day timetable
			response = lS(CURRENT_TIME_MESSAGE).format(self.timetable_db.getOffsetTime().strftime("%H:%M")) \
			+ "\n\n" \
			+ self.timetable_db.getAllDaysTimetable()

			bot.sendMessage(chat_id=chat_id
							, message=response
							, key_markup=MMKM
							)
		elif re.match("^/event[0-9]+$", message):
			# Event link is pressed
			event_info = self.timetable_db.getEventInfo(message[6:])
			if event_info:
				response = lS(CURRENT_TIME_MESSAGE).format(self.timetable_db.getOffsetTime().strftime("%H:%M")) \
				+ "\n\n" \
				+ event_info
				bot.sendMessage(chat_id=chat_id
							, message=response
							, key_markup=MMKM
							)
			else:
				bot.sendMessage(chat_id=chat_id
							, message=lS(EVENT_NOT_FOUND_MESSAGE)
							, key_markup=MMKM
							, reply_to=message_id
							)
		elif message == "/subscribe" or message in allv(SUBSCRIBE_BUTTON):
			if self.user_params.getEntry(chat_id, "subscribed") == 0:
				self.user_params.setEntry(chat_id, "subscribed", 1)
				bot.sendMessage(chat_id=chat_id
							, message=lS(SUBSCRIBED_MESSAGE)
							, key_markup=MMKM
							)
			else:
				bot.sendMessage(chat_id=chat_id
							, message=lS(ALREADY_SUBSCRIBED_MESSAGE)
							, key_markup=MMKM
							)
		elif message == "/unsubscribe" or message in allv(UNSUBSCRIBE_BUTTON):
			if self.user_params.getEntry(chat_id, "subscribed") == 1:
				self.user_params.setEntry(chat_id, "subscribed", 0)
				bot.sendMessage(chat_id=chat_id
							, message=lS(UNSUBSCRIBED_MESSAGE)
							, key_markup=MMKM
							)
			else:
				bot.sendMessage(chat_id=chat_id
							, message=lS(ALREADY_UNSUBSCRIBED_MESSAGE)
							, key_markup=MMKM
							)
		elif message == "my_events" or message in allv(MY_EVENTS_BUTTON):
			# show a table of events to which a user is subscribed
			self.timetable_db.getUserTimetable(chat_id=chat_id)
		elif re.match("^/sub[0-9]+$",message):
			event_index = message[4:]
			if self.timetable_db.eventIndexExists(event_index):
				# Event exists
				if not self.timetable_db.subscriptionExists(chat_id, event_index):
					self.timetable_db.addSubscription(chat_id, event_index)
					bot.sendMessage(chat_id=chat_id
									, message="You have subscribed to event {0}".format(event_index)
									, key_markup=MMKM
									)
				else:
					self.timetable_db.deleteSubscription(chat_id,event_index)
					bot.sendMessage(chat_id=chat_id
									, message="Subscription to event {0} deleted!".format(event_index)
									, key_markup=MMKM
									)
			else:
				# such event doesn't exist
				bot.sendMessage(chat_id=chat_id
							, message="Event with index {0} doesn't exist!".format(event_index)
							, key_markup=MMKM
							, reply_to=message_id
							)
		elif re.match("^[0-9]+$",message):
			self.user_params.setEntry(chat_id, 'remind_period', int(message))
			bot.sendMessage(chat_id=chat_id
							, message="Preliminary reminder period has been set to {0}".format(message)
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
		elif bot.isDocument(u) and self.user_params.getEntry(chat_id, 'admin') == 1:
			# check if it is a timetable
			if bot.getDocumentFileName(u) == EVENT_TIMETABLE_FILENAME:
				full_path = path.join(TEMP_FOLDER, EVENT_TIMETABLE_FILENAME)
				bot.downloadFile(bot.getFileID(u), full_path)

				try:
					with open(full_path, "r") as f:
						data = f.read()
						print(data)
						self.timetable_db.parseTimetable(data)

					os.remove(full_path)

					bot.sendMessage(chat_id=chat_id
								, message="Events added!"
								, key_markup=MMKM
								)
				except IndexError:
						bot.sendMessage(chat_id=chat_id
								, message="Parsing failed! Are all fields present in the file?"
								, key_markup=MMKM
								)
		elif re.match("^TZ(\+|-)([0-9]|[0-1][0-9]|2[0-3])$", message) and self.user_params.getEntry(chat_id, 'admin') == 1:
			# Setting the timezone parameter
			timezone = int(message[2:])
			self.server_params.setParam('timezone', timezone)
			bot.sendMessage(chat_id=chat_id
							, message="Timezone set to UTC{0}{1}".format("+" if timezone >= 0 else "", timezone)
							, key_markup=MMKM
							)
		elif message == "/revoke" and self.user_params.getEntry(chat_id, 'admin') == 1:
			# revoke admin rights
			self.user_params.setEntry(chat_id, 'admin', 0)
			bot.sendMessage(chat_id=chat_id
							, message="Admin rights revoked"
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