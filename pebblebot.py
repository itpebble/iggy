from dis import disco
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import sys
import re
import random
import openai
import secrets
import requests
from tiktokvoice import tts
from gtts import gTTS

# get into the PI:
# ssh -i /Users/pebble/key pebble@192.168.1.206
#tmux, ctrl b + d

# test or live token?
tokenType = "live"

# fetch bot token
def getToken():
	with open(os.path.join(sys.path[0], f'tokens/{tokenType}.txt')) as f:
		token = f.read()
	return token

# IDEAS
#
# NEW COMMANDS: 
# - twinning function
# - add message to list of quotes, say random quote 
# - rainworld name generator
# - some kinda chastity timer (self/public/specific people)
# - (cobalt suggestion) /squish, only usable on pooltoys, makes pooltoy do an involuntary squeak
#
# TWEAKS:
# - make commands that save variables use a single file
# - replace regex with something less taxing
# - give commands full descriptions
# - gag: work with links
# - message replacements - replace message first, only then delete
# - make third person and yinglet thingy work with pluralkit tags

# Initializing
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='>', intents=intents)
client = discord.Client(intents=intents)

# define things
absolute_path = os.path.dirname(__file__)
undefinedError = "Something borked."
global lastMessage
lastMessage = "a"

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
		embed = discord.Embed(title="Text Correction", colour=discord.Colour(0xffd912), description="### /tpon\nIggy will remind you when you forget to talk in third person.\n### /tpoff\nDisables third person reminders.\n### /yingon\nIggy will remind you to talk like a yinglet.\n### /yingoff\nDisables yingspeech reminders.")
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
		embed = discord.Embed(title="Kink", colour=discord.Colour(0xffd912), description="### /imp (who) (message)\nImpersonate a user.\n### /gag (type) (owner)\nApply a gag to yourself. This will edit your messages to make them sound as if you were gagged. You can (but don't have to) also define an owner, who will then be the only person able to remove the gag.\n### /ungag (who)\nRemove a gag. Leave \"(who)\" blank to ungag yourself, or select someone else to ungag, if you are set as their owner.\n### /bully (who) (new nickname)\nChange a user's nickname.\n### /secretbully (who) (new nickname)\nChange a user's nickname without sending a message.")
		embed.set_author(name="Iggy", icon_url="https://nexii.feen.us/yjf8a3j1vd.jpg")
		embed.set_footer(text="contact @ebbl for help")
		try:
			await interaction.response.edit_message(embed=embed, view=self)
		except:
			pass

	# misc section
	@discord.ui.button(label="Misc", style=discord.ButtonStyle.grey)
	async def miscbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed = discord.Embed(title="Misc", colour=discord.Colour(0xffd912), description="### /peet\nSends a random paw picture.\n### /dronename (length)\nGenerate a drone name. \"(Length)\" determines how long it should be (multiplied by 2). For example, /dronename 2 will generate a dronename that is 4 characters long.\n### /boop (who)\nBoop someone.")
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

# /tpon, turn on third person detection
@bot.tree.command(name="tpon", description="Iggy will remind you when you forget to talk in third person.")
async def _tpon(interaction: discord.Interaction):
	relative_path = "tp"
	full_path = os.path.join(absolute_path, relative_path)
	where = interaction.guild_id
	who = f"{interaction.user.id}"
	serverFileExists = os.path.exists(f'{full_path}/{where}.txt')
	if serverFileExists == False:
		with open(f'{full_path}/{where}.txt', 'w') as f:
			f.write(f'{who}\n')
			await interaction.response.send_message(f"Iggy will now remind you when you forget to talk in third person :3")
			pass
	elif serverFileExists == True:
		tpfile = open(f"{full_path}/{where}.txt", "r")
		tplist = tpfile.read().splitlines()
		if who in tplist:
			await interaction.response.send_message(f"You already have third person reminders enabled, use **/tpoff** to turn them off.")
			pass
		else:
			with open(f'{full_path}/{where}.txt', 'a') as f:
				f.write(f"{who}\n")
			await interaction.response.send_message(f"Iggy will now remind you when you forget to talk in third person :3")
			pass

