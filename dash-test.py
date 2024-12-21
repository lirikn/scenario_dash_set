from dash import Dash, dcc, html, Input, Output, State
import json

with open('config.json') as json_file:
    devices = json.load(json_file)

app = Dash(suppress_callback_exceptions=True)
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
        children=[],
        style={'columnCount': 4}
    )
])

def create_todo_item(todo_text, todo_number):
    return html.Div(
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
        options=[{'label': x, 'value': x} for x in devices[stat]['states']],
        value=None,
        style={'width': '120px'},
#                disabled=True
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
            value, len(existing_todos)
        ))
    return existing_todos

@app.callback(Output('item-container-0', 'children'),
              [Input('device-0', 'value')],
              [State('item-container-0', 'children')])
def append_stat(value, existing_todos):
    if value != None:
        existing_todos.append(create_stat(value, len(existing_todos)))
    return existing_todos

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
