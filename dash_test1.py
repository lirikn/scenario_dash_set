from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback, no_update
import dash_bootstrap_components as dbc
import json
#from mqtt_send import send_msg
from scene_test import send_msg

with open('config.json') as json_file:
    devices = json.load(json_file)

try:
    with open('save.json') as json_file:
        saves = json.load(json_file)
except:
    saves = []

def list_sort(elem):
    return elem['label']

def list_devices(prop):
    ret = [{'label': x['name'] + ' ' + x.get('room', ''), 'value': i}
                     for i, x in enumerate(devices) if prop in x]
    ret.sort(key=list_sort)
    return ret

devices_states = list_devices('states')
devices_commands = list_devices('commands')
todos = ['Устройство', 'Задержка', 'Сценарий', 'удалить']
count = [0, 1]
#scenarios = []
#scenes = {}

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
                options=devices_states,
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
                    options=devices_commands,
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
                    value='0',
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
                    options=[x['name'] for x in saves],
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


app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, maximum-scale=1"
    }]
)
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    dbc.Row([
        html.Div(
            id='load-div',
            children=[dcc.Dropdown(
                id='load-dropdown',
                options=[],
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
            style={'width': '110px'}
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

@callback(
    Output({'type': 'if-feature-div', 'index': MATCH}, 'children'),
    Input({'type': 'if-device-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'if-device-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_if_feature(device, id_):
    options, disabled = [], True
    if device is not None:
        options, disabled = [{'label': devices[device]['features'][x]['name'], 'value': x}
             for x in devices[device]['states']], False
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
def display_if_value(feature, device, id_):
    disabled = True
    id = {
        'type': 'if-value-input',
        'index': id_['index']
    }
    if feature is not None:
        if devices[device]['features'][feature]['type'] in ('bool', 'enum'):
            return [dcc.Dropdown(
                id=id,
                style={'width': '79px'},
                clearable=False,
                searchable=False,
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
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
def display_then_feature(device, id_):
    if device is None:
        return
    return [dcc.Dropdown(
        id={
            'type': 'then-feature-dropdown',
            'index': id_['index']
        },
        options=[{'label': devices[device]['features'][x]['name'], 'value': x}
             for x in devices[device]['commands']],
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
def display_then_value(feature, device, id_):
    disabled = True
    id = {
        'type': 'then-value-input',
        'index': id_['index']
    }
    if feature is not None:
        if devices[device]['features'][feature]['type'] in ('bool', 'enum'):
            return [dcc.Dropdown(
                id=id,
                style={'width': '79px'},
                clearable=False,
                searchable=False,
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
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
    if None in (second, minute, hour, day) or not day.isdigit() :
        return no_update
    return str(int(day) * 86400 + hour * 3600 + minute * 60 + second)

@callback(
    [Output({'type': 'then-wait-second', 'index': MATCH}, 'value'),
     Output({'type': 'then-wait-minute', 'index': MATCH}, 'value'),
     Output({'type': 'then-wait-hour', 'index': MATCH}, 'value'),
     Output({'type': 'then-wait-day', 'index': MATCH}, 'value')],
    Input({'type': 'then-wait-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'then-value-input', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def display_then_wait_(n_clicks, value):
    if value is None or not value.isdigit():
        return no_update
    s = int(value)
    h = s % 86400
    m = h % 3600
    return m % 60, m // 60, h // 3600, str(s // 86400)

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
        options=['включить', 'выключить', 'запустить', 'прервать'],
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
        options, placeholder = ['удалить'], 'Удалить'
    else:
        options, placeholder = ['сохранить', 'удалить'], 'Сохранить'
    return dcc.Dropdown(
                id="save-delete-dropdown",
                options=options,
                placeholder=placeholder,
                clearable=False,
                searchable=False,
                style={'width': '109px'})

@callback(
    Output('load-dropdown', 'options'),
    Input('url', 'id'),
#    prevent_initial_call=True
)
def press_load_dropdown(_):
    count[0], count[1] = 1, 1
    return [{'label': x['name'], 'value': i} for i, x in enumerate(saves)]

@callback(
    [Output('scene-input', 'value'),
     Output('if-row-container-div', 'children', allow_duplicate=True),
     Output('then-row-container-div', 'children', allow_duplicate=True),
     Output('load-dropdown', 'value')],
    Input('load-dropdown', 'value'),
    prevent_initial_call=True,
)
def press_load_dropdown(value):
    count[0] = saves[value]['count'][0]
    count[1] = saves[value]['count'][1]
    return saves[value]['name'], saves[value]['if_rows'], saves[value]['then_rows'], None

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

    def row_to_send(rows):
        send = []
        delay = 0
        for row in rows:
            line = []
            for props in row['props'].get('children', []):
                if children := props['props'].get('children'):
                    if children == 'сек.':
                        break
                    if isinstance(children, list):
                        data = children[0]['props'].get('value')
                        if data is not None:
                            if isinstance(data, int):
                                line.append(devices[data]['topic'])
                            else:
                                line.append(data)
            if not (qnt := len(line)):
                continue
            if qnt == 4:
                send.append({'topic': line[0], 'feature': line[1], 'value': line[2]})
                if line[3] == 'И':
                    continue
                send.append(name)
                send_msg('if', send)
                send = []
            elif qnt == 3:
                send.append({'delay': delay, 'topic': line[0], 'feature': line[1], 'value': line[2]})
                delay = 0
            elif qnt == 2:
                send.append({'delay': delay, 'scene': line[0], 'action': line[1]})
                delay = 0
            elif line[0].isdigit():
                delay += int(line[0])
        return send

    save = False
    for scene in saves:
        if scene['name'] == name:
            saves.remove(scene)
            save = True
            send_msg('del', name)
            break
    if value == 'сохранить':
        saves.append({'name': name, 'if_rows': if_rows.copy(), 'then_rows': then_rows.copy(), 'count': count.copy()})
        save = True

        row_to_send(if_rows)
        send_msg('then', {name: row_to_send(then_rows)})

    if save:
        with open('save.json', 'w') as json_file:
            json.dump(saves, json_file, ensure_ascii=False, indent=4)
    return "/"

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
