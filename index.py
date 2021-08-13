import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output, State

import os
import sys

from app import app
from app import server

from navbar import navbar
##########################################################################


##########################################################################
# Variable for the country determines which localization of simagri to run
country = sys.argv[1]

# app will not work if nothing is imported
if country == "ethiopia":
    from apps.ethiopia import about
    from apps.ethiopia import historical
    from apps.ethiopia import forecast_FResampler as forecast # OK
    # from apps.ethiopia import forecast_WGEN as forecast # OK
elif country == "senegal":
    from apps.senegal import about
    from apps.senegal import historical
    from apps.senegal import forecast_FResampler as forecast # Insufficient soil P data provided.  Program will stop.
    # from apps.senegal import forecast_WGEN as forecast # Insufficient soil P data provided.  Program will stop.
elif country == "colombia":
    from apps.colombia import about
    from apps.colombia import historical
    from apps.colombia import forecast_FResampler as forecast # OK
    # from apps.colombia import forecast_WGEN as forecast # OK
else:
    pass

apps = {
    "ethiopia": { 
        "logo": app.get_asset_url("ethioagroclimate.png"),
        "tutorial": "https://sites.google.com/iri.columbia.edu/simagri-ethiopia/simagri-tutorial",
        "feedback": "https://sites.google.com/iri.columbia.edu/simagri-ethiopia/user-feedback-survey-form",
        "paths": {
            "/about": about.layout,
            "/historical": historical.layout, 
            "/forecast": forecast.layout,
        },
    },
    "senegal":  { 
        "logo": app.get_asset_url("IRI_ISRA_senegal.gif"),
        "tutorial": "https://sites.google.com/iri.columbia.edu/simagri-senegal/simagri-tutorial",
        "feedback": "https://sites.google.com/iri.columbia.edu/simagri-senegal/user-feedback-survey-form",
        "paths": {
            "/about": about.layout,
            "/historical": historical.layout, 
            "/forecast": forecast.layout,
        },
    },
    "colombia": { 
        "logo": app.get_asset_url("SIMAGRI_CO_logo.GIF"), 
        "tutorial": "https://sites.google.com/iri.columbia.edu/simagri-colombia/home",
        "feedback": "https://sites.google.com/iri.columbia.edu/simagri-colombia/user-feedback-survey-form",
        "paths": {
            "/about": about.layout, 
            "/historical": historical.layout, 
            "/forecast": forecast.layout,
        },
    },
}

body = html.Div([
  dcc.Location(id="url", refresh=False),
  html.Div(id="page-content")
], id="body" )

app.layout = html.Div([navbar(apps[country]["logo"], country.capitalize(), apps[country]["tutorial"], apps[country]["feedback"] ), body])

## URL callback
################
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
)

def display_page(pathname):
    if pathname in [*apps[country]["paths"]]:
        return apps[country]["paths"][pathname]
    return "Nothing here"

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run_server(debug=False,
                   host="0.0.0.0",
                   port=port)
