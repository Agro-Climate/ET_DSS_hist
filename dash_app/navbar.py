import dash_html_components as html
import dash_bootstrap_components as dbc

def Navbar(logo):
    # NAVBAR
    navbar = dbc.Navbar([
        # LOGO & BRAND
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row([
            dbc.Col(html.Img(src=logo)),
            dbc.Col(dbc.NavbarBrand("SIMAGRI-Ethiopia", className="ml-3 font-weight-bold"),className="my-auto"),
            #EJ(6/12/2021) added Buttons for the links of Tutorial and Feedback
            dbc.Col(html.A(html.Button('Tutorial', className="ml-3 font-weight-bold"), href='https://sites.google.com/iri.columbia.edu/simagri-ethiopia/simagri-tutorial'),
            ),
            dbc.Col(html.A(html.Button('Feedback', className="ml-3 font-weight-bold"), href='https://sites.google.com/iri.columbia.edu/simagri-ethiopia/user-feedback-survey-form'),
            ),
            ],
            align ="left",
            no_gutters=True,
            ),
        href="#",
        ),
        # NAV ITEMS
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Historical Analysis", href="/historical", className="d-none", ),),
            dbc.NavItem(dbc.NavLink("Forecast Analysis", href="/forecast", className="d-none", ),),
            dbc.NavItem(dbc.NavLink("About", href="/about", className="d-none", ),),
        ],
        navbar=True,
        ),
    ],
    color="white",
    dark=False
    )
    return navbar