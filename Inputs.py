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

def getValidInput(game, input):
	for storedInput in getInputsForGame(game):
		if storedInput.lower() == input:
			return storedInput
	return None

def getInputsForGame(game):
	gameOrPlatform = getGameOrPlatform(game)

	if gameOrPlatform in inputsForPlatforms.keys():
		return inputsForPlatforms[gameOrPlatform]

def getGameOrPlatform(wantedGame):
	for platform, games in platformsWithMultipleGames.items():
		for game in games:
			if (game == wantedGame):
				return platform
	return wantedGame