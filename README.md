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
