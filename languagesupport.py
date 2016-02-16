#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-


class LanguageSupport(object):
	"""A class handling dictionaries of strings in several languages"""

	def __init__(self, lang):
		super(LanguageSupport, self).__init__()
		self.lang = lang

	def languageSupport(self, message):
		"""
		Returns a message depending on a language chosen by user
		:param message:
		"""
		lang = self.lang
		if isinstance(message, str):
			result = message
		elif isinstance(message, dict):
			try:
				result = message[lang]
			except KeyError:
				result = message["EN"]
		elif isinstance(message, list):
			# could be a key markup
			result = list(message)
			for n, i in enumerate(message):
				result[n] = self.languageSupport(i)
		else:
			result = ""

		return result

	def allVariants(self, data):
		"""
		Returns a list of all translations, if data is a dictionary.
		If it is a string, returns a list with one entry `data`
		:return: a list
		"""
		if isinstance(data, str):
			return [data]
		elif isinstance(data, dict):
			return [i for i in data.values()]