@_tpon.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /tpoff, turn off third person detection
@bot.tree.command(name="tpoff", description="Disables third person reminders.")
async def _tpoff(interaction: discord.Interaction):
	relative_path = "tp"
	full_path = os.path.join(absolute_path, relative_path)
	where = interaction.guild_id
	who = f"{interaction.user.id}"
	serverFileExists = os.path.exists(f'{full_path}/{where}.txt')
	if serverFileExists == False:
		await interaction.response.send_message(f"You don't have third person reminders enabled, use **/tpon** to turn them on.")
		pass
	elif serverFileExists == True:
		tpfile = open(f"{full_path}/{where}.txt", "r")
		tplist = tpfile.read().splitlines()
		if who in tplist:
			tplist.remove(who)
			with open(f'{full_path}/{where}.txt', 'w') as f:
				for x in tplist:
					f.write(f"{x}\n")
			await interaction.response.send_message(f"Iggy will no longer remind you to talk in third person.")
			pass
		else:
			await interaction.response.send_message(f"You don't have third person reminders enabled, use **/tpon** to turn them on.")
			pass

@_tpoff.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /yingon, turn on yingspeech detection
@bot.tree.command(name="yingon", description="Iggy will remind you to talk like a yinglet.")
async def _yingon(interaction: discord.Interaction):
	relative_path = "ying"
	full_path = os.path.join(absolute_path, relative_path)
	where = interaction.guild_id
	who = f"{interaction.user.id}"
	serverFileExists = os.path.exists(f'{full_path}/{where}.txt')
	if serverFileExists == False:
		with open(f'{full_path}/{where}.txt', 'w') as f:
			f.write(f'{who}\n')
			await interaction.response.send_message(f"Iggy will now remind you when you forget to talk like a yinglet :3")
			pass
	elif serverFileExists == True:
		tpfile = open(f"{full_path}/{where}.txt", "r")
		tplist = tpfile.read().splitlines()
		if who in tplist:
			await interaction.response.send_message(f"You already have yingspeech reminders enabled, use **/yingon** to turn them off.")
			pass
		else:
			with open(f'{full_path}/{where}.txt', 'a') as f:
				f.write(f"{who}\n")
			await interaction.response.send_message(f"Iggy will now remind you when you forget to talk like a yinglet :3")
			pass

@_yingon.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /yingoff, turn off yingspeech detection
@bot.tree.command(name="yingoff", description="Disables yingspeech reminders.")
async def _yingoff(interaction: discord.Interaction):
	relative_path = "ying"
	full_path = os.path.join(absolute_path, relative_path)
	where = interaction.guild_id
	who = f"{interaction.user.id}"
	serverFileExists = os.path.exists(f'{full_path}/{where}.txt')
	if serverFileExists == False:
		await interaction.response.send_message(f"You don't have yingspeech reminders enabled, use **/yingon** to turn them on")
		pass
	elif serverFileExists == True:
		tpfile = open(f"{full_path}/{where}.txt", "r")
		tplist = tpfile.read().splitlines()
		if who in tplist:
			tplist.remove(who)
			with open(f'{full_path}/{where}.txt', 'w') as f:
				for x in tplist:
					f.write(f"{x}\n")
			await interaction.response.send_message(f"Iggy will no longer remind you to talk like a yinglet.")
			pass
		else:
			await interaction.response.send_message(f"You don't have yingspeech reminders enabled, use **/tpon** to turn them on.")
			pass

