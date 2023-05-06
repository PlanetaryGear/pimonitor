
# keys for sending data about new units in the response to the info packet request
kInfoName				= 'name'
kInfoMDNSName			= 'mdnsname'
kInfoSSID				= 'ssid'
kInfoPassword			= 'password'
kInfoWebUser			= 'webuser'
kInfoWebPassword		= 'webpassword'
kInfoStaticIp			= 'staticip'
kInfoRouterIp			= 'routerip'
kInfoSubnet				= 'subnet'
kInfoInterval			= 'interval'
kInfoSendVCC			= 'sendvcc'
kInfoSendRSSI			= 'sendrssi'
kInfoNetworkType		= 'networktype'
kInfoNetworkTypeDHCP	= 'dhcp'
kInfoNetworkTypeStatic	= 'static'
kInfoUnits				= 'units'			# optional: new for generic device so that it can send it's own unit info
kInfoTag				= 'tag'				# required in the units entry must be a device type already in 
kInfoAddress			= 'address'			# requires in the units entry
kInfoOnLabel			= 'onlabel'			# optional
kInfoOffLabel			= 'offlabel'		# optional
kInfoIgnoreClicks		= 'ignoreclicks'	# optional
kInfoReceiveOnly		= 'receiveonly'		# optional
kInfoNoLog 				= 'nolog'			# optional send with units you wish to be created with the dontLogNewValueReceptions flag set
kInfoAllowColor			= 'allowcolor'		# optional can come from tag info if defined
kInfoAllowColorTemp		= 'allowcolortemp'	# optional can come from tag info if defined
kInfoDimmable			= 'dimmable'		# optional can come from tag info if defined
kInfoSimulated			= 'simulated'		# optional can come from tag info if defined
kInfoColorTempMin		= 'colortempmin'	# optional if color temp capable defaults to 2700
kInfoColorTempMax		= 'colortempmax'	# optional if color temp capable defaults to 6500
kInfoSuffix				= 'suffix'			# optional can come from tag info if defined
kInfoValue				= 'value'			# optional, if the new unit should have a default value then send it here
kInfoDefaultLabel		= 'label'			# optional sets the default display label separate from the on/off labels



#
#  keys for getting info from the info.json feedback
#
xtKey							= 'key'

# log colors for the second parameter to the XTension.writeLog command
# defaults to blue which is normal for most informational logging
# you can also pass instead a 6 character string of an HTML color for custom color logging

xtLogBlack						= '1'
xtLogBlue						= '2'
xtLogGreen						= '3'
xtLogRed						= '4'

#
#  keys into the dictionary that is a command sent or received from XTension to update
#  the unit in XTension or from XTension to tell you to send the proper command to a device
#

#  COMMAND
xtKeyCommand 		 			= 'mcmd'
	# the command key will be included in every packet sent from XTension and must
	# be included in any command you send up to XTension. If you wish to only update
	# one of the values below that are normally sent along with a unit value change
	# event you can use the NoOp command and then include whatever else you need to.

xtCommandBlink 				= 'blink'
	# Received from XTension.
	# will include xtKeyAddress, xtKeyTag and xtKeyValue
	# BLINK received from the blink script command
	# in the xtKeyValue field will be whatever numerical or string value
	# is passed in the "rate" parameter. Of the verb
	# http://machomeautomation.com/doku.php/dictionary/unitcontrol/blink

xtCommandGetUnitProperty	= 'GetUnitProperty'
	# sent to XTension. 
	# requires xtKeyAddress, xtKeyTag and xtKeyName
	# include the name of the unit property you wish to retrieve 
	# in the xtKeyName field. Only text and numerical values can be
	# handled in this way. XTension will respond asynchronously with an
	# xtCommandSetUnitProperty command to your command handler with the 
	# data included.

xtCommandExecuteGlobalScript = 'ExeGlblScpt'
	# sent from XTension when one of the items you added to the scripts menu is executed
	# either by selecting the menu item or via a scheduled event or another script via the
	# execute script command. You must have already sent that script via the xtCommandSetMyUnits
	# with a script portion included along with any units. 

xtCommandJSONRequest		= 'JSON'
	# sent to XTension.
	# requires xtKeyAddress, xtKeyTag
	# optional keys: xtKeyData, xtKeyJSONData, xtKeyUniqueID
	# a way to send JSON or other html form data to a special handler in a units ON script
	# I use this with the Vera support so that a user can get the JSON record
	# received for a unit in total and extract any extra data from it that they 
	# might wish to get out for devices I don't support automatically yet.
	# if the request includes GET or POST standard URL encoded values include them
	# as a string in the xtKeyData field. If there is JSON data include it in the
	# xtKeyJSONData field. The 2 datas will be turned into AppleScript records 
	# and passed to the "on jsonrequest( htmlData, jsonData)" handler in the units ON script
	# and there any action that they wish can be taken based on the data.
	# if you include a URL=/some/link/something parameter in the html form data then that
	# will also be passed to the script. If it ends in "/data" then the unit will respond with
	# all of the units internal settings and values converted to JSON and send a command with 
	# the same address and tag but with that keyData of JSON data back to your script.
	# The user in the script will also have the option of returning a value in reply to 
	# the request. If you wish to receive a reply from this call you must include a
	# unique ID for the request in the xtKeyUniqueID field. That can be any unique ID style
	# string. It will be included in the reply from XTension so that you can match it with
	# a request or an incoming connection. The reply command will have the same command key
	# and will include the same xtKeyUniqueID. The reply data will be included with the 
	# xtKeyData parameter. Additionally an HTML return code may be specified in xtKeyCode and
	# a content-type may be specified in the xtKeyContentType field. These responses are sent
	# asynchronously and no reply is guaranteed as the script may choose not to reply or
	# may suffer an error condition rather than returning anything.

xtCommandMessage			= 'MESS'
	# received from XTension
	# will contain xtKeyData
	# this comes from the Send Remote Message verb and will contain whatever text 
	# they included in the default parameter of the verb.
	# currently used to display messages on the front screens of thermostats that 
	# support such things.

xtCommandNewUnit			= 'NewU'
	# sent to XTension
	# requires xtkeyAddress, xtKeyTag and many others, see specific instructions for 
	# creating new units. If you can get the necessary units and their setup from your
	# device then you should create and send these commands whenever you are connected
	# if the units don't yet exist in XTension they will be created and added to whatever
	# list you specify saving the user from having to create them all manually and 
	# get them properly setup. If they already exist then they will be conformed to the
	# new settings to keep them updated. This has too many options to document here.

