import dash_html_components as html
import dash_bootstrap_components as dbc

layout = html.Div(
  dbc.Row(
    dbc.Col([
      html.Br(),
      html.Div(
        children= """
                    CAMDT is a tool designed to guide decision-makers in adopting appropriate crop and management practices that can improve crop yields given a seasonal climatic condition.
                  """, 
      ),
      html.Br(),
      html.Div(
      children= """
                  Smart planning of annual crop production requires consideration of possible scenarios.
                  The CAMDT tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
                  The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
                  in collaboration with CIAT-Colombia. 
                  The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
                  and evaluation of long-term effects, considering interactions of various factors.
                """, 
      ),
      html.Br(),
      html.Div([
        html.Div("Credits:"),
        html.Div("Eunjin Han, Ph.D. at IRI"),
        html.Div("Walter Baethgen, Ph.D. at IRI"),
        html.Div("Kesha Kumshayev, at IRI "),
        html.Div("Leonardo Ordonez, at CIAT-Colombia"),
        html.Div("Patricia, at CIAT-Colombia"),
      ],),
    ],
    className="text-center"
    )
  ),
)
