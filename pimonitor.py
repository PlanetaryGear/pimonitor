#!/usr/bin/python3
#
#			Raspberry Pi Monitor for XTension
#		c. 2022-2023 by James Sentman james@sentman.com
#		https://MacHomeAutomation.com/
#
#	this background program will connect to XTension and create units for the health of this
#	pi. It will send back information about power throtteling, temperature throtteling
#	disk space and possibly other errors or conditions. It will also keep a unit in XTension
#	turned on as long as this program is running alerting you to a pi that has gone offline
#	or having other problems.
#
#	XTENSION INSTALL:
#		on the XTension side this requires that you be running an instance of the "XTension Kits"
#		plugin. Only 1 instance is necessary for all devices on the local network that implement the
#		protocol. 
#
# 	INSTALL:
#		git is required to do the download of the latest version if you get an error when trying to
#		run git then you need to install it via:
#		sudo apt install git
#
#		1) copy or rename the configuration_template.py file to "configuration.py"
#			cp configuration_template.py configuration.py
#
#		2) edit the configuration file to include the things you wish to scan and the intervals
#			descriptions of the various options are included in the configuration.py file
#			nano ./configuration.py
#
#		3) install the systemctl files
#			The service file assumes that the program was installed in /home/pi/pimonitor
#			if you have installed the file in a different place please edit the file to point
#			to the new install location.
#
#			sudo cp /home/pi/pimonitor/pimonitor.service /lib/systemd/system/
#			sudo systemctl daemon-reload
#			sudo systemctl enable pimonitor
#			sudo systemctl start pimonitor
#
# Version info:
#	1.0 	Initial Release
#
#	1.0.1 	5/6/2023 	Added dont log new value receptions to the new unit creations for 
#						much of the data that changes frequently but is not necessarily
#						useful to have spamming the log as the values will be there to go
#						look for if needed.


import select
import datetime
import sys, os
import threading
from subprocess import PIPE, Popen


from xtension import *				# XTension plugin communication protocol support
from xtension_constants import *	# Constants used in the commands to XTension


currentHostname 	= None 			# will become either the machine hostname or was set by the user in configuration file
overrideDeviceId 	= None 			# see this value in the configuration file for more info

# import the configuration data
# if the configuration.py file is not found attempt to import the default values from the template file
try:
	from configuration import *		# user configuration 
except:

	# if they failed to copy the template file and make any changes then we can just use the defaults from the template file
	try:
		from configuration_template import *
	except:
		# if we cant find that either then strange things are afoot try to log it and then just sleep
		xtension = XTension( deviceName="misconfigured pimonitor")
		xtension.startup()
	
		sleep( 2)
		errMsg = "Unable to find the configuration.py file, did you remember to rename the template file?"
		print( errMsg)
		xtension.writeLog( errMsg)
		while True:
			# just keep the systemctl from restarting us over and over and over
			# so sit here and sleep and wait to be restarted by the user then there is
			# some configuration to use
			sleep( 1)






# addresses used for normal units 

addrThrottled 			= 'THROTTLED'
addrUndervolt 			= 'UNDERVOLT'
addrCapped				= 'CAPPED'
addrThrottledHistoric 	= 'HTHROTTLED'
addrUndervoltHistoric	= 'HUNDERVOLT'
addrCappedHistoric		= 'HCAPPED'
addrCPUTEMP 			= 'CPUTEMP'
addrRSSI 				= 'RSSI'
addrLinkQuality			= 'QUAL'
addrLinkRate			= 'RATE'
addrTXPower 			= 'TXPOWER'
addrWiFiFreq			= 'WFREQ'
addrCPUUsage 			= 'IDLE'
addrFrequency 			= 'FREQ'
addrDiskSpace 			= 'SPACE'
	# disk space will be the 'SPACE.' and then the path with all the slashes converted to more periods
	# so the root would be 'SPACE..' and /pi/recordings would be SPACE.PI.RECORDINGS



#
#	file accessors that we will keep open to read various system files via the select thread
#

throttledFile = None
CPUFreqFile = None

