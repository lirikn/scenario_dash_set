from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback
import dash_bootstrap_components as dbc
import json

with open('config.json') as json_file:
    devices = json.load(json_file)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = html.Div([
    html.Button("Add row", id="dynamic-add-btn", n_clicks=0),
    html.Div(id='dynamic-row-container-div', children=[]),
])

@callback(
    Output('dynamic-row-container-div', 'children'),
#    [Input('dynamic-add-btn', 'n_clicks'),
    Input({'type': 'todo-dynamic-dropdown', 'index': ALL}, 'value'),
    State({'type': 'todo-dynamic-dropdown', 'index': ALL}, 'id')
)
def display_row(todos, ids):
    patched_children = Patch()
    print(todos, ids)
    n_row = len(ids)
    for (i, todo) in enumerate(todos):
        id_ = ids[i]['index'] + 1
        if todo is None:
            del patched_children[id_]
            return patched_children
        else:
            n_row = id_
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

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
