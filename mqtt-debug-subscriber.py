#!/usr/bin/env python3
import time
import paho.mqtt.client as paho
import config as cfg

broker = cfg.broker
subscription_topic = cfg.topic

# callback functions
def on_connect(client, userdata, flags, rc):
    if rc == paho.MQTT_ERR_SUCCESS:
        print("successfully connected")
        # subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        print("subscribing to", subscription_topic)
        subscription_result = client.subscribe(subscription_topic)  # (0,1) means success, mid == 1
        # print(subscription_result)
        if subscription_result[0] != paho.MQTT_ERR_SUCCESS:
            print("error subscribing: ", paho.error_string(subscription_result[0]))
    else:
        print("could not connect to broker: ", paho.connack_string(rc))


# callback function (broker response to a subscribe request)
# can be ues to track subscription requests
# via mid returned by corresponding call to client.subscribe()
def on_subscribe(client, userdata, mid, granted_qos):
    print("broker acknowleged subscription")


def on_message(client, userdata, msg):
    print("received message.", "topic: ", msg.topic, "message: ", str(msg.payload.decode("utf-8")))


client = paho.Client("debug-subscriber-001")  # create client object
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message

print("connecting to broker ", broker)
client.connect(broker)  # connect

client.loop_start()  # start loop to process received messages
time.sleep(3600)
client.unsubscribe(subscription_topic)
client.disconnect()  # disconnect
client.loop_stop()  # stop loop