@_yingoff.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

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
@bot.tree.command(name="say", description="Use text to speech.")
@app_commands.describe(message = "message to say")
async def _say(interaction: discord.Interaction, message: str):
	global lastMessage
	lastMessage = message
	gttsthing = gTTS(message)
	gttsthing.save('speech.mp3')
	voice_user = interaction.user.voice
	if voice_user != None:
		vc.play(discord.FFmpegPCMAudio("speech.mp3"))
		await interaction.response.send_message("Done!", ephemeral=True)
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
@bot.tree.command(name="saytt", description="Use text to speech with a TikTok voice.")
@app_commands.describe(voice = "voice to use")
@app_commands.describe(message = "message to say")
@app_commands.choices(voice=[ app_commands.Choice(name="English AU - Female", value="en_au_001"), app_commands.Choice(name="English AU - Male", value="en_au_002"), app_commands.Choice(name="English UK - Male 1", value="en_uk_001"), app_commands.Choice(name="English UK - Male 2", value="en_uk_003"), app_commands.Choice(name="English US - Female (Int. 1)", value="en_us_001"), app_commands.Choice(name="English US - Female (Int. 2)", value="en_us_002"), app_commands.Choice(name="English US - Male 1", value="en_us_006"), app_commands.Choice(name="English US - Male 2", value="en_us_007"), app_commands.Choice(name="English US - Male 3", value="en_us_009"), app_commands.Choice(name="English US - Male 4", value="en_us_010"), app_commands.Choice(name="Ghost Face", value="en_us_ghostface"), app_commands.Choice(name="Chewbacca", value="en_us_chewbacca"), app_commands.Choice(name="C3PO", value="en_us_c3po"), app_commands.Choice(name="Stitch", value="en_us_stitch"), app_commands.Choice(name="Stormtrooper", value="en_us_stormtrooper"), app_commands.Choice(name="Rocket", value="en_us_rocket"), app_commands.Choice(name="Singing - Alto", value="en_female_f08_salut_damour"), app_commands.Choice(name="Singing - Tenor", value="en_male_m03_lobby"), app_commands.Choice(name="Singing - Warmy Breeze", value="en_female_f08_warmy_breeze"), app_commands.Choice(name="Singing - Sunshine Soon", value="en_male_m03_sunshine_soon"), app_commands.Choice(name="Narrator", value="en_male_narration"), app_commands.Choice(name="Wacky", value="en_male_funny"), app_commands.Choice(name="Peaceful", value="en_female_emotional")])
async def _saytt(interaction: discord.Interaction, voice: app_commands.Choice[str], message: str):
	VOICES = [ 'en_us_ghostface', 'en_us_chewbacca', 'en_us_c3po', 'en_us_stitch', 'en_us_stormtrooper', 'en_us_rocket', 'en_au_001', 'en_au_002', 'en_uk_001', 'en_uk_003', 'en_us_001', 'en_us_002', 'en_us_006', 'en_us_007', 'en_us_009', 'en_us_010', 'fr_001', 'fr_002', 'de_001', 'de_002', 'es_002', 'es_mx_002', 'br_001', 'br_003', 'br_004', 'br_005', 'id_001', 'jp_001', 'jp_003', 'jp_005', 'jp_006', 'kr_002', 'kr_003', 'kr_004', 'en_female_f08_salut_damour', 'en_male_m03_lobby', 'en_female_f08_warmy_breeze', 'en_male_m03_sunshine_soon', 'en_male_narration', 'en_male_funny', 'en_female_emotional']
	voice = voice.value
	if voice in VOICES:
		global lastMessage
		lastMessage = message
		tts(message, voice, "speech.mp3", play_sound=False)
		voice_user = interaction.user.voice
		if voice_user != None:
			vc.play(discord.FFmpegPCMAudio("speech.mp3"))
			await interaction.response.send_message("Done!", ephemeral=True)
			pass
		else:
			await interaction.response.send_message("You need to be in a voice channel to do this.")
			pass
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
	voice_user = interaction.user.voice
	if voice_user != None:
		vc.play(discord.FFmpegPCMAudio("speech.mp3"))
		await interaction.response.send_message(lastMessage)
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
	voice = voice.value
	tts(message, voice, "speech.mp3", play_sound=False)
	sendFile = f"{absolute_path}/speech.mp3"
	await interaction.response.send_message(file=discord.File(sendFile))
	pass	

@_save.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("what voice do you want to use / what do you want it to say? [[list of voices]](https://nexii.feen.us/60nucfrfh3.txt)")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send(undefinedError)
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

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
	server = interaction.guild_id
	relative_path = f"score/{server}"
	full_path = os.path.join(absolute_path, relative_path)
	toSend = "Scores:\n"
	scoreList = []
	for x in os.listdir(full_path):
		scoreFile = open(f"{full_path}/{x}", "r")
		score = scoreFile.read().splitlines()
		scoreList.append(f"{score[0]}: {score[1]}")
	scoreList.sort(key=num_sort, reverse = True)
	toSend += '\n'.join(scoreList)
	await interaction.response.send_message(toSend)