xtCommandNoOp				= 'NoOp'
	# sent to XTension
	# if you wish to send a key that rides along with another command but do not wish to
	# command a unit you can include the NoOp command.
	# for example if you wish to update the battery level for a device but
	# do not have a new value to send along with the change in battery status you 
	# can create a command with the xtKeyAddress and xtKeyTag and xtBatteryLevel
	# keys but with the NoOp command so that the unit will stil process the other included keys.
	# a command is always required in any packet. 


xtCommandOff				= 'OFF'
	# sent to XTension and received from XTension
	# requires xtKeyAddress and xtKeyTag
	# if received from XTension  you should take whatever action necessary to turn off the
	# addressed unit. If you receive a status update for a device for OFF you can create the
	# command and send it up to XTension. The addressed unit will then turn itself off
	# and run it's OFF script.


xtCommandOn					= 'ON'
	# sent to XTension and received from XTension
	# requires xtKeyAddress and xtKeyTag
	# may contain xtKeyValue
	# if received from XTension you should take whatever action necessary to turn on the
	# addressed unit. If the unit is configured as smart or simulated the command will
	# also include the xtKeyValue field which is the preset level the unit should return to.

xtCommandPing				= 'ping'
	# received from XTension 
	# if XTension hasn't heard from you in a while it may send a ping command just to make sure you're
	# still alive and able to communicate with your devices. If you receive a ping you should do whatever
	# is necessary to make sure you're still connected and operating properly and then respond
	# with an xtCommandPingResponse command. If you miss 2 consecutive ping requests the interface
	# will be forced to quit and restarted.

xtCommandPingResponse		= 'PSrp'
	# sent to XTension in response to the xtCommandPing request after you verify that
	# you're still able to communicate with your device. If you don't reply after 2 ping requests in a row
	# you will be force quit and restarted.

xtCommandQuery				= 'Qery'
	# received from XTension in response to the query verb for a unit
	# will contain the xtKeyAddress and xtKeyTag fields
	# You are being asked to perform a query out to the device being controlled for 
	# updating the value. When you receive a new value you should generate a normal
	# update command to XTension with the xtKeyUpdateOnly set to true.
	# queries are async, XTension will not wait for you to reply before more commands may be sent.

xtCommandReboot				= 'REBOOT'
	# received from XTension in response to the Reset Controller verb. If possible you should
	# ask the device or hub to reboot itself. You may also reset any default parameters that are
	# available in the device to reset it to some known state. Dont go so far as to reset the device
	# to factory defaults or anything such as that. This is a something is setup wrong or my device
	# may not be functioning correctly and needs a reboot command, not a factory reload command.

xtCommandRemoveData			= 'rXML'
xtCommandRemoveXMLData		= xtCommandRemoveData	# deprecated use xtCommandRemoveData

	# sent to XTension
	# requires xtKeyAddress, xtKeyTag and xtKeyName
	# removes the xtKeyName'd value from the units dictionary. You should use this only for 
	# values that you have added to the units key value pairs either via the dynamic interface
	# keys or with the xtCommandRemoveData command. You must also make sure that you are using a
	# namespace reserved for your plugin. ALWAYS use PLUGINID_nameOfValue or some other method to
	# distinguish your keys from the built in keys in XTension. XTension reserves the use of all
	# key names that do not begin with a plugin tag and underscore.
	# no attempt is made to validate the name is not reserved for XTension before it is removed
	# so you may render the unit unusable if you delete an important key.
	
xtCommandSendRawData		= 'sendRaw'
	# received from XTension response to the send data verb
	# This is usually a request to send the passed string directly to the device or down the port or
	# whatever makes sense. For some devices implementing this will not make any sense.
	# The data will be passed with the key xtKeyData

xtCommandSetDescription		= 'SetDesc'
	# sent to XTension
	# requires xtKeyAddress, xtKeyTag and xtKeyData
	# send this to XTension to set the "description" field of the unit to a string of your choosing.
	# the new description must be included in the xtKeyData field.
	# note that this will overwrite anything that the used has manually placed in this field.
	# Good for displaying text data about the value. For example a barameter sensor may wish 
	# to send a weather forecast to the description of the unit that holds the numerical value.

xtCommandSetUnitOfMeasure	= 'SetUnitOfMeasure'
	# sent to XTension
	# requires xtKeyAddress, xtKeyTag and xtKeyData
	# send this to change the value suffix of the unit to a new value. For example if the 
	# configuration of a temperature sensor has changed from F to C you may wish to send this
	# command to change the unit of measure to "C" so that will display in all interfaces after the value.
	# the new value will be included in the xtKeyData field.
	# this will overwrite any value that the user has placed in the value suffix field.

xtCommandSetUnitProperty 	= 'setUnitProperty'
	# sent to XTension and received from XTension in response to a xtCommandGetUnitProperty command
	# requires xtKeyAddress, xtKeyTag, xtKeyName, xtKeyData
	# sets a unit property given the name xtKeyName and the data xtKeydata both fields need to be
	# strings, or string representations of numbers. The key strings should be properly UTF8 encoded
	# this command is also returned to you with the selected data if you have sent an
	# xtCommandGetunitProperty command up to XTension. 

xtCommandSetValue			= 'SetValue'
	# sent to XTension and received from XTension
	# requires xtKeyAddress, xtKeyTag, xtKeyValue
	# if sent to XTension will update the addressed unit to the new numerical value and 
	# run the ON or OFF script.
	# if received from XTension the unit value has been changed and you should send whatever commands
	# to your connected device to bring the actual device to the same level.

xtCommandSetData			= 'sXML'
xtCommandSetXMLData			= xtCommandSetData	# deprecated use xtCommandSetData
	# sent to XTension
	# requires xtKeyAddress, xtKeyTag, xtKeyName, xtKeyValue
	# sent to XTension to save a string or numerical value into the root XML of a 
	# specific unit. This data will be available to you either with the 
	# xtCommandGetXMLData command or by getting the entirety of the 
	# units keyed data with all the setup info from the XTGetUnit command
	# you MUST use a prefix for your specific plugin for all data you store in the
	# units XML as it must share name space with built in and other data. Use
	# PLUGINNAME_valueName so that you don't overlap and cause a unit to become 
	# unusable. No validation is used to make sure you're not using a reserved key name.
	# note that only strings can be saved. The xtKeyValue must be a string and when you 
	# go looking for this in the xtUnit.data XTData object it will be returned as a string

