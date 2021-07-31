from typing import List
import json

inputsForPlatforms = {
	"Dolphin": [
		"Space", "RControl", "RCtrl", "Z", "X", "C", "LControl", "LCtrl", "I", "K", "J", "L", "W", "S", "A", "D", "Up", "Down", "Left", "Right", "Q", "E"
		]
}

platformsWithMultipleGames = {
	"Dolphin": [
		"The Legend of Zelda: Twilight Princess", "The Legend of Zelda: The Wind Waker"
		]
}

class InputData(object):
	def __init__(self, gameOrPlatform: str, input: dict[str, str], duration: float):
		self.gameOrPlatform = gameOrPlatform
		self.input = input
		self.duration = duration

def loadInputData():
	file = open("inputs.json")

	inputData = json.load(file)

	file.close()

	return inputData

def generateInputData():
	inputData = [
		InputData(
			gameOrPlatform="Dolphin",
			input={
				"input": "Right",
				"output": "Right"
			},
			duration=1
		),
		InputData(
			gameOrPlatform="Dolphin",
			input={
				"input": "Longright",
				"output": "Right"
			},
			duration=2
		),
		InputData(
			gameOrPlatform="Hollow Knight",
			input={
				"input": "Right",
				"output": "D"
			},
			duration=1
		),
		InputData(
			gameOrPlatform="Hollow Knight",
			input={
				"input": "Longright",
				"output": "D"
			},
			duration=2
		)
	]

	jsonObject = []
	for input in inputData:
		jsonObject.append(json.dumps(input.__dict__))

	print(jsonObject)

def getDataForInput(gameOrPlatform, input):
	for data in loadInputData():
		if (data.get("gameOrPlatform") == getGameOrPlatform(gameOrPlatform)):
			if (data.get("input").get("input") == input):
				return data
	return None

def getGameOrPlatform(wantedGame):
	for platform, games in platformsWithMultipleGames.items():
		for game in games:
			if (game == wantedGame):
				return platform
	return wantedGame