@_score.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /3score, :3 score list
@bot.tree.command(name="3score", description="Show :3 scoreboard.")
async def _3score(interaction: discord.Interaction):
	server = interaction.guild_id
	relative_path = f"score3/{server}"
	full_path = os.path.join(absolute_path, relative_path)
	toSend = "Scores:\n"
	scoreList = []
	for x in os.listdir(full_path):
		scoreFile = open(f"{full_path}/{x}", "r")
		score = scoreFile.read().splitlines()
		scoreList.append(f"{score[0]}: {score[1]}")
	scoreList.sort(key=num_sort, reverse = True)
	toSend += '\n'.join(scoreList)
	await interaction.response.send_message(toSend)

@_3score.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

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
	if gagtype == "1" or gagtype == 1:
		newmsg = msg.translate(looseTrans)
	elif gagtype == "2" or gagtype == 2:
		newmsg = msg.translate(severeTrans)
	elif gagtype == "3" or gagtype == 3:
		newmsg = msg.translate(extremeTrans)
	elif gagtype == "4" or gagtype == 4:
		newmsg = msg.translate(muteTrans)
	elif gagtype == "5" or gagtype == 5:
		dogsounds = ["worf!","borf!","bark!","warf!","awroof!","bworf!","rooroo!","woof!","wauf!","ruff!","woof!"]
		newmsg = random.choice(dogsounds)
	elif gagtype == "6" or gagtype == 6:
		pooltoysounds = ["Sqrrk!!", "Creak!", "Squeak!", "Bwomp!", "Squirk!"]
		newmsg = random.choice(pooltoysounds)
	#replace message
	if msg != newmsg:
		await message.delete()
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
			if hasattr(message.channel, "parent") == True: #if it is in a thread
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
			if hasattr(message.channel, "parent") == True:
				if message.attachments != []: # if has attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), files=files, username=message.author.display_name, thread=message.channel, avatar_url=message.author.display_avatar.url)
				else: # if no attachments
					await webhook.send(str(f"{newmsg}\n💬: ||{msg}||"), username=message.author.display_name, thread=message.channel, avatar_url=message.author.display_avatar.url)
	else:
		pass

# /gag, turn on a gag
@bot.tree.command(name="gag", description="Apply a gag to yourself.")
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
	# set number for gagtype
	gagtype = gagtype.value
	gagTypes=["loose","severe","extreme","mute","dog","pooltoy"] # index list
	gagTypeID = gagTypes.index(gagtype)+1 # +1 because 0 is no gag
	# define path to files
	full_path = os.path.join(absolute_path, "gag")
	# define server / who ran the command / an owner
	server = interaction.guild_id
	user = interaction.user
	if owner == None: #if no owner is defined
		ownerID = interaction.user.id # set owner id to self ID
		owner = interaction.user # change owner from none to message sender (self)
	else:
		ownerID = owner.id # set owner id to id of selected user
	#define messages
	messageGaggedSelf = f"You gagged yourself! :3\n(gag type: {gagtype}, unlockable by: {owner.display_name})"		
	messageGagChanged = f"Gag type changed! :3\n(gag type: {gagtype}, unlockable by: {owner.display_name})"
	# open and read file
	serverPathExists = os.path.exists(f'{full_path}/{server}') # define checking for if server path exists
	userFileExists = os.path.exists(f'{full_path}/{server}/{user.id}.txt') # define checking for if user file exists
	# define writing to file
	if serverPathExists == False: # check if server has a folder, if not make one
		os.mkdir(f'{full_path}/{server}')
	if userFileExists == False: # check if user file exists, if not make one
		with open(f'{full_path}/{server}/{user.id}.txt', 'w') as f:
			f.write(f'{gagTypeID}\n{ownerID}') # write gag type number and then owner ID to file
			await interaction.response.send_message(messageGaggedSelf)
	elif userFileExists == True: # if user file exists, continue
		gagFile = open(f"{full_path}/{server}/{user.id}.txt", "r") # open user's gag file
		gagList = gagFile.read().splitlines() # make list from file
		getUser = bot.get_user(int(gagList[1])) # get owner on file id
		ownerOnFile = getUser.display_name # get owner on file name
		messageNotAllowed = f"You're not allowed :3 ({ownerOnFile} is)"
		if gagList[0] == "0": # if the user has no gag set
			with open(f'{full_path}/{server}/{user.id}.txt', 'w') as f: # write new gag
				f.write(f'{gagTypeID}\n{ownerID}') # write gag type number and then owner ID to file
				await interaction.response.send_message(messageGaggedSelf)
		elif gagList[0] != "0": # if the user does have a gag set
			if gagList[1] == str(ownerID): # if the owner is the user
				with open(f'{full_path}/{server}/{user.id}.txt', 'w') as f:
					f.write(f'{gagTypeID}\n{ownerID}') # write gag type number and then owner ID to file
					await interaction.response.send_message(messageGagChanged)
			if gagList[1] != str(ownerID): # if the owner is not the user
				await interaction.response.send_message(messageNotAllowed)

