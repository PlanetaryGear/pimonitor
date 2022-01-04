#!/usr/bin/python3
#
#			Raspberry Pi Monitor for XTension
#		c. 2022 by James Sentman james@sentman.com
#		https://MacHomeAutomation.com/
#
#	this background program will connect to XTension and create units for the health of this
#	pi. It will send back information about power throtteling, temperature throtteling
#	disk space and possibly other errors or conditions. It will also keep a unit in XTension
#	turned on as long as this program is running alerting you to a pi that has gone offline
#	or having other problems.
#
#	
#	note that the install procedure below assumes you have placed the file into the
#	standard pi home directory. If you have installed it elsewhere or changed names
#	you will have to edit the file accordingly
#
#	to install copy the pimonitor.service file into the systemctl folder like:
#		sudo cp /home/pi/pimonitor/pimonitor.service /lib/systemd/system/
#		sudo systemctl daemon-reload
#		sudo systemctl enable pimonitor
#		sudo systemctl start pimonitor
#
#	or just reboot to start the process. In XTension run an XTension Kits Receiver plugin
#	only 1 instance of the plugin is required for all remote devices using that protocol
#	and the units will appear there.
#


import select
import datetime
import sys
import threading
from subprocess import PIPE, Popen


currentHostname = None 				# will become either the machine hostname or was set by the user in configuration file
from xtension import *				# XTension plugin communication protocol support
from xtension_constants import *	# Constants used in the commands to XTension
from configuration import *			# user configuration 



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



#
#	file accessors that we will keep open to read various system files via the select thread
#

throttledFile = None
CPUFreqFile = None


currentCPUTemp 		= 0.0
currentRSSI 		= []
currentQuality 		= []
currentBitRate 		= []
currentTXPower 		= []
currentWiFiFrequency= []
currentUsageData	= None
currentCPUUsage	 	= -1
currentCPUFreq 		= 0

for s in RSSIInterfaceName:	# make sure we have a previous value for each wireless lan interface
	currentRSSI.append( 0)
	currentQuality.append( 0)
	currentBitRate.append( 0)
	currentTXPower.append( 0)
	currentWiFiFrequency.append( 0)
	



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
	
	try:
		throttledFile = open( "/sys/devices/platform/soc/soc:firmware/get_throttled")
	except Exception as e:
		xtension.writeLog( "error opening throttled information file: %s" % e)

	
	if throttledFile != None:
		epoll.register( throttledFile.fileno(), select.EPOLLPRI | select.EPOLLERR)
	

	while True:
		skipOtherPolls = False # when the epoll.poll returns something it may be much faster than we want to count other seconds			
		for fd, event in epoll.poll( 1):
			print( " -- fd=%s event=%s" % (fd, event))
			skipOtherPolls = True

			if throttledFile != None and fd == throttledFile.fileno():
				processThrottledFile()

		if skipOtherPolls:
			continue
				
		if checkCPUTemp:
			CPUCheckCounter += 1
			if CPUCheckCounter >= CPUTempScanSeconds:
				processCPUTemp()
				CPUCheckCounter = 0
		
		
		if checkRSSI:
			RSSICheckCounter += 1
			if RSSICheckCounter >= RSSIScanSeconds:
				processRSSI()
				RSSICheckCounter = 0
		
		
		
		if checkCPUUsage:
			CPUUsageCounter += 1
			if CPUUsageCounter >= CPUUsageScanSeconds:
				processCPUUsage()
				CPUUsageCounter = 0
					


	if throtteledFile != None:
		epoll.unregisterFile( throttledFile.fileno())
		throttledFile.close()
	


