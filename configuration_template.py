#
#		PI MONITOR CONFIGURATION FILE		https://MacHomeAutomation.com
#
#		This program speaks to the xtension kit plugin for XTension and would
#		serve little purpose for anyone not using that.
#
#	to install this file rename from configuration_template.py to configuration.py
#
#		
#
# 	User selectable options for the various functions of the pimonitor application below
#

# OVERRIDE HOSTNAME
#	if this is not set here then the hostname set on the device will be used instead
#	uncomment this and set it if you wish to override that value
#currentHostname 		= "My Pi More Descriptive Name"

# OVERRIDE DEVICE ID
#	normally this is generated automatically from the MAC id of the device. If you wish to 
#	set this manually say when replacing one device with a new one and keep all the unit
#	addresses in XTension the same then set this to the id you wish it to use. These are
#	are by default a 6 digit string made up of the hex of the last 3 octets of the MAC
#	address but this limitation is not hard coded and they could be anything.
#	it will be used by XTension as the second part of every unit address like:
#	CPUUSAGE.123456 where 123456 is the string entered here or calculated
#overrideDeviceId = '123456'


showTempsinF	 		= False 	# display the temperature in F or C. Change to False for C

alsoShowInOtherScale	= True 		# if true then the C or F value, whichever is the one  
									# you did not select for the actual value will be displayed 
									# in the value string for the unit, but the numeric value 
									# for the unit will still be the one you selected above. 
									# For example without this the display will be
									# "53°C" or "127.4°F" With this turned on the display 
									# in XTension will instead show 
									# "53°C (127.4°F)" or "127.4°F (53°C)"
									# Note that pi thermal throttling starts around 80°C as of this writing

#
# CPU TEMPERATURE
# how often to check for a change to the CPU Temperature
#
checkCPUTemp			= True
CPUTempScanSeconds		= 10



#
#	WiFi RSSI
#
# how often to check the RSSI level
#
# name of the interface to scan RSSI on
# this is usually 'wlan0' but if you have unique interface names turned on or are using 
# external adaptors or have multiple wifi devices then this may be different
# NOTE that this value must be a python list even with just one element
# if you have multiple wireless lans you wish to check you can enter more in the list
# something like: ['wlan0', 'wlan1', 'wlan2']
RSSIInterfaceName 		= ['wlan0']
RSSIScanSeconds 		= 10
checkRSSI 				= True
showBitRate 			= True
showTXPower 			= True
showLinkQuality 		= True
showWiFiFrequency 		= True



# CPU Usage 
checkCPUUsage 			= True
CPUUsageScanSeconds 	= 10

# CPU Frequency
# this can change very rapidly and is more of an indication of the load on the machine as even the 
# fastest pi will throttle back when it's mostly idle. While you can set the speed to be very fast to catch
# rapid changes that can occur in the course of normal operation keep in mind the XTdb will not record values
# faster than once a second so it may not be useful to scan faster than that unless you want to 

checkCPUFrequency 		= False
CPUFrequencyScanSeconds	= 0.2

#
#	Disk Space
#
checkDiskSpace 			= True
diskScanSeconds 		= 60
volumesToScan 			= ['/']