@_gag.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("what type of gag do you want to apply? (**loose**, **severe**, **extreme**, **mute**, **dog** or **pooltoy**)")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send(undefinedError)
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /ungag, de-activate a gag
@bot.tree.command(name="ungag", description="Remove a gag.")
@app_commands.describe(who = "who do you want to ungag")
async def _ungag(interaction: discord.Interaction, who: discord.Member = None):
	# define path to files
	full_path = os.path.join(absolute_path, "gag")
	# define server / who ran the command / an owner
	server = interaction.guild_id
	user = interaction.user
	if who == None: #if no target is defined
		targetID = interaction.user.id # set target id to self ID
		target = interaction.user # change target from none to message sender (self)
	else:
		targetID = who.id # set target id to id of selected user
		target = who
	#define messages
	messageUngaggedSelf = f"Gag removed."		
	messageUngaggedSomeone = f"{target.display_name}'s gag removed."
	messageSelfNotGagged = f"You're not gagged!"
	messageNotGagged = f"{target.display_name} is not gagged!"
	# open and read file
	serverPathExists = os.path.exists(f'{full_path}/{server}') # define checking for if server path exists
	userFileExists = os.path.exists(f'{full_path}/{server}/{targetID}.txt') # define checking for if user file exists
	# define writing to file
	if serverPathExists == False: # if the server doesn't have a folder
		if target == user: # if user is trying to ungag self, send message
			await interaction.response.send_message(messageSelfNotGagged)
		elif target != user: #if user is trying to ungag someone else, send message
			await interaction.response.send_message(messageNotGagged)
	if userFileExists == False: # if the user file doesn't exist
		if target == user: # if user is trying to ungag self, send message
			await interaction.response.send_message(messageSelfNotGagged)
		elif target != user: #if user is trying to ungag someone else, send message
			await interaction.response.send_message(messageNotGagged)
	elif userFileExists == True: # if user file exists, continue
		gagFile = open(f"{full_path}/{server}/{targetID}.txt", "r") # open user's gag file
		gagList = gagFile.read().splitlines() # make list from file
		getUser = bot.get_user(int(gagList[1])) # get owner on file id
		ownerOnFile = getUser.display_name # get owner on file name
		messageNotAllowed = f"You're not allowed :3 ({ownerOnFile} is)"
		if gagList[0] == "0": # if the user has no gag set
			if target == user: # if user is trying to ungag self, send message
				await interaction.response.send_message(messageSelfNotGagged)
			elif target != user: #if user is trying to ungag someone else, send message
				await interaction.response.send_message(messageNotGagged)
		else: # if the user does have a gag set
			if gagList[1] == str(user.id): # if user has permission to ungag
				with open(f'{full_path}/{server}/{targetID}.txt', 'w') as f: # write new gag
					f.write(f'0\n{targetID}') # remove gag - write 0 and then owner ID to file
					if target == user: # if target is self
						await interaction.response.send_message(messageUngaggedSelf)
					elif target != user: #if target is someone else
						await interaction.response.send_message(messageUngaggedSomeone)
			elif gagList[1] != str(targetID): # if doesn't have permission to ungag
				await interaction.response.send_message(messageNotAllowed)

