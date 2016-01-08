# Lemmy's stuff
import LemmyUtils as Lutils
import RandomLenny

# Other stuff
import random
import discord
import asyncio
import os
from os import listdir
from os.path import isfile, join
import json
import sqlite3
import datetime
from PIL import Image

async def help(self, msg, dmsg):
	await self.client.send_message(msg.channel, "http://lynq.me/lemmy")

async def emotes(self, msg, dmsg):
	await self.client.send_message(msg.channel, "http://lynq.me/lemmy/#emotes")

async def stickers(self, msg, dmsg):
	await self.client.send_message(msg.channel, "http://lynq.me/lemmy/#stickers")

async def lenny(self, msg, dmsg):
	if len(dmsg.flags) == 0:
		await self.client.send_message(msg.channel, self.res.lennies[random.randint(0, len(self.res.lennies)-1)])
	elif dmsg.flags[0][0] == "-og":
		await self.client.send_message(msg.channel, self.res.lenny)
	elif dmsg.flags[0][0] == "-r":
		await self.client.send_message(msg.channel, RandomLenny.randomLenny())

async def logout(self, msg, dmsg):
	print("User with id " + str(msg.author.id) + " attempting to initiate logout.")
	if not Lutils.IsAdmin(msg.author):
		await self.client.send_message(msg.channel, "Error: User is not admin.")
	else:
		await self.client.send_message(msg.channel, "Shutting down.")
		await self.client.logout()

async def refresh(self, msg, dmsg):
	refreshedEmotes = [ os.path.splitext(f)[0] for f in listdir("pics/emotes") if isfile(join("pics/emotes",f)) ]
	refreshedStickers = [ os.path.splitext(f)[0] for f in listdir("pics/stickers") if isfile(join("pics/stickers",f)) ]

	newEmotes = [item for item in refreshedEmotes if item not in self.res.emotes]
	newStickers = [item for item in refreshedStickers if item not in self.res.stickers]

	self.res.emotes = refreshedEmotes
	self.res.stickers = refreshedStickers

	if len(newEmotes) > 0:
		await self.client.send_message(msg.channel, "__**New emotes:**__")

		for emote in newEmotes:
			await self.client.send_message(msg.channel, emote)
			await self.client.send_file(msg.channel, "pics/emotes/" + emote + ".png")

	if len(newStickers) > 0:
		await self.client.send_message(msg.channel, "__**New stickers:**__")

		for sticker in newStickers:
			await self.client.send_message(msg.channel, sticker)
			await self.client.send_file(msg.channel, "pics/stickers/" + sticker + ".png")

	await self.client.delete_message(msg)

async def correct(self, msg, dmsg):
	await self.client.send_message(msg.channel, "https://youtu.be/OoZN3CAVczs")

async def eightball(self, msg, dmsg):
	responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]
	await self.client.send_message(msg.channel, msg.author.mention + " :8ball: " + random.choice(responses))

async def userinfo(self, msg, dmsg):
	if len(dmsg.params) > 0:
		username = dmsg.params[0]
		user = Lutils.FindUserByName(msg.channel.server.members, username)
		if not user:
			await self.client.send_message(msg.channel, "User not found.")
		else:
			message = "**Username:** " + user.name + "\n**ID:** " + user.id + "\n**Join date:** " + str(user.joined_at)

			balance = Lutils.GetLemmyCoinBalance(self.res, user)
			if balance is not None:
				message += "\n**LemmyCoin Balance:** L$" + str(balance)

			message += "\n**Avatar URL:** " + user.avatar_url

			if user.voice_channel is not None:
				message += "\nCurrently talking in " + user.voice_channel.mention + "."

			# if user.game_id is not None:
			# 	message += "\nCurrent playing " + str(user.game_id) + "."

			await self.client.send_message(msg.channel, message)