xtCommandReindex			= 'rndx'
	# if you change the address or address prefix of a unit in XTension via the setaData
	# command then when you're done you must re-index the unit by sending this command
	# use uniqueID to target the correct unit Send the new prefix as the tag and the address 
	# in the xtKeyTag and xtKeyAddress properties of the command.

xtCommandSimmPacket			= 'SimPacket'
	# received from XTension
	# will include xtKeyData
	# this is a debugging aid if you need to simulate a packet reception that is difficult
	# to re-create. You can use the Simulate Packet verb to send the string to yourself and use this
	# to insert it into the appropriate step in the parsing of the data for testing. This is
	# not used as any part of normal interface control, just for debugging and development.

xtCommandStop				= 'Stop'
	# received from XTension
	# will include xtKeyAddress and xtKeyTag
	# from the stop verb, currently used for window shade controls but can be used for anything sensible

xtCommandUnitDeleted		= 'UnitDeleted'
	# received from XTension
	# will include xtKeyAddress and xtKeyTag
	# if the user deletes a unit assigned to your interface you will receive this event to 
	# let you know and take whatever action you feel is appropriate. Generally it's not a good
	# idea to delete things in response to this, but stop any processes you might have outstanding
	# or regularly talking to the unit in question. 
	# There is no support for you sending a command up to XTension that will delete a users units. 
	# any disconnected units should be deleted by them manually after saving off any other data or
	# scripts associated with them.
	
xtCommandWriteLog			= 'WrtL'
	# sent to XTension via the WriteLog command
	# color value is sent in the xtKeyValue
	# message is sent in the xtKeyDATA
	#
	
xtCommandGetMyUnits			= 'getUnits'
	# sent to XTEnsion as a request to return all units assigned to this interface
	# sent automatically during the connection process. After sending this command
	# any changes to those units configuration or setup or any value or runtime changes
	# will be sent automatically keeping the xtUnit object in our unit indexes up to date
	# you should not need to send this yourself as it's only necessary to send it once at startup.
	
	
xtCommandSetMyUnits			= 'setUnits'
	# Received from XTension in response to the getMyUnits command above. Handled internally
	# this is also the command that will contain any changed data for any of the units that
	# are assigned to your interface. You will receive this often. You should not have to 
	# handle this unit.
	
xtCommandSetDebugMode		= 'debug'
	# sent to turn on or turn off debug mode for the interface
	# a true or false will be included in the xtKeyValue key
	
xtCommandShutdown			= 'close'
	# sent to tell an interface that it should do any necessary cleanup and quit
	
xtCommandPing				= 'ping'
	# could be sent from either side. XTension will regularly ping your interface here
	# to make sure that the interface code hasn't hung up in some blocking method taking
	# far longer than it should. You should respond with the xtCommandPingResponse below
	# this is normally handled by the cXTension object and you don't have to handle it yourself
	# if you wish you can generate pings upstream to XTension and it will send back ping responses
	
xtCommandPingResponse		= 'PSrp'
	# sent or received in response to a ping command. If you don't respond to the ping 
	# request within the next ping interval the interface will be force quit and restarted
	
xtCommandAck				= 'ACK'
	# sent back to XTension when a command is received. You should ack the command even if the command
	# results in an error later. This just means that the plugin has received the command and is
	# processing it. This is handled automatically and you don't have to do anything with these.

xtKeyPacketId				= 'PkID'
	# when sending replies to specific messages include the packet ID from the original
	# packet. This is only needed right now for sending acks.
	
xtCommandGetKeyedData		= 'RKD'
	# used to request a keyed data object. Initially an object named "all" will be requested
	# automatically and this will become your XTension.settings xtData object.
	# you can send other xtData objects to XTension via the xtCommandSetKeyedData command
	# and then retrieve them via sending this command directly. You can add command handlers
	# to receive them when they are returned async. Check the xtKeyAddress field to find the 
	# name of the keyed data object that is being returned.

xtCommandSetKeyedData		= 'SKD'
	# a requested xtData object has been received. Check the xtKeyAddress field to find the
	# name of the object being received. Parse the data from the xtKeyData field into a new
	# xtData object. The "all" named object is what becomes the XTension.settings xtData object
	
xtCommandScriptHandler		= 'DoScript'
	# sent to or received from XTension. When receiving the command one of 3 things is happening
	# the user selected one of your context menu handlers by this name
	# the user used a script to tell xUnit to doSomeThing()
	# the user clicked one of the dynamic interface elements with an action parameter 
	# 
	# this is also used to run a script handler in either the interface, unit or global script
	# the command must include the uniqueID or address/tag of the unit and the 
	# xtCommandTaget must be set. The name of the handler is in xtKeyName and
	# any parameters you wish to pass to the handler should be a comma separated list of strings
	# in xtKeyData. There may be a better way to pass variables in the future if this is not enough
	
	
xtCommandSetRunState		= 'runState'
	# sent to XTension to set or clear an error on the interface. If your interface quits
	# XTension will restart it in a few seconds to try again. In those cases the run state
	# displays in XTension will automatically change to error and when those retries are exhausted
	# if you wish to handle the reconnections without quitting and being restarted then you 
	# can use this command to tell XTension that something is wrong to update its displays
	# the value is included in the xtKeyValue parameter of the command and can be any of these values
	# you can also include xtKeyErrorMessage with descriptive text but that may not be displayed
	# in the current version. You should include it anyway however
	
xtRunStateOK				= 'ok' # normal run state. No need to send this XTension will assume this until an error occurrs
xtRunStateError				= 'err' # displays a yellow icon in unit lists and in the interface list
xtRunStateFail				= 'fail' # displays a red background in XTension


	#
	# UDP Connection Sharing Commands
	#
	# since many plugins may want to listen on special UDP sockets or broadcast groups
	# use these commands to request access to a shared one from XTension
	# you will be sent any datagrams that are received over it. Be aware that there
	# may be packets and responses you did not solicit if other plugins are using the
	# sockets too.
	
xtCommandOpenUDP			= 'openUDP'
	# send to XTension to open a shared or at least shareable UDP or broadcast socket.
	# must include keys to specify data
	# xtKeyPort set to the port you wish to listen on
	# optionally you may include the broadcast group and a tag string to identify the connection
	# xtKeyBroadcastGroup the broadcast group to join
	# xtKeyTag an optional string to be passed back with any received data so you can identify the connection
	
