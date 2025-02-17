#! /usr/bin/python3

from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback, no_update
import dash_bootstrap_components as dbc
import json
import time
from mqtt_send import send_msg, actions

saves_json = 'saves.json'
config_json = 'config.json'
devices_menu = {'states': [], 'commands': []}
todos = ['Устройство', 'Задержка', 'Сценарий', 'удалить']
menu = [
    {'label': 'сохранить', 'value': 'save'},
    {'label': 'удалить', 'value': 'delete'},
    {'label': 'включить', 'value': 'activate'},
    {'label': 'выключить', 'value': 'diactivate'},
    {'label': 'запустить', 'value': 'start'},
    {'label': 'прервать', 'value': 'stop'}
]
count = [0, 1]
scene_names = set()
devices = {}

def if_row_create():
    n_row = count[0]
    count[0] += 1
    return dbc.Row([
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'if-device-dropdown',
                    'index': n_row
                },
                options=devices_menu['states'],
                optionHeight=50,
                clearable=False,
                value=None,
                searchable=False,
                style={'width': '199px'}
            )],
            style={'width': '200px'}
        ),
        html.Div(
            id={
                'type': 'if-feature-div',
                'index': n_row
            },
            children=[],
            style={'width': '180px'}
        ),
        html.Div(
            id={
                'type': 'if-value-div',
                'index': n_row
            },
            children=[],
            style={'width': '80px'}
        ),
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'if-todo-dropdown',
                    'index': n_row
                },
                options=['ТОГДА'],
                value='ТОГДА',
                style={'width': '100px'},
                clearable=False,
                searchable=False,
#                disabled=True
            )],
            style={'width': '100px'}
        )
    ])

def then_row_create(todo):
    n_row = count[1]
    count[1] += 1
    rows = {
        'Устройство': [
            html.Div([
                dcc.Dropdown(
                    id={
                        'type': 'then-device-dropdown',
                        'index': n_row
                    },
                    options=devices_menu['commands'],
                    clearable=False,
                    value=None,
                    searchable=False,
                    style={'width': '199px'}
                )],
                style={'width': '200px'}
            ),
            html.Div(
                id={
                    'type': 'then-feature-div',
                    'index': n_row
                },
                style={'width': '180px'}
            ),
            html.Div(
                id={
                    'type': 'then-value-div',
                    'index': n_row
                },
                style={'width': '80px'}
            )
        ],
        'Задержка': [
            html.P("Задержка:",
                style={'width': '80px', 'height': '10px'}
            ),
            html.Div([
                dcc.Input(
                    id={
                        'type': 'then-value-input',
                        'index': n_row
                    },
                    type='number',
                    min=0,
                    max=86399999,
                    step=1,
                    style={'width': '79px', 'height': '35px'}
                )],
                style={'width': '80px'}
            ),
            html.P("сек.",
                style={'width': '50px', 'height': '10px'}
            ),
            html.Button("-->",
                id={
                    'type': 'then-wait-button',
                    'index': n_row
                },
                style={'width': '55px', 'height': '35px'}
            ),
            html.Div([
                dcc.Input(
                    id={
                        'type': 'then-wait-day',
                        'index': n_row
                    },
                    value=0,
                    type='number',
                    min=0,
                    max=999,
                    step=1,
                    style={'width': '34px', 'height': '35px'}
                )],
                style={'width': '35px'}
            ),
            html.Div([
                dcc.Dropdown(
                    id={
                        'type': 'then-wait-hour',
                        'index': n_row
                    },
                    options=list(range(0, 24)),
                    value=0,
                    clearable=False,
                    searchable=False,
                    style={'width': '49px'}
                )],
                style={'width': '50px'}
            ),
            html.Div([
                dcc.Dropdown(
                    id={
                        'type': 'then-wait-minute',
                        'index': n_row
                    },
                    options=list(range(0, 60)),
                    value=0,
                    clearable=False,
                    searchable=False,
                    style={'width': '49px'}
                )],
                style={'width': '50px'}
            ),
            html.Div([
                dcc.Dropdown(
                    id={
                        'type': 'then-wait-second',
                        'index': n_row
                    },
                    options=list(range(0, 60)),
                    clearable=False,
                    searchable=False,
                    style={'width': '49px'}
                )],
                style={'width': '60px'}
            )
        ],
        'Сценарий': [
            html.P("Сценарий:",
                style={'width': '80px', 'height': '10px'}
            ),
            html.Div([
                dcc.Dropdown(
                    id={
                        'type': 'then-scene-dropdown',
                        'index': n_row
                    },
                    options=sorted(scene_names),
                    clearable=False,
                    searchable=False,
                    style={'width': '233px'}
                )],
                style={'width': '235px'}
            ),
            html.Div(
                id={
                    'type': 'then-scene-div',
                    'index': n_row
                },
                style={'width': '145px'}
            )
        ]
    }
    return dbc.Row(rows[todo] + [
        html.Div([
            dcc.Store(
                id={
                    'type': 'then-store',
                    'index': n_row
                },
                data = False
            ),
            dcc.Dropdown(
                id={
                    'type': 'then-todo-dropdown',
                    'index': n_row
                },
                options=todos,
                value=None,
                placeholder='Вставить',
                clearable=False,
                disabled=False,
                searchable=False,
                style={'width': '100px'}
            )],
            style={'width': '100px'}
        )],
        align='center',
#        justify='around'
    )

