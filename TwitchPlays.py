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

		# Inputs command
		if message == "!inputs":
			await channel.send("@" + user.name + ": Here are the inputs for " + game + ": " + str(get_input_list()))
			print("[COMMAND] Sent list of inputs to {" + user.name + "}")
		elif message == "!help":
			await channel.send("@" + user.name + ": Welcome to Twitch Plays! Twitch Plays is an interactive stream where you type inputs in chat and it sends those inputs to the game you're watching! You can optionally give a duration in seconds for the input (whole number or decimal)! Here's an example: {up 10} will move the player up for 10 seconds. Type !inputs to get the list of inputs or {!aliases <input name>} to get list of aliases")
			print("[COMMAND] Sent help to {" + user.name + "}")
		else:
			# Aliases command
			if message.startswith("!aliases"):
				words = message.split(" ", 2)
				if len(words) > 1:
					aliases = Inputs.get_all_aliases_for_input(Inputs.get_data_for_input(game, words[1].lower()))
					
					if aliases is not None:
						aliasesOutput = "@" + user.name + ": Aliases for " + words[1].lower() + ": "

						for alias in aliases:
							aliasesOutput += alias + ", "

						size = len(aliasesOutput)
						aliasesOutput = aliasesOutput[:size - 2]

						await channel.send(aliasesOutput)
						print("[COMMAND] Sent list of aliases to {" + user.name + "}")
					else:
						await channel.send("@" + user.name + ": Input {" + words[1].lower() + "} has no aliases.")
				else:
					await channel.send("@" + user.name + ": Input name must be given as argument!")
			else:
				inputName = message.split(" ", 1)[0] 
				data = Inputs.get_data_for_input(game, inputName)

				if data is not None:
					duration = Inputs.defaultDuration

					waitForWinActive = settings["waitForWinActive"]
					playSounds = settings["playSounds"]
					showStats = settings["showStats"]
					hasGivenDuration = False
					hasExitCond = False
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

					# Update stats
					global totalInputs
					totalInputs += 1

					if inputName in inputUsage:
						inputUsage[inputName] = inputUsage[inputName] + 1
					else:
						inputUsage[inputName] = 1

					if hasGivenDuration:
						print("[INPUT] Input {" + inputName + "} triggered with duration of {" + str(duration) + "} by {" + user.name + "}")
					else:
						print("[INPUT] Input {" + inputName + "} triggered by {" + user.name + "}")

					if playSounds:
						_thread.start_new_thread(try_play_sound, [game, settings["playSoundsChanceOverride"]])

def get_input_list():
	allInputs = ""
	for input in Inputs.get_all_inputs_for_game(game):
		allInputs += input["input"] + ", "

	size = len(allInputs)
	allInputs = allInputs[:size - 2]
	return allInputs

def on_quit(signal, frame):
	global isActive
	if isActive == True:
		print("\n--------------------------------------------------\n")
		print("Terminating from input...")

		if totalInputs > 0:
			Inputs.release_all_keys()
	
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