xtCommandReceivedUDP		= 'gotUDP'
	# sent from XTension whenever there is a packet received on a port you opened or subscribed to via
	# the xtCommandOpenUDP.
	# the packet data will be in xtKeyData
	# the received from IP address will be in xtKeyAddress
	# the received port will be in xtKeyPort
	
xtCommandCloseUDP			= 'closeUDP'

	
xtCommandReady				= 'ready'
	# sent to XTension when everything is running properly. Right now only used for the database sharing
	
xtCommandSetStatus			= 'defaultInfo'
	# sent to XTension to set the status line in the Interface list window. Show statuses or infomational text
	# include the text in the keyValue parameter

	



# keys for sending data in XTension commands

xtKeyAddress 			 		= 'addr'
	# any command from a unit will have an address associated with it
	# global commands or commands not associated with a specific unit
	# will not include this. Look for the address only after you have 
	# validated the command, or make sure to use the .get method or
	# a try block
	
xtKeyTag 			 			= 'APfx'
	# any command from a unit will have an address tag. The main purpose
	# of this is so that units with overlapping addresses, because they are of different
	# types, can have a unique address in the database for finding which unit to 
	# work on. For example your device might support dimmer channels 1, 2, and 3 and 
	# create units with the addresses of 1, 2, and 3. Your device might also support
	# GPIO pins 1, 2, and 3. As long as the device types and their tags are different those
	# will still become unique address strings. The Tag is prefixed to the address before 
	# indexing. So the actual indexed address of the above examples might be "dimmer:1",
	# "dimmer:2", "dimmer:3", "gpio:1", "gpio:2", "gpio:3". All device types are required to
	# have a tag associated with them. It is also used for setting up the user interface
	# when editing the unit. It will always be included with any command from a unit
	# and must always be included in any command going to a unit.
	
	
	
	
#
#		C O L O R   H A N D L I N G
#
#	COMMANDS FROM XTENSION
#
# every color capable device will send the xtKeyColorMode key with any On or SetValue command. This will
# be equal to either xtKeyColorModeColor if the device should switch to color more or xtKeyColorModeWhite
# if the device should switch to color temperature mode. Obviously if your device can only do one or the other
# then the mode can be ignored for receiving commands from XTension, but should still be included in outgoing commands
# TO XTension so that it's displays know what format to use.
#
# if a device is color capable then with any on or set value command the color values will also be included
# in the command from XTension. Those values will be sent 3 ways, as a standard HTML string format with the key
# xtKeyColor, as a comma separated list of HSV values in the xtKeyColorHSV and lastly as a comma separated list of
# x,y values. These are calculated in XTension and so the color corrections may not be applied the best for your device
# use whichever format is simplest for the device you are talking to.
#
# color temperatures in XTension are always in degrees K. If your device, like phillips hue bulbs, use some other custom range
# of temperatures then you must convert or map the values onto a real K scale when handling commands from XTension or sending
# them to XTension.
# the color temperature will be sent to you and can be sent from you to XTension via the xtKeyColorTemp key
#
# if your device can display colors but cannot display color temperatures directly XTension will also include a key
# of xtKeyCalculatedColorTemp in any color temperature command. This is a best guess RGB color for the color temperature
# requested. It may need to be adjusted or mapped in order to look at all correct. 
#
# in order to handle any color information or commands the unit must have it's xtKeyAllowColor and/or
# xtKeyColorColorTemp flags set when you create it and in the info.json definition for that unit type
#
# you should send the color mode with every command that includes color data to XTension
#
# when sending a command to XTension include whichever color format is most convienient and XTension
# will convert to the other types internally.
#

xtKeyColor						= 'RGBW'
	# received from or sent to XTension
	# a standard HTML color string in hex "RRGGBB" it will be the selected color without the 
	# value of the device applied. The brightness of the color should be handled either by you in code
	# or by the device as is usual.
	# yes, the value of this key says "RGBW" but there is no longer a white portion included


xtKeyColorHSV					= 'HSVc'

	# received from XTension or sent to XTension
	# a comma separated list of hue, sat, value. The value will always be 1 as the brightness
	# should be taken from the value of the unit and not the color.
	# the Hue and Saturation values are floats between 0 and 1 so you may need to convert or map
	# those for the specific device type that needs a different value range. And convert them 
	# back to the 0-1 range before sending a new value to XTension
	
	
	
xtKeyColorXY					= 'ClXY'
	# received from XTenstion or sent to XTension
	# a comma sepatated list of x,y values. The range is between 0 and 1 so you may need
	# to convert or map back and forth between the specific range needed by your device
	# the color as represented by this will have it's value at 100% as the brightness of the
	# color should be taken from the brightness of the unit or the value in the command

xtKeyColorMode 					= 'ClMd'
	# In the event that a device supports both color mode and color temperature mode this
	# key will be present to tell you which mode is being selected or updated

xtKeyColorModeColor				= 'color'
xtKeyColorModeWhite				= 'white'
	# possible color mode keys
	# since for a color capable device will always send you all the data, either the color
	# and value and the white temperature that is currently set you should pull this key out
	# to know what values to actually send to the device.


xtKeyColorTemp		 		 	= 'CTmp'
	# if the device supports a color temperature selection this key will contain the
	# color temperature value.

xtKeyCalculatedColorTemp		= 'CaTm'
	# if your device doesn't actually support sending color temperatures XTension
	# calculates the approximate RGB values for it here and that is included as a
	# standard RGB string of 6 hex chars like the color and root color mode.
	# this will not be perfect, but it will be close.
	



xtKeyColorTempMin				= 'CTmn'
xtKeyColorTempMax				= 'CTmx'
	#
	# color temp min and max
	# if your device supports color temperature then you should send a min/max
	# make sure to set the allowColorTemperature flag in the info.json file
	# describing this unit in order to have the color temperature controls displayed.
	# value, or include it in the defaults JSON description, for the bulb during the
	# create unit command. These can be included in the create unit command and will
	# inform the color temp slider in the XTension color temperature slider.
	# if your device is color temp capable you should include both of these. If you
	# do not include them then your device will get the default for phillphs hue bulbs
	# which are 153 to 300 for cool to warm which is actually backwards for most things
	# as higher numbers are usually cooler. So don't do that.
	# note that in this case, and most newer cases, these values will be the same
	# inside a command as inside the xUnit, so a separate key for keyUnitColorTempMin
	# is not necessary. If you wish to get these values out of the xUnit object you can 
	# use these same keys.
	#
	
	
