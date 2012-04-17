import evloop
from bot import RoundTableBot

if __name__=='__main__':
	bot = RoundTableBot('irc.cat.pdx.edu', 6667, 'RTB', 'RTB')
	bot.join('#rtb-test')
	bot.connect()
	evloop.EventDispatcher().loop_forever()

