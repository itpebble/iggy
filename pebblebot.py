from dis import disco
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import sys
import re
import random
import secrets
import requests
from tiktokvoice import tts
from gtts import gTTS
from fileHandling import iggyFile
from saucenao_api import SauceNao

# get into the PI (personal notes, ignore :v):
# ssh -i /Users/pebble/key pebble@192.168.1.206
# tmux, ctrl b + d

# test or live token?
tokenType = "live"

# / or \ for directory navigation?
slash = "/"

# IDEAS
#
# NEW COMMANDS: 
# - add message to list of quotes, say random quote 
# - some kinda chastity timer (self/public/specific people) (keymashes add hours/days)
# - (cobalt suggestion) /squish, only usable on pooltoys, makes pooltoy do an involuntary squeak
# - user info command that shows all user variables
#
# TWEAKS:
# - make third person and yinglet thingy work with pluralkit tags
# - bug - if a command takes too long, it'll send an error and only then finish
# - something to encourage not messing up with ying and tp
# - gag and twin together WILL cause issues
#
# HARD TO DO:
# - gag: work with links (maybe use re.split?)
# - replace regex with something less taxing
#
# pk tp idea
# pktp add "stuff before message" "stuff after message" (maybe as single entry?)
# keep items in a single iggyData entry, separated by some character 
# pktp list (lists all entries 
# pktp remove (entry number or stuff before and after message) 
# pktp reset (deleted everything)
# only allow basic characters, don't allow / or |

# Initializing
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='>', intents=intents)
client = discord.Client(intents=intents)

# define things
absolute_path = os.path.dirname(__file__)
undefinedError = "Something borked."
global lastMessage
lastMessage = "a"

# fetch bot token
def getToken():
	with open(os.path.join(sys.path[0], f'tokens{slash}{tokenType}.txt')) as f:
		token = f.read()
	return token

# fetch saucenao token
def getSauceToken():
	with open(os.path.join(sys.path[0], f'tokens{slash}saucenao.txt')) as f:
		token = f.read()
	return token

#generate list of keymash detection words to ignore
def generateReList():
	with open(os.path.join(sys.path[0], 'relist.txt')) as f:
		reList = f.read()
	return reList

#sorting algorithm for score
def num_sort(test_string):
	x = re.findall(r'\d+$', test_string)
	return list(map(int, x))[0]

#define a webhook
async def getWebhook(message):
	if hasattr(message.channel, "parent") == False: # if message was sent in a normal channel
		# START CODE FOR GETTING WEBHOOK
		channelWebhooks = await message.channel.webhooks() # get all the webhooks in the channel
		def findWebhook(channelWebhooks): # define function that finds the webhook
			for webhook in channelWebhooks:
				if webhook.name == "Iggy Webhook" and webhook.user.id == bot.user.id : # if it's iggy's webhook and created by self (for test bot vs iggy)
					return webhook # return the webhook
		if findWebhook(channelWebhooks) == None: # if iggy's webhook doesn't exist
			webhook = await message.channel.create_webhook(name="Iggy Webhook") # make a new webhook
		else: # if iggy's webhook exists
			webhook = findWebhook(channelWebhooks) # get the existing webhook
		# END CODE FOR GETTING WEBHOOK
	if hasattr(message.channel, "parent") == True: # if message was sent in a thread
		# START CODE FOR GETTING WEBHOOK
		channelWebhooks = await message.channel.parent.webhooks() # get all the webhooks in the channel
		def findWebhook(channelWebhooks): # define function that finds the webhook
			for webhook in channelWebhooks:
				if webhook.name == "Iggy Webhook" and webhook.user.id == bot.user.id : # if it's iggy's webhook and created by self (for test bot vs iggy)
					return webhook # return the webhook
		if findWebhook(channelWebhooks) == None: # if iggy's webhook doesn't exist
			webhook = await message.channel.parent.create_webhook(name="Iggy Webhook") # make a new webhook
		else: # if iggy's webhook exists
			webhook = findWebhook(channelWebhooks) # get the existing webhook
		# END CODE FOR GETTING WEBHOOK
	return webhook

