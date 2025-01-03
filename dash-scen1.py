from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback
import dash_bootstrap_components as dbc
import json
import time

with open('config.json') as json_file:
    devices = json.load(json_file)

def if_row_create(count=[0]):
    n_row = count[0]
    count[0] += 1
    return dbc.Row([
        dcc.Dropdown(
            id={
                'type': 'if-device-dropdown',
                'index': n_row
            },
            options=[{'label': x['name'], 'value': devices.index(x)}
                     for x in devices if 'states' in x],
            clearable=False,
            style={'width': '180px'}
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
        dcc.Dropdown(
            id={
                'type': 'if-todo-dropdown',
                'index': n_row
            },
            options=['И', 'ИЛИ', 'ТОГДА', 'удалить'],
            value='ТОГДА',
            style={'width': '100px'},
            clearable=False,
            disabled=True
        )
    ])

def then_todo_create(count=[0]):
    n_row = count[0]
    count[0] += 1
    return html.Div(
        id={
            'type': 'then-todo-div',
            'index': n_row
        },
        children=[
            dcc.Dropdown(
                placeholder='Действие',
                id={
                    'type': 'then-todo-dropdown',
                    'index': n_row
                },
                options=['Устройство', 'Задержка', 'Сценарий'],
                value=None,
                clearable=False,
                style={'width': '150px'}
            )
        ]
    )


def then_row_create(n_row):
    return dbc.Row([
        html.Button('+',
            id={
                'type': 'then-button+',
                'index': n_row
            },
            style={'width': '50px'},
            n_clicks=0,
            disabled=True
        ),
        dcc.Dropdown(
            id={
                'type': 'then-device-dropdown',
                'index': n_row
            },
            options=[{'label': x['name'], 'value': devices.index(x)}
                     for x in devices if 'commands' in x],
#            value=2,
            clearable=False,
            style={'width': '180px'}
        ),
        html.Div(
            id={
                'type': 'then-feature-div',
                'index': n_row
            },
            children=[],
            style={'width': '180px'}
        ),
        html.Div(
            id={
                'type': 'then-value-div',
                'index': n_row
            },
            children=[],
            style={'width': '100px'}
        ),
        html.Button('-',
            id={
                'type': 'then-button-',
                'index': n_row
            },
            style={'width': '40px'}
#            disabled=True
        )
    ])

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = html.Div([
    dbc.Row([
        dcc.Input(
            placeholder='Название сценария',
            id='scene-input',
            debounce=True,
            value ='',
            style={'width': '250px'}
        ),
        html.Button("сохранить",
            id="save-btn",
            disabled=True,
            n_clicks=0,
            style={'width': '100px'}
        ),
        html.Button("загрузить",
            id="load-btn",
#            disabled=True,
            n_clicks=0,
            style={'width': '100px'}
        )
    ]),
    html.Div(
        id='if-row-container-div',
        children=[if_row_create()]
    ),
    html.Div(
        id='then-row-container-div',
        children=[then_todo_create()]
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
                style={'width': '80px'},
                clearable=False,
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '80px'},
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
    State('if-row-container-div', 'children'),
    prevent_initial_call=True
)
def display_if_container_div(values, children):
    if values[-1] != 'ТОГДА':
        children.append(if_row_create())
    for i, value in enumerate(values):
        if value == 'удалить':
           del children[i]
           break
        if value == 'ТОГДА':
           del children[i+1:]
           break
    return children

@callback(
    Output({'type': 'then-todo-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-todo-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'then-todo-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_then_container_div(value, id_):
    if value == 'Устройство':
        return then_row_create(id_['index'])

@callback(
    Output({'type': 'then-feature-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-device-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'then-device-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_then_feature(device, id_):
    options, disabled = [], True
    if device is not None:
        options, disabled = [{'label': devices[device]['features'][x]['name'], 'value': x}
             for x in devices[device]['commands']], False
    return [dcc.Dropdown(
        id={
            'type': 'then-feature-dropdown',
            'index': id_['index']
        },
        options=options,
        clearable=False,
        disabled=disabled
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
                style={'width': '80px'},
                clearable=False,
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '80px'},
#        placeholder='>1',
        value=None,
        disabled=disabled
    )]

@callback(
    Output('then-row-container-div', 'children'),
    [Input({'type': 'then-value-input', 'index': ALL}, 'value'),
     Input({'type': 'then-button-', 'index': ALL}, 'n_clicks'),
     Input({'type': 'then-button+', 'index': ALL}, 'n_clicks')],
    [State({'type': 'then-todo-dropdown', 'index': ALL}, 'id'),
     State({'type': 'then-button-', 'index': ALL}, 'id'),
     State('then-row-container-div', 'children')],
    prevent_initial_call=True
)
def display_then_container_div(values, del_clicks, add_clicks, ids, ids_row, children):

    def del_row(n_row):
        for row_ in children:
            if row_['props']['id']['index'] == n_row:
                children.remove(row_)
                break

    if 1 in add_clicks:
        if ids:
            del_row(ids[0]['index'])
        for i, row in enumerate(children):
            if row['props']['id']['index'] == ids_row[add_clicks.index(1)]['index']:
                children.insert(i, then_todo_create())
                break
        return children
    if 1 in del_clicks:
        del_row(ids_row[del_clicks.index(1)]['index'])
        if not ids:
            children.append(then_todo_create())
        return children
    if len(values) < len(ids_row):
        return children
    if None in values and ids:
        del_row(ids[0]['index'])
    elif None not in values and not ids:
        children.append(then_todo_create())
    return children

@callback(
    [Output({'type': 'then-button+', 'index': ALL}, 'disabled'),
     Output({'type': 'then-button+', 'index': ALL}, 'n_clicks'),
     Output('save-btn', 'disabled')],
    [Input({'type': 'then-value-input', 'index': ALL}, 'value'),
     Input('scene-input', 'value'),
     Input({'type': 'if-value-input', 'index': ALL}, 'value')],
    [State({'type': 'then-button+', 'index': ALL}, 'id'),
     State({'type': 'if-device-dropdown', 'index': ALL}, 'id')],
#    prevent_initial_call=True
)
def display_then_button(values, name, if_values, ids, if_ids):
    ret = len(if_values) and len(if_values) < len(if_ids) or None in if_values
    ret = not ids or len(values) < len(ids) or None in values or ret
    return [ret for i in ids], [0 for i in ids], ret or not name

def scene_to_list(scene, rows, then):
    for row in rows:
        if then:
            row = row['props']['children']
            if type(row) is list:
                continue
        for props in row['props']['children']:
            value = props['props'].get('value', props['props'].get('children'))
            if value and type(value) is list:
                value = value[0]['props']['value']
            scene.append(value)

if_rows_save = []
then_rows_save = []

@callback(
#    Output({'type': 'then-button+', 'index': MATCH}, 'n_clicks'),
    Input('save-btn', 'n_clicks'),
    [State('scene-input', 'value'),
     State('if-row-container-div', 'children'),
     State('then-row-container-div', 'children')]
#    prevent_initial_call=True
)
def press_save_button(n_clicks, name, if_rows, then_rows):
    global if_rows_save, then_rows_save
    if_rows_save = if_rows
    then_rows_save = then_rows
    scene = [name]
    scene_to_list(scene, if_rows, False)
    scene_to_list(scene, then_rows, True)
#    print(scene)
#    return 0

@callback(
    [Output('if-row-container-div', 'children', allow_duplicate=True),
     Output('then-row-container-div', 'children', allow_duplicate=True)],
    Input('load-btn', 'n_clicks'),
    prevent_initial_call=True,
)

def press_load_button(n_clicks):
    print(if_rows_save, then_rows_save)
    return if_rows_save, then_rows_save

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
