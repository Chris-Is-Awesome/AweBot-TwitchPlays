import json
import os
import time
from ahk import AHK

ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')
inputData = None
defaultDuration = 1

# Key: Platform
# Value: Input
tempDisabledInputs = {}

def handle_key_event(key, duration):
	if duration > 0:
		hold_key(key, duration)
	else:
		press_key(key)

# Presses the given key
def press_key(key):
	ahk.key_press(key)
	print("Pressed key " + key)

# Holds the given key for the given duration
def hold_key(key, duration):
	ahk.key_down(key)
	print("Holding key " + key + " for duration " + str(duration))

	time.sleep(duration)
	release_key(key)

# Releases the given key
def release_key(key):
	ahk.key_release(key)
	print("Released key " + key)

# Returns json data for the given input or None if it data not found
def get_data_for_input(wantedGame, wantedInput):
	# Load data
	if inputData is None:
		load_input_data(wantedGame)

	# Read data
	program = inputData["program"]
	global defaultDuration
	defaultDuration = inputData["defaultDuration"]
	inputs = inputData["inputs"]
	
	# For each input
	for inputInfo in inputs:
		inputName = inputInfo["input"]
		aliases = inputInfo.get("aliases")

		# If wanted input is valid
		if inputName == wantedInput or (aliases is not None and wantedInput in aliases):

			# If input is not temporarily disabled
			if inputName not in tempDisabledInputs:
				return inputInfo

	return None

# Returns list of all inputs for the given game
def get_all_inputs_for_game(game):
	# Load data
	if inputData is None:
		load_input_data(game)

	return inputData["inputs"]

# Returns list of all aliases for the given input
def get_all_aliases_for_input(data):
	if data is not None:
		return data.get("aliases")
	return None

# Loads & parses input data from json for the given game
def load_input_data(game):
	file = open(get_config_for_game(game))

	global inputData
	inputData = json.load(file)

	file.close()

	return inputData

# Fetches the specific file for the given game
def get_config_for_game(game):
	game = game.replace(" ", "")
	path = os.getcwd() + "\\configs\\"

	# If path exists
	if os.path.isdir(path):
		for file in os.listdir(path):
			if game.lower() in file.lower():
				return path + file

	return None