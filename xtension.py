#
#		XTension Includes for the xtension.isf kit/device driver
#			https://MacHomeAutomation.com/
#			c. 2019 by James Sentman 	james@sentman.com		
#	
#
#		this code is offered for free and without limitations as to it's use. It is also
#		offered without any warranty or suggestion of usability whatsoever.
#
#		provides the XTension class necessary for registering ourself with the 
#		XTension plugin receiver process on the local network and sending all the
#		necessary info and controlling devices.
#
#
#		version 1.0 	11/23/2019
#

import json
from socket import *
from uuid import getnode
from threading import *
from time import *
import atexit



from xtension_constants import *

# a local global for our XTension class reference
# this is probably not necessary...

xtension = None


class XTension( object):

	# callbacks for XTension events
	
	# callbackGetInfo
	#	set this to a function that will return any other keyed information you need to send
	#	with the getInfo command. For example describing the units you want to be created and such
	callbackGetInfo = None
	
	# callbackHandleCommand
	#	set this to a function to be passed the "data" command when it comes in asking you to control a device
	#
	callbackHandleCommand = None
	
	#
	# callbackHandleShutdown
	#	set this to a function that will be called when we are being shutdown
	#	this is just trapping the atexit callback but makes it unnecessary to link that into
	#	the main app linking in this code
	callbackHandleShutdown = None

	# constants for known device types you can create in XTension
	
	tagTemperature		= 'xt.temp'				# a temperature device
	tagRegister			= 'xt.register'			# a dimmable register that can hold a floating point value, generic value holder
	tagDiscreteRegister	= 'xt.discrete'			# a non-dimmable register for just on/off, generic value holder
	tagLED				= 'xt.led'				# specific device type for controlling an indicator LED on/off not dimmable
	tagButton			= 'xt.button'			# a unit representing a physical button
	tagColorDevice		= 'xt.color'			# a color capable device, will show the regular color settings in XTension 
	tagBarometer		= 'xt.baro'				# a barometer pressure reading
	
	
	# top level supported device tags, each physical device should create one of these
	# as well as any of the above units for it's capabilities. This is where the device level
	# settings should be created.
	
	#tagRainbowHat		= 'xt.rainbowhat'		# the pimoroni rainbow hat for the raspberry pi
	# just use a generic one where we describe our units in the sendInfo packet
	#
	
	tagGenericDevice	= 'xt.generic'
	
	
	#
	#	constants used in sending the xtKit commands
	#	
	
	xtPCommandAnnounce			= "announce"
	xtPCommandInfo				= "info"
	xtPCommandByeBye			= "byebye"
	xtPCommandData				= "data"
	xtPCommandQuery				= "query"
	xtPCommandSearch			= "search"
	xtPCommandPing				= "ping"
	xtPCommandAck				= "ack"
	xtPCommandError				= "error"
	xtPCommandLog				= "log"
	xtPCommandLogLevel			= "loglevel"
	xtPCommandConfig			= "config"
	xtPCommandRestart			= "restart"
	xtPCommandDebug				= "debug" 		# passes 0 or 1 in the 7th packet format to turn it on or off
	xtPCommandFindMe			= "findme" 		# passes 0 or 1 in the 7th packet format to turn it on or off
	xtPCommandUpdateAvailable 	= "firmup" 		# a firmware update is available for this device, alert the user

	
	
	
	# flag constants and other necessary constants
	xtPFlagsNone				= 0
	xtPFlagsAck					= 1
	
	xtensionTimeout 			= 90 	# 90 seconds before we consider an XTension instance to be gone
	xtensionPingInterval		= 45	# 45 seconds of silence before we ping an XTension process to see if it's still there
	
	
	packetDelim					= ';'
	
	
	
	
	
	
	#
	#		I N I T
	#
	#	pass the device class as a string to the constructor
	#	as of this writing only tagRainbowhat supported for python
	#
	#	required to pass the proper deviceClass and the name you wish to be used in XTension
	#	to create the units and reference the device.
	#
	#	usage:
	#	xtension = XTension( deviceName='lab rainbow hat')
	#
	
	def __init__( self, *, deviceClass='xt.generic', deviceName='unnamed'):
	
		# store off a local global (is that even a thing?) so that other classes can access
		# the data and methods in this class, not just in the importing files that will create
		# this instance of us
		global xtension
		xtension = self
		
		atexit.register( self.exit_handler)
	
		self.deviceClass = deviceClass
		self.deviceName = deviceName
		self.debugMode = False
		self.udpPort = 20303
		self.udpBroadcastAddress = '255.255.255.255'
		
		# don't need to re-create these for each packet the way that the 
		# examples do. not sure what the overhead is for that but it's unnecessary
		# and will be at least slightly faster if we re-use these
		self.udpSocket = None
		self.udpBroadcastSocket = None
		
		self.udpListener = None
		
		# unique is 6 bytes in hex of the lower 3 bytes of our MAC address
		self.uniqueId = hex( getnode() & 16777215).upper()[2:] # also strip off the 0X at the beginning of the hex output
		print( "this pi's uniqueid is: %s" % self.uniqueId)
		
		# we can be connected to as many as 4 XTension instances so we need an array to hold those
		# data classes that describe them
		#self.xtInstances = [None, None, None, None]
		self.xtInstances = [None] * 4
		
		# counter so that we can send our announce packet every few minutes
		self.announceInterval = 120
		self.announceCounter = self.announceInterval # so it runs on the first loop iteration


	#
	#	G E T   I N S T A N C E
	#	
	#	takes the uniqueID of the XTension instance and if the instance exists then
	#	returns it. Returns None if not found
	#
	
	def getInstance( self, id):
		for x in self.xtInstances:
			if x != None and x.uniqueId == id:
				return x
		
		return None
		
	#
	#	A D D   I N S T A N C E
	#
	#	if no instance was found then we insert one here
	# 	since we can only hold 4 instances at a time we need to find an empty slot
	#	and if there is no empty slot then we put it in place where the oldest
	#	entry is and replace that as its probably not responding or something.
	#
	
	def addInstance( self, newInstance):

		# make sure we're not already in the index
		for i in range( len( self.xtInstances)):
			if self.xtInstances[ i] != None and self.xtInstances[ i].uniqueId == newInstance.uniqueId:
				self.xtInstances[ i] = newInstance
				return

		workIndex = -1
		
		for i in range( len( self.xtInstances)):
			if self.xtInstances[ i] == None:
				workIndex = i
				break
				
		if not workIndex == -1:
			self.xtInstances[ workIndex] = newInstance
			return
			
		# there were no empty instances found so we must find the one with the longest
		# time since we received anything from it and replace that one
		
		workTimeout = -1
		
		for i in range( len( self.xtInstances)):
			if self.xtInstances[ i].connectionTimeout > workTimeout:
				workTimeout = self.xtInstances[ i].connectionTimeout
				workIndex = i
				
		if workIndex == -1:
			print( "unable to store new XTension reference")
			return
			
		self.xtInstances[ workIndex] = newInstance
			
			
	#
	#
	#	R E M O V E   I N S T A N C E
	#
	#
	#	pass either the id or the instance, one or the other is required
	#
	def removeInstance( self, *, id=None, instance=None):
		if id == None and instance != None:
			id = instance.uniqueId
			
		if id == None:
			raise ValueException( 'either id or instance required for call to removeInstance')
			return
			
		for i in range( len( self.xtInstances)):
			x = self.xtInstances[ i]
			if x == None:
				continue
				
			if x.uniqueId == id:
				self.xtInstances[ i] = None
				return







	#
	#	S E N D   A N N O U N C E
	#
	#	sent at startup and periodically while we are online
	#	like the UPNP announce and keep alive messages
	#	but not in a stupid SOAP format
	#
	def sendAnnounce( self):
		self.sendBroadcastCommand( XTPCommand( command=self.xtPCommandAnnounce))
		self.announceCounter = 0
		
	
	#
	#	S E N D    P I N G
	#
	def sendPing( self, instance):
		self.sendCommand( instance=instance, command=XTPCommand( command=self.xtPCommandPing))
		
	
	#
	#	S E N D   B Y E   B Y E
	#
	def sendByeBye( self):
		self.sendBroadcastCommand( XTPCommand( command=self.xtPCommandByeBye))
		
	#
	#	S E N D   I N F O
	#
	#	this command contains a JSON object that describes this device and all the
	#	units that should be created for it.
	#	this is sent in response to receiving the request from it from a host like XTension
	#
	#	pass an xtInstance class to it as these are always sent upon request to a specific
	#	host and not via broadcast
	#
	
	def sendInfo( self, xtInfo):
	
		if self.callbackGetInfo == None:
			work = {}
		else:
			work = self.callbackGetInfo()
			
		# post process the addresses in any units that are passed to us
		# all unit address must end in a period and our device id which is self.uniqueId
		# but it shouldn't be necessary to pass it with this included, so if it is not there
		# then we will walk the array of units passed in here and add it.
		
		if 'units' in work:
			addressSuffix = '.' + self.uniqueId
			
			for workUnit in work[ 'units']:
			
				workAddress = workUnit[ 'address'] # all units MUST have an address
				if not workAddress.endswith( addressSuffix):
					workUnit[ 'address'] = workAddress + addressSuffix
					
				
			
		work[ 'name'] = self.deviceName
		work[ 'class'] = self.deviceClass
		
		#print( "in sendInfo with info=(%s)" % json.dumps( work))
			
		self.sendCommand( instance=xtInfo, command=XTPCommand( command=self.xtPCommandInfo, jsonData=work))
		


	#
	#	S T A R T U P
	#
	#	called to begin listening on the broadcast and direct sockets
	#	we then send our first announce broadcast and start the timer thread so that we
	#	can manage sending future ones as well as managing the XTension timeouts
	#
		
	def startup( self):
		self.udpListener = socket( AF_INET, SOCK_DGRAM)
		self.udpListener.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
		self.udpListener.bind( ('0.0.0.0', self.udpPort))
		self.udpListener.settimeout( 1)
		
		self.listenThread = Thread( target=self.threadedRead, args=(), name='udp listener')
		self.listenThread.start()
		
		# a short pause to let our listening socket get all started up and ready to receive
		# the info packets we're likely to receive immediately upon sending our announce
		sleep( 0.5)
		
		self.sendAnnounce()
		
		
		
		
	#
	#	T H R E A D E D   R E A D
	#
	#	the threaded handler for receiving UDP packets
	#	all the timeouts and other counters are managed during the timeout
	# 	on this socket as well
	#
	
	def threadedRead( self):
		readBuffer = b''
		
		while True:
			try:
				(readBuffer, readAddr) = self.udpListener.recvfrom( 4096)
				#print( "received: (%s) from (%s)" % (readBuffer, readAddr))
			except timeout:
				#print( "socket timeout")
				
				# in our timeout we process the ping timers and other timeouts
				
				for i in range( len( self.xtInstances)):
					workInstance = self.xtInstances[ i]
					if workInstance == None:
						continue
					
					workInstance.connectionTimeout += 1
						
					
					if workInstance.connectionTimeout > self.xtensionTimeout:
						# it's been longer than the connection timeout since we've heard from this
						# machine, so give up trying to do so
						self.xtInstances[ i] = None
						print( "removing XTension instance at index: %s" % i)
						continue
					
					if workInstance.connectionTimeout > self.xtensionPingInterval:
						#print( "sending ping to: %s" % workInstance.address)
						self.sendPing( workInstance)
				
				
				
				
				
				continue
				
			packets = readBuffer.split( b'\n')
			
			for x in packets:
				if x != b'':
					workPacket = XTPCommand( received=x, address=readAddr[0])
					#workPacket.debugLog()
					
					if workPacket.isValid:
						self.processReception( workPacket)
					else:
						print( "invalid packet ignored")
						
				
			
				
			


			
			
	

	#
	#	P R O C E S S   R E C E P T I O N
	#
	#	called from the threaded read when we have parsed a valid packet
	#
	
	def processReception( self, p):
		
		#	ignore our own reception of our own accounce and bye bye and other broadcast packets
		#	they will show up here as if they were from someone else
		
		if p.senderId == self.uniqueId:
			#print( "send to self broadcast ignored")
			return
			
		#p.debugLog()
			
		# if the packet is from XTension then we have to create the instance entry for this
		# or to update the timeouts and such
		
		if p.deviceType == 'xtension':
			workInstance = self.getInstance( p.senderId)
			
			if workInstance == None:
				# this is a new reception from this instance
				# we need to create an instance and insert it into the 
				# list
				
				print( "adding instance for XTension at: %s with ID %s" % (p.address, p.senderId))
				
				workInstance = XTInstance( address=p.address, uniqueId=p.senderId)
				
				self.addInstance( workInstance)
				# since this is the first time we've seen this XTension machine we should also send it our info
				self.sendInfo( workInstance)
				
			else:
				# if it is the bye bye command then we remove the instance of XTension
				# and stop processing here
				if p.command == self.xtPCommandByeBye:
					print( "ByeBye from XTension %s" % p.senderId)
					self.removeInstance( instance=workInstance)
					return
			
			
				#print( "udating timeouts for XTension at: %s with ID %s was %s seconds since we last heard from it" % (workInstance.address, workInstance.uniqueId, workInstance.connectionTimeout))
				workInstance.connectionTimeout = 0
				
			# we should have a valid instance reference now in workInstance so now we can process the command
			# if it is XTension sending us an Info packet, then we need to respond with our own Info packet
			
			if p.command == self.xtPCommandInfo:
				#print( "processing info packet from XTension")
				self.sendInfo( workInstance)
				return
		
		# all other commands should be directly addressed to us so we can bail out if we receive something
		# that does not match our ID
		
		if not p.targetId == self.uniqueId:
			#print( "packet not for us")
			return
				
		if not self.callbackHandleCommand == None:
			try:
				self.callbackHandleCommand( p)
			except Exception as e:
				print( "error:(%s) while handling command from XTension:" % e)
				p.debugLog()
				
			
			
			
		

				
	#
	#	S E N D   C O M M A N D   T O   A L L 
	#
	#	sends the same command to all currently valid instances of XTension on the network
	#
	def sendCommandToAll( self, theCommand):
	
		for xt in self.xtInstances:
			if not xt == None:
				self.sendCommand( instance=xt, command=theCommand)
				
		
	
	#
	#	S E N D   C O M M A N D
	#
	#	lower level sendCommand handler than sendCommandToAll and sendJSONCommandToAll
	# 	is called by those and other handlers to get the raw data of the command and 
	#	send the packet out
	#	
	#	this is NOT for broadcasts but for direct comms
	#	for broadcasts use the next sendBroadcast command
	#
	#	use named parameters like:
	#	xtension.sendCommand( address='1.2.3.4', command=theCommand)
	#	port is optional, if not there we will use the self.udpPort value
	#
	def sendCommand( self,*, instance, command):
		if self.udpSocket == None:
			self.udpSocket = socket( AF_INET, SOCK_DGRAM)
			self.udpSocket.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
			#self.udpSocket.setsockopt( SOL_SOCKET, SO_BROADCAST, 1)

		# set the targetId of the command to the one from the instance as this is most
		# normally used from the sendToAll calls which mean we will be reusing this command
		# for each one
		
		command.targetId = instance.uniqueId
		#print( "sending command (%s) to (%s, %s)" % (command.getRawData(), instance.address, instance.port))
						
		self.udpSocket.sendto( command.getRawData(), (instance.address, instance.port))
			

	#
	#	S E N D   B R O A D C A S T   C O M M A N D
	#
	def sendBroadcastCommand( self, command, *, address=None, port=None):
		if self.udpBroadcastSocket == None:
			self.udpBroadcastSocket = socket( AF_INET, SOCK_DGRAM)
			self.udpBroadcastSocket.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
			self.udpBroadcastSocket.setsockopt( SOL_SOCKET, SO_BROADCAST, 1)
			
		if address == None:
			address = self.udpBroadcastAddress
			
		if port == None:
			port = self.udpPort
			
		
		self.udpBroadcastSocket.sendto( command.getRawData(), (address, port))
		
			
			
	#
	#	W R I T E   L O G
	#
	#	sends the write log command to XTension after making sure that there are no
	#	packet delimiters in the string being sent
	#
	def writeLog( self, theData):
	
		self.sendCommandToAll( XTPCommand(	command=self.xtPCommandLog, data=[ theData]))
	
	
	
	
	
	
	def alertToFirmwareUpdate( self):
		pass
		
		
	#
	#	S E N D   A C K
	#
	#	used when a command has requested that we reply with an ack
	# 	pass the initial command and an ack will be created for it
	#
	
	def sendAck( self, theCommand):
		# get our xtension instance so that we can send the command back
		workInstance = self.getInstance( theCommand.senderId)
		
		if workInstance == None:
			raise ValueError( 'unable to find known instance of XTension with ID: (%s)' % (theCommand.senderId))
			return
			
		self.sendCommand( instance=workInstance,
				command = XTPCommand( command=self.xtPCommandAck, targetId=theCommand.senderId, packetId=theCommand.packetId))
		
		
		
		
		
	#
	#	R E C E I V E D   B Y E   B Y E
	#
	#	we have received a command from an XTension instance that it is going offline
	#	so we should remove it from our instance list if it is there
	#
	
	def receivedByeBye( self, theCommand):
		for i in range( 4):
			if self.xtInstances[ i] != None and self.xtInstances[i].uniqueId == theCommand.senderId:
				self.xtInstances[ i] = None
				return


	#
	#	shutting down
	#
	#	this is registered to the atexit to be called whenever the app is being shutdown by the system
	#	so that we can send a log line and also our proper bye bye message
	#
	
	def exit_handler( self):

		if not self.callbackHandleShutdown == None:
			try:
				self.callbackHandleShutdown()
			except Exception as e:
				self.writeLog( self.deviceName + ": error in shutdown: %s" % str( e))
				
		self.writeLog( self.deviceName + " is being shutdown")
		self.sendByeBye()
		sleep( 1)
		
		
	
	#
	#	S E N D   O N
	#
	#	shortcut for sending an On to XTension for a specific unit
	#	unit address and device tag are required. optionally you can
	#	specify any other parameters that should go into the command such as xtKeyUpdateOnly
	#	via other keywords to the call
	#
	def sendOn( self, *, address, tag, **kwargs):
		data = {xtKeyCommand:xtCommandOn, xtKeyTag:tag, xtKeyAddress:address}
		# add in any optional info sent to the command
		# expanding any global constants that you used as keys
		for key in kwargs:
			value = kwargs[ key]
			if key in globals():
				key = globals()[ key]
			
			data[ key] = value
			
		self.sendCommandToAll( XTPCommand( command=self.xtPCommandData, jsonData=data))
		
		
	#
	#	S E N D   O F F 
	#
	#	shortcut for sending an Off to an XTension unit
	#	unit address and device tag are required. Optionally you can 
	#	specify any other parameters that should go into the command such as xtKeyUpdateOnly
	#	via other keyed parameters to the call
	#
	def sendOff( self, *, address, tag, **kwargs):
		data = {xtKeyCommand:xtCommandOff, xtKeyTag:tag, xtKeyAddress:address}
		
		for key in kwargs:
			value = kwargs[ key]
			if key in globals():
				key = globals()[ key]
				
			data[ key] = value
			
		self.sendCommandToAll( XTPCommand( command=self.xtPCommandData, jsonData=data))
		
	#
	#	S E N D   V A L U E
	#
	#	shortcut for sending a value to an XTension unit
	#	unit address, device tag and value are required. Optionally you can specify any other
	#	parameters that should go into the command such as xtKeyUpdateOnly
	#
	def sendValue( self, *, address, tag, value, **kwargs):
		data = {xtKeyCommand:xtCommandSetValue, xtKeyTag:tag, xtKeyAddress:address, xtKeyValue:value}
		
		for key in kwargs:
			thisValue = kwargs[ key]
			if key in globals():
				key = globals()[ key]
			data[ key] = thisValue
			
		self.sendCommandToAll( XTPCommand( command=self.xtPCommandData, jsonData=data))
			
	
		
	
	
	
	
	
	
	
	
	
	
	