async def channelinfo(self, msg, dmsg):
	if len(dmsg.params) > 0:
		channelName = dmsg.params[0]
		channel = discord.utils.find(lambda m: m.name == channelName, [x for x in msg.channel.server.channels if x.type == discord.ChannelType.text])
		if channel:
			await self.client.send_message(msg.channel, "**Channel name: **" + channel.mention + "\n**ID: **" + channel.id)
		else:
			await self.client.send_message(msg.channel, "Channel not found.")

async def james(self, msg, dmsg):
	if len(dmsg.params) > 0:
		if dmsg.params[0] in self.res.jamesDb:
			response = msg.author.mention  + " pinging "
			for userId in self.res.jamesDb[dmsg.params[0]]:
				user = Lutils.FindUserById(msg.channel.server.members, userId)
				if user is not None:
					if user.status != discord.Status.offline and user != msg.author:
						response += user.mention + " "
			response += "for " + self.res.jamesConverter[dmsg.params[0]]
			await self.client.send_message(msg.channel, response)

	for fullFlag in dmsg.flags:
		flag = fullFlag[0]
		flagParams = fullFlag[1:] if len(fullFlag) > 1 else []
		update = False

		if flag == "-tags":
			response = "```"
			for key in self.res.jamesDb:
				response += "\n" + key + " (" + self.res.jamesConverter[key] + ")"
				for userId in self.res.jamesDb[key]:
					user = Lutils.FindUserById(msg.channel.server.members, userId)
					response += "\n> " + user.name
				response += "\n"
			response += "```"
			await self.client.send_message(msg.channel, response)

		elif flag == "-join":
			if len(flagParams) == 0:
				await self.client.send_message(msg.channel, msg.author.mention + " was not added to any tag: No tag was specified.")
			else:
				gameTag = flagParams[0]
				if not gameTag in self.res.jamesDb:
					await self.client.send_message(msg.channel, msg.author.mention + " was not added to '" + gameTag + "': No such tag exists.")
				else:
					if msg.author.id in self.res.jamesDb[gameTag]:
						await self.client.send_message(msg.channel, msg.author.mention + " was not added to '" + gameTag + "': User is already in '" + gameTag + "'.")
					else:
						update = True
						self.res.jamesDb[gameTag].append(msg.author.id)
						await self.client.send_message(msg.channel, msg.author.mention + " was successfully added to '" + gameTag + "'.")
					
		elif flag == "-leave":
			if len(flagParams) == 0:
				await self.client.send_message(msg.channel, msg.author.mention + " was not removed from any tag: No tag was specified.")
			else:
				gameTag = flagParams[0]
				if not gameTag in self.res.jamesDb:
					await self.client.send_message(msg.channel, msg.author.mention + " was not removed from '" + gameTag + "': No such tag exists.")
				else:
					if not msg.author.id in self.res.jamesDb[gameTag]:
						await self.client.send_message(msg.channel, msg.author.mention + " was not removed from '" + gameTag + "': User is not in '" + gameTag + "'.")
					else:
						update = True
						self.res.jamesDb[gameTag] = [x for x in self.res.jamesDb[gameTag] if x != msg.author.id]
						await self.client.send_message(msg.channel, msg.author.mention + " was successfully removed from '" + gameTag + "'.")

		elif flag == "-create":
			if not Lutils.IsModOrAbove(msg.author):
				await self.client.send_message(msg.channel, "No new tag created: User is not moderator or above.")
			else:
				if len(flagParams) == 0:
					await self.client.send_message(msg.channel, "No new tag created: No tag name was specified.")
				else:
					if len(flagParams) == 1:
						await self.client.send_message(msg.channel, "New tag '" + flagParams[0] + "' not created: No display name was given.")
					else:
						gameTag = flagParams[0]
						displayName = " ".join(flagParams[1:])

						if gameTag in self.res.jamesDb:
							await self.client.send_message(msg.channel, "New tag '" + gameTag + "' not created: Tag already exists.")
						else:
							update = True
							self.res.jamesDb[gameTag] = []
							self.res.jamesConverter[gameTag] = displayName
							await self.client.send_message(msg.channel, "New tag '" + gameTag + "' successfully created with display name '" + displayName + "'.")

		elif flag == "-delete":
			if not Lutils.IsModOrAbove(msg.author):
				await self.client.send_message(msg.channel, "No tag deleted: User is not moderator or above.")
			else:
				if len(flagParams) == 0:
					await self.client.send_message(msg.channel, "No tag deleted: No tag name was specified.")
				else:
					gameTag = flagParams[0]
					if not gameTag in self.res.jamesDb:
						await self.client.send_message(msg.channel, "Tag '" + gameTag + "' not deleted: Tag does not exist.")
					else:
						update = True
						self.res.jamesDb.pop(gameTag, None)
						self.res.jamesConverter.pop(gameTag, None)
						await self.client.send_message(msg.channel, "Tag '" + gameTag + "' successfully deleted.")						

		if update:
			try:
				with open("db/jamesDb.json", "w") as f:
					json.dump(self.res.jamesDb, f)
			except Exception as e:
				print("ERROR updating JamesDb! (" + str(e) + ")")
			else:
				print("JamesDb updated with " + str(len(self.res.jamesDb)) + " games.")

			try:
				with open("db/jamesConverter.json", "w") as f:
					json.dump(self.res.jamesConverter, f)
			except Exception as e:
				print("ERROR updating JamesConverter! (" + str(e) + ")")
			else:
				print("JamesConverter updated with " + str(len(self.res.jamesConverter)) + " games.")

