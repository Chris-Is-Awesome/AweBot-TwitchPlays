import json
import os
import sys
from dotenv import load_dotenv
from twitchio.ext import commands 
from TwitchPlays import *

# Set variables
load_dotenv()
oauth = os.environ.get("PASS")
client = os.environ.get("CLIENT")
hasJoined = False

bot = commands.Bot(
	token=oauth,
	client_id=client,
	nick="The_Goat_Howard",
	prefix="NOPREFIX",
	initial_channels=["ChrisIsAwesome"]
)

@bot.event()
async def event_join(channel, user):
	global hasJoined

	if hasJoined == False:
		print("AweBot:TwitchPlays has joined " + "ChrisIsAwesome" + "'s channel!\n\n--------------------------------------------------\n")
		await channel.send("Baaaa! Twitch Plays is active! Type inputs in chat to see them play out in game! TODO: Add link to info")
		hasJoined = True

@bot.event()
async def event_message(messageData):
	if messageData.author is not None:
		await on_message_sent(messageData)

def loadSettings():
	file = open("settings.json")
	settings = json.load(file)
	file.close()

	print("Setup has loaded settings:\n{")
	for setting in settings:
		print("     " + setting + ": " + str(settings[setting]))
	print("}\n\n--------------------------------------------------\n")

	apply_settings(settings)

loadSettings()
bot.run()