xtKeyAllowColor					= 'AlCl'
xtKeyAllowColorTemp				= 'AlCT'
	# If you specify these values in the new unit command then the unit created will
	# have it's flags to support color and or color temperature even if the info.json
	# does not specify it. Use only with the newUnit command. Not to be confused with the
	# xtUnitKeyAllowColor and xtUnitKeyAllowColorTemp keys into the unit's data object
	# which you can use later to figure out if a unit has these capabilities.
	
xtKeyPresetLevel				= 'PSet'
	# sent with the new unit command. If you are sending a value that is non-zero then that
	# value will be used as the preset level that it will return to when turning on later.
	# if the device is off but the preset level is available then you should specify this
	# key in the newUnit command so that the next On from XTension can return the light
	# to it's internal preset value.
	
	
	
xtKeyBatteryLevel 				= 'Batt'
	# when sending to XTension you can include a battery level reading if applicable.
	# including this will cause the battery icon in the flags to enable and display it
	# as a battery percentage. Valid values are from 0 to 100. Setting the value to 10 or 
	# less will cause the battery icon to show red and for the unit to be included in 
	# lists of low battery units.
	# for units that do not support a percentage just send 100 to cancel a no low batt flag or 
	# to show a green battery icon and 0 to display the low batt flag.
	
xtKeyCommError			 		= 'comm'
	# include a comm error number in any command to XTension and the unit will display
	# the alert icon next to it and run the interface error script for this unit when the
	# command is received. Send a 0 as the number to cancel the error. Error numbers are
	# not reserved and can be whatever makes sense for your own device and debugging.

xtKeyErrorMessage 				= 'ErrM'
	# in addition to an xtKeyCommError number you should include a message that describes the
	# error. This will be written to the log and also stored in the units properties so that
	# the error can be more easily made sense of.
	
xtKeyPowerLevel			 		= 'PwLv'
	# if your device supports a power level reading, for example how was the quality or power of  
	# the received signal, you can include it here and it will be available in the units ON/OFF
	# script by using the "signal strength" verb.
	
xtKeyRate 						= 'Rate'
	# received from XTension, this is the value placed in the ramp rate parameter of the ON 
	# or dim/bri or set value verbs. If your device does not support this just ignore. 
	
xtKeyUpdateOnly	 				= 'UpDt'
	# sent to XTension. If you include this as a boolean true value in the command then
	# XTension will compare the new value you sent with the current value of the unit and
	# take no action if the values are the same. You should send the first values read on 
	# startup with this set always. That will conform the current database to the existing
	# state of things but will only update the units and run scripts if values are different
	# rather than make all units think they actually received an update when they really didnt.
	# for things like temp sensors you can send all values with this set and XTension will
	# just ignore ones that arent changed. No need to keep track of previous values and compare
	# then with each reception. 
	# The reception of this command does update the last message received date in the unit
	# even if the values are the same (NOTE: NOT the "last timestamp" or "time delta" value!)
	# this is used to verify that a device is actually still receiving data even if the value
	# hasn't changed. See the advanced tab of the Edit Unit dialog for more info on the 
	# alert if the unit becomes inactive for some reason.

xtKeyNoScript					= 'NScp'
	# causes the unit to update regardless of the value being the same or not, but
	# suppresses the running of the ON or OFF script
	
xtKeyOffLabel					= 'OfLb'
xtKeyOnLabel					= 'OnLb'
	# in any command you can include a new string for the ON or OFF label of the unit
	# for example, a thermostat unit would hold a numerical representation of the
	# state of the furnace, 0=off, 1=heat, 2=AC. But just showing 0, 1, 2 isn't very
	# informative so by setting the OFF label to "off" and including a new On label
	# that reflects the actual state in text along with the set value command it will
	# display everywhere what the unit is actually doing instead of just showing a number.
	# these can be specified when the unit is created and included with any other command
	# going to the unit to change it later. If included they will overwrite any options
	# the user might have added in the Edit Unit Dialog. 
	# they can also include advanced label syntax.
xtKeyDefaultLabel				= 'DLbl'
	# the setting of the On and Off label should generally be limited to creating new units
	# once a unit is created you can set the default label in it and as long as the user has
	# not changed the on/off labels the value will display everywhere your setting of the
	# default label. If the user has overridden the On/Off labels then those will display instead.
	# this way you don't overwrite what the user has specifically entered.
	# the xtKeyDefaultLabel can be included in any command going  to a unit or sent by itself
	# with an xtCommandNoOp command addressed to the unit.
	
xtKeyTimestamp					= 'TStm'
	# sent to XTension. This parameter is optional for any command. If it is not included
	# XTension will use the current time when it processes the command as the new "last
	# timestamp value for the unit. If you are loading delayed data or processing older data
	# then you can include this and it will override the current date and be used as the
	# "last timestamp" value for the unit.
	# note that XTdb will not store values out of order. New records must be after the last record
	# that it added or the records will be ignored. They do not have to be current, they 
	# just have to be added in order chronologically. It is perfectly acceptable to batch
	# process a lot of value updates to get them into the database, as long as they are sent
	# in order they will be saved.
	
xtKeyValue						= 'Valu'
	# if the command requires a value it will be included with this key. An OFF command requires
	# no value so this will be absent. A dim, bright or new value command requires a value and it
	# will be included with this key. An ON command MAY include a value key if they unit is marked as
	# "smart" or "simulated" then the current preset value will be included in this value for an ON 
	# command as well. 


xtKeyUnitPropertyName			= 'UPN'
xtKeyUnitPropertyValue			= 'UPV'
	# Up to 10 unit properties can be sent in any command. They will be added to the unit properties
	# and all the new unit property events will be called. unit properties sent in this way can only
	# be string values, but they can be converted to numbers or anything else by the scripts that access
	# them. 
	# In this case you must alter the keys by adding an integer value from 0 to 0 after them, so instead of
	# including just the key you must include the key + "0" the key + "1" etc this makes the actual key length 
	# 4 characters "UPN0" and "UPV0" then "UPN1" and "UPN2" and so forth. They must be in order
	# as processing of them stops when the next number is not found. You must send both the propertyName
	# and PropertyValue keys. 
	
