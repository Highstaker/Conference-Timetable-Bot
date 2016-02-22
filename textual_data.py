#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

##############
# FILENAMES###
##############

SERVER_PARAMS_SAVEFILE_NAME = "Conference_timetable_bot_server_parameters.save"

MAP_FILENAME = "map.png"
EVENT_TIMETABLE_FILENAME = "timetable.txt"

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
HELP_MESSAGE = {"EN": "Help message", "RU": "Помощь"}
ABOUT_MESSAGE = "About"
OTHER_BOTS_MESSAGE = "Other bots"
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