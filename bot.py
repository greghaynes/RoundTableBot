import evloop
import socket
import random

from irc import numeric_events
from settings import settings as default_settings

class IrcBot(evloop.TcpSocketWatcher):

	def __init__(self, server, port, nick, username, fullname='RTB', settings=default_settings()):
		super(IrcBot, self).__init__()
		self.server = server
		self.port = port
		self.nick = nick
		self.username = username
		self.fullname = fullname
		self.buffer = ''
		self.is_connected = False
		self.is_nicked = False
		self.channels = []
		self.settings = settings
		
	def connect(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.server, self.port))
		self.setup_socket(s)

	def join(self, channel):
		if channel not in self.channels:
			self.channels.append(channel)
			if self.is_connected:
				self.do_join(channel)

	def join_channels(self):
		for channel in self.channels:
			self.do_join(channel)

	def do_join(self, channel):
		self.send('JOIN :%s\r\n' % channel)

	def handle_connect(self):
		self.send('NICK %s\r\n' % self.nick)
		self.send('USER %s 0 * : %s\r\n' % (self.username, self.fullname))
		
	def handle_read(self, fd):
		tmp = self.socket.recv(1024)
		self.buffer += tmp
		lines = self.buffer.split('\r\n')
		self.buffer = lines.pop()
		for line in lines:
			self.handle_line(line)

	def handle_line(self, line):
		if not self.is_connected:
			self.is_connected = True
			self.handle_connect()
		parts = line.split(' ')

		if parts[0].startswith(':'):
			cmd = parts[1]
			prefix = parts[0][1:]
			args = parts[2:]
		else:
			cmd = parts[0]
			prefix = None
			args = parts[1:]
			args[0] = args[0][1:]

		if cmd.isdigit():
			cmd = numeric_events[cmd]

		try:
			func = getattr(self, 'on_'+cmd.lower())
		except AttributeError:
			pass
		else:
			func(line, args)

	def handle_privmsg(self, sender, msg):
		if msg.startswith(self.settings['cmd_prefix']):
			try:
				getattr(self, 'cmd_'+msg.split(' ')[0][1:].lower().replace('.', '_'))(sender, msg)
			except AttributeError:
				if self.settings['warn_command_notfound']:
					self.send_privmsg(sender, 'Not a valid command')

	def on_mode(self, line, args):
		if not self.is_nicked:
			self.is_nicked = True
			self.join_channels()

	def on_privmsg(self, line, args):
		elems = line.split(':')
		self.handle_privmsg(elems[1].split(' ')[2], elems[2])

	def on_nicknameinuse(self, line, arg):
		self.nick = self.nick + '_'
		self.handle_connect()

	def on_ping(self, line, args):
		self.send('PONG :%s\r\n' % args[0])

	def cmd_version(self, sender, msg):
		self.send_privmsg(sender, 'Round Table Bot v0.1')

	def send_privmsg(self, to, msg):
		self.send('PRIVMSG %s :%s\r\n' % (to, msg))


class NickRecordingBot(IrcBot):

	def __init__(self, server, port, nick, username, fullname='RTB', settings=default_settings()):
		super(NickRecordingBot, self).__init__(server, port, nick, username, fullname, settings)
		self.channel_names = {}

	def on_namreply(self, line, args):
		args = line.split(':')
		names = args[2].split(' ')
		channel = args[1].split(' ')[4]
		self.channel_names[channel] = {}
		for name in names:
			self.channel_names[channel][name] = True

	def on_join(self, line, args):
		nick = line.split('!')[0][1:]
		channel = args[0]
		if nick != self.nick:
			self.channel_names[channel][nick] = True

	def on_part(self, line, args):
		nick = line.split('!')[0][1:]
		channel = args[0]
		try:
			del self.channel_names[channel][nick]
		except KeyError:
			pass

	def cmd_listnicks(self, sender, msg):
		self.send_privmsg(sender, self.channel_nicks(sender))

	def channel_nicks(self, channel):
		return self.channel_names[channel].keys()

class RoundTableBot(NickRecordingBot):

	def __init__(self, server, port, nick, username, fullname='RTB', settings=default_settings()):
		super(RoundTableBot, self).__init__(server, port, nick, username, fullname, settings)
		self.table = []
		self.table_blacklist = []

	def cmd_table_new(self, sender, msg):
		self.table = self.channel_nicks(sender)
		random.shuffle(self.table)
		self.send_privmsg(sender, 'New table created.')

	def cmd_table_next(self, sender, msg):
		while len(self.table) > 0:
			victim = self.table.pop()
			if victim not in self.table_blacklist:
				self.send_privmsg(sender, victim)
				return
		self.send_privmsg(sender, 'No new members at the table.')

	def cmd_table_block(self, sender, msg):
		try:
			msg = msg.split(' ')[1]
		except IndexError:
			msg = ''
		if msg == '':
			self.send_privmsg(sender, 'Usage: tableblock <nick>')
 		else:
			if msg in self.table_blacklist:
				self.send_privmsg(sender, 'Nick already blocked from table')
			else:
				self.table_blacklist.append(msg)
				self.send_privmsg(sender, 'Blocked %s' % msg)

