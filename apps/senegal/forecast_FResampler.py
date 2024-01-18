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

from app import app

from os import path # path
import os
import subprocess  #to run executable
from datetime import date
import datetime    #to convert date to doy or vice versa
import calendar
import bisect   # an element into sorted list 

import graph

from apps.senegal.write_SNX import writeSNX_clim, writeSNX_frst_FR 
from apps.senegal.write_WTH import write_WTH   #save WTH from the output fo WGEN
from apps.senegal.write_WTH_FR import write_WTH_FR   #save WTH from the output fo FREsampler

from shared.run_FResampler import run_FResampler  # Downscaling method 1) FResampler 

sce_col_names=[ "sce_name", "Trimester1", "AN1","BN1", "AN2","BN2",
                "Crop", "Cultivar","stn_name", "PltDate", #"FirstYear", "LastYear", 
                "soil","iH2O","iNO3","plt_density", #"TargetYr",
                "Fert_1_DOY", "N_1_Kg", "P_1_Kg", "K_1_Kg", "Fert_2_DOY", "N_2_Kg", "P_2_Kg", "K_2_Kg", "Fert_3_DOY", "N_3_Kg", "P_3_Kg", "K_3_Kg",
                "Fert_4_DOY", "N_4_Kg", "P_4_Kg", "K_4_Kg", "P_level", "IR_method", "IR_1_DOY", "IR_1_amt", "IR_2_DOY", "IR_2_amt", "IR_3_DOY", "IR_3_amt", 
                "IR_4_DOY", "IR_4_amt", "IR_5_DOY", "IR_5_amt", "AutoIR_depth", "AutoIR_thres", "AutoIR_eff", 
                "CropPrice", "NFertCost", "SeedCost","IrrigCost", "OtherVariableCosts", "FixedCosts"
],

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
    dcc.Store(id="memory-yield-table_frst"),  #to save fertilizer application table
    dcc.Store(id="memory-sorted-yield-table_frst"),  #to save fertilizer application table
    dcc.Store(id="memory-EB-table_frst"),  #to save fertilizer application table
    dbc.Row([
      dbc.Col([ ## LEFT HAND SIDE
        html.Div(
          html.Div([
            html.Header(
              html.B(
                "Entrée de la simulation (Prévision)",
              ),
            className=" card-header",
            ),

            dbc.Form([ ## INPUT FORM
              html.Div( # SCROLLABLE FORM
                html.Div([ # FORM START
                  dbc.FormGroup([ # Scenario
                    dbc.Label("1) Nom du scénario", html_for="sce-name_frst", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="text", id="sce-name_frst", value="", minLength=4, maxLength=4, required="required", ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Station
                    dbc.Label("2) Station", html_for="SNstation_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                      id="SNstation_frst",
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
                      dbc.Label("Météo observée :", html_for="ETstation_frst", className="p-2", align="start", ),
                      dbc.Row([
                        dbc.Col(dbc.Input(type="text", id="obs_1st", disabled="disabled" ), width=5, ),
                        dbc.Col(html.Div("to", className="text-center",), width=2, ),
                        dbc.Col(dbc.Input(type="text", id="obs_last", disabled="disabled" ), width=5, ),
                      ],),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Seasonal climate forecast EJ(7/25/2021)
                    dbc.Label("3) Prévisions climatiques saisonnières", html_for="SCF", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      html.Div([ # SEASONAL CLIMATE FORECAST
                        html.Div([ # 1st trimester
                          dbc.Row([
                            dbc.Col(
                              dbc.Label("1er trimestre :", html_for="trimester1", className="p-2", align="start", ),
                            ),
                            dbc.Col(
                              dcc.Dropdown(
                                id="trimester1",
                                options=[
                                  {"label": "JFM", "value": "JFM"},
                                  {"label": "FMA", "value": "FMA"},
                                  {"label": "MAM", "value": "MAM"},
                                  {"label": "AMJ", "value": "AMJ"},
                                  {"label": "MJJ", "value": "MJJ"},
                                  {"label": "JJA", "value": "JJA"},
                                  {"label": "JAS", "value": "JAS"},
                                  {"label": "ASO", "value": "ASO"},
                                  {"label": "SON", "value": "SON"},
                                  {"label": "OND", "value": "OND"},
                                  {"label": "NDJ", "value": "NDJ"},
                                  {"label": "DJF", "value": "DJF"}
                                ],
                              value="JJA",
                              clearable=False,
                              ),
                            ),
                          ],),
                          html.Div([
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("AN", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.Label("BN", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.Label("NN", className="text-center", ),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="AN1", value=40, min="0", max="100", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="BN1", value=20, min="0", max="100", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="NN1", value=40, disabled="disabled", required="required", ),
                                ],),
                              ),
                            ],),
                          ]),
                        ]),
                        html.Div([ # 2nd trimester
                          dbc.Row([
                            dbc.Col(
                              dbc.Label("2ème trimestre :", html_for="SCF2", className="p-2", align="start", ),
                            ),
                            dbc.Col(
                              dbc.Input(type="text", id="trimester2", value="SON", disabled="disabled", required="required", ),
                            ),
                          ],),
                          html.Div([
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("AN", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.Label("BN", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.Label("NN", className="text-center", ),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="AN2", value=33, min="0", max="100", step="0.1", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="BN2", value=33, min="0", max="100", step="0.1", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="NN2", value=34, disabled="disabled", required="required", ),
                                ],),
                              ),
                            ],),
                          ]),
                        ]),
                      ],
                      id="scf-table-Comp", 
                      className="w-100",
                      #style={"display": "none"},
                      ),
                    ],
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Crop
                    dbc.Label("4) Culture", html_for="crop-radio_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                      id="crop-radio_frst",
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
                    dbc.Label("5) Cultivar", html_for="cultivar-dropdown_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="cultivar-dropdown_frst", 
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
                  dbc.FormGroup([ # Soil Type
                    dbc.Label("6) Type de sol", html_for="SNsoil_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="SNsoil_frst", 
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
                    dbc.Label("7) État hydrique initial du sol", html_for="ini-H2O_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="ini-H2O_frst", 
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
                    dbc.Label(["8) Teneur initiale du sol en NO3 ", html.Span("  ([N kg/ha] dans les 30 premiers centimètres du sol)"), ],html_for="ini-NO3_frst", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="ini-NO3_frst", value="20.1",min=1, max=150, step=0.1, required="required", ),
                      dbc.FormText("Référence] Faible teneur en nitrates : 20 N kg/ha (~ 4,8 ppm), forte teneur en nitrates : 85 N kg/ha (~20 ppm)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Date
                    dbc.Label("9) Date de semis", html_for="PltDate-picker_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.DatePickerSingle(
                      id="PltDate-picker_frst",
                      # min_date_allowed=date(2021, 1, 1),
                      # max_date_allowed=date(2021, 12, 31),
                      initial_visible_month=date(2021, 6, 5),
                      display_format="DD/MM/YYYY",
                      date=date(2021, 6, 15),
                      ),
                      # dbc.FormText("Only Month and Date are counted"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Density
                    dbc.Label(["10) Densité de semis", html.Span(" (plants/m"), html.Sup("2"), html.Span(")"), ], html_for="plt-density_frst", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="plt-density_frst", value=5, min=1, max=300, step=0.1, required="required", ),
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
                    dbc.Label("11) Application d'engrais N", html_for="fert_input_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="fert_input_frst",
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

                             ]),    

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
                            dbc.Label("Jours après semis", className="text-center", ),
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
                              dbc.Input(type="number", id="fert-day1_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="N-amt1_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="P-amt1_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="K-amt1_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
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
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day2_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="N-amt2_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="P-amt2_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="K-amt2_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),

                      dbc.Row(
                        dbc.FormText(" NB: Vous devez remplir le jour de semis et saisir les nombres ci-dessus sur ces cases. " ),
                               ),
                     dbc.Row("--------------------------------------------------------------------------"),
                      
                     
                     
                      ],id="aff_1" ,
                      style={"display":"none"}
                      ),

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
                              dbc.Input(type="number", id="fert-day3_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                         
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="N-amt3_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="P-amt3_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="K-amt3_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),

                       dbc.Row(
                        dbc.FormText(" NB: Vous devez remplir le jour de semis et saisir les nombres ci-dessus sur ces cases. " ),
                               ),
                     dbc.Row("--------------------------------------------------------------------------"),

                        dbc.Row([
                         
                          dbc.Col(
                            dbc.FormGroup([
                        #      dbc.Input(type="number", id="fert-day4_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                         
                          dbc.Col(
                            dbc.FormGroup([
                        #      dbc.Input(type="number", id="N-amt4_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                        #      dbc.Input(type="number", id="P-amt4_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                        #      dbc.Input(type="number", id="K-amt4_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
                      dbc.Row([
                       # dbc.FormText(" L'utilisateur doit déduire la quantité de N de la quantité totale d'engrais. Par exemple, si l'on applique 150 kg/ha de NPK (15-15-15), la quantité de N sera de 150*15/100 = 22,5 N kg/ha."),
                        ],
                        ),
                      ],
                      id="fert-table-Comp_frst", 
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
                    dbc.Label("12) Simulation du phosphore ?[arachide seulement]", html_for="P_input_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="P_input_frst",
                        options=[
                          {"label": "Oui", "value": "P_yes"},
                          {"label": "Non", "value": "P_no"},
                        ],
                        labelStyle = {"display": "inline-block","marginRight": 10},
                        value="P_no",
                      ),
                      html.Div([
                        dbc.Label("Niveau de phosphore extractible du sol", html_for="extr_P_frst", align="start", ),
                        dcc.Dropdown(
                          id="extr_P_frst", 
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
                      id="P-sim-Comp_frst", 
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
                    dbc.Label("13) Irrigation", html_for="irrig_input_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="irrig_input_frst",
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
                          dbc.Label("Méthode d'irrigation ", html_for="ir_method_frst", align="start", ),
                          dcc.Dropdown(
                            id="ir_method_frst", 
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
                                  dbc.Input(type="number", id="irrig-day1_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt1_frst", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("2ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day2_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt2_frst", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("3ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day3_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt3_frst", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("4ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day4_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt4_frst", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("5ème", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-day5_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="irrig-amt5_frst", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                          ],),
                        ],
                        id="irrig-table-Comp_frst", 
                        className="w-100",
                        style={"display": "none"},
                        ),
                        html.Div([ # "Automatic when required"
                          dbc.Row([  #irrigation depth
                            dbc.Col(
                              dbc.Label("Gestion de la profondeur du sol", html_for="ir_depth_frst", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_depth_frst", value=30, min=1, max=100, step=0.1, required="required", ),
                              dbc.FormText("[cm]"),
                            ],),
                          ],
                          className="py-2",
                          ),
                          dbc.Row([  #irrigation threshold
                            dbc.Col(
                              dbc.Label("Seuil", html_for="ir_threshold_frst", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_threshold_frst", value=50, min=1, max=100, step=0.1, required="required", ),
                              dbc.FormText("(% de l'eau maximale disponible déclenchant l'irrigation)"),
                            ],),
                          ],
                          className="py-2",
                          ),
                          dbc.Row([  #efficiency fraction
                            dbc.Col(
                              dbc.Label("Fraction d'efficience de l'irrigation", html_for="ir_eff_frst", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_eff_frst", value=0.9, min=0.1, max=1, step=0.1, required="required", ),
                              dbc.FormText("[0 ~ 1]"),
                            ],), 
                          ],
                          className="py-2",
                          ),
                        ],
                        id="autoirrig-table-Comp_frst", 
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
                    dbc.Label("14) Budgétisation de la Campagne?", html_for="EB_radio_frst", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="EB_radio_frst",
                        options=[
                          {"label": "Yes", "value": "EB_Yes"},
                          {"label": "No", "value": "EB_No"},
                        ],
                        labelStyle = {"display": "inline-block","marginRight": 10},
                        value="EB_No",
                      ),
                      html.Div([ # ENTERPRISE BUDGETING FORM
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("prix de récolte attendu", html_for="crop-price_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="crop-price_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/kg]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Coût de l'engrais", html_for="fert-cost_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-cost_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/N kg]"),
                              # dbc.FormText("If you pay X CFA for 1 bag of 50kg fertilizer (N:P:K = 6:20:10 for peanut), your fertilizer cost = X*100/(6*50) [CFA/N kg]"),
                              dbc.FormText("Si vous payez X FCFA pour 1 sac d'engrais de 50 kg (N:P:K = 6:20:10 pour l'arachide), votre coût d'engrais = X*100/(6*50) [CFA/N kg]."),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Coût des semences", html_for="seed-cost_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="seed-cost_frst", value=0, min=0, step=0.1, required="required", ),
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
                              dbc.Input(type="number", id="irrigation-cost", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/mm]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Autres coûts variables", html_for="variable-costs_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="variable-costs_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/ha]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Coûts fixes", html_for="fixed-costs_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fixed-costs_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[CFA/ha]"),
                            ],),
                          ),
                        ],),
                        # Tutorial link here is hardcoded
                        dbc.FormText(
                          html.Span([
                            "Voir le ",
                            html.A("manuel", target="_blank", href="https://sites.google.com/iri.columbia.edu/simagri-senegal/simagri-tutorial"),
                            " pour plus de détails sur les calculs."
                          ])
                        ),
                      ],
                      id="EB-table-Comp_frst", 
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
                dbc.Button(id="write-button-state_frst", 
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
                id="scenario-table_frst",
                columns=([
                    {"id": "sce_name", "name": "Nom du scénario" }, #Scenario Name"},
                    {"id": "Trimester1", "name": "Trimester1"},  #First trimester e.g., JJA
                    {"id": "AN1", "name": "AN1"},  #AN of the first trimeter
                    {"id": "BN1", "name": "BN1"},  #BN of the first trimester
                    {"id": "AN2", "name": "AN2"},  #AN of the second (following) trimester
                    {"id": "BN2", "name": "BN2"},  #BN of the second (following)
                    {"id": "Crop", "name": "Culture"}, # Crop"},
                    {"id": "Cultivar", "name": "Cultivar"},
                    {"id": "stn_name", "name": "Station"},
                    {"id": "PltDate", "name": "Date de semis"}, # Planting Date"},
                    # {"id": "FirstYear", "name": "First Year"},
                    # {"id": "LastYear", "name": "Last Year"},
                    {"id": "soil", "name": "Type de sol"}, #   Soil Type"},
                    {"id": "iH2O", "name": "Initial H2O"}, #"Initial Soil Water Content"},
                    {"id": "iNO3", "name": "Initial NO3"}, #"Initial Soil Nitrate Content"},
                    {"id": "plt_density", "name": "Densité de semis"}, #  Planting Density"},
                    # {"id": "TargetYr", "name": "Target Yr"},
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
                #    {"id": "Fert_4_DOY", "name": "FDOY(4)"},
                #   {"id": "N_4_Kg", "name": "N(Kg/ha)(4)"},
                #    {"id": "P_4_Kg", "name": "P(Kg/ha)(4)"},
                #   {"id": "K_4_Kg", "name": "K(Kg/ha)(4)"},
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
          #          dict(**{param: "N/A" for param in sce_col_names}) for i in range(1, 2)
                  #  list("N/A" for param in sublist) for i in range(1, 2) for sublist in sce_col_names
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
                        html.Div(html.B("Importer des scénarios :")),
                        "Glisser-déposer ou  ",
                        dcc.Link("sélectionner un fichier", href="", )
                      ],
                      className="d-block mx-auto text-center p-2"
                      )
                    ],
                    id="import-sce_frst", 
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
                    id="download-btn-sce_frst", 
                    n_clicks=0, 
                    className="w-75 h-50 d-block mx-auto m-4",
                    color="secondary"
                    ),
                    dcc.Download(id="download-sce_frst")
                  ],),
                ],
                className="mx-3", 
                no_gutters=True
                ),
                html.Div( # IMPORT/DOWNLOAD ERROR MESSAGES
                  dbc.Row([
                    dbc.Col(
                      html.Div("",
                      id="import-sce-error_frst",
                      style={"display": "none"},
                      ),
                    ),
                    dbc.Col([
                      html.Div(
                        html.Div("Nothing to Download",
                        className="d-block mx-auto m-2", 
                        style={"color": "red"},
                        ),
                      id="download-sce-error_frst",
                      style={"display": "none"}, 
                      ),
                    ]),
                  ]),
                className="text-center mx-3",
                ),
              ]),
            ]),

            html.Div([ # AFTER SCENARIO TABLE
              html.Br(),
              html.Div( ## RUN DSSAT BUTTON
                dbc.Button(id="simulate-button-state_frst", 
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
        html.Div([
          html.Div( # SIMULATIONS
            html.Div([
              html.Header(
                html.B("Graphiques de simulation (Prévision)"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div(
                    dbc.Spinner(children=[
                      html.Div([
                        html.Div(id="yieldbox-container_frst"),
                        html.Div(id="yieldcdf-container_frst"),  #exceedance curve
                        html.Div( #interactive graph for CDF curve like flexible forecast
                          dbc.FormGroup([ # individual cdf graph comparison (climatology vs. forecast)
                            dbc.Label("Nom du scénario ", html_for="sname_cdf", sm=3, align="start", ),
                            dbc.Col([
                              dcc.Dropdown(
                              id="sname_cdf",
                              clearable=False,
                              ),
                            ],
                            className="py-2",
                            xl=9,
                            ),
                          ],
                          row=True,
                          className="m-2",
                          ),                        
                        ),  
                        html.Div(id="yieldcdf-container_indiv"),  #interactive individual cdf graph
                        dbc.Row([
                          dbc.Col(
                            html.Div(id="rain_trimester1"),
                          md=6),
                          dbc.Col(
                            html.Div(id="rain_trimester2"),
                          md=6),
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
                        dbc.Col("", xs=4, className="p-2"),
                        dbc.Col(
                          dbc.Button(id="btn_csv_yield_frst", 
                          children="Rendement simulé", 
                          className="d-block mx-auto",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                        dbc.Col("", xs=4, className="p-2"),
                      ],
                      className="m-3",
                      ),
                      Download(id="download-dataframe-csv-yield_frst"),
                      html.Div(
                        dash_table.DataTable(
                          columns = [{"id": "YEAR", "name": "YEAR"}],
                          id="yield-table",
                          style_table = {"height": "10vh"},
                        ),
                      id="fcst-yieldtables-container", 
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
                    dbc.Label("Facteur d'ajustement du rendement de la budgétisation d'entreprise", html_for="yield-multiplier_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="yield-multiplier_frst", value=1, min=0, max=2, step=0.1, required="required", ),
                      dbc.FormText("Entrez un multiplicateur pour tenir compte d'une marge d'erreur."),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.Button(id="EB-button-state_frst", 
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
                      html.Div(id="EBbox-container_frst"), 
                      html.Div(id="EBcdf-container_frst"),  #exceedance curve
                      html.Div(id="EBtimeseries-container_frst"), #exceedance curve

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
                  dbc.Row([
                    dbc.Col("", xs=4, className="p-2"),
                    dbc.Col(
                      dbc.Button(id="btn_csv_EB_frst", 
                      children="Télécharger", 
                      className="d-block mx-auto w-100",
                      color="secondary"
                      ), 
                    xs=4, 
                    className="p-2"
                    ),
                    dbc.Col("", xs=4, className="p-2"),                    
                  ],
                  className="m-1",
                  ),
                  Download(id="download-dataframe-csv_EB_frst"),
                  html.Div(id="EBtables-container_frst", 
                  className="overflow-auto",
                  style={"height": "20vh"},
                  ),   #yield simulated output
                ]),
              ]),
            ],
            id="EB-figures_frst",
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

Wdir_path = DSSAT_FILES_DIR    #for linux systemn

#==============================================================
#call back to update the first & last weather observed dates
@app.callback(Output("obs_1st", component_property="value"),
              Output("obs_last", component_property="value"),
              Input("SNstation_frst", component_property="value"))
def func(station_id):
    WTD_fname = path.join(Wdir_path, station_id +".WTD")
    data1 = np.loadtxt(WTD_fname,skiprows=1)
    #convert numpy array to dataframe
    df = pd.DataFrame({"YEAR":data1[:,0].astype(int)//1000,   
                    "DOY":data1[:,0].astype(int)%1000,
                    "RAIN":data1[:,4]})
    doy, year = df.DOY.values[0], df.YEAR.values[0]
    result = pd.to_datetime(doy-1, unit='D', origin=str(year))
    first_obsdate = result.strftime('%b-%d-%Y')
    doy, year = df.DOY.values[-1], df.YEAR.values[-1]
    result = pd.to_datetime(doy-1, unit='D', origin=str(year))
    last_obsdate = result.strftime('%b-%d-%Y')
    return [first_obsdate, last_obsdate]

#============================================================== 
#call back to fill second SCF trimester
@app.callback(Output("trimester2", component_property="value"),
              Input("trimester1", component_property="value"))
def func(trimester):
  next_trimester = {
    "JFM": "AMJ",
    "FMA": "MJJ",
    "MAM": "JJA",
    "AMJ": "JAS",
    "MJJ": "ASO",
    "JJA": "SON",
    "JAS": "OND",
    "ASO": "NDJ",
    "SON": "DJF",
    "OND": "JFM",
    "NDJ": "FMA",
    "DJF": "MAM"}
  return next_trimester[trimester]
#==============================================================
#call back to fill SCF Near-Normal 1
@app.callback(Output("NN1", component_property="value"),
              Input("BN1", component_property="value"),
              Input("AN1", component_property="value"),
              )
def func(AN, BN):
  return 100.0-AN-BN
#==============================================================
#call back to fill SCF Near-Normal 1
@app.callback(Output("NN2", component_property="value"),
              Input("BN2", component_property="value"),
              Input("AN2", component_property="value"),
              )
def func(AN, BN):
  return 100.0-AN-BN
#==============================================================
#Dynamic call back for different cultivars for a selected target crop
@app.callback(
    Output("cultivar-dropdown_frst", "options"),
    Input("crop-radio_frst", "value"))
def set_cultivar_options(selected_crop):
    return [{"label": i[7:], "value": i} for i in cultivar_options[selected_crop]]

@app.callback(
    Output("cultivar-dropdown_frst", "value"),
    Input("cultivar-dropdown_frst", "options"))
def set_cultivar_value(available_options):
    return available_options[0]["value"]
#=============================================================
#Dynamic call back for different soils for a selected target crop
@app.callback(
    Output("SNsoil_frst", "options"),
    Input("crop-radio_frst", "value"))
def set_soil_options(selected_crop):
    return [{"label": i, "value": i} for i in soil_options[selected_crop]]

@app.callback(
    Output("SNsoil_frst", "value"),
    Input("SNsoil_frst", "options"))
def set_cultivar_value(available_options):
    return available_options[0]["value"]
#==============================================================
#1) for yield - call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv-yield_frst", "data"),
    Input("btn_csv_yield_frst", "n_clicks"),
    State("memory-yield-table_frst","data"), 
    # State("yield-table_frst", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, yield_data):
    df =pd.DataFrame(yield_data)
    sce_name = np.unique(df.EXPERIMENT.values)
    data = df.HWAM[df["EXPERIMENT"] == sce_name[0]].values  #first scenario
    df_out = pd.DataFrame(data, columns=[sce_name[0]])

    for i in sce_name[1:]:  #from second scenario
      data = df.HWAM[df["EXPERIMENT"] == i].values  
      df_temp = pd.DataFrame(data, columns=[i])
      df_out = pd.concat([df_out, df_temp], axis=1) #concatenate columns with different size

    # col = df.columns  #EJ(6/7/2021)
    # col_names = [df.columns[0]]   #list for col names - first column for YEAR
    # for i in range(1,len(col),3):  
    #     col_names.append(df.columns[i])
      
    # #make a new filtered dataframe to save into a csv
    # df_out = pd.DataFrame(columns = col_names)
    # # df_out.iloc[:,0]=df.iloc[:,[0]].values  #first column for YEAR
    # df_out.iloc[:,0] = df.iloc[:,0].values  #first column for YEAR
    # k=1
    # for i in range(1,len(col),3):  #for YIELD
    #     temp=df.iloc[:,i]
    #     temp=temp.astype(int)
    #     df_out.iloc[:,k]=temp.values
    #     k=k+1 #column index for a new df
    return dcc.send_data_frame(df_out.to_csv, "simulated_yield_forecast.csv")
#==============================================================
#Dynamic call back for individual exceedance curve based on the selected scenario name
@app.callback(
    Output(component_id="yieldcdf-container_indiv", component_property="children"),
    Output(component_id="rain_trimester1", component_property="children"),
    Output(component_id="rain_trimester2", component_property="children"),
    Input("sname_cdf", "value"),
    State("memory-yield-table_frst","data"), 
    prevent_initial_call=True,
    )
def individual_exceedance(scenario_name, yield_table):
    df_yield = pd.DataFrame(yield_table)  #read dash_table.DataTable into pd df 
    exe_name = np.unique(df_yield.EXPERIMENT[df_yield["SNAME"]==scenario_name].values) 
    #1)Yield CDF graphs for both climatology and forecast
    yld_exc = go.Figure()
    for i in exe_name:  
        x_data = df_yield.HWAM[df_yield["EXPERIMENT"]==i].values
        x_data = np.sort(x_data)
        fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
        Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

        yld_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                    mode="lines+markers",
                    name=i)) #name=i[4:]))
        # Edit the layout
        yld_exc.update_layout(title="Courbe de dépassement de rendement pour un scénario sélectionné",
                        xaxis_title="Rendement [Yield, kg/ha]",
                        yaxis_title="Probabilité de dépassement [-]")
    #2) Trimester 1 rainfall CDF graphs for both climatology and forecast
    rain1 = go.Figure()
    for i in exe_name:  
        x_data2 = df_yield.RAIN_T1[df_yield["EXPERIMENT"]==i].values
        x_data2 = np.sort(x_data2)
        fx_scf2 = [1.0/len(x_data2)] * len(x_data2) #pdf
        Fx_scf2 = 1.0-np.cumsum(fx_scf2)  #for exceedance curve

        rain1.add_trace(go.Scatter(x=x_data2, y=Fx_scf2,
                    mode="lines+markers",
                    name=i)) #name=i[4:]))
        # Edit the layout
        rain1.update_layout(title="[Trimester #1] Précipitations ",
                        xaxis_title="Précipitations [mm]",
                        yaxis_title="Probabilité de dépassement [-]")
    #3) Trimester 2 rainfall CDF graphs for both climatology and forecast
    rain2 = go.Figure()
    for i in exe_name:  
        x_data3 = df_yield.RAIN_T2[df_yield["EXPERIMENT"]==i].values
        x_data3 = np.sort(x_data3)
        fx_scf3 = [1.0/len(x_data3)] * len(x_data3) #pdf
        Fx_scf3 = 1.0-np.cumsum(fx_scf3)  #for exceedance curve

        rain2.add_trace(go.Scatter(x=x_data3, y=Fx_scf3,
                    mode="lines+markers",
                    name=i)) #name=i[4:]))
        # Edit the layout
        rain2.update_layout(title="[Trimester #2] Précipitations ",
                        xaxis_title="Précipitations [mm]",
                        yaxis_title="Probabilité de dépassement [-]")
    return [dcc.Graph(id="yield-excd_ind", figure = yld_exc, config = graph.config, ),
            dcc.Graph(id="rain-excd_ind1", figure = rain1, config = graph.config, ),
            dcc.Graph(id="rain-excd_ind2", figure = rain2, config = graph.config, ),
    ]
#==============================================================
#==============================================================
# #2) for rainfall - call back to save df into a csv file
# @app.callback(
#     Output("download-dataframe-csv-rain", "data"),
#     Input("btn_csv_rain", "n_clicks"),
#     State("yield-table", "data"),
#     prevent_initial_call=True,
# )
# def func(n_clicks, yield_data):
#     df =pd.DataFrame(yield_data)
#     col = df.columns  #EJ(6/7/2021) 
#     col_names = [df.columns[0]]   #first column for YEAR
#     for i in range(3,len(col),3):  
#         col_names.append(df.columns[i])
      
#     #make a new filtered dataframe to save into a csv
#     df_out = pd.DataFrame(columns = col_names)
#     df_out.iloc[:,0] = df.iloc[:,0].values  #first column for YEAR
#     k=1
#     for i in range(3,len(col),3):  #for YIELD
#         # temp=df.iloc[:,[i]]
#         temp=df.iloc[:,i]
#         temp=temp.astype(int)
#         df_out.iloc[:,k]=temp.values
#         k=k+1 #column index for a new df
#     return dcc.send_data_frame(df_out.to_csv, "seasonal_rainfall.csv")
# #=================================================    
# #3) for prob of exceedance - call back to save df into a csv file
# @app.callback(
#     Output("download-dataframe-csv-Pexe", "data"),
#     Input("btn_csv_Pexe", "n_clicks"),
#     State("yield-table", "data"),
#     prevent_initial_call=True,
# )
# def func(n_clicks, yield_data):
#     df =pd.DataFrame(yield_data)
#     col = df.columns  #EJ(6/7/2021) 
#     col_names = [df.columns[0]]   #first column for YEAR
#     for i in range(2,len(col),3):  
#         col_names.append(df.columns[i])
      
#     #make a new filtered dataframe to save into a csv
#     df_out = pd.DataFrame(columns = col_names)
#     df_out.iloc[:,0] = df.iloc[:,0].values  #first column for YEAR
#     k=1
#     for i in range(2,len(col),3):  #for YIELD
#         temp=df.iloc[:,i]
#         df_out.iloc[:,k]=temp.values
#         k=k+1 #column index for a new df
#     return dcc.send_data_frame(df_out.to_csv, "prob_of_exceedance.csv")
#==============================================================
#call back to save Enterprise Budgeting df into a csv file
@app.callback(
    Output("download-dataframe-csv_EB_frst", "data"),
    Input("btn_csv_EB_frst", "n_clicks"),
    State("memory-EB-table_frst", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, EB_data):
    df =pd.DataFrame(EB_data)
    return dcc.send_data_frame(df.to_csv, "simulated_yield_EB.csv")
#=================================================   
#call back to "show/hide" fertilizer input table
@app.callback(Output("fert-table-Comp_frst", component_property="style"),
              Input("fert_input_frst", component_property="value"))
def show_hide_table(visibility_state):
    if visibility_state == "Fert":
        return {}
    if visibility_state == "No_fert":
        return {"display": "none"}
#==============================================================
#call back to "show/hide" Phosphorus Simulation option
@app.callback(Output("P-sim-Comp_frst", component_property="style"),
              Input("P_input_frst", component_property="value"))
def show_hide_table(visibility_state):
    if visibility_state == "P_yes":
        return {}
    if visibility_state == "P_no":
        return {"display": "none"}
#==============================================================
#call back to "show/hide" irrigation options
@app.callback([Output("irrig-table-Comp_frst", component_property="style"),
              Output("autoirrig-table-Comp_frst", component_property="style")],
              Input("irrig_input_frst", component_property="value"))
def show_hide_table(visibility_state):
    if visibility_state == "repr_irrig":
        return [{}, {"display": "none"}]
    if visibility_state =="auto_irrig":
        return [{"display": "none"}, {}]
    if visibility_state =="No_irrig":
        return [{"display": "none"}, {"display": "none"}]
#==============================================================
#call back to "show/hide" Enterprise Budgetting input table
@app.callback(Output("EB-table-Comp_frst", component_property="style"),
              Input("EB_radio_frst", component_property="value"))
def show_hide_EBtable(visibility_state):
    if visibility_state == "EB_Yes":
        return {}
    if visibility_state == "EB_No":
        return {"display": "none"}
#==============================================================
#call back to "show/hide" Enterprise Budgetting graphs
@app.callback(Output("EB-figures_frst", component_property="style"),
              Input("EB_radio_frst", component_property="value"),
              Input("scenario-table_frst","data"),
)
def show_hide_EBtable(EB_radio_frst, scenarios):
    existing_sces = pd.DataFrame(scenarios)
    if EB_radio_frst == "EB_Yes":
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
@app.callback(Output("download-sce_frst", "data"),
              Output("download-sce-error_frst", component_property="style"),
              Input("download-btn-sce_frst", "n_clicks"),
              State("scenario-table_frst","data"),
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
    return [dcc.send_data_frame(scenarios.to_csv, f"simagri_SN_fcst_scenarios_{timestamp}.csv"), {"display": "none"}]
#==============================================================
# submit to scenario table or import CSV
@app.callback(Output("scenario-table_frst", "data"),
              Output("import-sce-error_frst","style"),
              Output("import-sce-error_frst","children"),
              Input("write-button-state_frst", "n_clicks"),
              Input("import-sce_frst", "contents"),
              State("import-sce_frst", "filename"),
              State("SNstation_frst", "value"),
              State("trimester1", "value"),
              State("AN1", "value"),
              State("BN1", "value"),
              State("AN2", "value"),
              State("BN2", "value"),
              # State("year1", "value"),
              # State("year2", "value"),
              State("PltDate-picker_frst", "date"),
              State("crop-radio_frst", "value"),
              State("cultivar-dropdown_frst", "value"),
              State("SNsoil_frst", "value"),
              State("ini-H2O_frst", "value"),
              State("ini-NO3_frst", "value"),
              State("plt-density_frst", "value"),
              State("sce-name_frst", "value"),
              # State("target-year", "value"),
              State("fert_input_frst", "value"),
              State("fert-day1_frst","value"),
              State("N-amt1_frst","value"),
              State("P-amt1_frst","value"),
              State("K-amt1_frst","value"),
              State("fert-day2_frst","value"),
              State("N-amt2_frst","value"),
              State("P-amt2_frst","value"),
              State("K-amt2_frst","value"),
              State("fert-day3_frst","value"),
              State("N-amt3_frst","value"),
              State("P-amt3_frst","value"),
              State("K-amt3_frst","value"),
            # State("fert-day4_frst","value"),
            # State("N-amt4_frst","value"),
            # State("P-amt4_frst","value"),
            # State("K-amt4_frst","value"),
              State("P_input_frst", "value"),
              State("extr_P_frst", "value"),
              State("irrig_input_frst", "value"),
              State("ir_method_frst", "value"),
              State("irrig-day1_frst", "value"),
              State("irrig-amt1_frst", "value"),
              State("irrig-day2_frst", "value"),
              State("irrig-amt2_frst", "value"),
              State("irrig-day3_frst", "value"),
              State("irrig-amt3_frst", "value"),
              State("irrig-day4_frst", "value"),
              State("irrig-amt4_frst", "value"),
              State("irrig-day5_frst", "value"),
              State("irrig-amt5_frst", "value"),
              State("ir_depth_frst", "value"),
              State("ir_threshold_frst", "value"),
              State("ir_eff_frst", "value"),
              State("EB_radio_frst", "value"),
              State("crop-price_frst","value"),
              State("seed-cost_frst","value"),
              State("fert-cost_frst","value"),
              State("irrigation-cost","value"),
              State("fixed-costs_frst","value"),
              State("variable-costs_frst","value"),
              State("scenario-table_frst","data")
)
def make_sce_table(
    n_clicks, file_contents, filename, station, trimester, AN1, BN1, AN2, BN2, planting_date, crop, cultivar, soil_type, 
    initial_soil_moisture, initial_soil_no3_content, planting_density, scenario, #target_year, 
    fert_app, 
    fd1, fN1,fP1,fK1, #EJ(7/7/2021) added P and K as well as N
    fd2, fN2,fP2,fK2,
    fd3, fN3,fP3,fK3,
  #  fd4, fN4,fP4,fK4,
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

    if triggered_by == "import-sce_frst":
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
                # start_year = str(csv_df.FirstYear[i]) # str (original: int)
                # end_year = str(csv_df.LastYear[i]) # str (original: int)
                planting_date = csv_df.PltDate[i] # str
                crop = csv_df.Crop[i] # str
                cultivar = csv_df.Cultivar[i] # str
                soil_type = csv_df.soil[i] # str
                initial_soil_moisture = csv_df.iH2O[i] # str
                initial_soil_no3_content = csv_df.iNO3[i] # str
                planting_density = str(csv_df.plt_density[i]) # str (original: float)
                # target_year = str(csv_df.TargetYr[i]) # str (original: int)

                # fertiilizer simulation
                fd1 = int(csv_df.Fert_1_DOY[i]) # int
                fN1 = float(csv_df.N_1_Kg[i]) # float
                fP1 = float(csv_df.P_1_Kg[i]) # float
                fK1 = float(csv_df.K_1_Kg[i]) # float
                fd2 = int(csv_df.Fert_2_DOY[i]) # int
                fN2 = float(csv_df.N_2_Kg[i]) # float
                fP2 = float(csv_df.P_2_Kg[i]) # float
                fK2 = float(csv_df.K_2_Kg[i]) # float
                fd3 = int(csv_df.Fert_3_DOY[i]) # int
                fN3 = float(csv_df.N_3_Kg[i]) # float
                fP3 = float(csv_df.P_3_Kg[i]) # float
                fK3 = float(csv_df.K_3_Kg[i]) # float
              #  fd4 = int(csv_df.Fert_4_DOY[i]) # int
              #  fN4 = float(csv_df.N_4_Kg[i]) # float
              #  fP4 = float(csv_df.P_4_Kg[i]) # float
              #  fK4 = float(csv_df.K_4_Kg[i]) # float

                current_fert = pd.DataFrame({
                    "DAP": [fd1, fd2, fd3,  ],#fd4,
                    "NAmount": [fN1, fN2, fN3, ], # fN4,
                    "PAmount": [fP1, fP2, fP3,  ], #fP4,
                    "KAmount": [fK1, fK2, fK3,  ],# fK4,
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
                    # or  start_year == None
                    # or  end_year == None
                    # or  target_year == None
                    or  planting_date == None
                    or  planting_density == None
                    or (
                            fd1 == None or fN1 == None  or fP1 == None  or fK1== None 
                        or  fd2 == None or fN2 == None  or fP2 == None  or fK2== None 
                        or  fd3 == None or fN3 == None  or fP3 == None  or fK3== None 
                #        or  fd4 == None or fN4 == None  or fP4 == None  or fK4== None 
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
                    or  (fd3 < 0 or 365 < fd3) or fN3 < 0 or fP3 < 0 or fK3 < 0
              #      or  (fd4 < 0 or 365 < fd4) or fN4 < 0 or fP4 < 0 or fK4 < 0
                ):
                    if not (
                            fd1 == -99 and fN1 == -99 and fP1 == -99 and fK1 == -99
                        and fd2 == -99 and fN2 == -99 and fP2 == -99 and fK2 == -99
                        and fd3 == -99 and fN3 == -99 and fP3 == -99 and fK3 == -99
               #         and fd4 == -99 and fN4 == -99 and fP4 == -99 and fK4 == -99
                    ):
                        fert_valid = False
                else:
                    if not (
                            float(fd1).is_integer() and (fN1*10.0).is_integer() and (fP1*10.0).is_integer() and (fK1*10.0).is_integer()
                        and float(fd2).is_integer() and (fN2*10.0).is_integer() and (fP2*10.0).is_integer() and (fK2*10.0).is_integer()
                        and float(fd3).is_integer() and (fN3*10.0).is_integer() and (fP3*10.0).is_integer() and (fK3*10.0).is_integer()
              #          and float(fd4).is_integer() and (fN4*10.0).is_integer() and (fP4*10.0).is_integer() and (fK4*10.0).is_integer()
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
                    # mm = pl_date_split[0]
                    # dd = pl_date_split[1]
                    mm = pl_date_split[1]  #EJ(8/11/2011)
                    dd = pl_date_split[2]

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
                    # and int(start_year) >= 1981 and int(start_year) <= 2018
                    # and int(end_year) >= 1981 and int(end_year) <= 2018
                    # and int(target_year) >= 1981 and int(target_year) <= 2018
                    and float(planting_density) >= 1 and float(planting_density) <= 300
                    and planting_date_valid and fert_valid and IR_reported_valid and EB_valid
                )

                if csv_sce_valid:
                    df = pd.DataFrame({
                        "sce_name": [scenario], "Trimester1": [trimester], "AN1": [AN1],"BN1": [BN1],"AN2": [AN2],"BN2": [BN2],
                        "Crop": [crop], "Cultivar": [cultivar[7:]], "stn_name": [station], "PltDate":[planting_date], # [planting_date[5:]], 
                        "soil": [soil_type], "iH2O": [initial_soil_moisture], 
                        "iNO3": [initial_soil_no3_content], "plt_density": [planting_density], #"TargetYr": [target_year], 
                        "Fert_1_DOY": [-99], "N_1_Kg": [-99], "P_1_Kg": [-99], "K_1_Kg": [-99], 
                        "Fert_2_DOY": [-99], "N_2_Kg": [-99], "P_2_Kg": [-99], "K_2_Kg": [-99], 
                        "Fert_3_DOY": [-99], "N_3_Kg": [-99], "P_3_Kg": [-99], "K_3_Kg": [-99], 
            #            "Fert_4_DOY": [-99], "N_4_Kg": [-99], "P_4_Kg": [-99], "K_4_Kg": [-99], 
                        "P_level": [-99],   #P simulation    EJ(7/72021)
                        "IR_method": [irrig_method],
                        "IR_1_DOY": [ird1], "IR_1_amt": [iramt1],
                        "IR_2_DOY": [ird2], "IR_2_amt": [iramt2],
                        "IR_3_DOY": [ird3], "IR_3_amt": [iramt3],
                        "IR_4_DOY": [ird4], "IR_4_amt": [iramt4],
                        "IR_5_DOY": [ird5], "IR_5_amt": [iramt5],
                        "AutoIR_depth":  [ir_depth], "AutoIR_thres": [ir_threshold], "AutoIR_eff": [ir_eff], #Irrigation automatic
                        "CropPrice": [crop_price], "NFertCost": [fert_cost], "SeedCost": [seed_cost],"IrrigCost": [irrig_cost], "OtherVariableCosts": [variable_costs], "FixedCosts": [fixed_costs],  
                    })
                    val_csv = val_csv.append(df, ignore_index=True)
                else:
                    return [sce_in_table, {"color": "red"}, f"Scenario '{scenario}' contains invalid data."]

                #=====================================================================
                # # Write SNX file
                # writeSNX_main_hist(Wdir_path,station,start_year,end_year,f"2021-{planting_date}",crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3,
                #                     planting_density,scenario,fert_app, current_fert, p_sim, p_level, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
                #=====================================================================
                # Write SNX file for climatology runs
                writeSNX_clim(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                                    planting_density,scenario,fert_app, current_fert, p_sim, p_level, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)  #This is differnt from writeSNX_main_hist in the historical analysis
 
                # Write SNX for forecast runs 
                # #1)for WGEN
                # writeSNX_frst_(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                #                     planting_density,scenario,fert_app, current_fert, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
                #2) for FResampler
                writeSNX_frst_FR(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                                    planting_density,scenario,fert_app, current_fert, p_sim, p_level, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
                #=====================================================================
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

    if triggered_by == "write-button-state_frst":
        if ( # first check that all required inputs have been given
                scenario == None
            or  initial_soil_no3_content == None
            or  planting_date == None
            or  planting_density == None
            or (
                    AN1 == None
                or  BN1 == None
                or  AN2 == None
                or  BN2 == None
            )
            or (
                    fert_app == "Fert"
                and (
                        fd1 == None or fN1 == None  or fP1 == None  or fK1== None 
                    or  fd2 == None or fN2 == None  or fP2 == None  or fK2== None 
                    or  fd3 == None or fN3 == None  or fP3 == None  or fK3== None 
          #          or  fd4 == None or fN4 == None  or fP4 == None  or fK4== None 
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
        # start_year = str(start_year)
        # end_year = str(end_year)
        # target_year = str(target_year)
        planting_density = str(planting_density)

        # Make a new dataframe to return to scenario-summary table
        current_sce = pd.DataFrame({
            "sce_name": [scenario], "Trimester1": [trimester], "AN1": [AN1],"BN1": [BN1],"AN2": [AN2],"BN2": [BN2],
            "Crop": [crop], "Cultivar": [cultivar[7:]], "stn_name": [station], "PltDate":[planting_date], # [planting_date[5:]], 
            "soil": [soil_type], "iH2O": [initial_soil_moisture], 
            "iNO3": [initial_soil_no3_content], "plt_density": [planting_density], #"TargetYr": [target_year], 
            "Fert_1_DOY": [-99], "N_1_Kg": [-99], "P_1_Kg": [-99], "K_1_Kg": [-99], 
            "Fert_2_DOY": [-99], "N_2_Kg": [-99], "P_2_Kg": [-99], "K_2_Kg": [-99], 
            "Fert_3_DOY": [-99], "N_3_Kg": [-99], "P_3_Kg": [-99], "K_3_Kg": [-99], 
            "Fert_4_DOY": [-99], "N_4_Kg": [-99], "P_4_Kg": [-99], "K_4_Kg": [-99], 
            "P_level": [p_level],   #P simulation    EJ(7/72021)
            "IR_method": [irrig_method], #Irrigation on reported date
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
                "DAP": [fd1, fd2, fd3,  ],#fd4,
                "NAmount": [fN1, fN2, fN3,  ],#fN4,
                "PAmount": [fP1, fP2, fP3,  ],#fP4,
                "KAmount": [fK1, fK2, fK3, ], #fK4,
            })

            fert_frame =  pd.DataFrame({
                "Fert_1_DOY": [fd1], "N_1_Kg": [fN1],"P_1_Kg": [fP1],"K_1_Kg": [fK1],
                "Fert_2_DOY": [fd2], "N_2_Kg": [fN2],"P_2_Kg": [fP2],"K_2_Kg": [fK2],
                "Fert_3_DOY": [fd3], "N_3_Kg": [fN3],"P_3_Kg": [fP3],"K_3_Kg": [fK3],
        #        "Fert_4_DOY": [fd4], "N_4_Kg": [fN4],"P_4_Kg": [fP4],"K_4_Kg": [fK4],
            })
            current_sce.update(fert_frame)

            # validation fert
            if (
                    (fd1 < 0 or 365 < fd1) or fN1 < 0 or fP1 < 0 or fK1 < 0
                or  (fd2 < 0 or 365 < fd2) or fN2 < 0 or fP2 < 0 or fK2 < 0
                or  (fd3 < 0 or 365 < fd3) or fN3 < 0 or fP3 < 0 or fK3 < 0
        #        or  (fd4 < 0 or 365 < fd4) or fN4 < 0 or fP4 < 0 or fK4 < 0
            ):
                fert_valid = False
            else:
                if not (
                        float(fd1).is_integer() and (fN1*10.0).is_integer() and (fP1*10.0).is_integer() and (fK1*10.0).is_integer()
                    and float(fd2).is_integer() and (fN2*10.0).is_integer() and (fP2*10.0).is_integer() and (fK2*10.0).is_integer()
                    and float(fd3).is_integer() and (fN3*10.0).is_integer() and (fP3*10.0).is_integer() and (fK3*10.0).is_integer()
        #            and float(fd4).is_integer() and (fN4*10.0).is_integer() and (fP4*10.0).is_integer() and (fK4*10.0).is_integer()
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
        # writeSNX_main_hist(Wdir_path,station,start_year,end_year,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3,
        #                     planting_density,scenario,fert_app, current_fert, p_sim, p_level, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
        writeSNX_clim(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                            planting_density,scenario,fert_app, current_fert, p_sim, p_level, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)  #This is differnt from writeSNX_main_hist in the historical analysis
        # #1)for WGEN
        # writeSNX_frst_(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
        #                     planting_density,scenario,fert_app, current_fert, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
        #2) for FResampler
        writeSNX_frst_FR(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
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

            if not (re.match("\d\d", dd) and re.match("\d\d", mm)): #  and re.match("2021", yyyy)):  #EJ(8/10/2021)
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
            # and int(current_sce.FirstYear.values[0]) >= 1981 and int(current_sce.FirstYear.values[0]) <= 2018
            # and int(current_sce.LastYear.values[0]) >= 1981 and int(current_sce.LastYear.values[0]) <= 2018
            # and int(current_sce.TargetYr.values[0]) >= 1981 and int(current_sce.TargetYr.values[0]) <= 2018
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
@app.callback(Output(component_id="yieldbox-container_frst", component_property="children"),
                Output(component_id="yieldcdf-container_frst", component_property="children"),
                # Output(component_id="yieldtimeseries-container", component_property="children"),
                # Output(component_id="yield-BN-container", component_property="children"),
                # Output(component_id="yield-NN-container", component_property="children"),
                # Output(component_id="yield-AN-container", component_property="children"),
                # Output(component_id="yieldtables-container", component_property="children"),
                Output("sname_cdf", "options"),
                Output("memory-yield-table_frst", "data"),
                Input("simulate-button-state_frst", "n_clicks"),
                State("scenario-table_frst","data"), ### scenario summary table
                # State("season-slider_frst", "value"), #EJ (5/13/2021) for seasonal total rainfall
                prevent_initial_call=True,
              )

def run_create_figure(n_clicks, sce_in_table):
    if n_clicks is None:
        raise PreventUpdate
    else: 

        # 1) Read saved scenario summaries and get a list of scenarios to run
        # dff = pd.read_json(intermediate, orient="split")
        scenarios = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        sce_numbers = len(scenarios.sce_name.values)
        # num_sces = len(scenarios.sce_name.values)
        Wdir_path = DSSAT_FILES_DIR   #for linux system
        TG_yield = []

        #compute seasonal rainfall total for each trimester EJ(7/27/2021)
        trim_dates = { 
            "JFM": [1,90,91,181], #AMJ    1)first doy of 1st trimester, 2) last doy of 1st trimester, 3) first doy of 2nd trimester, 4)last doy of 2nd trimester
            "FMA": [31,120,121,212], #"MJJ",
            "MAM": [60,151,152,243], #"JJA",
            "AMJ": [91,181,182,273], #"JAS",
            "MJJ": [121,212,213,304], #"ASO",
            "JJA": [152,243,244,334], #" SON",
            "JAS": [182,273,274,365], #"OND",
            "ASO": [213,304,305,31], #"NDJ",
            "SON": [244,334,335,59], #"DJF",
            "OND": [274,365,1,90], #"JFM",
            "NDJ": [305,31,32,120], #"FMA",
            "DJF": [335,59,60,151],} #"MAM"}

        for i in range(sce_numbers):
            scenario = scenarios.sce_name.values[i]
            station = scenarios.stn_name.values[i] 
            trimester  = scenarios.Trimester1.values[i]
            tri_doylist = trim_dates[trimester]
            WTD_fname = path.join(Wdir_path, scenarios.stn_name[i]+".WTD")
            AN1 = scenarios.AN1.values[i]
            BN1 = scenarios.BN1.values[i]
            AN2 = scenarios.AN2.values[i]
            BN2 = scenarios.BN2.values[i]
            # # EJ(7/27/2021) RUN WEATHER GENERATOR TO MAKE SYNTHETIC WEATHER REALIZATION
            # i) check if station name and target trimester is repeated or not
            if i ==0:
              # #1)WGEN
              # df_wgen = run_WGEN(scenarios[i:i+1], tri_doylist, Wdir_path)  #pass subset of summary table => NOTE: the scenario names are in reverse order and thus last scenario is selected first
              # write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)   #by taking into account planting and approximate harvesting dates
              #2)FResampler\
              df_wgen = run_FResampler(scenarios[i:i+1], tri_doylist, Wdir_path)  
              write_WTH_FR(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)  
            else:
              if station == scenarios.stn_name.values[i-1] and trimester == scenarios.Trimester1.values[i-1]:
                if AN1 == scenarios.AN1.values[i-1] and BN1 == scenarios.BN1.values[i-1] and AN2 == scenarios.AN2.values[i-1] and BN2 == scenarios.BN2.values[i-1]:
                  #No need to run WGEN again => use df_wgen from previous scenario
                  write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path) 
                else:
                  # #1)WGEN
                  # df_wgen = run_WGEN(scenarios[i:i+1], tri_doylist, Wdir_path)
                  # write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)
                  #2)FResampler
                  df_wgen = run_FResampler(scenarios[i:i+1], tri_doylist, Wdir_path)  
                  write_WTH_FR(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)  
              else:
                # #1)WGEN
                # df_wgen = run_WGEN(scenarios[i:i+1], tri_doylist, Wdir_path)
                # write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)
                #2)FResampler
                df_wgen = run_FResampler(scenarios[i:i+1], tri_doylist, Wdir_path)  
                write_WTH_FR(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path) 
            # # EJ(7/27/2021) end of RUN WEATHER GENERATOR TO MAKE SYNTHETIC WEATHER REALIZATION
            #=====================================================================
            # 1) Write V47 file for climatolgoy
            temp_dv7 = path.join(Wdir_path, f"DSSBatch_template_{scenarios.Crop[i]}.V47")
            dv7_fname = path.join(Wdir_path, "DSSBatch.V47")
            fr = open(temp_dv7, "r")  # opens temp DV4 file to read
            fw = open(dv7_fname, "w")
            # read template and write lines
            for line in range(0, 10):
                temp_str = fr.readline()
                fw.write(temp_str)

            temp_str = fr.readline()
            # SNX_fname = path.join(Wdir_path, "ETMZ{scenario}.SNX")
            # SNX_fname = path.join(Wdir_path, f"ET{scenarios.Crop[i]}{scenario}.SNX")
            SNX_fname = path.join(Wdir_path, f"CL{scenarios.Crop[i]}{scenario}.SNX")  #climatology run
            SNX_fname2 = path.join(Wdir_path, f"FC{scenarios.Crop[i]}{scenario}.SNX")  #forecast run <<<<<<<====================

            # On Linux system, we don"t need to do this:
            # SNX_fname = SNX_fname.replace("/", "\\")    #===========>for windows
            # SNX_fname2 = SNX_fname2.replace("/", "\\")  #===========>for windows
            new_str = "{0:<95}{1:4s}".format(SNX_fname, repr(1).rjust(4)) + temp_str[99:]
            fw.write(new_str)
            new_str2 = "{0:<95}{1:4s}".format(SNX_fname2, repr(1).rjust(4)) + temp_str[99:]
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
            fout_name2 = f"SN{scenarios.Crop[i]}{scenario}.OVERVIEW"  #EJ(8/10 for debugging purpose)
            arg_mv2 = f"mv OVERVIEW.OUT {fout_name2}"     #EJ(8/10 for debugging purpose)         
            os.system(args)
            os.system(arg_mv) 
            os.system(arg_mv2)   #EJ(8/10 for debugging purpose)
            # #===========>end of for linux system
            #=====================================================================

            #4) read DSSAT output => Read Summary.out from all scenario output
            # fout_name = path.join(Wdir_path, "SUMMARY.OUT")
            df_OUT=pd.read_csv(fout_name,delim_whitespace=True ,skiprows=3)
            HWAM = df_OUT.iloc[:,20].values  #read 21th column only
            EXPERIMENT = df_OUT.iloc[:,7].values  #read 4th column only
            PDAT = df_OUT.iloc[:,13].values  #read 14th column only
            ADAT = df_OUT.iloc[:,15].values  #read 14th column only
            MDAT = df_OUT.iloc[:,16].values  #read 14th column only    
            YEAR = df_OUT.iloc[:,13].values//1000
            run_type = ["Forecast" if x[:2] == 'FC' else "Climatology" for x in EXPERIMENT]  #to distinguish "FC(Forecast)" and "CL (climatology)"  check
            sname = [x[4:] for x in EXPERIMENT]  #scenario name (4 char)
            #============================================================
            # ===compute seasonal rainfall total from climatolgoy for trimester 1 & 2
            # WTD_fname = path.join(Wdir_path, scenarios.stn_name[i]+".WTD")
            WTH_fname = path.join(Wdir_path, scenarios.sce_name[i] + '_all.WTH') #+repr(scenarios.PltDate[i])[3:5] +"99.WTH")  # e.g., aaaa2199.WTH
            if i ==0:
              df_FC = Rain_trimester_gen(WTH_fname, tri_doylist)
              df_CL = Rain_trimester_obs(WTD_fname, tri_doylist)
              df_rain = df_CL.append(df_FC, ignore_index=True)
            else:
              if station == scenarios.stn_name.values[i-1] and trimester == scenarios.Trimester1.values[i-1]:
                if AN1 == scenarios.AN1.values[i-1] and BN1 == scenarios.BN1.values[i-1] and AN2 == scenarios.AN2.values[i-1] and BN2 == scenarios.BN2.values[i-1]:
                  print("---no need to estimate rainfall total for each trimester => use old df")
                else:
                  df_FC = Rain_trimester_gen(WTH_fname, tri_doylist)
                  # df_CL = Rain_trimester_obs(WTD_fname, tri_doylist)
                  df_rain = df_CL.append(df_FC, ignore_index=True)
              else:
                df_FC = Rain_trimester_gen(WTH_fname, tri_doylist)
                df_CL = Rain_trimester_obs(WTD_fname, tri_doylist)
                df_rain = df_CL.append(df_FC, ignore_index=True)

            #=========================================================end of seasonal rainfall total estimation              
            # Make a new dataframe for plotting
            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT,"MDAT":MDAT, "HWAM":HWAM, 
                    "RUN": run_type, "SNAME": sname, "RAIN_T1":df_rain.iloc[:,0], "RAIN_T2":df_rain.iloc[:,1]} #,"RAIN":df_season_rain.season_rain.values,"RANK":df_season_rain.Rank.values}
            temp_df = pd.DataFrame (data) #, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM", "RUN", "SNAME"]) #"RAIN", "RANK"])

            #In case of hindcast forecasting (i.e., if the planting year is among the observed years
            year1= temp_df.YEAR[temp_df["RUN"] == "Climatology"].values[0]  #first year of the climatolgy run
            year2= temp_df.YEAR[temp_df["RUN"] == "Climatology"].values[-1]  #lats year of the climatolgy run
            target_year = repr(scenarios.PltDate[i])[1:5]
            if int(target_year) <= year2 and int(target_year) >= year1:
              doy = repr(PDAT[0])[4:]
              target = target_year + doy
              yr_index = np.argwhere(PDAT == int(target))
              TG_yield_temp = HWAM[yr_index[0][0]]   
            else:
              TG_yield_temp = np.nan #-99  #or np.nan ?
            TG_yield = [TG_yield_temp]+TG_yield   #check

            if i==0:
                df = temp_df.copy()
            else:
                df = temp_df.append(df, ignore_index=True)

        # df = df.round({"RAIN": 0})  #Round a DataFrame to a variable number of decimal places.
        # yield_min = np.min(df.HWAM.values)  #to make a consistent yield scale for exceedance curve =>Fig 4,5,6
        # yield_max = np.max(df.HWAM.values)
        x_val = np.unique(df.EXPERIMENT.values)  # => array(['CLMZaaaa', 'CLMZbbbb', 'FCMZaaaa', 'FCMZbbbb'], dtype=object)
        # x_val2 = []
        # for j in scenarios.sce_name.values:
        #   x_val2.append(np.unique(df.EXPERIMENT[df["SNAME"]==j].values))  #CL##aaaa, FC##aaaa, CL##bbbb, FC##bbbb......
        x_val3 = [v for i, v in enumerate(x_val) if "FC" in v] #=> forecast Experiment names only check 
        #4) Make a boxplot
        x_val2 = scenarios.sce_name.values
        yld_box = px.box(df, x="SNAME", y="HWAM", color="RUN", title="Boxplot du rendement")
        yld_box.add_scatter(x=x_val2, y=TG_yield, mode="markers", 
            marker=dict(color='LightSkyBlue', size=10, line=dict(color='MediumPurple', width=2))) #, mode="lines+markers") #"lines")
        yld_box.update_xaxes(title= "[*Note:Le(s) point(s) LightBlue représente(nt) le(s) rendement(s) simulé(s) en utilisant les conditions météorologiques observées de l'année de plantation]")
        yld_box.update_yaxes(title= "Rendement [kg/ha]")

        yld_exc = go.Figure()
        # for i in x_val:
        for i in x_val3:  #forecast Experiment names only       check 
            x_data = df.HWAM[df["EXPERIMENT"]==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            yld_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode="lines+markers",
                        name=i[4:]))
        # Edit the layout
        yld_exc.update_layout(title="Courbe de dépassement de rendement", #Exceedance Curves of Forecasted Yield for All Scenarios",
                        xaxis_title="Rendement [kg/ha]",
                        yaxis_title="Probabilité de dépassement [-]")
        yld_exc.update_yaxes(range=[0, 1])

        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_yield_first.csv")
        df.to_csv(fname, index=False)  #EJ(7/27/2021) check 
        #print({"label": i, "value": i} for i in list(df_out.columns))
        dic_sname = [{"label": i, "value": i} for i in np.unique(df.SNAME.values)]   #check
        return [
            dcc.Graph(id="yield-boxplot", figure = yld_box, config = graph.config, ), 
            dcc.Graph(id="yield-exceedance", figure = yld_exc, config = graph.config, ),
            dic_sname, #EJ(7/27/2021)
            df.to_dict("records"),   #df_out.to_dict("records"),    #EJ(7/27/2021) check 
        ]
#Last callback to create figures for Enterprise budgeting
@app.callback(Output(component_id="EBbox-container_frst", component_property="children"),
                Output(component_id="EBcdf-container_frst", component_property="children"),
                # Output(component_id="EBtimeseries-container", component_property="children"),
                # Output(component_id="EBtables-container_frst", component_property="children"),
                Output("memory-EB-table_frst", "data"),
                Input("EB-button-state_frst", "n_clicks"),
                State('yield-multiplier_frst', 'value'), #EJ(6/5/2021)
                State("scenario-table_frst","data") ### scenario summary table
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
            run_type = ["Forecast" if x[:2] == 'FC' else "Climatology" for x in EXPERIMENT]  #to distinguish "FC(Forecast)" and "CL (climatology)"  check
            sname = [x[4:] for x in EXPERIMENT]  #scenario name (4 char)
            #Compute gross margin
            # GMargin=HWAM*float(EB_sces.CropPrice[i])- float(EB_sces.NFertCost[i])*NICM - float(EB_sces.SeedCost[i]) - float(EB_sces.OtherVariableCosts[i]) - float(EB_sces.FixedCosts[i])
            GMargin=HWAM*float(EB_sces.CropPrice[i])- float(EB_sces.NFertCost[i])*NICM - float(EB_sces.IrrigCost[i])*IRCM - float(EB_sces.SeedCost[i]) - float(EB_sces.OtherVariableCosts[i]) - float(EB_sces.FixedCosts[i])
  
            # TG_GMargin_temp = np.nan
            # if int(EB_sces.TargetYr[i]) <= int(EB_sces.LastYear[i]):
            #     doy = repr(PDAT[0])[4:]
            #     target = EB_sces.TargetYr[i] + doy
            #     yr_index = np.argwhere(PDAT == int(target))
            #     TG_GMargin_temp = GMargin[yr_index[0][0]]

            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT,"MDAT":MDAT,  "HWAM":HWAM,"NICM":NICM,"IRCM":IRCM, 
                    "GMargin":GMargin, "RUN": run_type, "SNAME": sname,}  #EJ(6/5/2021) fixed
            temp_df = pd.DataFrame (data) #, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM","NICM","GMargin"])  #EJ(6/5/2021) fixed
            
            #In case of hindcast forecasting (i.e., if the planting year is among the observed years
            year1= temp_df.YEAR[temp_df["RUN"] == "Climatology"].values[0]  #first year of the climatolgy run
            year2= temp_df.YEAR[temp_df["RUN"] == "Climatology"].values[-1]  #lats year of the climatolgy run
            target_year = repr(EB_sces.PltDate[i])[1:5]
            if int(target_year) <= year2 and int(target_year) >= year1:
              doy = repr(PDAT[0])[4:]
              target = target_year + doy
              yr_index = np.argwhere(PDAT == int(target))
              TG_GMargin_temp = GMargin[yr_index[0][0]]   
            else:
              TG_GMargin_temp = np.nan #-99  #or np.nan ?
            TG_GMargin = [TG_GMargin_temp]+TG_GMargin   #check

            if i==0:
                df = temp_df.copy()
            else:
                df = temp_df.append(df, ignore_index=True)

            # TG_GMargin = [TG_GMargin_temp]+TG_GMargin
        # adding column name to the respective columns
        df.columns =["EXPERIMENT", "YEAR","PDAT", "ADAT","MDAT", "HWAM","NICM","IRCM","GMargin", "RUN", "SNAME"]
        x_val = np.unique(df.EXPERIMENT.values)
        #1) Make a boxplot
        x_val2 = EB_sces.sce_name.values
        gmargin_box = px.box(df, x="SNAME", y="GMargin", color="RUN", title="Boxplot de la marge brute")
        gmargin_box.add_scatter(x=x_val2, y=TG_GMargin, mode="markers", 
            marker=dict(color='LightSkyBlue', size=10, line=dict(color='MediumPurple', width=2))) #, mode="lines+markers") #"lines")
        gmargin_box.update_xaxes(title= "[*Note:Le(s) point(s) LightBlue représente(nt) la marge brute en utilisant le(s) rendement(s) simulé(s) avec les conditions météorologiques observées au cours de l'année de plantation]")
        gmargin_box.update_yaxes(title= "marge brute[Gross Margin, CFA/ha]")

        gmargin_exc = go.Figure()
        for i in x_val:
            x_data = df.GMargin[df["EXPERIMENT"]==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            gmargin_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode="lines+markers",
                        name=i))
        # Edit the layout
        gmargin_exc.update_layout(title="Courbe de dépassement de la marge brute",
                        xaxis_title="marge brute[CFA/ha]",
                        yaxis_title="Probabilité de dépassement [-]")

        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_Gmargin_frst.csv")
        df.to_csv(fname, index=False)  #EJ(7/27/2021) check 
        return [
            dcc.Graph(id="EB-boxplot", figure = gmargin_box, config = graph.config, ),
            dcc.Graph(id="EB-exceedance", figure = gmargin_exc, config = graph.config, ),
            df.to_dict("records")
            ]

#====================================================================
#Read observed rainfall for two consecutive trimesters in a row 
def Rain_trimester_obs(fname,tri_doylist):  #sname=> scenario name to make a colum of output df
    data1 = np.loadtxt(fname,skiprows=1)
    #convert numpy array to dataframe
    df = pd.DataFrame({"YEAR":data1[:,0].astype(int)//1000,    #python 3.6: / --> //
                    "DOY":data1[:,0].astype(int)%1000,
                    "RAIN":data1[:,4]})

    #===============Remove Feb 29th
    # rain_WTD = df.RAIN.values
    year_WTD = df.YEAR.values
    doy_WTD = df.DOY.values
    #Exclude Feb. 29th in leapyears (60th DOY in a leap year)
    temp_indx = [0 if (calendar.isleap(year_WTD[i])) & (doy_WTD[i] == 60) else 1 for i in range(len(year_WTD))] #[f(x) if condition else g(x) for x in sequence]
    df["leap_indx"]=temp_indx
    df2 = df[df['leap_indx'] > 0]  #drop rows having Feb 29th
    #Make a new DOY column 
    doy_list = []
    yr_list = np.unique(year_WTD)
    for i in range(len(np.unique(year_WTD))):
        temp = df2.leap_indx[df2["YEAR"]== yr_list[i]].values
        doy1 = df2.DOY[df2["YEAR"]== yr_list[i]].values[0] #first doy of the year
        new_doy = (doy1-1) + np.cumsum(temp)
        doy_list = doy_list + list(new_doy) #concatenate two lists

    #drop old DOY column
    df2 = df2.drop(['DOY','leap_indx'], axis=1)
    df2["DOY"]=doy_list  #add a new column with new DOY (rearranged after removing Feb. 29th)
    #===============end of Remove Feb 29th
    #============================================================================================
    #start to compute seasonal sum
    # tri_doylist = trim_dates["JJA"]
    sdoy1 = tri_doylist[0] # starting doy of the target period
    edoy1 = tri_doylist[1]  #ending doy of the target period
    sdoy2 = tri_doylist[2] # starting doy of the target period
    edoy2 = tri_doylist[3]  #ending doy of the target period
    sdoy1_ind = df.DOY[df.DOY == sdoy1].index.tolist()
    edoy1_ind = df.DOY[df.DOY == edoy1].index.tolist()
    sdoy2_ind = df.DOY[df.DOY == sdoy2].index.tolist()
    edoy2_ind = df.DOY[df.DOY == edoy2].index.tolist()

    if sdoy1_ind[0] < edoy2_ind[0]:  #the target season is within a year
        if sdoy1_ind[-1] < edoy2_ind[-1]:  #the target season is within a year
            nyears = len(sdoy1_ind)
            # year_array = df2.YEAR.unique()
        else:  #sdoy1_ind[-1] > edoy2_ind[-1]:  
            nyears = len(sdoy1_ind)-1
            # year_array = df2.YEAR.unique()[:-1]  #ignore last year because it does not have a full season
    elif sdoy1_ind[0] > edoy2_ind[0]:  #the target season goes beyond a year
        if sdoy1_ind[-2] < edoy2_ind[-1]: 
            nyears = len(sdoy1_ind)-1
            # year_array = df2.YEAR.unique()[:-1]
        else:
            nyears = len(sdoy1_ind)-2
            # year_array = df2.YEAR.unique()[:-2]

    #compute seasonal sum
    sum_T1 = []
    sum_T2 = []
    # for i in range(len(sdoy1_ind)):
    for i in range(nyears):
        #1st trimester
        if sdoy1_ind[i] < edoy1_ind[i]:  #last year does not have full season days
            sum_T1.append(np.sum(df.RAIN.iloc[sdoy1_ind[i]:edoy1_ind[i]+1].values))
        elif sdoy1_ind[i] > edoy1_ind[i]:  #last year does not have full season days
            sum_T1.append(np.sum(df.RAIN.iloc[sdoy1_ind[i]:edoy1_ind[i+1]+1].values))

        #2nd trimester    
        if sdoy1_ind[i] < edoy2_ind[i]:  #last year does not have full season days
            if sdoy2_ind[i] < edoy2_ind[i]:  #last year does not have full season days
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i]:edoy2_ind[i]+1].values))
            elif sdoy2_ind[i] > edoy2_ind[i]:  #last year does not have full season days
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i]:edoy2_ind[i+1]+1].values))
        else:  #sdoy1_ind[i] > edoy2_ind[i] => 2nd trimester starts from the 2nd year although data is available (when the first year is incomplete)
            if sdoy2_ind[i] < edoy2_ind[i]:
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i+1]:edoy2_ind[i+1]+1].values))
            elif sdoy2_ind[i] > edoy2_ind[i]:  
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i]:edoy2_ind[i+1]+1].values))        

    data = {"RainT1": np.array(sum_T1), "RainT2": np.array(sum_T2),}
    df_out = pd.DataFrame(data)
    # #write dataframe into CSV file for debugging
    # df_out.to_csv("C:\\IRI\\Dash_ET_forecast\\ET_forecast_windows\\TEST_ET\\trimester_rain_clim.csv", index=False)
    return df_out
#====================================================================
# End of computing seasonal total rainfall of climatology
#====================================================================
#====================================================================
# === Read daily GENERATED rainfall into a dataframe (note: Feb 29th was skipped in df_obs)
def Rain_trimester_gen(fname,tri_doylist):  #sname=> scenario name to make a colum of output df
    #1) Read daily generated weather into a matrix (note: Feb 29th was skipped)
    # WTD_fname = r"C:\IRI\Dash_ET_forecast\ET_forecast_windows\TEST_ETN\aaaa0199.WTH"
    data1 = np.loadtxt(fname,skiprows=5)
    #convert numpy array to dataframe
    df = pd.DataFrame({"YEAR":data1[:,0].astype(int)//1000,    #python 3.6: / --> //
                    "DOY":data1[:,0].astype(int)%1000,
                    "RAIN":data1[:,4]})

    #===============Remove Feb 29th
    # a = df.YEAR[df["DOY"]==1].values
    a = df.YEAR.values
    new_year = [a[i]+100 if a[i] < a[0] else a[i] for i in range(len(a))]
    new_year = np.array(new_year) + 2000
    df["YEAR"] = new_year  #update YEAR column from 2 digit to 4 digit
    # rain_WTD = df.RAIN.values
    year_WTD = df.YEAR.values 

    doy_WTD = df.DOY.values
    #Exclude Feb. 29th in leapyears (60th DOY in a leap year)
    temp_indx = [0 if (calendar.isleap(year_WTD[i])) & (doy_WTD[i] == 60) else 1 for i in range(len(year_WTD))] #[f(x) if condition else g(x) for x in sequence]
    df["leap_indx"]=temp_indx
    df2 = df[df['leap_indx'] > 0]  #drop rows having Feb 29th
    #Make a new DOY column 
    doy_list = []
    yr_list = np.unique(year_WTD)
    for i in range(len(np.unique(year_WTD))):
        temp = df2.leap_indx[df2["YEAR"]== yr_list[i]].values
        doy1 = df2.DOY[df2["YEAR"]== yr_list[i]].values[0] #first doy of the year
        new_doy = (doy1-1) + np.cumsum(temp)
        doy_list = doy_list + list(new_doy) #concatenate two lists

    #drop old DOY column
    df2 = df2.drop(['DOY','leap_indx'], axis=1)
    df2["DOY"]=doy_list  #add a new column with new DOY (rearranged after removing Feb. 29th)
    #===============end of Remove Feb 29th
    #============================================================================================
    #start to compute seasonal sum
    # tri_doylist = trim_dates["JJA"]
    sdoy1 = tri_doylist[0] # starting doy of the target period
    edoy1 = tri_doylist[1]  #ending doy of the target period
    sdoy2 = tri_doylist[2] # starting doy of the target period
    edoy2 = tri_doylist[3]  #ending doy of the target period
    sdoy1_ind = df.DOY[df.DOY == sdoy1].index.tolist()
    edoy1_ind = df.DOY[df.DOY == edoy1].index.tolist()
    sdoy2_ind = df.DOY[df.DOY == sdoy2].index.tolist()
    edoy2_ind = df.DOY[df.DOY == edoy2].index.tolist()

    if sdoy1_ind[0] < edoy2_ind[0]:  #the target season is within a year
        if sdoy1_ind[-1] < edoy2_ind[-1]:  #the target season is within a year
            nyears = len(sdoy1_ind)
            # year_array = df2.YEAR.unique()
        else:  #sdoy1_ind[-1] > edoy2_ind[-1]:  
            nyears = len(sdoy1_ind)-1
            # year_array = df2.YEAR.unique()[:-1]  #ignore last year because it does not have a full season
    elif sdoy1_ind[0] > edoy2_ind[0]:  #the target season goes beyond a year
        if sdoy1_ind[-2] < edoy2_ind[-1]: 
            nyears = len(sdoy1_ind)-1
            # year_array = df2.YEAR.unique()[:-1]
        else:
            nyears = len(sdoy1_ind)-2
            # year_array = df2.YEAR.unique()[:-2]

    #compute seasonal sum
    sum_T1 = []
    sum_T2 = []
    # for i in range(len(sdoy1_ind)):
    for i in range(nyears):
        #1st trimester
        if sdoy1_ind[i] < edoy1_ind[i]:  #last year does not have full season days
            sum_T1.append(np.sum(df.RAIN.iloc[sdoy1_ind[i]:edoy1_ind[i]+1].values))
        elif sdoy1_ind[i] > edoy1_ind[i]:  #last year does not have full season days
            sum_T1.append(np.sum(df.RAIN.iloc[sdoy1_ind[i]:edoy1_ind[i+1]+1].values))

        #2nd trimester    
        if sdoy1_ind[i] < edoy2_ind[i]:  #last year does not have full season days
            if sdoy2_ind[i] < edoy2_ind[i]:  #last year does not have full season days
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i]:edoy2_ind[i]+1].values))
            elif sdoy2_ind[i] > edoy2_ind[i]:  #last year does not have full season days
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i]:edoy2_ind[i+1]+1].values))
        else:  #sdoy1_ind[i] > edoy2_ind[i] => 2nd trimester starts from the 2nd year although data is available (when the first year is incomplete)
            if sdoy2_ind[i] < edoy2_ind[i]:
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i+1]:edoy2_ind[i+1]+1].values))
            elif sdoy2_ind[i] > edoy2_ind[i]:  
                sum_T2.append(np.sum(df.RAIN.iloc[sdoy2_ind[i]:edoy2_ind[i+1]+1].values))        

    data = {"RainT1": np.array(sum_T1), "RainT2": np.array(sum_T2),}
    df_out = pd.DataFrame(data)
    # #write dataframe into CSV file for debugging
    # df_out.to_csv("C:\\IRI\\Dash_ET_forecast\\ET_forecast_windows\\TEST_ET\\trimester_rain_frst.csv", index=False)
    return df_out
#====================================================================
# End of reading observations (WTD file) into a matrix 
#====================================================================