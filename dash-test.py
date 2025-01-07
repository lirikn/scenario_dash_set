from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback, no_update
import dash_bootstrap_components as dbc
import json


with open('config.json') as json_file:
    devices = json.load(json_file)

def list_sort(elem):
    return elem['label']

def list_devices(prop):
    ret = [{'label': x['name'] + ' ' + x.get('room', ''), 'value': devices.index(x)}
                     for x in devices if prop in x]
    ret.sort(key=list_sort)
    return ret

devices_states = list_devices('states')
devices_commands = list_devices('commands')
todos = ['Устройство', 'Задержка', 'Сценарий', 'удалить']
count = [0, 1]
save = []

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
#                [{'label': x['name'], 'value': devices.index(x)}
#                     for x in devices if 'states' in x],
                optionHeight=50,
                clearable=False,
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
        dcc.Store(
            id={
                'type': 'if-store',
                'index': n_row
            },
            data=False
        ),
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'if-todo-dropdown',
                    'index': n_row
                },
                options=['И', 'ИЛИ', 'ТОГДА', 'удалить'],
                value='ТОГДА',
                style={'width': '100px'},
                clearable=False,
                searchable=False,
                disabled=True
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
#                    [{'label': x['name'], 'value': devices.index(x)}
#                         for x in devices if 'commands' in x],
                    clearable=False,
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
        align='center'
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
    dbc.Row([
        dcc.Input(
            placeholder='Название сценария',
            id='scene-input',
            value='',
            debounce=True,
            style={'width': '199px'}
        ),
        html.Button("сохранить",
            id="save-button",
            disabled=True,
            n_clicks=0,
            style={'width': '99px'}
        ),
        html.Button("загрузить",
            id="load-button",
#            disabled=True,
            n_clicks=0,
            style={'width': '99px'}
        )
    ], style={'width': '400px'}),
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
                options=['Устройство', 'Задержка', 'Сценарий'],
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
    Output({'type': 'if-todo-dropdown', 'index': MATCH}, 'disabled'),
    Input({'type': 'if-value-input', 'index': MATCH}, 'value'),
#    State({'type': 'if-value-input', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_if_todo(value):
    return value is None or value == ''

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
    [Output({'type': 'then-todo-dropdown', 'index': ALL}, 'disabled'),
     Output({'type': 'then-todo-dropdown', 'index': ALL}, 'value')],
    Input({'type': 'then-store', 'index': ALL}, 'data'),
#    prevent_initial_call=True
)
def display_then_button(datas):
    lines = len(datas) + 1
    return [False in datas] * lines, [None] * lines

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
    Output('save-button', 'disabled'),
    [Input('scene-input', 'value'),
     Input({'type': 'if-todo-dropdown', 'index': ALL}, 'value'),
     Input({'type': 'if-value-input', 'index': ALL},'value'),
     Input({'type': 'then-store', 'index': ALL}, 'data')],
    prevent_initial_call=True
)
def display_save_button(name, if_todos, if_values, then_store):
    return len(if_values) and len(if_values) < len(if_todos) or None in if_values or False in then_store or not name

@callback(
#    Output({'type': 'then-button+', 'index': MATCH}, 'n_clicks'),
    Input('save-button', 'n_clicks'),
    [State('scene-input', 'value'),
     State('if-row-container-div', 'children'),
     State('then-row-container-div', 'children')],
    prevent_initial_call=True
)
def press_save_button(n_clicks, name, if_rows, then_rows):
    for scene in save:
        if scene['name'] == name:
            del scene
    save.append({'name': name, 'if_rows': if_rows, 'then_rows': then_rows, 'count': count})
    print(len(save))

@callback(
    [Output('if-row-container-div', 'children', allow_duplicate=True),
     Output('then-row-container-div', 'children', allow_duplicate=True)],
    Input('load-button', 'n_clicks'),
    State('scene-input', 'value'),
    prevent_initial_call=True,
)
def press_load_button(n_clicks, name):
    for scene in save:
        if scene['name'] == name:
            return scene['if_rows'], scene['then_rows']
    return no_update, no_update

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
