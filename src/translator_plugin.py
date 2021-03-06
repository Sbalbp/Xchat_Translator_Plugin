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
import sys
import os

sys.path.append(os.environ.get('PYTHONPATH'))

import apertiumpluginutils.apertiumInterfaceAPY as iface
import apertiumpluginutils.apertiumFiles as files

pyVersion = sys.version_info[0]

printMode = 'print'

displayMode = 'compressed'

custom_emit = False

def notify(text, info = True):
	if(info):
		if(printMode == 'dialog'):
			xchat.command('GUI MSGBOX \"'+text+'\"')
		elif(printMode == 'print'):
			print('Translator plugin information:\n'+text)
	else:
		if(printMode == 'dialog'):
			xchat.command('GUI MSGBOX \"'+text+'\"')
		elif(printMode == 'print'):
			print('Translator plugin error: '+text)

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

	if(user == 1 and args[0] == 'outgoing'):
		notify('Cannot bind a language pair to outgoing messages for a particular user', info=False)
		return False

	return True

def translate(text, user, direction):
	result = None
	source = None
	target = None

	if(userBlocked(user)):
		return None

	if(direction != 'incoming' and direction != 'outgoing'):
		return None

	dictionary = files.getDictionary()[direction]

	for key in [user, getFullChannel(), 'default']:
		if(key in dictionary.keys()):
			result = iface.translate(text, dictionary[key]['source'], dictionary[key]['target'])
			source = dictionary[key]['source']
			target = dictionary[key]['target']
			break

	if(result != None):
		if(result['ok']):
			result = result['result']
		else:
			notify(result['errorMsg'], info=False)
			result = None

	return [result, [source, target]]

def apertium_apy_cb(word, word_eol, userdata):
	if(len(word) <= 1):
		text = 'APY addresses:\n'
		for i in range(iface.getAPYListSize()):
			text = text+'\n'+iface.getAPYAddress(i)
		notify(text)
	elif(len(word) == 2):
		if(iface.getAPYListSize() > int(word[1])):
			notify('APY address number '+word[1]+':\n\n'+iface.getAPYAddress(int(word[1])))
		else:
			notify('Error: Only '+str(iface.getAPYListSize())+' APY addresses available',info=False)
	else:
		if(iface.setAPYAddress(word[2],order=int(word[1])) == None):
			notify('Couldn\'t change APY address\nNo response from given server',info=False)
		else:
			files.setKey('apyAddress',iface.getAPYList())
			notify('Successfully added the APY address: '+word[2])

	return xchat.EAT_ALL

def apertium_removeapy_cb(word, word_eol, userdata):
	if(len(word) <= 1):
		iface.setAPYList([])
		files.setKey('apyAddress',[])
		notify('All APY addresses removed')
	else:
		if(iface.removeAPYAddress(int(word[1]))):
			files.setKey('apyAddress',iface.getAPYList())
			notify('Successfully removed APY address '+word[1])
		else:
			notify('Couldn\'t remove APY address '+word[1],info=False)

	return xchat.EAT_ALL

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

	return xchat.EAT_ALL

def apertium_check_cb(word, word_eol, userdata):
	incoming = files.getKey('incoming')
	outgoing = files.getKey('outgoing')
	channel = getFullChannel()
	text = ''

	if(len(word) < 2):
		text = text+'Default language settings:\n\n  incoming: '
		if 'default' in incoming.keys():
			text = text+incoming['default']['source']+' - '+incoming['default']['target']+'\n'
		else:
			text = text+'None\n'

		text = text+'  outgoing: '
		if 'default' in outgoing.keys():
			text = text+outgoing['default']['source']+' - '+outgoing['default']['target']+'\n\n'
		else:
			text = text+'None\n\n'

		text = text+'Language settings for this channel:\n\n  incoming: '
		if channel in incoming.keys():
			text = text+incoming[channel]['source']+' - '+incoming[channel]['target']+'\n'
		else:
			text = text+'None\n'

		text = text+'  outgoing: '
		if channel in outgoing.keys():
			text = text+outgoing[channel]['source']+' - '+outgoing[channel]['target']+''
		else:
			text = text+'None'
	else:
		text = text+'Language settings for user '+word[1]+':\n\n incoming: '
		if word[1] in incoming.keys():
			text = text+incoming[word[1]]['source']+' - '+incoming[word[1]]['target']+'\n'
		else:
			text = text+'None\n'

	notify(text)

	return xchat.EAT_ALL

