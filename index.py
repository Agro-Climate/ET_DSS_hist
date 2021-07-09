import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output, State

import os

from app import app
from app import server


from navbar import navbar
from apps import about, tutorial, feedback
from apps.senegal import historical as sn_hist


# Preparing to use a variable for the country
country = "senegal"

base_apps = { "/about": about.layout, "/tutorial": tutorial.layout, "/feedback": feedback.layout, }

#et_apps = base_apps.update({ "/historical": et_hist.layout, })
sn_apps = base_apps.update({ "/historical": sn_hist.layout, })
# co_apps = base_apps.update({ "/historical": co_hist.layout, })


apps = {
    #"ethiopia": { "/about": about.layout, "/tutorial": tutorial.layout, "/feedback": feedback.layout,  "/historical": et_hist.layout, },
    "senegal": { "/about": about.layout, "/tutorial": tutorial.layout, "/feedback": feedback.layout,  "/historical": sn_hist.layout, },
    # "colombia": { "/about": about.layout, "/tutorial": tutorial.layout, "/feedback": feedback.layout,  "/historical": co_hist.layout, },
}

# SIMAGRI_LOGOS = app.get_asset_url("ethioagroclimate.png")
SIMAGRI_LOGOS = app.get_asset_url("IRI_ISRA_senegal.gif")


body = html.Div([
  dcc.Location(id="url", refresh=False),
  html.Div(id="page-content")
], id="body" )

app.layout = html.Div([navbar(SIMAGRI_LOGOS), body])

## URL callback
################
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
)

def display_page(pathname):
    if pathname in [*apps[country]]:
        return apps[country][pathname]

    # if pathname == '/historical':
    #     return et_hist.layout
    # if pathname == '/about':
    #     return about.layout
    return "Nothing here"

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run_server(debug=False,
                   host="0.0.0.0",
                   port=port)
    #For windows test (EJ)
    # app.run_server(debug=True)  
    # app.run_server(debug=False)  