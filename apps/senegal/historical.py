import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pathlib
import re
import base64
import io

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table

from dash.dependencies import Input, Output, State
from dash_extensions import Download
from dash.exceptions import PreventUpdate
#import folium
#from folium.plugins import MarkerCluster
from app import app

from os import path # path
import os
import subprocess  #to run executable
from datetime import date
import datetime    #to convert date to doy or vice versa
import calendar
import bisect   # an element into sorted list

import graph

sce_col_names=[ "sce_name", "Crop", "Cultivar", "stn_name", "PltDate", "FirstYear", "LastYear", "soil", "iH2O", "iNO3", "plt_density", "TargetYr",
                "Fert_1_DOY", "N_1_Kg", "P_1_Kg", "K_1_Kg", "Fert_2_DOY", "N_2_Kg", "P_2_Kg", "K_2_Kg", "Fert_3_DOY", "N_3_Kg", "P_3_Kg", "K_3_Kg",
                "Fert_4_DOY", "N_4_Kg", "P_4_Kg", "K_4_Kg", "P_level", "IR_method", "IR_1_DOY", "IR_1_amt", "IR_2_DOY", "IR_2_amt", "IR_3_DOY", "IR_3_amt",
                "IR_4_DOY", "IR_4_amt", "IR_5_DOY", "IR_5_amt", "AutoIR_depth", "AutoIR_thres", "AutoIR_eff",
                "CropPrice", "NFertCost", "SeedCost", "IrrigCost","OtherVariableCosts", "FixedCosts"
],  #  

#Fert_4_DOY=0,
#N_4_Kg=0,
#P_4_Kg=0,
#K_4_Kg=0,

Position= { "Dakar":  [14.700047543225823, -17.50001290971342 ] , 
            "Bambey": [15.000134707867867, -16.49997854796095 ], 
            "Mbacke": [14.80013483323102, -15.900042920979626 ] , 
            "Fatick_Niakhar": [14.500155792376464, -16.400032192151638],
            "Foundiougne":  [13.90012496236718, -16.400010734495066 ],
            "Birkilane":  [14.10010404228193, -15.800000005654653 ],
            "Kounguel":  [14.00014572838203, -14.80002146332832 ],
            "Kaolack":  [ 14.100156070240521, -16.10000000565467],
            "Nioro du Rip":   [13.700156340499975, -15.800032192171074 ],
            "Kolda":  [12.800198769551196, -14.60000000568494 ],
            "Medina Yoroufoula":  [13.100156731601537, -14.600032192184925],
            "Velingrara":  [12.90017777424403, -14.100000005682656 ],
            "Linguere":  [15.300155213889152, -15.500042920966724 ],
            "Louga":  [ 15.500103371403704, -16.0000214632902],
           "Saint Louis":  [16.100133989082607, -16.49997854793152],
            "Sedhiou":  [12.700198848162987, -15.6000429210294 ],
            "Koumpentoum":  [14.00017695879087, -14.600032192163923],
            "Tambacounda 1":  [13.100177630843898, -13.300021463349408],
            "Tambacounda 2":  [13.800177111914401, -13.700010734497527 ],
            "Tambacounda 3":  [13.90015620632161, -14.100042921001881 ],
            "Mbour":  [14.40019742960074, -17.00000000564732 ],
            "Thies":  [14.800186697639713, -17.000000005637286 ],
            "Tivaoune":  [ 15.000196887377449, -16.800021463303363],
            "Bignona":  [ 13.000188156663333, -16.200010734516013],
            "Oussouye":  [12.50016758003306, -16.499989276855867 ],
            "Ziguinchor":  [12.500157105519985, -16.00004292103381 ],
          }
#a=folium.Map(location=(14.700047543225823, -17.50001290971342))      # afficher la carte

#for ville,coords in Position.items():
#     folium.Marker(coords,popup=f"<b>{ville}</b><br>{coords}",
#     tooltip=ville, icon=folium.Icon(icon="cloud")).add_to(a)


