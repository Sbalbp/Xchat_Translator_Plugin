XChat Translator Plugin
=======================

XChat plugin to translate incoming and outgoing messages with the help of the software developed by the [Apertium](http://www.apertium.org/ "Apertium") project team.

This plugin is currently still not finished and, therefore, some things are still subject to change.

###What it does

When loaded, this plugin keeps track of the user's language preferences for different users and channels (both incoming and outgoing messages). If the user has set the language pair eng-spa (English -> Spanish) for incoming messages from user1@channel1, then the plugin will attempt to tranlate all incoming messages from user1 in channel1 to Spanish (assuming they will be in English).

The translating is done by an [Apertium-apy](http://wiki.apertium.org/wiki/Apy "Apertium-apy") that may run locally or on a remote location (its address can be set from within the plugin).

###Requirements

* **Python.**
* **(Optional)[Apertium-apy](http://wiki.apertium.org/wiki/Apy "Apertium-apy").** Needed if you intend to run your own apy in your machine.

###Installing

For this plugin to work, it is first necessary to install the python module included in this repository 'ApertiumPluginUtils', as it is used by the plugin:

* python setup.py install

###Loading the plugin

To load the plugin with XChat go to XChat -> Load script or plugin and select the .py file that is included inside the src folder. Alternatively, you can also use the /load *route* command in XChat to load the plugin.

###Plugin commands

THe following commands can be used in XChat when the plugin is loaded:

* **/apertium_apy _address_** Changes the apy address where translation requests are sent. If no arguments are passed, it just shows the address. The default address is http://localhost:2737.
* **/apertium_pairs** Ask the apy which language pairs are available and shows them.
* **/apertium_bind _direction_ _user_ _source_ _target_** Sets a language pair for the given *user*. *direction* must be either 'incoming' (for incoming messages) or 'outgoing' (for messages sent). *source* and *target* are the source and target languages of the language pair to be set, respectively. If no *user* is provided, the language pair is instead bound to the current channel.
* **/apertium_unbind _user_** Unbinds the langugage pair associated to a user or channel. *user* (optional) is the name of the user whose associated language pair is to be unbound. If omitted, the language pair is unbound from the channel itself.
* **/apertium_default _direction_ _source_ _target_** Sets the language pair to be used to translate messages when there is no language pair for the user that sent the message nor the channel it was sent on. *direction* must be either 'incoming' (for incoming messages) or 'outgoing' (for messages sent). *source* and *target* are the source and target languages of the language pair to be set, respectively.
* **/apertium_block _user_** Blocks a given *user* so that their messages are not translated.
* **/apertium_unblock _user_** Unblocks a given blocked *user* to have their messages translated again.
* **/apertium_display _displayMode_** Selects how translated messages are displayed. _displayMode_ must be 'both' (displays the original message and its translation) or 'replace' (only displays the translation).
* **/apertium_errordisplay _errorDisplayMode_** Selects how errors should be displayed. *errorDisplayMode* must be 'dialog' (shows a dialog box with the error), 'print' (prints the error in the xchat history) or 'none' (errors are not displayed).