# current values so we can only send info when something has changed
currentCPUTemp 		= 0.0
currentRSSI 		= [0] * len( RSSIInterfaceName)
currentQuality 		= [0] * len( RSSIInterfaceName)
currentBitRate 		= [0] * len( RSSIInterfaceName)
currentTXPower 		= [0] * len( RSSIInterfaceName)
currentWiFiFrequency= [0] * len( RSSIInterfaceName)
currentUsageData	= None
currentCPUUsage	 	= -1
currentCPUFreq 		= 0
currentDiskSpace 	= [0] * len( volumesToScan)

	



# 
# 	T H R E A D E D   F I L E   W A T C H E R
#
#	called as a thread, pauses on select to watch all the necessary files that might
#	change and to send updates to XTension
# 	unfortunately it seems that only the throttled file will respond to being read via the select.poll method
#	and the others will still have to be read regularly in a separate thread.
#	but since there is a 1 second timeout on the poll we can at least get close unless a lot is happening to the pi
#	in which case the other scans will happen slightly more frequently
#	TODO switch this to datetime intervals instead of just counting sleeps of a second
#
def threadedFileWatcher():
	global throttledFile


	epoll = select.epoll()
	
	CPUCheckCounter 	= CPUTempScanSeconds
	RSSICheckCounter 	= RSSIScanSeconds
	CPUUsageCounter 	= CPUUsageScanSeconds
	diskSpaceCounter 	= diskScanSeconds
	
	try:
		throttledFile = open( "/sys/devices/platform/soc/soc:firmware/get_throttled")
	except Exception as e:
		xtension.writeLog( "error opening throttled information file: %s" % e)

	
	if throttledFile != None:
		epoll.register( throttledFile.fileno(), select.EPOLLPRI | select.EPOLLERR)
	

	while True:
		skipOtherPolls = False # when the epoll.poll returns something it may be much faster than we want to count other seconds	
		for fd, event in epoll.poll( 1):
			skipOtherPolls = True

			if throttledFile != None and fd == throttledFile.fileno():
				try:
					processThrottledFile()
				except Exception as e:
					xtension.writeLog( "ERROR: processThrottledFile( %s)" % e)
					

		if skipOtherPolls:
			continue
				
		if checkCPUTemp:
			CPUCheckCounter += 1
			if CPUCheckCounter >= CPUTempScanSeconds:
				try:
					processCPUTemp()
				except Exception as e:
					xtension.writeLog( "ERROR: processCPUTemp( %s)" % e)
					
				CPUCheckCounter = 0
		
		
		if checkRSSI:
			RSSICheckCounter += 1
			if RSSICheckCounter >= RSSIScanSeconds:
				try:
					processRSSI()
				except Exception as e:
					xtension.writeLog( "ERROR: processRSSI( %s)" % e)
					
					
				RSSICheckCounter = 0
		
		
		
		if checkCPUUsage:
			CPUUsageCounter += 1
			if CPUUsageCounter >= CPUUsageScanSeconds:
				try:
					processCPUUsage()
				except Exception as e:
					xtension.writeLog( "ERROR: processCPUUsage( %s)" % e)
					
				CPUUsageCounter = 0
		
		
		if checkDiskSpace:
			diskSpaceCounter += 1
			if diskSpaceCounter >= diskScanSeconds:
				try:
					processDiskSpace()
				except Exception as e:
					xtension.writeLog( "ERROR: processDiskSpace( %s)" % e)
					
				diskSpaceCounter = 0
					


	if throtteledFile != None:
		epoll.unregisterFile( throttledFile.fileno())
		throttledFile.close()
	
	
	
		

#
#		P R O C E S S   R S S I
#
#	called at the interval in configuration to process the various WiFi statistics
#	as turned on in the configuration, or nothing if the list of wlan interfaces is empty
#	
	
