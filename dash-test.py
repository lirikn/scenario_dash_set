from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import json

with open('config.json') as json_file:
    devices = json.load(json_file)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
layout = html.Div([
    dcc.Input(
        placeholder='Введите название',
        id='add-todo',
        debounce=True,
        value=None,
        style={'width': '400px'}
    ),

    html.Div(
        id='todo-container',
        children=[]
#        style={'columnCount': 4}
    )
])

def create_todo_item(todo_text, todo_number):
    return dbc.Row(
        id='item-container-{}'.format(todo_number),
        children=[
            dcc.Dropdown(
                id='device-{}'.format(todo_number),
                options=[{'label': x['name'], 'value': devices.index(x)} for x in devices if 'states' in x],
                value=None,
                style={'width': '250px'}
            )
        ]
    )

def create_stat(stat, stat_number):
    return dcc.Dropdown(
        id='stat-{}'.format(stat_number),
        options=[{'label': devices[stat]['features'][x]['name'], 'value': x}
                 for x in devices[stat]['states']],
        value=None,
        style={'width': '250px'},
#                disabled=True
    )

def create_if(value, row_number):
    return dcc.Dropdown(
        id='if-{}'.format(row_number),
        options=[{'label': x, 'value': x} for x in range(5)],
        value=None,
        style={'width': '50px'},
    )

app.layout = layout

@app.callback(Output('todo-container', 'children'),
              [Input('add-todo', 'value')],  
              [State('todo-container', 'children')])
def append_todo(value, existing_todos):
    if value == '':
        existing_todos.clear()
    elif value != None and len(existing_todos) == 0:
       existing_todos.append(create_todo_item(
            value, 0
        ))
    return existing_todos

@app.callback(Output('item-container-0', 'children'),
              [Input('device-0', 'value'),
               Input('stat-0', 'value')],
              [State('item-container-0', 'children'),
               State('device-0', 'n_clicks')])
def append_stat(device, feature, existing_todos, n_clicks):
    if device != None:
        if len(existing_todos) == 1:
            existing_todos.append(create_stat(device, 0))
        else:
            existing_todos[1] = create_stat(device, 0)
    return existing_todos

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
