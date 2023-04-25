# dash app with a single image

# Path: src\local_image_search\app\annotate.py

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import MATCH, ALL
from dash import Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import cv2
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dash_table
import pandas as pd
import LocalGalleryLogic as lgl
# caching
from flask_caching import Cache
from utils import *

# read config
import yaml
cfg = yaml.safe_load(open("config.yaml"))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


images = list(lgl.get_all_image_paths("images"))
faces = pd.read_csv(cfg["faces_crops"])
face_pointer = 0

people = read_people_csv(len(faces))

names = dict.fromkeys(people["name"].unique())

# cache config
cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache"})
app.config.suppress_callback_exceptions = True

@cache.memoize(timeout=3600)
def get_face_figure(face_pointer):
    global faces
    image = get_face_image(face_pointer,faces)
    # get lower resolution image for faster loading
    image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    fig = px.imshow(image, binary_backend="jpg")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=2))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    # remove background grid
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    return fig


def get_class_buttons():
    global names
    return dmc.ButtonGroup(
        [dmc.Button(name, id={"type": "class_button", "index": name},color="gray") for name in names],buttonBorderWidth=5
    )


def create_label(value):
    return dmc.Group(
        [
            dmc.Button(value, id={"type": "label_button", "index": f"button_{value}"}),
            # trash icon button
            dmc.ActionIcon(
                DashIconify(icon="mdi:trash-can-outline", width=20),
                size="lg",
                id={"type": "button_delete_option", "index": f"button_{value}_delete"},
                n_clicks=0,
                mb=10,
            ),
        ]
    )

import cozo_client

client = cozo_client.start_client(cfg["cozo_db"])
def get_similarities_table(face_pointer):
    # get similarities for each name
    return cozo_client.get_similarities_table(client, face_pointer, names)

class_card = dbc.Card(
    [
        dbc.CardHeader(html.H2("Dodaj osobę")),
        dbc.CardBody([
            dbc.Row([
    dbc.Input(id="name_input", type="text", placeholder="Wpisz imię"),
    dbc.Button("Dodaj", id="add_button"),
            ]),
            
            # datatable with names
            dash_table.DataTable(
                id="probability_table",
                columns=[{"name": "Imię", "id": "name"}, {"name": "Podobieństwo", "id": "similarity"}],
                data=get_similarities_table(face_pointer),
                style_cell={"textAlign": "center"},
                row_deletable=True,
                style_header={"textAlign": "center"},
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    }
                ],
                style_as_list_view=True,
                style_cell_conditional=[
                    {"if": {"column_id": "label"}, "width": "100%"}
                ],
                style_table={"height": "300px", "overflowY": "auto"},
            ),

            html.Div(id="output-container"),
        ]),
    ]
)

fig = get_face_figure(face_pointer)

image_annotation_card = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(html.H2("Klasyfikacja twarzy")),
        dbc.CardBody(
            [
                dcc.Graph(
                    id="graph",
                    figure=fig,
                )
            ]
        ),
        dbc.CardFooter(
            [
                dbc.Container([
                    dbc.Row(id="class_checkboxes",children=[
                      get_class_buttons() 
                    ]),
                ]),
                dbc.Col([
                    dbc.Row("Wybierz jedną z osób lub dodaj nową"),
                    dbc.Row("Przejdź do kolejnej osoby klikając przycisk 'Następny'"),
                    dbc.Row("Możesz cofać się i wyjść w dowolnym momencie, wyniki zostaną zapisane")
            ],style={"padding": "10px"}),
                dbc.ButtonGroup(
                    [
                        dbc.Button("Poprzedni", id="previous", outline=True),
                        dbc.Button("Następny", id="next", outline=True),
                    ],
                    size="lg",
                    style={"width": "100%"},
                ),
            ]
        ),
    ],
)
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Image Annotation App")),
                ],
                align="center",
            ),
            dbc.Row(
                dbc.Col(
                    [
                        dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Collapse(
                            dbc.Nav(
                                [],
                                className="ml-auto",
                                navbar=True,
                            ),
                            id="navbar-collapse",
                            navbar=True,
                        ),
                    ]
                ),
                align="center",
            ),
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
    className="mb-5",
)

# put annotate_div in a dbc card
app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(image_annotation_card, md=7),
                        dbc.Col(class_card, md=3),
                    ],
                ),
            ]
        ),
    ]
)

@app.callback(
    [Output('probability_table', 'data'),Output("class_checkboxes", "children")],
    [Input('add_button', 'n_clicks'),Input("previous", "n_clicks"), Input("next", "n_clicks")],
    State('name_input', 'value'))
def table_change(n_clicks,n_clicks_2,n_clicks_3,name):
    global face_pointer
    buttons_patch = Patch()
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext == "add_button.n_clicks":
        if name != None:
            names[name] = None
        buttons_patch = get_class_buttons()
    return get_similarities_table(face_pointer), buttons_patch


@app.callback(
    Output("graph", "figure"),
    [Input("previous", "n_clicks"), Input("next", "n_clicks")],
)
def update_image(previous, next):
    global face_pointer
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if previous is None:
        previous = 0
    if next is None:
        next = 0

    if cbcontext == "previous.n_clicks":
        image_index_change = -1
    if cbcontext == "next.n_clicks":
        image_index_change = 1

    face_pointer += image_index_change
    face_pointer %= len(faces)

    return get_face_figure(face_pointer)


@app.callback(
    [Output({"type": "class_button", "index": ALL}, "color")],
    [Input({"type": "class_button", "index": ALL}, "n_clicks"),Input("previous", "n_clicks"), Input("next", "n_clicks")],
)
def update_choice(n_clicks,n_clicks_2,n_clicks_3):
    global face_pointer
    
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext not in [".", "previous.n_clicks", "next.n_clicks"] :
        choice = list(dash.callback_context.triggered_prop_ids.values())[0]["index"]
        people.loc[face_pointer, "name"] = choice
        people.to_csv(cfg["faces_names"], index=False)

    return get_colors(face_pointer, people, names)



if __name__ == "__main__":
    app.run_server(debug=True)
