import dash_html_components as html
import dash_bootstrap_components as dbc

def navbar(logo):
    # NAVBAR
    navbar = dbc.Navbar([
        # LOGO & BRAND
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row([
                dbc.Col(html.Img(src=logo)),
                dbc.Col(dbc.NavbarBrand("SIMAGRI-Ethiopia", className="ml-3 font-weight-bold"),className="my-auto"),
            ],
            align ="left",
            no_gutters=True,
            ),
        href="/about",
        ),
        # NAV ITEMS
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Historical Analysis", href="/historical", ),),
            dbc.NavItem(dbc.NavLink("Forecast Analysis", href="/forecast", className="d-none", ),),
            dbc.NavItem(dbc.NavLink("About", href="/about", ),),
            dbc.NavItem(dbc.NavLink("Tutorial", href="https://sites.google.com/iri.columbia.edu/simagri-ethiopia/simagri-tutorial", ),),
            dbc.NavItem(dbc.NavLink("Feedback", href="https://sites.google.com/iri.columbia.edu/simagri-ethiopia/user-feedback-survey-form", ),),
        ],
        navbar=True,
        ),
    ],
    color="white",
    dark=False
    )
    return navbar