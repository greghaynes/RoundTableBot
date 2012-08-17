import plugin
from eventbus import event_bus

class TwitterUpdatesPlugin(plugin.Plugin):
	def __init__(self, bot):
		self.bot = bot
		event_bus.connect('cmd.test', self.cmd_test)

	def cmd_test(self, sender, msg):
		self.bot.send_privmsg(sender, 'ohai')