xtKeyUnitPropertyName0			= 'UPN0'
xtKeyUnitPropertyValue0			= 'UPV0'
xtKeyUnitPropertyName1			= 'UPN1'
xtKeyUnitPropertyValue1			= 'UPV1'
xtKeyUnitPropertyName2			= 'UPN2'
xtKeyUnitPropertyValue2			= 'UPV2'
xtKeyUnitPropertyName3			= 'UPN3'
xtKeyUnitPropertyValue3			= 'UPV3'
xtKeyUnitPropertyName4			= 'UPN4'
xtKeyUnitPropertyValue4			= 'UPV4'
xtKeyUnitPropertyName5			= 'UPN5'
xtKeyUnitPropertyValue5			= 'UPV5'
xtKeyUnitPropertyName6			= 'UPN6'
xtKeyUnitPropertyValue6			= 'UPV6'
xtKeyUnitPropertyName7			= 'UPN7'
xtKeyUnitPropertyValue7			= 'UPV7'
xtKeyUnitPropertyName8			= 'UPN8'
xtKeyUnitPropertyValue8			= 'UPV8'
xtKeyUnitPropertyName9			= 'UPN9'
xtKeyUnitPropertyValue9			= 'UPV9'
	
xtKeyIgnoreClicks				= 'IgCl'
	# sent with the xtCommandNewUnit to specify that the unit bring created should have it's ignore clicks setting
	# turned on by default. Double clicks in the list will be ignored, though the unit can still be controlled
	# by the user with the advanced control window or scripting. Controls in the list and in views will not offer 
	# direct means to control. For example toggle controls will not show their paddle but just the value or labels
	# centered in the toggle display. See also xtKeyReceiveOnly
	
xtKeyReceiveOnly				= 'RxOl'
	# sent with the xtCommandNewUnit to specify that the unit cannot transmit and so no commands generated in XTension
	# will result in a command being sent to the plugin. 


xtKeyContentType				= 'CnTp'
	# received from XTension
	# used in the reply from the xtCommandJSONRequest when the user has generated some response
	# from the event. See the documentation for the JSONREquest handling
	
	
xtKeyCode						= 'Code'
	# received from XTension
	# used in the reply from the xtCommandJSONRequest when the user has generated some response
	# this will then be the HTTP return code. 200 for a success or might be some other number
	# for some error that the user wishes to respond.
	
	
xtKeyData						= 'DATA'
	# received from XTension and sent to XTension
	# used in many of the above commands to send the data associated with a command
	
xtKeyDimmable					= 'Dimm'
	# when sending the new unit command include this key set to True in order to mark the 
	# unit you're creating as dimmable
		
xtKeyDimmableTypeSmart			= 'DSmt'
xtKeyDimmableTypeSimulated		= 'DSim'
	# in addition to the xtKeyDimmable boolean you can include one or the other of these
	# to make the unit Smart or Simulated dimmable

	
xtKeyJSONData					= 'JSdt'
	# used with the xtCommandJSONRequest if the request should include a JSON dictionary
	# it should be included as a string in this field. It will be parsed to an AppleScript dictionary
	# and passed to the units ON script.
	
xtKeyList						= 'List'
	# sent to XTension with the new unit command
	# if included the unit you create will be placed in a list with the name included in this
	# field. If the list doesn't exist it will be created.
	
xtKeyName						= 'Name'
	# used throughout the command set whenever a name is required. Also used when creating a new unit
	# for the default name to use when creating the unit. If the name is not unique XTension will add a
	# numerical value at the end to make it unique.
	
xtKeyReadOnly					= 'RdNl'
	# sent to XTension with the new unit command
	# if included with a True the unit will display with it's interface and type and other setup greyed out
	# so that the user cannot edit the basic unit properties, though display properties and scripts will always be 
	# editable. If it becomes necessary to edit these for any reason the used can hold the option key down when
	# opening the edit unit window and the fields will be enabled.
	
xtKeySuffix						= 'Sfix'
	# send to xtension with the new unit command
	# if included the string value in this field will fill in the unit of measure or display suffix field
	# of the new unit. For example a temperature unit might include a "F" in this value 
	# NOTE this is not the address suffix, just a display suffix.
	
xtKeyFormat						= 'Frmt'
	# send to XTension with the new unit command
	# if included the string value of this field will fill in the Format field. This uses standard
	# number formatting syntax see the wiki docs for specifics.

xtKeyUniqueId					= 'UnID'
xtKeyId							= xtKeyUniqueId
	# included used in several commands back and forth from XTension where a uniqueID is needed
	# not to be confused with the xtUnitKeyUniqueId which is the unique ID of the unit
	
xtKeyBroadcastGroup				= 'BcGr'
	# Optionally included in the xtCommandOpenUDP command if you wish the new or shared socket to
	# join a broadcast group on the included xtKeyPort
	
xtKeyPort						= 'Port'
	# required in the xtCommandOpenUDP command, the port the shared UDP socket will listen on
	
xtKeyDefaultInfoDisplay			= 'defaultInfo'
	# sent to the interface data via the set XML data command
	# this will be displayed in the interface list window after the name
	# could contain a status info or some info on the connection or anything
	# if you change it the display will update live

xtKeyCommandTarget				= 'trgt'
	# if sending a command for a shared object and the target of that command is
	# ambiguous then use this key to specify what object it should be sent to.
	# at the moment that is just xtCommandScriptHandler which can be sent to the 
	# interface to run a handler in the interface script, to a unit in order to 
	# execute a handler in the unit On script or to a global script to execute a
	# handler in that. This is only important if you're commanding a shared interface
	# device. the command can be targeted by including your own units address and tag
	# in any other circumstance. 
	
xtTargetInterface				= 'interface'
xtTargetUnit					= 'unit'
xtTargetGlobalScript			= 'targetScript'
xtTargetList					= 'list'
xtTargetMotionReport			= 'motionReport'
xtTargetVideoStream				= 'video'

xtKeyLocalAddress				= 'localAddress'
	# the first active local IP address of the machine in case you need to advertise that
	# it is included in the XTension.settings object
	
xtKeyXTensionBuild				= 'build'
	# the build number of XTension
	# actual version numbers have several dots and are capricious
	# the build numbers will always be numerical and always increase
	# you can check the version of XTension that the plugin is running
	# against with this

	
xtTrue							= 'true'
xtFalse							= 'false'
	# textual representation of true and false used in the commands to XTension



