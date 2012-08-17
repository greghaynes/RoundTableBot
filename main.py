import evloop
from bot import RoundTableBot
from plugin_loader import PluginLoader

if __name__=='__main__':
	plugin_loader = PluginLoader('plugins')
	bot = RoundTableBot('irc.cat.pdx.edu', 6667, 'RTB', 'RTB')
	bot.join('#rtb-test')
	bot.connect()
	plugin_loader.load_all(bot)
	evloop.EventDispatcher().loop_forever()

