from dash import dcc, html, callback, Output, Input, State, MATCH, ALL, Patch, no_update
import dash_bootstrap_components as dbc

devices = {}
if_todos = [
    {'label': 'И', 'value': 1},
    {'label': 'ИЛИ', 'value': 2},
    {'label': 'ТОГДА', 'value': 3},
    {'label': 'удалить', 'value': 0}
]
then_todos = [
    {'label': 'Устройство', 'value': 1},
    {'label': 'Задержка', 'value': 2},
    {'label': 'Сценарий', 'value': 3},
    {'label': 'удалить', 'value': 0}
]

class ScenarioClass:

    def __init__(self, cond):
        self.scenes = None
        self.devices = None
        self.index = None
        self.cond = cond
        self.features = 'states' if cond == 'if' else 'commands'
        callbacks_func(cond, self.features, self.create_row)
        eval(cond + '_callbacks_func')()

    def setup(self):
        def list_sort(elem):
            return elem['label']
        self.index = 0
        self.devices = sorted([{'label': device['name'] + ' ' + device.get('room', ''), 'value': uuid}
            for uuid, device in devices.items() if self.features in device], key = list_sort)

    def create_row(self, choice=0):
        row, placeholder = link_func[choice](self.cond, self.index, self.devices, self.scenes)
        row.append(create_todo(self.cond, self.index, placeholder))
        self.index += 1
        return dbc.Row(row, align='center')


def create_todo(cond, index, placeholder):
    return html.Div(
        children=dcc.Dropdown(
            id={
                'type': cond + '-todo-dropdown',
                'index': index
            },
            options=[if_todos[2]],
            value=3 if cond == 'if' else None,
            style={'width': '100px'},
            placeholder=placeholder,
            clearable=False,
            searchable=False,
        ),
        style={'width': '100px'}
    )

def null_row(cond, index, options, names):
    return [], 'Добавить'

def device_row(cond, index, options, names):
    return [html.Div(
        children=dcc.Dropdown(
            options=options,
            id={
                'type': cond + '-device-dropdown',
                'index': index
            },
            optionHeight=50,
            clearable=False,
            value=None,
            searchable=False,
            style={'width': '199px'}
        )
        ,style={'width': '200px'}),
        html.Div(
            id={
                'type': cond + '-feature-div',
                'index': index
            },
            style={'width': '180px'}
        ),
        html.Div(
            id={
                'type': cond + '-value-div',
                'index': index
            },
            style={'width': '80px'}
        )
    ], 'Вставить'

def delay_row(cond, index, options, names):
    return [html.P("Задержка:",
            style={'width': '80px', 'height': '10px'}
        ),
        html.Div(
            children=dcc.Input(
                id={
                    'type': 'then-value-input',
                    'index': index
                },
                type='number',
                min=0,
                max=86399999,
                step=1,
                style={'width': '79px', 'height': '35px'}
            ),
            style={'width': '80px'}
        ),
        html.P("сек.",
            style={'width': '50px', 'height': '10px'}
        ),
        html.Button("-->",
            id={
                'type': 'then-wait-button',
                'index': index
            },
            style={'width': '55px', 'height': '35px'}
        ),
        html.Div(
            children=dcc.Input(
                id={
                    'type': 'then-wait-day',
                    'index': index
                },
                value=0,
                type='number',
                min=0,
                max=999,
                step=1,
                style={'width': '34px', 'height': '35px'}
            ),
            style={'width': '35px'}
        ),
        html.Div(
            children=dcc.Dropdown(
                id={
                    'type': 'then-wait-hour',
                    'index': index
                },
                options=list(range(0, 24)),
                value=0,
                clearable=False,
                searchable=False,
                style={'width': '49px'}
            ),
            style={'width': '50px'}
        ),
        html.Div(
            children=dcc.Dropdown(
                id={
                    'type': 'then-wait-minute',
                    'index': index
                },
                options=list(range(0, 60)),
                value=0,
                clearable=False,
                searchable=False,
                style={'width': '49px'}
            ),
            style={'width': '50px'}
        ),
        html.Div(
            children=dcc.Dropdown(
                id={
                    'type': 'then-wait-second',
                    'index': index
                },
                options=list(range(0, 60)),
                clearable=False,
                searchable=False,
                style={'width': '49px'}
            ),
            style={'width': '60px'}
        )
    ], 'Вставить'

def scene_row(cond, index, options, names):
    return [html.P("Сценарий:",
            style={'width': '80px', 'height': '10px'}
        ),
        html.Div(
            children=dcc.Dropdown(
                id={
                    'type': 'then-scene-dropdown',
                    'index': index
                },
                options=names,
                clearable=False,
                searchable=False,
                style={'width': '233px'}
            ),
            style={'width': '235px'}
        ),
        html.Div(
            id={
                'type': 'then-scene-div',
                'index': index
            },
            style={'width': '145px'}
        )
    ], 'Вставить'

