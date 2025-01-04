from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback
import dash_bootstrap_components as dbc
import json

with open('config.json') as json_file:
    devices = json.load(json_file)

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

def then_todo_create(n_row):
    return dbc.Row([
        html.Div(
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
                    style={'width': '110px'}
                )
            ],
            style={'width': '110px'}
        ),
        html.Div(
            id={
                'type': 'then-device-div',
                'index': n_row
            },
            style={'width': '180px'}
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
            children=[],
            style={'width': '70px'}
        )
    ])


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
            value='-',
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
    html.Div(
        id='if-row-container-div',
        children=[if_row_create(0)]
    ),
    html.Div(
        id='then-row-container-div',
        children=[then_todo_create(0)]
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
    [State({'type': 'if-todo-dropdown', 'index': ALL}, 'id'),
     State('if-row-container-div', 'children')],
    prevent_initial_call=True
)
def display_if_container_div(values, ids, children):
    if values[-1] != 'ТОГДА':
        children.append(if_row_create(ids[-1]['index'] + 1))
    for i, value in enumerate(values):
        if value == 'удалить':
           del children[i]
           break
        if value == 'ТОГДА':
           del children[i+1:]
           break
    return children

@callback(
    Output({'type': 'then-device-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-todo-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'then-todo-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_then_container_div(value, id_):
    if value == 'Устройство':
        return dcc.Dropdown(
            id={
                'type': 'then-device-dropdown',
                'index': id_['index']
            },
            options=[{'label': x['name'], 'value': devices.index(x)}
                     for x in devices if 'commands' in x],
            clearable=False,
            style={'width': '180px'}
        )


@callback(
    Output({'type': 'then-feature-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-device-dropdown', 'index': MATCH}, 'value'),
    State({'type': 'then-device-dropdown', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def display_then_feature(device, id_):
    if device is None:
        return
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
        disabled=disabled,
        style={'width': '180px'}
    )]

@callback(
    Output({'type': 'then-value-div', 'index': MATCH}, 'children'),
    Input({'type': 'then-feature-dropdown', 'index': MATCH}, 'value'),
    [State({'type': 'then-device-dropdown', 'index': MATCH}, 'value'),
     State({'type': 'then-feature-dropdown', 'index': MATCH}, 'id')],
    prevent_initial_call=True
)
def display_then_value(feature, device, id_):
    if feature is None:
        return
    disabled = True
    id = {
        'type': 'then-value-input',
        'index': id_['index']
    }
    if feature is not None:
        if devices[device]['features'][feature]['type'] in ('bool', 'enum'):
            return [dcc.Dropdown(
                id=id,
                style={'width': '70px'},
                clearable=False,
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '70px'},
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
        for row in children:
            if row['props']['id']['index'] == n_row:
                children.remove(row)
                break

    print(add_clicks)
    if 1 in del_clicks:
#        del_row(ids_row[del_clicks.index(1)]['index'])
#        if not ids:
#            children.append(then_todo_create(ids_row[-1]['index'] + 1))
        return children
    if len(values) < len(ids_row):
        return children
#    if None in values and ids:
#        del_row(ids[0]['index'])
#    elif None not in values and not ids:
#        children.append(then_todo_create(ids_row[-1]['index'] + 1))
    return children

@callback(
    Output({'type': 'then-button+', 'index': ALL}, 'disabled'),
    Input({'type': 'then-value-input', 'index': ALL}, 'value'),
    State({'type': 'then-button+', 'index': ALL}, 'id'),
#    prevent_initial_call=True
)
def display_then_button(values, ids):
    ret = len(values) < len(ids) or None in values
    return [ret for i in ids]


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
