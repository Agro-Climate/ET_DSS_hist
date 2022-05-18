import dash_html_components as html
import dash_bootstrap_components as dbc

layout = html.Div(
  dbc.Row(
    dbc.Col([
      html.Br(),
      html.Div("""
          Climate-Agriculture Modeling Decision/Discussion Support Tool,  SIMAGRI-Ethiopia overview
        """,
      className="mx-auto w-75", 
      ),
      html.Br(),
      html.Div("""
          Smart planning of annual crop production requires consideration of possible scenarios.
          The CAMDT tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
          The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
          in collaboration with the Ethiopian Institute of Agricultural Research (EIAR) and CCAFS/CIMMYT-Ethiopia. 
          The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
          and evaluation of long-term effects, considering interactions of various factors.
        """,
      className="mx-auto w-75", 
      ),
      html.Br(),
      html.Div([
        html.Div("Credits:"),
        html.Div("Eunjin Han, Ph.D. at IRI"),
        html.Div("Walter Baethgen, Ph.D. at IRI"),
        html.Div("James Hansen, Ph.D. at IRI"),
        html.Div("Kesha Kumshayev, at IRI "),
        html.Div("Jemal Seid Ahmed, at EIAR"),
        html.Div("Kindie Tesfaye, Ph.D. at CIMMYT"),
        html.Div("Dawit Solomon, Ph.D. at CCAFS"),
      ],),
    ],
    className="text-center m-3"
    )
  ),
)
