#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sqlite3
import re
from datetime import datetime, timedelta
from os import path
import xlrd

from textual_data import EVENT_NOT_FOUND_MESSAGE, DATABASES_FOLDER_NAME

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
		self.filename = path.join(SCRIPT_FOLDER, DATABASES_FOLDER_NAME, filename + ".db")

		# if database already exists, do nothnig
		if path.isfile(self.filename):
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

	# noinspection PyUnnecessaryBackslash
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

		day_split = filter(None, re.split("##", parse))

		parse_processor = lambda event_date='', \
								event_time='', \
								event_name='', \
								description='', \
								location='', \
								author='',\
								end_time = '',\
								event_type = '': dict(date=event_date.strip('\n\t\r ')
								, time=event_time.strip('\n\t\r ')
								, name=event_name.strip('\n\t\r ')
								, desc=description.strip('\n\t\r ')
								, location=location.strip('\n\t\r ')
								, author=author.strip('\n\t\r ')
								, end_time=end_time.strip('\n\t\r ')
								, event_type=event_type.strip('\n\t\r ')
													  )

		result_parse = []
		for day in day_split:
			event_split = re.split("#", day)
			date = event_split.pop(0)
			for event in event_split:
				event_data_split = re.split("@@", event)
				result_parse += [parse_processor(date, event_data_split[0],event_data_split[1],
												event_data_split[2],event_data_split[3],
												event_data_split[4],event_data_split[5],
												event_data_split[6]
												)]

		for i in result_parse:
			self.createEvent(date=i['date'], time=i['time'], name=i['name'],
							 desc=i['desc'], location=i['location'], author=i['author'],
							 end_time=i['end_time'], event_type=i['event_type'])

	def parseTimetableXLS(self, filename):
		book = xlrd.open_workbook(filename)
		sheet = book.sheet_by_index(0)

		date = ""
		result_parse = []
		for event in range(1, sheet.nrows):
			cells = sheet.row_values(event)
			# print('len(cells)', len(cells))#debug
			event_data = dict()

			for n, cell in enumerate(cells):
				if n == 0:
					#A date
					if cell:
						# store date for use with other events on this day
						date = cell
					event_data['date'] = date
				if n == 1:
					# start time
					event_data['time'] = cell
				if n == 2:
					# end time
					event_data['end_time'] = cell
				if n == 3:
					# Name of the event
					event_data['name'] = cell
				if n == 4:
					# Event description
					event_data['desc'] = cell
				if n == 5:
					# event location
					event_data['location'] = cell
				if n == 6:
					# event type
					event_data['event_type'] = cell
				if n == 7:
					# The person who holds this event
					event_data['author'] = cell

			result_parse += [event_data]

		for i in result_parse:
			self.createEvent(date=i['date'], time=i['time'], name=i['name'],
							 desc=i['desc'], location=i['location'], author=i['author'],
							 end_time=i['end_time'], event_type=i['event_type'])

	def getDates(self):
		"""
		Returns a list of all dates present in the timetable
		:return:
		"""
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
		command = """SELECT event_name, time(event_time), location, description, date(event_time), author,
					time(end_time), event_type
			  		FROM {0} WHERE id={1};""".format(TABLE_NAME,id)
		data = self._run_command(command)[0]
		data = [i if not i is None else "" for i in data]
		print(data)#debug

		if data:
			return dict(id=id,name=data[0],time=data[1][:5],  # time without seconds
						location=data[2],desc=data[3],date=data[4],author=data[5],end_time=data[6],
						event_type=data[7])
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
			duration = ""
			if data['end_time']:
				duration = round(
							round(
							(self.stringTimeToDatetime(data['date'] + " " + data['end_time'][:5])
							- self.stringTimeToDatetime(data['date'] + " " + data['time'][:5])
							).seconds/60
							)/60
							,1)


			result = """{0}
Date: {4}
Time: {1} - {6}
Duration: {8} h.
Held by: {5}
Type: {7}
Location: {2}

{3}

To subscribe to this event, type or click the link:
/sub{9}
""".format(data['name'], data['time'][:5],data['location'],data['desc'],data['date'],data['author'],
			data['end_time'][:5],data['event_type'],duration,id)
		else:
			result = EVENT_NOT_FOUND_MESSAGE

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

		result = ""
		if data:
			result += "\n".join(["/event{0} {1} {2}".format(i[0], i[2], i[1]) for i in data])

		return result


	def getAllDaysTimetable(self):
		"""
		Returns a string representation of timetable for all days.
		:return:
		"""
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
								author TEXT,
								end_time TEXT,
								event_type TEXT
								);""".format(TABLE_NAME)

		self._run_command(command)

		# Create the table of subscriptions
		command = """CREATE TABLE {0}(chat_id INTEGER,
								event_id INTEGER,
								status INTEGER
								);""".format(SUBSCRIPTIONS_TABLE_NAME)

		self._run_command(command)

	def getUnnotifiedSubscriptions(self):
		"""
		Returns all subscription that have not been notified yet.
		:return:
		"""
		command = """SELECT {0}.chat_id, {0}.event_id, {0}.status, {1}.event_time FROM {0}
JOIN {1} ON {0}.event_id={1}.id
WHERE status!=2;""".format(SUBSCRIPTIONS_TABLE_NAME, TABLE_NAME)

		data = self._run_command(command)
		# print("getUnnotifiedSubscriptions", data)#debug
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

	def createEvent(self, date, time, name, desc, location, author, end_time, event_type):
		"""
		Creates a database entry for an even with the given parameters
		:param event_type:
		:param end_time:
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

		def checkEndDate(ts, end_ts):
			#If the end of event happens the next day, move the end time one day forward
			start_dt = self.stringTimeToDatetime(ts)
			end_dt = self.stringTimeToDatetime(end_ts)

			if (end_dt - start_dt).days < 0:
				end_dt += timedelta(days=1)

			return end_dt.strftime("%Y-%m-%d %H:%M")


		timestamp = (date + " " + time) if time else ""
		end_timestamp = (date + " " + end_time) if end_time else ""
		if end_timestamp:
			end_timestamp = checkEndDate(timestamp,end_timestamp)

		command = """INSERT INTO {0}(event_time, event_name, description, location, author, end_time, event_type)
VALUES ('{1}','{2}','{3}','{4}','{5}','{6}','{7}');
		""".format(TABLE_NAME, timestamp, pS(name), pS(desc), pS(location), pS(author), end_timestamp, pS(event_type))
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
