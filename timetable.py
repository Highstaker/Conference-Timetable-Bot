#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sqlite3
import re
from datetime import datetime, timedelta

from os import path

# The folder containing the script itself
SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

TABLE_NAME = "Events"
SUBSCRIPTIONS_TABLE_NAME = "Subscriptions"


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
class TimetableDatabase(object):
	"""docstring for TimetableDatabase"""
	def __init__(self, filename, server_params):
		"""

		:param filename: name of database file without extension
		:return:
		"""
		super(TimetableDatabase, self).__init__()
		self.server_params = server_params
		self.filename = filename + ".db"

		# if database already exists, do nothnig
		if path.isfile(path.join(SCRIPT_FOLDER, self.filename)):
			pass
		else:
			#database doesn't exist, create it
			self._createTable()

	@staticmethod
	def isDate(data):
		return bool(re.match("^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])$",data))

	@staticmethod
	def getUTCdatetime():
		"""
		Returns the UTC time as a datetime object
		:return: datetime object
		"""
		return datetime.utcnow()

	def getOffsetTime(self):
		"""
		Returns a timedate object representing the current time with the offset from UTC specified in server parameters.
		Basically, this is the manually set server time.
		:return: datetime object
		"""
		return self.getUTCdatetime() + timedelta(hours=self.server_params.getParam('timezone'))

	def parseTimetable(self, data):
		"""
		Parses the text data into the database
		:param data: Format of the input data (example):
		##2016/10/23
		#14:00@@Event Name@@Event Description@@Event location@@Event author
		#15:59@@Event Name@@Event Description@@Event location@@Event author
		##2016/10/24
		#16:00@@Event Name@@Event Description@@Event location@@Event author
		#17:30@@Event Name@@Event Description@@Event location@@Event author
		:return:
		"""

		# print(data)#debug
		# Removing empty lines and leading/trailing spaces/tabs/etc
		parse = "\n".join([i.strip(" \t\r") for i in data.split("\n") if i.strip(" \t\r")])

		print('parse \n', parse)#debug

		# split parts by days
		# the parts overlap with ## so (?=(something)) assures that overlapped parts are processed
		# DAY_TIMETABLE_PATTERN = "(?=(#{2}([^#].*)#{2}))"
		# day_searcher = re.compile(DAY_TIMETABLE_PATTERN, flags=re.DOTALL)
		# day_split = day_searcher.findall(parse)

		day_split = filter(None, re.split("##", parse))

		# print("day_split", day_split)#debug

		parse_processor = lambda event_date='', \
								event_time='', \
								event_name='', \
								description='', \
								location='', \
								author='': dict(date=event_date.strip('\n\t\r ')
								, time=event_time.strip('\n\t\r ')
								, name=event_name.strip('\n\t\r ')
								, desc=description.strip('\n\t\r ')
								, location=location.strip('\n\t\r ')
								, author=author.strip('\n\t\r '))

		result_parse = []
		date = None
		for day in day_split:
			event_split = re.split("#", day)
			date = event_split.pop(0)
			for event in event_split:
				print("event\n", event)#debug
				event_data_split = re.split("@@", event)
				print("event_data_split", event_data_split)
				result_parse += [parse_processor(date, event_data_split[0],event_data_split[1],
												event_data_split[2],event_data_split[3],
												event_data_split[4]
												)]

		print('result_parse', result_parse)

		for i in result_parse:
			self.createEvent(date=i['date'], time=i['time'], name=i['name'],
							 desc=i['desc'], location=i['location'], author=i['author'])

	def getDates(self):
		command = "SELECT DISTINCT date(event_time) FROM {0};".format(TABLE_NAME)

		dates = self._run_command(command)

		dates = [i[0] for i in dates]

		return dates

	def getTimetableMarkup(self):
		"""
		Returns a keyboard markup for a timetable showing depending on the days that are in the base
		:return: List
		"""
		def split_list(alist,max_size=1):
			"""Yield successive n-sized chunks from l."""
			for i in range(0, len(alist), max_size):
				yield alist[i:i+max_size]

		dates = self.getDates()

		markup = list(split_list(dates,3)) +[["All days"]]
		print(markup)
		return markup

	def setReminderStatus(self, chat_id, event_id, status):
		"""
		Sets the status of the reminder for current user and and event
		:param chat_id: user ID
		:param event_id:
		:param status: 0 = neither preliminary reminder nor the on-time one has been triggered
		1 = preliminary reminder has been triggered, on-time has not
		2 = bot reminders have been triggered already
		:return:
		"""
		command = """UPDATE {0} SET status={1}
WHERE chat_id={2} AND event_id={3};""".format(SUBSCRIPTIONS_TABLE_NAME,status,chat_id,event_id)

		self._run_command(command)

	def getEventData(self, id):
		"""
		Returns all teh data for a given event
		:param id: even ID
		:return:
		"""
		command = """SELECT event_name, time(event_time), location, description, date(event_time), author
				  FROM {0} WHERE id={1};""".format(TABLE_NAME,id)
		data = self._run_command(command)

		if data:
			return dict(id=id,name=data[0][0],time=data[0][1][:5],  # time without seconds
					location=data[0][2],desc=data[0][3],date=data[0][4],author=data[0][5])
		else:
			return None

	@staticmethod
	def stringTimeToDatetime(strdatetime):
		"""
		Converts the date and time as strings into `datetime` object
		:param strdatetime: string representation of date and time in "YYYY-MM-DD HH:MM" format
		:return: `datetime` object
		"""
		return datetime.strptime(strdatetime, "%Y-%m-%d %H:%M")

	def getEventDatetime(self, id):
		"""
		Returns the time of an event as a datetime object
		:param id: event ID
		:return: datetime object
		"""
		data = self.getEventData(id)

		result = self.stringTimeToDatetime(data['date'] + " " + data['time'])
		return result

	def getEventInfo(self, id):
		"""
		Returns a string representation of a detailed even information
		:param id: event ID
		:return: string
		"""
		data = self.getEventData(id)

		if data:
			result = """{0}
Time: {1} {4}
Held by: {5}
Location: {2}

{3}

To subscribe to this event, type or click the link:
/sub{6}
""".format(data['name'], data['time'][:5],data['location'],data['desc'],data['date'],data['author'],id)
		else:
			result = None

		return result

	def eventIndexExists(self, id):
		"""
		Returns True if an event with a given index exists
		:param id: event ID
		:return: bool
		"""
		command = "SELECT * FROM {0} WHERE id={1};".format(TABLE_NAME, id)

		data = self._run_command(command)

		return bool(data)

	def getDayTimetable(self, date):
		"""
		Returns a string representation of the timetable for the given date
		:param date: YYYY-MM-DD
		:return: string
		"""
		command = """SELECT id, event_time, event_name FROM {0}
WHERE date(event_time)=date('{1}')
ORDER BY time(event_time);""".format(TABLE_NAME, date)

		data = self._run_command(command)
		print("getDayTimetable", data)#debug

		result = date + ":\n\n"
		result += "\n".join(["/event{0} {1} {2}".format(i[0], i[1], i[2]) for i in data])
		result += "\n\n"

		return result

	def getUserTimetableData(self, chat_id):
		"""
		Returns brief data for events a given user has subscribed to.
		:param chat_id: user ID
		:return: list of tuples [(event ID, name, time, date),...]
		"""
		command = """SELECT id, event_name, event_time FROM {0} JOIN {1} ON {0}.id={1}.event_id AND {1}.chat_id={2}
ORDER BY date(event_time) DESC;
""".format(TABLE_NAME, SUBSCRIPTIONS_TABLE_NAME, chat_id)

		data = self._run_command(command)

		print('getUserTimetable', data)#debug

		return data

	def getUserTimetable(self, chat_id):
		"""
		Returns a string representation of timetable of events a given user has subscribed to.
		:param chat_id: user ID
		:return: string timetable
		"""
		data = self.getUserTimetableData(chat_id)



	def getAllDaysTimetable(self):
		dates = self.getDates()

		result = ""
		for date in dates:
			result += self.getDayTimetable(date)

		return result


	def _createTable(self):
		"""
		Initializes the database and the timetable
		:return:
		"""
		# Create the table of events
		command = """CREATE TABLE {0}(id INTEGER PRIMARY KEY,
								event_time TEXT,
								event_name TEXT,
								description TEXT,
								location TEXT,
								author TEXT
								);""".format(TABLE_NAME)

		self._run_command(command)

		# Create the table of subscriptions
		command = """CREATE TABLE {0}(chat_id INTEGER,
								event_id INTEGER,
								status INTEGER
								);""".format(SUBSCRIPTIONS_TABLE_NAME)

		self._run_command(command)

	def getUnnotifiedSubscriptions(self):
		command = """SELECT {0}.chat_id, {0}.event_id, {0}.status, {1}.event_time FROM {0}
JOIN {1} ON {0}.event_id={1}.id
WHERE status!=2;""".format(SUBSCRIPTIONS_TABLE_NAME, TABLE_NAME)

		data = self._run_command(command)
		print("getUnnotifiedSubscriptions", data)#debug
		return data

	def addSubscription(self, chat_id, event_id):
		"""
		Adds a subscription for reminders for given user and event
		:param chat_id: user ID
		:param event_id: event ID
		:return:
		"""
		status = 0
		event_time = self.getEventDatetime(event_id)
		if (self.getOffsetTime()-event_time).days >= 0:
			status = 2

		command = "INSERT INTO {0}(chat_id, event_id, status) VALUES ({1},{2},{3});".format(SUBSCRIPTIONS_TABLE_NAME,
																						chat_id, event_id, status)
		self._run_command(command)

	def subscriptionExists(self, chat_id, event_id):
		"""
		Returns True if a user is subscribed to a given event
		:param chat_id:
		:param event_id:
		:return: bool
		"""
		command = "SELECT * FROM {0} " \
				  "WHERE chat_id={1} AND event_id={2};".format(SUBSCRIPTIONS_TABLE_NAME, chat_id, event_id)

		data = self._run_command(command)

		return bool(data)

	def deleteSubscription(self, chat_id, event_id):
		"""
		Deletes a subscription for a given event for a user
		:param chat_id:
		:param event_id:
		:return:
		"""
		command = "DELETE FROM {0} " \
				  "WHERE chat_id={1} AND event_id={2};".format(SUBSCRIPTIONS_TABLE_NAME, chat_id, event_id)

		self._run_command(command)

	def createEvent(self, date, time, name, desc, location, author):
		"""
		Creates a database entry for an even with the given parameters
		:param date:
		:param time:
		:param name:
		:param desc:
		:param location:
		:param author:
		:return:
		"""
		def pS(text):
			# process strings for compatibility with SQLite
			result = text.replace("'", "''")
			return result


		timestamp = date + " " + time

		command = """INSERT INTO {0}(event_time, event_name, description, location, author)
VALUES ('{1}','{2}','{3}','{4}','{5}');
		""".format(TABLE_NAME, timestamp, pS(name), pS(desc), pS(location), pS(author))
		print(command)#debug

		self._run_command(command)

	def _run_command(self, command):
		"""
		Runs a given command and returns the output.
		:param command:
		:return:
		"""
		conn = sqlite3.connect(self.filename)
		cursor = conn.execute(command)
		data =[i for i in cursor]
		conn.commit()
		conn.close()

		return data

if __name__ == '__main__':
	T = TimetableDatabase("timetable")

	data = """##2016/02/16
	#14:00@@Dinner@@Nomnom time@@Dining room
	#16:00@@Day nap@@ZZZZZ time@@Couch
	#18:00@@Tea time@@Drinking tea@@Living room
	##2016/02/17
	 #14:00@@Dinner@@Nomnom time again@@Dining room
	#15:59@@Day nap@@ZZZZZ time. AGAIN!@@Couch
	  #18:00@@Tea time@@Drinking tea. As usual.@@Living room

	"""

	# T.parseTimetable(data)

