import socket
import threading
from Inputs import *
from ahk import AHK
from dotenv import load_dotenv
load_dotenv()
import os
import time
import _thread

#Download Autohotkey at https://www.autohotkey.com/ and provide the address to
#AutoHotkey.exe below!
ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')

SERVER = "irc.twitch.tv"
PORT = 6667

#Your OAUTH Code Here https://twitchapps.com/tmi/
PASS = os.environ.get("PASS")

#What you'd like to name your bot
BOT = "The_Goat_Howard"

#The channel you want to monitor
CHANNEL = "chrisisawesome"

#Your account
OWNER = "ChrisIsAwesome"

message = ""
user = ""

irc = socket.socket()

irc.connect((SERVER, PORT))
irc.send((	"PASS " + PASS + "\n" +
			"NICK " + BOT + "\n" +
			"JOIN #" + CHANNEL + "\n").encode())

def gamecontrol():

	global message

	while True:

		if len(message) != 0:
			if message != "twitch.tv/tags":
				data = getDataForInput("The Legend of Zelda: Twilight Princess", message.lower())
				if data is not None:
					input = data["input"]
					outputs = data["outputs"]
					heldInputs = {}

					print("Chat triggered " + input + "!")

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

def twitch():

	global user
	global message

	def joinchat():
		Loading = True
		while Loading:
			readbuffer_join = irc.recv(1024)
			readbuffer_join = readbuffer_join.decode()
			print(readbuffer_join)
			for line in readbuffer_join.split("\n")[0:-1]:
				print(line)
				Loading = loadingComplete(line)

	def loadingComplete(line):
		if("End of /NAMES list" in line):
			print("TwitchBot has joined " + CHANNEL + "'s Channel!")
			sendMessage(irc, "Hello World!")
			return False
		else:
			return True

	def sendMessage(irc, message):
		messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
		irc.send((messageTemp + "\n").encode())

	def getUser(line):
		#global user
		colons = line.count(":")
		colonless = colons-1
		separate = line.split(":", colons)
		user = separate[colonless].split("!", 1)[0]
		return user

	def getMessage(line):
		#global message
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
					#print(user + " : " + message)
				except Exception:
					pass

def main():
	if __name__ =='__main__':
		t1 = threading.Thread(target = twitch)
		t1.start()
		t2 = threading.Thread(target = gamecontrol)
		t2. start()
main()