@_ungag.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		await ctx.send(undefinedError)
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

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
	pass

@_peet.error
async def infoError(ctx, error):
	if isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /dronename, generate a drone name
@bot.tree.command(name="dronename", description="Generate a drone name.")
@app_commands.describe(length = "how long should the name be?")
async def _dronename(interaction: discord.Interaction, length: int):
	name = secrets.token_hex(length)
	await interaction.response.send_message(name)
	pass

@_dronename.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("How long should the name be?")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send("Command failed to run (the parameter has to be a number).")
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

# /boop, boop a user
@bot.tree.command(name="boop", description="Boop someone.")
@app_commands.describe(who = "who to boop")
async def _boop(interaction: discord.Interaction, who: discord.Member):
	relative_path = "score2"
	full_path = os.path.join(absolute_path, relative_path)
	mention = who.id
	server = interaction.guild_id
	serverPathExists = os.path.exists(f'{full_path}/{server}')
	scoreFileExists = os.path.exists(f'{full_path}/{server}/{mention}.txt')
	if serverPathExists == False:
		os.mkdir(f'{full_path}/{server}')
		pass
	if scoreFileExists == False:
		with open(f'{full_path}/{server}/{mention}.txt', 'w') as f:
			f.write('1')
		await interaction.response.send_message(f"<@{mention}> has been booped! They've been booped 1 time!")
		pass
	if scoreFileExists == True:
		scoreFile = open(f"{full_path}/{server}/{mention}.txt", "r")
		score = scoreFile.read()
		scoreInt = int(score)
		scoreInt += 1
		with open(f'{full_path}/{server}/{mention}.txt', 'w') as f:
			f.write(f'{scoreInt}')
		await interaction.response.send_message(f"<@{mention}> has been booped! They've been booped {scoreInt} times!")
		pass

@_boop.error
async def infoError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Who do you want to boop?")
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send("User not found.")
	elif isinstance(error, commands.CommandInvokeError):
		await ctx.send(undefinedError)
	elif isinstance(error, commands.CommandError):
		await ctx.send(undefinedError)

#-----------------------------------------
#
#              Context Menu
#
#-----------------------------------------

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

#-----------------------------------------
#
#             Per Message Code
#
#-----------------------------------------

