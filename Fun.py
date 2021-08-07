import os
import random
from ahk import AHK

ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')

def loadAllSounds(game):
	path = os.getcwd() + "\\sounds\\" + game
	if os.path.exists(path):
		allSoundFiles = os.listdir(path)
		playSound(path, allSoundFiles)

def tryPlaySound(game):
	loadAllSounds(game)

def playSound(path, allSoundFiles):
	randChance = random.randint(0, 100)
	if randChance <= 5:
		randSound = random.randint(0, len(allSoundFiles) - 1)
		file = path + "/" + allSoundFiles[randSound]
		ahk.set_volume(50)
		ahk.sound_play(file)
		print("[SOUND] Played sound: '" + allSoundFiles[randSound] + "' with random chance of: " + str(randChance))