XChat Translator Plugin
=======================

XChat plugin to translate incoming and outgoing messages with the help of the software developed by the [Apertium](http://www.apertium.org/ "Apertium") project team.

This plugin is currently still not finished and, therefore, some things are still subject to change.

###What it does

When loaded, this plugin keeps track of the user's language preferences for different users and channels (both incoming and outgoing messages). If the user has set the language pair eng-spa (English -> Spanish) for incoming messages from user1@channel1, then the plugin will attempt to tranlate all incoming messages from user1 in channel1 to Spanish (assuming they will be in English).

There are 3 kinds of language pair bindings:

* **user binding.** Only available for incoming messages. Binds a language pair to a specific username, so that messages from that user are translated according to the associated pair. This binding ignores channel names, meaning that the translating will be done in every channel a user with the username that was associated with the language pair speaks.

* **channel binding.** Binds a language pair to a channel, so that all the messages to/from that channel are translated accordingly.

* **default binding.** If set, the language pair set to default will be user to translate any text that does not fall under any of the previous binding categories.

In case there exist different kinds of bindings that could be user to translate a message, the order of priority (from most to least) is: user, channel, default. This means that if a user who has an associated language pair sends a message in a channel that also has an associated language pair, the message will be translated using the the pair associated to the user. Any users who don't have language pair bindings will have their messages translated using the channel associated language pair.

All bindings are stored to a preferences file and are, therefore, persistent across different XChat sessions.

The translating is done by an [Apertium-apy](http://wiki.apertium.org/wiki/Apy "Apertium-apy") that may run locally or on a remote location (its address can be set from within the plugin).

The plugin is able to use several APY instances, as it stores an ordered APY list. The first APY in the list takes priority when the plugin need to make a request to an APY. If the first APY is unreachable or unable to give an answer, the plugin will attempt to make the same request to the second APY in the list, and so on.

###Requirements

* **Python.**
* **(Optional)[Apertium-apy](http://wiki.apertium.org/wiki/Apy "Apertium-apy").** Needed if you intend to run your own apy in your machine.

###Installing

For this plugin to work, it is first necessary to install the Python module included in this repository under the 'Apertium_Plugin_Utils' folder, as it is used by the plugin.

If you have just cloned this repository you will need to first update the submodule:

* ./updateSub.sh

this will always fetch the latest version of the Python module, so it can be used to keep it up to date.

Now that you have the Python module, you might want to install it. First enter the submodule directory

* cd Apertium_Plugin_Utils

and install the module.

You can opt for a global installation with

* sudo python setup.py install

Alternatively, you can install the module to a chosen directory (prefix installation). To do this run the following

* python setup.py install --prefix=route/to/module

don't forget to use your own custom route to install the module there. After that, a new directory tree containing the Python module will be created. You still need to tell Python to look for the module in this new directory, so you will have to add its route to your PYTHONPATH environment variable:

* export PYTHONPATH=route/to/module/lib/pythonX.Y/site-packages:$PYTHONPATH

don't forget to add the whole route up to the site-packages directory (included). You can also edit your .profile/.bash_profile/.login file to add the above line so that the route is added to the PYTHONPATH automatically when you log in (therefore, you won't have to manually edit it every time).

You can refer to this [documentation](https://docs.python.org/2/install/ "documentation") for other different installing alternatives.

###Loading the plugin

To load the plugin with XChat go to XChat -> Load script or plugin and select the .py file that is included inside the src folder. Alternatively, you can also use the /load *route* command in XChat to load the plugin (for a non-absolute route, XChat current directory is by default *home*).

###Plugin commands

The following commands can be used in XChat when the plugin is loaded:

* **/apertium_apy _position_ _address_** Inserts an APY *address* at the given *position* of the APY list. If no arguments are passed, it just shows the list of addresses. If the *address* argument is omitted, the address at the given *position* is shown.

	For example, if the APY list looks like [address1, address2, address3] and we issue the command '/apertium_apy 1 http://localhost 2737', it will insert the address http://localhost:2737 to the APY list in the position number 1, pushing back ay other APY, which results in the following APY list: [address1, http://localhost:2737, address2, address3]. This means that the new address wil take priority over address2 and address3 when issuing a command that makes a request to an APY, but it will always be asked after address1.

	The default list only address is http://localhost:2737. The address http://apy.projectjj.com can be added to the list. This address, however, is not guaranteed to work 100% of the times, as it is still in test stage.

* **/apertium_removeapy _position_** Removes athe APY at the given *position* from the APY list. If no arguments are passed, all the APYs are removed.
* **/apertium_pairs** Ask the apy which language pairs are available and shows them.
* **/apertium_check _user_** Show the language pair bindings for the given *user*. If the *user* argument is omitted, show the default and current channel language pair bindings.
* **/apertium_bind _direction_ _user_ _source_ _target_** Sets a language pair for the given *user*. *direction* must be either 'incoming' (for incoming messages) or 'outgoing' (for messages sent). *source* and *target* are the source and target languages of the language pair to be set, respectively. If no *user* is provided, the language pair is instead bound to the current channel.

	It's worth noting that 'outgoing' messages will only be translated if a language pair has been assigned to either 'default' (with apertium_default outgoing) or the channel (for example, the language pair eng-spa to translate your messages in english to spanish in a spanish channel). This means you can't bind an outgoing language pair to a user.

* **/apertium_unbind _user_** Unbinds the langugage pair associated to a user or channel. *user* (optional) is the name of the user whose associated language pair is to be unbound. If omitted, the language pair is unbound from the channel itself.
* **/apertium_default _direction_ _source_ _target_** Sets the language pair to be used to translate messages when there is no language pair for the user that sent the message nor the channel it was sent on. *direction* must be either 'incoming' (for incoming messages) or 'outgoing' (for messages sent). *source* and *target* are the source and target languages of the language pair to be set, respectively.
* **/apertium_block _user_** Blocks a given *user* so that their messages are not translated.
* **/apertium_unblock _user_** Unblocks a given blocked *user* to have their messages translated again.
* **/apertium_display _displayMode_** Selects how translated messages are displayed. _displayMode_ must be 'both' (displays the original message and its translation), 'replace' (only displays the translation) or 'compressed' (displays both the original message and its translation in a compressed 2-line way). If no argument is passed, the current display mode is shown.
* **/apertium_infodisplay _infoDisplayMode_** Selects how information should be displayed. *infoDisplayMode* must be 'dialog' (shows a dialog box with the information), 'print' (prints the information in the xchat history) or 'none' (information is not displayed).
