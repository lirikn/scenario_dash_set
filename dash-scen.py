from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback
import dash_bootstrap_components as dbc
import json

with open('config.json') as json_file:
    devices = json.load(json_file)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = html.Div([
    dbc.Row([
        dcc.Input(
            placeholder='Название сценария',
            id='scene-input',
            debounce=True,
            value=None,
            style={'width': '300px'}
        ),
        html.Button("сохранить",
            id="save-btn",
            disabled=True,
            n_clicks=0,
            style={'width': '100px'}
        )
    ]),
    html.Div(id='dynamic-row-container-div', children=[]),
    html.Div(id='dynamic-then-container-div', children=[])
])

@callback(
    Output('dynamic-row-container-div', 'children'),
    [Input('scene-input', 'value'),
     Input({'type': 'todo-dynamic-dropdown', 'index': ALL}, 'value')],
    State({'type': 'todo-dynamic-dropdown', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def display_row(value, todos, ids):
    if value == '':
        return []
    patched_children = Patch()
    n_row = 0
    then = 0
    for (i, todo) in enumerate(todos):
        if then > 0:
            del patched_children[then]
            if todo == 'ТОГДА':
                return patched_children
            continue
        if todo is None:
            del patched_children[i]
            return patched_children
        n_row = ids[i]['index'] + 1
        if todo == 'ТОГДА':
            then = i + 1
    del patched_children[len(ids)]
    new_element = dbc.Row([
        dcc.Dropdown(
            id={
                'type': 'device-dynamic-dropdown',
                'index': n_row
            },
            options=[{'label': x['name'], 'value': devices.index(x)}
                     for x in devices if 'states' in x],
            value=None,
            style={'width': '250px'}
        ),
        dcc.Dropdown(
            id={
                'type': 'feature-dynamic-dropdown',
                'index': n_row
            },
            options=[],
            value=None,
            disabled=True,
            style={'width': '300px'}
        ),
        html.Div(
            id={
                'type': 'value-dynamic-div',
                 'index': n_row
            },
            style={'width': '100px'}
        ),
        dcc.Dropdown(
            id={
                'type': 'todo-dynamic-dropdown',
                'index': n_row
            },
            options=['И', 'ИЛИ', 'ТОГДА'],
            value=None,
            disabled=True,
            style={'width': '100px'}
        )
    ])
    if then > 0:
        new_element = html.Div([
           dcc.Dropdown(
                id='then-dropdown',
                options=['Устройство', 'Сценарий', 'Задержка'],
                style={'width': '250px'}
           )
        ])
    patched_children.append(new_element)
    return patched_children

@callback(
    [Output({'type': 'feature-dynamic-dropdown', 'index': MATCH}, 'options'),
     Output({'type': 'feature-dynamic-dropdown', 'index': MATCH}, 'disabled')],
    Input({'type': 'device-dynamic-dropdown', 'index': MATCH}, 'value'),
#    State({'type': 'device-dynamic-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_feature(value):
    if value is None:
        return [], True
    return [{'label': devices[value]['features'][x]['name'], 'value': x}
                 for x in devices[value]['states']], False

@callback(
    Output({'type': 'value-dynamic-div', 'index': MATCH}, 'children'),
    Input({'type': 'feature-dynamic-dropdown', 'index': MATCH}, 'value'),
    [State({'type': 'device-dynamic-dropdown', 'index': MATCH}, 'value'),
     State({'type': 'feature-dynamic-dropdown', 'index': MATCH}, 'id')],
    prevent_initial_call=True
)
def display_value(feature, device, id_):
    if feature is None:
        return []
    if devices[device]['features'][feature]['type'] in ('bool', 'enum'):
        children = [dcc.Dropdown(
            id={
                'type': 'value-dynamic-input',
                'index': id_['index']
            },
            options=devices[device]['features'][feature].get('values', ['True', 'False']),
            style={'width': '80px'}
        )]
    else:
        children = [dcc.Input(
            id={
                'type': 'value-dynamic-input',
                'index': id_['index']
            },
            placeholder='>1',
#            debounce=True,
            value=None,
            style={'width': '80px'}
        )]
    return children

@callback(
    Output({'type': 'todo-dynamic-dropdown', 'index': MATCH}, 'disabled'),
    Input({'type': 'value-dynamic-input', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def display_todo(input_):
     return input_ is None

@callback(
    Output('dynamic-then-container-div', 'children'),
    Input('then-dropdown', 'value'),
    prevent_initial_call=True
)
def display_then(value):
    if value is None:
        return
    patched_children = Patch()
    n_row = 0
    new_element = dbc.Row([
        dcc.Dropdown(
            id={
                'type': 'device-commands-dropdown',
                'index': n_row
            },
            options=[{'label': x['name'], 'value': devices.index(x)}
                     for x in devices if 'commands' in x],
            value=None,
            style={'width': '250px'}
        )
    ])
    patched_children.append(new_element)
    return patched_children


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
