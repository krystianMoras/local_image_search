from dash import Dash, html


external_scripts = [
    {
        "src": '"https://code.jquery.com/jquery-3.3.1.slim.min.js"',
        "integrity": "sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo",
        "crossorigin": "anonymous",
    },
    {
        "src": "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js",
        "integrity": "sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1",
        "crossorigin": "anonymous",
    },
    {
        "src": "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js",
        "integrity": "sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM",
        "crossorigin": "anonymous",
    },
]

# external CSS stylesheets
external_stylesheets = [
    {
        "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "rel": "stylesheet",
        "integrity": "sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO",
        "crossorigin": "anonymous",
    }
]


class CustomDash(Dash):
    def interpolate_index(self, **kwargs):
        return """
        <!DOCTYPE html>
        
        <html>
            <head>
                <title>My App</title>
                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"
    integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"
    crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"
    integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1"
    crossorigin="anonymous"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
    integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"
    crossorigin="anonymous"></script>

      <link rel="stylesheet" href="assets/photoswipe.css">
  <link rel="stylesheet" href="assets/default-skin.css">
  <link rel="stylesheet" href="assets/main.css">
            </head>
            <body>

                <div class="pswp" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="pswp__bg"></div>
    <div class="pswp__scroll-wrap">
      <div class="pswp__container">
        <div class="pswp__item"></div>
        <div class="pswp__item"></div>
        <div class="pswp__item"></div>
      </div>

      <div class="pswp__ui pswp__ui--hidden">
        <div class="pswp__top-bar">
          <div class="pswp__counter"></div>
          <button class="pswp__button pswp__button--close" title="Close (Esc)"></button>
          <button class="pswp__button pswp__button--share" title="Share"></button>
          <button class="pswp__button pswp__button--fs" title="Toggle fullscreen"></button>
          <button class="pswp__button pswp__button--zoom" title="Zoom in/out"></button>

          <div class="pswp__preloader">
            <div class="pswp__preloader__icn">
              <div class="pswp__preloader__cut">
                <div class="pswp__preloader__donut"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="pswp__share-modal pswp__share-modal--hidden pswp__single-tap">
          <div class="pswp__share-tooltip"></div>
        </div>

        <button class="pswp__button pswp__button--arrow--left" title="Previous (arrow left)"></button>
        <button class="pswp__button pswp__button--arrow--right" title="Next (arrow right)"></button>

        <div class="pswp__caption">
          <div class="pswp__caption__center"></div>
        </div>
      </div>
    </div>
  </div>


                <div class="row">
                <div class="col gallery">
                </div>
                </div>

                {app_entry}
                {config}
                {scripts}
                {renderer}
            </body>
        </html>
        """.format(
            app_entry=kwargs["app_entry"],
            config=kwargs["config"],
            scripts=kwargs["scripts"],
            renderer=kwargs["renderer"],
        )
from dash import DiskcacheManager
import diskcache
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)
app = CustomDash(
    external_scripts=external_scripts, external_stylesheets=external_stylesheets,background_callback_manager=background_callback_manager
)

import dash_bootstrap_components as dbc



app.layout = html.Div(
    [
        html.H1("Image Gallery generator"),
        dbc.Button("Select folder", id="select_folder", className="mr-1"),
        html.Div(id="output"),
        html.Progress(id="progress_bar", value="0",style={"visibility": "hidden"}),
        html.Div(id="thumbnail_generation"),

        html.Div(id="thumbnails_path")
        
    ]
)
from dash.dependencies import Input, Output

import subprocess

@app.callback(
    Output("output", "children"),
    [Input("select_folder", "n_clicks")],
)
def add(n_clicks):
    if n_clicks > 0:
        command = ['python', './local.py']
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = p.communicate()
        print(out,err)
        path = out.decode("utf-8").strip()
        return path

import time

@app.callback(
    Output("thumbnails_path", "children"),
    [Input("output", "children")],
    background=True,
    running=[
        (Output("select_folder", "disabled"), True, False),
        (
            Output("thumbnail_generation", "children"),
            "Generating thumbnails...",
            "Done",
        ),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    prevent_initial_call=True
)
def add(set_progress,path):
    total = 5
    for i in range(total + 1):
        set_progress((str(i), str(total)))
        time.sleep(1)
    return path

import os
from pathlib import Path, PurePath

# generate thumbnails
def generate_thumbnails(path):
    # for each image in path
    # generate thumbnail
    # save thumbnail in path/thumbnails

    # create thumbnails folder if not exists
    thumbnails_path = Path(path, "/thumbnails")
    thumbnails_path.mkdir(parents=True, exist_ok=True)

    # for each image in path and subfolders
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                print(PurePath(root, filename))
                






if __name__ == "__main__":
    app.run_server(debug=True)
