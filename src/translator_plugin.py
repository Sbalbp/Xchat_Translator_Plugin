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

errors_on = True

def notify(text, info = True):
	if(info or errors_on):
		xchat.command("GUI MSGBOX \""+text+"\"")

def apertium_pairs_cb(word, word_eol, userdata):
	result = iface.getAllPairs()

	if(result['ok']):
		resultText = 'Available pairs:\n'
		result = result['result']

		for pair in result:
			resultText = resultText+"\n"+pair[0]+" - "+pair[1]

		notify(resultText)
	else:
		notify(result['errorMsg'],info=False)

	return xchat.EAT_NONE

def unload_cb(userdata):
    files.save()

files.setFile("apertium_xchat_plugin_preferences.pkl")
files.read()

xchat.hook_unload(unload_cb)
xchat.hook_command("apertium_pairs", apertium_pairs_cb, help='/apertium_pairs\nShows all the available Apertium language pairs that can be used.')
