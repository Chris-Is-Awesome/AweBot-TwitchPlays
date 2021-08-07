import json
import time

platformsWithMultipleGames = {
	"Dolphin": [
		"The Legend of Zelda: Twilight Princess", "The Legend of Zelda: The Wind Waker"
		]
}

# Key: Platform
# Value: Input
tempDisabledInputs = {}

def getDataForInput(wantedPlatform, wantedInput):
	for data in loadInputData():
		platform = data["platform"]
		if platform == wantedPlatform or platform == getGameOrPlatform(wantedPlatform):
			for input in data["inputs"]:
				if input["input"] == wantedInput:
					disabledInputsForPlatform = tempDisabledInputs.get(platform)
					if disabledInputsForPlatform != None:
						for disabledInput in disabledInputsForPlatform:
							if disabledInput == wantedInput:
								return None
					return input
	return None


def getAllInputsForGame(wantedPlatform):
	for data in loadInputData():
		platform = data["platform"]
		if platform == wantedPlatform or platform == getGameOrPlatform(wantedPlatform):
			return data["inputs"]

	return None

def releaseInputAfterDelay(ahk, input, delay):
	time.sleep(delay)
	ahk.key_release(input)

def loadInputData():
	file = open("inputs.json")

	inputData = json.load(file)

	file.close()

	return inputData

def getGameOrPlatform(wantedGame):
	for platform, games in platformsWithMultipleGames.items():
		for game in games:
			if (game == wantedGame):
				return platform
	return wantedGame