import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.Header import Header


layout = html.Div([
  Header("Forecast Analysis", className="text-center card-header", ),
  dbc.Row([
    dbc.Col(
      dbc.Button(
        html.Div([
          html.Div("Use Resampling Mode"),
          dbc.FormText("(faster but less precise)"),
        ]),
      className="w-75 mx-auto my-3",
      color="primary",
      href="/forecast-rs",
      ),
    className="text-center",
    ),
    dbc.Col(
      dbc.Button(
        html.Div([
          html.Div("Use Weather Generation Mode"),
          dbc.FormText("(slower but more precise)"),
        ]),
      className="w-75 mx-auto my-3",
      color="primary",
      href="/forecast-wg",
      ),
    className="text-center",
    ),
  ],
  className="py-3",
  ),
],
className="card h-100 m-3"
)