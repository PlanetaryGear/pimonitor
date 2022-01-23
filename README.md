# PiMonitor
PiMonitor is a python script that runs on the Raspberry Pi and sends various status and informational data to a local machine running 
[XTension](https://MacHomeAutomation.com/) A home automation program for the Macintosh. If you are not running XTension it is unlikely to be
of any great interest.

PiMonitor will let you track things like undervoltage or over temp throttling of the pi which is hard to see when you're running a headless pi or one that
does not have the desktop interface installed. It will also allow you to monitor CPU usage, temperature and disk space usage as well as WiFi signal strength and link quality.
Additionally it can monitor the CPU frequency as it is changed due to CPU load. This changes very quickly therefore creating some load on the network and the XTension
machine so it may not be useful except under certain debugging situations.

## XTension Setup
PiMonitor requires at least one instance of XTension 9.4.44 or newer running on the same subnet as the raspberry pi. To receive the information you must 
have a single instance of the XTension Kits plugin running in it. Only a single instance of the plugin running in XTension is required for any
number of PiMonitor or other kit protocol enabled devices. You do not need a separate plugin setup for each device.

## Raspberry Pi Installation
PiMonitor uses Python3 and runs fine in the slightly older version that is included in the standard Raspberry Pi install image.
No other python packages are needed beyond the default ones.

### Installing via git:
Git is not part of the standard raspberry pi image so you may first need to install git via:
```sudo apt install git```

From your home directory at `/home/pi` run the following:

```git clone https://github.com/PlanetaryGear/pimonitor.git```

To update a current install to the latest commit enter the pimonitor directory and enter:

```git pull```


### Installing via curl:
To download the files as a zip file use the "Download Zip" option in the header of the main page above, or use curl from your command line. 
In your `/home/pi` directory execute:

```curl -L --output pimonitor.zip https://github.com/PlanetaryGear/pimonitor/archive/refs/heads/main.zip```

The -L switch tells curl to follow the redirect that will happen to the server that will actually host the file, the --output portion tells
curl where to put the output file. Unzip the file with the unzip command:

```unzip pimonitor.zip``` 

This will create a folder called "pimonitor-main" which you then need to rename to just pimonitor like:

```mv pimonitor-main pimonitor```

### Run At Startup
If you wish to test your install and configuration you can run the program from the command line. It is required to run as root in order to read some of this
information so to test it from inside the pimonitor directory use a command like:

```sudo python3 ./pimonitor.py```

Some debugging output may be generated at the console but most info will go to XTension. You'll see the units created in XTension within a few seconds. 
To quit the program use ctrl-c.

You may wish to complete the configuration via the configuration.py file as described below before running the program the first time so that the appropriate
units with the appropriate names will be created in XTension rather than potentially some that you do not want or with some incorrect name or ID.

To run the program automatically at startup we need to register it with the systemctl system. The service file is included with the distribution and is called
`pimonitor.service` If you have changed the default install location from the default of `/home/pi/pimonitor/pimonitor.py` you will need to edit this 
file to point to the new location. If not you can use it as given. Skip the last step to start the program if you have not yet edited the configuration file. 
From inside the pimonitor directory run the following commands:

```
sudo cp ./pimonitor.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pimonitor
sudo systenctl start pimonitor
```



At this point the program will be running, unless you have skipped the start command until after configuration is complete, and it will be started 
with each boot of the Pi.


## Units Created In XTension:
![XTension Units Screenshot](/pimonitor-xtension-units.png)

- **Status Unit:** The first unit created shows the online/offline status of the pi. If the program is quit normally via a reboot or other shutdown this will turn off
and show a label of offline. If the pi hangs or drops off the network for more than 4 minutes the unit will timeout and switch to offline as well.
- **Active Undervoltage**: Will be on if the pi is currently in an undervoltage state. This can switch on and off rapidly as the problem comes and goes with varied load.
- **Undervoltage Has Occurred:** Will be on if the pi has had any undervoltage events since the last reboot.
- **Active Throttling:** Will be on if the pi is currently in a speed throttled state.
- **Throttling Has Occurred:** Will be on if the pi has had any throttling events since the last reboot.
- **Active CPU Speed Capping:** Will be on if the pi has had it's speed capped at any time since the last reboot.
- **CPU Speed Capping Has Occcurred:** Will be on if the pi has had any speed capping events since it's last reboot.

The first 7 units above will always be created, the following ones will either be present or not, or others may be present depending on your configuration.

- **CPU Temperature:** The CPU temperature as reported by the pi, in whatever format and label settings that you set in the configuration file below.
- **WiFi RSSI:** The RSSI in dbm as read from the configured WiFi interface. Numbers closer to 0 are better.
- **WiFi Bit Rate:** The bit rate that the wifi is currently running as. Very low nubers may indicate a reception or link quality issue.
- **WiFi TX Power:** How much power the wifi has to broadcast to reliably reach the access point.
- **WiFi Link Quality:** A simple percent value taking into account the other values.
- **WiFi Frequency:** The channel that the WiFi radio is operating on
- **CPU Frequency:** Turned off by default in the configuration, the speed the CPU is currently running at. This will change rapidly according to the load the device is under.
- **CPU Idle:** The percent idle of the CPU if turned on in the configuration file.
- **Disk Space:** A Disk Space unit will be created for each mount point that you setup to be scanned for disk space usage. The default name of the unit will be the hostname of the
pi, "Disk Space" and the path to the mountpoint.

**Note that the standard default naming convention for new units is the hostanme of the pi and then the descriptive name along with any other information needed.
Once the units are created new information is targeted to them via their Address and not their name. You can edit the name at any time to be more descriptive or
useful to you.**



## Configuration
If you wish to run with the default configuration you can skip this step.

Move into the pimonitor directory with `cd pimonitor` and copy the default configuration file to one we can edit with:

```cp configuration_template.py configuration.py```

Note that at the moment this is a python file that is just included into the running app so you need to follow python syntax rules
or you will get an error at startup. If the app cannot load the configuration.py file for any reason either that it does not exist 
or if you write something that does not compile it will load the default configuration file instead.

To edit the configuration file from the `/home/pi/pimonitor` folder use nano or your editor of choice to edit the file:

```nano configuration.py```

**Note that the configuration names are case sensitive. Booleans are case sensitive as well and must be "True" or "False". Just "true" or "false" will generate
an error upon loading the configuration file.**

- **Override Hostname:** By default the hostname of the device is used to name the units created in XTension. If you wish to use a different, or more descriptive name for the unit name prefix in XTension you can uncomment this line and enter any reasonable string to use instead.
  - ```overrideHostname = "A More Descriptive Name Here"```

- **Override Device ID:**
Every unit in XTension must have a unique ID or Address. By default the MAC address of the Pi is used to create a unique 6 character hex string that is appended
to the other info to create a unique address for each data point and each pi that you are monitoring. If you replace one pi with another or if you replace
one network adaptor with another you may wish to keep the previous ID so that the current units in XTension are used rather than new units being created
with the new address. If so uncomment this line and enter the previous id. Note that the IDs are not case sensitive but will be converted to all upper case 
by XTension.

  - ```overrideDeviceId = "123456" # the id of the previously used pi```

- **Show Temps In F:**
Change to True in order to display the temperature
in °F rather than °C. But before you decide to display in F see the next option which will let you see it in both formats in XTension.

  - ```showTempsInF = False```

- **Also Show In Other Scale:**
I find it useful to see the temperatures in °C as the published infor for when the Pi starts temperature throttling is published in C. So I know as it aproaches
80°C I'm in potential trouble. However being from America I don't think in Celcius so to have an idea of what the temperature really is I like to also see it in 
F. If this option is turned on then the actual value of the Unit in XTension will be set to the format you have chosen in the previous option, but the label
displayed in any value column in XTension or the web interfaces will include the other format as well. For example: if you have showTempsInF set to false and this 
set to true the value of the Unit will be in C, but the label of the value will show "53°C (127.4°F)" or if showTempsInF is set to True then the label will be
"127.4°F (53°C)"

  - ```alsoShowInOtherScale = True```

- **Check CPU Temp:**
Set to false if you do not wish to regularly check the CPU temperature.

  - ```checkCPUTemp = True```

- **CPU Temp Scan Seconds:**
How often do you wish to check the CPU temperature. This must be an integer value of the seconds between checks of the CPU temp. An update to XTension is only
sent if the new value read is different from the previously sent value so you will not necessarily be receiving an update in XTension this often.

  - ```CPUTempScanSeconds = 10```

- **RSSI Interface Name:**
If you are using WiFi to connect the Pi it can be useful to watch the RSSI and link quality to look for changes. This value is a Python list and can include any
number of wifi interfaces that support getting this information. If you have enabled the unique interface names then you may have to edit this name
to be the unique name it assigns to your wifi interface. If you are using the default interface naming conventions and have only a single
WiFi interface then the default will likely work as is. If you are using Ethernet or do not wish to scan the WiFi set this to an empty list like `[]`

  - ```RSSIInterfaceName = ['wlan0'] # scan just the default interface```
  - ```RSSIInterfaceName = [] # do not scan any interfaces```
  - ```RSSIInterfaceName = ['wlan0', 'wlan1', 'wlan2'] # scan 3 different wifi interfaces```


- **RSSI Scan Seconds:**
How often in seconds to scan the WiFi information. This must be an integer. Only values that have changed since the last scan are sent as updates to their units
in XTension.

  - ```RSSIScanSeconds = 10```

- **Check RSSI:**
If you do not wish to create a unit for the RSSI value set this to False. The other values, if any, that are enabled will still be scanned.

  - ```checkRSSI = True```

- **Show Bit Rate:**
If you do not wish to create a unit for the Bit Rate of the interface set this to False. 

  - ```showBitRate = True```

- **Show TX Power:**
If you do not wish to create a unit for the transmit power being used set this to False.

  - ```showTXPower = True```

- **Show Link Quality:**
The link quality is a percentage and is very useful for tracking issues as it is easy to see and immediately understand unlike the RSSI value.

  - ```showLinkQuality = True```

- **Show Wifi Frequency:**
This can show you what channel is being used to connect and therefore which access point it is connected to, though this may change from the Access Point
randomly as well. 

  - ```showWiFiFrequency = True```

- **Check CPU Usage:**
Set to false if you do not wish to scan the CPU usage. This is the percent of the time the CPU is idle. So a reading of 100% is a CPU that is doing practically nothing.

  - ```checkCPUUsage = True```

- **CPU Usage Scan Seconds:**
How often in seconds you wish to scan the CPU Usage

  - ```CPUUsageScanSeconds = 10```

- **Check CPU Frequency:**
Set to True if you wish to also watch the CPU speed change. This can change very rapidly generating a lot of traffic and potentially load in XTension. Since this
has to be a regular check and cannot be triggered by an event when the speed changes you may miss very rapid changes as well. In XTension and XTdb the limit for
saving data is one value a second and this can change much more rapidly than that so quick changes may not register properly in the database and graph displays. Use
for debugging purposes if necessary but disabled by default.

  - ```checkCPUFrequency = False```

- **CPU Frequency Scan Seconds:**
See the above for discussion about this. Unlike all the other scan intervals this is a float value of seconds so you can scan the CPU speed much faster than the
other values. Setting it too fast will cause the process to use a lot more CPU and it may still miss quick bumbs in CPU speed.

  - ```CPUFrequencyScanSeconds = 0.2```

- **Check Disk Space:**
Any number of mount points can be checked for available space on a regular basis as well. The value sent to the Unit in XTension will be the number of k that is available
on the drive. The label in XTension will be a more human readable version like "45 MB" or "6.5 GB.

  - ```checkDiskSpace = True```

- **Disk Scan Seconds:**
How often in seconds do you wish to scan the drives for changes in usage. This must be an integer number of seconds.

  - ```diskScanSeconds = 60```

- **Volumes To Scan:**
This is a python list of the mount points that you wish to scan. By default only the root volume is scanned but if you have configured other mount points they
can be added to this list. See the RSSIInterfaceName entry above for more info on making syntactically correct python lists.

  - ```volumesToScan = ['/']```

