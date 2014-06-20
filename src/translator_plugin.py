#
# XChat Translator Plugin.
#
# Copyright (C) 2014 Sergio Balbuena <sbalbp@gmail.com>.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

#!/usr/bin/env python

__module_name__ = "Message translator"
__module_version__ = "0.1.0"
__module_description__ = "Translates incoming messages using Apertium"
__module_author__ = "Sergio Balbuena <sbalbp@gmail.com>"

import xchat
import apertiumpluginutils.apertiumInterfaceAPY as iface
import apertiumpluginutils.apertiumFiles as files
try:
    import html.parser as HTMLParser
except:
	import HTMLParser

parser = HTMLParser.HTMLParser()
errors_on = True

def getFullChannel():
	fullChannel = ''
	list = xchat.get_list('channels')

	if(list):
		for i in list:
			fullChannel = fullChannel+i.channel+'.'

	return fullChannel

def notify(text, info = True):
	if(info or errors_on):
		xchat.command('GUI MSGBOX \"'+text+'\"')

def translate(text, user, direction):
	result = None

	if(direction != 'incoming' and direction != 'outgoing'):
		return None

	dictionary = files.getDictionary()[direction]

	for key in [user+'@'+getFullChannel(), getFullChannel(), 'default']:
		if(key in dictionary.keys()):
			result = iface.translate(text, dictionary[key]['source'], dictionary[key]['target'])
			break

	if(result != None):
		if(result['ok']):
			result = result['result']
		else:
			result = None
			notify(result['errorMsg'])

	return result

def apertium_apy_cb(word, word_eol, userdata):
	if(len(word) <= 1):
		notify('APY address:\n'+iface.getAPYAddress())
	else:
		if(iface.setAPYAddress(word[1]) == None):
			notify('Couldn\'t change APY address\nNo response from given server',info=False)
		else:
			files.setKey('apyAddress',word[1])
			notify('Successfully changed the APY address to '+word[1])

	return xchat.EAT_NONE

def apertium_pairs_cb(word, word_eol, userdata):
	result = iface.getAllPairs()
	it = 2

	if(result['ok']):
		resultText = 'Available pairs:\n'
		result = result['result']

		for pair in result:
			if(it == 0):
				it = 2
				resultText = resultText+pair[0]+' - '+pair[1]+'\n'
			else:
				resultText = resultText+(pair[0]+' - '+pair[1]).ljust(25)
				it = it-1

		notify(resultText)
	else:
		notify(result['errorMsg'],info=False)

	return xchat.EAT_NONE

def translate_cb(word, word_eol, userdata):
	translation = translate(word[1],word[0],'incoming')

	if(translation != None):
		print('\ntranslation:\n'+(parser.unescape(translation)).encode('utf-8')+'\n')

def unload_cb(userdata):
    files.save()

files.setFile('apertium_xchat_plugin_preferences.pkl')
files.read()
iface.setAPYAddress(files.getKey('apyAddress'))


xchat.hook_unload(unload_cb)
xchat.hook_command('apertium_apy', apertium_apy_cb, help='/apertium_apy <address>\nChanges the apy address where translation requests are sent. If no arguments are passed, it just shows the address.')
xchat.hook_command('apertium_pairs', apertium_pairs_cb, help='/apertium_pairs\nShows all the available Apertium language pairs that can be used.')

xchat.hook_print("Channel Message", translate_cb)