async def happening(self, msg, dmsg):
	await self.client.send_message(msg.channel, "https://i.imgur.com/bYGOUHP.png")

async def ruseman(self, msg, dmsg):
	await self.client.send_file(msg.channel, "pics/ruseman/" + random.choice(os.listdir("pics/ruseman/")))

async def lemmycoin(self, msg, dmsg):
	for fullFlag in dmsg.flags:
		flag = fullFlag[0]
		param1 = fullFlag[1] if len(fullFlag) > 1 else None
		param2 = fullFlag[2] if len(fullFlag) > 2 else None

		if flag == "-balance" or flag == "-b":
			user = None

			if param1 is None:
				user = msg.author
			else:
				targetUser = Lutils.FindUserByName(msg.channel.server.members, param1)
				if targetUser is None:
					await self.client.send_message(msg.channel, "User '" + param1 + "' was not found on this Discord server.")
				else:
					user = targetUser

			if user is not None:
				balance = Lutils.GetLemmyCoinBalance(self.res, user)

				if balance is None:
					await self.client.send_message(msg.channel, user.mention + " does not have a LemmyCoin balance because they have not been registered in the database.")
				else:
					await self.client.send_message(msg.channel, user.mention + " has a LemmyCoin balance of L$" + str(balance) + ".")

		elif flag == "-pay" or flag == "-p":
			if param1 is not None:
				target = Lutils.FindUserByName(msg.channel.server.members, param1)
				if target is None:
					await self.client.send_message(msg.channel, "LemmyCoins not sent: User '" + param1 + "' was not found on this server.")
				elif param2 is None:
					await self.client.send_message(msg.channel, "No LemmyCoins paid to " + target.name + ": No amount was specified.")
				else:
					try:
						amount = float(param2)
					except ValueError:
						await self.client.send_message(msg.channel, "No LemmyCoins paid to " + target.name + ": Amount was incorrectly formatted.")
					else:
						if amount <= 0:
							await self.client.send_message(msg.channel, "No LemmyCoins paid to " + target.name + ": Amount must be greater than zero.")
						else:
							cursor = self.res.sqlConnection.cursor()
							cursor.execute("SELECT COUNT(*) FROM tblUser WHERE UserId = ?", (target.id,))
							result = cursor.fetchone()[0]

							if result == 0:
								await self.client.send_message(msg.channel, "No LemmyCoins paid to " + target.name + ": " + target.name + " has not been registered in the database.")
							else:
								cursor.execute("SELECT LemmyCoinBalance FROM tblUser WHERE UserId = ?", (msg.author.id,))
								senderBalance = cursor.fetchone()[0]

								if senderBalance < amount:
									await self.client.send_message(msg.channel, "No LemmyCoins paid to " + target.name + ": " + msg.author.mention + " does not have enough LemmyCoins in their account to make the payment.")
								else:
									cursor.execute("UPDATE tblUser SET LemmyCoinBalance = LemmyCoinBalance - ? WHERE UserId = ?", (amount, msg.author.id))
									cursor.execute("UPDATE tblUser SET LemmyCoinBalance = LemmyCoinBalance + ? WHERE UserId = ?", (amount, target.id))
									cursor.execute("INSERT INTO tblLemmyCoinPayment (DateTime, SenderId, ReceiverId, Amount) VALUES (?, ?, ?, ?)", (datetime.datetime.now(), msg.author.id, target.id, amount))
									self.res.sqlConnection.commit()
									await self.client.send_message(msg.channel, "**L$" + str(amount) + "** successfully sent to " + target.mention + " by " + msg.author.mention + ".")