#
# Constants for accessing information in the Interface level communications dictionary
# and for script controlled connection dictionary info
#

xtKeyRemoteAddress			= 'RemoteAddress'
	# if the connection type is for outgoing TCP then the remote address configured in the interface window will be stored here
xtKeyRemotePort				= 'RemotePort'
	# If the connection type is for outgoing TCP then the remote address port will be stored here
xtKeyName					= 'Name'
	# The name given to your specific interface. This will already be pre-pended to any log lines you generate but it may be useful for other things.
xtKeyDescription			= 'Description'
	# the description of your interface plugin from the info.json file
xtKeyPortName				= 'PortName'
	# if NONE is selected then it will be
xtPortNameNone				= 'none'
	# if you're making an outgoing TCP connection then this value will be:
xtPortNameOutgoingTCP		= 'IP'
	#for accepting incoming connections the portName will be this
xtPortNameListen			= 'IPin'
	# this is that the user has selected a listening socket and has entered a port number to listen on
	# you should set the xtKeyListenType below to xtKeyListenTypeTCP or xtKeyListenTypeUDP
	
	# if it isn't one of those then it will contain the unix name of the selected serial port

xtShareUDP					= 'shareUDP'
	# set this to true in the constructor of the XTRemoteConnection class to use a shared
	# UDP connection rather than one that locks the port as in use.
	# this is unimplemented at the moment
	
xtKeyFolderPath				= 'isf'
	# an escaped shell path to the folder that your plugin is running from
xtBroadcastAddress			= 'broadcast'
	# specify this constant instead of the address if you wish to broadcast a UDP packet.
	
xtAccessFullDatabase		= 'fullAccess'
	# set in the JSON description of the interface if your plugin needs to access all database units
	# and not just the ones that are assigned to this interface. Things like external interfaces, logging
	# utilities or bridges to other protocols may need this level of access. The user will have the choice
	# in XTension's interface to limit the access to specific lists of units or to allow entire access.
xtAccessUnits				= 'accessUnits'
	# if your database access requires the sharing of units add this as a boolean true to your info.json file
xtAccessScripts				= 'accessScripts'
	# if you wish to share the users global scripts add this as a boolean true to your info.json file
xtKeyPortSelectIncoming		= 'portSelectIncoming'
	# force the port selection popup to select incoming connections
xtKeyAllowListening			= 'TCPListen'
	# allow the user to select the server option from the port popup.
xtKeyListenType				= 'listenType'
	# set in the info.json file and will allow the server to startup the correct type of listener
	# either TCP or UDP. This can be overridden in the XTRemoteConnection subclass to open 
	# whatever you want.
xtKeyListenTypeTCP			= 'tcp'
xtKeyListenTypeUDP			= 'udp'

xtKeyAllowSSL				= 'allowSSL'
	# if included in the info.json file then the user will be offered the option to check the "use SSL" checkbox
	# in the interface setup dialog. If they select true then the kEnableSSL key below will be turned on in the settings
	# and the path to the pem file will be included in the settings via the kKeyCertificatePath constant.
xtKeyEnableSSL				= 'EnableSSL'
xtKeyCertificatePath		= 'CertPath'

xtKeyAllowSerial			= 'allowSerial'
	# if included in the info.json and true then the user will be able to select from serial ports in the port popup
xtKeyAllowTCP				= 'allowTCP'
	# if included in the info.json and true then the user will be able to select an outgoing TCP connection in the port popup

xtKeyForceIp				= 'forceIp'
	# this is used when creating an incoming server
	# usually it's OK to just use 0.0.0.0 meaning all interfaces for binding a listening server
	# but sometimes that doesn't work because the machine has a VPN running or other weirdness
	# you may also wish to limit the server to a specific subnet or something like that. IN
	# which case you can use the forceIp() script command to set this value. If it's set then
	# this value will be used for incoming connections on that interface.
	
xtKeyUse24HourTime			= 'use24hourtime'
	# in XTension's settings data a boolean to let you know how the users machine is setup for 
	# formatting time. If false then use am/pm in any time displays
	
xtKeyShortWeekdayNames		= 'shortDayNames'
	# comma delimited string of short weekday names in the language of the system. saved in XTension.settings object for use to print out pretty dates

xtKeyLongWeekdayNames		= 'longDayNames'
	# command delimited string of long weekday names in the language of the system. Saved in the XTension.settings object



#
# Constants for access unit configuration information from the XTUnitById and XTUnitByAddress dictionary data
#
# note that these are different from the keys above for unit properties. The keys into the xtData object for the unit
# are different than when creating a unit or addressing it directly via the xtCommand object.

xtUnitKeyName					= 'Name'
	# the name of the unit
xtUnitKeyColorPreset			= 'cpreset'
	# if the unit has allowColor enabled then there will be 8 color presets
	# each key starts with this key and then appends a number going 0-7
	# the value will be a comma separated string of the R, G, and B values stored as the
	# color preset.
	
xtUnitKeyTag					= 'AddressPrefix'
	# the address prefix or tag as defined in the info.json file for this unit type
	# use this key to get it out of a unit info dictionary
	
xtUnitKeyIgnoreClicks			= 'IgnoreClicksInList'
	# if set to true the unit is not controllable by clicking on it in a list
	# but can still be controlled via the HUD control popups or scripts.
	# is an aide to not accidentally clicking on things that shouldn't be controlled

xtUnitKeyQuickControlType		= 'QuickControlType'
	# an integer value either 0 or 1. This is the saved off value of the last used
	# HUD popup window. If the value is 0 then the simple interface was last used and will
	# be opened again when the user next requests that window, if the value is 1 then the
	# advanced window was last used and will be shown next for this unit.
	
xtUnitKeyLastActivity			= 'LastActivity'
	# date as a string holding the last time the unit changed state, value or received
	# a command with the same value but without the only update if changed flag.
	
xtUnitKeyIgnoreOffs				= 'IgnoreOffs'
	# if true then the unit will not update it's last activity date when an OFF command
	# is received. Good for things like motion sensors where the off isn't as interesting
	# as the last ON received.
	
xtUnitKeySmart					= 'Smart'
	# the unit dimmable type is set to Smart. This means that XTension expects the unit
	# to return to the last preset level when an ON is sent rather than just go to 100%
	
xtUnitKeyPresetLevel			= 'PresetLevel'
	# if smart or simulated this is the value that the unit will return to when it's 
	# next sent an on command. 