@bot.listen()
async def on_message(message):
	channel = message.channel
	msg = message.content
	if hasattr(message.guild, "id") == True: #make sure this isn't DMs
		server = message.guild.id
		#keymash detection
		if bool(re.search("(?![^\s]*(\w)\\1{1,})([b-df-hj-np-tv-xz]){5,}", msg, re.IGNORECASE)) == True and bool(re.search("\/|[x]", msg)) == False and bool(re.search(generateReList(), msg, re.IGNORECASE)) == False and message.author.id != 193461317342986240 and message.author.bot == False:
			relative_path = "score"
			full_path = os.path.join(absolute_path, relative_path)
			who = message.author.id
			usrname = message.author.global_name
			serverPathExists = os.path.exists(f'{full_path}/{server}')	
			scoreFileExists = os.path.exists(f'{full_path}/{server}/{who}.txt')
			detectedWord = re.search("(?![^\s]*(\w)\\1{1,})([b-df-hj-np-tv-xz]){5,}", msg, re.IGNORECASE)
			if serverPathExists == False:
				os.mkdir(f'{full_path}/{server}')
				pass
			if scoreFileExists == False:
				with open(f'{full_path}/{server}/{who}.txt', 'w') as f:
					f.write(f'{usrname}\n1')
				if server == "1050443221383254026":
					with open(f'{absolute_path}/keymashlog.txt', 'a') as f:
						f.write(f'{usrname}: {detectedWord}: {msg}\n')
					pass
			elif scoreFileExists == True:
				scoreFile = open(f"{full_path}/{server}/{who}.txt", "r")
				score = scoreFile.read().splitlines()
				scoreInt = int(score[1])
				scoreInt += 1
				with open(f'{full_path}/{server}/{who}.txt', 'w') as f:
					f.write(f'{usrname}\n{scoreInt}')
				if server == "1050443221383254026":
					with open(f'{absolute_path}/keymashlog.txt', 'a') as f:
						f.write(f'{usrname}: {detectedWord}: {msg}\n')
				if scoreInt == 50 or scoreInt == 100 or scoreInt == 200 or scoreInt == 300 or scoreInt == 400 or scoreInt == 500 or scoreInt == 1000:
					await channel.send(f"{scoreInt} keymash milestone reached!")
				pass
		#:3 detection
		if bool(re.search(":3\s|:3$|:3c\s|:3c$|:3E\s|:3E$", msg, re.IGNORECASE)) == True and bool(re.search("\/|[x]", msg)) == False and message.author.id != 193461317342986240 and message.author.bot == False:
			relative_path = "score3"
			full_path = os.path.join(absolute_path, relative_path)
			who = message.author.id
			usrname = message.author.global_name
			serverPathExists = os.path.exists(f'{full_path}/{server}')
			scoreFileExists = os.path.exists(f'{full_path}/{server}/{who}.txt')
			if serverPathExists == False:
				os.mkdir(f'{full_path}/{server}')
				pass
			if scoreFileExists == False:
				with open(f'{full_path}/{server}/{who}.txt', 'w') as f:
					f.write(f'{usrname}\n1')
			elif scoreFileExists == True:
				scoreFile = open(f"{full_path}/{server}/{who}.txt", "r")
				score = scoreFile.read().splitlines()
				scoreInt = int(score[1])
				scoreInt += 1
				with open(f'{full_path}/{server}/{who}.txt', 'w') as f:
					f.write(f'{usrname}\n{scoreInt}')
				if scoreInt == 50 or scoreInt == 100 or scoreInt == 200 or scoreInt == 300 or scoreInt == 400 or scoreInt == 500 or scoreInt == 1000:
					await channel.send(f"{scoreInt} :3 milestone reached!")
				pass
		#third person detection
		if bool(re.search("(^|\s)(i|me|my|im|i'm|i'd|i've|ive|i'll)(\s|$)", msg, re.IGNORECASE)):
			server = message.guild.id
			relative_path = "tp"
			full_path = os.path.join(absolute_path, relative_path)
			serverFileExists = os.path.exists(f'{full_path}/{server}.txt')
			if serverFileExists == True:
				tpfile = open(f"{full_path}/{server}.txt", "r")
				tplist = tpfile.read().splitlines()
				if f"{message.author.id}" in tplist:
					await channel.send("silly thing, you can't talk in first person!")
					pass
			else:
				pass
		#yingy text detection
		if bool(re.search("th", msg, re.IGNORECASE)) and bool(re.search("http://|https://|[x]", msg, re.IGNORECASE)) == False:
			server = message.guild.id
			relative_path = "ying"
			full_path = os.path.join(absolute_path, relative_path)
			serverFileExists = os.path.exists(f'{full_path}/{server}.txt')
			if serverFileExists == True:
				tpfile = open(f"{full_path}/{server}.txt", "r")
				tplist = tpfile.read().splitlines()
				if f"{message.author.id}" in tplist:
					await channel.send("silly thing, yinglets don't talk like that!")
					pass
			else:
				pass
		#gag detection
		if bool(re.search("http://|https://|[x]", msg, re.IGNORECASE)) == False and message.type != discord.MessageType.thread_created: # make sure it doesn't contain a link or start a thread
			server = message.guild.id
			relative_path = "gag"
			full_path = os.path.join(absolute_path, relative_path)
			where = message.guild.id
			who = message.author.id
			serverFileExists = os.path.exists(f'{full_path}/{where}/{who}.txt')
			serverPathExists = os.path.exists(f'{full_path}/{where}')
			if serverFileExists == True and serverPathExists == True:
				tpfile = open(f"{full_path}/{server}/{who}.txt", "r")
				tplist = tpfile.read().splitlines()
				#check if gag type is valid before running code
				if tplist[0] in ["1","2","3","4","5","6"]:
					await gagReplace(msg, message, tplist[0])
				else:
					pass
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