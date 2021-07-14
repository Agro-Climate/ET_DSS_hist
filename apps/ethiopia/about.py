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
                  in collaboration with the Ethiopian Institute of Agricultural Research (EIAR). 
                  The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
                  and evaluation of long-term effects, considering interactions of various factors.
                """, 
      ),
      html.Br(),
      html.Div("""
          Credits:
          
          Eunjin Han, Ph.D. at IRI
          Walter Baethgen, Ph.D. at IRI
          James Hansen, Ph.D. at IRI
          Kesha Kumshayev, at IRI 
          Jemal Seid Ahmed, at EIAR
          Kindie Tesfaye, Ph.D. at CIMMYT
          Dawit Solomon, Ph.D. at CCAFS
      """
      ),
    ],
    className="text-center"
    )
  ),
)
