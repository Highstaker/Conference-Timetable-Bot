#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from random import randint

def breakLongMessage(msg, max_chars_per_message=2048):
	"""
	Breaks a message that is too long.
	:param max_chars_per_message: maximum amount of characters per message.
	The official maximum is 4096.
	Changing this is not recommended.
	:param msg: message to be split
	:return: a list of message pieces
	"""

	# let's split the message by newlines first
	message_split = msg.split("\n")

	# the result will be stored here
	broken = []

	# splitting routine
	while message_split:
		result = message_split.pop(0) + "\n"
		if len(result) > max_chars_per_message:
			# The chunk is huge. Split it not caring for newlines.
			broken += [result[i:i+max_chars_per_message] for i in range(0,len(result),max_chars_per_message)]
		else:
			# It's a smaller chunk, append others until their sum is bigger than maximum
			while len(result) <= max_chars_per_message:
				if not message_split:
					# if the original ran out
					break
				# check if the next chunk makes the merged chunk it too big
				if len(result) + len(message_split[0]) <= max_chars_per_message:
					# nope. append chunk
					result += message_split.pop(0) + "\n"
				else:
					# yes, it does. Stop on this.
					break
			broken += [result]


	return broken


###########################
data = ''
for i in range(randint(20, 100)):
	data += "".join([str(i%10) for i in range(randint(10,200))])
	data += "\n"
print(data)
broken = breakLongMessage(data)
print("BROKEN")
for i in broken:
	print(i)
	print("-"*40)
###############################
print("#"*100)
print("\n\n\n")

data='0'*10000
broken = breakLongMessage(data)
print("BROKEN")
for i in broken:
	print(i)
	print("-"*40)
###############################
print("#"*100)
print("\n\n\n")