def apertium_bind_cb(word, word_eol, userdata):
	if(parseBindArguments(word[1:])):
		if(len(word) > 4):
			user = 1
			username = word[2]
		else:
			user = 0
			username = getFullChannel()

		if(files.setLangPair(word[1],username,word[2+user],word[3+user])):
			notify('Successfully set '+word[2+user]+' - '+word[3+user]+' as the '+word[1]+' language pair for '+username)
		else:
			notify('An error occurred while binding the language pair')

	return xchat.EAT_ALL

def apertium_unbind_cb(word, word_eol, userdata):
	if(len(word) > 1):
		key = word[1]
	else:
		key = getFullChannel()

	success = False

	if(files.unsetLangPair('incoming',key)):
		success = True
	if(files.unsetLangPair('outgoing',key)):
		success = True

	if(success):
		notify('Successfully removed bindings for '+key)

	return xchat.EAT_ALL

def apertium_default_cb(word, word_eol, userdata):
	if(parseBindArguments(word[1:])):
		if(files.setLangPair(word[1],'default',word[2],word[3])):
			notify('Successfully set '+word[2]+' - '+word[3]+' as the '+word[1]+' default language pair')
		else:
			notify('An error occurred while binding the language pair')

	return xchat.EAT_ALL

def apertium_block_cb(word, word_eol, userdata):
	if(len(word) < 2):
		notify('Not enough arguments provided', info=False)
		return xchat.EAT_ALL

	blocked = files.getKey('blocked')

	if(blocked == None):
		blocked = {}

	if(not(getFullChannel() in blocked.keys())):
		blocked[getFullChannel()] = []
	blocked[getFullChannel()].append(word[1])

	files.setKey('blocked',blocked)

	return xchat.EAT_ALL

def apertium_unblock_cb(word, word_eol, userdata):
	if(len(word) < 2):
		notify('Not enough arguments provided', info=False)
		return xchat.EAT_ALL

	if(userBlocked(word[1])):
		blocked = files.getKey('blocked')
		blocked[getFullChannel()].remove(word[1])
		files.setKey('blocked',blocked)

	return xchat.EAT_ALL

def apertium_display_cb(word, word_eol, userdata):
	global displayMode

	if(len(word) < 2):
		text = ''
		if(displayMode == 'both'):
			text = '"Both"\nBoth the original message and its translation are displayed'
		elif(displayMode == 'replace'):
			text = '"Replace"\nOnly the translated message is displayed'
		elif(displayMode == 'compressed'):
			text = '"Compressed"\nBoth the original message and its translation are displayed in a compressed way'
		notify('Current display mode:\n'+text, info=True)
		return xchat.EAT_ALL

	if(not word[1] in ['both','replace','compressed']):
		notify('Display mode argument must be \'both\', \'replace\' or \'compressed\'', info=False)
		return xchat.EAT_ALL

	displayMode = word[1]
	files.setKey('displayMode',displayMode)
	notify('Successfully set display mode to '+displayMode)

	return xchat.EAT_ALL

def apertium_errordisplay_cb(word, word_eol, userdata):
	global printMode

	if(len(word) < 2):
		notify('Not enough arguments provided', info=False)
		return xchat.EAT_ALL

	if(not word[1] in ['dialog','print','none']):
		notify('Display mode argument must be \'dialog\', \'print\' or \'none\'', info=False)
		return xchat.EAT_ALL

	printMode = word[1]

	return xchat.EAT_ALL

def translate_cm_cb(word, word_eol, userdata):
	global custom_emit

	if(custom_emit):
		return xchat.EAT_NONE

	result = translate(word[1],word[0],'incoming')
	translation = result[0]

	if(translation != None):
		if(pyVersion >= 3):
			translation = translation.decode('utf-8')

		if(displayMode == 'both'):
			text = '--- Original ---\n'+word[1]+'\n--- Translation ---\n'+translation
		elif(displayMode == 'replace'):
			text = translation
		elif(displayMode == 'compressed'):
			text = word[1]+'\napertium '+result[1][0]+'-'+result[1][1]+': '+translation
		else:
			text = word[1]

		custom_emit = True
		xchat.emit_print('Channel Message', word[0], text.replace('\t',' '))
		custom_emit = False

	return xchat.EAT_ALL