def processRSSI():
	global currentRSSI
	
	for i in range( len( RSSIInterfaceName)):

		thisName 		= RSSIInterfaceName[ i]	
		
		process = Popen( ['iwconfig', thisName], stdout=PIPE, stderr=PIPE)
		output, _error = process.communicate()
		output = output.decode()
		
		lines = output.split( '\n')
		
		for workLine in lines:
			if showWiFiFrequency and 'Frequency:' in workLine:
				value = float( workLine.split( 'Frequency:')[1].split( ' GHz')[0])

				if value != currentWiFiFrequency[ i]:
					currentWiFiFrequency[ i] = value
					thisAddress = addrWiFiFreq + '.' + thisName
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
			
			if checkRSSI and 'Signal level=' in workLine:
				value = int( workLine.split( 'Signal level=')[1].split( ' dBm')[0])
				
				if value != currentRSSI[ i]:
					thisAddress = addrRSSI + '.' + thisName
					currentRSSI[ i] = value
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
					
			if showBitRate and 'Bit Rate=' in workLine:
				value = float( workLine.split( 'Bit Rate=')[1].split( ' Mb/s')[0])
				
				if value != currentBitRate[ i]:
					thisAddress = addrLinkRate + '.' + thisName
					currentBitRate[ i] = value
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
					
			if showTXPower and 'Tx-Power=' in workLine:
				value = int( workLine.split( 'Tx-Power=')[1].split( ' dBm')[0])
				
				if value != currentTXPower[ i]:
					currentTXPower[ i] = value
					thisAddress = addrTXPower + '.' + thisName
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
					
			if showLinkQuality and 'Link Quality=' in workLine:
				s = workLine.split( 'Link Quality=')[1].split( ' ')[0].split( '/')
				value = round( ( float( s[0]) / float( s[1]) * 100))
				
				if value != currentQuality[ i]:
					currentQuality[ i] = value
					thisAddress = addrLinkQuality + '.' + thisName
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
			
				
				
			
			


#
#	P R O C E S S   C P U   T E M P
#
#	called at the configured interval by the main watcher thread
#	opens the CPU temperature "file" and sends any changes to XTension
#

def processCPUTemp():
	global currentCPUTemp

	CPUTempFile = open( '/sys/class/thermal/thermal_zone0/temp')
	tempInC = round( float( CPUTempFile.read().strip()) / 100) / 10
	CPUTempFile.close()
	tempInF = CtoF( tempInC)
	
		
	if showTempsInF:
		displayTemp = tempInF
		augTemp = tempInC
		primarySuffix = '°F'
		secondarySuffix = '°C'
	else:
		displayTemp = tempInC
		augTemp = tempInF
		primarySuffix = '°C'
		secondarySuffix = '°F'


	#print( "CPU: %s" % displayTemp)
	
	if displayTemp != currentCPUTemp:
		currentCPUTemp = displayTemp
		if alsoShowInOtherScale:
			xtension.sendValue( value=displayTemp, tag=xtension.tagTemperature, address=addrCPUTEMP,
				xtKeyDefaultLabel='%s%s (%s%s)' % (displayTemp, primarySuffix, augTemp, secondarySuffix))
		else:
			xtension.sendValue( value=displayTemp, tag=xtension.tagTemperature, address=addrCPUTEMP, xtKeyDefaultLabel='')


#
#	C   T O   F
#	
#	just conversion routine
#
def CtoF( inTemp):
	inTemp = 9.0 / 5.0 * inTemp + 32
	return round( (inTemp * 10)) / 10
	


#
#	P R O C E S S   C P U   F R E Q   F I L E
#
#	called at the interval in the configuration or not at all if this is turned off
#	reads the current CPU frequency and sends any changes to XTension
#	this can change very quickly and so is turned off by default as the scanning must be
#	multiple times a second to catch very short changes and some may be missed regardless
#	is useful for debugging purposes or to know how your pi is managing itself but probably not
#	something you'd want to have streaming constantly all the time.
#

def processCPUFreqFile():
	global currentCPUFreq
	global CPUFreqFile
	
	if CPUFreqFile == None:
		CPUFreqFile = open( "/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_cur_freq")

	while True:
		sleep( CPUFrequencyScanSeconds)
		try:
			CPUFreqFile.seek( 0)
			rawInfo = CPUFreqFile.read().strip()
			if rawInfo != '':
				newFreq = int( rawInfo) / 1000
			else:
				continue
	
			if newFreq != currentCPUFreq:
				currentCPUFreq = newFreq	
				xtension.sendValue( value=newFreq, tag=xtension.tagRegister, address=addrFrequency, xtKeyUpdateOnly=True)
		except Exception as e:
			# basically ifgnore any errors as the file will be changing sometimes
			print( "error in CPUFreq read: %s" % e)
			continue

	CPUFreqFile.close()
	