async def channelids(self, msg, dmsg):
	ret = ""
	for channel in msg.channel.server.channels:
		ret += channel.name + " : " + channel.id + "\n"
	await self.client.send_message(msg.channel, ret)

async def serverinfo(self, msg, dmsg):
	#await self.client.send_message(msg.channel, msg.channel.server.name + ": " + msg.channel.server.id)
	server = msg.server
	response = "**Name:** " + server.name
	response += "\n**Region:** " + str(server.region)
	response += "\n**Owner:** " + server.owner.name
	response += "\n**Population:** " + str(len(server.members)) + " (" + str(len([member for member in server.members if member.status != discord.Status.offline])) + " currently online)"
	response += "\n**Roles:** "
	for role in server.roles:
		response += "\n  " + ("everyone" if role.name == "@everyone" else role.name)
	response += "\n**Default channel:** " + server.default_channel.name
	response += "\n**AFK channel:** " + server.afk_channel.name
	response += "\n**AFK timeout length:** " + str(server.afk_timeout) + " minutes"
	response += "\n**Icon URL:** " + server.icon_url


	await self.client.send_message(msg.channel, response)

async def choose(self, msg, dmsg):
	params = ["OR" if x.lower() == "or" else x for x in dmsg.params]
	options = " ".join(params).split(" OR ")
	options = [x for x in options if x != ""]
	if len(options) > 0:
		# await self.client.send_message(msg.channel, msg.author.mention + "\n```\n" + random.choice(options) + "\n```")
		await self.client.send_message(msg.channel, msg.author.mention + "   `" + random.choice(options) + "`")

# async def radio(self, msg, dmsg):
# 	# radioChannel = discord.utils.find(lambda m: m.id == "133010408377286656", msg.server.channels)
# 	# if not radioChannel:
# 	# 	await client.send_message(msg.channel, "Radio channel not found.")
# 	# else:
# 	# 	voice = await client.join_voice_channel(radioChannel)
# 	# 	player = voice.create_ffmpeg_player("audio/songs/sirens_in_the_distance.mp3")
# 	# 	player.start()

# 	flag = Lutils.GetNthFlagWithAllParams(1, params)[0]
# 	flagParams = Lutils.GetNthFlagWithAllParams(1, params)[1:]

# 	if flag == "-quick":
# 		musicDir = "N:\Cafe Del Mar"
# 		await client.send_message(msg.channel, "Queueing directory " + musicDir)
# 		res.radio.QueueDirectory(musicDir)
# 		await client.send_message(msg.channel, "Directory queued. New queue size: " + str(res.radio.queue.qsize()))
		
