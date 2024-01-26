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
    from apps.ethiopia import forecast_FResampler as forecast
    # from apps.ethiopia import forecast_WGEN as forecast

    # from apps.ethiopia import forecast as forecast_choice
    # from apps.ethiopia import forecast_FResampler as forecast_rs
    # from apps.ethiopia import forecast_WGEN as forecast_wg
elif country == "senegal":
    from apps.senegal import about
    from apps.senegal import historical
    # from apps.senegal import historical_FR
    from apps.senegal import forecast_FResampler as forecast
    # from apps.senegal import forecast_WGEN as forecast
elif country == "colombia":
    from apps.colombia import about
    from apps.colombia import historical
    from apps.colombia import forecast_FResampler as forecast
    # from apps.colombia import forecast_WGEN as forecast
else:
    pass

apps = {
    "ethiopia": { 
        "logo": app.get_asset_url("CWP_IRI_ET.gif"), #simagri-logo-2.png"), #ethioagroclimate.png"),
        "tutorial": "https://sites.google.com/iri.columbia.edu/simagri-ethiopia/simagri-tutorial",
        "feedback": "https://sites.google.com/iri.columbia.edu/simagri-ethiopia/user-feedback-survey-form",
        "paths": {
            "/about": about.layout,
            "/historical": historical.layout,
            "/forecast": forecast.layout,
            # "/forecast": forecast_choice.layout,
            # "/forecast-rs": forecast_rs.layout,
            # "/forecast-wg": forecast_wg.layout,
        },
    },
    "senegal":  { 
        # "logo": app.get_asset_url("CWP_IRI_ISRA_senegal.GIF"), #IRI_ISRA_senegal.gif"),
        "logo": app.get_asset_url("SIMAGRI_senegal_AICCRA_logo.gif"), 
        # "tutorial": "https://sites.google.com/iri.columbia.edu/simagri-senegal/simagri-tutorial",
        "tutorial": "https://sites.google.com/iri.columbia.edu/simagri-french/simagri-tutorial",
        "feedback": "https://sites.google.com/iri.columbia.edu/simagri-senegal/user-feedback-survey-form",
        "paths": {
            "/about": about.layout,
            "/historical": historical.layout, 
            "/forecast": forecast.layout,
        },
    },
    "colombia": { 
        "logo": app.get_asset_url("CWP_IRI_CO_logo.GIF"), #SIMAGRI_CO_logo.GIF"), #
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
    # return "Nothing here"
    return "Climate-Agriculture Modeling Decision Support Tool,  SIMAGRI. Please click the main menu bars for SIMAGRI analysis"
    

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run_server(debug=False,
                   host="0.0.0.0",
                   port=port)
