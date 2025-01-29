from dash import Dash, dcc, html, callback, Output, Input, State, MATCH, ALL, Patch, no_update
import dash_bootstrap_components as dbc

devices = {}

class SceneIfClass:
    def __init__(self):
        self.cond = 'if'
        self.features = 'states'
        self.todos = [
            {'label': 'И', 'value': 1},
            {'label': 'ИЛИ', 'value': 2},
            {'label': 'ТОГДА', 'value': 3},
            {'label': 'удалить', 'value': 0}
        ]

        @callback(
            Output({'type': 'if-todo-dropdown', 'index': MATCH}, 'options'),
            Input({'type': 'if-value-input', 'index': MATCH}, 'value'),
            #        prevent_initial_call=True
        )
        def display_if_todo_options(value):
            return self.todos if value else self.todos[2:]

        self.init()

    def init(self):

        @callback(
            Output({'type': self.cond + '-feature-div', 'index': MATCH}, 'children'),
            Input({'type': self.cond + '-device-dropdown', 'index': MATCH}, 'value'),
            State({'type': self.cond + '-device-dropdown', 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def display_feature(uuid, id_):
            if uuid is None:
                return
            options = [{'label': devices[uuid]['features'][x]['name'], 'value': x}
                       for x in devices[uuid][self.features]]
            return dcc.Dropdown(
                id={
                    'type': self.cond + '-feature-dropdown',
                    'index': id_['index']
                },
                options=options,
                searchable=False,
                style={'width': '179px'},
                clearable=False
            )

        @callback(
            Output({'type': self.cond + '-value-div', 'index': MATCH}, 'children'),
            Input({'type': self.cond + '-feature-dropdown', 'index': MATCH}, 'value'),
            [State({'type': self.cond + '-device-dropdown', 'index': MATCH}, 'value'),
             State({'type': self.cond + '-feature-dropdown', 'index': MATCH}, 'id')],
            prevent_initial_call=True
        )
        def display_value(feature, uuid, id_):
            disabled = True
            if feature is not None:
                if devices[uuid]['features'][feature]['type'] in ('bool', 'enum'):
                    return dcc.Dropdown(
                        id={
                            'type': self.cond + '-value-input',
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
                    'type': self.cond + '-value-input',
                    'index': id_['index']
                },
                style={'width': '79px', 'height': '35px'},
                value=None,
                disabled=disabled
            )

        @callback(
            Output(self.cond + '-row-container-div', 'children'),
            Input({'type': self.cond + '-todo-dropdown', 'index': ALL}, 'value'),
            prevent_initial_call=True
        )
        def display_container_div(values):
            children = Patch()
            if 0 in values:
                del children[values.index(0)]
            return self.add_to_container(children, values)

    def add_to_container(self, children, values):
        if values[-1] != 3:
            children.append(self.create_row())
        else:
            idx = values.index(3) + 1
            for i in range(idx, len(values)):
                del children[idx]
        return children

    def create_row(self, choice=0):
        return self.create_todo(self.device_row, value=3)

    def create_todo(self, func, placeholder=None, value=None):
        row = func()
        row.append(html.Div(
            children=dcc.Dropdown(
                id={
                    'type': self.cond + '-todo-dropdown',
                    'index': self.index
                },
                options=[self.todos[2]],
                value=value,
                style={'width': '100px'},
                placeholder=placeholder,
                clearable=False,
                searchable=False,
            ),
            style={'width': '100px'}
        ))
        self.index += 1
        return dbc.Row(row, align='center')

    def device_row(self):
        return [html.Div(
            children=dcc.Dropdown(
                options=self.devices,
                id={
                    'type': self.cond + '-device-dropdown',
                    'index': self.index
                },
                optionHeight=50,
                clearable=False,
                value=None,
                searchable=False,
                style={'width': '199px'}
            )
            , style={'width': '200px'}),
            html.Div(
                id={
                    'type': self.cond + '-feature-div',
                    'index': self.index
                },
                style={'width': '180px'}
            ),
            html.Div(
                id={
                    'type': self.cond + '-value-div',
                    'index': self.index
                },
                style={'width': '80px'}
            )
        ]

    def setup(self):
        def list_sort(elem):
            return elem['label']
        self.index = 0
        self.devices = sorted([{'label': device['name'] + ' ' + device.get('room', ''), 'value': uuid}
            for uuid, device in devices.items() if self.features in device], key = list_sort)


class SceneThenClass(SceneIfClass):

    def __init__(self):
        self.scenes = None
        self.cond = 'then'
        self.features = 'commands'
        self.todos = [
            {'label': 'Устройство', 'value': 1},
            {'label': 'Задержка', 'value': 2},
            {'label': 'Сценарий', 'value': 3},
            {'label': 'удалить', 'value': 0}
        ]

        @callback(
            [Output({'type': 'then-todo-dropdown', 'index': ALL}, 'options'),
             Output({'type': 'then-todo-dropdown', 'index': ALL}, 'value')],
            Input({'type': 'then-value-input', 'index': ALL}, 'value'),
            State({'type': 'then-todo-dropdown', 'index': ALL}, 'id'),
        )
        def display_then_todo_options(values, ids):
            lines = len(ids) - 1
            if not lines or len(values) == lines and all(values):
                options = [self.todos] * lines
                options.append(self.todos[0:-1])
            else:
                options = [[self.todos[-1]]] * lines
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

        self.init()

    def add_to_container(self, children, values):
        if todo := [[i, t] for i, t in enumerate(values) if t]:
            children.insert(todo[0][0], self.create_row(todo[0][1]))
        return children

    def create_row(self, choice=0):
        link_func = [list, self.device_row, self.delay_row, self.scene_row]
        placeholder = 'Вставить' if choice else 'Добавить'
        return self.create_todo(link_func[choice], placeholder=placeholder)

    def delay_row(self):
        return [html.P("Задержка:",
                style={'width': '80px', 'height': '10px'}
            ),
            html.Div(
                children=dcc.Input(
                    id={
                        'type': 'then-value-input',
                        'index': self.index
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
                    'index': self.index
                },
                style={'width': '55px', 'height': '35px'}
            ),
            html.Div(
                children=dcc.Input(
                    id={
                        'type': 'then-wait-day',
                        'index': self.index
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
                        'index': self.index
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
                        'index': self.index
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
                        'index': self.index
                    },
                    options=list(range(0, 60)),
                    clearable=False,
                    searchable=False,
                    style={'width': '49px'}
                ),
                style={'width': '60px'}
            )
        ]

    def scene_row(self):
        return [html.P("Сценарий:",
                style={'width': '80px', 'height': '10px'}
            ),
            html.Div(
                children=dcc.Dropdown(
                    id={
                        'type': 'then-scene-dropdown',
                            'index': self.index
                        },
                    options=self.scenes,
                    clearable=False,
                    searchable=False,
                    style={'width': '233px'}
                ),
                style={'width': '235px'}
            ),
            html.Div(
                id={
                    'type': 'then-scene-div',
                    'index': self.index
                },
                style={'width': '145px'}
            )
        ]


if __name__ == '__main__':
    if_row = SceneIfClass()
    then_row = SceneThenClass()
    if_row.setup()
    then_row.setup()
    then_row.scenes = ['scene_test']
    print(if_row.create_row())
    print(then_row.create_row(3))
    print(if_row.create_row())
    print(then_row.create_row(2))


