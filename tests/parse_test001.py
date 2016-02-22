#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import re

def parseTimetable(data):
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

data = """##2016-02-19
	#14:00@@Dinner@@Nomnom time@@Dining room@@Da'wg
	#16:00@@Day nap@@ZZZZZ time@@Couch@@Cat
	#18:00@@Tea time@@Drinking tea@@Living room@@Hooman
	##2016-02-20
	 #14:00@@Dinner@@Nomnom time again@@Dining room@@Da'wg
	#15:59@@Day nap@@ZZZZZ time.
	YES! AGAIN!@@Couch@@Cat
	  #18:00@@Tea time@@Drinking tea. As usual.@@Living room@@Hooman
    #09:00@@waking up@@It's a "pain", really@@Bed, where else?@@Cat, Hooman

"""

parseTimetable(data)