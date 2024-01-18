import dash_html_components as html
import dash_bootstrap_components as dbc

layout = html.Div(
  dbc.Row(
    dbc.Col([
      html.Br(),
      html.Div(
        children= """
                    Climate-Agriculture Modeling Decision/Discussion Support Tool,  SIMAGRI-Senegal overview
                  """, 
      ),
      html.Div(
        children= """
                    Outil d'aide à la décision pour la modélisation climato-agricole, SIMAGRI-Sénégal : vue d'ensemble 
                  """, 
      ),
      html.Br(),
      html.Div(
      children= """
                  Smart planning of annual crop production requires consideration of possible scenarios.
                  The SIMAGRI tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
                  The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
                  in collaboration with ISRA (Institut Sénégalais de Recherches Agricoles). 
                  The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
                  and evaluation of long-term effects, considering interactions of various factors.

                """, 
      ),
      html.Br(),
      html.Div(
      children= """
                  La planification intelligente de la production de cultures annuelles nécessite la prise en compte de scénarios possibles.
                  L'outil SIMAGRI adopte des modèles de simulation de cultures inclus dans le package DSSAT (Decision Support System for Agrotechnology Transfer). 
                  La méthodologie a été développée par l'IRI (International Research Institute for Climate and Society / Columbia University) en collaboration avec l'Institut Sénégalais de Recherches Agricoles (ISRA), Sénégal.
                  L'objectif de cet outil est de soutenir la prise de décision du producteur ou du conseiller technique, ce qui facilite la discussion sur les stratégies de production optimales, les risques liés à l'adoption de la technologie et l'évaluation des effets à long terme, en tenant compte des interactions de divers facteurs.

                """, 
      ),
      html.Br(),
      html.Div([
      html.Div("Credits:"),
      html.Div("Eunjin Han, Ph.D. at IRI"),
      html.Div("Walter Baethgen, Ph.D. at IRI"),
      html.Div("James Hansen, Ph.D. at IRI"),
      html.Div("Kesha Kumshayev, at IRI "),
      html.Div("Adama Faye, Institut Sénégalais de Recherches Agricoles (ISRA), Senegal"),
      html.Div("Mbaye Diop, Institut Sénégalais de Recherches Agricoles (ISRA), Senegal"),
      html.Div("Abdoulaye Diop , Institut Sénégalais de Recherches Agricoles (ISRA), Senegal"),
      ],),
    ],
    className="text-center"
    )
  ),
)
