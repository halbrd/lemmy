import discord
import datetime
import asyncio
import os
import os.path
import json
import importlib
import sys

sys.path.append('modules')

class Lemmy:
	class NoConfigException(Exception):
		def __init__(self, message=None):
			if message is None:
				message = 'config.json does not exist (create it from config.example.json)'

			super(NoConfigException, self).__init__(message)


	def __init__(self, token):
		self.client = discord.Client()
		self.modules = {}

		# import config
		if not os.path.isfile('config.json'):
			raise NoConfigException

		self.config = json.load(open('config.json', 'r'))

		# load modules
		self.load_modules()

		# register events
		@self.client.event
		async def on_message(message):
			self.log(f'({message.channel.server.name}) {message.author.name} => #{message.channel.name}: {message.content}')

			# pass the event to the modules
			for _, module in self.modules.items():
				await module.on_message(message)

			if message.content == '$shutdown' and message.author.id == '77041679726551040':
				await self.client.logout()

		@self.client.event
		async def on_ready():
			self.log('Logged in.')

		# log in
		self.log('Logging in...')
		self.client.run(token)


	def log(self, message):
		output = '[{}] {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)

		print(output)

		if self.config['log_file']:
			with open(self.config['log_file'], 'a') as f:
				f.write(output + '\n')


	def load_modules(self):
		manifest = json.load(open('modules/manifest.json', 'r'))

		for module_name, class_name in manifest.items():
			module = importlib.import_module(module_name)
			importlib.reload(module)   # changes to the module will be loaded (for if this was called again while the bot is running)
			class_ = getattr(module, class_name)
			self.modules[class_name] = class_(self.client)



if __name__ == '__main__':
	if not os.path.isfile('config.json'):
		raise NoConfigException
	lemmy = Lemmy(json.load(open('config.json', 'r'))['token'])