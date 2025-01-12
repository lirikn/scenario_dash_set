from paho.mqtt import client as mqtt_client
from threading import Thread, Timer, Event
import time
import json

client_id = f'scenario-test'
broker = '192.168.3.1'
topic = 'scenario_test'

client = mqtt_client.Client(client_id)

if_list, then_dict = [], {}

def send_msg(t, msg):
    if t == 'if':
        if_list.append(msg)
    elif t == 'then':
        then_dict.update(msg)
        client.unsubscribe("stat/#")
        client.subscribe("stat/#", qos=0)
    else:
        for line in if_list:
            if line[-1] == msg:
                if_list.remove(line)
        if msg in then_dict:
            del then_dict[msg]

timers = {}
deactivated = set()
#perf = [0, 0]

def stop_scene(name):
    if name in timers:
        timers[name].cancel()
        del timers[name]

def start_task(name, tasks):
    task = tasks.pop(0)
    if scene := task.get('scene'):
        if scene in then_dict:
            if task['action'] == 'включить':
                deactivated.discard(scene)
            elif task['action'] == 'выключить':
                stop_scene(scene)
                deactivated.add(scene)
            elif task['action'] == 'запустить':
                start_scene(scene, then_dict[scene].copy())
            elif task['action'] == 'прервать':
                stop_scene(scene)
    else:
        client.publish(f"cmnd/{task['topic']}/{task['feature']}", task['value'])
#        perf[1] = time.perf_counter()
#        print(perf[1] - perf[0])
    if len(tasks):
        start_scene(name, tasks)
    else:
        stop_scene(name)

def start_scene(name, tasks):
    stop_scene(name)
    if name in deactivated:
        return
    timers[name] = Timer(tasks[0]['delay'], start_task, args = (name, tasks))
    timers[name].start()

def isfloat(val):
    try:
        float(val)
        return True
    except:
        return False

def stat_msg(message):
    for line in if_list:
        condition = False
        for item in line[:-1]:
            if f"stat/{item['topic']}/{item['feature']}" == message.topic:
                value = str(message.payload.decode("utf-8")).split()[0]
                if item['value'][0] in '<>' and isfloat(item['value'][1:]) and isfloat(value):
                    item['condition'] = eval(value + item['value'])
                else:
                    item['condition'] = value == item['value']
                condition = all([x.get('condition') for x in line[:-1]])
        if condition:
            start_scene(line[-1], then_dict[line[-1]].copy())

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True #set flag
        print("Connected OK")
        client.subscribe("stat/#", qos=0)
#        client.subscribe(its_topic, qos=0)
        try:
            client.publish("tele/" + topic + "/LWT", "Online", retain=1)
        except:
            print("Cannot set topic 'tele/%r/LWT'" % topic)
    else:
        print("Bad connection, Returned code %r" % rc)

def on_message(client, userdata, message):
    if message:
#        perf[0] = time.perf_counter()
        Thread(target=stat_msg, args=(message,)).start()


client.will_set("tele/" + topic + "/LWT", "Offline", 0, True)
client.connected_flag = False
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker)
client.loop_start()