#
#		P R O C E S S   T H R O T T L E D   F I L E 
#
#	if the epoll returns the throttled file as having changed then we read it here
#
def processThrottledFile():
	throttledFile.seek( 0)
	status = int( throttledFile.read().strip(), 16)

	#
	# HISTORIC THROTTLED
	#
	if (status & 0x40000):
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOn, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrThrottledHistoric, xtKeyUpdateOnly:True}
		))
		
	elif (status != 0): # it sends a 0 sometimes which does not mean these are not on still for whatever reason
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrThrottledHistoric, xtKeyUpdateOnly:True}
		))

	
	#
	# HISTORIC ARM freqency capping
	#
	if (status & 0x20000):
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOn, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrCappedHistoric, xtKeyUpdateOnly:True}
		))
	elif (status != 0): # it sends a 0 sometimes which does not mean these are not on still for whatever reason
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrCappedHistoric, xtKeyUpdateOnly:True}
		))


	#
	# HISTORIC UNDERVOLTAGE		
	#
	if (status & 0x10000):
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOn, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrUndervoltHistoric, xtKeyUpdateOnly:True}
		))
	elif (status != 0): # it sends a 0 sometimes which does not mean these are not on still for whatever reason
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrUndervoltHistoric, xtKeyUpdateOnly:True}
		))
	
	
	#
	# ACTIVE THROTTLING
	#
	if (status & 0x4):
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOn, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrThrottled, xtKeyUpdateOnly:True}
		))
	else: # it sends a 0 sometimes which does not mean these are not on still for whatever reason
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrThrottled, xtKeyUpdateOnly:True}
		))


	#
	# FREQUENCY CAPPED
	#
	if (status & 0x2):
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOn, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrCapped, xtKeyUpdateOnly:True}
		))
	else: # it sends a 0 sometimes which does not mean these are not on still for whatever reason
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrCapped, xtKeyUpdateOnly:True}
		))
		
	# ACTIVE UNDERVOLTAGE
	if (status & 0x1):
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOn, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrUndervolt, xtKeyUpdateOnly:True}
		))
	else: # it sends a 0 sometimes which does not mean these are not on still for whatever reason
		xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
			{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrUndervolt, xtKeyUpdateOnly:True}
		))



#
#	P R O C E S S   C P U   U S A G E
#

def processCPUUsage():
	global currentUsageData
	global currentCPUUsage
	
	with open( '/proc/stat') as f:
		rawValues = f.read().strip().split( '\n')[0]
	
	x = rawValues.split()
	data = {'user':int( x[1]), 'nice':int( x[2]), 'system':int( x[3]), 
		'idle':int( x[4]), 'iowait':int( x[5]), 'irq':int( x[6]),
		'softirq':int( x[7]), 'steal':int( x[8]), 'guest':int( x[9]), 
		'quest_nice':int( x[10])}
		
	data[ 'idle_total'] = data[ 'idle'] + data[ 'iowait']
	data[ 'non_idle'] = data[ 'user'] + data[ 'nice'] + data[ 'system'] + data[ 'irq'] + data[ 'softirq'] + data[ 'steal']
	data[ 'total'] = data[ 'idle_total'] + data[ 'non_idle']

	# if we are running the first time then just save off the data and look again at whatever interval
	if currentUsageData == None:
		currentUsageData = data
		return

	totald = data[ 'total'] - currentUsageData[ 'total']
	idled = data[ 'idle_total'] - currentUsageData[ 'idle_total']
	
	newIdle = 100 - round( ((totald-idled) / totald) * 100)
	
	if newIdle != currentCPUUsage:
		currentCPUUsage = newIdle
		xtension.sendValue( value=newIdle, tag=xtension.tagRegister, address=addrCPUUsage)





#
#	H U M A N   R E A D A B L E   S I Z E
#
#	used to format the disk space available into a human readable label that is used as the value
#	display in XTension. The actual k available is sent as the real unit value but this output
#	like 16GB or 10MB is sent as the display label to be easier to read.
#
def humanReadableSize( size, decimalPlaces = 2):
	for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
		if size < 1024.0 or unit == 'PB':
			break
		size /= 1024.0
	
	formatString = '{:.%sf} {}' % decimalPlaces	
	return formatString.format( size, unit)


