#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import pickle
import logging
from os import path

from textual_data import DATABASES_FOLDER_NAME

# The folder containing the script itself
SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

# noinspection PyPep8
class ServerParameters(object):
	"""docstring for ServerParameters"""

	def __init__(self, savefile_name, initial_params, from_file=True):
		super(ServerParameters, self).__init__()
		self.params = initial_params
		self.params_backup_filename = path.join(SCRIPT_FOLDER, DATABASES_FOLDER_NAME, savefile_name)  # backup filename

		if from_file:
			self._loadParams()  # load subscribers from a file, if it exists

	def _loadParams(self):
		"""
		Loads subscribers from a file. Show warning if it doesn't exist.
		"""
		try:
			with open(self.params_backup_filename, 'rb') as f:
				self.params = pickle.load(f)
				logging.warning(("self.params", self.params))
		except FileNotFoundError:
			logging.warning("Parameters file not found. Initializing from initials!")

	def _saveParams(self):
		"""
		Saves a subscribers list to file
		"""
		with open(self.params_backup_filename, 'wb') as f:
			pickle.dump(self.params, f, pickle.HIGHEST_PROTOCOL)

	def getParam(self, param):
		"""
		Returns a parameter from subscribers list.
		:param param: a key of a parameter to be retrieved
		:return: a specified parameter
		"""
		return self.params[param]

	def setParam(self, param, value, save=True, append=False):
		"""
		Sets the given parameter to a certain value
		:param append: if False, the parameter is set to value. It True, the value is appended to the parameter (e.g. list)
		:param param: a key of a parameter to be modified
		:param value: value to set to a parameter
		:param save: saves the subscribers list to file if True
		:return: None
		"""
		if append:
			self.params[param] += value
		else:
			self.params[param] = value
		if save:
			self._saveParams()