#
#
#	class 		X T   I N S T A N C E
#
#	this is just a data holder that stores the necessary info for us to know about XTension
# 	or other listeners that we have found. It holds their address and the last time we
# 	heard from them as well as their unique ID and such
#	they are stored in the XTension class in the xtInstances list
#
#	to the constructor please pass:
#		address = "ip.address.of.thing"
#		uniqueId = "123456"
#
class XTInstance( object):
	def __init__( self, *, address, uniqueId, port=None):
		self.address = address
		self.uniqueId = uniqueId
		if port == None:
			self.port = xtension.udpPort
		else:
			self.port = port
		
		self.connectionTimeout = 0
		self.pingSent = False
		self.timeout = 0
		self.pingInterval = 0
		
	def debugLog( self):
		print( "----- begin XTInstance Debug Logging")
		print( "	address:	%s" % self.address)
		print( "	id:			%s" % self.uniqueId)
		print( "	timeout:	%s" % self.connectionTimeout)
		print()
		
		















#
#	class 		X T   P   C O M M A N D
#
# 	if creating an ack or something that needs to include a specific packet ID then pass
#	packetId=1234 or whatever. if the packet ID is not passed then it will be generated and the
#	currentCommandId incremented
#
class XTPCommand( object):

	# shared property of the class for currentCommandID this is a rotating number
	# from 0 to 1000 and then rolls over. This way we can ignore repeats of broadcasted
	# commands
	currentCommandId = 0
	
	# commands always start with "xtkit"
	commandStart = "xtkit"
	packetDelim = ';'
	
	def __init__( self, *, received=None, flags=0, targetId=None, command=None, data=[], jsonData=None, packetId=None, address=None):
	
		if received == None:
			self.isValid = True 	# we are a new outgoing packet so should always be valid
			self.address = address
			self.flags = flags
			self.targetId = targetId
			self.command = command
			self.data = data
			self.jsonData = jsonData
			
			# we need a packet ID if we are being created to go out
			self.packetId = self.currentCommandId
			
			self.currentCommandId += 1
			if self.currentCommandId > 1000:
				self.currentCommandId = 0
				
			
		else:
			self.address = address
			self.isValid = False 	# will set to true at the end if no exception
			self.parse( received)
			self.isValid = True
			
		
	def parse( self, received):
	
		if isinstance( received, bytes):
			received = received.decode()
	
		self.data = received.split( self.packetDelim)
		# all commands start with xtkit
		
		try:
			prefix = self.data.pop( 0)
			if not prefix == self.commandStart:
				raise ValueError( 'not an XTension packet. Begins with( %s)' % prefix)
				return
		except Exception as e:
			raise ValueError( 'malformed packet: (%s) %s' % (received, str( e)))
			return
		
		# all command should have at least this many parts to the command
		# though not all will have the additional data sections
		# so if any error occurs here then the command is invalid
		try:
			self.packetId = self.data.pop( 0)
			self.flags = self.data.pop( 0)
			self.senderId = self.data.pop( 0)
			self.targetId = self.data.pop( 0)
			self.deviceType = self.data.pop( 0)
			self.command = self.data.pop( 0)
		except Exception as e:
			raise ValueError( 'malformed packet: (%s) %s' % (received, str( e)))
			return
			
		self.isValid = True
		
	def debugLog( self):
		print( "-----BEGIN PACKET DEBUG valid=%s" % self.isValid)
		print( "	packetId 	= %s (%s)" % (self.packetId, type( self.packetId)))
		print( "	flags 		= %s (%s)" % (self.flags, type( self.flags)))
		print( "	senderId 	= %s (%s)" % (self.senderId, type( self.senderId)))
		print( "	targetId 	= %s (%s)" % (self.targetId, type( self.targetId)))
		print( "	deviceType 	= %s (%s)" % (self.deviceType, type( self.deviceType)))
		print( "	command 	= %s (%s)" % (self.command, type( self.command)))
		print( "	data 		= %s (%s)" % (self.data, type( self.data)))
		print( "")
			
			
	def getDataAsJSON( self):
		return json.loads( self.data[0])
		
	def setDataAsJSON( self, theData):
		#self.data.append( json.dumps( theData).replace( xtension.packetDelim, '-'))
		self.jsonData = theData
		
	def appendData( self, theData):
		self.data.append( theData.replace( xtension.packetDelim, '-'))
		
	def getRawData( self):
		if self.targetId == None:
			self.targetId = ''
			
		work = [self.commandStart, str( self.packetId), str( self.flags), xtension.uniqueId, 
			self.targetId, xtension.deviceClass, self.command]
			
		# add in any other items in the data list
		
		for s in self.data:
			work.append( s)
			
		# lastly add in the JSON data that describes the lower level command if it is there
		
		if not self.jsonData == None:
			work.append( json.dumps( self.jsonData).replace( xtension.packetDelim, '-'))
			
			
		return (xtension.packetDelim.join( work) + '\n').encode()
		
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		



