import dash_html_components as html
import dash_bootstrap_components as dbc

def navbar(logo, country, tutorial, feedback):
    # tutorial = dbc.NavItem(dbc.NavLink("Tutorial", target="_blank", href=tutorial, ),)
    # feedback = dbc.NavItem(dbc.NavLink("Feedback", target="_blank", href=feedback, ),)
    # NAVBAR
    if country == "Senegal":  #French version
        tutorial = dbc.NavItem(dbc.NavLink("Manuel", target="_blank", href=tutorial, ),)
        feedback = dbc.NavItem(dbc.NavLink("Retour d'information", target="_blank", href=feedback, ),)
        navbar = dbc.Navbar([
            # LOGO & BRAND
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row([
                    dbc.Col(html.Img(src=logo)),
                    dbc.Col(dbc.NavbarBrand(f"SIMAGRI-{country}", className="ml-3 font-weight-bold"),className="my-auto"),
                ],
                align ="left",
                no_gutters=True,
                ),
            href="/about",
            ),
            # NAV ITEMS
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Analyse historique", href="/historical", ),),
                # dbc.NavItem(dbc.NavLink("Forecast Analysis", href="/forecast", className="d-none", ),),
                dbc.NavItem(dbc.NavLink("Analyse des prévisions", href="/forecast", ),), #EJ(7/27/2021)
                tutorial,
                feedback,
            ],
            navbar=True,
            ),
        ],
        color="white",
        dark=False
        )
    else:  #Ethiopia and Colombia in English
        tutorial = dbc.NavItem(dbc.NavLink("Tutorial", target="_blank", href=tutorial, ),)
        feedback = dbc.NavItem(dbc.NavLink("Feedback", target="_blank", href=feedback, ),)
        navbar = dbc.Navbar([
            # LOGO & BRAND
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row([
                    dbc.Col(html.Img(src=logo)),
                    dbc.Col(dbc.NavbarBrand(f"SIMAGRI-{country}", className="ml-3 font-weight-bold"),className="my-auto"),
                ],
                align ="left",
                no_gutters=True,
                ),
            href="/about",
            ),
            # NAV ITEMS
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Historical Analysis", href="/historical", ),),
                # dbc.NavItem(dbc.NavLink("Forecast Analysis", href="/forecast", className="d-none", ),),
                dbc.NavItem(dbc.NavLink("Forecast Analysis", href="/forecast", ),), #EJ(7/27/2021)
                tutorial,
                feedback,
            ],
            navbar=True,
            ),
        ],
        color="white",
        dark=False
        )
    return navbar