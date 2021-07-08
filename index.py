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
elif country == "senegal":
    from apps.senegal import about
    from apps.senegal import historical
elif country == "colombia":
    from apps.colombia import historical
else:
    pass


# base_apps = { "/about": about.layout }

# et_apps = base_apps.update({ "/historical": historical.layout, })
# sn_apps = base_apps.update({ "/historical": historical.layout, })
# co_apps = base_apps.update({ "/historical": historical.layout, })


apps = {
    "ethiopia": { "/about": about.layout, "/historical": historical.layout, },
    "senegal": { "/about": about.layout, "/historical": historical.layout, },
    # "colombia": { "/about": about.layout, "/historical": historical.layout, },
}

SIMAGRI_LOGOS = app.get_asset_url("ethioagroclimate.png")

body = html.Div([
  dcc.Location(id="url", refresh=False),
  html.Div(id="page-content")
], id="body" )

app.layout = html.Div([navbar(SIMAGRI_LOGOS, country.capitalize()), body])

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
    #     return historical.layout
    # if pathname == '/about':
    #     return about.layout
    return "Nothing here"

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run_server(debug=False,
                   host="0.0.0.0",
                   port=port)
