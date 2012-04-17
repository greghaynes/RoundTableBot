import evloop
from bot import IrcBot

if __name__=='__main__':
	bot = IrcBot('irc.cat.pdx.edu', 6667, 'RTB', 'RTB')
	bot.join('#cscapstone-b')
	bot.connect()
	evloop.EventDispatcher().loop_forever()

