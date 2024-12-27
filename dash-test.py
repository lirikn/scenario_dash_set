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
#            value='Тест',
            style={'width': '250px'}
        ),
        html.Button("сохранить",
            id="save-btn",
            disabled=True,
            n_clicks=0,
            style={'width': '100px'}
        )
    ]),
    html.Div(id='main-div', children=[])
])

def if_row_create(n_row):
    return dbc.Row([
        dcc.Dropdown(
            id={
                'type': 'if-device-dropdown',
                'index': n_row
            },
            options=[{'label': x['name'], 'value': devices.index(x)}
                     for x in devices if 'states' in x],
#            value=2,
            style={'width': '200px'}
        ),
        html.Div(
            id={
                'type': 'if-feature-div',
                'index': n_row
            },
            children=[],
            style={'width': '200px'}
        ),
        html.Div(
            id={
                'type': 'if-value-div',
                'index': n_row
            },
            children=[],
            style={'width': '100px'}
        ),
        dcc.Dropdown(
            id={
                'type': 'if-todo-dropdown',
                'index': n_row
            },
            options=['И', 'ИЛИ', 'ТОГДА'],
            style={'width': '100px'},
            disabled=True
        )
    ])

@callback(
    Output('main-div', 'children'),
    Input('scene-input', 'value')
#    prevent_initial_call=True
)
def display_main(value):
    if value is None or value == '':
        return []
    return [html.Div(
        id='if-row-container-div',
        children=[if_row_create(0)]
    )]

@callback(
    Output({'type': 'if-feature-div', 'index': MATCH}, 'children'),
    Input({'type': 'if-device-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'if-device-dropdown', 'index': MATCH}, 'id')
#    prevent_initial_call=True
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
        disabled=disabled
    )]

@callback(
    Output({'type': 'if-value-div', 'index': MATCH}, 'children'),
    Input({'type': 'if-feature-dropdown', 'index': MATCH}, 'value'),
    [State({'type': 'if-device-dropdown', 'index': MATCH}, 'value'),
     State({'type': 'if-feature-dropdown', 'index': MATCH}, 'id')],
#    prevent_initial_call=True
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
                style={'width': '100px'},
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '100px'},
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
    if value is None or value == '':
        return True
    return False

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