#
#	P R O C E S S   D I S K   S P A C E
#
#	called at the interval set in configuration if there is anything in the 
#	list of volumes to check.
#
def processDiskSpace():
	global currentDiskSpace
	
	for i in range( len( volumesToScan)):
		try:
			thisPath = volumesToScan[ i]
			thisAddress = addrDiskSpace + '.' + thisPath.replace( '/', '.')
			diskInfo = os.statvfs( thisPath)
			thisSpace = diskInfo.f_bavail * diskInfo.f_frsize
			
			if thisSpace != currentDiskSpace[ i]:
				currentDiskSpace[ i] = thisSpace
				xtension.sendValue( value=thisSpace, tag=xtension.tagRegister, address=thisAddress,
					xtKeyDefaultLabel=humanReadableSize( thisSpace), xtKeyUpdateOnly=True)

		except Exception as e:
			xtension.writeLog( 'Unable to get disk space for volume at "%s" %s' % (thisPath, e))
			
		
		


#
#	R E A D   H O S T N A M E   I N   L I N E
#
# 	If a name to use is not included in the configuration file then this is called
#	to read the hostname of the pi. This will be used in unit naming when creating the
#	units in XTension.
#	note that this will not be monitored yet and so if you change the hostname it will not
#	update until the program is restarted.
#

def readHostnameInline():
	global currentHostname
	try:
		file = open( "/etc/hostname")
	except:
		print( "no hostname file found")
		sys.exit( 1)
		
	currentHostname = file.read().strip()
	file.close
	

#
#	G E T   P I   T Y P E
#
#	sent as a unit property to the main Status unit. 
#

def getPiType():
	try:
		with open( '/proc/device-tree/model') as f:
			boardName = f.read().strip()
			
		
		return boardName
	except:
		return '(unknown pi type)'
	

#
#	G E T   I N F O   F O R   X T E N S I O N
#
#	part of the XTension Kits protocol implementation. When an XTension instance finds us it will ask for 
#	an info packet that describes our units to it so that it can create them. This is a largish JSON file
#	that we create here based on the configuration. It is called whenever we reconnect to XTension or when
#	XTension polls us for potentially new information. After this any other changes to the units configured
#	is pushed to XTension and not polled, but this is loaded periodically.
#
#	1.0.1 added the kInfoNoLog flag to the creation of units that change frequently but for which it might not
#	be useful to have it log constantly like CPU Usage and CPU Temp. You can turn this back on in the Advanced
#	tab of the Edit Unit dialog in XTension.