def dyn_layout():
    def list_sort(elem):
        return elem['label']
    with open(config_json) as json_file:
        for device in json.load(json_file):
            devices[device['uuid']] = device
    for prop in devices_menu:
        devices_menu[prop] = [{'label': device['name'] + ' ' + device.get('room', ''), 'value': uuid}
             for uuid, device in devices.items() if prop in device]
        devices_menu[prop].sort(key=list_sort)
    scene_names.clear()
    scene_names.update(set(actions.keys()))
    count[0], count[1] = 0, 1
    return html.Div([
    dcc.Location(id='url', refresh=True),
    dbc.Row([
        html.Div([
            dcc.Dropdown(
                id='load-dropdown',
                options=sorted(scene_names),
                placeholder='Загрузить',
                clearable=False,
                searchable=False,
                style={'width': '233px'}
            )],
            style={'width': '235px'}
        ),
        html.Div([
            dcc.Input(
                placeholder='Название сценария',
                id='scene-input',
                value='',
                debounce=True,
                style={'width': '214px', 'height': '35px'}
            )],
            style={'width': '215px'}
        ),
        html.Div(
            id ='save-delete-div',
            style={'width': '110px'},
#            n_clicks=0
        )],
        style={'width': '560px'}
    ),
    html.Div(
        id='if-row-container-div',
        children=[if_row_create()],
        style={'width': '560px'}
    ),
    html.Div(
        id='then-row-container-div',
        children=[
            dcc.Dropdown(
                id={
                    'type': 'then-todo-dropdown',
                    'index': 0
                },
                options=todos[0:-1],
                value=None,
                placeholder='Добавить',
                clearable=False,
                searchable=False,
                disabled=False,
                style={'width': '110px'}
            )
        ],
        style={'width': '560px'}
    )
])


app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, maximum-scale=1"
    }]
)
app.layout = dyn_layout

