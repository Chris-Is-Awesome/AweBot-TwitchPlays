import asyncio
import Inputs
import multiprocessing
from ahk import AHK
from ahk.window import Window
from Fun import try_play_sound
#from multiprocessing.pool import ThreadPool as Pool
from signal import signal, SIGINT

# Set variables
ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')
channel = None
isActive = True;

heldKeys = []

# Stats
totalInputs = 0
inputUsage = {}

#poolSize = 5 # Max # of processes (lower = better CPU usage)
#pool = Pool(poolSize)
#pool = multiprocessing.Pool()

processes = []

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
		elif message == "!fornerds":
			await channel.send("@" + user.name + ": I am fueled by JS and Python as I was made in 2 parts. Part 1 is for everything that is not Twitch Plays related, such as fun commands like !whoop and !bff. Part 1 was written in JS using tmi-js and is  hosted on Heroku. Source: https://github.com/Chris-Is-Awesome/AweBot-Twitch")
			await channel.send("@" + user.name + ": Part 2 is the Twitch Plays part, which was written in Python using twitchio. Twitch Plays was coded separately as it needs to run locally, while part 1 of bot runs on a server. Source: https://github.com/Chris-Is-Awesome/AweBot-TwitchPlays")
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
				# Handle input
				inputName = message.split(" ", 1)[0].lower()
				data = Inputs.get_data_for_input(game, inputName)

				if data is not None:
					requiredWindow = None
					waitForWinActive = settings["waitForWinActive"]

					if waitForWinActive:
						config = Inputs.load_input_data(game)

						for window in ahk.windows():
							if str(window.title).startswith("b'" + config["program"]) and not str(window.title).endswith("MusicBee'"):
								requiredWindow = window
								requiredWindow.activate()
								break

					if not waitForWinActive or requiredWindow is not None:
						duration = Inputs.defaultDuration

						waitForWinActive = settings["waitForWinActive"]
						playSounds = settings["playSounds"]
						showStats = settings["showStats"]
						hasGivenDuration = False
						outputs = data["outputs"]

						for output in outputs:
							key = output["output"]
							forcedDuration = output.get("duration")

							if forcedDuration is not None:
								duration = forcedDuration
							else:
								for word in message.split(" "):
									try:
										duration = float(word)
										hasGivenDuration = True
										break
									except:
										continue

							#_thread.start_new_thread(Inputs.handle_key_event, [key, duration])
							#pool.apply_async(Inputs.handle_key_event, [key, duration])
							#pool = Process(target=Inputs.handle_key_event, [key, duration])
							#pool.start()
							#func = Inputs.handle_key_event, [key, duration]
							#test.append(func)
							#runFuncsInParallel(Inputs.handle_key_event, [key, duration])
							#pool.map(Inputs.handle_key_event, [key, duration])
							asyncio.get_event_loop().run_in_executor(None, Inputs.handle_key_event(key, duration))
							#print("Triggered key event for " + key + " with duration of " + str(duration))

							if duration > 0:
								if key not in heldKeys:
									heldKeys.append(key)

							"""
							for heldKey in heldKeys:
								exitCond = heldKeys[heldKey].get("exitCond")
								if exitCond is None:
									Inputs.release_key(heldKey, defaultDuration)
								else:
									releaseDelay = heldKeys[heldKey].get("releaseDelay")
									print("Releasing key " + heldKey + " after " + str(releaseDelay))
									Inputs.release_key(heldKey, releaseDelay)
									heldKeys.pop(heldKey)
									break
						"""

						inputName = data["input"]

						#runFuncsInParallel(test)

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

						#if playSounds:
							#_thread.start_new_thread(try_play_sound, [game, settings["playSoundsChanceOverride"]])

def runFuncsInParallel(*funcs):
	for func in funcs:
		process = Process(target=func)
		process.start()
		processes.append(process)
	for process in processes:
		process.join()

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

		for key in heldKeys:
			Inputs.release_key(key)
			heldKeys.remove(key)
	
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