# 		res.radio.ShuffleQueue()
# 		await client.send_message(msg.channel, "Queue shuffled.")

# 		radioChannel = res.radio.GetRadioChannel()
# 		voice = await client.join_voice_channel(radioChannel)
# 		res.radio.SetVoiceConnection(voice)
# 		while not res.radio.queue.empty():
# 			res.radio.StartNextSong()
# 			#await client.send_message(res.radio.GetInfoChannel(), res.radio.GetCurrentSong())

# 	elif flag == "-queuedir":
# 		await client.send_message(msg.channel, "Queueing directory " + flagParams[0])
# 		res.radio.QueueDirectory(flagParams[0])
# 		await client.send_message(msg.channel, "Directory queued. New queue size: " + str(res.radio.queue.qsize()))

# 	elif flag == "-shuffle":
# 		res.radio.ShuffleQueue()
# 		await client.send_message(msg.channel, "Queue shuffled.")

# 	elif flag == "-play":
# 		radioChannel = res.radio.GetRadioChannel()
# 		voice = await client.join_voice_channel(radioChannel)
# 		res.radio.SetVoiceConnection(voice)
# 		while not res.radio.queue.empty():
# 			res.radio.StartNextSong()
# 			#await client.send_message(res.radio.GetInfoChannel(), res.radio.GetCurrentSong())

# 	elif flag == "-stop":
# 		res.radio.StopPlayer()

# 	elif flag == "-pause":
# 		res.radio.PausePlayer()

# 	elif flag == "-resume":
# 		res.radio.ResumePlayer()

# 	elif flag == "-clear":
# 		res.radio.ClearQueue()
# 		await client.send_message(msg.channel, "Queue cleared. [DEBUG] len(queue)=" + str(res.radio.queue.qsize()))

# 	# elif flag == "-nowplaying":
# 	# 	await client.send_message(msg.channel, res.radio.GetCurrentSong())

# 	elif flag == "-viewqueue":
# 		await client.send_message(msg.channel, res.radio.ViewQueue())

#####################
# Archived commands #
#####################

# def register(client, res, msg, params):
# 	if Lutils.IsAdmin(msg.author):
# 		if len(params) > 0:
# 			userId = params[0]
			
# 			cursor = res.sqlConnection.cursor()
# 			cursor.execute("SELECT COUNT(*) FROM tblUser WHERE UserId = ?", (userId,))
# 			if cursor.fetchone()[0] > 0:
# 				await client.send_message(msg.channel, "User with id " + userId + " not registered to database: User already exists in database.")
# 			else:
# 				user = Lutils.FindUserById(msg.channel.server.members, userId)
# 				if not user:
# 					await client.send_message(msg.channel, "User with id " + userId + " not registered to database: ID does not reference a Discord user on this server.")
# 				else:
# 					cursor.execute("INSERT INTO tblUser (UserId, LemmyCoinBalance) VALUES (?, 10)", (userId,))
# 					res.sqlConnection.commit()
# 					await client.send_message(msg.channel, "User with id " + userId + " (" + user.mention + ") successfully registered to database.")

# async def combine(self, msg, dmsg):
# 	# This command is deprecated, since it's a native feature of the bot
# 	allEmotes = True
# 	for param in params:
# 		if param not in res.emotes and param not in res.stickers:
# 			allEmotes = False

# 	if allEmotes:
# 		images = []
# 		for param in params:
# 			try:
# 				images.append(Image.open("pics/emotes/" + param + ".png"))
# 			except IOError:
# 				images.append(Image.open("pics/stickers/" + param + ".png"))

# 	Lutils.CombineImages(images)

# 	await client.send_file(msg.channel, "pics/result.png")

# async def tts(self, msg, dmsg):
# 	await self.client.send_message(msg.channel, msg.content[5:], tts=True)
# 	await self.client.delete_message(msg)