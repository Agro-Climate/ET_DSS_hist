import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

layout = html.Div(
  dbc.Row(
    dbc.Col([
      html.Header(
        html.B(
        "Climate-Agriculture Modeling Decision Support Tool,  SIMAGRI-Senegal overview",
        ),
        className=" card-header",
        ),

      html.Br(),
      # html.Div(
      #   children= """
      #               SIMAGRI is a tool designed to guide decision-makers in adopting appropriate crop and climat risk management practices given a seasonal climatic condition.
      #             """, 
      # ),
      # html.Br(),
      # html.Div(
      # children= """
      #             Smart planning of annual crop production requires consideration of possible scenarios.
      #             The SIMAGRI tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
      #             The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
      #             in collaboration with the Institut Sénégalais de Recherches Agricoles (ISRA), Senegal. 
      #             The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
      #             and evaluation of long-term effects, considering interactions of various factors.
      #           """, 
      # ),
      html.Div([
            dcc.Markdown('''
              SIMAGRI is a tool designed to guide decision-makers in adopting appropriate crop and climat risk management practices given a seasonal climatic condition.

              Smart planning of annual crop production requires consideration of possible scenarios.
              The SIMAGRI tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer).

              The methodology was developed by the IRI ([International Research Institute for Climate and Society](https://iri.columbia.edu/), [Columbia University](https://columbia.edu)) 
              in collaboration with the Institut Sénégalais de Recherches Agricoles (ISRA), Senegal. 

              The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
              and evaluation of long-term effects, considering interactions of various factors.

            '''),
              ], 
              style={'marginLeft': 20, 'marginRight': 10, 'marginTop': 5, 'marginBottom': 5, 
                    'backgroundColor':'#F7FBFE','padding': '6px 20px 0px 8px'}),
                    # 'border': 'thin lightgrey dashed', 'padding': '6px 20px 0px 8px'}),
      html.Br(),
      html.Header(
        html.B(
        "Authors and Contributors",
        ),
        className=" card-header",
        ),
      dcc.Markdown('''
      * **Eunjin Han**, Ph.D. International Research Institute for Climate and Society (IRI), Columbia University, USA
      * **Walter Baethgen**, Ph.D. at IRI
      * **James Hansen**, Ph.D. at IRI
      * **Kesha Kumshayev**, at IRI
      * **Adama Faye**, Institut Sénégalais de Recherches Agricoles (ISRA), Senegal
      * **Mbaye Diop**, Institut Sénégalais de Recherches Agricoles (ISRA), Senegal
      ''')  
    ],
    # className="text-center"
    )
  ),
)