def translate_ym_cb(word, word_eol, userdata):
	result = translate(word[1],'default','outgoing')
	translation = result[0]

	if(translation != None):
		text = translation
	else:
		text = word[1]

	xchat.command("msg #channel %s" % text.replace('\t',' '))

	return xchat.EAT_ALL

def unload_cb(userdata):
    files.save()

files.setFile('apertium_xchat_plugin_preferences.pkl')
files.read()

iface.setAPYList(files.getKey('apyAddress'))

if(files.getKey('displayMode') != None):
	displayMode = files.getKey('displayMode')
else:
	displayMode = 'compressed'
	files.setKey('displayMode',displayMode)

xchat.hook_unload(unload_cb)
xchat.hook_command('apertium_apy', apertium_apy_cb, help='/apertium_apy <position> <address>\nAdds a new APY address in a given position of the APY addresses list.\n If no arguments are passed, it just shows the list of addresses. If only the position argument is passed, it shows the APY address at that position.')
xchat.hook_command('apertium_removeapy', apertium_removeapy_cb, help='/apertium_removeapy <position>\nRemoves the APY address at the given position from the APY list.\nIf no arguments are given, all the APYs are removed.')
xchat.hook_command('apertium_pairs', apertium_pairs_cb, help='/apertium_pairs\nShows all the available Apertium language pairs that can be used.')
xchat.hook_command('apertium_check', apertium_check_cb, help='/apertium_check <user>\nShows the current language pair bindings for the given user.\nIf no argument is passed, shows the default and current channel language pair bindings.')
xchat.hook_command('apertium_bind', apertium_bind_cb, help='/apertium_bind <direction> <user> <source> <target>\nBinds a given language pair to a user or channel.\ndirection must be either \'incoming\' or \'outgoing\'.\nuser (optional) is the name of the user whose messages are translated using the given language pair. If omitted, the language pair is bound to the channel itself.\nsource and target are the codes for the source and target languages from the language pair, respectively. \'outgoing\' messages will only be translated if a language pair has been assigned to either \'default\' (with apertium_default outgoing) or the channel (for example, the language pair eng-spa to translate your messages in english to spanish in a spanish channel). This means you can\'t bind an outgoing language pair to a user.')
xchat.hook_command('apertium_unbind', apertium_unbind_cb, help='/apertium_unbind <user>\nUnbinds the langugage pair associated to a user or channel.\nuser (optional) is the name of the user whose language pairs are to be unbound. If omitted, the language pairs are unbound from the channel itself.')
xchat.hook_command('apertium_default', apertium_default_cb, help='/apertium_default <direction> <source> <target>\nSets a given language pair as default when no bindings exist for users or channels.\ndirection must be either \'incoming\' or \'outgoing\'.\nsource and target are the codes for the source and target languages from the language pair, respectively.')
xchat.hook_command('apertium_block', apertium_block_cb, help='/apertium_block <user>\nBlocks the given user so that their messages are not translated in the current channel.')
xchat.hook_command('apertium_unblock', apertium_unblock_cb, help='/apertium_unblock <user>\nUnblocks the given user so that their messages are translated again in the current channel.')
xchat.hook_command('apertium_display', apertium_display_cb, help='/apertium_display <display_mode>\nSelects how translated messages should be displayed.\n display_mode must be one of the following:\n\'both\' Displays both the original message and its translation.\n\'replace\' Only the translated message is displayed.\n\'compressed\' Shows both the original text and its translation, in a compressed 2-line way.')
xchat.hook_command('apertium_infodisplay', apertium_errordisplay_cb, help='/apertium_infodisplay <info_display_mode>\nSelects how plugin information should be displayed.\n info_display_mode must be one of the following:\n\'dialog\' Shows a dialog box with the information.\n\'print\' Prints the information in the xchat history.\n\'none\' Information is not displayed')

xchat.hook_print('Channel Message', translate_cm_cb)
xchat.hook_print('Your Message', translate_ym_cb)
