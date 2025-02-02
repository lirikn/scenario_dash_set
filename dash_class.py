from dash import Dash, dcc, html, callback, Output, Input, State, MATCH, ALL, Patch, no_update
import dash_bootstrap_components as dbc

class SceneIfClass:
    cond = 'stat'
    todos = [
        {'label': 'И', 'value': 1},
        {'label': 'ИЛИ', 'value': 2},
        {'label': 'ТОГДА', 'value': 3},
        {'label': 'удалить', 'value': 0}
    ]

    def __init__(self):

        @callback(
            Output({'type': 'stat-todo-dropdown', 'index': MATCH}, 'options'),
            Input({'type': 'stat-value-input', 'index': MATCH}, 'value'),
            #        prevent_initial_call=True
        )
        def display_stat_todo_options(value):
            return self.todos if value else self.todos[2:]

        self.init()

    def init(self):

        @callback(
            Output({'type': self.cond + '-feature-div', 'index': MATCH}, 'children'),
            Input({'type': self.cond + '-device-dropdown', 'index': MATCH}, 'value'),
            State({'type': self.cond + '-device-dropdown', 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def display_feature(topic, id_):
            if topic is None:
                return
            options = [{'label': x['name'], 'value': key} for key, x in self.features[topic].items()]
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
        def display_value(feature, topic, id_):
            disabled = True
            if feature is not None:
                if self.features[topic][feature]['type'] in ('bool', 'enum'):
                    return dcc.Dropdown(
                        id={
                            'type': self.cond + '-value-input',
                            'index': id_['index']
                        },
                        style={'width': '79px'},
                        clearable=False,
                        searchable=False,
                        options=self.features[topic][feature].get('values', ['True', 'False'])
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

    def setup(self, devices):
        def list_sort(elem):
            return elem['label']
        self.index = 0
        self.devices = []
        self.features = {}
        for device in devices:
            features = device.get(self.cond)
            if features:
                self.devices.append({'label': device['name'] + ' ' + device.get('room', ''), 'value': device['topic']})
                self.features[device['topic']] = {feature: device['features'][feature] for feature in features}
        self.devices.sort(key = list_sort)

class SceneThenClass(SceneIfClass):
    cond = 'cmnd'
    todos = [
        {'label': 'Устройство', 'value': 1},
        {'label': 'Задержка', 'value': 2},
        {'label': 'Сценарий', 'value': 3},
        {'label': 'удалить', 'value': 0}
    ]

    def __init__(self):

        self.scenes = None

        @callback(
            [Output({'type': 'cmnd-todo-dropdown', 'index': ALL}, 'options'),
             Output({'type': 'cmnd-todo-dropdown', 'index': ALL}, 'value')],
            Input({'type': 'cmnd-value-input', 'index': ALL}, 'value'),
            State({'type': 'cmnd-todo-dropdown', 'index': ALL}, 'id'),
        )
        def display_cmnd_todo_options(values, ids):
            lines = len(ids) - 1
            if not lines or len(values) == lines and all(values):
                options = [self.todos] * lines
                options.append(self.todos[0:-1])
            else:
                options = [[self.todos[-1]]] * lines
                options.append([''])
            return options, [None] * (lines + 1)

        @callback(
            Output({'type': 'cmnd-value-input', 'index': MATCH}, 'value'),
            [Input({'type': 'cmnd-wait-second', 'index': MATCH}, 'value'),
             Input({'type': 'cmnd-wait-minute', 'index': MATCH}, 'value'),
             Input({'type': 'cmnd-wait-hour', 'index': MATCH}, 'value'),
             Input({'type': 'cmnd-wait-day', 'index': MATCH}, 'value')],
            prevent_initial_call=True
        )
        def display_cmnd_wait(second, minute, hour, day):
            if None in (second, minute, hour, day):
                return no_update
            return day * 86400 + hour * 3600 + minute * 60 + second

        @callback(
            [Output({'type': 'cmnd-wait-second', 'index': MATCH}, 'value'),
             Output({'type': 'cmnd-wait-minute', 'index': MATCH}, 'value'),
             Output({'type': 'cmnd-wait-hour', 'index': MATCH}, 'value'),
             Output({'type': 'cmnd-wait-day', 'index': MATCH}, 'value')],
            Input({'type': 'cmnd-wait-button', 'index': MATCH}, 'n_clicks'),
            State({'type': 'cmnd-value-input', 'index': MATCH}, 'value'),
            prevent_initial_call=True
        )
        def display_cmnd_wait_(_, s):
            if s is None:
                return no_update
            h = s % 86400
            m = h % 3600
            return m % 60, m // 60, h // 3600, s // 86400

        self.init()

    def add_to_container(self, children, values):
        todo = [[i, t] for i, t in enumerate(values) if t]
        if todo:
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
                        'type': 'cmnd-value-input',
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
                    'type': 'cmnd-wait-button',
                    'index': self.index
                },
                style={'width': '55px', 'height': '35px'}
            ),
            html.Div(
                children=dcc.Input(
                    id={
                        'type': 'cmnd-wait-day',
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
                        'type': 'cmnd-wait-hour',
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
                        'type': 'cmnd-wait-minute',
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
                        'type': 'cmnd-wait-second',
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
                        'type': 'cmnd-scene-dropdown',
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
                    'type': 'cmnd-scene-div',
                    'index': self.index
                },
                style={'width': '145px'}
            )
        ]
