#!/usr/bin/env python2.7
"""
openstatus.py collects devices in our k4cg-intern wifi
and generates json output into a documentroot
that rezeptionistin can read

at a later point we can also work with the collected
data in a statistical way.
"""

import sys
import json
import datetime
import requests
import warnings

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_accelerometer import BrickletAccelerometer
from tinkerforge.bricklet_sound_intensity import BrickletSoundIntensity
from tinkerforge.bricklet_uv_light import BrickletUVLight

from paho.mqtt import client as mqttc

class NetworkScanner(object):
    """
    Scans the network for hosts
    """

    def __init__(self):
        """ Define network and machine specific parameters """
        self.ap_ip= "192.168.178.2"
        self.hosts = dict()
        self.login = 'https://192.168.178.2/login.cgi'
        self.user = sys.argv[1]
        self.pw = sys.argv[2]
        self.static_hosts = []

    def get_hosts(self):
        """
        Return hosts in the network
        :returns: list
        """
        # arrange new session and login
        s = requests.Session()
        ans = s.get(self.login, verify=False)
        print ans

        # query ip/status.cgi which results in json
        r = s.post(self.login, verify=False, data={'username': self.user, 'password': self.pw, 'uri':'/status.cgi'}).text
        #print r
        r = json.loads(r)

        # fetch count of wireless connections from json
        self.hosts = r['wireless']['count']
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
            self.ipcon.disconnect()
            uv_light = uvl.get_uv_light()
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

warnings.filterwarnings('ignore', 'Unverified HTTPS request')

# Scan network
sc = NetworkScanner()
hosts = sc.get_hosts()

se = Sensors()
date = datetime.datetime.now().isoformat()
sound = se.get_sound()
light = se.get_light()
temp = se.get_temperature()

cli = mqttc.Client("spacestatus", clean_session=False)
cli.username_pw_set("spacestatus", sys.argv[3])
cli.connect("heimat", port=1883)
cli.publish("sensors/spacestatus/online", payload=date+" "+str(hosts), retain=True)
cli.publish("sensors/spacestatus/sound", payload=date+" "+str(sound), retain=True)
cli.publish("sensors/spacestatus/light", payload=date+" "+str(light), retain=True)
cli.publish("sensors/spacestatus/temp", payload=date+" "+str(temp), retain=True)

