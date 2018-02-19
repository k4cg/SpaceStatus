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
from tinkerforge.bricklet_sound_intensity import BrickletSoundIntensity
from tinkerforge.bricklet_uv_light import BrickletUVLight

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
        s.get(self.login, verify=False)

        # query ip/status.cgi which results in json
        r = s.post(self.login, verify=False, data={'username': self.user, 'password': self.pw, 'uri':'status.cgi'}).text
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

class HeimatlicherServierer(object):
    def __init__(self):
        pass

    def get_hservierer_status(self):
        hserv_doc = "/var/www/htdocs/spacestatus/heimatlicher_status.json"
        try:
            with open(hserv_doc, "r") as f:
                data = json.loads(f.read())
            return data
        except:
            return None

def gen_json(hosts, sound, light, temp, hserv):
    """
    Generate json documents to output to documentroot
    """
    date = datetime.datetime.now().isoformat()
    document = "/var/www/htdocs/spacestatus/status.json"

    with open(document, "r") as f:
        doc_data = json.loads(f.read())

    doc_data.update({
        "date": date,
        "online": hosts,
        "hosts": [], # spec ip addresses dont work anymore
        "sound": sound,
        "light": light,
        "temp": temp,
        "hservierer" : hserv
    })

    with open(document, "w") as f:
        f.write(json.dumps(doc_data))
        f.close()

    return True

warnings.filterwarnings('ignore', 'Unverified HTTPS request')

# Scan network
sc = NetworkScanner()
hosts = sc.get_hosts()

se = Sensors()
sound = se.get_sound()
light = se.get_light()
temp = se.get_temperature()

# get data from heimatlicher servierer
hs = HeimatlicherServierer()
hsdata = hs.get_hservierer_status()

# Generate output
gen_json(hosts, sound, light, temp, hsdata)
