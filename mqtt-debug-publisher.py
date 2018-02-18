#!/usr/bin/env python3
import paho.mqtt.publish as paho
import config as cfg

broker = cfg.broker
topic = cfg.topic

paho.single(topic, "__door-closed__", hostname=cfg.broker)