# /info buttons
class simpleView(discord.ui.View):
	async def disable_all_items(self): # code for disabling buttons
		for item in self.children:
			item.disabled = True
		await self.message.edit(view=self)

	async def on_timeout(self): #disable buttons on timeout
		await self.disable_all_items()

	# text correction section
	@discord.ui.button(label="Text Correction", style=discord.ButtonStyle.grey)
	async def correctbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed = discord.Embed(title="Text Correction", colour=discord.Colour(0xffd912), description="### /tp\nIggy will remind you when you forget to talk in third person.\n### /ying\nIggy will remind you to talk like a yinglet.")
		embed.set_author(name="Iggy", icon_url="https://nexii.feen.us/yjf8a3j1vd.jpg")
		embed.set_footer(text="contact @ebbl for help")
		try:
			await interaction.response.edit_message(embed=embed, view=self)
		except:
			pass

	# text and speech section
	@discord.ui.button(label="Text and Speech", style=discord.ButtonStyle.grey)
	async def textbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed = discord.Embed(title="Text and Speech", colour=discord.Colour(0xffd912), description="### /join\nAdds Iggy to the voice channel you are in.\n### /leave\nRemoves Iggy from voice channel.\n### /say (message)\nUse text to speech. You and Iggy must be in a voice channel to use this.\n### /saytt (voice) (message)\nUse text to speech with a TikTok voice. You and Iggy must be in a voice channel to use this.\n### /repeat\nRepeat the last text to speech message.\n### /save (voice) (message)\nGenerate a text to speech file with a selected voice.\n### /relay (message)\nSend a message as iggy.\n### /dm (who) (message)\nDM a server user as iggy.")
		embed.set_author(name="Iggy", icon_url="https://nexii.feen.us/yjf8a3j1vd.jpg")
		embed.set_footer(text="contact @ebbl for help")
		try:
			await interaction.response.edit_message(embed=embed, view=self)
		except:
			pass

	# scores section
	@discord.ui.button(label="Scores", style=discord.ButtonStyle.grey)
	async def scorebutton(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed = discord.Embed(title="Scores", colour=discord.Colour(0xffd912), description="### /score\nShow keymash scoreboard.\n### /3score\nShow :3 scoreboard.")
		embed.set_author(name="Iggy", icon_url="https://nexii.feen.us/yjf8a3j1vd.jpg")
		embed.set_footer(text="contact @ebbl for help")
		try:
			await interaction.response.edit_message(embed=embed, view=self)
		except:
			pass

	# kink sectiion
	@discord.ui.button(label="Kink", style=discord.ButtonStyle.grey)
	async def kinkbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed = discord.Embed(title="Kink", colour=discord.Colour(0xffd912), description="### /imp (who) (message)\nImpersonate a user.\n### /gag (type) (owner)\nApply a gag to yourself. This will edit your messages to make them sound as if you were gagged. You can (but don't have to) also define an owner, who will then be the only person able to remove the gag.\n### /ungag (who)\nRemove a gag. Leave \"(who)\" blank to ungag yourself, or select someone else to ungag, if you are set as their owner.\n### /bully (who) (new nickname)\nChange a user's nickname.\n### /secretbully (who) (new nickname)\nChange a user's nickname without sending a message.\n### /twin (on/off) (who)\nTwin a server member. This will make your messages appear as if sent by the twinned user (who).")
		embed.set_author(name="Iggy", icon_url="https://nexii.feen.us/yjf8a3j1vd.jpg")
		embed.set_footer(text="contact @ebbl for help")
		try:
			await interaction.response.edit_message(embed=embed, view=self)
		except:
			pass

	# misc section
	@discord.ui.button(label="Misc", style=discord.ButtonStyle.grey)
	async def miscbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed = discord.Embed(title="Misc", colour=discord.Colour(0xffd912), description="### /peet\nSends a random paw picture.\n### /dronename (length)\nGenerate a drone name. \"(Length)\" determines how long it should be (multiplied by 2). For example, /dronename 2 will generate a dronename that is 4 characters long.\n### /boop (who)\nBoop someone.\n### /source (link)\nGet source for an image link. Also usable by right clicking on a message > Apps > Get Image Source.")
		embed.set_author(name="Iggy", icon_url="https://nexii.feen.us/yjf8a3j1vd.jpg")
		embed.set_footer(text="contact @ebbl for help")
		try:
			await interaction.response.edit_message(embed=embed, view=self)
		except:
			pass

# set bot status, run bot
@bot.event
async def on_ready():
	game = discord.Game("/info")
	await bot.change_presence(status=discord.Status.online, activity=game)
	try:
		synced = await bot.tree.sync()
		print(f"Synced {len(synced)} command(s)")
	except Exception as e:
		print(e)

# delete default help command
bot.remove_command('help')

# /terminate, kill Iggy
@bot.tree.command(name="terminate", description="Kill Iggy.")
async def _terminate(interaction: discord.Interaction):
	if (interaction.user.id == 241168125704273922 or interaction.user.id == 481950002235572229 or interaction.user.id == 446104935931576321):
		await interaction.response.send_message("https://media.tenor.com/FZfzOwrrJWsAAAAC/janet-the-good-place.gif")
		sys.exit()
	else:
		await interaction.response.send_message("You're not allowed.")

# /info
@bot.tree.command(name="info", description="List all of Iggy's commands.")
async def _info(interaction: discord.Interaction):
	view = simpleView(timeout=120) # set timeout for buttons
	embed = discord.Embed(title="Select a section.", colour=discord.Colour(0xffd912), description="### Text Correction\nReminders for when you forget to talk how you're supposed to.\n### Text and Speech\nSending messages and text to speech.\n### Scores\nView the scores Iggy keeps track of.\n### Kink\nBot assisted bullying. Make sure you have consent.\n### Misc\nRandom fun commands.\n")
	embed.set_author(name="Iggy", icon_url="https://nexii.feen.us/yjf8a3j1vd.jpg")
	embed.set_footer(text="contact @ebbl for help")
	message = await interaction.response.send_message(embed=embed, view=view, ephemeral=True) # send the message
	view.message = message # i honestly don't know
	await view.wait()
	await view.disable_all_items() # disable buttons after timer
	pass

@_info.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		await ctx.send(undefinedError)
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

#-----------------------------------------
#
#         Text Correction Section
#
#-----------------------------------------

@app_commands.describe(option="This is a description of what the option means")
@app_commands.choices(option=[
        app_commands.Choice(name="Option 1", value="1"),
        app_commands.Choice(name="Option 2", value="2")
    ])
async def test(interaction: discord.Interaction, option: app_commands.Choice[str]):
    pass

# /tp, toggle third person detection
@bot.tree.command(name="tp", description="Iggy will remind you when you forget to talk in third person.")
@app_commands.describe(toggle = "Do you want to enable or disable third person detection?")
@app_commands.choices(toggle = [
		app_commands.Choice(name="On", value="on"),
		app_commands.Choice(name="Off", value="off")
	])
async def _tp(interaction: discord.Interaction, toggle: app_commands.Choice[str]):
	if toggle.value == "on":
		iggyData = iggyFile.read(interaction.user, interaction.guild)
		if iggyData.thirdPerson == "on":
			await interaction.response.send_message(f"You already have third person reminders enabled, use **/tpoff** to turn them off.")
		elif iggyData.thirdPerson == "off":
			iggyData.thirdPerson = "on"
			iggyFile.write(iggyData, interaction.user, interaction.guild)
			await interaction.response.send_message(f"Iggy will now remind you when you forget to talk in third person :3")
	elif toggle.value == "off":
		iggyData = iggyFile.read(interaction.user, interaction.guild)
		if iggyData.thirdPerson == "off":
			await interaction.response.send_message(f"You don't have third person reminders enabled, use **/tpon** to turn them on.")
		elif iggyData.thirdPerson == "on":
			iggyData.thirdPerson = "off"
			iggyFile.write(iggyData, interaction.user, interaction.guild)
			await interaction.response.send_message(f"Iggy will no longer remind you to talk in third person.")

# /ying, toggle yingspeak detection
@bot.tree.command(name="ying", description="Iggy will remind you to talk like a yinglet.")
@app_commands.describe(toggle = "Do you want to enable or disable yingspeak detection?")
@app_commands.choices(toggle = [
		app_commands.Choice(name="On", value="on"),
		app_commands.Choice(name="Off", value="off")
	])
async def _ying(interaction: discord.Interaction, toggle: app_commands.Choice[str]):
	if toggle.value == "on":
		iggyData = iggyFile.read(interaction.user, interaction.guild)
		if iggyData.yinglet == "on":
			await interaction.response.send_message(f"You already have yingspeech reminders enabled, use **/yingoff** to turn them off.")
		elif iggyData.yinglet == "off":
			iggyData.yinglet = "on"
			iggyFile.write(iggyData, interaction.user, interaction.guild)
			await interaction.response.send_message(f"Iggy will now remind you when you forget to talk like a yinglet :3")
	elif toggle.value == "off":
		iggyData = iggyFile.read(interaction.user, interaction.guild)
		if iggyData.yinglet == "off":
			await interaction.response.send_message(f"You don't have yingspeech reminders enabled, use **/yingon** to turn them on")
		elif iggyData.yinglet == "on":
			iggyData.yinglet = "off"
			iggyFile.write(iggyData, interaction.user, interaction.guild)
			await interaction.response.send_message(f"Iggy will no longer remind you to talk like a yinglet.")

# twinning replacement code
async def twinReplace(msg, message, twin):
	# replace message
	twinnedUser = message.channel.guild.get_member(int(twin)) # fetch the user they are twinning
	if message.attachments != []: # make a files variable if there are files, saves space to put it here
		files=[await f.to_file() for f in message.attachments]
	webhook = await getWebhook(message) # get the webhook
	if message.reference is not None: # if it is replying to someone
		inreplyto = await message.channel.fetch_message(message.reference.message_id) # get who we're replying to
		replyembed = discord.Embed(description=f"**[Reply to:]({inreplyto.jump_url})** {inreplyto.content[0:98]}...") # define reply embed
		replyembed.set_author(name=f"{inreplyto.author.display_name} ↩️", icon_url=inreplyto.author.display_avatar.url) # set reply embed author
		if hasattr(message.channel, "parent") == False:	# if it is not in a thread
			if message.attachments != []: # if has attachments
				await webhook.send(msg, files=files, username=twinnedUser.display_name, embed=replyembed, avatar_url=twinnedUser.display_avatar.url)
			else: # if no attachments
				await webhook.send(msg, username=twinnedUser.display_name, embed=replyembed, avatar_url=twinnedUser.display_avatar.url)
		elif hasattr(message.channel, "parent") == True: #if it is in a thread
			if message.attachments != []: # if has attachments
				await webhook.send(msg, files=files, username=twinnedUser.display_name, thread=message.channel, embed=replyembed, avatar_url=twinnedUser.display_avatar.url)
			else: # if no attachments
				await webhook.send(msg, username=twinnedUser.display_name, thread=message.channel, embed=replyembed, avatar_url=twinnedUser.display_avatar.url)
	elif message.flags.has_thread == False: # if it is not replying to someone
		if hasattr(message.channel, "parent") == False:
			if message.attachments != []: # if has attachments
				await webhook.send(msg, files=files, username=twinnedUser.display_name, avatar_url=twinnedUser.display_avatar.url)
			else: # if no attachments
				await webhook.send(msg, username=twinnedUser.display_name, avatar_url=twinnedUser.display_avatar.url)
		elif hasattr(message.channel, "parent") == True:
			if message.attachments != []: # if has attachments
				await webhook.send(msg, files=files, username=twinnedUser.display_name, thread=message.channel, avatar_url=twinnedUser.display_avatar.url)
			else: # if no attachments
				await webhook.send(msg, username=twinnedUser.display_name, thread=message.channel, avatar_url=twinnedUser.display_avatar.url)
	await message.delete()

# /twin, twin a server member
@bot.tree.command(name="twin", description="Twin a server member. This will make your messages appear as if sent by the twinned user.")
@app_commands.describe(toggle = "Do you want to enable or disable twinning?")
@app_commands.choices(toggle = [
		app_commands.Choice(name="On", value="on"),
		app_commands.Choice(name="Off", value="off")
	]) # options!
@app_commands.describe(who = "Who do you want to twin? (only use this if turning it on)")
async def _twin(interaction: discord.Interaction, toggle: app_commands.Choice[str], who: discord.Member = None):
	if toggle.value == "on": # if the option selected is to turn it on
		if who != None: # make sure the user selected who they want to twin
			iggyData = iggyFile.read(interaction.user, interaction.guild) # get iggy data
			if iggyData.twin == str(who.id): # check if user is already twinning the user
				await interaction.response.send_message(f"You are already twinning this user. Use \"/twin off\" to turn it off.") # send message if they are
			else: # if a user is NOT already twinning the user
				iggyData.twin = str(who.id) # set twin value to desired user id
				iggyFile.write(iggyData, interaction.user, interaction.guild) # write twin id value to file
				await interaction.response.send_message(f"You are now twinning {who.display_name} :3") # send message
		else: # if the user didn't select who they want to twin
			await interaction.response.send_message(f"You need to specify who you want to twin") # send message
	elif toggle.value == "off": # if the option selected is to turn it off
		iggyData = iggyFile.read(interaction.user, interaction.guild) # get iggy data
		if iggyData.twin == str(interaction.user.id): # check if user is twinning anyone
			await interaction.response.send_message(f"You are not twinning anyone.") # if not, send message
		else: # if user is twinning someone
			twinnedUser = interaction.guild.get_member(int(iggyData.twin)) # fetch the user they are twinning
			iggyData.twin = str(interaction.user.id) # set twin parameter to user's own id to disable it
			iggyFile.write(iggyData, interaction.user, interaction.guild) # write data to file
			await interaction.response.send_message(f"You are no longer twinning {twinnedUser.display_name}.") # send message

#-----------------------------------------
#
#         Text and Speech Section
#
#-----------------------------------------

# /join, join voice channel of user who runs command
@bot.tree.command(name="join", description="Adds Iggy to the voice channel you are in.")
async def _join(interaction: discord.Interaction):
	global vc
	voice_user = interaction.user.voice
	if voice_user != None:
		vc = await voice_user.channel.connect(timeout=60.0, reconnect=True, self_deaf=False, self_mute=False)
		await interaction.response.send_message("Done!", ephemeral=True)
	else:
		await interaction.response.send_message("You need to be in a voice channel to do this.", ephemeral=True)
		pass

@_join.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		await ctx.send("Iggy is already in a voice channel. If you want it to join a different one use **/leave** first.")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /leave, leave voice channel
@bot.tree.command(name="leave", description="Removes Iggy from voice channel.")
async def _leave(interaction: discord.Interaction):
	await interaction.guild.voice_client.disconnect()
	await interaction.response.send_message("Done!", ephemeral=True)
	pass

@_leave.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		await ctx.send("Iggy is not in a voice channel.")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /say, text to speech in voice channel
@bot.tree.command(name="say", description="Use text to speech. You and Iggy must be in a voice channel to use this.")
@app_commands.describe(message = "message to say")
async def _say(interaction: discord.Interaction, message: str):
	voice_user = interaction.user.voice # define the voice user aka who's in a voice channel
	if voice_user != None: # if a user is in a voice channel
		await interaction.response.send_message("Working on it!", ephemeral=True) # reply, this needs to be done here bc the timeout of 3 seconds is often not enough
		global lastMessage # set the last message as a global thing, this is lazy ignore it
		lastMessage = message # set the last message variable to be used by the /repeat command
		gttsthing = gTTS(message) # use google text to speech
		gttsthing.save('speech.mp3') # save google text to speech message as file
		vc.play(discord.FFmpegPCMAudio("speech.mp3")) # play message in voice channel
		msg = await interaction.original_response() # get original response
		await msg.edit(content="Done!") # edit original response
	else: 
		await interaction.response.send_message("You need to be in a voice channel to do this.", ephemeral=True)

@_say.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("What do you want Iggy to say?")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send("Something borked, make sure Iggy is in a voice channel (use **join**)")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /saytt, text to speech in voice channel but with voice selection
@bot.tree.command(name="saytt", description="Use text to speech with a TikTok voice. You and Iggy must be in a voice channel to use this.")
@app_commands.describe(voice = "voice to use")
@app_commands.describe(message = "message to say")
@app_commands.choices(voice=[ app_commands.Choice(name="English AU - Female", value="en_au_001"), app_commands.Choice(name="English AU - Male", value="en_au_002"), app_commands.Choice(name="English UK - Male 1", value="en_uk_001"), app_commands.Choice(name="English UK - Male 2", value="en_uk_003"), app_commands.Choice(name="English US - Female (Int. 1)", value="en_us_001"), app_commands.Choice(name="English US - Female (Int. 2)", value="en_us_002"), app_commands.Choice(name="English US - Male 1", value="en_us_006"), app_commands.Choice(name="English US - Male 2", value="en_us_007"), app_commands.Choice(name="English US - Male 3", value="en_us_009"), app_commands.Choice(name="English US - Male 4", value="en_us_010"), app_commands.Choice(name="Ghost Face", value="en_us_ghostface"), app_commands.Choice(name="Chewbacca", value="en_us_chewbacca"), app_commands.Choice(name="C3PO", value="en_us_c3po"), app_commands.Choice(name="Stitch", value="en_us_stitch"), app_commands.Choice(name="Stormtrooper", value="en_us_stormtrooper"), app_commands.Choice(name="Rocket", value="en_us_rocket"), app_commands.Choice(name="Singing - Alto", value="en_female_f08_salut_damour"), app_commands.Choice(name="Singing - Tenor", value="en_male_m03_lobby"), app_commands.Choice(name="Singing - Warmy Breeze", value="en_female_f08_warmy_breeze"), app_commands.Choice(name="Singing - Sunshine Soon", value="en_male_m03_sunshine_soon"), app_commands.Choice(name="Narrator", value="en_male_narration"), app_commands.Choice(name="Wacky", value="en_male_funny"), app_commands.Choice(name="Peaceful", value="en_female_emotional")])
async def _saytt(interaction: discord.Interaction, voice: app_commands.Choice[str], message: str):
	# set all the voice values
	VOICES = [ 'en_us_ghostface', 'en_us_chewbacca', 'en_us_c3po', 'en_us_stitch', 'en_us_stormtrooper', 'en_us_rocket', 'en_au_001', 'en_au_002', 'en_uk_001', 'en_uk_003', 'en_us_001', 'en_us_002', 'en_us_006', 'en_us_007', 'en_us_009', 'en_us_010', 'fr_001', 'fr_002', 'de_001', 'de_002', 'es_002', 'es_mx_002', 'br_001', 'br_003', 'br_004', 'br_005', 'id_001', 'jp_001', 'jp_003', 'jp_005', 'jp_006', 'kr_002', 'kr_003', 'kr_004', 'en_female_f08_salut_damour', 'en_male_m03_lobby', 'en_female_f08_warmy_breeze', 'en_male_m03_sunshine_soon', 'en_male_narration', 'en_male_funny', 'en_female_emotional']
	voice = voice.value # get value of voice
	if voice in VOICES: # if the voice selected is valid
		voice_user = interaction.user.voice # define the voice user aka who's in a voice channel
		if voice_user != None: # if a user is in a voice channel
			await interaction.response.send_message("Working on it!", ephemeral=True) # reply, this needs to be done here bc the timeout of 3 seconds is often not enough
			global lastMessage # set the last message as a global thing, this is lazy ignore it
			lastMessage = message # set the last message variable to be used by the /repeat command
			tts(message, voice, "speech.mp3", play_sound=False) # use tiktok text to speech and save the files
			vc.play(discord.FFmpegPCMAudio("speech.mp3")) # play message in voice channel
			msg = await interaction.original_response() # get original response
			await msg.edit(content="Done!") # edit original response
		else:
			await interaction.response.send_message("This voice does not exist. [[list of voices]](https://nexii.feen.us/60nucfrfh3.txt)")

@_saytt.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("what voice do you want to use / what do you want it to say? [[list of voices]](https://nexii.feen.us/60nucfrfh3.txt)")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send("Something borked, make sure Iggy is in a voice channel (use **join**)")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /repeat, repeat last text to speech message
@bot.tree.command(name="repeat", description="Repeat the last text to speech message.")
async def _repeat(interaction: discord.Interaction):
	voice_user = interaction.user.voice # define the voice user aka who's in a voice channel
	if voice_user != None: # if a user is in a voice channel
		await interaction.response.send_message(lastMessage) # send text message of the last message said
		vc.play(discord.FFmpegPCMAudio("speech.mp3")) # play last message said in the voice channel
	else:
		await interaction.response.send_message("You need to be in a voice channel to do this.", ephemeral=True)

@_repeat.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		await ctx.send("Something borked, make sure Iggy is in a voice channel (use **join**)")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /save, save a text to speech voice message to file and send
@bot.tree.command(name="save", description="Generate a text to speech file with a selected voice.")
@app_commands.describe(voice = "voice to use")
@app_commands.describe(message = "message to say")
@app_commands.choices(voice=[ app_commands.Choice(name="English AU - Female", value="en_au_001"), app_commands.Choice(name="English AU - Male", value="en_au_002"), app_commands.Choice(name="English UK - Male 1", value="en_uk_001"), app_commands.Choice(name="English UK - Male 2", value="en_uk_003"), app_commands.Choice(name="English US - Female (Int. 1)", value="en_us_001"), app_commands.Choice(name="English US - Female (Int. 2)", value="en_us_002"), app_commands.Choice(name="English US - Male 1", value="en_us_006"), app_commands.Choice(name="English US - Male 2", value="en_us_007"), app_commands.Choice(name="English US - Male 3", value="en_us_009"), app_commands.Choice(name="English US - Male 4", value="en_us_010"), app_commands.Choice(name="Ghost Face", value="en_us_ghostface"), app_commands.Choice(name="Chewbacca", value="en_us_chewbacca"), app_commands.Choice(name="C3PO", value="en_us_c3po"), app_commands.Choice(name="Stitch", value="en_us_stitch"), app_commands.Choice(name="Stormtrooper", value="en_us_stormtrooper"), app_commands.Choice(name="Rocket", value="en_us_rocket"), app_commands.Choice(name="Singing - Alto", value="en_female_f08_salut_damour"), app_commands.Choice(name="Singing - Tenor", value="en_male_m03_lobby"), app_commands.Choice(name="Singing - Warmy Breeze", value="en_female_f08_warmy_breeze"), app_commands.Choice(name="Singing - Sunshine Soon", value="en_male_m03_sunshine_soon"), app_commands.Choice(name="Narrator", value="en_male_narration"), app_commands.Choice(name="Wacky", value="en_male_funny"), app_commands.Choice(name="Peaceful", value="en_female_emotional")])
async def _save(interaction: discord.Interaction, voice: app_commands.Choice[str], message: str):
	await interaction.response.send_message("Working on it!", ephemeral=True) # reply, this needs to be done here bc the timeout of 3 seconds is often not enough
	voice = voice.value # get value of voice
	tts(message, voice, "speech.mp3", play_sound=False) # use tiktok tts to get the audio file
	sendFile = f"speech.mp3" # get the thingy to send
	msg = await interaction.original_response() # get original response
	await msg.add_files(discord.File(sendFile)) # edit original response	
	await msg.edit(content="Done!") # edit original response

'''@_save.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("what voice do you want to use / what do you want it to say? [[list of voices]](https://nexii.feen.us/60nucfrfh3.txt)")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send(undefinedError)
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)'''

# /relay, send message as iggy
@bot.tree.command(name="relay", description="Send a message as iggy.")
@app_commands.describe(message = "message to relay")
async def _relay(interaction: discord.Interaction, message: str):
	await interaction.channel.send(message)
	await interaction.response.send_message("Done!", ephemeral=True)
	pass

@_relay.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("What message do you want Iggy to relay?")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send(undefinedError)
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /dm, dm someone as iggy
@bot.tree.command(name="dm", description="DM a server user as iggy.")
@app_commands.describe(who = "who to message")
@app_commands.describe(message = "message to send")
async def _dm(interaction: discord.Interaction, who: discord.Member, message: str):
	usr = await bot.fetch_user(who.id)
	await usr.send(message)
	await interaction.response.send_message("Done!", ephemeral=True)
	pass

@_dm.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Who do you want Iggy do DM / what message do you want Iggy to relay?")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send("User ID is invalid or the user's settings are preventing Iggy frrom messaging them.")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

#-----------------------------------------
#
#                 Scores
#
#-----------------------------------------

# /score, keymash score list
@bot.tree.command(name="score", description="Show keymash scoreboard.")
async def _score(interaction: discord.Interaction):
	scoreList = [] # make an empty list
	toSend = "Keymash Scores:\n" # prepare message 
	for member in interaction.guild.members: # for every member in the server, do this
		iggyData = iggyFile.read(member, interaction.guild) # get the data
		if iggyData.keymashScore != "0": # if the score for the user isn't 0
			scoreList.append(f"{member.display_name}: {iggyData.keymashScore}") # add score entry to list
		scoreList.sort(key=num_sort, reverse = True) # order the list
	toSend += '\n'.join(scoreList) # add list items to message
	await interaction.response.send_message(toSend) # send message

# /3score, :3 score list
@bot.tree.command(name="3score", description="Show :3 scoreboard.")
async def _3score(interaction: discord.Interaction):
	scoreList = [] # make an empty list
	toSend = ":3 Scores:\n" # prepare message 
	for member in interaction.guild.members: # for every member in the server, do this
		iggyData = iggyFile.read(member, interaction.guild) # get the data
		if iggyData.kittyScore != "0": # if the score for the user isn't 0
			scoreList.append(f"{member.display_name}: {iggyData.kittyScore}") # add score entry to list
		scoreList.sort(key=num_sort, reverse = True) # order the list
	toSend += '\n'.join(scoreList) # add list items to message
	await interaction.response.send_message(toSend) # send message

#-----------------------------------------
#
#                  Kink
#
#-----------------------------------------

# /imp, impersonate a server user
@bot.tree.command(name="imp", description="Impersonate a user.")
@app_commands.describe(who = "who to impersonate")
@app_commands.describe(message = "what to say")
async def _imp(interaction: discord.Interaction, who: discord.Member, message: str):
	webhook = await getWebhook(interaction)
	if hasattr(interaction.channel, "parent") == False:
		await webhook.send(str(message), username=who.display_name, avatar_url=who.display_avatar.url)
		await interaction.response.send_message("Done!", ephemeral=True)
	if hasattr(interaction.channel, "parent") == True:
		await webhook.send(str(message), username=who.display_name, thread=message.channel, avatar_url=who.display_avatar.url)
		await interaction.response.send_message("Done!", ephemeral=True)

@_imp.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Who do you want Iggy to impersonate / what do you want to say?")
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send("User not found.")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send("Command failed to run, Iggy may not have sufficient permissions to delete your message.")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

#define gag translations
dictLoose = {"l": "w", "t": "g", "s": "f", "L": "W", "T": "G", "S": "F"}
dictSevere = {"h":"d","u":"d","i":"d","q":"d","k":"m","l":"f","d":"f","b":"f","j":"r","s":"r","v":"r","a":"r","z":"r","x":"r","g":"n","i":"d","H":"D","U":"D","I":"D","Q":"D","K":"M","L":"F","D":"F","B":"F","J":"R","S":"R","V":"R","A":"R","Z":"R","X":"R","G":"N","I":"D"}
dictExtreme = {"t":"m","e":"m","u":"m","i":"m","k":"m","b":"m","o":"m","a":"m","u":"m","s":"m","d":"m","v":"m","q":"ph","c":"ph","r":"ph","n":"ph","j":"ph","r":"ph","l":"ph","y":"ph","w":"f","x":"f","z":"f","T":"M","E":"M","U":"M","I":"M","K":"M","B":"M","O":"M","A":"M","U":"M","S":"M","D":"M","V":"M","Q":"PH","C":"PH","R":"PH","N":"PH","J":"PH","R":"PH","L":"PH","Y":"PH","W":"F","X":"F","Z":"F"}				
dictMute = {"a":"#","b":"#","c":"#","d":"#","e":"#","f":"#","g":"#","h":"#","i":"#","j":"#","k":"#","l":"#","m":"#","n":"#","o":"#","p":"#","q":"#","r":"#","s":"#","t":"#","u":"#","v":"#","w":"#","x":"#","y":"#","z":"#","A":"#","B":"#","C":"#","D":"#","E":"#","F":"#","G":"#","H":"#","I":"#","J":"#","K":"#","L":"#","M":"#","N":"#","O":"#","P":"#","Q":"#","R":"#","S":"#","T":"#","U":"#","V":"#","W":"#","X":"#","Y":"#","Z":"#"}
looseTrans = str.maketrans(dictLoose)
severeTrans = str.maketrans(dictSevere)
extremeTrans = str.maketrans(dictExtreme)
muteTrans = str.maketrans(dictMute)

#gag replacement code
async def gagReplace(msg, message, gagtype):
	#define gagtypes
	if gagtype == "loose":
		newmsg = msg.translate(looseTrans)
	elif gagtype == "severe":
		newmsg = msg.translate(severeTrans)
	elif gagtype == "extreme":
		newmsg = msg.translate(extremeTrans)
	elif gagtype == "mute":
		newmsg = msg.translate(muteTrans)
	elif gagtype == "dog":
		dogsounds = ["worf!","borf!","bark!","warf!","awroof!","bworf!","rooroo!","woof!","wauf!","ruff!","woof!"]
		newmsg = random.choice(dogsounds)
	elif gagtype == "pooltoy":
		pooltoysounds = ["Sqrrk!!", "Creak!", "Squeak!", "Bwomp!", "Squirk!"]
		newmsg = random.choice(pooltoysounds)
	# replace message
	if msg != newmsg: # if the replacement message isn't the same as the original
		if message.attachments != []: # make a files variable if there are files, saves space to put it here
			files=[await f.to_file() for f in message.attachments]
		webhook = await getWebhook(message) # get the webhook
		if message.reference is not None: # if it is replying to someone
			inreplyto = await message.channel.fetch_message(message.reference.message_id)
			replyembed = discord.Embed(description=f"**[Reply to:]({inreplyto.jump_url})** {inreplyto.content[0:98]}...")
			replyembed.set_author(name=f"{inreplyto.author.display_name} ↩️", icon_url=inreplyto.author.display_avatar.url)
			if hasattr(message.channel, "parent") == False:	# if it is not in a thread
				if message.attachments != []: # if has attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), files=files, username=message.author.display_name, embed=replyembed, avatar_url=message.author.display_avatar.url)
				else: # if no attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), username=message.author.display_name, embed=replyembed, avatar_url=message.author.display_avatar.url)
			elif hasattr(message.channel, "parent") == True: #if it is in a thread
				if message.attachments != []: # if has attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), files=files, username=message.author.display_name, thread=message.channel, embed=replyembed, avatar_url=message.author.display_avatar.url)
				else: # if no attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), username=message.author.display_name, thread=message.channel, embed=replyembed, avatar_url=message.author.display_avatar.url)
		elif message.flags.has_thread == False: # if it is not replying to someone
			if hasattr(message.channel, "parent") == False:
				if message.attachments != []: # if has attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), files=files, username=message.author.display_name, avatar_url=message.author.display_avatar.url)
				else: # if no attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), username=message.author.display_name, avatar_url=message.author.display_avatar.url)
			elif hasattr(message.channel, "parent") == True:
				if message.attachments != []: # if has attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), files=files, username=message.author.display_name, thread=message.channel, avatar_url=message.author.display_avatar.url)
				else: # if no attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), username=message.author.display_name, thread=message.channel, avatar_url=message.author.display_avatar.url)
		await message.delete()
	else:
		pass

# /gag, turn on a gag
@bot.tree.command(name="gag", description="Apply a gag to yourself. Optionally set an owner, they will be the only user who can remove the gag.")
@app_commands.describe(gagtype = "Gag type")
@app_commands.describe(owner = "Owner")
@app_commands.choices(gagtype=[
        app_commands.Choice(name="Loose", value="loose"),
        app_commands.Choice(name="Severe", value="severe"),
        app_commands.Choice(name="Extreme", value="extreme"),
		app_commands.Choice(name="Mute", value="mute"),
		app_commands.Choice(name="Dog", value="dog"),
		app_commands.Choice(name="Pooltoy", value="pooltoy"),
        ])
async def _gag(interaction: discord.Interaction, gagtype: app_commands.Choice[str], owner: discord.Member = None):
	# define owner
	if owner == None: # if no owner is defined
		ownerID = str(interaction.user.id) # set owner id to self ID
		owner = interaction.user # change owner from none to message sender (self)
	else:
		ownerID = str(owner.id) # set owner id to id of selected user
	#define messages
	messageGaggedSelf = f"You gagged yourself! :3\n(gag type: {gagtype.value}, unlockable by: {owner.display_name})"		
	messageGagChanged = f"Gag type changed! :3\n(gag type: {gagtype.value}, unlockable by: {owner.display_name})"
	# open and read user data
	iggyData = iggyFile.read(interaction.user, interaction.guild)
	# define writing to file
	getUser = bot.get_user(int(iggyData.gagOwner)) # get owner on file
	ownerOnFile = getUser.display_name # get owner on file name
	messageNotAllowed = f"You're not allowed :3 ({ownerOnFile} is)"
	if iggyData.gagType == "none": # if the user has no gag set
		iggyData.gagType = gagtype.value # set gagtype on data to desired gag type
		iggyData.gagOwner = ownerID # set owner ID
		iggyFile.write(iggyData, interaction.user, interaction.guild) # write data to file
		await interaction.response.send_message(messageGaggedSelf)		
	elif iggyData.gagType != "none": # if the user does have a gag set
		if iggyData.gagOwner == str(interaction.user.id): # if the owner is the user
			iggyData.gagType = gagtype.value # set gagtype on data to desired gag type
			iggyData.gagOwner = ownerID # set owner ID
			iggyFile.write(iggyData, interaction.user, interaction.guild) # write data to file
			await interaction.response.send_message(messageGagChanged)
		elif iggyData.gagOwner != str(interaction.user.id): # if the owner is not the user
			await interaction.response.send_message(messageNotAllowed)

# /ungag, de-activate a gag
@bot.tree.command(name="ungag", description="Remove a gag. Remove a gag. Leave \"(who)\" blank to ungag yourself, or select someone else to ungag.")
@app_commands.describe(who = "who do you want to ungag")
async def _ungag(interaction: discord.Interaction, who: discord.Member = None):
	# define server / who ran the command / an owner
	if who == None: # if no target is defined
		target = interaction.user # change target from none to message sender (self)
	else:
		target = who
	#define messages
	messageUngaggedSelf = f"Gag removed."		
	messageUngaggedSomeone = f"{target.display_name}'s gag removed."
	messageSelfNotGagged = f"You're not gagged!"
	messageNotGagged = f"{target.display_name} is not gagged!"
	# open and read user data
	iggyData = iggyFile.read(target, interaction.guild)
	# define writing to file
	getUser = bot.get_user(int(iggyData.gagOwner)) # get owner on file
	ownerOnFile = getUser.display_name # get owner on file name
	messageNotAllowed = f"You're not allowed :3 ({ownerOnFile} is)"
	if iggyData.gagType == "none": # if the user has no gag set
		if target == interaction.user: # if user is trying to ungag self, send message
			await interaction.response.send_message(messageSelfNotGagged)
		elif target != interaction.user: #if user is trying to ungag someone else, send message
			await interaction.response.send_message(messageNotGagged)
	else: # if the user does have a gag set
		if iggyData.gagOwner == str(interaction.user.id): # if user has permission to ungag
			iggyData.gagType = "none" # write new gag (none)
			iggyData.gagOwner = str(interaction.user.id) # set owner as self
			iggyFile.write(iggyData, target, interaction.guild) # write data to file
			if target == interaction.user: # if target is self
				await interaction.response.send_message(messageUngaggedSelf)
			elif target != interaction.user: #if target is someone else
				await interaction.response.send_message(messageUngaggedSomeone)
		elif iggyData.gagOwner != str(interaction.user.id): # if doesn't have permission to ungag
			await interaction.response.send_message(messageNotAllowed)

# /bully, change a user's nickname
@bot.tree.command(name="bully", description="Change a user's nickname.")
@app_commands.describe(who = "whose nickname to change")
@app_commands.describe(nickname = "what to change their nickname to")
async def _bully(interaction: discord.Interaction, who: discord.Member, nickname: str):
	await who.edit(nick = nickname)
	await interaction.response.send_message(f"{who.global_name}'s name was changed to \"{nickname}\"!")
	pass

@_bully.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Whose name do you want to change / what do you want to change it to?")
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send("User not found.")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send("Command failed to run, Iggy may not have sufficient permissions to edit this user's nickname.")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /secretbully, change a user's nickname quietly
@bot.tree.command(name="secretbully", description="Change a user's nickname without sending a message.")
@app_commands.describe(who = "whose nickname to change")
@app_commands.describe(nickname = "what to change their nickname to")
async def _secretbully(interaction: discord.Interaction, who: discord.Member, nickname: str):
	await who.edit(nick = nickname)
	await interaction.response.send_message(f"{who.global_name}'s name was changed to \"{nickname}\"!", ephemeral=True)
	pass

@_secretbully.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Whose name do you want to change / what do you want to change it to?")
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send("User not found.")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send("Command failed to run, Iggy may not have sufficient permissions to edit this user's nickname.")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

#-----------------------------------------
#
#                  Misc
#
#-----------------------------------------

# /peet, send a random paw pic
@bot.tree.command(name="peet", description="Sends a random paw picture.")
async def _peet(interaction: discord.Interaction):
	relative_path = "paws/"
	full_path = os.path.join(absolute_path, relative_path)
	sendPeet = f"{full_path}{random.choice(os.listdir(full_path))}"
	await interaction.response.send_message(file=discord.File(sendPeet))

# /dronename, generate a drone name
@bot.tree.command(name="dronename", description="Generate a drone name. \"(Length)\" determines how long it should be (multiplied by 2)")
@app_commands.describe(length = "how long should the name be?")
async def _dronename(interaction: discord.Interaction, length: int):
	name = secrets.token_hex(length)
	await interaction.response.send_message(name)

# /boop, boop a user
@bot.tree.command(name="boop", description="Boop someone.")
@app_commands.describe(who = "who to boop")
async def _boop(interaction: discord.Interaction, who: discord.Member):
	iggyData = iggyFile.read(who, interaction.guild)
	scoreInt = int(iggyData.boopScore)
	scoreInt += 1
	iggyData.boopScore = str(scoreInt)
	iggyFile.write(iggyData, who, interaction.guild)
	await interaction.response.send_message(f"<@{who.id}> has been booped! They've been booped {scoreInt} times!")

# /source, get image source
@bot.tree.command(name="source", description="Get source for an image link. Also usable by right clicking on a message > Apps > Get Image Source.")
@app_commands.describe(link = "link to the image")
async def _source(interaction: discord.Interaction, link: str):
	if bool(re.search("(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])", link, re.IGNORECASE)): # check if entry is a valid link
		sauce = SauceNao(getSauceToken()) # initialize sauce
		results = sauce.from_url(link) # get results
		best = results[0]  # get the best result
		links = "" # define empty links string
		for link in best.urls: # add every link to string
			links = f"{links}\n{link}"
		embed = discord.Embed(title=f"Drawn by: {best.author}", colour=discord.Colour(0xffd912), description=f"Similarity: {best.similarity}%\nLinks:{links}") # set base embed
		embed.set_footer(text="Powered by SauceNAO") # set embed footer
		embed.set_thumbnail(url=best.thumbnail) # set embed thumbnail
		await interaction.response.send_message(embed=embed) # send response with embed
	else: #if the link is not valid
		await interaction.response.send_message("This is not a valid link.", ephemeral=True)

'''
# /userinfo, list info of a user
@bot.tree.command(name="userinfo", description="List saved Iggy preferences for a specific user.")
@app_commands.describe(who = "whose info to display")
async def _boop(interaction: discord.Interaction, who: discord.Member = None):
	if who == None: # if no target user was defined
		who = interaction.user # define target as user who ran the command
	iggyData = iggyFile.read(who, interaction.guild) # read iggy data
	embed = discord.Embed(title="a0b8", colour=discord.Colour(0x4f5bee), description="### ?info\nDisplays this command list\n### ?say (Message)\na0b8 will repeat the message\n### ?do (Action)\na0b8 will preform the action to the best of its ability\n### ?find (Subject)\na0b8 will find the subject online to the best of its ability\n### ?titleme (Title)\na0b8 will call you by the entered title\n### ?bully (New name)\na0b8 will use the entered name\n### ?idea (Your idea)\nSend a0b8 an idea for a new command")
	embed.set_author(name="a0b8", icon_url="https://cdn.discordapp.com/attachments/1124439205808963594/1159579645717524551/a0bp_shaded_pfp.png")
	embed.set_footer(text="a0b8 appreciates praise, let it know if its been a good drone.")

	await interaction.response.send_message(f"<@{who.id}> has been booped! They've been booped {scoreInt} times!")
	            self.displayName = displayName
                self.userid = userid
                self.keymashScore = keymashScore
                self.kittyScore = kittyScore
                self.boopScore = boopScore
                self.gagType = gagType
                self.gagOwner = gagOwner
                self.thirdPerson = thirdPerson
                self.yinglet = yinglet'''

#-----------------------------------------
#
#              Context Menu
#
#-----------------------------------------

# delete message
async def deleteBotMessage(interaction: discord.Interaction, message: discord.Message):
	if message.author.id == 1103354385930657854:
		await message.delete()
		await interaction.response.send_message("Message deleted!", ephemeral=True)
	elif message.author.display_name == interaction.user.display_name:
		await message.delete()
		await interaction.response.send_message("Message deleted!", ephemeral=True)
	else:
		await interaction.response.send_message("You cannot delete this message.", ephemeral=True)
deleteContextMenu = app_commands.ContextMenu(name='❌ Delete Message', callback=deleteBotMessage)
bot.tree.add_command(deleteContextMenu)

# source image
async def sourceContext(interaction: discord.Interaction, message: discord.Message):
	link = re.search("(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])", message.content, re.IGNORECASE) # get link from message
	if link == None and message.attachments == []: # if message doesn't have a link or attachments
		await interaction.response.send_message("Could not find a link in selected message.", ephemeral=True)
	async def respond(interaction): # define response code
		best = results[0]  # get the best result
		links = "" # define empty links string
		for link in best.urls: # add every link to string
			links = f"{links}\n{link}"
		embed = discord.Embed(title=f"Drawn by: {best.author}", colour=discord.Colour(0xffd912), description=f"Similarity: {best.similarity}%\nLinks:{links}") # set base embed
		embed.set_footer(text="Powered by SauceNAO") # set embed footer
		embed.set_thumbnail(url=best.thumbnail) # set embed thumbnail
		await interaction.response.send_message(embed=embed) # send response with embed
	if link == None and message.attachments != []: # if message doesn't have a link BUT has attachments
		sauce = SauceNao(getSauceToken()) # initialize sauce
		link = message.attachments[0].proxy_url
		results = sauce.from_url(link) # get results
		await respond(interaction=interaction)
	else: # if message has link
		sauce = SauceNao(getSauceToken()) # initialize sauce
		results = sauce.from_url(link.group(0)) # get results
		await respond(interaction=interaction) # respond
		
sourceContextMenu = app_commands.ContextMenu(name='🖼️ Get Image Source', callback=sourceContext)
bot.tree.add_command(sourceContextMenu)

#-----------------------------------------
#
#             Per Message Code
#
#-----------------------------------------

@bot.listen()
async def on_message(message):
	channel = message.channel
	msg = message.content
	if hasattr(message.guild, "id") == True and msg.endswith("<:ignore:1176605355900416020>") == False: # make sure this isn't DMs and ignore messages that have ignore emote
		iggyData = iggyFile.read(message.author, message.guild) # define iggy data object
		server = message.guild.id
		#keymash detection
		if bool(re.search("(?![^\s]*(\w)\\1{1,})([b-df-hj-np-tv-xz]){5,}", msg, re.IGNORECASE)) == True and bool(re.search("\/|[x]", msg)) == False and bool(re.search(generateReList(), msg, re.IGNORECASE)) == False and message.author.id != 193461317342986240 and message.author.bot == False:
			keymashScoreNew = int(iggyData.keymashScore)
			keymashScoreNew += 1
			iggyData.keymashScore = str(keymashScoreNew)
			iggyFile.write(iggyData, message.author, message.guild)
			if str(keymashScoreNew).endswith("00"):
				await channel.send(f"{keymashScoreNew} keymash milestone reached!")
			
		#:3 detection
		if bool(re.search("(:|;)3\s|(:|;)3$|(:|;)3c\s|(:|;)3c$|(:|;)3E\s|(:|;)3E$", msg, re.IGNORECASE)) == True and bool(re.search("\/|[x]", msg)) == False and message.author.id != 193461317342986240 and message.author.bot == False:
			kittyScoreNew = int(iggyData.kittyScore)
			kittyScoreNew += 1
			iggyData.kittyScore = str(kittyScoreNew)
			iggyFile.write(iggyData, message.author, message.guild)
			if str(kittyScoreNew).endswith("00"):
				await channel.send(f"{kittyScoreNew} :3 milestone reached!")

		#third person detection
		if bool(re.search("(^|\s)(i|me|my|im|i'm|i'd|i've|ive|i'll)(\s|$)", msg, re.IGNORECASE)) and bool(re.search("http://|https://|[x]|^p:", msg, re.IGNORECASE)) == False:
			if iggyData.thirdPerson == "on":
				await channel.send("Silly thing, you can't talk in first person!")
				
		#yingy text detection
		if bool(re.search("th", msg, re.IGNORECASE)) and bool(re.search("http://|https://|[x]", msg, re.IGNORECASE)) == False:
			if iggyData.yinglet == "on":
				await channel.send("silly thing, yinglets don't talk like that!")

		#gag detection
		if bool(re.search("http://|https://|[x]", msg, re.IGNORECASE)) == False and message.type != discord.MessageType.thread_created: # make sure it doesn't contain a link or start a thread
			if iggyData.gagType != "none": # if a gag is set
				await gagReplace(msg, message, iggyData.gagType)

		#twin detection
		if message.type != discord.MessageType.thread_created: # make sure it doesn't or start a thread
			if iggyData.twin != str(message.author.id): # if a user is twinning someone
				await twinReplace(msg, message, iggyData.twin)

		#make a thread when posting  in #art
		if message.author.bot == False and message.channel.id == 1124374436871667774:
			if message.attachments or bool(re.search("https://|http://", msg, re.IGNORECASE)):
				asdf = message.author.display_name
				await message.create_thread(name=f"replies to {asdf}'s post", slowmode_delay=None, reason=None)
				pass

		#reminder to use new commands
		oldCommands = [">tpon",">tpoff",">yingon",">yingoff",">join",">leave",">say",">saytt",">save",">relay",">dm",">score",">:3score",">imp",">gag",">ungag",">bully",">secretbully",">peet",">dronename",">boop",">info"]
		if msg.lower().startswith(tuple(oldCommands)) and message.author.bot == False:
			msgCommand = msg.partition(" ")[0]
			await channel.send(f"Use /{msgCommand[1:]} instead!")

		#deffy bot commands
		if msg.lower().startswith("?info"):
			embed = discord.Embed(title="a0b8", colour=discord.Colour(0x4f5bee), description="### ?info\nDisplays this command list\n### ?say (Message)\na0b8 will repeat the message\n### ?do (Action)\na0b8 will preform the action to the best of its ability\n### ?find (Subject)\na0b8 will find the subject online to the best of its ability\n### ?titleme (Title)\na0b8 will call you by the entered title\n### ?bully (New name)\na0b8 will use the entered name\n### ?idea (Your idea)\nSend a0b8 an idea for a new command")
			embed.set_author(name="a0b8", icon_url="https://cdn.discordapp.com/attachments/1124439205808963594/1159579645717524551/a0bp_shaded_pfp.png")
			embed.set_footer(text="a0b8 appreciates praise, let it know if its been a good drone.")
			webhook = await getWebhook(message)
			if hasattr(channel, "parent") == False:
				await webhook.send(embed=embed, username="a0b8", avatar_url="https://cdn.discordapp.com/attachments/1124439205808963594/1159579645717524551/a0bp_shaded_pfp.png")
			if hasattr(channel, "parent") == True:
				await webhook.send(embed=embed, username="a0b8", thread=message.channel, avatar_url="https://cdn.discordapp.com/attachments/1124439205808963594/1159579645717524551/a0bp_shaded_pfp.png")
		
		#helper bot commands
		if msg.lower().startswith("<info"):
			embed = discord.Embed(title="Helper Bot", colour=discord.Colour(0x66d199), description="### <info\nDisplays this command list\n### <say (Message)\nHelper will repeat the message\n### <do (Action)\nHelper will preform the action to the best of its ability\n### <find (Subject)\nHelper will find the subject online to the best of its ability\n### <titleme (Title)\nHelper will call you by the entered title\n### <bully (New name)\nHelper will use the entered name\n### <idea (Your idea)\nSend Helper an idea for a new command")
			embed.set_author(name="Helper", icon_url="https://cdn.discordapp.com/attachments/897498264448950282/1127789397165756426/IMG_7709.jpg")
			embed.set_footer(text="Helper Bot appreciates praise, let it know if its been a good drone.")
			webhook = await getWebhook(message)
			if hasattr(channel, "parent") == False:
				await webhook.send(embed=embed, username="best drone (1ece) <info for commands", avatar_url="https://cdn.discordapp.com/attachments/897498264448950282/1127789397165756426/IMG_7709.jpg")
			if hasattr(channel, "parent") == True:
				await webhook.send(embed=embed, username="best drone (1ece) <info for commands", thread=message.channel, avatar_url="https://cdn.discordapp.com/attachments/897498264448950282/1127789397165756426/IMG_7709.jpg")

#-----------------------------------------
#
#             On Reaction Code
#
#-----------------------------------------

#delete iggy's message
@bot.listen()
async def on_reaction_add(reaction, user):
	whatEmoji = reaction.emoji
	if reaction.message.author.id == 1103354385930657854 and whatEmoji == "❌":
		await reaction.message.delete()
		pass
	elif reaction.message.author.display_name == user.display_name and whatEmoji == "❌":
		await reaction.message.delete()
		pass

bot.run(getToken())