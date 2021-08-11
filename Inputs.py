import _thread
import json
import os
import time
from ahk import AHK

ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')
inputData = None
defaultDuration = 1
heldKeys = {}

# Key: Platform
# Value: Input
tempDisabledInputs = {}

def handle_key_event(data, duration = 0):
	outputs = data["outputs"]
	
	for output in outputs:
		key = output["output"]
		forcedDuration = output.get("duration")
		isMulti = output.get("isMulti")
		exitCond = output.get("exitCond")

		if forcedDuration is None:
			forcedDuration = duration
		else:
			duration = forcedDuration

		if duration > 0:
			hold_key(key, duration, isMulti, exitCond)
		else:
			press_key(key)

		for heldKey in heldKeys:
			if key == heldKeys[heldKey]:
				release_key(heldKey)
				heldKeys.pop(heldKey)
				break

# Presses the given key
def press_key(key):
	ahk.key_press(key)

# Holds the given key for the given duration
def hold_key(key, duration, isMulti, exitCond):
	ahk.key_down(key)

	if isMulti is not None and exitCond is not None:
		if key not in heldKeys:
			heldKeys[key] = exitCond

	if not isMulti:
		time.sleep(duration)
		release_key(key)

# Releases the given key
def release_key(key):
	ahk.key_release(key)

# Releases all currently held keys
def release_all_keys():
	# Release every key & remove them from list of held keys
	for key in heldKeys:
		ahk.key_release(key)
		heldKeys.pop(key)

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
	return data.get("aliases")

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