#
#	not everything works to see a change like the throttled file
#	so some must just be checked at intervals
#
# def nonSelectFileThread():
# 
# 	# Force to run after one second to prime the pump
# 	CPUCheckCounter 	= CPUTempScanSeconds
# 	RSSICheckCounter 	= RSSIScanSeconds
# 	CPUUsageCounter 	= CPUUsageScanSeconds
# 
# 	while True:
# 		sleep( 1)
# 		
# 		# do this every second
# 		# processCPUFreqFile()
# 		
# 		if checkCPUTemp:
# 			CPUCheckCounter += 1
# 			if CPUCheckCounter >= CPUTempScanSeconds:
# 				processCPUTemp()
# 				CPUCheckCounter = 0
# 		
# 		
# 		if checkRSSI:
# 			RSSICheckCounter += 1
# 			if RSSICheckCounter >= RSSIScanSeconds:
# 				processRSSI()
# 				RSSICheckCounter = 0
# 		
# 		
# 		
# 		if checkCPUUsage:
# 			CPUUsageCounter += 1
# 			if CPUUsageCounter >= CPUUsageScanSeconds:
# 				processCPUUsage()
# 				CPUUsageCounter = 0
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
					print( "%s Freq: %s" % ( thisAddress, value))
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
			
			if checkRSSI and 'Signal level=' in workLine:
				value = int( workLine.split( 'Signal level=')[1].split( ' dBm')[0])
				
				if value != currentRSSI[ i]:
					thisAddress = addrRSSI + '.' + thisName
					currentRSSI[ i] = value
					print( "%s RSSI: %s" % (thisAddress, value))
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
					
			if showBitRate and 'Bit Rate=' in workLine:
				value = float( workLine.split( 'Bit Rate=')[1].split( ' Mb/s')[0])
				
				if value != currentBitRate[ i]:
					thisAddress = addrLinkRate + '.' + thisName
					currentBitRate[ i] = value
					print( "%s BitRate: %s" % (thisAddress, value))
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
					
			if showTXPower and 'Tx-Power=' in workLine:
				value = int( workLine.split( 'Tx-Power=')[1].split( ' dBm')[0])
				
				if value != currentTXPower[ i]:
					currentTXPower[ i] = value
					thisAddress = addrTXPower + '.' + thisName
					print( "%s TX Power: %s" % (thisAddress, value))
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
					
			if showLinkQuality and 'Link Quality=' in workLine:
				s = workLine.split( 'Link Quality=')[1].split( ' ')[0].split( '/')
				value = round( ( float( s[0]) / float( s[1]) * 100))
				
				if value != currentQuality[ i]:
					currentQuality[ i] = value
					thisAddress = addrLinkQuality + '.' + thisName
					print( "%s Quality: %s" % (thisAddress, value))
					xtension.sendValue( value=value, tag=xtension.tagRegister, address=thisAddress, keyUpdateOnly=True)
			
				
				
			
			





		# address format is "RSSI.WLAN0" so that if we have multiple ones
		# with different names they can coexist in XTension
# 		thisAddress = addrRSSI + '.' + thisName
		
		# so it turns out that iwlist is not the right thing to use for this
		# we want the information from iwconfig instead as it is faster and contains only 
		# our currently connected to device
	
# 		process = Popen( ['iwlist', thisName, 'scan'], stdout=PIPE, stderr=PIPE)
# 		output, _error = process.communicate()
# 		output = output.decode()
# 	
# 		lines = output.split( '\n')
# 		for s in lines:
# 			if "Signal level=" in s:
# 				thisLevel = s.split( 'Signal level=', 2)[1]
# 				thisLevel = int( thisLevel.split( ' ', 2)[0])
# 				break
# 	
# 		if thisLevel == 255: # an error reading the RSSI or there is no interface currently by this name
# 			continue
# 		
# 		if thisLevel != currentRSSI:
# 			currentRSSI[ i] = thisLevel
# 			xtension.sendValue( value=thisLevel, tag=xtension.tagRegister, address=thisAddress)
# 			print( "RSSI: %s" % theLevel)
			




def processCPUTemp():
	global currentCPUTemp

	CPUTempFile = open( '/sys/class/thermal/thermal_zone0/temp')
	tempInC = round( float( CPUTempFile.read().strip()) / 100) / 10
	CPUTempFile.close()
	tempInF = CtoF( tempInC)
	
		
	if showTempsinF:
		displayTemp = tempInF
		augTemp = tempInC
		primarySuffix = '°F'
		secondarySuffix = '°C'
	else:
		displayTemp = tempInC
		augTemp = tempInF
		primarySuffix = '°C'
		secondarySuffix = '°F'


	print( "CPU: %s" % displayTemp)
	
	if displayTemp != currentCPUTemp:
		currentCPUTemp = displayTemp
		if alsoShowInOtherScale:
			xtension.sendValue( value=displayTemp, tag=xtension.tagTemperature, address=addrCPUTEMP,
				xtKeyDefaultLabel='%s%s (%s%s)' % (displayTemp, primarySuffix, augTemp, secondarySuffix))
		else:
			xtension.sendValue( value=displayTemp, tag=xtension.tagTemperature, address=addrCPUTEMP, xtKeyDefaultLabel='')

