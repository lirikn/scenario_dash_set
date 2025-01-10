

if_list, then_list = [], []

def send_msg(t, msg):
    if t == 'if':
        if_list.append(msg)
    elif t == 'then':
        then_list.append(msg)
    else:
        for line in if_list:
            if line[-1] == msg[0]:
                if_list.remove(line)
        for line in then_list:
            if line[0] == msg[0]:
                then_list.remove(line)
    print(if_list, then_list)

def stat_msg(topic, value):
    pass