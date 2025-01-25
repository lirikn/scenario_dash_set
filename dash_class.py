from dash import dcc, html, callback, Output, Input, State, MATCH
import dash_bootstrap_components as dbc

devices = {}

class ScenarioClass():

    def __init__(self, cond_):
        self.cond = cond_
#        self.todo = if_todo if cond_ == 'if' else then_todo
        callbacks_func(cond_)

    def create_row(self, choice=None):
        placeholder = 'Вставить'
        if choice == 'Сценарий':
            row = scene_row(self.index, self.scenes)
        elif choice == 'Задержка':
            row = delay_row(self.index)
        elif choice == 'Устройство':
            row = device_row(self.cond, self.index, self.devices)
        else:
            placeholder = 'Добавить'
            row = []
        row.append(create_todo(self.cond, self.index, placeholder))
        self.index += 1
        return dbc.Row(row, align='center')


def create_todo(cond, index, placeholder):
   return html.Div([
        dcc.Dropdown(
            id={
                'type': cond + '-todo-dropdown',
                'index': index
            },
            options=['ТОГДА'],
            value='ТОГДА',
            style={'width': '100px'},
            placeholder=placeholder,
            clearable=False,
            searchable=False,
        )],
        style={'width': '100px'}
    )


def device_row(cond, index, options):
    return [html.Div([
            dcc.Dropdown(
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
        ],style={'width': '200px'}),
        html.Div(
            id={
                'type': cond + '-feature-div',
                'index': index
            },
            children=[],
            style={'width': '180px'}
        ),
        html.Div(
            id={
                'type': cond + '-value-div',
                'index': index
            },
            children=[],
            style={'width': '80px'}
        )
    ]

def delay_row(index):
    return [html.P("Задержка:",
            style={'width': '80px', 'height': '10px'}
        ),
        html.Div([
            dcc.Input(
                id={
                    'type': 'then-value-input',
                    'index': index
                },
                type='number',
                min=0,
                max=86399999,
                step=1,
                style={'width': '79px', 'height': '35px'}
            )],
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
        html.Div([
            dcc.Input(
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
            )],
            style={'width': '35px'}
        ),
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'then-wait-hour',
                    'index': index
                },
                options=list(range(0, 24)),
                value=0,
                clearable=False,
                searchable=False,
                style={'width': '49px'}
            )],
            style={'width': '50px'}
        ),
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'then-wait-minute',
                    'index': index
                },
                options=list(range(0, 60)),
                value=0,
                clearable=False,
                searchable=False,
                style={'width': '49px'}
            )],
            style={'width': '50px'}
        ),
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'then-wait-second',
                    'index': index
                },
                options=list(range(0, 60)),
                clearable=False,
                searchable=False,
                style={'width': '49px'}
            )],
            style={'width': '60px'}
        )
    ]

def scene_row(index, names):
    return [html.P("Сценарий:",
            style={'width': '80px', 'height': '10px'}
        ),
        html.Div([
            dcc.Dropdown(
                id={
                    'type': 'then-scene-dropdown',
                    'index': index
                },
                options=names,
                clearable=False,
                searchable=False,
                style={'width': '233px'}
            )],
            style={'width': '235px'}
        ),
        html.Div(
            id={
                'type': 'then-scene-div',
                'index': index
            },
            style={'width': '145px'}
        )
    ]


def callbacks_func(cond):
    features = 'states' if cond == 'if' else 'commands'
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


if __name__ == '__main__':
    if_row = ScenarioClass('if')
    if_row.index = 0
    if_row.devices = ['if_test']
    then_row = ScenarioClass('then')
    then_row.index = 1
    then_row.devices = ['then_test']
    then_row.scenes = ['scene_test']
    print(if_row.create_row())
    print(then_row.create_row('Сценарий'))
    print(if_row.create_row())
    print(then_row.create_row('Задержка'))