layout = html.Div([
    dcc.Store(id="memory-yield-table"),  #to save fertilizer application table
    dcc.Store(id="memory-sorted-yield-table"),  #to save fertilizer application table
    dcc.Store(id="memory-EB-table"),  #to save fertilizer application table
    dbc.Row([
      dbc.Col([ ## LEFT HAND SIDE
        html.Div(
          html.Div([
            html.Header(
              html.B(
                "Données d’entrée de la simulation (Historique)",
              ),
            className=" card-header",
            ),

            dbc.Form([ ## INPUT FORM
              html.Div( # SCROLLABLE FORM
                html.Div([ # FORM START
                  dbc.FormGroup([ # Scenario
                    dbc.Label("1) Nom du scénario", html_for="sce-name", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="text", id="sce-name", value="", minLength=4, maxLength=4, required="required", ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Station
                    dbc.Label("2) Station", html_for="SNstation", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                      id="SNstation",
                      # options=[
                      #   {"label": "Bambey", "value": "CNRA"},
                      #   {"label": "Nioro", "value": "NRIP"},
                      #   {"label": "Sinthiou Malem", "value": "SNTH"}
                      # ],
                      # value="CNRA",
                      options=[
                        {"label": "Dakar(14.7N, 17.5W),", "value": "0002"}, #1
                        {"label": "Bambey(15.0N, 16.5W)", "value": "0032"}, #2
                        {"label": "Mbacke(14.8N, 15.9W)", "value": "4871"}, #3
                        {"label": "Fatick(14.5N, 16.4W)", "value": "1669"}, #4
                        {"label": "Foundiougne(13.9N, 16.4W)", "value": "2014"}, #5
                        {"label": "Birkelane(14.1N, 15.8W)", "value": "2843"}, #6
                        {"label": "Koungheul(14.0N, 14.8W)", "value": "2454"}, #7
                        {"label": "Kaolack(14.1N, 16.1W)", "value": "3292"}, #8
                        {"label": "Nioro Du Rip(13.7N, 15.8W)", "value": "5699"}, #9
                        {"label": "Kolda(12.8N, 14.6W)", "value": "4051"}, #10
                        {"label": "Medina Yoroufoula(13.1N, 14.6W)", "value": "2127"}, #11
                        {"label": "Velingara(12.9N, 14.1W)", "value": "5976"}, #12
                        {"label": "Linguere(15.3N, 15.5W)", "value": "5884"}, #13
                        {"label": "Louga(15.5N, 16.0W)", "value": "2898"}, #14
                        {"label": "Saint Louis(16.1N, 16.5W)", "value": "5017"}, #15
                        {"label": "Sedhiou(12.7N, 15.6W)", "value": "1758"}, #16
                        {"label": "Koumpentoum(14.0N, 14.6W)", "value": "0171"}, #17
                        {"label": "Tambacounda(13.1N, 13.3W)", "value": "4506"}, #18
                        {"label": "Tambacounda(13.8N, 13.7W)", "value": "3317"}, #19
                        {"label": "Tambacounda(13.9N, 14.1W)", "value": "3366"}, #20
                        {"label": "Mbour(14.4N, 17.0W)", "value": "6083"}, #21
                        {"label": "Thies(14.8N, 17.0W)", "value": "3167"}, #22
                        {"label": "Tivaoune(15.0N, 16.8W)", "value": "5664"}, #23
                        {"label": "Bignona(13.0N, 16.2W)", "value": "6120"}, #24
                        {"label": "Oussouye(12.5N, 16.5W)", "value": "1171"}, #25
                        {"label": "Ziguinchor(12.5N, 16.0W)", "value": "5457"}, #25
                      ],
                      value="0032",  #"CNRA"
                      clearable=False,
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Crop
                    dbc.Label("3) Culture", html_for="crop-radio", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                      id="crop-radio",
                      # options=[{"label": k, "value": k} for k in cultivar_options.keys()],
                      options = [
                        {"label": "Arachide", "value": "PN"},
                        {"label": "Mil", "value": "ML"},
                        {"label": "Sorgho", "value": "SG"},
                      ],
                      labelStyle = {"display": "inline-block","marginRight": 10},
                      value="SG",
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Cultivar
                    dbc.Label("4) Cultivar", html_for="cultivar-dropdown", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="cultivar-dropdown",
                        options=[
                          {"label": "Fadda-D", "value": "IB0066 Fadda-D"},
                          {"label": "IS15401-D", "value": "IB0069 IS15401-D"},
                          {"label": "Soumba-D", "value": "IB0070 Soumba-D"},
                          {"label": "Faourou-D", "value": "IB0071 Faourou-D"},],
                        value="IB0066 Fadda-D",
                        clearable=False,
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Start Year
                    dbc.Label("5) Année de début de la simulation ", html_for="year1", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="year1", placeholder="YYYY", value="1983", min=1983, max=2016, required="required", ),
                      dbc.FormText("(au plus tôt en 1983)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # End Year
                    dbc.Label("6) Année de fin de la simulation ", html_for="year2", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="year2", placeholder="YYYY", value="2016", min=1983, max=2016,   required="required", ),
                      dbc.FormText("(pas plus tard que 2016)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Year to Highlight
                    dbc.Label("7) Une année à mettre en évidence", html_for="target-year", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="target-year", placeholder="YYYY", value="2016",min=1983, max=2016,   required="required", ),
                      dbc.FormText("Tapez une année spécifique dont vous vous souvenez (par exemple, une année de sécheresse) et que vous souhaitez comparer avec une distribution climatologique complète."),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Soil Type
                    dbc.Label("8) Type de sol", html_for="SNsoil", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="SNsoil",
                        options=[
                          {"label": "CNCNioro14(S)", "value": "CNCNioro14"},
                          {"label": "CNNior14_S(S)-shallow", "value": "CNNior14_S"},
                          {"label": "CNCNNior15(SL)", "value": "CNCNNior15"},
                          {"label": "CNNior15_S(S)-shallow", "value": "CNNior15_S"},
                          {"label": "CNBambey14(LS)", "value": "CNBambey14"},
                          {"label": "CNBambey14(S)-shallow", "value": "CNBambey14"},
                          {"label": "SN-N15Rain(S)", "value": "SN-N15Rain"},
                          {"label": "SN-N15Irrg(S)", "value": "SN-N15Irrg"},
                          {"label": "SN-N16Rain(S)", "value": "SN-N16Rain"},
                          {"label": "SN-N16Irrg(S)", "value": "SN-N16Irrg"},
                          {"label": "SN-S15Rain(LS)", "value": "SN-S15Rain"},
                          {"label": "SN-S16Rain(LS)", "value": "SN-S16Rain"},
                          {"label": "SN00840067(SL)", "value": "SN00840067"},
                          {"label": "SN00840080(SL)", "value": "SN00840080"},
                          {"label": "SN00840042(SL)", "value": "SN00840042"},
                          {"label": "SN00840056(SL)", "value": "SN00840056"},
                        ],
                        value="SN-N15Rain",
                        clearable=False,
                      ),
                    # dbc.FormText("S, LS, and SL in parenthesis represent Sand, Loamy sand, and Sandy loam, respectively."),
                    dbc.FormText("S, LS et SL entre les parenthèses représentent respectivement le Sable, le Sable Limoneux et le Limon Sableux."),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Initial Soil Water Condition
                    dbc.Label("9) État hydrique initial du sol", html_for="ini-H2O", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="ini-H2O",
                        options=[
                          {"label": "10% of AWC", "value": "0.1"},
                          {"label": "20% of AWC", "value": "0.2"},
                          {"label": "30% of AWC", "value": "0.3"},
                          {"label": "40% of AWC", "value": "0.4"},
                          {"label": "50% of AWC", "value": "0.5"},
                          {"label": "60% of AWC", "value": "0.6"},
                          {"label": "70% of AWC", "value": "0.7"},
                          {"label": "80% of AWC", "value": "0.8"},
                          {"label": "90% of AWC", "value": "0.9"},
                          {"label": "100% of AWC", "value": "1.0"},
                        ],
                        value="0.5",
                        clearable=False,
                      ),
                    dbc.FormText("Capacité de rétention d'eau disponible (AWC)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Initial NO3 Condition
                    dbc.Label(["10) Teneur initiale du sol en NO3", html.Span("  ([N kg/ha] dans les 30 premiers centimètres du sol)"), ],html_for="ini-NO3", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="ini-NO3", value="20.1",min=1, max=150, step=0.1, required="required", ),
                      dbc.FormText("[Référence] Faible teneur en nitrates : 20 N kg/ha (~ 4,8 ppm), forte teneur en nitrates : 85 N kg/ha (~20 ppm)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Date
                    dbc.Label("11) Date de semis", html_for="PltDate-picker", sm=3, align="start", ),
                    dbc.Col([
                      dcc.DatePickerSingle(
                      id="PltDate-picker",
                      min_date_allowed=date(2021, 1, 1),
                      max_date_allowed=date(2021, 12, 31),
                      initial_visible_month=date(2021, 6, 5),
                      display_format="DD/MM/YYYY",
                      date=date(2021, 6, 15),
                      ),
                      dbc.FormText("Seuls le mois et la date sont pris en compte"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Density
                    dbc.Label(["12) Densité de semis", html.Span(" (plants/m"), html.Sup("2"), html.Span(")"), ], html_for="plt-density", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="plt-density", value=5, min=1, max=300, step=0.1, required="required", ),
                      # dbc.FormText("Typical planting density is 4, 6 and 17 plants/m2 for millet, sorghum and peanut respectively."),
                      dbc.FormText("La densité de semi recommandée est respectivement de 4, 6 et 17 plantes/m2 pour le mil, le sorgho et l'arachide."),

                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Fertilizer Application
                    dbc.Label("13) Application d'engrais N", html_for="fert_input", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="fert_input",          # la fertilisation
                        options=[
                          {"label": "Engrais", "value": "Fert"},
                          {"label": "Pas d'engrais", "value": "No_fert"},
                        ],
                        labelStyle = {"display": "inline-block","marginRight": 10},
                        value="No_fert",
                      ),
                      html.Div([ # FERTILIZER INPUT TABLE
                        dbc.Row(
                        dbc.FormText("1ere Application d'engrais",color="green",className="text-center"),
                               ),  
                        dbc.Row([
                            
                            dbc.Col(
                                dbc.Label("Type de Fertilisation", className="text-center")
                            ),
                            dbc.Col(
                                dbc.Label("Quantite (kg/ha)", className="text-center", ),
                            ),
                            dbc.Col(
                                dbc.Label("Formule d'engrais ", className="text-center", ),
                            ),
                            
                                ]),
                        dbc.Row([
                          dbc.Col(
                           dcc.Dropdown(
                              id="typ_fert1",
                              options=[
                               {"label":"NPK", "value":"NPK"},
                               {"label":"Uree","value":"Uree"},
                               {"label":"DAP","value":"DAP"},
                            ],
                         value="NPK",
                          clearable=False
                        )   
                          ),
                          dbc.Col(
                              dcc.Dropdown(
                        id="Q_1",
                        options=[
                          {"label": "50", "value":   50}, # choix des valeurs
                          {"label": "100", "value": 100},  # essayons avec input mais en changeant les entrees
                          {"label": "150", "value": 150},
                          {"label": "200", "value": 200},
                      #  dbc.Input(type="number", id="Q_1", required="required", ),  
                                ],    
                          value=50,
                          clearable=False,
                      
                       ),
                          ),

                        dbc.Col(
                        dcc.Dropdown(
                        id="Form_ang1",          
                        options=[
                          {"label": "15-15-15", "value": "15-15-15"}, # formule d'angrais
                          {"label": "15-10-10", "value": "15-10-10"},
                          {"label": "6-10-20", "value": "6-10-20"},
                          {"label": "46-0-0", "value": "46-0-0"},
                          {"label": "18-46-0", "value": "18-46-0"},
                          
                         
                        ],
#                        value="15-15-15",
                        clearable=False,
                            )    

                        )  
                               
                        ]) , 
                          dbc.Row(""),   
                        dbc.Row([
                           dbc.Col(""),
                          dbc.Col(
                           dbc.Label(" N(Kg/ha)", className="text-center", ),
                          
                          ),
                          dbc.Col(
                            dbc.Label(" P(Kg/ha)", className="text-center", ),
                             
                          ),
                          dbc.Col(
                            dbc.Label(" K(Kg/ha)", className="text-center", ),
                          ),
                        ],),
                        
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Jours après semis", className="text-center" ),
                          ), 
                                                             
                          dbc.Col(                      
                            dbc.FormGroup([
                             html.Div(id="N_1", className="text-center")
                            ],),                         
                          ),
                          dbc.Col(
                            dbc.FormGroup([               
                              html.Div(id="P_1", className="text-center")
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                            html.Div(id="K_1", className="text-center")
                            ],),
                          ),
                        ],),
                        
                        dbc.Row([
                            dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day1", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                            
                           dbc.Col( 
                               dbc.FormGroup([
                            dbc.Input(type="number", id="N-amt1", value=0, min="0", step="0.1", required="required", ),
                                             ],), 
                                     ),
                          dbc.Col(
                               dbc.FormGroup([      
                            dbc.Input(type="number", id="P-amt1", value=0, min="0", step="0.1", required="required", ),
                                            ],),
                                 ),
                          dbc.Col(
                              dbc.FormGroup([ 
                            dbc.Input(type="number", id="K-amt1", value=0, min="0", step="0.1", required="required", ), 
                                            ],),                                
                                 ),
                              ], ),
                              dbc.Row(
                        dbc.FormText(" NB: Vous devez remplir le jour de semis et saisir les nombres ci-dessus sur ces cases. " ),
                               ),
# pour Ajouter 
                     dbc.Row("--------------------------------------------------------------------------"),
                      dbc.Row(
                    dcc.RadioItems(
                        id="ajout1",          # la fertilisation
                        options=[
                          {"label": "Ajouter", "value": "ajout_1"},
                          {"label": "Non", "value": "No_ajout_1"},
                        ],
                        labelStyle = {"display": "inline-block","marginRight": 10},
                        value="No_ajout_1",
                      ),
                             ),
                    html.Div([
                      dbc.Row([
                          
                            
                          
                            dbc.Col(
                                dbc.Label("Type de Fertilisation", className="text-center")
                            ),
                            dbc.Col(
                                dbc.Label("Quantite (Kg/ha)", className="text-center" ),
                            ),
                            dbc.Col(
                                dbc.Label("Formule d'engrais ", className="text-center" ),
                            ),
                            
                               
                      ]),

                  dbc.Row([
                          
                          dbc.Col(""),

                          dbc.Col(
                           dcc.Dropdown(
                              id="typ_fert2",
                              options=[
                               {"label":"NPK", "value":"NPK"},
                               {"label":"Uree","value":"Uree"},
                               {"label":"DAP","value":"DAP"},
                               {"label":"Sans Fertilisation","value":"Sans_fertilisation"}
                            ],
                         value="Sans fertilisation",
                          clearable=False
                                        )   
                                  ),
                            dbc.Col(
                              dcc.Dropdown(
                        id="Q_2",
                        options=[
                          {"label": "50", "value":   50}, # choix des valeurs
                          {"label": "100", "value": 100},  # essayons avec input mais en changeant les entrees
                          {"label": "150", "value": 150},
                          {"label": "200", "value": 200},
                          
                          
                        ],
                        value=0,
                        clearable=False,
                      
                                          ),
                                     ),
                           dbc.Col(
                        dcc.Dropdown(
                        id="Form_ang2",          
                        options=[
                          {"label": "15-15-15", "value": "15-15-15"}, # formule d'angrais
                          {"label": "15-10-10", "value": "15-10-10"},
                          {"label": "6-10-20", "value": "6-10-20"},
                          {"label": "46-0-0", "value": "46-0-0"},
                          {"label": "18-46-0", "value": "18-46-0"},
                          
                         
                        ],
                         value="Pas d'angrais",
                        clearable=False,
                                      )    

                                    ) 

                          ] ),
                      dbc.Row([
                           dbc.Col(""),
                          dbc.Col(
                           dbc.Label(" N(Kg/ha)", className="text-center", ),
                          
                          ),
                          dbc.Col(
                            dbc.Label(" P(Kg/ha)", className="text-center", ),
                             
                          ),
                          dbc.Col(
                            dbc.Label(" K(Kg/ha)", className="text-center", ),
                          ),
                        ],),

                      dbc.Row([
                         dbc.Col(
                            dbc.Label("Jours après semis", className="text-center", ),
                          ),
                      
                      dbc.Col( html.Div(id="N_2"),className="text-center"),
                      dbc.Col( html.Div(id="P_2"),className="text-center"),
                      dbc.Col( html.Div(id="K_2"),className="text-center"),
                            ] ),
                       dbc.Row([ 
                          dbc.Col(
                     dbc.Input(type="number", id="fert-day2", value=0, min="0", max="365", required="required" )
                      ), 

                          dbc.Col(
                              dbc.FormGroup([
                                dbc.Input(type="number", id="N-amt2", value=0, min="0", step="0.1", required="required", ),
                                           ],),      
                                 ),
                          dbc.Col( 
                                 dbc.FormGroup([
                                dbc.Input(type="number", id="P-amt2", value=0, min="0", step="0.1", required="required", ),
                                              ],),
                                 ), 
                          dbc.Col( 
                               dbc.FormGroup([
                                dbc.Input(type="number", id="K-amt2", value=0, min="0", step="0.1", required="required", ), 
                                            ],),
                                 ), 
                              ], ),
                       dbc.Row(
                        dbc.FormText(" NB: Vous devez remplir le jour de semis et saisir les nombres ci-dessus sur ces cases. " ),
                               ),
                     dbc.Row("--------------------------------------------------------------------------"), 

                      ],id="aff_1" ,
                      style={"display":"none"}
                      
                      ),          
#
                        dbc.Row(
                        dbc.FormText(" Application d'engrais",color="green",className="text-center"),
                               ),

                        dbc.Row([
                            dbc.Col(
                                dbc.Label("Type de Fertilisation", className="text-center")
                            ),
                            dbc.Col(
                                dbc.Label("Quantite (kg/ha)", className="text-center", ),
                            ),
                            dbc.Col(
                                dbc.Label("Formule d'engrais ", className="text-center", ),
                            ),
                            
                                ]),

                        dbc.Row([
                          dbc.Col(
                           dcc.Dropdown(
                              id="typ_fert3",
                              options=[
                               {"label":"NPK", "value":"NPK"},
                               {"label":"Uree","value":"Uree"},
                               {"label":"DAP","value":"DAP"},
                               {"label":"Sans Fertilisation","value":"Sans_fertilisation"}
                            ],
                         value="Sans fertilisation",
                          clearable=False
                        )   
                          ),
                          dbc.Col(
                              dcc.Dropdown(
                        id="Q_3",
                        options=[
                          {"label": "50", "value":   50}, # choix des valeurs
                          {"label": "100", "value": 100},  # essayons avec input mais en changeant les entrees
                          {"label": "150", "value": 150},
                          {"label": "200", "value": 200},
                          
                          
                        ],
                        value=50,
                        clearable=False,
                      
                       ),
                          ),

                        dbc.Col(
                        dcc.Dropdown(
                        id="Form_ang3",          
                        options=[
                          {"label": "15-15-15", "value": "15-15-15"}, # formule d'angrais
                          {"label": "15-10-10", "value": "15-10-10"},
                          {"label": "6-10-20", "value": "6-10-20"},
                          {"label": "46-0-0", "value": "46-0-0"},
                          {"label": "18-46-0", "value": "18-46-0"},
                          
                         
                        ],
                         value="Pas d'angrais",
                        clearable=False,
                            )    

                        )  
                               
                        ]) ,

                        dbc.Row([
                          dbc.Col(""),
                          dbc.Col(
                           dbc.Label(" N(Kg/ha)", className="text-center", ),
                          
                          ),
                          dbc.Col(
                            dbc.Label(" P(Kg/ha)", className="text-center", ),
                             
                          ),
                          dbc.Col(
                            dbc.Label(" K(Kg/ha)", className="text-center", ),
                          ),
                        ],),

                        dbc.Row([
                          
                         dbc.Col(
                            dbc.Label("Jours après semis", className="text-center", ),
                          ),                         
                          
                          dbc.Col(
                            dbc.FormGroup([
                            html.Div(id="N_3", className="text-center")
                            ],),
                        
                          ),
                        
                          dbc.Col(
                            dbc.FormGroup([                          
                           html.Div(id="P_3", className="text-center")
                            ],),
                          ),
                        dbc.Col(
                            dbc.FormGroup([
                            html.Div(id="K_3", className="text-center") 
                            ],),
                          ), 

                        ],), 
                        dbc.Row([ 
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day3", value=0, min="0", max="365", required="required", ),
                           
                            ],),
                          ),  

                          dbc.Col( 
                              dbc.FormGroup([
                          dbc.Input(type="number", id="N-amt3", value=0, min="0", step="0.1", required="required", ),
                                          ],),
                                 ),
                          dbc.Col( 
                              dbc.FormGroup([
                                dbc.Input(type="number", id="P-amt3", value=0, min="0", step="0.1", required="required", ),
                                           ],),
                                 ), 
                          dbc.Col( 
                              dbc.FormGroup([
                                dbc.Input(type="number", id="K-amt3", value=0, min="0", step="0.1", required="required", ), 
                                          ],),
                                 ), 
                               ], ),
                               dbc.Row(
                        dbc.FormText(" NB: Vous devez remplir le jour de semis et saisir les nombres ci-dessus sur ces cases. " ),
                               ),
                     dbc.Row("--------------------------------------------------------------------------"),
                      
                         
                       

                        
                        dbc.Row( [     
                          dbc.Col( 
                              dbc.FormGroup([
                            #    dbc.Input(type="number", id="N-amt4", value=0, min="0", step="0.1", required="required", ),
                                           ],),
                                 ),
                          dbc.Col( 
                              dbc.FormGroup([
                            #    dbc.Input(type="number", id="P-amt4", value=0, min="0", step="0.1", required="required", ),
                                           ],),
                                 ), 
                          dbc.Col(
                              dbc.FormGroup([ 
                            #    dbc.Input(type="number", id="K-amt4", value=0, min="0", step="0.1", required="required", ), 
                                      ],),
                                 ), 
                              ] ,),
                       
                       ],
                      id="fert-table-Comp", 
                      className="w-100",
                      style={"display": "none"},
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Phosphorous simualtion
                    dbc.Label("14) Simulation du phosphore ? [arachide seulement]", html_for="P_input", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="P_input",
                        options=[
                          {"label": "Oui", "value": "P_yes"},
                          {"label": "Non", "value": "P_no"},
                        ],
                        labelStyle = {"display": "inline-block","marginRight": 10},
                        value="P_no",
                      ),
                      html.Div([
                        dbc.Label("Niveau de phosphore extractible du sol", html_for="extr_P", align="start", ),
                        dcc.Dropdown(
                          id="extr_P",
                          options=[
                            {"label": "Tés lent (2 ppm)", "value": "VL"},
                            {"label": "Lent (7 ppm)", "value": "L"},
                            {"label": "Moyen (12 ppm)", "value": "M"},
                            {"label": "Elevé (18 ppm)", "value": "H"},
                          ],
                          value="L",
                          clearable=False,
                        ),
                      ],
                      id="P-sim-Comp",
                      className="w-100",
                      style={"display": "none"},
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Irrigation
                    dbc.Label("15) Irrigation", html_for="irrig_input", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="irrig_input",
                        options=[
                          {"label": " Pas d'irrigation", "value": "No_irrig"},
                          {"label": " Aux dates déclarées", "value": "repr_irrig"},
                          {"label": " Automatique lorsque nécessaire", "value": "auto_irrig"}
                        ],
                        labelStyle = {"display": "block","marginRight": 10},
                        value="No_irrig",
                      ),
                      html.Div([
                        html.Div([ # "on reported dates"
                          #irrigation method
                          dbc.Label("Méthode d'irrigation ", html_for="extr_P", align="start", ),
                          dcc.Dropdown(
                            id="ir_method",
                            options=[
                              {"label": "asperseur", "value": "IR004"},
                              {"label": "irrigation goutte à goutte", "value": "IR005"},  #IR005    Drip or trickle, mm   
                              {"label": "sillon", "value": "IR001"},
                              {"label": "inondation", "value": "IR001"},
                            ],
                            value="IR004",
                            clearable=False,
                          ),
                          html.Div([
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("No.", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.Label("Jours après semis", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.Label("Quantité d'eau [mm]", className="text-center", ),
                              ),
                            ],
                            className="py-3",
                            ),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("1er", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day1", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt1", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label(" 2ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day2", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt2", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("3ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day3", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt3", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("4ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day4", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt4", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("5ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day5", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt5", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                          ],),
                        ],
                        id="irrig-table-Comp",
                        className="w-100",
                        style={"display": "none"},
                        ),
                        html.Div([ # "Automatic when required"
                          dbc.Row([  #irrigation depth
                            dbc.Col(
                              dbc.Label("Gestion de la profondeur du sol", html_for="ir_depth", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_depth", value=30, min=1, max=100, step=0.1, required="required", ),
                              dbc.FormText("[cm]"),
                            ],),
                          ],
                          className="py-2",
                          ),
                          dbc.Row([  #irrigation threshold
                            dbc.Col(
                              dbc.Label("Seuil", html_for="ir_threshold", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_threshold", value=50, min=1, max=100, step=0.1, required="required", ),
                              dbc.FormText("(% de l'eau maximale disponible déclenchant l'irrigation)"),
                            ],),
                          ],
                          className="py-2",
                          ),
                          dbc.Row([  #efficiency fraction
                            dbc.Col(
                              dbc.Label("Fraction d'efficience de l'irrigation", html_for="ir_eff", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_eff", value=0.9, min=0.1, max=1, step=0.1, required="required", ),
                              dbc.FormText("[0 ~ 1]"),
                            ],),
                          ],
                          className="py-2",
                          ),
                        ],
                        id="autoirrig-table-Comp",
                        className="w-100",
                        style={"display": "none"},
                        ),
                      ]),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Enterprise Budgeting?
                    dbc.Label("16) Budgétisation de la Campagne?", html_for="EB_radio", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="EB_radio",
                        options=[
                          {"label": "Oui", "value": "EB_Yes"},
                          {"label": "Non", "value": "EB_No"},
                        ],
                        labelStyle = {"display": "inline-block","marginRight": 10},
                        value="EB_No",
                      ),
                      html.Div([ # ENTERPRISE BUDGETING FORM
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("prix de récolte attendu", html_for="crop-price", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="crop-price", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/kg]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Coût de l'engrais", html_for="fert-cost", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-cost", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/N kg]"),
                              # dbc.FormText("If you pay X CFA for 1 bag of 50kg fertilizer (N:P:K = 6:20:10 for peanut), your fertilizer cost = X*100/(6*50) [CFA/N kg]"),
                              dbc.FormText("Si vous payez X FCFA pour 1 sac d'engrais de 50 kg (N:P:K = 6:20:10 pour l'arachide), votre coût d'engrais = X*100/(6*50) [CFA/N kg]."),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Coût des semences", html_for="seed-cost", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="seed-cost", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/ha]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Coût de l'irrigation", html_for="irrigation-cost", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="irrigation-cost", value=0, min=0, step=0.1, ),#required="required", ),
                              dbc.FormText("[CFA/mm]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Autres coûts variables", html_for="variable-costs", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="variable-costs", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/ha]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("FCoûts fixes", html_for="fixed-costs", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fixed-costs", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/ha]"),
                            ],),
                          ),
                        ],),
                        # Tutorial link here is hardcoded
                        dbc.FormText(
                          html.Span([
                            "Voir le  ",
                            # html.A("manuel", target="_blank", href="https://sites.google.com/iri.columbia.edu/simagri-senegal/simagri-tutorial"),
                            html.A("manuel", target="_blank", href="https://sites.google.com/iri.columbia.edu/simagri-french/simagri-tutorial"),
                            " pour plus de détails sur les calculs."
                          ])
                        ),
                      ],
                      id="EB-table-Comp",
                      className="w-100",
                      style={"display": "none"},
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                ],
                className="p-3"
                ),
              className="overflow-auto",
              style={"height": "63vh"},
              ),
              html.Header(html.B("Scénarios"), className="card-header",),
              dbc.FormGroup([ # SUBMIT - ADD SCENARIO
                dbc.Button(id="write-button-state",
                n_clicks=0,
                children="Créer ou ajouter un nouveau scénario",
                className="w-75 d-block mx-auto my-3",
                color="primary"
                ),
              ]),
            ]),
            # FORM END

            html.Div([
              html.Div([ # SCENARIO TABLE
                dash_table.DataTable(
                id="scenario-table",
                columns=([
                    {"id": "sce_name", "name": "Nom du scénario" }, #Scenario Name"},
                    {"id": "Crop", "name": "Culture"}, # Crop"},
                    {"id": "Cultivar", "name": "Cultivar"},
                    {"id": "stn_name", "name": "Station"},
                    {"id": "PltDate", "name": "Date de semis"}, # Planting Date"},
                    {"id": "FirstYear", "name": "Première année"}, # First Year"},
                    {"id": "LastYear", "name": "l'année dernière" }, # Last Year"},
                    {"id": "soil", "name": "Type de sol"}, #   Soil Type"},
                    {"id": "iH2O", "name": "Initial H2O"}, #"Initial Soil Water Content"},
                    {"id": "iNO3", "name": "Initial NO3"}, #"Initial Soil Nitrate Content"},
                    {"id": "plt_density", "name": "Densité de semis"}, #  Planting Density"},
                    {"id": "TargetYr", "name": "année cible"}, # Target Yr"},
                    {"id": "Fert_1_DOY", "name": "FDOY(1)"},
                    {"id": "N_1_Kg", "name": "N(Kg/ha)(1)"},
                    {"id": "P_1_Kg", "name": "P(Kg/ha)(1)"},
                    {"id": "K_1_Kg", "name": "K(Kg/ha)(1)"},
                    {"id": "Fert_2_DOY", "name": "FDOY(2)"},
                    {"id": "N_2_Kg", "name": "N(Kg/ha)(2)"},
                    {"id": "P_2_Kg", "name": "P(Kg/ha)(2)"},
                    {"id": "K_2_Kg", "name": "K(Kg/ha)(2)"},
                    {"id": "Fert_3_DOY", "name": "FDOY(3)"},
                    {"id": "N_3_Kg", "name": "N(Kg/ha)(3)"},
                    {"id": "P_3_Kg", "name": "P(Kg/ha)(3)"},
                    {"id": "K_3_Kg", "name": "K(Kg/ha)(3)"},
                  #  {"id": "Fert_4_DOY", "name": "FDOY(4)"},
                  #  {"id": "N_4_Kg", "name": "N(Kg/ha)(4)"},
                  #  {"id": "P_4_Kg", "name": "P(Kg/ha)(4)"},
                  #  {"id": "K_4_Kg", "name": "K(Kg/ha)(4)"},
                    {"id": "P_level", "name": "P extractible"}, # Extractable P"},
                    {"id": "IR_method", "name": "Méthode d'irrigation" }, # Irrigation Method"},
                    {"id": "IR_1_DOY", "name": "IDOY(1)"},
                    {"id": "IR_1_amt", "name": "IR(mm)(1)"},
                    {"id": "IR_2_DOY", "name": "IDOY(2)"},
                    {"id": "IR_2_amt", "name": "IR(mm)(2)"},
                    {"id": "IR_3_DOY", "name": "IDOY(3)"},
                    {"id": "IR_3_amt", "name": "IR(mm)(3)"},
                    {"id": "IR_4_DOY", "name": "IDOY(4)"},
                    {"id": "IR_4_amt", "name": "IR(mm)(4)"},
                    {"id": "IR_5_DOY", "name": "IDOY(5)"},
                    {"id": "IR_5_amt", "name": "IR(mm)(5)"},
                    {"id": "AutoIR_depth", "name": "AutoIR_depth"},
                    {"id": "AutoIR_thres", "name": "AutoIR_thres"},
                    {"id": "AutoIR_eff", "name": "AutoIR_eff"},
                    {"id": "CropPrice", "name": "Coût de la culture à la récolte" }, #Crop Price"},
                    {"id": "NFertCost", "name": "Coût de l'engrais"}, # Fertilizer Cost"},
                    {"id": "SeedCost", "name": "Coût des semences"}, # Seed Cost"},
                    {"id": "IrrigCost", "name": "Coût de l'irrigation"}, # Irrigation Cost"},
                    {"id": "OtherVariableCosts", "name": "Autres coûts variables"}, # Other Variable Costs"},
                    {"id": "FixedCosts", "name": "Coûts fixes" }, #Fixed Costs"},
                ]),
                data=[
              #      dict(**{param: "N/A" for param in sce_col_names}) for i in range(1, 2)
                   # list("N/A" for param in sublist) for i in range(1, 2) for sublist in sce_col_names
                ],
                style_table = {
                    "overflowX": "auto",
                    "minWidth": "100%",
                },
                fixed_columns = { "headers": True, "data": 1 },
                style_cell = {   # all three widths are needed
                    "minWidth": "120px", "width": "120px", "maxWidth": "150px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                },
                row_deletable=True
                ),
              ]),
              html.Div([
                dbc.Row([ # IMPORT/DOWNLOAD SCENARIOS
                  dbc.Col(
                    dcc.Upload([
                      html.Div([
                        html.Div(html.B("Importer des scénarios ")),
                        "Glisser-déposer ou ",
                        dcc.Link("sélectionner un fichier", href="", )
                      ],
                      className="d-block mx-auto text-center p-2"
                      )
                    ],
                    id="import-sce",
                    className="w-75 d-block mx-auto m-3",
                    style={
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "background-color": "lightgray"
                    },
                    ),
                  ),
                  dbc.Col([
                    dbc.Button(
                      "Télécharger des scénarios",
                    id="download-btn-sce",
                    n_clicks=0,
                    className="w-75 h-50 d-block mx-auto m-4",
                    color="secondary"
                    ),
                    dcc.Download(id="download-sce")
                  ],),
                ],
                className="mx-3",
                no_gutters=True
                ),
                html.Div( # IMPORT/DOWNLOAD ERROR MESSAGES
                  dbc.Row([
                    dbc.Col(
                      html.Div("",
                      id="import-sce-error",
                      style={"display": "none"},
                      ),
                    ),
                    dbc.Col([
                      html.Div(
                        html.Div("Nothing to Download",
                        className="d-block mx-auto m-2",
                        style={"color": "red"},
                        ),
                      id="download-sce-error",
                      style={"display": "none"},
                      ),
                    ]),
                  ]),
                className="text-center mx-3",
                ),
              ]),
            ]),

            html.Div([ # AFTER SCENARIO TABLE
              dbc.FormGroup([ # Approximate Growing Season
                dbc.Label("17) Période de croissance critique pour relier la quantité de pluie au rendement des cultures", html_for="season-slider"),
                dbc.FormText("La période sélectionnée est utilisée pour trier les années plus sèches/plus humides sur la base des précipitations totales saisonnières."),
                dcc.RangeSlider(
                  id="season-slider",
                  min=1, max=12, step=1,
                  marks={1: "janv.", 2: "fév",3: "mars", 4: "avr", 5: "mai", 6: "juin", 7: "juil", 8: "août", 9: "sept.", 10: "oct.", 11: "nov.", 12: "déc."},
                  value=[6, 9]
                ),
              ],
              ),
              html.Br(),
              html.Div( ## RUN DSSAT BUTTON
                dbc.Button(id="simulate-button-state",
                children="Simuler tous les scénarios (Exécuter DSSAT)",
                className="w-75 d-block mx-auto",
                color="success",
                ),
              )
            ],
            className="p-3",
            ),

          ],
          ),
        className="block card",
        ),
      ],
      md=5,
      className="p-1",
      ),
                                                                    
  dbc.Col([ ## RIGHT HAND SIDE -- CARDS WITH SIMULATION ETC
  
# dcc.Graph(figure=html.Iframe(srcDoc=a.get_root().render(), width="30%", height="30")), #   # Affichage de la cate

        html.Div([
         #   dbc.Label(" on va mettre la carte ici pour le tester"),
          html.Div( # SIMULATIONS
            html.Div([
              html.Header(
                html.B("Graphiques de simulation (historique)"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div(
                    dbc.Spinner(children=[
                      html.Div([
                        html.Div(id="yieldbox-container"),
                        html.Div(id="yieldcdf-container"),  #exceedance curve
                        html.Div(id="yieldtimeseries-container"),  #time-series
                        dbc.Row([
                          dbc.Col(
                            html.Div(id="yield-BN-container"),
                          md=4),
                          dbc.Col(
                            html.Div(id="yield-NN-container"),
                          md=4),
                          dbc.Col(
                            html.Div(id="yield-AN-container"),
                          md=4),
                        ],
                        no_gutters=True,
                        ),
                      ],),
                    ],
                    size="lg", color="primary", type="border",
                    ),
                  )
                ],
                id="simulation-graphs",
                className="overflow-auto",
                style={"height": "94vh"},
                ),
              ),
            ],
            ),
          ),

          # CSV FOR SIMULATED YIELD
          html.Div( # ORIGINAL CSV
            html.Div([
              html.Header(
                html.B("Télécharger le rendement simulé en format CSV"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div([
                    html.Div([ # ORIGINAL CSV STUFF
                      dbc.Row([
                        dbc.Col(
                          dbc.Button(id="btn_csv_yield",
                          children="Rendement simulé ",
                          className="d-block mx-auto",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                        dbc.Col(
                          dbc.Button(id="btn_csv_Pexe",
                          children="Probabilité de dépassement",
                          className="d-block mx-auto",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                        dbc.Col(
                          dbc.Button(id="btn_csv_rain",
                          children="Pluies saisonnières",
                          className="d-block mx-auto",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                      ],
                      className="m-3",
                      ),
                      # dcc.Download(id="download-dataframe-csv"),
                      Download(id="download-dataframe-csv-yield"),
                      Download(id="download-dataframe-csv-rain"),
                      Download(id="download-dataframe-csv-Pexe"),
                      html.Div(
                        dash_table.DataTable(
                          columns = [{"id": "YEAR", "name": "YEAR"}],
                          id="yield-table",
                          style_table = {"height": "10vh"},
                        ),
                      id="yieldtables-container",
                      ),  #yield simulated output
                    ], ),
                  ],
                  ),
                ],
                id="original-yield-csv-table",
                className="dash-table-container"
                ),
              ),
            ],
            ),
          ),

          html.Div( # ENTERPRISE BUDGETING
            html.Div([
              html.Header(
                html.B("Budgétisation de la campagnie"),
              className=" card-header",
              ),
              html.Div([
                dbc.Form([ # EB FIGURES
                  dbc.FormGroup([ # Enterprise Budgeting Yield Adjustment Factor
                    dbc.Label("Facteur d'ajustement du rendement de la budgétisation d'entreprise", html_for="yield-multiplier", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="yield-multiplier", value=1, min=0, max=2, step=0.1, required="required", ),
                      dbc.FormText("Entrez un multiplicateur pour tenir compte d'une marge d'erreur."),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.Button(id="EB-button-state",
                  children="Afficher les figures pour les budgets d'entreprise",
                  className="w-75 d-block mx-auto my-3",
                  color="danger"
                  ),
                ],
                className="p-3",
                ),

                html.Div([
                  html.Div(
                    html.Div([
                      html.Div(id="EBbox-container"),
                      html.Div(id="EBcdf-container"),  #exceedance curve
                      html.Div(id="EBtimeseries-container"), #exceedance curve

                    ],
                    className="plot-container plotly"),
                  className="js-plotly-plot"
                  )
                ],
                id="enterprise-budgeting",
                className="overflow-auto",
                style={"height": "94vh"},
                ),
              ]),
              html.Div([
                html.Header(
                  html.B("Télécharger budgétisation de la campagnie en format CSV"),
                className=" card-header"
                ),
                html.Div([
                  html.Br(),
                  dbc.Button(id="btn_csv_EB",
                  children="Télécharger",
                  className="w-50 d-block mx-auto m-1",
                  color="secondary"
                  ),
                  # dcc.Download(id="download-dataframe-csv"),
                  Download(id="download-dataframe-csv_EB"),
                  html.Div(id="EBtables-container",
                  className="overflow-auto",
                  style={"height": "20vh"},
                  ),   #yield simulated output
                ]),
              ]),
            ],
            id="EB-figures",
            style={"display": "none"},
            ),
          ),
        ],
        className="block card"
        ),
      ],
      md=7,
      className="p-1",
      ),
    ],
    className="m-1"
    ),
])

# is this needed?
DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()
DSSAT_FILES_DIR_SHORT = "/DSSAT/dssat-base-files"  #for linux systemn
DSSAT_FILES_DIR = os.getcwd() + DSSAT_FILES_DIR_SHORT   #for linux systemn

#https://community.plotly.com/t/loading-when-opening-localhost/7284
#I suspect that this is related to the JS assets from the CDN not loading properly - perhaps because they are blocked by your firewall or some other reason.
#You can load the assets locally by setting:
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

cultivar_options = {
    "PN": ["IB0090 VAR_FLEUR_11","IB0091 VAR_73-33"],
    "ML": ["IB0044 CIVT"],
    # "MZ": ["CIMT01 BH540","CIMT02 MELKASA-1","CIMT17 BH660-FAW-40%", "CIMT19 MELKASA2-FAW-40%", "CIMT21 MELKASA-LowY"],
    # "WH": ["CI2021 KT-KUB", "CI2022 RMSI", "CI2023 Meda wolabu", "CI2024 Sofumer", "CI2025 Hollandi", "CI2018 ET-MED", "CI2019 ET-LNG"],
    "SG": ["IB0066 Fadda-D","IB0069 IS15401-D","IB0070 Soumba-D","IB0071 Faourou-D"]
}
soil_options = {
    "PN": ["CNCNioro14(S)","CNCNNior15(SL)", "CNBambey14(LS)", #from Adama
          "CNNior14_S(S)", "CNNior15_S(SL)", "CNBamb14_S(LS)", #from Adama-SRGF adjusted],
          "SN00840067(SL)", "SN00840080(SL)", "SN00840042(SL)", "SN00840056(SL)"],
    "ML": ["CNCNioro14(S)","CNCNNior15(SL)", "CNBambey14(LS)", #from Adama
          "CNNior14_S(S)", "CNNior15_S(SL)", "CNBamb14_S(LS)", #from Adama-SRGF adjusted],
          "SN00840067(SL)", "SN00840080(SL)", "SN00840042(SL)", "SN00840056(SL)"],
    "SG": ["SN-N15Rain(S)", "SN-N15Irrg(S)", "SN-N16Rain(S)", "SN-N16Irrg(S)", "SN-S15Rain(LS)","SN-S16Rain(LS)",#from Ganyo(2019) sorghum
          "SN00840067(SL)", "SN00840080(SL)", "SN00840042(SL)", "SN00840056(SL)"]
}
type_angrais = {
    "NPK": ["15-15-15","15-10-10", "6-10-20"],
    "Uree":["46-0-0"],
    "DAP":["18-46-0"],
    "Sans_fertilisation":["0-0-0"]
}
#Q_1 = 50 or 100 or 150 or 200,

Wdir_path = DSSAT_FILES_DIR    #for linux systemn

#==============================================================
# Choix du type de fertilisation 1
@app.callback(
        Output("Form_ang1","options"),
        Input("typ_fert1","value")
)
def set_type_ang1(ang1_choisi):
    return [{"label": i,"value":i} for i in type_angrais[ang1_choisi]]

@app.callback(
        Output("Form_ang1","value"),
        Input("Form_ang1", "options")
        
)
def set_Form_ang1(option1_valide):
    return option1_valide[0]["value"]
#---------------------------------------------------
# Choix du type de fertilisation 
@app.callback(
        Output("Form_ang3","options"),
        Input("typ_fert3","value")
)
def set_type_ang3(ang3_choisi):
    return [{"label": i,"value":i} for i in type_angrais[ang3_choisi]]

@app.callback(
        Output("Form_ang3","value"),
        Input("Form_ang3", "options")
)
def set_Form_ang3(option3_valide):
    return option3_valide[0]["value"]

# Remplissage de N P et K automatiquement en fonction du type d'engrais choisi
# Reccuperer les deux valeurs (quantite x %N, .........)

#--------------- 1ere Application ----------------------------------

#----------- Remplissage de N_1------------------------------------
@app.callback(                       # Recuperer la quantite d'angrais
        Output("N_1", "children"),      
        [Input("Q_1","value"),
         Input("Form_ang1","value")
        ],
)

def quantite_N1(Q_1 ,Form_ang1):   
   if Form_ang1 == "15-15-15":
       N_1= Q_1 * 0.15
   elif Form_ang1 == "15-10-10":
       N_1= Q_1 * 0.15
   elif Form_ang1 == "6-10-20":
        N_1= Q_1 * 0.06
   elif Form_ang1 == "46-0-0":
       N_1= Q_1 * 0.46
   elif Form_ang1 == "18-46-0":
       N_1=Q_1 * 0.18
   else :
       N_1= "Entrer les valeurs"
   return N_1     
#------------Remlissage de P_1_Kg---------------------------------
@app.callback(                   
        Output("P_1", "children"),      
        [Input("Q_1","value"),
         Input("Form_ang1","value")
        ],
  
)
def quantite_P1(Q_1 ,Form_ang1 ):
    if Form_ang1 == "15-15-15":
        P_1= Q_1 * 0.15
    elif Form_ang1 == "15-10-10":
        P_1= Q_1 * 0.10
    elif Form_ang1 == "6-10-20":
        P_1= Q_1 * 0.10
    elif Form_ang1 == "46-0-0":
        P_1= Q_1 * 0
    elif Form_ang1 == "18-46-0":
        P_1= Q_1 * 0.46
    else :
        P_1="Entrer les valeurs"
    return P_1     
#---------------- Remplissage de K_1_Kg--------------------------
@app.callback(                    
        Output("K_1", "children"),       
        [Input("Q_1","value"),
         Input("Form_ang1","value")
        ],
    
)
def quantite_K1(Q_1 ,Form_ang1 ):
    if Form_ang1 == "15-15-15":
        K_1= Q_1 * 0.15
    elif Form_ang1 == "15-10-10":
        K_1= Q_1 * 0.10
    elif Form_ang1 == "6-10-20":
        K_1= Q_1 * 0.20
    elif Form_ang1 == "46-0-0":
        K_1= Q_1 * 0
    elif Form_ang1 == "18-46-0":
        K_1= Q_1 * 0
    else :
        K_1="Entrer les valeurs"
    return K_1    

# Pour le premier Ajout
#@app.callback(
#       Output('a_afficher_1',"children"),
#       [Input('a_ajout_1','n_clicks')],
#       prevent_initial_call=True

#)

#def afficher_choix(n_clicks):
#    if n_clicks >0:
#        return "a_afficher_1"
#    else:
#        return []

#--------- 2eme Application -----------------------------
# -----------Remplissage N_2------------------
@app.callback(
      Output("N_2","children"),
      [Input("Q_2","value"),
         Input("Form_ang2","value")
        ]
)
def quantite_N2(Q_2 ,Form_ang2):   
   if Form_ang2 == "15-15-15":
       N_2= Q_2 * 0.15
   elif Form_ang2 == "15-10-10":
       N_2= Q_2 * 0.15
   elif Form_ang2 == "6-10-20":
        N_2= Q_2 * 0.06
   elif Form_ang2 == "46-0-0":
       N_2= Q_2 * 0.46
   elif Form_ang2 == "18-46-0":
       N_2=Q_2 * 0.18
   elif Form_ang2 == "0-0-0":
       N_2=Q_2 * 0
   else :
       N_2= "Entrer les valeurs"
   return N_2

# ---------- Remplissage de P_2_Kg---------------
@app.callback(                      
        Output("P_2", "children"),      
        [Input("Q_2","value"),
         Input("Form_ang2","value")
        ],
)

def quantite_P2(Q_2 ,Form_ang2):   
   if Form_ang2 == "15-15-15":
       P_2= Q_2 * 0.15
   elif Form_ang2 == "15-10-10":
       P_2= Q_2 * 0.1
   elif Form_ang2 == "6-10-20":
        P_2= Q_2 * 0.1
   elif Form_ang2 == "46-0-0":
       P_2= Q_2 * 0
   elif Form_ang2 == "18-46-0":
       P_2=Q_2 * 0.46
   elif Form_ang2 == "0-0-0":
       P_2=Q_2 * 0
   else :
       P_2= "Entrer les valeurs"
   return P_2

#---------- Remplissage K_2_Kg------------------
@app.callback(                      
        Output("K_2", "children"),      
        [Input("Q_2","value"),
         Input("Form_ang2","value")
        ],
)

def quantite_K2(Q_2 ,Form_ang2):   
   if Form_ang2 == "15-15-15":
       K_2= Q_2 * 0.15
   elif Form_ang2 == "15-10-10":
       K_2= Q_2 * 0.1
   elif Form_ang2 == "6-10-20":
        K_2= Q_2 * 0.2
   elif Form_ang2 == "46-0-0":
       K_2= Q_2 * 0
   elif Form_ang2 == "18-46-0":
       K_2=Q_2 * 0
   elif Form_ang2 == "0-0-0":
       K_2=Q_2 * 0
   else :
       K_2= "Entrer les valeurs"
   return K_2


##### ---------- 3eme application -----------------------

#-------------- Remplissage de N_3_Kg--------------------

@app.callback(                       # Recuperer la quantite d'angrais
        Output("N_3", "children"),      
        [Input("Q_3","value"),
         Input("Form_ang3","value")
        ],
)

def quantite_N3(Q_3 ,Form_ang3):   
   if Form_ang3 == "15-15-15":
       N_3= Q_3 * 0.15
   elif Form_ang3 == "15-10-10":
       N_3= Q_3 * 0.15
   elif Form_ang3 == "6-10-20":
        N_3= Q_3 * 0.06
   elif Form_ang3 == "46-0-0":
       N_3= Q_3 * 0.46
   elif Form_ang3 == "18-46-0":
       N_3=Q_3 * 0.18
   elif Form_ang3 == "0-0-0":
       N_3=Q_3 * 0
   else :
       N_3= "Entrer les valeurs"
   return N_3

#------------ Remplissage de P_3_Kg--------------------

@app.callback(                      
        Output("P_3", "children"),      
        [Input("Q_3","value"),
         Input("Form_ang3","value")
        ],
)

def quantite_P3(Q_3 ,Form_ang3):   
   if Form_ang3 == "15-15-15":
       P_3= Q_3 * 0.15
   elif Form_ang3 == "15-10-10":
       P_3= Q_3 * 0.1
   elif Form_ang3 == "6-10-20":
        P_3= Q_3 * 0.1
   elif Form_ang3 == "46-0-0":
       P_3= Q_3 * 0
   elif Form_ang3 == "18-46-0":
       P_3=Q_3 * 0.46
   elif Form_ang3 == "0-0-0":
       P_3=Q_3 * 0
   else :
       P_3= "Entrer les valeurs"
   return P_3

# --------------- Remplissage de K_3_Kg---------------------

@app.callback(                     
        Output("K_3", "children"),      
        [Input("Q_3","value"),
         Input("Form_ang3","value")
        ],
)

def quantite_K3(Q_3 ,Form_ang3):   
   if Form_ang3 == "15-15-15":
       K_3= Q_3 * 0.15
   elif Form_ang3 == "15-10-10":
       K_3= Q_3 * 0.1
   elif Form_ang3 == "6-10-20":
        K_3= Q_3 * 0.2
   elif Form_ang3 == "46-0-0":
       K_3= Q_3 * 0
   elif Form_ang3 == "18-46-0":
       K_3=Q_3 * 0
   elif Form_ang3 == "0-0-0":
       K_3=Q_3 * 0   
   else :
       K_3= "Entrer les valeurs"
   return K_3

# ---------- 4eme application -------------
# -----------Remplissage N_4------------------

#@app.callback(
#      Output("N_4","children"),
#      [Input("Q_4","value"),
#         Input("Form_ang4","value")
#        ]
#)
#def quantite_N4(Q_4 ,Form_ang4):   
#   if Form_ang4 == "15-15-15":
#       N_4= Q_4 * 0.15
#   elif Form_ang4 == "15-10-10":
#       N_4= Q_4 * 0.15
#   elif Form_ang4 == "6-10-20":
#        N_4_Kg= Q_4 * 0.06
#  elif Form_ang4 == "46-0-0":
#       N_4_Kg= Q_4 * 0.46
#   elif Form_ang4 == "0-0-0":
#       N_4=Q_4 * 0
#   else :
#       N_4_Kg= "Entrer les valeurs"
#   return N_4

# ---------- Remplissage de P_4_Kg---------------

#@app.callback(                      
#        Output("P_4", "children"),      
#        [Input("Q_4","value"),
#         Input("Form_ang4","value")
#        ],
#)

#def quantite_P4(Q_4 ,Form_ang4):   
#   if Form_ang4 == "15-15-15":
#       P_4= Q_4 * 0.15
#   elif Form_ang4 == "15-10-10":
#       P_4= Q_4 * 0.1
#   elif Form_ang4 == "6-10-20":
#        P_4_Kg= Q_4 * 0.1
#   elif Form_ang4 == "46-0-0":
#       P_4_Kg= Q_4 * 0
#   elif Form_ang4 == "0-0-0":
#       P_4=Q_4 * 0
#   else :
#       P_4_Kg= "Entrer les valeurs"
#   return P_4

#---------- Remplissage K_4_Kg------------------

#@app.callback(                      
#        Output("K_4", "children"),      
#        [Input("Q_4","value"),
#         Input("Form_ang4","value")
#        ],
#)

#def quantite_K2(Q_4 ,Form_ang4):   
#   if Form_ang4 == "15-15-15":
#       K_4= Q_4 * 0.15
#   elif Form_ang4 == "15-10-10":
#       K_4= Q_4 * 0.1
#   elif Form_ang4 == "6-10-20":
#        K_4_Kg= Q_4 * 0.2
#   elif Form_ang4 == "46-0-0":
#       K_4_Kg= Q_4 * 0
#   elif Form_ang4 == "0-0-0":
#       K_4=Q_4 * 0
#   else :
#       K_4_Kg= "Entrer les valeurs"
#   return K_4

# ----------Bouton ajouter 1 ---------------
@app.callback(
     Output("aff_1",component_property="style"),
     Input("ajout1",component_property="value")
#     prevent_initial_call=True
        
)
def afficher1(visibility_state):
    if visibility_state =="No_ajout_1":
        N_2=0,
        P_2=0,
        K_2=0,
        return {"display":"none"}
    
    else:
       # visibility_state =="ajout_1":
        return {"display":"block"}

# ----  Bouton Ajouter 2 -------------

#@app.callback(
#     Output("aff_2",component_property="style"),
#     Input("ajout2",component_property="value")
        
#)
#def afficher2(visibility_state2):
#    if visibility_state2 =="ajout_2":
#        return {"display":"none"}

#Dynamic call back for different cultivars for a selected target crop
@app.callback(
    Output("cultivar-dropdown", "options"),
    Input("crop-radio", "value"))
def set_cultivar_options(selected_crop):
    return [{"label": i[7:], "value": i} for i in cultivar_options[selected_crop]]

@app.callback(
    Output("cultivar-dropdown", "value"),
    Input("cultivar-dropdown", "options"))
def set_cultivar_value(available_options):
    return available_options[0]["value"]
#=============================================================
#Dynamic call back for different soils for a selected target crop
@app.callback(
    Output("SNsoil", "options"),
    Input("crop-radio", "value"))
def set_soil_options(selected_crop):
    return [{"label": i, "value": i} for i in soil_options[selected_crop]]

@app.callback(
    Output("SNsoil", "value"),
    Input("SNsoil", "options"))
def set_cultivar_value(available_options):
    return available_options[0]["value"]
#==============================================================
#1) for yield - call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv-yield", "data"),
    Input("btn_csv_yield", "n_clicks"),
    State("yield-table", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, yield_data):
    df =pd.DataFrame(yield_data)
    col = df.columns  #EJ(6/7/2021)
    col_names = [df.columns[0]]   #list for col names - first column for YEAR
    for i in range(1,len(col),3):
        col_names.append(df.columns[i])

    #make a new filtered dataframe to save into a csv
    df_out = pd.DataFrame(columns = col_names)
    # df_out.iloc[:,0]=df.iloc[:,[0]].values  #first column for YEAR
    df_out.iloc[:,0] = df.iloc[:,0].values  #first column for YEAR
    k=1
    for i in range(1,len(col),3):  #for YIELD
        temp=df.iloc[:,i]
        temp=temp.astype(int)
        df_out.iloc[:,k]=temp.values
        k=k+1 #column index for a new df
    return dcc.send_data_frame(df_out.to_csv, "simulated_yield.csv")
#==============================================================
#2) for rainfall - call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv-rain", "data"),
    Input("btn_csv_rain", "n_clicks"),
    State("yield-table", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, yield_data):
    df =pd.DataFrame(yield_data)
    col = df.columns  #EJ(6/7/2021)
    col_names = [df.columns[0]]   #first column for YEAR
    for i in range(3,len(col),3):
        col_names.append(df.columns[i])

    #make a new filtered dataframe to save into a csv
    df_out = pd.DataFrame(columns = col_names)
    df_out.iloc[:,0] = df.iloc[:,0].values  #first column for YEAR
    k=1
    for i in range(3,len(col),3):  #for YIELD
        # temp=df.iloc[:,[i]]
        temp=df.iloc[:,i]
        temp=temp.astype(int)
        df_out.iloc[:,k]=temp.values
        k=k+1 #column index for a new df
    return dcc.send_data_frame(df_out.to_csv, "seasonal_rainfall.csv")
#=================================================
#3) for prob of exceedance - call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv-Pexe", "data"),
    Input("btn_csv_Pexe", "n_clicks"),
    State("yield-table", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, yield_data):
    df =pd.DataFrame(yield_data)
    col = df.columns  #EJ(6/7/2021)
    col_names = [df.columns[0]]   #first column for YEAR
    for i in range(2,len(col),3):
        col_names.append(df.columns[i])

    #make a new filtered dataframe to save into a csv
    df_out = pd.DataFrame(columns = col_names)
    df_out.iloc[:,0] = df.iloc[:,0].values  #first column for YEAR
    k=1
    for i in range(2,len(col),3):  #for YIELD
        temp=df.iloc[:,i]
        df_out.iloc[:,k]=temp.values
        k=k+1 #column index for a new df
    return dcc.send_data_frame(df_out.to_csv, "prob_of_exceedance.csv")
#==============================================================
#call back to save Enterprise Budgeting df into a csv file
@app.callback(
    Output("download-dataframe-csv_EB", "data"),
    Input("btn_csv_EB", "n_clicks"),
    State("memory-EB-table", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, EB_data):
    df =pd.DataFrame(EB_data)
    return dcc.send_data_frame(df.to_csv, "simulated_yield_EB.csv")
#=================================================
#call back to "show/hide" fertilizer input table
@app.callback(Output("fert-table-Comp", component_property="style"),
              Input("fert_input", component_property="value"))
def show_hide_table(visibility_state):
    if visibility_state == "Fert":
        return {}
    if visibility_state == "No_fert":
        return {"display": "none"}
#==============================================================
#call back to "show/hide" Phosphorus Simulation option
@app.callback(Output("P-sim-Comp", component_property="style"),
              Input("P_input", component_property="value"))
def show_hide_table(visibility_state):
    if visibility_state == "P_yes":
        return {}
    if visibility_state == "P_no":
        return {"display": "none"}
#==============================================================
#call back to "show/hide" irrigation options
@app.callback([Output("irrig-table-Comp", component_property="style"),
              Output("autoirrig-table-Comp", component_property="style")],
              Input("irrig_input", component_property="value"))
def show_hide_table(visibility_state):
    if visibility_state == "repr_irrig":
        return [{}, {"display": "none"}]
    if visibility_state =="auto_irrig":
        return [{"display": "none"}, {}]
    if visibility_state =="No_irrig":
        return [{"display": "none"}, {"display": "none"}]
#==============================================================
#call back to "show/hide" Enterprise Budgetting input table
@app.callback(Output("EB-table-Comp", component_property="style"),
              Input("EB_radio", component_property="value"))
def show_hide_EBtable(visibility_state):
    if visibility_state == "EB_Yes":
        return {}
    if visibility_state == "EB_No":
        return {"display": "none"}
#==============================================================
#call back to "show/hide" Enterprise Budgetting graphs
@app.callback(Output("EB-figures", component_property="style"),
              Input("EB_radio", component_property="value"),
              Input("scenario-table","data"),
)
def show_hide_EBtable(EB_radio, scenarios):
    existing_sces = pd.DataFrame(scenarios)
    if EB_radio == "EB_Yes":
        return {}
    if existing_sces.empty:
        return {"display": "none"}
    else:
        if existing_sces.sce_name.values[0] == "N/A" or set(existing_sces.CropPrice.values) == {-99}:
            return {"display": "none"}
        else:
            return {}
#==============================================================
# callback for downloading scenarios
@app.callback(Output("download-sce", "data"),
              Output("download-sce-error", component_property="style"),
              Input("download-btn-sce", "n_clicks"),
              State("scenario-table","data"),
)
def download_scenarios(n_clicks, scenario_table):
    scenarios = pd.DataFrame(scenario_table)
    # first validate that there is relevant data in the scenario table. TODO: finish validation
    if scenarios.empty:
        return [None, {}]
    else:
        if scenarios.sce_name.values[0] == "N/A":
            return [None, {}]

    # take timestamp and download as csv
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    return [dcc.send_data_frame(scenarios.to_csv, f"simagri_SN_scenarios_{timestamp}.csv"), {"display": "none"}]
#==============================================================
# submit to scenario table or import CSV
@app.callback(Output("scenario-table", "data"),
              Output("import-sce-error","style"),
              Output("import-sce-error","children"),
              Input("write-button-state", "n_clicks"),
              Input("import-sce", "contents"),
              State("import-sce", "filename"),
              State("SNstation", "value"),
              State("year1", "value"),
              State("year2", "value"),
              State("PltDate-picker", "date"),
              State("crop-radio", "value"),
              State("cultivar-dropdown", "value"),
              State("SNsoil", "value"),
              State("ini-H2O", "value"),
              State("ini-NO3", "value"),
              State("plt-density", "value"),
              State("sce-name", "value"),
              State("target-year", "value"),
              State("fert_input", "value"),   # de la
              State("fert-day1","value"),
        #     State("N_1","value"),
        #     State("P_1","value"),
        #     State("K_1","value"),
        #     State("fert-day2","value"),
        #     State("N_2","value"),
        #     State("P_2","value"),
        #     State("K_2","value"),
        #     State("fert-day3","value"),
        #     State("N_3","value"),
        #     State("P_3","value"),
        #     State("K_3","value"),
        #     State("fert-day4","value"),
        #     State("N_4","value"),
        #     State("P_4","value"),
        #     State("K_4","value"),
              State("N-amt1","value"),
              State("P-amt1","value"),
              State("K-amt1","value"),
              State("fert-day2","value"),
              State("N-amt2","value"),
              State("P-amt2","value"),
              State("K-amt2","value"),
              State("fert-day3","value"),
              State("N-amt3","value"),
              State("P-amt3","value"),
              State("K-amt3","value"),
            # State("fert-day4","value"),
            # State("N-amt4","value"),
            # State("P-amt4","value"),
            # State("K-amt4","value"),      
              State("P_input", "value"),
              State("extr_P", "value"),
              State("irrig_input", "value"),
              State("ir_method", "value"),
              State("irrig-day1", "value"),
              State("irrig-amt1", "value"),
              State("irrig-day2", "value"),
              State("irrig-amt2", "value"),
              State("irrig-day3", "value"),
              State("irrig-amt3", "value"),
              State("irrig-day4", "value"),
              State("irrig-amt4", "value"),
              State("irrig-day5", "value"),
              State("irrig-amt5", "value"),
              State("ir_depth", "value"),
              State("ir_threshold", "value"),
              State("ir_eff", "value"),
              State("EB_radio", "value"),
              State("crop-price","value"),
              State("seed-cost","value"),
              State("fert-cost","value"),
              State("irrigation-cost","value"),
              State("fixed-costs","value"),
              State("variable-costs","value"),
              State("scenario-table","data")
)
def make_sce_table( # 53 valeurs
    n_clicks, file_contents, filename, station, start_year, end_year, planting_date, crop, cultivar, soil_type,
    initial_soil_moisture, initial_soil_no3, planting_density, scenario, target_year,
    fert_app,
   #  fd1, fa1,
    fd1, fN1,fP1,fK1, #EJ(7/7/2021) added P and K as well as N
    fd2, fN2,fP2,fK2,
    fd3, fN3,fP3,fK3,
#    fd4, fN4,fP4,fK4,
    p_sim, p_level,  #EJ(7/7/2021) Phosphorous simualtion
    irrig_app,  #EJ(7/7/2021) irrigation option
    irrig_method,  #on reported date
    ird1, iramt1,
    ird2, iramt2,
    ird3, iramt3,
    ird4, iramt4,
    ird5, iramt5,
    ir_depth,ir_threshold, ir_eff,  #automatic when required
    EB_radio,
    crop_price,
    seed_cost,
    fert_cost,
    irrig_cost, ##EJ(7/30/2021) irrigation option
    fixed_costs,
    variable_costs,
    sce_in_table
):

    existing_sces = pd.DataFrame(sce_in_table)
    ctx = dash.callback_context
    if not ctx.triggered:
        triggered_by = "Not triggered"
    else:
        triggered_by = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_by == "import-sce":
        if file_contents is not None:
            content_type, content_string = file_contents.split(",")
            decoded = base64.b64decode(content_string)

            csv_df = None
            try:
                if filename.split(".")[-1] == "csv":
                    # Assume that the user uploaded a CSV file
                    csv_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                    # Remove 'Unnamed: 0' index column
                    csv_df = csv_df.drop(columns=["Unnamed: 0"])
            except Exception as e:
                print(e)
                return [sce_in_table, {"color": "red"}, "There was an error processing this file."]

            # if user deleted all rows from scenario table reassign column names
            if not list(existing_sces):
                existing_sces = pd.DataFrame(columns=sce_col_names)

            if list(csv_df) != list(existing_sces):
                return [sce_in_table, {"color": "red"}, "The columns in the CSV are invalid."]

            # IF all columns match up
            shared_scenarios = list(set(csv_df.sce_name.values) & set(existing_sces.sce_name.values))
            val_csv = pd.DataFrame()
            for i in range(len(csv_df)):
                scenario = csv_df.sce_name[i] # str
                station = csv_df.stn_name[i] # str
                start_year = str(csv_df.FirstYear[i]) # str (original: int)
                end_year = str(csv_df.LastYear[i]) # str (original: int)
                planting_date = csv_df.PltDate[i] # str
                crop = csv_df.Crop[i] # str
                cultivar = csv_df.Cultivar[i] # str
                soil_type = csv_df.soil[i] # str
                initial_soil_moisture = csv_df.iH2O[i] # str
                initial_soil_no3_content = csv_df.iNO3[i] # str
                planting_density = str(csv_df.plt_density[i]) # str (original: float)
                target_year = str(csv_df.TargetYr[i]) # str (original: int)

                # fertiilizer simulation
                fd1 = int(csv_df.Fert_1_DOY[i]) # int
                fN1 = float(csv_df.N_1_Kg[i]) # float
                fP1 = float(csv_df.P_1_Kg[i]) # float
                fK1 = float(csv_df.K_1_Kg[i]) # float
                fd2 = int(csv_df.Fert_2_DOY[i]) # int
                fN2 = float(csv_df.N_2_Kg[i]) # float
                fP2 = float(csv_df.P_2_Kg[i]) # float
                fK2 = float(csv_df.K_2_Kg[i]) # float
                fd3 = int(csv_df.Fert_3_DOY[i]) # int   # enlever
                fN3 = float(csv_df.N_3_Kg[i]) # float
                fP3 = float(csv_df.P_3_Kg[i]) # float
                fK3 = float(csv_df.K_3_Kg[i]) # float
               # fd4 = int(csv_df.Fert_4_DOY[i]) # int
               # fN4 = float(csv_df.N_4_Kg[i]) # float
               # fP4 = float(csv_df.P_4_Kg[i]) # float
               # fK4 = float(csv_df.K_4_Kg[i]) # float

                current_fert = pd.DataFrame({
                    "DAP": [fd1, fd2, fd3, ],     #,fd4 , sortie de crochets
                    "NAmount": [fN1, fN2 ,fN3, ], #,fN4 ,
                    "PAmount": [fP1, fP2 ,fP3,],  #, fP4 
                    "KAmount": [fK1, fK2, fK3, ], #fK4 ,
                })

                # Phosphorous simualtion
                p_level = csv_df.P_level[i] # str

                # irrigation option
                irrig_method = csv_df.IR_method[i] # str

                #on reported date
                ird1 = int(csv_df.IR_1_DOY[i]) # int
                iramt1 = float(csv_df.IR_1_amt[i]) # float
                ird2 = int(csv_df.IR_2_DOY[i]) # int
                iramt2 = float(csv_df.IR_2_amt[i]) # float
                ird3 = int(csv_df.IR_3_DOY[i]) # int
                iramt3 = float(csv_df.IR_3_amt[i]) # float
                ird4 = int(csv_df.IR_4_DOY[i]) # int
                iramt4 = float(csv_df.IR_4_amt[i]) # float
                ird5 = int(csv_df.IR_5_DOY[i]) # int
                iramt5 = float(csv_df.IR_5_amt[i]) # float

                current_irrig = pd.DataFrame({
                    "DAP": [ird1, ird2, ird3, ird4, ird5,],
                    "WAmount": [iramt1, iramt2, iramt3, iramt4,iramt5,],
                })

                #automatic when required
                ir_depth = float(csv_df.AutoIR_depth[i]) # float
                ir_threshold = float(csv_df.AutoIR_thres[i]) # float
                ir_eff = float(csv_df.AutoIR_eff[i]) # float

                crop_price = float(csv_df.CropPrice[i]) # float
                seed_cost = float(csv_df.NFertCost[i]) # float
                fert_cost = float(csv_df.SeedCost[i]) # float
                irrig_cost = float(csv_df.IrrigCost[i]) # float
                fixed_costs = float(csv_df.OtherVariableCosts[i]) # float
                variable_costs = float(csv_df.FixedCosts[i]) # float
                #################################################
                # Validate data

                if ( # first check that all required inputs have been given
                        scenario == None
                    or  start_year == None
                    or  end_year == None
                    or  target_year == None
                    or  planting_date == None
                    or  planting_density == None
                    or (
                            fd1 == None or fN1 == None  or fP1 == None  or fK1== None
                        or  fd2 == None or fN2 == None  or fP2 == None  or fK2== None
                        or  fd3 == None or fN3 == None  or fP3 == None  or fK3== None
   #                     or  fd4 == None or fN4 == None  or fP4 == None  or fK4== None
                    )
                    or (
                            irrig_method == None
                        or  ird1 == None  or iramt1 == None
                        or  ird2 == None  or iramt2 == None
                        or  ird3 == None  or iramt3 == None
                        or  ird4 == None  or iramt4 == None
                        or  ird5 == None  or iramt5 == None
                    )
                    or (
                            ir_depth == None
                        or  ir_threshold == None
                        or  ir_eff == None
                    )
                    or (
                            crop_price == None
                        or  seed_cost == None
                        or  fert_cost == None
                        or  irrig_cost == None
                        or  fixed_costs == None
                        or  variable_costs == None
                    )
                ):
                    return [sce_in_table, {"color": "red"}, f"Scenario '{scenario}' is missing data."]

                csv_sce_valid = True

                fert_valid = True
                if (
                        (fd1 < 0 or 365 < fd1) or fN1 < 0 or fP1 < 0 or fK1 < 0
                    or  (fd2 < 0 or 365 < fd2) or fN2 < 0 or fP2 < 0 or fK2 < 0
                    or  (fd3 < 0 or 365 < fd3) or fN3 < 0 or fP3 < 0 or fK3 < 0     # enlever
    #                or  (fd4 < 0 or 365 < fd4) or fN4 < 0 or fP4 < 0 or fK4 < 0
                ):
                    if not (
                            fd1 == -99 and fN1 == -99 and fP1 == -99 and fK1 == -99
                        and fd2 == -99 and fN2 == -99 and fP2 == -99 and fK2 == -99
                        and fd3 == -99 and fN3 == -99 and fP3 == -99 and fK3 == -99    # enlever
   #                     and fd4 == -99 and fN4 == -99 and fP4 == -99 and fK4 == -99
                    ):
                        fert_valid = False
                else:
                    if not (
                            float(fd1).is_integer() and (fN1*10.0).is_integer() and (fP1*10.0).is_integer() and (fK1*10.0).is_integer()
                        and float(fd2).is_integer() and (fN2*10.0).is_integer() and (fP2*10.0).is_integer() and (fK2*10.0).is_integer()
                        and float(fd3).is_integer() and (fN3*10.0).is_integer() and (fP3*10.0).is_integer() and (fK3*10.0).is_integer()   # enlever
   #                     and float(fd4).is_integer() and (fN4*10.0).is_integer() and (fP4*10.0).is_integer() and (fK4*10.0).is_integer()
                    ):
                        fert_valid = False

                IR_reported_valid = True
                if (
                        (ird1 < 0 or 365 < ird1) or iramt1 < 0
                    or  (ird2 < 0 or 365 < ird2) or iramt2 < 0
                    or  (ird3 < 0 or 365 < ird3) or iramt3 < 0
                    or  (ird4 < 0 or 365 < ird4) or iramt4 < 0
                    or  (ird5 < 0 or 365 < ird5) or iramt5 < 0
                ):
                    if not (
                            ird1 == -99 and iramt1 == -99
                        and ird2 == -99 and iramt2 == -99
                        and ird3 == -99 and iramt3 == -99
                        and ird4 == -99 and iramt4 == -99
                        and ird5 == -99 and iramt5 == -99
                    ):
                        IR_reported_valid = False
                    else: # this happens if all the above are -99. ie. if automatic irrigation is selected
                        if (
                                (ir_depth < 1 or 100 < ir_depth)
                            or  (ir_threshold < 1 or 100 < ir_threshold)
                            or  (ir_eff < 0.1 or 1 < ir_eff)
                        ):
                            if not (
                                    ir_depth == -99
                                and ir_threshold == -99
                                and ir_eff == -99
                            ):
                                IR_reported_valid = False
                        else:
                            if not (
                                    (ir_depth*10.0).is_integer()
                                and (ir_threshold*10.0).is_integer()
                                and (ir_eff*10.0).is_integer()
                            ):
                                IR_reported_valid = False
                else:
                    if not (
                            float(ird1).is_integer() and (iramt1*10.0).is_integer()
                        and float(ird2).is_integer() and (iramt2*10.0).is_integer()
                        and float(ird3).is_integer() and (iramt3*10.0).is_integer()
                        and float(ird4).is_integer() and (iramt4*10.0).is_integer()
                        and float(ird5).is_integer() and (iramt5*10.0).is_integer()
                    ):
                        IR_reported_valid = False

                EB_valid = True
                if (
                        crop_price < 0
                    or  seed_cost < 0
                    or  fert_cost < 0
                    or  irrig_cost < 0
                    or  fixed_costs < 0
                    or  variable_costs < 0
                ):
                    if not (
                            crop_price == -99
                        and seed_cost == -99
                        and fert_cost == -99
                        and irrig_cost == -99
                        and fixed_costs == -99
                        and variable_costs == -99
                    ): 
                        EB_valid = False
                else:
                    if not (
                            (crop_price*10.0).is_integer()
                        and  (seed_cost*10.0).is_integer()
                        and  (fert_cost*10.0).is_integer()
                        and (irrig_cost*10.0).is_integer()
                        and  (fixed_costs*10.0).is_integer()
                        and  (variable_costs*10.0).is_integer()
                    ):
                        EB_valid = False

                # validate planting date
                planting_date_valid = True
                pl_date_split = planting_date.split("-")
                if not len(pl_date_split) == 2:
                    planting_date_valid = False
                else:
                    mm = pl_date_split[0]
                    dd = pl_date_split[1]

                    long_months = [1,3,5,7,8,10,12]
                    short_months = [2,4,6,9,11]

                    if int(mm) in long_months:
                        if int(dd) < 1 or 31 < int(dd):
                            planting_date_valid = False
                    if int(mm) in short_months:
                        if int(dd) < 1 or 30 < int(dd):
                            planting_date_valid = False
                    if int(mm) == 2:
                        if int(dd) < 1 or 28 < int(dd):
                            planting_date_valid = False

                csv_sce_valid = (
                        re.match("....", scenario)
                    and int(start_year) >= 1983 and int(start_year) <= 2016
                    and int(end_year) >= 1983 and int(end_year) <= 2016
                    and int(target_year) >= 1983 and int(target_year) <= 2016
                    and float(planting_density) >= 1 and float(planting_density) <= 300
                    and planting_date_valid and fert_valid and IR_reported_valid and EB_valid
                )

                if csv_sce_valid:
                    df = pd.DataFrame({
                        "sce_name": [scenario], "Crop": [crop], "Cultivar": [cultivar], "stn_name": [station], "PltDate": [planting_date],
                        "FirstYear": [start_year], "LastYear": [end_year], "soil": [soil_type], "iH2O": [initial_soil_moisture],
                        "iNO3": [initial_soil_no3_content], "plt_density": [planting_density], "TargetYr": [target_year],
                        "Fert_1_DOY": [fd1], "N_1_Kg": [fN1],"P_1_Kg": [fP1],"K_1_Kg": [fK1],
                        "Fert_2_DOY": [fd2], "N_2_Kg": [fN2],"P_2_Kg": [fP2],"K_2_Kg": [fK2],
                        "Fert_3_DOY": [fd3], "N_3_Kg": [fN3],"P_3_Kg": [fP3],"K_3_Kg": [fK3],   # enlever
          #              "Fert_4_DOY": [fd4], "N_4_Kg": [fN4],"P_4_Kg": [fP4],"K_4_Kg": [fK4],
                        "P_level": [p_level],
                        "IR_method": [irrig_method],
                        "IR_1_DOY": [ird1], "IR_1_amt": [iramt1],
                        "IR_2_DOY": [ird2], "IR_2_amt": [iramt2],
                        "IR_3_DOY": [ird3], "IR_3_amt": [iramt3],
                        "IR_4_DOY": [ird4], "IR_4_amt": [iramt4],
                        "IR_5_DOY": [ird5], "IR_5_amt": [iramt5],
                        "AutoIR_depth":  [ir_depth], "AutoIR_thres": [ir_threshold], "AutoIR_eff": [ir_eff], #Irrigation automatic
                        "CropPrice": [crop_price], "NFertCost": [fert_cost], "SeedCost": [seed_cost],"IrrigCost": [irrig_cost],  "OtherVariableCosts": [variable_costs], "FixedCosts": [fixed_costs],
                    })
                    val_csv = val_csv.append(df, ignore_index=True)
                else:
                    return [sce_in_table, {"color": "red"}, f"Scenario '{scenario}' contains invalid data."]

                #=====================================================================
                # Write SNX file
                writeSNX_main_hist(Wdir_path,station,start_year,end_year,f"2021-{planting_date}",crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3,
                                    planting_density,scenario,fert_app, current_fert, p_sim, p_level, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)

            updated_sces = existing_sces
            if existing_sces.empty: # overwrite if empty
                return [val_csv.to_dict("rows"), {"display": "none"}, ""]
            else:
                if existing_sces.sce_name.values[0] == "N/A": # overwrite if "N/A"
                    return [val_csv.to_dict("rows"), {"display": "none"}, ""]
                if bool(shared_scenarios): # duplicate scenario names exist
                    updated_sces = val_csv.append(existing_sces, ignore_index=True)
                    duplicates = ", ".join(f"'{s}'" for s in shared_scenarios)
                    return [updated_sces.to_dict("rows"), {"color": "red"}, f"Could not import scenarios: {duplicates} because they already exist in the table"]
                else: # no duplicate scenario names exist
                    updated_sces = val_csv.append(existing_sces, ignore_index=True) # otherwise append new entry
                    return [updated_sces.to_dict("rows"), {"display": "none"}, ""]
        else:
            return [sce_in_table, {"color": "red"}, "Empty file provided"]

    if triggered_by == "write-button-state":
        if ( # first check that all required inputs have been given
                scenario == None
            or  start_year == None
            or  end_year == None
            or  target_year == None
            or  planting_date == None
            or  planting_density == None
            or (
                    fert_app == "Fert"
                and (
                        fd1 == None or fN1 == None  or fP1 == None  or fK1== None
                    or  fd2 == None or fN2 == None  or fP2 == None  or fK2== None
                    or  fd3 == None or fN3 == None  or fP3 == None  or fK3== None   # enlever
    #               or  fd4 == None or fN4 == None  or fP4 == None  or fK4== None
                )
            )
            or (
                    irrig_app == "repr_irrig"
                and (
                        irrig_method == None
                    or  ird1 == None  or iramt1 == None
                    or  ird2 == None  or iramt2 == None
                    or  ird3 == None  or iramt3 == None
                    or  ird4 == None  or iramt4 == None
                    or  ird5 == None  or iramt5 == None
                )
            )
            or (
                    irrig_app == "auto_irrig"
                and (
                        ir_depth == None
                    or  ir_threshold == None
                    or  ir_eff == None
                )
            )
            or (
                    EB_radio == "EB_Yes"
                and (
                        crop_price == None
                    or  seed_cost == None
                    or  fert_cost == None
                    or  irrig_cost == None
                    or  fixed_costs == None
                    or  variable_costs == None
                )
            )
        ):
            return [sce_in_table, {"display": "none"}, ""]

        # convert integer inputs to string
        start_year = str(start_year)
        end_year = str(end_year)
        target_year = str(target_year)
        planting_density = str(planting_density)

        # Make a new dataframe to return to scenario-summary table
        current_sce = pd.DataFrame({
            "sce_name": [scenario], "Crop": [crop], "Cultivar": [cultivar], "stn_name": [station], "PltDate": [planting_date[5:]],
            "FirstYear": [start_year], "LastYear": [end_year], "soil": [soil_type], "iH2O": [initial_soil_moisture],
            "iNO3": [initial_soil_no3], "plt_density": [planting_density], "TargetYr": [target_year],
            "Fert_1_DOY": [-99], "N_1_Kg": [-99], "P_1_Kg": [-99], "K_1_Kg": [-99],
            "Fert_2_DOY": [-99], "N_2_Kg": [-99], "P_2_Kg": [-99], "K_2_Kg": [-99],
            "Fert_3_DOY": [-99], "N_3_Kg": [-99], "P_3_Kg": [-99], "K_3_Kg": [-99],   # enlever
            "Fert_4_DOY": [-99], "N_4_Kg": [-99], "P_4_Kg": [-99], "K_4_Kg": [-99],
            "P_level": [-99],   #P simulation    EJ(7/7/2021)
            "IR_method": [-99], #Irrigation on reported date
            "IR_1_DOY": [-99], "IR_1_amt": [-99],
            "IR_2_DOY": [-99], "IR_2_amt": [-99],
            "IR_3_DOY": [-99], "IR_3_amt": [-99],
            "IR_4_DOY": [-99], "IR_4_amt": [-99],
            "IR_5_DOY": [-99], "IR_5_amt": [-99],
            "AutoIR_depth":  [-99], "AutoIR_thres": [-99], "AutoIR_eff": [-99], #Irrigation automatic
            "CropPrice": [-99], "NFertCost": [-99], "SeedCost": [-99], "IrrigCost": [-99], "OtherVariableCosts": [-99], "FixedCosts": [-99],
        })

        #=====================================================================
        # #Update dataframe for fertilizer inputs
        fert_valid = True
        current_fert = pd.DataFrame(columns=["DAP", "FDEP", "NAmount", "PAmount", "KAmount"])
        if fert_app == "Fert":
            current_fert = pd.DataFrame({
                "DAP": [fd1, fd2,fd3,  ],      # fd4 sortie
                "NAmount": [fN1, fN2, fN3, ],  # fN4 
                "PAmount": [fP1, fP2, fP3,  ],  # fP4,
                "KAmount": [fK1, fK2, fK3,  ],  # fK4,
            })

            fert_frame =  pd.DataFrame({
                "Fert_1_DOY": [fd1], "N_1_Kg": [fN1],"P_1_Kg": [fP1],"K_1_Kg": [fK1],
                "Fert_2_DOY": [fd2], "N_2_Kg": [fN2],"P_2_Kg": [fP2],"K_2_Kg": [fK2],
                "Fert_3_DOY": [fd3], "N_3_Kg": [fN3],"P_3_Kg": [fP3],"K_3_Kg": [fK3],  # enlever
    #            "Fert_4_DOY": [fd4], "N_4_Kg": [fN4],"P_4_Kg": [fP4],"K_4_Kg": [fK4],
            })
            current_sce.update(fert_frame)

            # validation fert
            if (
                    (fd1 < 0 or 365 < fd1) or fN1 < 0 or fP1 < 0 or fK1 < 0
                or  (fd2 < 0 or 365 < fd2) or fN2 < 0 or fP2 < 0 or fK2 < 0
                or  (fd3 < 0 or 365 < fd3) or fN3 < 0 or fP3 < 0 or fK3 < 0   # enlever
     #           or  (fd4 < 0 or 365 < fd4) or fN4 < 0 or fP4 < 0 or fK4 < 0
            ):
                fert_valid = False
            else:
                if not (
                        float(fd1).is_integer() and (fN1*10.0).is_integer() and (fP1*10.0).is_integer() and (fK1*10.0).is_integer()
                    and float(fd2).is_integer() and (fN2*10.0).is_integer() and (fP2*10.0).is_integer() and (fK2*10.0).is_integer()
                    and float(fd3).is_integer() and (fN3*10.0).is_integer() and (fP3*10.0).is_integer() and (fK3*10.0).is_integer()
     #               and float(fd4).is_integer() and (fN4*10.0).is_integer() and (fP4*10.0).is_integer() and (fK4*10.0).is_integer()
                ):
                    fert_valid = False

        #=====================================================================
        # #Update dataframe for irrigation (on reported date) inputs
        IR_reported_valid = True
        current_irrig = pd.DataFrame(columns=["DAP", "WAmount"])
        if irrig_app == "repr_irrig":
            current_irrig = pd.DataFrame({
                "DAP": [ird1, ird2, ird3, ird4, ird5,],
                "WAmount": [iramt1, iramt2, iramt3, iramt4,iramt5,],
            })

            irrig_frame =  pd.DataFrame({
                "IR_1_DOY": [ird1], "IR_1_amt": [iramt1],
                "IR_2_DOY": [ird2], "IR_2_amt": [iramt2],
                "IR_3_DOY": [ird3], "IR_3_amt": [iramt3],
                "IR_4_DOY": [ird4], "IR_4_amt": [iramt4],
                "IR_5_DOY": [ird5], "IR_5_amt": [iramt5],
            })
            current_sce.update(irrig_frame)

            if (
                    (ird1 < 0 or 365 < ird1) or iramt1 < 0
                or  (ird2 < 0 or 365 < ird2) or iramt2 < 0
                or  (ird3 < 0 or 365 < ird3) or iramt3 < 0
                or  (ird4 < 0 or 365 < ird4) or iramt4 < 0
                or  (ird5 < 0 or 365 < ird5) or iramt5 < 0
            ):
                IR_reported_valid = False
            else:
                if not (
                        float(ird1).is_integer() and (iramt1*10.0).is_integer()
                    and float(ird2).is_integer() and (iramt2*10.0).is_integer()
                    and float(ird3).is_integer() and (iramt3*10.0).is_integer()
                    and float(ird4).is_integer() and (iramt4*10.0).is_integer()
                    and float(ird5).is_integer() and (iramt5*10.0).is_integer()
                ):
                    IR_reported_valid = False

        if irrig_app == "auto_irrig":
          current_sce.loc[0,"AutoIR_depth"] = ir_depth   #check index 0
          current_sce.loc[0,"AutoIR_thres"] = ir_threshold
          current_sce.loc[0,"AutoIR_eff"] = ir_eff

          if (
                  (ir_depth < 1 or 100 < ir_depth)
              or  (ir_threshold < 1 or 100 < ir_threshold)
              or  (ir_eff < 0.1 or 1 < ir_eff)
          ):
              IR_reported_valid = False

        #=====================================================================
        # Write SNX file
        writeSNX_main_hist(Wdir_path,station,start_year,end_year,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3,
                            planting_density,scenario,fert_app, current_fert, p_sim, p_level, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
        #=====================================================================
        # #Update dataframe for Enterprise Budgeting inputs
        EB_valid = True
        if EB_radio == "EB_Yes":
            EB_frame =  pd.DataFrame({
                "CropPrice": [crop_price],
                "NFertCost": [seed_cost],
                "SeedCost": [fert_cost],
                "IrrigCost": [irrig_cost],
                "OtherVariableCosts": [fixed_costs],
                "FixedCosts": [variable_costs],
            })
            current_sce.update(EB_frame)

            if (
                    crop_price < 0
                or  seed_cost < 0
                or  fert_cost < 0
                or  irrig_cost < 0
                or  fixed_costs < 0
                or  variable_costs < 0
            ):
                EB_valid = False
            else:
                if not (
                        (crop_price*10.0).is_integer()
                    and  (seed_cost*10.0).is_integer()
                    and  (fert_cost*10.0).is_integer()
                    and  (irrig_cost*10.0).is_integer()
                    and  (fixed_costs*10.0).is_integer()
                    and  (variable_costs*10.0).is_integer()
                ):
                    EB_valid = False

        # validate planting date
        planting_date_valid = True
        pl_date_split = planting_date.split("-")
        if not len(pl_date_split) == 3:
            planting_date_valid = False
        else:
            yyyy = pl_date_split[0]
            mm = pl_date_split[1]
            dd = pl_date_split[2]

            long_months = [1,3,5,7,8,10,12]
            short_months = [2,4,6,9,11]

            if not (re.match("\d\d", dd) and re.match("\d\d", mm) and re.match("2021", yyyy)):
                planting_date_valid = False
            else:
                if int(mm) in long_months:
                    if int(dd) < 1 or 31 < int(dd):
                        planting_date_valid = False
                if int(mm) in short_months:
                    if int(dd) < 1 or 30 < int(dd):
                        planting_date_valid = False
                if int(mm) == 2:
                    if int(dd) < 1 or 28 < int(dd):
                        planting_date_valid = False

        # required="required" triggers tooltips. This validation actually prevents improper forms being submitted. BOTH are necessary
        form_valid = (
                re.match("....", current_sce.sce_name.values[0])
            and int(current_sce.FirstYear.values[0]) >= 1983 and int(current_sce.FirstYear.values[0]) <= 2016
            and int(current_sce.LastYear.values[0]) >= 1983 and int(current_sce.LastYear.values[0]) <= 2016
            and int(current_sce.TargetYr.values[0]) >= 1983 and int(current_sce.TargetYr.values[0]) <= 2016
            and float(current_sce.plt_density.values[0]) >= 1 and float(current_sce.plt_density.values[0]) <= 300
            and planting_date_valid and fert_valid and IR_reported_valid and EB_valid
        )

        if form_valid:
            if existing_sces.empty: # overwrite if empty
                data = current_sce.to_dict("rows")
            else:
                if existing_sces.sce_name.values[0] == "N/A": # overwrite if "N/A"
                    data = current_sce.to_dict("rows")
                elif scenario in existing_sces.sce_name.values: # no duplicate scenario names
                    data = existing_sces.to_dict("rows")
                else:
                    all_sces = current_sce.append(existing_sces, ignore_index=True) # otherwise append new entry
                    data = all_sces.to_dict("rows")
            return [data, {"display": "none"}, ""]
        else:
            return [sce_in_table, {"display": "none"}, ""]

#===============================
#2nd callback to run ALL scenarios
@app.callback(Output(component_id="yieldbox-container", component_property="children"),
                Output(component_id="yieldcdf-container", component_property="children"),
                Output(component_id="yieldtimeseries-container", component_property="children"),
                Output(component_id="yield-BN-container", component_property="children"),
                Output(component_id="yield-NN-container", component_property="children"),
                Output(component_id="yield-AN-container", component_property="children"),
                Output(component_id="yieldtables-container", component_property="children"),
                Output("memory-yield-table", "data"),
                Input("simulate-button-state", "n_clicks"),
                State("scenario-table","data"), ### scenario summary table
                State("season-slider", "value"), #EJ (5/13/2021) for seasonal total rainfall
                prevent_initial_call=True,
              )

def run_create_figure(n_clicks, sce_in_table, slider_range):
    if n_clicks is None:
        raise PreventUpdate
    else:

        # 1) Read saved scenario summaries and get a list of scenarios to run
        # dff = pd.read_json(intermediate, orient="split")
        scenarios = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        num_sces = len(scenarios.sce_name.values)
        Wdir_path = DSSAT_FILES_DIR   #for linux system
        TG_yield = []

        #EJ(5/3/2021) run DSSAT for each scenarios with individual V47
            #EJ(5/18/2021)variables for extracting seasonal total rainfall
        start_month, end_month = slider_range
        first_DOYs = [1,32,60,91,121,152,182,213,244,274,305,335]
        last_DOYs = [31,59,90,120,151,181,212,243,273,304,334,365]
        season_starts_DOY = first_DOYs[start_month-1]  #first doy of the target season
        season_ends_DOY = last_DOYs[end_month-1]  #last doy of the target season

        # for each scenario
        for i in range(num_sces):
            scenario = scenarios.sce_name.values[i]
            # EJ(5/18/2021) extract seasonal rainfall total
            firstyear = int(scenarios.FirstYear[i])
            lastyear = int(scenarios.LastYear[i])
            WTD_fname = path.join(Wdir_path, scenarios.stn_name[i]+".WTD")
            df_obs = read_WTD(WTD_fname,firstyear, lastyear)  # === Read daily observations into a dataframe (note: Feb 29th was skipped in df_obs)
            df_season_rain = season_rain_rank(df_obs, season_starts_DOY, season_ends_DOY)  #get indices of the sorted years based on SCF1 => df_season_rain.columns = ["YEAR","season_rain", "Rank"]
            #==============end of # EJ(5/18/2021) extract seasonal rainfall total

            # 2) Write V47 file
            temp_dv7 = path.join(Wdir_path, f"DSSBatch_template_{scenarios.Crop[i]}.V47")

            dv7_fname = path.join(Wdir_path, "DSSBatch.V47")
            fr = open(temp_dv7, "r")  # opens temp DV4 file to read
            fw = open(dv7_fname, "w")
            # read template and write lines
            for line in range(0, 10):
                line = fr.readline()
                fw.write(line)

            temp_str = fr.readline()
            SNX_fname = path.join(Wdir_path, f"SN{scenarios.Crop[i]}{scenario}.SNX")

            # On Linux system, we don"t need to do this:
            # SNX_fname = SNX_fname.replace("/", "\\")
            new_str2 = "{0:<95}{1:4s}".format(SNX_fname, repr(1).rjust(4)) + temp_str[99:]
            fw.write(new_str2)
            fr.close()
            fw.close()
            #=====================================================================
            #3) Run DSSAT executable
            os.chdir(Wdir_path)  #change directory  #check if needed or not
            if scenarios.Crop[i] == "PN":
                args = "./dscsm047 CRGRO047 B DSSBatch.V47"
                # args = "./dscsm047 B DSSBatch.V47"
            elif scenarios.Crop[i] == "ML":
                args = "./dscsm047 MLCER047 B DSSBatch.V47"
            else:  # SG
                args = "./dscsm047 SGCER047 B DSSBatch.V47"

            fout_name = f"SN{scenarios.Crop[i]}{scenario}.OSU"
            arg_mv = f"mv Summary.OUT {fout_name}"

            os.system(args)
            os.system(arg_mv)
            # #===========>end of for linux system

            #4) read DSSAT output => Read Summary.out from all scenario output
            # fout_name = path.join(Wdir_path, "SUMMARY.OUT")
            df_OUT=pd.read_csv(fout_name,delim_whitespace=True ,skiprows=3)
            HWAM = df_OUT.iloc[:,20].values  #read 21th column only
            EXPERIMENT = df_OUT.iloc[:,7].values  #read 4th column only
            PDAT = df_OUT.iloc[:,13].values  #read 14th column only
            ADAT = df_OUT.iloc[:,15].values  #read 14th column only
            MDAT = df_OUT.iloc[:,16].values  #read 14th column only
            YEAR = df_OUT.iloc[:,13].values//1000

            doy = repr(PDAT[0])[4:]
            target = scenarios.TargetYr[i] + doy
            yr_index = np.argwhere(PDAT == int(target))

            TG_yield_temp = HWAM[yr_index[0][0]]

            # Make a new dataframe for plotting
            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT, "HWAM":HWAM,"RAIN":df_season_rain.season_rain.values,"RANK":df_season_rain.Rank.values}
            temp_df = pd.DataFrame (data, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM", "RAIN", "RANK"])

            if i==0:
                df = temp_df.copy()
            else:
                df = temp_df.append(df, ignore_index=True)

            TG_yield = [TG_yield_temp]+TG_yield

        df = df.round({"RAIN": 0})  #Round a DataFrame to a variable number of decimal places.
        yield_min = np.min(df.HWAM.values)  #to make a consistent yield scale for exceedance curve =>Fig 4,5,6
        yield_max = np.max(df.HWAM.values)
        x_val = np.unique(df.EXPERIMENT.values)
        #4) Make a boxplot
        # df = px.data.tips()
        # fig = px.box(df, x="time", y="total_bill")
        # fig.show()s
        # fig.update_layout(transition_duration=500)
        # df = px.data.tips()
        # fig = px.box(df, x="Scenario Name", y="Yield [kg/ha]")
        yld_box = px.box(df, x="EXPERIMENT", y="HWAM", title="Boxplot du rendement")
        yld_box.add_scatter(x=x_val,y=TG_yield, mode="markers") #, mode="lines+markers") #"lines")
        yld_box.update_xaxes(title= "Nom du scénario [*Note : Le(s) point(s) rouge(s) représente(nt) le(s) rendement(s) basé(s) sur la météo de l'année cible].")
        yld_box.update_yaxes(title= "Rendement [kg/ha]")

        yld_exc = go.Figure()
        for i in x_val:
            x_data = df.HWAM[df["EXPERIMENT"]==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            yld_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode="lines+markers",
                        name=i[4:]))
        # Edit the layout
        yld_exc.update_layout(title="Courbe de dépassement de rendement",
                        xaxis_title="Rendement [kg/ha]",
                        yaxis_title="Probabilité de dépassement [-]")

        #make a new dataframe to save into CSV
        yr_val = np.unique(df.YEAR.values)
        df_out = pd.DataFrame({"YEAR":yr_val})

        yld_t_series = go.Figure()
        BN_exc = go.Figure() #yield exceedance curve using only BN category
        NN_exc = go.Figure()  #yield exceedance curve using only NN category
        AN_exc = go.Figure()  #yield exceedance curve using only AN category
        for i in x_val:
            x_data = df.YEAR[df["EXPERIMENT"]==i].values
            y_data = df.HWAM[df["EXPERIMENT"]==i].values
            yield_rank = y_data.argsort().argsort() + 1 #<<<<<<==================
            yield_Pexe = np.around(1-[1.0/len(y_data)] * yield_rank, 2) #<<<<<<=====probability of exceedance,  round to the given number of decimals.
            rain_data = df.RAIN[df["EXPERIMENT"]==i].values  # EJ(5/18/2021) seasonal rainfall total
            rain_rank = df.RANK[df["EXPERIMENT"]==i].values  # EJ(5/18/2021) rank of seasonal rainfall total

            ##make a new dataframe to save into CSV
            col_name0 = "Yield_" + i[4:]
            col_name1 = "Y_Pexe_" + i[4:]
            col_name2 = "Rain_" + i[4:]
            df_temp = pd.DataFrame({col_name0:y_data, col_name1:yield_Pexe, col_name2:rain_data})  # EJ(5/18/2021) seasonal rainfall total
            df_out = pd.concat([df_out, df_temp], axis=1)

            yld_t_series.add_trace(go.Scatter(x=x_data, y=y_data,
                        mode="lines+markers",
                        name=i[4:]))
            #==================================================
            #exceedance curve for BN
            BN_thres = len(rain_rank)//3  #Return the largest integer smaller or equal to the division of the inputs.
            NN_thres = len(rain_rank) - BN_thres
            #1)BN
            x_data = y_data[rain_rank <= BN_thres]
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve
            BN_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf, mode="lines+markers", name=i[4:]))
            #2)NN
            mask = np.logical_and(rain_rank > BN_thres, rain_rank <= NN_thres)
            x_data = y_data[mask]
            # x_data = y_data[rain_rank > BN_thres & rain_rank <= NN_thres]
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve
            NN_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf, mode="lines+markers", name=i[4:]))
            #3)AN
            x_data = y_data[rain_rank > NN_thres]
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve
            AN_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf, mode="lines+markers", name=i[4:]))
            #====================================================
        # Edit the layout
        yld_t_series.update_layout(title="Série chronologique du rendement",
                        xaxis_title="année",
                        yaxis_title="Rendement [kg/ha]")
        BN_exc.update_layout(title="Rendement simulé [catégorie sèche]",
                        xaxis_title="Rendement [kg/ha]",
                        yaxis_title="Probabilité de dépassement [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        BN_exc.update_xaxes(range=[yield_min, yield_max])
        NN_exc.update_layout(title="Rendement simulé [catégorie normale]",
                        xaxis_title="Rendement [kg/ha]",
                        yaxis_title="Probabilité de dépassement [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        NN_exc.update_xaxes(range=[yield_min, yield_max])
        AN_exc.update_layout(title="Rendement simulé [catégorie humide]",
                        xaxis_title="Rendement [kg/ha]",
                        yaxis_title="Probabilité de dépassement [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        AN_exc.update_xaxes(range=[yield_min, yield_max])

        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_yield.csv")
        df_out.to_csv(fname, index=False)

        return [
            dcc.Graph(id="yield-boxplot", figure = yld_box, config = graph.config, ),
            dcc.Graph(id="yield-exceedance", figure = yld_exc, config = graph.config, ),
            dcc.Graph(id="yield-ts", figure = yld_t_series, config = graph.config, ),
            dcc.Graph(id="yield-BN_exceedance", figure = BN_exc, config = graph.config, ),
            dcc.Graph(id="yield-NN_exceedance", figure = NN_exc, config = graph.config, ),
            dcc.Graph(id="yield-AN_exceedance", figure = AN_exc, config = graph.config, ),
            dash_table.DataTable(columns = [{"name": i, "id": i} for i in df_out.columns],data=df_out.to_dict("records"),
              id="yield-table",
              sort_action = "native",
              sort_mode = "single",
              style_table = {
                "maxHeight": "30vh",
                "overflow": "auto",
                "minWidth": "100%",
              },
              fixed_rows = { "headers": True, "data": 0 },
              fixed_columns = { "headers": True, "data": 1 },
              style_cell = {   # all three widths are needed
                "minWidth": "120px", "width": "120px", "maxWidth": "150px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
              }
            ),
            df_out.to_dict("records"),
        ]
#Last callback to create figures for Enterprise budgeting
@app.callback(Output(component_id="EBbox-container", component_property="children"),
                Output(component_id="EBcdf-container", component_property="children"),
                Output(component_id="EBtimeseries-container", component_property="children"),
                Output(component_id="EBtables-container", component_property="children"),
                Output("memory-EB-table", "data"),
                Input("EB-button-state", "n_clicks"),
                State('yield-multiplier', 'value'), #EJ(6/5/2021)
                State("scenario-table","data") ### scenario summary table
              )

def EB_figure(n_clicks, multiplier, sce_in_table): #EJ(6/5/2021) added multiplier
    if n_clicks is None:
        raise PreventUpdate
        return
    else:
        # 1) Read saved scenario summaries and get a list of scenarios to run
        current_sces = pd.DataFrame(sce_in_table)
        EB_sces = current_sces[current_sces["CropPrice"] != -99]
        sce_numbers = len(EB_sces.sce_name.values)

        if multiplier == None:
            return [html.Div(""),html.Div(""),html.Div(""),html.Div(""),]
        else:
            if multiplier < 0 or 2 < multiplier or sce_numbers == 0:
                return [html.Div(""),html.Div(""),html.Div(""),html.Div(""),]

        Wdir_path = DSSAT_FILES_DIR  #for linux system
        os.chdir(Wdir_path)  #change directory  #check if needed or not
        TG_GMargin = []

        #EJ(5/3/2021) Read DSSAT output for each scenarios
        for i in range(sce_numbers):
            sname = EB_sces.sce_name.values[i]
            fout_name = path.join(Wdir_path, f"SN{EB_sces.Crop[i]}"+sname+".OSU")

            #4) read DSSAT output => Read Summary.out from all scenario output
            df_OUT=pd.read_csv(fout_name,delim_whitespace=True ,skiprows=3)
            HWAM = df_OUT.iloc[:,20].values  #read 21th column only
            HWAM = np.multiply(HWAM, float(multiplier)) #EJ(6/5/2021) added multiplier
            EXPERIMENT = df_OUT.iloc[:,7].values  #read 4th column only
            PDAT = df_OUT.iloc[:,13].values  #read 14th column only
            ADAT = df_OUT.iloc[:,15].values  #read 14th column only
            MDAT = df_OUT.iloc[:,16].values  #read 14th column only
            YEAR = df_OUT.iloc[:,13].values//1000
            NICM = df_OUT.iloc[:,39].values  #read 40th column only,  #NICM   Tot N app kg/ha Inorganic N applied (kg [N]/ha)
            IRCM = df_OUT.iloc[:,30].values    #IRCM   Irrig mm        Season irrigation (mm)   EJ(7/30/2021)
            HWAM[HWAM < 0]=0 #==> if HWAM == -99, consider it as "0" yield (i.e., crop failure)
            #Compute gross margin
            GMargin=HWAM*float(EB_sces.CropPrice[i])- float(EB_sces.NFertCost[i])*NICM - float(EB_sces.IrrigCost[i])*IRCM - float(EB_sces.SeedCost[i]) - float(EB_sces.OtherVariableCosts[i]) - float(EB_sces.FixedCosts[i])

            TG_GMargin_temp = np.nan
            if int(EB_sces.TargetYr[i]) <= int(EB_sces.LastYear[i]):
                doy = repr(PDAT[0])[4:]
                target = EB_sces.TargetYr[i] + doy
                yr_index = np.argwhere(PDAT == int(target))
                TG_GMargin_temp = GMargin[yr_index[0][0]]

            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT, "HWAM":HWAM,"NICM":NICM, "IRCM":IRCM, "GMargin":GMargin}  #EJ(6/5/2021) fixed
            temp_df = pd.DataFrame (data) #, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM","NICM","GMargin"])  #EJ(6/5/2021) fixed

            if i==0:
                df = temp_df.copy()
            else:
                df = temp_df.append(df, ignore_index=True)

            TG_GMargin = [TG_GMargin_temp]+TG_GMargin

        # adding column name to the respective columns
        df.columns =["EXPERIMENT", "YEAR","PDAT", "ADAT","HWAM","NICM","IRCM","GMargin"]
        x_val = np.unique(df.EXPERIMENT.values)
        fig = px.box(df, x="EXPERIMENT", y="GMargin", title="Boxplot de la marge brute")
        fig.add_scatter(x=x_val,y=TG_GMargin, mode="markers") #, mode="lines+markers") #"lines")
        fig.update_xaxes(title= " Nom du scénario")
        fig.update_yaxes(title= "marge brute[CFA/ha]")

        fig2 = go.Figure()
        for i in x_val:
            x_data = df.GMargin[df["EXPERIMENT"]==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            fig2.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode="lines+markers",
                        name=i))
        # Edit the layout
        fig2.update_layout(title="Courbe de dépassement de la marge brute",
                        xaxis_title="marge brute[CFA/ha]",
                        yaxis_title="Probabilité de dépassement [-]")

        #make a new dataframe to save into CSV
        yr_val = np.unique(df.YEAR.values)
        df_out = pd.DataFrame({"YEAR":yr_val})

        fig3 = go.Figure()
        for i in x_val:
            x_data = df.YEAR[df["EXPERIMENT"]==i].values
            y_data = df.GMargin[df["EXPERIMENT"]==i].values
            y_data = y_data.astype(int) #EJ(6/5/2021)

            ##make a new dataframe to save into CSV
            df_temp = pd.DataFrame({i:y_data})
            df_out = pd.concat([df_out, df_temp], axis=1)

            fig3.add_trace(go.Scatter(x=x_data, y=y_data,
                        mode="lines+markers",
                        name=i))
        # Edit the layout
        fig3.update_layout(title="Série chronologique de la marge brute",
                        xaxis_title="année",
                        yaxis_title="marge brute[CFA/ha]")
        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_yield_GMargin.csv")
        df_out.to_csv(fname, index=False)
        return [
            dcc.Graph(id="EB-boxplot", figure = fig, config = graph.config, ),
            dcc.Graph(id="EB-exceedance", figure = fig2, config = graph.config, ),
            dcc.Graph(id="EB-ts", figure = fig3, config = graph.config, ),
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in df_out.columns],
                data=df_out.to_dict("records"),
                style_cell={"whiteSpace": "normal","height": "auto",},),
            df_out.to_dict("records")
            ]

# =============================================
def writeSNX_main_hist(Wdir_path,station,start_year,end_year,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3,
                        planting_density,scenario,fert_app, df_fert,
                        p_sim, p_level, irrig_app, irrig_method, df_irrig, ir_depth,ir_threshold, ir_eff):

    WSTA = station
    NYERS = repr(int(end_year) - int(start_year) + 1)
    plt_year = start_year
    if planting_date is not None:
        date_object = datetime.datetime.strptime(planting_date, '%Y-%m-%d').date()
        plt_doy = date_object.timetuple().tm_yday
    PDATE = plt_year[2:] + repr(plt_doy).zfill(3)
        #   IC_date = first_year * 1000 + (plt_doy - 1)
        #   PDATE = repr(first_year)[2:] + repr(plt_doy).zfill(3)
        # ICDAT = repr(IC_date)[2:]
    ICDAT = plt_year[2:] + repr(plt_doy-1).zfill(3)  #Initial condition => 1 day before planting
    SDATE = ICDAT
    INGENO = cultivar[0:6]
    CNAME = cultivar[7:]
    ID_SOIL = soil_type[0:10]
    PPOP = planting_density  #planting density
    i_NO3 = initial_soil_no3  #
    IC_w_ratio = float(initial_soil_moisture)
    if irrig_app == "repr_irrig":  #on reported dates
        IRRIG = 'D' # days after planting     'R'
        # IMETH = irrig_method
    elif irrig_app == 'auto_irrig':  # automatic when required
        IRRIG = 'A'  # automatic, or 'N' (no irrigation)
        # IMDEP = ir_depth
        # ITHRL = ir_threshold
        # IREFF = ir_eff
    else:
        IRRIG = 'N'  # automatic, or 'N' (no irrigation)
    if fert_app == "Fert":  # fertilizer applied
        FERTI = 'D'  # 'D'= Days after planting, 'R'=on report date, or 'N' (no fertilizer)
    else:
        FERTI = 'N'

    #1) make SNX
    temp_snx = path.join(Wdir_path, f"SN{crop}TEMP.SNX")
    snx_name = f"SN{crop}"+scenario[:4]+".SNX"

    SNX_fname = path.join(Wdir_path, snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    # read lines 1-9 from temp file
    for line in range(0, 14):
        temp_str = fr.readline()
        fw.write(temp_str)

    if irrig_app == "repr_irrig": #on reported dates
        MI = "1"
    else:   #no irrigation or automatic irrigation
        MI = "0"
    if fert_app == "Fert":
        MF = "1"
    else:
        MF = "0"
    if p_sim == "P_yes":  #EJ(7/8/2021) Addd Soil Analysis section if P is simulated
      SA = "1"
    else:
      SA = "0"
    # SA = "0"
    IC = "1"
    MP = "1"
    MR = "0"
    MC = "0"
    MT = "0"
    ME = "0"
    MH = "0"
    SM = "1"
    temp_str = fr.readline()
    FL = "1"
    fw.write("{0:3s}{1:31s}{2:3s}{3:3s}{4:3s}{5:3s}{6:3s}{7:3s}{8:3s}{9:3s}{10:3s}{11:3s}{12:3s}{13:3s}".format(
        FL.rjust(3), "1 0 0 ET-SIMAGRI                 1",
        FL.rjust(3), SA.rjust(3), IC.rjust(3), MP.rjust(3), MI.rjust(3), MF.rjust(3), MR.rjust(3), MC.rjust(3),
        MT.rjust(3), ME.rjust(3), MH.rjust(3), SM.rjust(3)))
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *CULTIVARS
    temp_str = fr.readline()
    new_str = temp_str[0:3] + crop + temp_str[5:6] + INGENO + temp_str[12:13] + CNAME
    fw.write(new_str)
    fw.write(" \n")

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)
    # ================write *FIELDS
    # Get soil info from *.SOL
    SOL_file = path.join(Wdir_path, "SN.SOL")
    soil_depth, wp, fc, nlayer, SLTX = get_soil_IC(SOL_file, ID_SOIL)
    SLDP = repr(soil_depth[-1])
    ID_FIELD = WSTA + "0001"
    WSTA_ID =  WSTA
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write(
        "{0:2s} {1:8s}{2:5s}{3:3s}{4:6s}{5:4s}  {6:10s}{7:4s}".format(FL.rjust(2), ID_FIELD, WSTA_ID.rjust(5),
                                                                        "       -99   -99   -99   -99   -99   -99 ",
                                                                        SLTX.ljust(6), SLDP.rjust(4), ID_SOIL,
                                                                        " -99"))
    fw.write(" \n")
    temp_str = fr.readline()  # 1 -99      CCER       -99   -99 DR000   -99   -99
    temp_str = fr.readline()  # @L ...........XCRD ...........YCRD .....ELEV
    fw.write(temp_str)
    temp_str = fr.readline()  # 1             -99             -99       -99   ==> skip
    # ================write *FIELDS - second section
    # This line must not be changed for Linux version - DSSAt seems to be sensitive to spacing
    fw.write("{0:2s} {1:89s}".format(FL.rjust(2),
                                    "            -99             -99       -99               -99   -99   -99   -99   -99   -99"))
    fw.write(" \n")
    fw.write(" \n")

    #EJ(7/8/2021) Addd Soil Analysis section if P is simulated
    if p_sim == "P_yes":
      fw.write('*SOIL ANALYSIS'+ "\n")
      fw.write('@A SADAT  SMHB  SMPX  SMKE  SANAME'+ "\n")
      fw.write(' 1 '+ ICDAT + ' SA011 SA002 SA014  -99'+ "\n")
      fw.write('@A  SABL  SADM  SAOC  SANI SAPHW SAPHB  SAPX  SAKE  SASC'+ "\n")
      soil_depth, SADM, SAOC, SANI, SAPHW = get_soil_SA(SOL_file, ID_SOIL)
      if p_level == 'V':  #very low
        SAPX = '   2.0'
      elif p_level == 'L':  #Low
        SAPX = '   7.0'
      elif p_level == 'M':  #Medium
        SAPX = '  12.0'
      else:   #high
        SAPX = '  18.0'
      for i in range(0, len(soil_depth)):
        new_str = ' 1'+ repr(soil_depth[i]).rjust(6) + repr(SADM[i]).rjust(6) + repr(SAOC[i]).rjust(6) + repr(SANI[i]).rjust(6) + repr(SAPHW[i]).rjust(6)+ '   -99' + SAPX + '   -99   -99'+"\n"
        fw.write(new_str)

    # read lines from temp file
    for line in range(0, 3):
        temp_str = fr.readline()
        fw.write(temp_str)

    # write *INITIAL CONDITIONS
    temp_str = fr.readline()
    new_str = temp_str[0:9] + ICDAT + temp_str[14:]
    fw.write(new_str)
    temp_str = fr.readline()  # @C  ICBL  SH2O  SNH4  SNO3
    fw.write(temp_str)

    # #Get soil info from *.SOL
    # SOL_file=path.join(self._Setting.ScenariosSetup.Working_directory, "SN.SOL")
    # soil_depth, wp, fc, nlayer = get_soil_IC(SOL_file, ID_SOIL)
    temp_str = fr.readline()

    # check if 30cm soil layer exists - Searching for the position
    soil_set = set(soil_depth)
    if not 30 in soil_set:   #insert one more layer for 30 cm depth
        bisect.insort(soil_depth, 30)  #soil_depth is updated by adding 30cm layer
        index_30=soil_depth.index(30)
        fc = fc[:index_30] + [fc[index_30]] + fc[index_30:]
        wp = wp[:index_30] + [wp[index_30]] + wp[index_30:]
        for nline in range(0, nlayer+1):
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if soil_depth[nline] <= 30:
                #Estimate NO3[ppm] from the user input [N kg/ha] by assuming Buld density = 1.4 g/cm3
                temp_SNO3 = i_NO3 * 10.0 / (1.4 * 30) # **EJ(2/18/2021)
                SNO3 = repr(temp_SNO3)[0:4]  # convert float to string
            else:
                # temp_SH2O = fc[nline]  # float
                SNO3 = '0.5'
            SH2O = repr(temp_SH2O)[0:5]  # convert float to string
            new_str = temp_str[0:5] + repr(soil_depth[nline]).rjust(3) + ' ' + SH2O.rjust(5) + temp_str[14:22] + SNO3.rjust(4) + "\n"
            fw.write(new_str)
    else: #if original soil profile has a 30cm depth
        for nline in range(0, nlayer):
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if soil_depth[nline] <= 30:
                #Estimate NO3[ppm] from the user input [N kg/ha] by assuming Buld density = 1.4 g/cm3
                temp_SNO3 = float(i_NO3) * 10.0 / (1.4 * 30) # **EJ(2/18/2021)
                SNO3 = repr(temp_SNO3)[0:4]  # convert float to string
            else:
                # temp_SH2O = fc[nline]  # float
                SNO3 = '0.5'  # **EJ(5/27/2015)
            SH2O = repr(temp_SH2O)[0:5]  # convert float to string
            new_str = temp_str[0:5] + repr(soil_depth[nline]).rjust(3) + ' ' + SH2O.rjust(5) + temp_str[14:22] + SNO3.rjust(4) + "\n"
            fw.write(new_str)
    fw.write("  \n")

    for nline in range(0, 10):
        temp_str = fr.readline()
        if temp_str[0:9] == '*PLANTING':
            break

    fw.write(temp_str)  # *PLANTING DETAILS
    temp_str = fr.readline()  # @P PDATE EDATE
    fw.write(temp_str)
    # write *PLANTING DETAILS
    temp_str = fr.readline()
    PPOE = PPOP #planting density
    new_str = temp_str[0:3] + PDATE + "   -99" + PPOP.rjust(6) + PPOE.rjust(6) + temp_str[26:]
    fw.write(new_str)
    fw.write("  \n")

    # write *IRRIGATION AND WATER MANAGEMENT, if irrigation on reported dates
    if irrig_app == 'repr_irrig':
        fw.write('*IRRIGATION AND WATER MANAGEMENT'+ "\n")
        fw.write('@I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME'+ "\n")
        fw.write(' 1     1    30    50   100 GS000 IR001    10 -99'+ "\n")
        fw.write('@I IDATE  IROP IRVAL'+ "\n")
        IROP = irrig_method  #irrigation method
        df_irrig = df_irrig.astype(float)
        df_filtered = df_irrig[(df_irrig["DAP"] >= 0) & (df_irrig["WAmount"] >= 0)]
        irrig_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        IDATE = df_filtered.DAP.values
        IRVAL = df_filtered.WAmount.values
        if irrig_count > 0:   # irrigation applied
            for i in range(irrig_count):
                # new_str = ' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + IRVAL.rjust(5)
                fw.write(' 1   '+ repr(int(IDATE[i])).rjust(3) + " " + IROP + " " + repr(IRVAL[i]).rjust(5)+ "\n")
            # fw.write(" \n")

            # df_irrig, ir_depth,ir_threshold, ir_eff
        #end of writing irrigation application

    # write *FERTILIZERS (INORGANIC)
    #get fertilizer info using dash_table.DataTable(https://dash.plotly.com/datatable/callbacks
    #use editable datatable https://dash.plotly.com/datatable/editable
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:12] == "*FERTILIZERS":
            break
    fw.write(temp_str)  # *FERTILIZERS (INORGANIC)
    temp_str = fr.readline()  # @F FDATE  FMCD  FACD
    fw.write(temp_str)
    temp_str = fr.readline()  #1     0 FE005 AP001     5    30   -99   -99   -99   -99   -99   -99
#-0------------        # write *FERTILIZERS (INORGANIC)
    if fert_app == "Fert":                          # ici ?
        df_fert = df_fert.astype(float)
        df_filtered = df_fert[(df_fert["DAP"] >= 0)] # & (df_fert["NAmount"] >= 0)]
        fert_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        FDATE = df_filtered.DAP.values
        FMCD = "FE005"  #Urea
        FACD = 'AP002' #Broadcast, incorporated    #"AP001"  #Broadcast, not incorporated
        FDEP = "2"   #2cm    5cm depth
        FAMN = df_filtered.NAmount.values    # N
        FAMP = df_filtered.PAmount.values    # P
        FAMK = df_filtered.KAmount.values    # K

        if fert_count > 0:   # fertilizer applied
            for i in range(fert_count):
                new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + " " + FMCD.rjust(5) + " " + FACD.rjust(5) + " " + FDEP.rjust(5) + " " + repr(FAMN[i]).rjust(5) + " " + repr(FAMP[i]).rjust(5) + " " + repr(FAMK[i]).rjust(5) + temp_str[44:]
                fw.write(new_str)
            fw.write(" \n")
#-------------------------------------------
    # else: #if no fertilzier applied
    #     temp_str = fr.readline()  #  1     0 FE005 AP002
    #     fw.write(temp_str)
    #     temp_str = fr.readline()  #  1    45 FE005 AP002
    #     fw.write(temp_str)

    fw.write("  \n")
    for nline in range(0, 20):
        temp_str = fr.readline()
        if temp_str[0:11] == "*SIMULATION":
            break
    fw.write(temp_str)  # *SIMULATION CONTROLS
    temp_str = fr.readline()
    fw.write(temp_str)  # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME
    # write *SIMULATION CONTROLS
    temp_str = fr.readline()
    new_str = temp_str[0:18] + NYERS.rjust(2) + temp_str[20:33] + SDATE + temp_str[38:]
    fw.write(new_str)
    temp_str = fr.readline()  # @N OPTIONS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OP
    if p_sim == "P_yes":  #if phosphorous simulation is "on"
        fw.write(' 1 OP              Y     Y     Y     Y     N     N     N     N     D'+ "\n")
    else:
        fw.write(' 1 OP              Y     Y     Y     N     N     N     N     N     D'+ "\n")
    temp_str = fr.readline()  # @N METHODS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 ME
    fw.write(temp_str)
    temp_str = fr.readline()  # @N MANAGEMENT
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 MA
    new_str = temp_str[0:25] + IRRIG + temp_str[26:31] + FERTI + temp_str[32:]
    fw.write(new_str)
    # fw.write(temp_str)
    temp_str = fr.readline()  # @N OUTPUTS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 OU
    fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 5):
        temp_str = fr.readline()
        fw.write(temp_str)
    # irrigation method
    temp_str = fr.readline()  # 1 IR
    if irrig_app == 'auto_irrig':  # automatic when required
        IMDEP = ir_depth
        ITHRL = ir_threshold
        IREFF = ir_eff
        fw.write(' 1 IR          ' + repr(IMDEP).rjust(5) + repr(ITHRL).rjust(6) + '   100 GS000 IR001    10'+ repr(IREFF).rjust(6)+ "\n")
    else:
        # new_str = temp_str[0:39] + IMETH + temp_str[44:]
        fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 7):
        temp_str = fr.readline()
        fw.write(temp_str)

    fr.close()
    fw.close()
    return



# ============================================
#===============================================================
def get_soil_IC(SOL_file, ID_SOIL):
    # SOL_file=Wdir_path.replace("/","\\") + "\\SN.SOL"
    # initialize
    depth_layer = []
    ll_layer = []
    ul_layer = []
    n_layer = 0
    soil_flag = 0
    count = 0
    fname = open(SOL_file, "r")  # opens *.SOL
    for line in fname:
        if ID_SOIL in line:
            soil_depth = line[33:38]#37]
            s_class = line[25:29]
            soil_flag = 1
        if soil_flag == 1:
            count = count + 1
            if count >= 7:
                depth_layer.append(int(line[0:6]))
                ll_layer.append(float(line[13:18]))
                ul_layer.append(float(line[19:24]))
                n_layer = n_layer + 1
                if line[3:6].strip() == soil_depth.strip():
                    fname.close()
                    break
    return depth_layer, ll_layer, ul_layer, n_layer, s_class
#===============================================================
# =============================================
def get_soil_SA(SOL_file, ID_SOIL):
    # SOL_file=Wdir_path.replace("/","\\") + "\\SN.SOL"
    # initialize
    depth_layer = []
    SADM = [] #bulk density
    SAOC = [] #organic carbon %
    SANI = [] #total nitrogen %
    SAPHW = [] #pH in water
    soil_flag = 0
    count = 0
    fname = open(SOL_file, "r")  # opens *.SOL
    for line in fname:
        if ID_SOIL in line:
            soil_depth = line[33:37]
            soil_flag = 1
        if soil_flag == 1:
            count = count + 1
            if count >= 7:
                depth_layer.append(int(line[0:6]))
                SADM.append(float(line[43:49]))
                SAOC.append(float(line[49:55]))
                SANI.append(float(line[73:79]))
                SAPHW.append(float(line[79:85]))
                if line[3:6].strip() == soil_depth.strip():
                    fname.close()
                    break
    return depth_layer, SADM, SAOC, SANI, SAPHW

#===============================================================
def season_rain_rank(WTD_df, sdoy, edoy):
    #sdoy: starting doy of the target period
    #edoy: ending doy of the target period
    #===================================================
    sdoy = int(sdoy) #convert into integer just in case
    edoy = int(edoy)
    #3-1) Extract daily weather data for the target period
    # count how many years are recorded
    year_array = WTD_df.YEAR.unique()
    nyears = year_array.shape[0]

    #Make 2D array and aggregate during the specified season/months (10/15/2020)
    rain_array = np.reshape(WTD_df.RAIN.values, (nyears,365))
    if edoy > sdoy: #all months within the target season is within one year
        season_rain_sum = np.sum(rain_array[:,(sdoy-1):edoy], axis=1)
    else: #seasonal sum goes beyond the first year  #   if edoy < sdoy:
        a= rain_array[:-1,(sdoy-1):]
        b = rain_array[1:,0:edoy]
        rain_array2 = np.concatenate((a,b), axis = 1)
        # season_rain_sum = np.sum(rain_array[:-1,(sdoy-1):(sdoy+edoy)], axis=1)
        season_rain_sum = np.sum(rain_array2, axis=1) #check !
        nyears = nyears - 1
    #================================================================
    # #save dataframe into a csv file [Note: Feb 29th was excluded]
    # df_season_rain = pd.DataFrame(np.zeros((nyears, 3)))
    # df_season_rain.columns = ["YEAR","season_rain", "rank"]  #iyear => ith year
    # df_season_rain.name = "season_rain_sorted"+str(sdoy)
    # df_season_rain.YEAR.iloc[:]= year_array[0:nyears][np.argsort(season_rain_sum)]
    # df_season_rain.season_rain.iloc[:]= season_rain_sum[np.argsort(season_rain_sum)]
    # df_season_rain.sindex.iloc[:]= np.argsort(season_rain_sum)
    rain_rank = season_rain_sum.argsort().argsort()+1  #<<<<<<==================
    # rain_rank = rain_rank +1  #to start from 1, not 0
    data = {"YEAR":year_array[0:nyears], "season_rain": season_rain_sum, "Rank":rain_rank}
    df_season_rain = pd.DataFrame (data, columns = ["YEAR","season_rain", "Rank"])
    # #write dataframe into CSV file for debugging
    # df_season_rain.to_csv("C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\df_season_rain.csv", index=False)
    return df_season_rain
#===============================================================
#====================================================================
# === Read daily observations into a dataframe (note: Feb 29th was skipped in df_obs)
def read_WTD(fname,firstyear, lastyear):
    #1) Read daily observations into a matrix (note: Feb 29th was skipped)
    # WTD_fname = r"C:\Users\Eunjin\IRI\Hybrid_WGEN\CNRA.WTD"
    #1) read observed weather *.WTD (skip 1st row - heading)
    data1 = np.loadtxt(fname,skiprows=1)
    #convert numpy array to dataframe
    WTD_df = pd.DataFrame({"YEAR":data1[:,0].astype(int)//1000,    #python 3.6: / --> //
                    "DOY":data1[:,0].astype(int)%1000,
                    "SRAD":data1[:,1],
                    "TMAX":data1[:,2],
                    "TMIN":data1[:,3],
                    "RAIN":data1[:,4]})

    #=== Extract only years with full 365/366 days:  by checking last obs year if it is incomplete or not
    WTD_last_year = WTD_df.YEAR.values[-1]
    WTD_last_doy = WTD_df.DOY[WTD_df["YEAR"] == WTD_last_year].values[-1]
    if calendar.isleap(WTD_last_year):
        if WTD_last_doy < 366:
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_last_year].index
            WTD_df.drop(indexNames , inplace=True) # Delete these row indexes from dataFrame
    else:
        if WTD_last_doy < 365:
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_last_year].index
            WTD_df.drop(indexNames , inplace=True)
    #=== Extract only years with full 365/366 days:  by checking first obs year if it is incomplete or not
    WTD_first_year = WTD_df.YEAR.values[0]
    WTD_first_date = WTD_df.DOY[WTD_df["YEAR"] == WTD_first_year].values[0]
    if WTD_first_date > 1:
        if calendar.isleap(WTD_first_year):
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_first_year].index
            WTD_df.drop(indexNames , inplace=True)
        else:
            indexNames = WTD_df[WTD_df["YEAR"] == WTD_first_year].index
            WTD_df.drop(indexNames , inplace=True)
    #========================
    rain_WTD = WTD_df.RAIN.values
    srad_WTD = WTD_df.SRAD.values
    Tmax_WTD = WTD_df.TMAX.values
    Tmin_WTD = WTD_df.TMIN.values
    year_WTD = WTD_df.YEAR.values
    doy_WTD = WTD_df.DOY.values
    obs_yrs = np.unique(year_WTD).shape[0]
    #Exclude Feb. 29th in leapyears
    temp_indx = [1 if (calendar.isleap(year_WTD[i])) & (doy_WTD[i] == 29) else 0 for i in range(len(year_WTD))] #[f(x) if condition else g(x) for x in sequence]
    # Get the index of elements with value 15  result = np.where(arr == 15)
    rain_array = rain_WTD[np.where(np.asarray(temp_indx) == 0)]
    rain_array = np.reshape(rain_array, (obs_yrs,365))
    srad_array = srad_WTD[np.where(np.asarray(temp_indx) == 0)]
    srad_array = np.reshape(srad_array, (obs_yrs,365))
    Tmax_array = Tmax_WTD[np.where(np.asarray(temp_indx) == 0)]
    Tmax_array = np.reshape(Tmax_array, (obs_yrs,365))
    Tmin_array = Tmin_WTD[np.where(np.asarray(temp_indx) == 0)]
    Tmin_array = np.reshape(Tmin_array, (obs_yrs,365))

    #save dataframe into a csv file [Note: Feb 29th was excluded]
    df_obs = pd.DataFrame(np.zeros((obs_yrs*365, 6)))
    df_obs.columns = ["YEAR","DOY","SRAD","TMAX","TMIN","RAIN"]  #iyear => ith year
    df_obs.name = "WTD_observed_365"
    k = 0
    for i in range(obs_yrs):
        iyear = np.unique(year_WTD)[i]
        df_obs.YEAR.iloc[k:365*(i+1)] = np.tile(iyear,(365,))
        df_obs.DOY.iloc[k:365*(i+1)]= np.asarray(range(1,366))
        df_obs.SRAD.iloc[k:365*(i+1)]= np.transpose(srad_array[i,:])
        df_obs.TMAX.iloc[k:365*(i+1)]= np.transpose(Tmax_array[i,:])
        df_obs.TMIN.iloc[k:365*(i+1)]= np.transpose(Tmin_array[i,:])
        df_obs.RAIN.iloc[k:365*(i+1)]= np.transpose(rain_array[i,:])
        k=k+365

    #EJ(5/18/2021) Filter df by condition (from firstyear to lastyear)
    df_obs_filter = df_obs.loc[(df_obs["YEAR"] >= firstyear) & (df_obs["YEAR"] <= lastyear)]

    ## df_obs.to_csv(wdir +"//"+ df_obs.name + ".csv", index=False)
    del rain_WTD; del srad_WTD; del Tmax_WTD; del Tmin_WTD; del year_WTD; del doy_WTD
    del rain_array; del srad_array; del Tmax_array; del Tmin_array
    # return WTD_df_orig, df_obs
    return df_obs_filter
#====================================================================
# End of reading observations (WTD file) into a matrix
#====================================================================