def getInfoForXTension():

	# info about our device and the units we want to create is sent in this dictionary object 
	work = {}
	
	
	
	work[ 'devicetype'] = "Pi Monitor"	# this name is used when creating the status unit so it shows what the device is clearly in XTension
	
	
	# we always watch the throttling and power file for info so those units are always present
	units = [
		{kInfoName:'Active Throttling', kInfoTag:xtension.tagDiscreteRegister, kInfoAddress:addrThrottled, 
			kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoOnLabel:'THROTTLED', kInfoOffLabel:'OK'},
		{kInfoName:'Active Undervoltage', kInfoTag:xtension.tagDiscreteRegister, kInfoAddress:addrUndervolt, 
			kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoOnLabel:'UNDERVOLT', kInfoOffLabel:'OK'},
		{kInfoName:'Active CPU Speed Capping', kInfoTag:xtension.tagDiscreteRegister, kInfoAddress:addrCapped, 
			kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoOnLabel:'CAPPED', kInfoOffLabel:'OK'},
		{kInfoName:'Throttling Has Occurred', kInfoTag:xtension.tagDiscreteRegister, kInfoAddress:addrThrottledHistoric,
			kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoOnLabel:'THROTTLED', kInfoOffLabel:'OK'},
		{kInfoName:'Undervoltage Has Occurred', kInfoTag:xtension.tagDiscreteRegister, kInfoAddress:addrUndervoltHistoric, 
			kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoOnLabel:'UNDERVOLT', kInfoOffLabel:'OK'},
		{kInfoName:'CPU Speed Capping Has Occurred', kInfoTag:xtension.tagDiscreteRegister, kInfoAddress:addrCappedHistoric, 
			kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoOnLabel:'CAPPED', kInfoOffLabel:'OK'}
	]
	
	
	if checkCPUTemp:
		units += [{kInfoName:'CPU Temperature', kInfoTag:xtension.tagTemperature, kInfoAddress:addrCPUTEMP, 
			kInfoDimmable:True, kInfoSuffix:'°F', kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoNoLog:True}]
			
	if checkRSSI:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi RSSI ' + thisInterface
			thisAddress = addrRSSI + '.' + thisInterface
			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' dBm', kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoNoLog:True}]
				
	if showBitRate:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi Bit Rate ' + thisInterface
			thisAddress = addrLinkRate + '.' + thisInterface
			
			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' Mb/s', kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoNoLog:True}]
				
	if showTXPower:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi TX Power ' + thisInterface
			thisAddress = addrTXPower + '.' + thisInterface

			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' dBm', kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoNoLog:True}]
				
	if showLinkQuality:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi Link Quality ' + thisInterface
			thisAddress = addrLinkQuality + '.' + thisInterface

			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:'%', kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoNoLog:True}]
	
	if showWiFiFrequency:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi Frequency ' + thisInterface
			thisAddress = addrWiFiFreq + '.' + thisInterface

			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' GHz', kInfoIgnoreClicks:True, kInfoReceiveOnly:True}]

	if checkCPUUsage:
		units += [{kInfoName:'CPU Idle', kInfoTag:xtension.tagRegister, kInfoAddress:addrCPUUsage, 
			kInfoDimmable:True, kInfoSuffix:'%', kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoNoLog:True}]
			
	if checkCPUFrequency:
		units += [{kInfoName:'CPU Frequency', kInfoTag:xtension.tagRegister, kInfoAddress:addrFrequency, 
			kInfoDimmable:True,	kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoSuffix:' MHz', kInfoNoLog:True}]
			
	if checkDiskSpace:
		for thisPath in volumesToScan:
			thisAddress = addrDiskSpace + '.' + thisPath.replace( '/', '.')
			units += [{kInfoName:'Disk Space: %s' % thisPath, kInfoTag:xtension.tagRegister, 
				kInfoAddress:thisAddress, kInfoDimmable:True, kInfoReceiveOnly:True, kInfoIgnoreClicks:True, kInfoNoLog:True}]
				

	work[ 'units'] = units
	
	# additional properties for the master unit
	# NOTE this is not yet implemented in the XTension kit plugin, but I'll get that working shortly
	work[ 'mainprops'] = [
		{'pi type':piType}
	]
	
	return work
	





#
#		M A I N
#

# if the user has not set it then we will do so from the machine hostname
if currentHostname == None:
	readHostnameInline()

piType = getPiType()

xtension = XTension( deviceName=currentHostname, deviceId=overrideDeviceId)
xtension.callbackGetInfo = getInfoForXTension

xtension.startup()

# give it a moment to actually find XTension so that initial values can be sent
sleep( 2)


# before beginning the watching of the file make sure that the historical throttled units
# are off. If they turn out to be on as soon as we begin reading the file then they will
# be turned on again. But since we cannot reliably read a 0 for nothing we cannot reliably 
# send an off for these. They are normally only reset by a reboot so when this program starts we send them
# an off.

xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
	{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrThrottledHistoric, xtKeyUpdateOnly:True}
))
xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
	{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrCappedHistoric, xtKeyUpdateOnly:True}
))
xtension.sendCommandToAll( XTPCommand( command=xtension.xtPCommandData, jsonData=
	{xtKeyCommand:xtCommandOff, xtKeyTag:xtension.tagDiscreteRegister, xtKeyAddress:addrUndervoltHistoric, xtKeyUpdateOnly:True}
))



fileWatcherThread = Thread( target=threadedFileWatcher, args=())
fileWatcherThread.start()

#
# if the CPU Frequency check is enabled this will run in a separate thread from the main watcher thread as it needs to
# scan must more rapidly than the resolution of the main watcher system.
if checkCPUFrequency:
	CPUSpeedThread = Thread( target=processCPUFreqFile, args=())
	CPUSpeedThread.start()

xtension.writeLog( "PiMonitor Startup")


	
	








