#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from os import path
import xlrd

# The folder containing the script itself
SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

class TestClass(object):
	"""docstring for TestClass"""
	def __init__(self, filename):
		super(TestClass, self).__init__()
		self.parseTimetableXLS(filename)

	def createEvent(self, *args, **kwargs):
		print(args, kwargs)
		pass
		
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


filename = path.join(SCRIPT_FOLDER, "NFC2016_timetable.xls")
TestClass(filename)
