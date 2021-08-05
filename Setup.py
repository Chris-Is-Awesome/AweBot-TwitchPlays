import os
import socket
import time
import _thread
import threading
from Inputs import *
from ahk import AHK
from dotenv import load_dotenv
from Fun import *

load_dotenv()
ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')
SERVER = "irc.twitch.tv"
PORT = 6667
PASS = os.environ.get("PASS")
BOT = "The_Goat_Howard"
CHANNEL = "chrisisawesome"
OWNER = "ChrisIsAwesome"
message = ""
user = ""
irc = socket.socket()

def setup():
	file = open("settings.json")
	loadedData = json.load(file)
	file.close()
	print("Setup has loaded settings:\n{")
	for setting in loadedData:
		print("     " + setting + ": " + str(loadedData[setting]))
	print("}\n")
	return loadedData

settings = setup()

def update():

	global message

	while True:

		if len(message) != 0:
			if message != "twitch.tv/tags":
				game = settings["game"]
				data = getDataForInput(game, message.lower())
				if data is not None:
					waitForWinActive = settings["waitForWinActive"]
					playSounds = settings["playSounds"]
					input = data["input"]
					outputs = data["outputs"]
					heldInputs = {}

					print("Chat triggered " + input + "!")

					if playSounds:
						_thread.start_new_thread(tryPlaySound, (game,))

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

					for heldInput in heldInputs:
						duration = heldInputs[heldInput]
						if type(duration) == int or type(duration) == float:
							_thread.start_new_thread(releaseInputAfterDelay, (ahk, heldInput, duration))
				message = ""

def connect():
	irc.connect((SERVER, PORT))
	irc.send((	"PASS " + PASS + "\n" + "NICK " + BOT + "\n" + "JOIN #" + CHANNEL + "\n").encode())

def twitch():

	global user
	global message

	def joinchat():
		Loading = True
		while Loading:
			readbuffer_join = irc.recv(1024)
			readbuffer_join = readbuffer_join.decode()
			for line in readbuffer_join.split("\n")[0:-1]:
				Loading = loadingComplete(line)

	def loadingComplete(line):
		if("End of /NAMES list" in line):
			print("AweBot:TwitchPlays has joined " + CHANNEL + "'s channel!\n\n--------------------------------------------------\n")
			sendMessage(irc, "Baaaa! Twitch Plays is active! Type inputs in chat to see them play out in game! TODO: Add link to info")
			return False
		else:
			return True

	def sendMessage(irc, message):
		messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
		irc.send((messageTemp + "\n").encode())

	def getUser(line):
		colons = line.count(":")
		colonless = colons-1
		separate = line.split(":", colons)
		user = separate[colonless].split("!", 1)[0]
		return user

	def getMessage(line):
		try:
			colons = line.count(":")
			message = (line.split(":", colons))[colons]
		except:
			message = ""
		return message

	def console(line):
		if "PRIVMSG" in line:
			return False
		else:
			return True

	joinchat()
	irc.send("CAP REQ :twitch.tv/tags\r\n".encode())
	while True:
		try:
			readbuffer = irc.recv(1024).decode()
		except:
			readbuffer = ""
		for line in readbuffer.split("\r\n"):
			if line == "":
				continue
			if "PING :tmi.twitch.tv" in line:
				print(line)
				msgg = "PONG :tmi.twitch.tv\r\n".encode()
				irc.send(msgg)
				print(msgg)
				continue
			else:
				try:
					user = getUser(line)
					message = getMessage(line)
				except Exception:
					pass

def main():
	if __name__ =='__main__':
		connect()

		t1 = threading.Thread(target = twitch)
		t1.start()
		t2 = threading.Thread(target = update)
		t2. start()
main()