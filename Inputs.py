import json

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
		if platform == getGameOrPlatform(wantedPlatform):
			for input in data["inputs"]:
				if input["input"] == wantedInput:
					disabledInputsForPlatform = tempDisabledInputs.get(platform)
					if disabledInputsForPlatform != None:
						for disabledInput in disabledInputsForPlatform:
							if disabledInput == wantedInput:
								return None
					return input
	return None

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