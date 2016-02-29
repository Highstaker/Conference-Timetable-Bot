#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

##############
# FILENAMES###
##############

SERVER_PARAMS_SAVEFILE_NAME = "Conference_timetable_bot_server_parameters.save"

MAP_FILENAME = "map.png"
EVENT_TIMETABLE_FILENAME = "timetable.txt"
EVENT_TIMETABLE_XLS_FILENAME = "timetable.xls"

DATABASES_FOLDER_NAME = "databases"
RESOURCES_FOLDER_NAME = "resources"

# A temporary folder where files will be saved for processing
TEMP_FOLDER = "/tmp"

#############
# TEXTS######
#############

HELP_BUTTON = {"EN": "⁉️" + "Help", "RU": "⁉️" + "Помощь"}
ABOUT_BUTTON = {"EN": "ℹ️ About", "RU": "ℹ️ О программе"}
OTHER_BOTS_BUTTON = {"EN": "👾 My other bots", "RU": "👾 Другие мои боты"}

MAP_BUTTON = {"EN": "Map", "RU": "Карта"}
GET_TIMETABLE_BUTTON = {"EN": "Show timetable", "RU": "Показать расписание"}
ALL_DAYS_BUTTON = {"EN": "All days", "RU": "Все дни"}
SUBSCRIBE_BUTTON = {"EN": "Subscribe", "RU": "Подписаться"}
UNSUBSCRIBE_BUTTON = {"EN": "Unsubscribe", "RU": "Отписаться"}
MY_EVENTS_BUTTON = {"EN": "My events", "RU": "Мой список событий"}

EN_LANG_BUTTON = "🇬🇧 EN"
RU_LANG_BUTTON = "🇷🇺 RU"

START_MESSAGE = "Welcome! Type /help to get help."
MAP_MESSAGE = "Map message"
NO_MAP_FILE_MESSAGE = {"EN": "No map found", "RU": "Карта не найдена"}
GET_TIMETABLE_MESSAGE = {"EN": "Choose a day", "RU": "Выберите день"}
SUBSCRIBED_MESSAGE = "You have subscribed to event reminders."
ALREADY_SUBSCRIBED_MESSAGE = "You are already subscribed!"
UNSUBSCRIBED_MESSAGE = "You have unsubscribed to event reminders."
ALREADY_UNSUBSCRIBED_MESSAGE = "You are already unsubscribed!"
EVENT_NOT_FOUND_MESSAGE = {"EN": "Event not found!", "RU": "Мероприятие не найдено!"}
CURRENT_TIME_MESSAGE = {"EN": "Current time: {0}", "RU": "Текущее время: {0}"}

##################
# BIG TEXTS#######
##################

ABOUT_MESSAGE = {"EN": """*Conference Timetable Bot*
_Created by:_ Highstaker a.k.a. OmniSable.
For questions, suggestions and bug reports, ask @OmniSable.
[Source code](https://github.com/Highstaker/Conference-Timetable-Bot)
Version: {0}

This bot uses the [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot) library.
"""
,"RU": """*Conference Timetable Bot*
_Автор:_ Highstaker a.k.a. OmniSable.
По вопросам и предложениям обращайтесь в Телеграм (@OmniSable).
Исходный код [здесь](https://github.com/Highstaker/Conference-Timetable-Bot)
Версия: {0}

Этот бот написан на основе библиотеки [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot).
"""
}
HELP_MESSAGE = {"EN": """This bot shows the timetable and allows you to subscribe to certain events. They will appear in your personal timetable and you will be reminded about them beforehand and at the event start.

Type /timetable or press `{0}` button to enter the menu of dates. Press a date to receive a timetable for that date, along with graphical representation of that day's timetable (if available).
You can type /all or press the `{1}` button to get the timetable for all dates. Note that the graphical timetable is not shown in this case.

Each event in the timetable has a link in the format ` /eventN` (where N is the ID number of the event). Press or type it to get detailed information about the event.
At the bottom of an event summary there is a link in a format ` /subN`. Click it to subscribe to an event. That way it will appear in your list of selected events, which you can access by pressing the `{2}` button or typing /myevents. Additionally, you will be reminded about this event when it starts and several minutes before it starts (the default is 30 minutes before the event. You can set this period by simply typing any number), but only if you have subscribed to reminders. Press the `{3}` button or type /subscribe to subscribe to event reminders.

"""
, "RU": "Помощь"}

OTHER_BOTS_MESSAGE = {"EN": """*My other bots*:

@multitran_bot: a Russian-Whichever dictionary with support of 9 languages. Has transcriptions for English words.

@OmniCurrencyExchangeBot: a currency converter bot supporting past rates and graphs.
"""
, "RU": """*Другие мои боты*:

@multitran_bot: Русско-любой словарь с поддержкой 9 языков. Есть транскрипции английских слов.

@OmniCurrencyExchangeBot: Конвертер валют с поддержкой графиков и прошлых курсов.
"""
}

##################
# DICTIONARIES####
##################

MONTHS = {
	1: {"EN": "Jan.", "RU": "Янв."},
	2: {"EN": "Feb.", "RU": "Фев."},
	3: {"EN": "Mar.", "RU": "Мар."},
	4: {"EN": "Apr.", "RU": "Апр."},
	5: {"EN": "May", "RU": "Май"},
	6: {"EN": "Jun.", "RU": "Июн."},
	7: {"EN": "Jul.", "RU": "Июл."},
	8: {"EN": "Aug.", "RU": "Авг.."},
	9: {"EN": "Sep.", "RU": "Сен."},
	10: {"EN": "Oct.", "RU": "Окт."},
	11: {"EN": "Nov.", "RU": "Ноя."},
	12: {"EN": "Dec.", "RU": "Дек."}
		  }

WEEKDAYS = {
	0: {"EN": "Mon.", "RU": "Пн."},
	1: {"EN": "Tue.", "RU": "Вт."},
	2: {"EN": "Wed.", "RU": "Ср."},
	3: {"EN": "Thu.", "RU": "Чт."},
	4: {"EN": "Fri.", "RU": "Пт."},
	5: {"EN": "Sat.", "RU": "Сб."},
	6: {"EN": "Sun.", "RU": "Вс."}
}