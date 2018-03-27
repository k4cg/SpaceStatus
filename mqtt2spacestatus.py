#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import datetime
import paho.mqtt.client as paho
import yaml
import json


def read_configuration(path="config.yaml"):
    """
    opens and reads yaml configuration file
    :path: str
    :returns: dict
    """
    with open(path) as conffile:
        conf = yaml.load(conffile)

    return conf

def read_status(path="status.json"):
    """
    opens the written status file in case of restarts
    that we do not start with an empty status file.
    If there is no file, create empty status dict
    :path: str
    :returns: dict
    """
    try:
        with open(path, "r") as jsonfile:
            status = json.load(jsonfile)
    except IOError:
        status = {}

    return status

def write_status(status, path="status.json"):
    """
    Persists the current status to the json file
    and adds the latest timestamp
    :status: dict
    :returns: boolean
    """

    status.update({"date": datetime.datetime.now().isoformat()})
    with open(path, "w") as jsonfile:
        jsonfile.write(json.dumps(status))

    return True

def handler_temperature(msg):
    """
    Parses temperature message from topic
    and sends back formatted json data for status.json
    :msg: message object from mqtt
    :returns: dict
    """

    resp = json.loads(msg.payload.decode("utf-8"))
    resp = resp["temperature"] / 100
    resp = { "temperature": resp }
    return resp

def handler_sound(msg):
    """
    Parses sound message from topic
    and sends back formatted json data for status.json
    :msg: message object from mqtt
    :returns: dict
    """

    resp = json.loads(msg.payload.decode("utf-8"))
    resp = resp["intensity"]
    resp = { "sound": resp }
    return resp

def handler_light(msg):
    """
    Parses light message from topic
    and sends back formatted json data for status.json
    :msg: message object from mqtt
    :returns: dict
    """

    resp = json.loads(msg.payload.decode("utf-8"))
    resp = resp["uv_light"]
    resp = { "light": resp }
    return resp

def handler_humidity(msg):
    """
    Parses humidity message from topic
    and sends back formatted json data for status.json
    :msg: message object from mqtt
    :returns: dict
    """

    resp = json.loads(msg.payload.decode("utf-8"))
    resp = float(resp["value"])
    resp = { "humidity": resp }
    return resp

def handler_hosts(msg):
    """
    Parses hosts message from topic
    and sends back formatted json data for status.json
    :msg: message object from mqtt
    :returns: dict
    """

    resp = json.loads(msg.payload.decode("utf-8"))
    resp = float(resp["online"])
    resp = { "online": resp }
    return resp

def handler_door(msg):
    """
    Parses door message from topic
    and sends back formatted json data for status.json
    :msg: message object from mqtt
    :returns: dict
    """

    resp = json.loads(msg.payload.decode("utf-8"))
    resp = resp["value"]
    resp = { "door": resp }
    return resp

### On Message Parser
def on_message(client, userdata, msg):
    """
    This function parses all messages coming from the subscribed mqtt topics
    and hands them over to the correct handler
    :client: paho mqtt object
    :userdata:
    :msg: paho message object
    :returns: boolean
    """

    # debug
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            print("topic: ", msg.topic, "message: ", str(msg.payload.decode("utf-8")))

    # Pattern match on topic and give message to corresponding handler
    if msg.topic == "sensors/tischtennis/bricklet/temperature/tfj/temperature":
        doc = handler_temperature(msg)
    elif msg.topic == "sensors/tischtennis/bricklet/sound_intensity/voE/intensity":
        doc = handler_sound(msg)
    elif msg.topic == "sensors/tischtennis/bricklet/uv_light/xpa/uv_light":
        doc = handler_light(msg)
    elif msg.topic == "sensors/door/default/bme280/humidity":
        doc = handler_humidity(msg)
    elif msg.topic == "sensors/wifi/online":
        doc = handler_hosts(msg)
    elif msg.topic == "sensors/door/default/status":
        doc = handler_door(msg)
    else:
        doc = {}

    # update internal dict with latest data (any)
    status.update(doc)

    return True


def on_connect(client, userdata, flags, rc):
    subscription_result = client.subscribe("sensors/#")

if __name__ == "__main__":

    conf = read_configuration()
    status = read_status()

    client = paho.Client(conf['username'])
    client.username_pw_set(conf['username'], conf['password'])
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(conf['broker'])

    while True:
        client.loop(30)
        write_status(status=status,path=conf['output'])
