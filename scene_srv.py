#! /usr/bin/python3

from paho.mqtt import client as mqtt_client
from threading import Thread, Timer
import time
import json

client_id = f'scenario_server'
broker = '192.168.3.1'
topic = 'scene_srv'
#set_topic = 'scenario_dash'
scenes_file = 'scenes.json'


client = mqtt_client.Client(client_id)

timers = {}
actions = {}
pub_time = 0


try:
    with open(scenes_file) as json_file:
        scenes = json.load(json_file)
except:
    scenes = [[], {}]

if_list, then_dict = scenes

def save_scene():
    with open(scenes_file, 'w') as json_file:
        json.dump(scenes, json_file, ensure_ascii=False, indent=4)

def stop_scene(name):
    if name in timers:
        timers.pop(name).cancel()

def action_set(name, action):
#    print(name, action)
    if action == 'activate':
        actions[name] = 'idle'
    elif action == 'delete':
        stop_scene(name)
        del actions[name]
    elif actions.get(name) == 'deactivated':
        return
    elif action == 'deactivate':
        actions[name] = 'deactivated'
        stop_scene(name)
    elif action == 'start':
        actions[name] = 'run'
        start_scene(name, then_dict[name].copy())
    elif action in ('stop', 'save'):
        actions[name] = 'idle'
        stop_scene(name)
    global pub_time
    pub_time = time.time()

def cmnd_msg(message):
    action = message.topic.split('/')[-1]
    msg = json.loads(str(message.payload.decode("utf-8")))
    print(msg)
    name = msg.pop(0) if isinstance(msg, list) else msg
    action_set(name, action)
    if action not in ('delete', 'save'):
        return
    for line in if_list:
        if line[-1] == name:
            if_list.remove(line)
    if action == 'save':
        then_dict[name] = msg.pop()
        if_list.extend(msg)
        client.unsubscribe("stat/#")
        client.subscribe("stat/#", qos=0)
    else:
        del then_dict[name]
    stop_scene('save_scene')
    timers['save_scene'] = Timer(120, save_scene)
    timers['save_scene'].start()


#perf = [0, 0]

def start_task(name, tasks):
    task = tasks.pop(0)
    if scene := task.get('scene'):
        if scene in then_dict:
            action_set(scene, task['action'])
    else:
        client.publish(f"cmnd/{task['topic']}/{task['feature']}", task['value'])
#        perf[1] = time.perf_counter()
#        print(perf[1] - perf[0])
    if len(tasks):
        start_scene(name, tasks)
    else:
        action_set(name, 'stop')

def start_scene(name, tasks):
    stop_scene(name)
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
            action_set(line[-1], 'start')

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True #set flag
        print("Connected OK")
        client.subscribe(f"set/{topic}/actions", qos=0)
        client.subscribe("stat/#", qos=0)
        client.subscribe(f"cmnd/{topic}/#", qos=0)
        try:
            client.publish(f"tele/{topic}/LWT", "Online", retain=1)
        except:
            print("Cannot set topic 'tele/%r/LWT'" % topic)
    else:
        print("Bad connection, Returned code %r" % rc)

def on_message(client, userdata, message):
    if not message:
        return
#        perf[0] = time.perf_counter()
    if f"set/{topic}/actions" == message.topic:
        client.unsubscribe(f"set/{topic}/actions")
        actions.update(json.loads(str(message.payload.decode("utf-8"))))
        for name in actions.copy():
            if name not in then_dict:
                action_set(name, 'delete')
            elif actions[name] == 'run':
                action_set(name, 'start')
        for name in then_dict:
            if name not in actions:
                action_set(name, 'activate')
#        Thread(target=set_msg, args=(message,)).start()
    elif "stat/" in message.topic:
        Thread(target=stat_msg, args=(message,)).start()
    else:
        Thread(target=cmnd_msg, args=(message,)).start()

client.will_set(f"tele/{topic}/LWT", "Offline", 0, True)
client.connected_flag = False
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker)
client.loop_start()

while True:
    if pub_time and time.time() - pub_time > 0.2:
        client.publish(f"set/{topic}/actions", json.dumps(actions, separators=(',', ':'), ensure_ascii=False), retain=True)
        pub_time = 0
    time.sleep(0.1)

