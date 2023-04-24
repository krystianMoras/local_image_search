
import dash

from dash import html


from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

import subprocess


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Button("Select folder", id="add", className="mr-1"),
    html.Div(id="output")
])

@app.callback(
    Output("output", "children"),
    [Input("add", "n_clicks")],
)
def add(n_clicks):
    if n_clicks > 0:
        command = ['python', './local.py']
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = p.communicate()
        print(out,err)
        return out.decode()

app.run_server(debug=True)