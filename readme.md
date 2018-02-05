# SpaceStatus

spacestatus.py collects various data and puts them into a json format.
spacestatus_mqtt.py collects the same data and pushed it to an mqtt server.

# The measurements

* Temperature
* UV Light
* Devices in Wifi network
* Sound intensity
* another temperature

# Method for wifi collection

At the moment only arp information is used.
for performance reasons nmap scan is deactivated

# Thanks

... to our friends from @b4ckspace, for providing the idea, some of the implementation
and hints.

