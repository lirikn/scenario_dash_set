from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback, no_update
import dash_bootstrap_components as dbc
import json

with open('config.json') as json_file:
    devices = json.load(json_file)

def if_row_create(n_row):
    return dbc.Row([
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'if-device-dropdown',
                    'index': n_row
                },
                options=[{'label': x['name'], 'value': devices.index(x)}
                     for x in devices if 'states' in x],
                clearable=False,
                searchable=False,
                style={'width': '178px'}
            )],
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
        )],
#        style={'width': '540px'}
    )

def then_row_create(todo, n_row):
    rows = {
        'Устройство': [
            html.Div([
                dcc.Dropdown(
                    id={
                        'type': 'then-device-dropdown',
                        'index': n_row
                    },
                    options=[{'label': x['name'], 'value': devices.index(x)}
                         for x in devices if 'commands' in x],
                    clearable=False,
                    searchable=False,
                    style={'width': '107%'}
                )],
                style={'width': '32%'}
            ),
            html.Div(
                id={
                    'type': 'then-feature-div',
                    'index': n_row
                },
                style={'width': '32%'}
            ),
            html.Div(
                id={
                    'type': 'then-value-div',
                    'index': n_row
                },
                style={'width': '12%'}
            )
        ],
        'Задержка': [
            html.P("Задержка:",
                style={'width': '80px'}
            ),
            html.Div([
                dcc.Input(
                    id={
                        'type': 'then-wait-input',
                        'index': n_row
                    },
                    style={'width': '78px'}
                )],
                style={'width': '80px'}
            ),
            html.P("cекунд",
                style={'width': '80px'}
            ),
            html.Div([
                dcc.Input(
                    id={
                        'type': 'then-wait-day',
                        'index': n_row
                    },
                    style={'width': '35px'}
                )],
                style={'width': '36px'}
            ),
            html.P("д",
                style={'width': '0px'}
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
                    style={'width': '35px'}
                )],
                style={'width': '40px'}
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
                    style={'width': '35px'}
                )],
                style={'width': '40px'}
            ),

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
                options=['Устройство', 'Задержка', 'Сценарий', 'удалить'],
                value=None,
                placeholder='Вставить',
                clearable=False,
                disabled=False,
                searchable=False,
                style={'width': '100%'}
            )],
            style={'width': '24%'}
        )
    ],
#    style={'width': '540px'},
#    justify='center'
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
            debounce=True,
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
        children=[if_row_create(0)],
        style={'width': '540px'}
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
        style={'width': '540px'}
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
        style={'width': '178px'},
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
                style={'width': '78px'},
                clearable=False,
                searchable=False,
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '78px'},
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
        searchable=False,
        style={'width': '107%'}
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
                style={'width': '125%'},
                clearable=False,
                searchable=False,
                options=devices[device]['features'][feature].get('values', ['True', 'False'])
            )]
        disabled = False
    return [dcc.Input(
        id=id,
        style={'width': '125%'},
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
    State({'type': 'then-todo-dropdown', 'index': ALL}, 'id'),
#    State('then-row-container-div', 'children')],
    prevent_initial_call=True
)
def display_then_container_div(values, ids):
    todos = ['Устройство', 'Задержка', 'Сценарий', 'Удалить']
    children = Patch()
    for todo in todos:
        if todo in values:
            inx = values.index(todo)
            if todo == 'удалить':
                del children[inx]
                break
            children.insert(inx, then_row_create(todo, ids[inx]['index'] + 1))
            break
    return children

@callback(
    [Output({'type': 'then-todo-dropdown', 'index': ALL}, 'disabled'),
     Output({'type': 'then-todo-dropdown', 'index': ALL}, 'value')],
    Input({'type': 'then-store', 'index': ALL}, 'data'),
#    State({'type': 'then-button+', 'index': ALL}, 'id'),
#    prevent_initial_call=True
)
def display_then_button(datas):
    disabled = False in datas
    lines = len(datas) + 1
    return [disabled] * lines, [None] * lines


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