link_func = [null_row, device_row, delay_row, scene_row]

def if_callbacks_func():
    @callback(
        Output({'type': 'if-todo-dropdown', 'index': MATCH}, 'options'),
        Input({'type': 'if-value-input', 'index': MATCH}, 'value'),
#        prevent_initial_call=True
    )
    def display_if_todo_options(value):
        return if_todos if value else if_todos[2:]

def then_callbacks_func():
    @callback(
        [Output({'type': 'then-todo-dropdown', 'index': ALL}, 'options'),
         Output({'type': 'then-todo-dropdown', 'index': ALL}, 'value')],
        Input({'type': 'then-value-input', 'index': ALL}, 'value'),
        State({'type': 'then-todo-dropdown', 'index': ALL}, 'id'),
    )
    def display_then_todo_options(values, ids):
        lines = len(ids) - 1
        if not lines or len(values) == lines and all(values):
            options = [then_todos] * lines
            options.append(then_todos[0:-1])
        else:
            options = [[then_todos[-1]]] * lines
            options.append([''])
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
        if None in (second, minute, hour, day):
            return no_update
        return day * 86400 + hour * 3600 + minute * 60 + second

    @callback(
        [Output({'type': 'then-wait-second', 'index': MATCH}, 'value'),
         Output({'type': 'then-wait-minute', 'index': MATCH}, 'value'),
         Output({'type': 'then-wait-hour', 'index': MATCH}, 'value'),
         Output({'type': 'then-wait-day', 'index': MATCH}, 'value')],
        Input({'type': 'then-wait-button', 'index': MATCH}, 'n_clicks'),
        State({'type': 'then-value-input', 'index': MATCH}, 'value'),
        prevent_initial_call=True
    )
    def display_then_wait_(_, s):
        if s is None:
            return no_update
        h = s % 86400
        m = h % 3600
        return m % 60, m // 60, h // 3600, s // 86400


def callbacks_func(cond, features, create_row):
    @callback(
        Output({'type': cond + '-feature-div', 'index': MATCH}, 'children'),
        Input({'type': cond + '-device-dropdown', 'index': MATCH}, 'value'),
        State({'type': cond + '-device-dropdown', 'index': MATCH}, 'id'),
        prevent_initial_call=True
    )
    def display_feature(uuid, id_):
        if uuid is None:
            return
        options = [{'label': devices[uuid]['features'][x]['name'], 'value': x}
             for x in devices[uuid][features]]
        return dcc.Dropdown(
            id={
                'type': cond + '-feature-dropdown',
                'index': id_['index']
            },
            options=options,
            searchable=False,
            style={'width': '179px'},
            clearable=False
        )

    @callback(
        Output({'type': cond + '-value-div', 'index': MATCH}, 'children'),
        Input({'type': cond + '-feature-dropdown', 'index': MATCH}, 'value'),
        [State({'type': cond + '-device-dropdown', 'index': MATCH}, 'value'),
         State({'type': cond + '-feature-dropdown', 'index': MATCH}, 'id')],
        prevent_initial_call=True
    )
    def display_value(feature, uuid, id_):
        disabled = True
        if feature is not None:
            if devices[uuid]['features'][feature]['type'] in ('bool', 'enum'):
                return dcc.Dropdown(
                    id={
                        'type': cond + '-value-input',
                        'index': id_['index']
                    },
                    style={'width': '79px'},
                    clearable=False,
                    searchable=False,
                    options=devices[uuid]['features'][feature].get('values', ['True', 'False'])
                )
            disabled = False
        return dcc.Input(
            id={
                'type': cond + '-value-input',
                'index': id_['index']
            },
            style={'width': '79px', 'height': '35px'},
            value=None,
            disabled=disabled
        )

    @callback(
        Output(cond + '-row-container-div', 'children'),
        Input({'type': cond + '-todo-dropdown', 'index': ALL}, 'value'),
    prevent_initial_call=True
    )
    def display_container_div(values):
        children = Patch()
        if 0 in values:
            del children[values.index(0)]
        if cond == 'if':
            if values[-1] != 3:
                children.append(create_row(1))
            else:
                idx = values.index(3) + 1
                for i in range(idx, len(values)):
                    del children[idx]
        else:
            if todo := [[i, t] for i, t in enumerate(values) if t]:
                children.insert(todo[0][0], create_row(todo[0][1]))
        return children


if __name__ == '__main__':
    if_row = ScenarioClass('if')
    if_row.index = 0
    if_row.devices = ['if_test']
    then_row = ScenarioClass('then')
    then_row.index = 1
    then_row.devices = ['then_test']
    then_row.scenes = ['scene_test']
    print(if_row.create_row())
    print(then_row.create_row(3))
    print(if_row.create_row())
    print(then_row.create_row(2))


