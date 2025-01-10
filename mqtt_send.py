from paho.mqtt import client as mqtt_client
import json

client_id = f'scenario-dash'
broker = '192.168.3.1'
topic = 'scenario_dash'

client = mqtt_client.Client(client_id)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True #set flag
        print("Connected OK")
#        client.subscribe(cmnd_topic + "#", qos=0)
#        client.subscribe(its_topic, qos=0)
        try:
            client.publish("tele/" + topic + "/LWT", "Online", retain=1)
        except:
            print("Cannot set topic 'tele/%r/LWT'" % topic)
    else:
        print("Bad connection, Returned code %r" % rc)

def on_message(client, userdata, message):
    pass

def send_msg(t, msg):
    client.publish(f'set/{topic}/{t}', json.dumps(msg, separators=(',', ':'), ensure_ascii=False))

client.will_set("tele/" + topic + "/LWT", "Offline", 0, True)
client.connected_flag = False
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker)
client.loop_start()


