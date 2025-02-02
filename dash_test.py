#! /usr/bin/python3

import json
import time
#from mqtt_send import send_msg, actions
from test_class import *

actions = {}
def send_msg(*args):
    if args[0] == 'save':
        actions[args[1][0]] = 'idle'
    elif args[0] == 'delete':
        del actions[args[1]]
    elif args[0] == 'start':
        actions[args[1]] = 'run'
    elif args[0] in ('stop', 'activate'):
        actions[args[1]] = 'idle'
    elif args[0] == 'deactivate':
        actions[args[1]] = 'deactivated'


saves_json = 'saves.json'
config_json = 'config.json'
menu = [
    {'label': 'сохранить', 'value': 'save'},
    {'label': 'удалить', 'value': 'delete'},
    {'label': 'включить', 'value': 'activate'},
    {'label': 'выключить', 'value': 'deactivate'},
    {'label': 'запустить', 'value': 'start'},
    {'label': 'прервать', 'value': 'stop'}
]

if_class = SceneIfClass()
then_class = SceneThenClass()

def dyn_layout():
    with open(config_json) as json_file:
        devices = json.load(json_file)
    if_class.setup(devices)
    then_class.setup(devices)
    then_class.scenes = sorted(actions.keys())
    return html.Div([
    dcc.Location(id='url', refresh=True),
    dbc.Row([
        html.Div(
            children=dcc.Dropdown(
                id='load-dropdown',
                options=then_class.scenes,
                placeholder='Загрузить',
                clearable=False,
                searchable=False,
                style={'width': '233px'}
            ),
            style={'width': '235px'}
        ),
        html.Div(
            children=dcc.Input(
                placeholder='Название сценария',
                id='scene-input',
                value='',
                debounce=True,
                style={'width': '214px', 'height': '35px'}
            ),
            style={'width': '215px'}
        ),
        html.Div(
            id ='save-delete-div',
            style={'width': '110px'},
        )],
        style={'width': '560px'}
    ),
    html.Div(
        id='stat-row-container-div',
        children=[if_class.create_row()],
        style={'width': '560px'}
    ),
    html.Div(
        id='cmnd-row-container-div',
        children=[then_class.create_row()],
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
    Output({'type': 'cmnd-scene-div', 'index': MATCH}, 'children'),
    Input({'type': 'cmnd-scene-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'cmnd-scene-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_cmnd_scene(value, id_):
    if value is None:
        return
    return dcc.Dropdown(
        id={
            'type': 'cmnd-value-input',
            'index': id_['index']
        },
        options=menu[2:],
        clearable=False,
        searchable=False,
        style={'width': '144px'}
    )

@callback(
    Output('save-delete-div', 'children'),
    [Input('scene-input', 'value'),
     Input({'type': 'stat-todo-dropdown', 'index': ALL}, 'value'),
     Input({'type': 'stat-value-input', 'index': ALL},'value'),
     Input({'type': 'cmnd-todo-dropdown', 'index': ALL},'options')],
    prevent_initial_call=True
)
def display_save_button(name, if_todos, if_values, then_todos):
    if not name or (len(if_values) and len(if_values) < len(if_todos)) or None in if_values or len(then_todos) == 1 or not then_todos[-1][0]:
        return
    return [dcc.Dropdown(
            id="save-delete-dropdown",
            options=[],
            placeholder='Сохранить',
            clearable=False,
            searchable=False,
            style={'width': '109px'}
#        ),
#        dcc.Interval(
#            id='interval-component',
#            interval=30*1000,
#            n_intervals=0
        )
    ]

@callback(
    Output('save-delete-dropdown', 'options'),
#    Input('interval-component', 'n_intervals'),
    Input('save-delete-div', 'n_clicks'),
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
     Output('stat-row-container-div', 'children', allow_duplicate=True),
     Output('cmnd-row-container-div', 'children', allow_duplicate=True),
     Output('load-dropdown', 'value')],
    Input('load-dropdown', 'value'),
    prevent_initial_call=True,
)
def press_load_dropdown(name):
    with open(saves_json) as json_file:
        save = json.load(json_file)[name]
    if_class.index = save['if_index']
    then_class.index = save['then_index']
    return name, save['if_rows'], save['then_rows'], None

@app.callback(
    Output("url", "href"),
    Output('save-delete-dropdown', 'value'),
    Input("save-delete-dropdown", "value"),
    [State('scene-input', 'value'),
     State('stat-row-container-div', 'children'),
     State('cmnd-row-container-div', 'children')],
    prevent_initial_call=True,
)
def save_delete_dropdown(value, name, if_rows, then_rows):
    if value is None:
        return no_update, None

    if value == 'save':
        send_list = []
        def row_to_send(rows):
            send = []
            delay = 0
            for row in rows:
                line = []
                for props in row['props'].get('children', []):
                    if children := props['props'].get('children'):
                        if children == 'сек.':
                            break
                        if isinstance(children, dict):
                            data = children['props'].get('value')
                            if data is not None:
                                line.append(data)
                qnt = len(line)
                if not qnt:
                    continue
                if qnt == 4:
                    send.append({'topic': line[0], 'feature': line[1], 'value': line[2]})
                    if line[3] == 1:
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
        send_list.append(row_to_send(then_rows))
        send_msg(value, send_list)
    else:
        send_msg(value, name)
        if value != 'delete':
            return no_update, None

#    with open(saves_json, 'r+') as json_file:
#        saves = json.load(json_file)
#        json_file.seek(0)
#        if value == 'save':
#            while name not in actions:
#                time.sleep(0.1)
#            saves[name] = {'if_rows': if_rows, 'then_rows': then_rows, 'if_index': if_class.index, 'then_index': then_class.index}
#        elif name in saves:
#            while name in actions:
#                time.sleep(0.1)
#            del saves[name]
#        json_file.truncate(0)
#        json.dump(saves, json_file, ensure_ascii=False, indent=4)
    return "/", None

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)