def CtoF( inTemp):
	inTemp = 9.0 / 5.0 * inTemp + 32
	return round( (inTemp * 10)) / 10
	

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
				print( "CPU Freq: %s" % newFreq)
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




def processCPUUsage():
	global currentUsageData
	global currentCPUUsage
	
	with open( '/proc/stat') as f:
		rawValues = f.read().strip().split( '\n')[0]
		
	#print( "RAW (%s)" % rawValues)
	
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





def readHostnameInline():
	global currentHostname
	try:
		file = open( "/etc/hostname")
	except:
		print( "no hostname file found")
		sys.exit( 1)
		
	currentHostname = file.read().strip()
	file.close


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
			kInfoDimmable:True, kInfoSuffix:'°F', kInfoIgnoreClicks:True, kInfoReceiveOnly:True,}]
			
	if checkRSSI:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi RSSI ' + thisInterface
			thisAddress = addrRSSI + '.' + thisInterface
			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' dBm', kInfoIgnoreClicks:True, kInfoReceiveOnly:True}]
				
	if showBitRate:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi Bit Rate ' + thisInterface
			thisAddress = addrLinkRate + '.' + thisInterface
			
			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' Mb/s', kInfoIgnoreClicks:True, kInfoReceiveOnly:True}]
				
	if showTXPower:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi TX Power ' + thisInterface
			thisAddress = addrTXPower + '.' + thisInterface

			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' dBm', kInfoIgnoreClicks:True, kInfoReceiveOnly:True}]
				
	if showLinkQuality:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi Link Quality ' + thisInterface
			thisAddress = addrLinkQuality + '.' + thisInterface

			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:'%', kInfoIgnoreClicks:True, kInfoReceiveOnly:True}]
	
	if showWiFiFrequency:
		for thisInterface in RSSIInterfaceName:
			thisName = 'WiFi Frequency ' + thisInterface
			thisAddress = addrWiFiFreq + '.' + thisInterface

			units += [{kInfoName:thisName, kInfoTag:xtension.tagRegister, kInfoAddress:thisAddress, 
				kInfoDimmable:True, kInfoSuffix:' GHz', kInfoIgnoreClicks:True, kInfoReceiveOnly:True}]

	if checkCPUUsage:
		units += [{kInfoName:'CPU Idle', kInfoTag:xtension.tagRegister, kInfoAddress:addrCPUUsage, 
			kInfoDimmable:True, kInfoSuffix:'%', kInfoIgnoreClicks:True, kInfoReceiveOnly:True}]
			
	if checkCPUFrequency:
		units += [{kInfoName:'CPU Frequency', kInfoTag:xtension.tagRegister, kInfoAddress:addrFrequency, 
			kInfoDimmable:True,	kInfoIgnoreClicks:True, kInfoReceiveOnly:True, kInfoSuffix:' MHz'}]

	
	work[ 'units'] = units
	
	return work
	
	



def ParseThrottleStatus(status):
	StatusStr = ""

	if (status == 0):
		StatusStr += "No Problems"

	if (status & 0x40000):
		StatusStr += "Throttling has occured. "
	if (status & 0x20000):
		StatusStr += "ARM freqency capping has occured. "
	if (status & 0x10000):
		StatusStr += "Undervoltage has occured. "
	if (status & 0x4):
		StatusStr += "Active throttling. "
	if (status & 0x2):
		StatusStr += "Active ARM frequency capped. "
	if (status & 0x1):
		StatusStr += "Active undervoltage. "

	return StatusStr



print( "begin")

# if the user has not set it then we will do so from the machine hostname
if currentHostname == None:
	readHostnameInline()

xtension = XTension( deviceName=currentHostname)
xtension.callbackGetInfo = getInfoForXTension

xtension.startup()

# give it a moment to actually find XTension so that initial values can be sent
sleep( 2)

print( "starting watcher threads")

# this is now handled inline with the regular fileWatcherThread so less threads needed
# secondaryWatcherThread = Thread( target=nonSelectFileThread, args=())
# secondaryWatcherThread.start()


fileWatcherThread = Thread( target=threadedFileWatcher, args=())
fileWatcherThread.start()

if checkCPUFrequency:
	CPUSpeedThread = Thread( target=processCPUFreqFile, args=())
	CPUSpeedThread.start()

print( "hostname is: %s" % currentHostname)


	
	








