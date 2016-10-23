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

class Collector(object):

    """Docstring for Collector. """

    def __init__(self):
        """ Define network and machine specific parameters """
        self.network = "10.88.88.0/24"
        self.interface = "vlan88"
        self.hosts = dict()
        self.json = "/var/www/htdocs/devices/devices.json"
        self.history = "/var/www/htdocs/devices/history.json"
        self.static_hosts = [
                               '10.88.88.254', # Heimat
                               '10.88.88.206', # AP
                               '10.88.88.12', # chromecast
                               '10.88.88.11', # scotty
                               '10.88.88.17', # Hue
                               '10.88.88.14', # Raspi Temperatur
                               '10.88.88.10', # matomat
                               '10.88.88.18', # WLAN AP
			                   '10.88.88.233', # iPad - noqqe 20161022
			                   '10.88.88.64', # KEINE AHNUNG - noqqe 20161022
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


    def gen_json(self):
        """ Generate json documents to output to documentroot """
        self.hosts = self.substract_static_hosts(self.hosts)
        doc = json.dumps({
                            "online": len(self.hosts),
                            "hosts": self.hosts
                         })

        with open(self.json, "w") as f:
            f.write(doc)
            f.close()

        return True

Collector().gen_json()
