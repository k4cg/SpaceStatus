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

# callback functions
def on_message(client, userdata, msg):
    sensors = conf["sensors"]
    for sensor in sensors.keys():
        if msg.topic == sensors[sensor]["topic"]:
            if sensors[sensor]["msg_type"] == "json":
                resp = json.loads(msg.payload.decode("utf-8"))
                resp = resp[sensors[sensor]["src_field"]]
            else:
                resp = msg.payload.decode("utf-8")
                status.update({sensors[sensor]["dst_field"]: resp})
        else:
            print("topic: ", msg.topic, "message: ", str(msg.payload.decode("utf-8")))

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
        client.loop(5)
        write_status(status=status,path=conf['output'])
