from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch, callback, no_update, MATCH
import random

class TestClass():
    def __init__(self, inx_):
        self.inx = inx_
        @callback(
            Output('container-div', 'children'),
            Input('button-add', 'n_clicks'),
            prevent_initial_call=True
        )
        def add_button(n_clicks):
            children = Patch()
            children.append(self.new_button())
            return children

    def new_button(self):
        self.inx += 1
        return html.Div([
            html.Button(self.inx, id={'type': 'button', 'index': self.inx}),
            html.Div(id={'type':'text', 'index': self.inx})
        ])

    def test_callback(self, rnd):
        print(rnd)
        @callback(
            Output({'type': 'text', 'index': MATCH}, 'children'),
            Input({'type': 'button', 'index': MATCH}, 'n_clicks'),
            State({'type': 'button', 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def display(n_clicks, id):
            return html.Span(f'{id["index"]}: {n_clicks} - {rnd}')


#test = None

def dyn_layout():
#    global test
    test = TestClass(0)
    test.test_callback(random.random())
    return html.Div([
        html.Div(id='live-update-text'),
        html.Div(id='container-div'),
        html.Button("-->", id='button-add')
   ])


app = Dash(suppress_callback_exceptions=True)

app.layout = dyn_layout



if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
