import _thread
import asyncio
import Inputs
from ahk import AHK
from Fun import try_play_sound
from signal import signal, SIGINT

# Set variables
ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')
channel = None
isActive = True;

# Stats
totalInputs = 0
inputUsage = {}

async def on_message_sent(messageData):
	if isActive == True:
		global game
		game = settings["game"]
		user = messageData.author
		global channel
		channel = messageData.channel
		rawData = messageData.raw_data
		tags = messageData.tags
		timestamp = messageData.timestamp
		message = messageData.content

		if message == "!inputs":
			await channel.send("@" + user.name + ": Here are the inputs for " + game + ": " + str(get_input_list()))
			print("[COMMAND] Sent list of inputs to {" + user.name + "}")
		else:
			inputName = message.split(" ", 1)[0] 
			data = Inputs.get_data_for_input(game, inputName)
			duration = Inputs.defaultDuration

			waitForWinActive = settings["waitForWinActive"]
			playSounds = settings["playSounds"]
			showStats = settings["showStats"]
			hasGivenDuration = False
			hasExitCond = False

			if data is not None:
				outputs = data["outputs"]

				for output in outputs:
					if output.get("exitCond") is not None:
						hasExitCond = True

				if not hasExitCond:
					for word in message.split(" "):
						try:
							duration = float(word)
							hasGivenDuration = True
							break
						except:
							continue

				_thread.start_new_thread(Inputs.handle_key_event, [data, duration])

				if hasGivenDuration:
					print("[INPUT] Input {" + inputName + "} triggered with duration of {" + str(duration) + "} by {" + user.name + "}")
				else:
					print("[INPUT] Input {" + inputName + "} triggered by {" + user.name + "}")

				if playSounds:
					_thread.start_new_thread(try_play_sound, [game, settings["playSoundsChanceOverride"]])
			else:
				print("[ERROR] No input data found for the game: " + game)

def handle_input(data, user):
	waitForWinActive = settings["waitForWinActive"]
	playSounds = settings["playSounds"]
	outputs = data["outputs"]

	print("[INPUT] Input '" + data["input"] + "' triggered by '" + user + "'!")

	if playSounds:
		_thread.start_new_thread(tryPlaySound, [game])

	# Run input(s)
	for output in outputs:
		key = output["output"]
		duration = output["duration"]
		isRecursive = output["isRecursive"]
		exitCond = output["exitCondition"]

		# Press/hold input
		if duration <= 0:
			ahk.key_press(key)
		else:
			ahk.key_down(key)
			if isRecursive:
				if exitCond:
					heldInputs[key] = exitCond
				else:
					heldInputs[key] = duration
			else:
				time.sleep(duration)
				ahk.key_release(key)

		# Check if any held input needs to be released based on exit condition
		for heldInput in heldInputs:
			keyToRelease = heldInput
			if key == heldInputs[heldInput]:
				ahk.key_release(keyToRelease)
				heldInputs.pop(heldInput)
				break

	# Release held inputs after their duration
	for heldInput in heldInputs:
		duration = heldInputs[heldInput]
		if type(duration) == int or type(duration) == float:
			_thread.start_new_thread(releaseInputAfterDelay, (ahk, heldInput, duration))

	# Update stats
	inputName = data["input"]
	global totalInputs
	totalInputs += 1
	if inputName in inputUsage:
		inputUsage[inputName] = inputUsage[inputName] + 1
	else:
		inputUsage[inputName] = 1

	return None

def get_input_list():
	allInputs = ""
	for input in get_all_inputs_for_game(game):
		allInputs += input["input"] + ", "

	size = len(allInputs)
	allInputs = allInputs[:size - 2]
	return allInputs

def on_quit(signal, frame):
	global isActive
	if isActive == True:
		print("\n--------------------------------------------------\n")
		print("Terminating from input...")
	
		isActive = False
		if channel is not None:
			loop = asyncio.get_event_loop()
			loop.create_task(channel.send("Twitch Plays is inactive. Here are the session's stats:"))
			loop.create_task(channel.send("Total input(s): " + str(totalInputs)))

			inputUsageOutput = "Top command(s): "
			iterations = 0
			for key, value in sorted(inputUsage.items(), key=lambda x: x[1], reverse=True):
				if iterations < 3:
					inputUsageOutput += key + ": " + str(value) + ", "
					iterations += 1

			size = len(inputUsageOutput)
			inputUsageOutput = inputUsageOutput[:size - 2]

			loop.create_task(channel.send(inputUsageOutput))

		print("\n--------------------------------------------------\n")
		#input("Press any key to exit...")

def apply_settings(loadedSettings):
	global settings
	settings = loadedSettings

signal(SIGINT, on_quit)