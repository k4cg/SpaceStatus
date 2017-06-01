#!/usr/bin/env python2.7
"""
openstatus.py collects devices in our k4cg-intern wifi
and generates json output into a documentroot
that rezeptionistin can read

at a later point we can also work with the collected
data in a statistical way.
"""

import re
import commands
import json
import datetime
import requests

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_accelerometer import BrickletAccelerometer
from tinkerforge.bricklet_sound_intensity import BrickletSoundIntensity
from tinkerforge.bricklet_uv_light import BrickletUVLight

class NetworkScanner(object):
    """
    Scans the network for hosts
    """

    def __init__(self):
        """ Define network and machine specific parameters """
        self.network = "192.168.178.0/24"
        self.interface = "vio0"
        self.hosts = dict()
        self.static_hosts = [
		]

        # for performance reasons, we currently disable nmap
        # self.scan_nmap()
        self.scan_arp()

    def substract_static_hosts(self,hosts):
        """ Used for substracting static hosts
        like scotty, heimat, philips hue from the hosts
        :returns: dict
        """
        for host in self.static_hosts:
            try:
                del self.hosts[host]
            except KeyError:
                pass
        return self.hosts


    def scan_nmap(self):
        """ Scan network for Devices with nmap """
        cmd = 'nmap --host-timeout 3 -sP -n %s' % (self.network)
        (status, output) = commands.getstatusoutput(cmd)

        if status:
            sys.stderr.write('Error running nmap command')
            return False

        self.parse_nmap(output)

    def scan_arp(self):
        """ Execute arp scan """
        cmd = "arp -a "
        (status, output) = commands.getstatusoutput(cmd)

        if status:
            sys.stderr.write('Error running arp command')

        self.parse_arp(output)


    def parse_nmap(self, output):
        """ Parse output of nmap to a dictionary """
        matches = re.findall(r'scan report for\s+((?:\d{1,3}\.){3}\d{1,3}).*?MAC Address:\s+((?:[0-9A-F]{2}\:){5}[0-9A-F]{2})', output, re.M | re.S)
        for match in matches:
            ip = match[0]
            self.hosts[ip] = match[1].lower()

    def parse_arp(self, output):
        """ Parse output of arp to a dictionary """
        for e in output.split("\n"):
            if not re.search('expired', e) and re.search(self.interface, e):
                ip = e.split()[0]
                mac = e.split()[1].lower()
                self.hosts[ip] = mac

    def get_hosts(self):
        """
        Return hosts in the network
        :returns: list
        """
        self.hosts = self.substract_static_hosts(self.hosts)
        return self.hosts

class Sensors(object):

    """Docstring for MyClass. """

    def __init__(self):
        self.HOST = "192.168.178.3"
        self.PORT = 4223
        self.TEMP_UID = "tfj"
        self.SOUND_UID = "voE"
        self.LIGHT_UID = "xpa"
        self.ipcon = IPConnection()


    def get_temperature(self):
        try:
            t = BrickletTemperature(self.TEMP_UID, self.ipcon)
            self.ipcon.connect(self.HOST, self.PORT)
            temperature = t.get_temperature()
            self.ipcon.disconnect()
            return float(temperature/100.0)
        except:
            return None


    def get_light(self):
        try:
            uvl = BrickletUVLight(self.LIGHT_UID, self.ipcon)
            self.ipcon.connect(self.HOST, self.PORT)
            uv_light = uvl.get_uv_light()
            self.ipcon.disconnect()
            return float(uv_light)
        except:
            return None

    def get_sound(self):
        try:
            si = BrickletSoundIntensity(self.SOUND_UID, self.ipcon)
            self.ipcon.connect(self.HOST, self.PORT)
            intensity = si.get_intensity()
            self.ipcon.disconnect()
            return float(intensity)
        except:
            return None


def gen_json(hosts, sound, light, temp):
    """
    Generate json documents to output to documentroot
    """
    date = datetime.datetime.now().isoformat()
    document = "/var/www/htdocs/spacestatus/status.json"
    doc = json.dumps({
        "date": date,
        "online": len(hosts),
        "hosts": hosts,
        "sound": sound,
        "light": light,
        "temp": temp,
    })

    with open(document, "w") as f:
        f.write(doc)
        f.close()

    return True


# Scan network
sc = NetworkScanner()
sc.scan_arp()
hosts = sc.get_hosts()

se = Sensors()
sound = se.get_sound()
light = se.get_light()
temp = se.get_temperature()


# Generate output
gen_json(hosts, sound, light, temp)