xtUnitKeyReverseLogic			= 'ReverseLogic'
	# if set to true the unit will actually show the opposite of the last command received.

xtUnitKeyAddress				= 'Address'
	# the address of the unit as entered by the user into the Edit Unit dialog.

xtUnitKeyDeviceId				= 'Device'
	# the unique ID of the interface to which this unit is assigned. This will always be the
	# same as the interface unique id passed in the interface level configuration data 
	# since an interface can only talk directly to it's own units.
	
xtUnitKeyLastMessage			= 'lastMessage'
	# a date as a string holding the time the last message was received for this unit. Not
	# always the same as the last activity as the unit may be updating with the same value
	# and setting the only update if changed flag. This is the value used by the idle timeout
	# alert settings.
	
xtUnitKeyValue					= 'Value'
	# the stored value of the unit when the database was last saved. This value does not 
	# update with every change or command to the unit as the unit records are only refreshed
	# when the database is saved or when the unit is edited or saved.
	
xtUnitKeyPreset					= 'Preset'
	# the saved preset value that a device should return to when sent an On command
	# this is the last on level set or received for that device.
	
xtUnitKeyDimmable				= 'Dimmable'
	# boolean, if the unit is setup to accept a value or just discrete on and off.

xtUnitKeyDeviceType				= 'DeviceType'
	# string description of the unit type. For plugin assigned units this
	# will always just say 'plugin'

xtUnitKeySimulated				= 'Simulated'
	# boolean if true then XTension will send the preset value instead of an ON command
	# as we are simulating a smart unit that remembered it's last value.


xtUnitKeyReceiveOnly			= 'ReceiveOnly'
	# boolean if true then the unit is set to only receive data and will not send a command
	# to the interface if the unit is controlled by the user or a script.
	
xtUnitKeyUniqueId				= 'UniqueID'
	# a unique ID string for this unit. 
	

xtUnitKeyBlocked				= 'Blocked'
	# boolean string, if true then the unit is blocked and will not respond to updates
	# nor send commands. A blocked unit that receives an update will update the database value
	# that it displays, but no scripts will be run. Generally you should send any updates for
	# a unit even if it is blocked, but XTension will not send you any commands for a blocked unit.
	# that way the database can stay updated to new values, but scripts will not be run.
	
xtUnitKeyBatteryLevel			= 'battLevel'
	# if included in the units data object then the unit supports battery level
	# will be between 0 and 100%
	# if the unit does not support sending a battery level but sends a low battery flag then
	#	this value will go from 100 to 0 when that flag turns on.
	# levels below 10% generally show the red battery icon in XTension.

xtUnitKeyDescription			= 'Description'
	# the key to pull the description field from an xtData object representing a unit in XTension
	
xtUnitKeyUseMinMax				= 'UseMM'
xtUnitKeyMaxValue				= 'maxvalue'
xtUnitKeyMinValue				= 'minvalue'
	# if the unit is limited to a specific range set the xtUnitKeyUseMinMax to xtTrue and
	# set the minimum and maximum values into the other 2 fields.
	# there is no accompanying direct creating unit command for these so use a new
	# xtData object with these keys and include it in the new unit command as xtKeyData
	
	
xtUnitKeyErrorLevel				= 'ErrLvl'
	# set in the units data if there is an error it will be non-zero
	# if there is no error then the value will either be 0 or not present

xtUnitKeyErrorMessage			= 'ErrMessage'
	# sent along with the error level. Will be displayed in the help tag of the unit displays when
	# hovering over the error icon and potentially logged or otherwise displayed where appropriate

xtUnitKeyAllowColorTemp			= 'AllowColorTemp'
xtUnitKeyAllowColor				= 'AllowColor'
	# if the device supports color temperature or color controls then these flags will be
	# set to true. If not they will be either false or not present

xtUnitKeyColorMode				= 'color mode'
	# the color mode will either contain xtKeyColorModeColor if the device is showing a color
	# or xtKeyColorModeWhite if the device is showing a white color temperature
	# in sending a command to XTension include the xtKeyColorMode and set it to one of those
	# two values.

xtUnitKeyColorTemp				= 'color temperature'
	# the current color temp being shown buy the unit if the color mode is xtKeyColorModeWhite
	# this will be translated from whatever scale the device uses and be in degrees K.
	# to send a command to XTension with this value use the xtKeyColorTemp

xtUnitKeyColor					= 'color'
	# 

xtUnitKeyColorWithValue			= 'ColorWithValue'
xtUnitKeyColorHSV				= 'colorhsv'
xtUnitKeyColorXY				= 'colorxy'

xtUnitKeyDefaultLabel			= 'defaultLabel'
	# this is the value that is set when you pass an xtKeyDefaultLabel in a command
	# if the user has not set specific on/off labels to override this then it is used
	# instead of the standard values. You may include Advanced Label Syntax in this
	# just setting the value in the units data will not cause interfaces to update
	# you must include the new value with an actual command that would otherwise also
	# generate an update. Use the xtKeyDefaultLabel key in a command. You can use this to
	# see if the value is now different from what is actually being displayed though.
	
xtUnitKeyCurrentLabel			= 'currentLabel'
	# the currently displayed value including everything you need to display for the unit 
	# based on its on/off labels, default labels, advanced label tags, value formatting
	# and suffix values. This will change and be updated when any of those things change.
	# it is not necessary to do any work to sort that out to get what should be displayed for
	# a unit you can just subscribe to this value.

xtSharingSummaryKey				= 'summaryKey'
	# for interfaces sharing the database only and optional. If you require extra setup
	# for the units that are being shared to you you can use the sharing controls
	# which will be displayed in the configure sharing sheet window in the edit interface
	# window. Thats where you would select things like "share as switch/dimmer/something"
	# necessary for things like the Home Kit plugin where it needs to know more things about
	# the units than just what XTension has about them. This key is so that you can provide
	# a summary to display in the list of shared units and scripts. The value of this key
	# must be placed in your info.json file. It must be unique and use the naming convetion
	# so it might be something like "james.hap.summary" then you must also use that value as
	# the key for a short description of what the settings already are and use the setData command
	# to insert it into the individual units as they are edited and saved. Then it will be
	# displayed providing more useful user feedback in the app itself.
	
xtSharingControls			 	= 'sharingControls'
	# also for the configure sharing display, this is the JSON array of controls that you want
	# to display in the configure sharing window. This is a key into your info.json file