@callback(
    Output({'type': 'if-feature-div', 'index': MATCH}, 'children'),
    Input({'type': 'if-device-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'if-device-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_if_feature(uuid, id_):
    options, disabled = [], True
    if uuid is not None:
        options, disabled = [{'label': devices[uuid]['features'][x]['name'], 'value': x}
             for x in devices[uuid]['states']], False
    return [dcc.Dropdown(
        id={
            'type': 'if-feature-dropdown',
            'index': id_['index']
        },
        options=options,
        disabled=disabled,
        searchable=False,
        style={'width': '179px'},
        clearable=False
    )]

@callback(
    Output({'type': 'if-value-div', 'index': MATCH}, 'children'),
    Input({'type': 'if-feature-dropdown', 'index': MATCH}, 'value'),
    [State({'type': 'if-device-dropdown', 'index': MATCH}, 'value'),
     State({'type': 'if-feature-dropdown', 'index': MATCH}, 'id')],
    prevent_initial_call=True
)
def display_if_value(feature, uuid, id_):
    disabled = True
    id = {
        'type': 'if-value-input',
        'index': id_['index']
    }
    if feature is not None:
        if devices[uuid]['features'][feature]['type'] in ('bool', 'enum'):
            return [dcc.Dropdown(
                id=id,
                style={'width': '79px'},
                clearable=False,
                searchable=False,
                options=devices[uuid]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '79px', 'height': '35px'},
#        placeholder='>1',
        value=None,
        disabled=disabled
    )]

@callback(
    Output({'type': 'if-todo-dropdown', 'index': MATCH}, 'options'),
    Input({'type': 'if-value-input', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def display_if_todo_options(value):
    options = ['ТОГДА', 'удалить']
    if value:
        options = ['И', 'ИЛИ'] + options
    return options

@callback(
    Output('if-row-container-div', 'children'),
    Input({'type': 'if-todo-dropdown', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def display_if_container_div(values):
    children = Patch()
    if 'удалить' in values:
        del children[values.index('удалить')]
    if values[-1] != 'ТОГДА':
        children.append(if_row_create())
    else:
        n = values.index('ТОГДА') + 1
        for i in range(n, len(values)):
            del children[n]
    return children

@callback(
    Output({'type': 'then-feature-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-device-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'then-device-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_then_feature(uuid, id_):
    if uuid is None:
        return
    return [dcc.Dropdown(
        id={
            'type': 'then-feature-dropdown',
            'index': id_['index']
        },
        options=[{'label': devices[uuid]['features'][x]['name'], 'value': x}
             for x in devices[uuid]['commands']],
        clearable=False,
        searchable=False,
        style={'width': '179px'}
    )]

@callback(
    Output({'type': 'then-value-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-feature-dropdown', 'index': MATCH}, 'value'),
    [State({'type': 'then-device-dropdown', 'index': MATCH}, 'value'),
     State({'type': 'then-feature-dropdown', 'index': MATCH}, 'id')],
    prevent_initial_call=True
)
def display_then_value(feature, uuid, id_):
    disabled = True
    id = {
        'type': 'then-value-input',
        'index': id_['index']
    }
    if feature is not None:
        if devices[uuid]['features'][feature]['type'] in ('bool', 'enum'):
            return [dcc.Dropdown(
                id=id,
                style={'width': '79px'},
                clearable=False,
                searchable=False,
                options=devices[uuid]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '79px', 'height': '35px'},
#        placeholder='>1',
        value=None,
        disabled=disabled
    )]

@callback(
    Output({'type': 'then-store', 'index': MATCH}, 'data'),
    Input({'type': 'then-value-input', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def display_then_value(value):
    return value != '' and value is not None


@callback(
    Output('then-row-container-div', 'children'),
    Input({'type': 'then-todo-dropdown', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def display_then_container_div(values):
    children = Patch()
    for todo in todos:
        if todo in values:
            inx = values.index(todo)
            if todo == 'удалить':
                del children[inx]
                break
            children.insert(inx, then_row_create(todo))
            break
    return children

@callback(
    [Output({'type': 'then-todo-dropdown', 'index': ALL}, 'options'),
     Output({'type': 'then-todo-dropdown', 'index': ALL}, 'value')],
    Input({'type': 'then-store', 'index': ALL}, 'data'),
    #    prevent_initial_call=True
)
def display_then_button(then_store):
    lines = len(then_store)
    if all(then_store):
        options = [todos] * lines
        options.append(todos[0:-1])
    else:
        options = [['']] * (lines + 1)
        options[then_store.index(False)] = ['удалить']
    return options, [None] * (lines + 1)

@callback(
    Output({'type': 'then-value-input', 'index': MATCH}, 'value'),
    [Input({'type': 'then-wait-second', 'index': MATCH}, 'value'),
     Input({'type': 'then-wait-minute', 'index': MATCH}, 'value'),
     Input({'type': 'then-wait-hour', 'index': MATCH}, 'value'),
     Input({'type': 'then-wait-day', 'index': MATCH}, 'value')],
    prevent_initial_call=True
)
def display_then_wait(second, minute, hour, day):
    if None in (second, minute, hour, day):
        return no_update
    return day * 86400 + hour * 3600 + minute * 60 + second

@callback(
    [Output({'type': 'then-wait-second', 'index': MATCH}, 'value'),
     Output({'type': 'then-wait-minute', 'index': MATCH}, 'value'),
     Output({'type': 'then-wait-hour', 'index': MATCH}, 'value'),
     Output({'type': 'then-wait-day', 'index': MATCH}, 'value')],
    Input({'type': 'then-wait-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'then-value-input', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def display_then_wait_(_, s):
    if s is None:
        return no_update
    h = s % 86400
    m = h % 3600
    return m % 60, m // 60, h // 3600, s // 86400

@callback(
    Output({'type': 'then-scene-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-scene-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'then-scene-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_then_feature(value, id_):
    if value is None:
        return
    return [dcc.Dropdown(
        id={
            'type': 'then-value-input',
            'index': id_['index']
        },
        options=menu[2:],
        clearable=False,
        searchable=False,
        style={'width': '144px'}
    )]

@callback(
    Output('save-delete-div', 'children'),
    [Input('scene-input', 'value'),
     Input({'type': 'if-todo-dropdown', 'index': ALL}, 'value'),
     Input({'type': 'if-value-input', 'index': ALL},'value'),
     Input({'type': 'then-store', 'index': ALL}, 'data')],
    prevent_initial_call=True
)
def display_save_button(name, if_todos, if_values, then_store):
    if not name or (len(if_values) and len(if_values) < len(if_todos)) or None in if_values or not then_store or False in then_store:
        return
    return [dcc.Dropdown(
                id="save-delete-dropdown",
                options=[],
                placeholder='Сохранить',
                clearable=False,
                searchable=False,
                style={'width': '109px'}),
            dcc.Interval(
                id='interval-component',
                interval=1*1000,
                n_intervals=0
        )]

@callback(
    Output('save-delete-dropdown', 'options'),
    Input('interval-component', 'n_intervals'),
    State('scene-input', 'value'),
    prevent_initial_call=True
)
def save_delete_menu(_, name):
    options = [menu[0]]
    if name in actions:
        options.append(menu[1])
        if actions[name] == 'idle':
            options.extend(menu[3:5])
        elif actions[name] == 'deactivated':
            options.append(menu[2])
        elif actions[name] == 'run':
            options.extend(menu[3::2])
    return options


@callback(
    [Output('scene-input', 'value'),
     Output('if-row-container-div', 'children', allow_duplicate=True),
     Output('then-row-container-div', 'children', allow_duplicate=True),
     Output('load-dropdown', 'value')],
    Input('load-dropdown', 'value'),
    prevent_initial_call=True,
)
def press_load_dropdown(name):
    with open(saves_json) as json_file:
        save = json.load(json_file)[name]
    count[0] = save['count'][0]
    count[1] = save['count'][1]
    return name, save['if_rows'], save['then_rows'], None

@app.callback(
    Output("url", "href"),
    Input("save-delete-dropdown", "value"),
    [State('scene-input', 'value'),
     State('if-row-container-div', 'children'),
     State('then-row-container-div', 'children')],
    prevent_initial_call=True,
)
def save_delete_dropdown(value, name, if_rows, then_rows):
    if value is None:
        return no_update

    if value == 'save':
        send_list = []
        def row_to_send(rows):
            send = []
            delay = 0
            for row in rows:
                line = []
                for props in row['props'].get('children', []):
                    children = props['props'].get('children')
                    if children:
                        if children == 'сек.':
                            break
                        if isinstance(children, list):
                            data = children[0]['props'].get('value')
                            if data is not None:
                                if data in devices:
                                    data = devices[data]['topic']
                                line.append(data)
                qnt = len(line)
                if not qnt:
                    continue
                if qnt == 4:
                    send.append({'topic': line[0], 'feature': line[1], 'value': line[2]})
                    if line[3] == 'И':
                        continue
                    send.append(name)
                    send_list.append(send)
                    send = []
                elif qnt == 3:
                    send.append({'delay': delay, 'topic': line[0], 'feature': line[1], 'value': line[2]})
                    delay = 0
                elif qnt == 2:
                    send.append({'delay': delay, 'scene': line[0], 'action': line[1]})
                    delay = 0
                elif isinstance(line[0], int):
                    delay += line[0]
            return send
        send_list.append(name)
        row_to_send(if_rows)
        send_list.append({name: row_to_send(then_rows)})
        send_msg(value, send_list)
    else:
        send_msg(value, name)
        if value != 'delete':
            return no_update

    with open(saves_json, 'r+') as json_file:
        saves = json.load(json_file)
        json_file.seek(0)
        if value == 'save':
            while name not in actions:
                time.sleep(0.1)
            saves[name] = {'if_rows': if_rows, 'then_rows': then_rows, 'count': count}
        elif name in saves:
            while name in actions:
                time.sleep(0.1)
            del saves[name]
        json_file.truncate(0)
        json.dump(saves, json_file, ensure_ascii=False, indent=4)
    return "/"

if __name__ == '__main__':
    app.run_server('192.168.3.2', debug=True, use_reloader=False)
