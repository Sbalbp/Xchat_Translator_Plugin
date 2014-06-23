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
import sys

pyVersion = sys.version_info[0]

errors_on = True

def notify(text, info = True):
	if(info or errors_on):
		xchat.command('GUI MSGBOX \"'+text+'\"')

def userBlocked(user):
	blocked = files.getKey('blocked')

	if(blocked != None and getFullChannel() in blocked.keys() and user in blocked[getFullChannel()]):
		return True

	return False

def getFullChannel():
	fullChannel = ''
	list = xchat.get_list('channels')

	if(list):
		for i in list:
			fullChannel = fullChannel+i.channel+'.'

	return fullChannel

def parseBindArguments(args):
	numArgs = len(args)

	if(numArgs < 3):
		notify('Not enough arguments provided', info=False)
		return False

	if(numArgs > 3):
		user = 1
	else:
		user = 0

	if(not args[0] in ['incoming','outgoing']):
		notify('First argument must be either \'incoming\' or \'outgoing\'', info=False)
		return False
	else:
		isPair = iface.pairExists(args[1+user],args[2+user])
		if(isPair['ok']):
			if(not isPair['result']):
				notify('Pair '+args[1+user]+' - '+args[2+user]+' does not exist', info=False)
				return False
		else:
			notify(isPair['errorMsg'], info=False)
			return False

	return True

def translate(text, user, direction):
	result = None

	if(userBlocked(user)):
		return None

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

def apertium_bind_cb(word, word_eol, userdata):
	if(parseBindArguments(word[1:])):
		if(len(word) > 4):
			user = 1
		else:
			user = 0

		dictionary = files.getDictionary()
		newDict = {}
		newDict['source'] = word[2+user]
		newDict['target'] = word[3+user]

		if(user == 1):
			dictionary[word[1]][word[2]+'@'+getFullChannel()]=newDict
		else:
			dictionary[word[1]][getFullChannel()]=newDict

		files.setDictionary(dictionary)
		if(user == 1):
			notify('Successfully set '+word[3]+' - '+word[4]+' as the '+word[1]+' language pair for '+word[2]+'@'+getFullChannel())
		else:
			notify('Successfully set '+word[2]+' - '+word[3]+' as the '+word[1]+' language pair for '+getFullChannel())

def apertium_default_cb(word, word_eol, userdata):
	if(parseBindArguments(word[1:])):
		dictionary = files.getDictionary()
		newDict = {}
		newDict['source'] = word[2]
		newDict['target'] = word[3]
		dictionary[word[1]]['default']=newDict

		files.setDictionary(dictionary)

def apertium_block_cb(word, word_eol, userdata):
	if(len(word) < 2):
		notify('Not enough arguments provided', info=False)
		return

	blocked = files.getKey('blocked')

	if(blocked == None):
		blocked = {}

	if(not(getFullChannel() in blocked.keys())):
		blocked[getFullChannel()] = []
	blocked[getFullChannel()].append(word[1])

	files.setKey('blocked',blocked)


def translate_cb(word, word_eol, userdata):
	translation = translate(word[1],word[0],'incoming')

	if(translation != None):
		if(pyVersion >= 3):
			print('\ntranslation:\n'+(translation.decode('utf-8'))+'\n')
		else:
			print('\ntranslation:\n'+translation+'\n')

def unload_cb(userdata):
    files.save()

files.setFile('apertium_xchat_plugin_preferences.pkl')
files.read()
iface.setAPYAddress(files.getKey('apyAddress'))

xchat.hook_unload(unload_cb)
xchat.hook_command('apertium_apy', apertium_apy_cb, help='/apertium_apy <address>\nChanges the apy address where translation requests are sent. If no arguments are passed, it just shows the address.')
xchat.hook_command('apertium_pairs', apertium_pairs_cb, help='/apertium_pairs\nShows all the available Apertium language pairs that can be used.')
xchat.hook_command('apertium_bind', apertium_bind_cb, help='/apertium_bind <direction> <user> <source> <target>\nBinds a given language pair to a user or channel.\ndirection must be either \'incoming\' or \'outgoing\'.\nuser (optional) is the name of the user whose messages are translated using the given language pair. If omitted, the language pair is bound to the channel itself.\nsource and target are the codes for the source and target languages from the language pair, respectively.')
xchat.hook_command('apertium_default', apertium_default_cb, help='/apertium_default <direction> <source> <target>\nSets a given language pair as default when no bindings exist for users or channels.\ndirection must be either \'incoming\' or \'outgoing\'.\nsource and target are the codes for the source and target languages from the language pair, respectively.')
xchat.hook_command('apertium_block', apertium_block_cb, help='/apertium_block <user>\nBlocks the given user so that their messages are not translated in the current channel.')

xchat.hook_print("Channel Message", translate_cb)
