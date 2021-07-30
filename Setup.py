import socket
import threading
from Inputs import *
from ahk import AHK
from dotenv import load_dotenv
load_dotenv()
import os

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
				input = getValidInput("The Legend of Zelda: Twilight Princess", message.lower())
				if input is not None:
					ahk.key_press(input)
					print("Chat pressed " + input + "!")
				message = ""

				# Goals with v2:

					# 1. Better way of storing inputs that allow for more dynamic input handling (store inputs in json & learn how to deserialize it)
					# (list<string>) games/platforms
						# (dictionary<string, string>) dictionary containing user-friendly inputs and raw inputs
							# (string) user-friendly input (input user must type/outputted to console) (ex. longright)
							# (string) raw input (real AHK input value) (ex. right)
						# (float) duration

					# 2. PLS FIND A WAY TO NOT CALL GAMECONTROL() EVERY FRAME D:
						# Look into TMI with python? idk if it works with this though...

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