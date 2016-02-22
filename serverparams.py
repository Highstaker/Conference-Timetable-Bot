#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import pickle
import logging


# noinspection PyPep8
class ServerParameters(object):
	"""docstring for ServerParameters"""

	def __init__(self, savefile_name, initial_params, from_file=True):
		super(ServerParameters, self).__init__()
		self.params = initial_params
		self.params_backup_filename = savefile_name  # backup filename

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

	# def init_user(self, chat_id, force=False, params=None, save=True):
	# 	"""
	# 	Initializes a user with initialparams
	# 	:param chat_id: user's chat id number
	# 	:param force: if False, do not initialize a user if they already exist
	# 	:param params: a dictionary of parameters that should be assigned on initialization
	# 	:param save: saves the subscribers list to file if True and if initialization took place
	# 	:return: None
	# 	"""
	# 	if not (chat_id in self.params.keys()) or force:
	# 		# T T = T
	# 		# F T = T
	# 		# T F = T
	# 		# F F = F
	# 		self.params[chat_id] = self.initial_params.copy()
	# 		if params:
	# 			for i in params:
	# 				self.params[chat_id][i] = params[i]
	# 		if save:
	# 			self.saveSubscribers()

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

	# def popFromParam(self, chat_id, param, index):
	# 	"""
	# 	Pops a value from a list, if it is a list. Does nothing if it is not.
	# 	:param chat_id: user's chat id number
	# 	:param param: a key of a parameter to be modified
	# 	:param index: index of a value to be removed
	# 	:return: the removed value. None if it was not a list/
	# 	"""
	# 	if isinstance(self.params[param], list):
	# 		try:
	# 			val = self.params[param].pop(index)
	# 			return val
	# 		except IndexError:
	# 			return None
	# 	else:
	# 		return None
