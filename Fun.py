import os
import random
from ahk import AHK

ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')

def load_all_sounds(game, chanceOverride):
	path = os.getcwd() + "\\sounds\\" + game
	if os.path.exists(path):
		allSoundFiles = os.listdir(path)
		play_sound(path, allSoundFiles, chanceOverride)

def try_play_sound(game, chanceOverride):
	load_all_sounds(game, chanceOverride)

def play_sound(path, allSoundFiles, chanceOverride = 5):
	randChance = random.randint(0, 100)
	if randChance <= chanceOverride:
		randSound = random.randint(0, len(allSoundFiles) - 1)
		file = path + "/" + allSoundFiles[randSound]
		ahk.set_volume(50)
		ahk.sound_play(file)
		print("[SOUND] Played sound: {" + allSoundFiles[randSound] + "} with random chance of: {" + str(randChance) + "}")