import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pathlib
import re


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

import graph


# from apps.ethiopia import write_SNX
# from apps.ethiopia.write_SNX import writeSNX_main_hist, writeSNX_main_frst 
# from write_SNX import writeSNX_main_hist, writeSNX_main_frst  #EJ(7/26/2021)

sce_col_names=[ "sce_name", "Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","TargetYr",
                "Fert_1_DOY","Fert_1_Kg","Fert_2_DOY","Fert_2_Kg","Fert_3_DOY","Fert_3_Kg","Fert_4_DOY","Fert_4_Kg",
                "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"
]

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
                "Simulation Input",
              ),
            className=" card-header",
            ),

            dbc.Form([ ## INPUT FORM
              html.Div( # SCROLLABLE FORM
                html.Div([ # FORM START
                  dbc.FormGroup([ # Scenario
                    dbc.Label("1) Scenario Name", html_for="sce-name", sm=3, className="p-2", align="start", ),
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
                    dbc.Label("2) Station", html_for="ETstation", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                      id="ETstation",
                      options=[
                        {"label": "Melkasa", "value": "MELK"},
                        {"label": "Mieso", "value": "MEIS"},
                        {"label": "Awassa", "value": "AWAS"},
                        {"label": "Asella", "value": "ASEL"},
                        {"label": "Bako", "value": "BAKO"},
                        {"label": "Mahoni", "value": "MAHO"},
                        {"label": "Kobo", "value": "KOBO"}
                      ],
                      value="MELK",
                      clearable=False,
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Seasonal climate forecast EJ(7/25/2021)
                    dbc.Label("3) Seasonal Climate Forecast", html_for="SCF", sm=3, className="p-0", align="start", ),
                    dbc.Col([
                      html.Div([ # SEASONAL CLIMATE FORECAST
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("1st trimester:", html_for="trimester1", sm=3, className="p-0", align="start", ),
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
                              dbc.Input(type="number", id="AN1", value=0, min="0", max="100", ), #required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="BN1", value=0, min="0", max="100", ), #required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="NN1", value=0, min="0", step="0.1", ), #required="required", ),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("2nd trimester:", html_for="SCF2", sm=3, className="p-2", align="start", ),
                          ),
                          dbc.Col(
                            dbc.Input(type="text", id="trimester2", disabled="disabled"), #required="required", ),
                          ),
                        ],),
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
                              dbc.Input(type="number", id="AN2", value=0, min="0", max="100", step="0.1", ), #required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="BN2", value=0, min="0", max="100", step="0.1", ), #required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="NN2", value=0, min="0", step="0.1", ), #required="required", ),
                            ],),
                          ),
                        ],),
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
                    dbc.Label("3) Crop", html_for="crop-radio", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                      id="crop-radio",
                      options = [
                        {"label": "Maize", "value": "MZ"}, 
                        {"label": "Wheat", "value": "WH"}, 
                        {"label": "Sorghum", "value": "SG"},
                      ],
                      labelStyle = {"display": "inline-block","margin-right": 10},
                      value="MZ",
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Cultivar
                    dbc.Label("4) Cultivar", html_for="cultivar-dropdown", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="cultivar-dropdown", 
                        options=[
                          {"label": "CIMT01 BH540", "value": "CIMT01 BH540-Kassie"},
                          {"label": "CIMT02 MELKASA-1", "value": "CIMT02 MELKASA-Kassi"},
                          {"label": "CIMT17 BH660-FAW-40%", "value": "CIMT17 BH660-FAW-40%"},
                          {"label": "CIMT19 MELKASA2-FAW-40%", "value": "CIMT19 MELKASA2-FAW-40%"},
                          {"label": "CIMT21 MELKASA-LowY", "value": "CIMT21 MELKASA-LowY"},], 
                        value="CIMT19 MELKASA2-FAW-40%",
                        clearable=False,
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  # dbc.FormGroup([ # Start Year
                  #   dbc.Label("5) Start Year", html_for="year1", sm=3, className="p-2", align="start", ),
                  #   dbc.Col([
                  #     dbc.Input(type="number", id="year1", placeholder="YYYY", value="1981", min=1981, max=2018, required="required", ),
                  #     dbc.FormText("(No earlier than 1981)"),
                  #   ],
                  #   className="py-2",
                  #   xl=9,
                  #   ),
                  # ],
                  # row=True
                  # ),
                  # dbc.FormGroup([ # End Year
                  #   dbc.Label("6) End Year", html_for="year2", sm=3, className="p-2", align="start", ),
                  #   dbc.Col([
                  #     dbc.Input(type="number", id="year2", placeholder="YYYY", value="2018", min=1981, max=2018, required="required", ),
                  #     dbc.FormText("(No later than 2018)"),
                  #   ],
                  #   className="py-2",
                  #   xl=9,
                  #   ),
                  # ],
                  # row=True
                  # ),
                  # dbc.FormGroup([ # Year to Highlight
                  #   dbc.Label("7) Year to Highlight", html_for="target-year", sm=3, className="p-2", align="start", ),
                  #   dbc.Col([
                  #     dbc.Input(type="number", id="target-year", placeholder="YYYY", value="2015",min=1981, max=2018, required="required", ),
                  #     dbc.FormText("Type a specific year you remember (e.g., drought year) and want to compare with a full climatology distribution"),
                  #   ],
                  #   className="py-2",
                  #   xl=9,
                  #   ),
                  # ],
                  # row=True
                  # ),
                  dbc.FormGroup([ # Soil Type
                    dbc.Label("8) Soil Type", html_for="ETsoil", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="ETsoil", 
                        options=[
                          {"label": "ETET000010(AWAS,L)", "value": "ETET000010"},
                          {"label": "ETET000_10(AWAS,L, shallow)", "value": "ETET000_10"},
                          {"label": "ETET000011(BAKO,C)", "value": "ETET000011"},
                          {"label": "ETET001_11(BAKO,C,shallow)", "value": "ETET001_11"},
                          {"label": "ETET000018(MELK,L)", "value": "ETET000018"},
                          {"label": "ETET001_18(MELK,L,shallow)", "value": "ETET001_18"},
                          {"label": "ETET000015(KULU,C)", "value": "ETET000015"},
                          {"label": "ETET001_15(KULU,C,shallow)", "value": "ETET001_15"},
                          {"label": "ET00990066(MAHO,C)", "value": "ET00990066"},
                          {"label": "ET00990_66(MAHO,C,shallow)", "value": "ET00990_66"},
                          {"label": "ET00920067(KOBO,CL)", "value": "ET00920067"},
                          {"label": "ET00920_67(KOBO,CL,shallow)", "value": "ET00920_67"},
                          {"label": "ETET000022(MIES, C)", "value": "ETET000022"},
                          {"label": "ETET001_22(MIES, C, shallow", "value": "ETET001_22"},
                        ],
                        value="ETET001_18",
                        clearable=False,
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Initial Soil Water Condition
                    dbc.Label("9) Initial Soil Water Condition", html_for="ini-H2O", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="ini-H2O", 
                        options=[
                          {"label": "30% of AWC", "value": "0.3"},
                          {"label": "50% of AWC", "value": "0.5"},
                          {"label": "70% of AWC", "value": "0.7"},
                          {"label": "100% of AWC", "value": "1.0"},
                        ], 
                        value="0.5",
                        clearable=False,
                      ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Initial NO3 Condition
                    dbc.Label("10) Initial Soil NO3 Condition", html_for="ini-NO3", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="ini-NO3", 
                        options=[
                          {"label": "High(65 N kg/ha)", "value": "H"},
                          {"label": "Low(23 N kg/ha)", "value": "L"},
                        ], 
                        value="L",
                        clearable=False,
                      ),                
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Date
                    dbc.Label("11) Planting Date", html_for="plt-date-picker", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.DatePickerSingle(
                      id="plt-date-picker",
                      min_date_allowed=date(2021, 1, 1),
                      max_date_allowed=date(2021, 12, 31),
                      initial_visible_month=date(2021, 6, 5),
                      display_format="DD/MM/YYYY",
                      date=date(2021, 6, 15),
                      ),
                      dbc.FormText("Only Month and Date are counted"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Density
                    dbc.Label(["12) Planting Density", html.Span(" (plants/m"), html.Sup("2"), html.Span(")"), ], html_for="plt-density", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="plt-density", value=5, min=1, max=300, step=0.1, required="required", ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Fertilizer Application
                    dbc.Label("13) Fertilizer Application", html_for="fert_input", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="fert_input",
                        options=[
                          {"label": "Fertilizer", "value": "Fert"},
                          {"label": "No Fertilizer", "value": "No_fert"},
                        ],
                        labelStyle = {"display": "inline-block","margin-right": 10},
                        value="No_fert",
                      ),

                      html.Div([ # FERTILIZER FORM
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("No.", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.Label("Days After Planting", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.Label("Amount of N [kg/ha]", className="text-center", ),
                          ),
                        ],
                        className="py-3",
                        ),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("1st", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day1", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt1", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("2nd", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day2", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt2", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("3rd", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day3", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt3", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("4th", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day4", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt4", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
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
                  dbc.FormGroup([ # Enterprise Budgeting?
                    dbc.Label("14) Enterprise Budgeting?", html_for="EB_radio", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="EB_radio",
                        options=[
                          {"label": "Yes", "value": "EB_Yes"},
                          {"label": "No", "value": "EB_No"},
                        ],
                        labelStyle = {"display": "inline-block","margin-right": 10},
                        value="EB_No",
                      ),

                      html.Div([ # ENTERPRISE BUDGETING FORM
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Crop Price", html_for="crop-price", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="crop-price", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[ETB/kg]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Fertilizer Price", html_for="fert-cost", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-cost", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[ETB/N kg]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Seed Cost", html_for="seed-cost", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="seed-cost", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[ETB/ha]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Other Variable Costs", html_for="variable-costs", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="variable-costs", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[ETB/ha]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Fixed Costs", html_for="fixed-costs", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fixed-costs", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[ETB/ha]"),
                            ],),
                          ),
                        ],),
                        # Tutorial link here is hardcoded
                        dbc.FormText(
                          html.Span([
                            "See the ",
                            html.A("Tutorial", target="_blank", href="https://sites.google.com/iri.columbia.edu/simagri-ethiopia/simagri-tutorial"),
                            " for more details of calculation"
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

                  # INPUT FORM END
                ], 
                className="p-3"
                ),
              className="overflow-auto",
              style={"height": "63vh"},
              ),
              html.Div([ # SCENARIO TABLE
                html.Header(html.B("Scenarios"), className="card-header",),
                dbc.FormGroup([ # SUBMIT - ADD SCENARIO
                  dbc.Button(id="write-button-state", 
                  n_clicks=0, 
                  children="Create or Add a new Scenario", 
                  className="w-75 d-block mx-auto my-3",
                  color="primary"
                  ),
                ]),
                dash_table.DataTable(
                id="scenario-table",
                columns=([
                    {"id": "sce_name", "name": "Scenario Name"},
                    {"id": "Trimester1", "name": "Trimester1"},  #First trimester e.g., JJA
                    {"id": "AN1", "name": "AN1"},  #AN of the first trimeter
                    {"id": "BN1", "name": "BN1"},  #BN of the first trimester
                    {"id": "AN2", "name": "AN2"},  #AN of the second (following) trimester
                    {"id": "BN2", "name": "BN2"},  #BN of the second (following) trimester
                    {"id": "Crop", "name": "Crop"},
                    {"id": "Cultivar", "name": "Cultivar"},
                    {"id": "stn_name", "name": "Station"},
                    {"id": "Plt-date", "name": "Planting Date"},
                    # {"id": "FirstYear", "name": "First Year"},
                    # {"id": "LastYear", "name": "Last Year"},
                    {"id": "soil", "name": "Soil Type"},
                    {"id": "iH2O", "name": "Initial Soil Water Content"},
                    {"id": "iNO3", "name": "Initial Soil Nitrate Content"},
                    # {"id": "TargetYr", "name": "Target Year"},
                    {"id": "Fert_1_DOY", "name": "DOY 1st Fertilizer Applied"},
                    {"id": "Fert_1_Kg", "name": "1st Amount Applied (Kg/ha)"},
                    {"id": "Fert_2_DOY", "name": "DOY 2nd Fertilizer Applied"},
                    {"id": "Fert_2_Kg", "name": "2nd Amount Applied(Kg/ha)"},
                    {"id": "Fert_3_DOY", "name": "DOY 3rd Fertilizer Applied"},
                    {"id": "Fert_3_Kg", "name": "3rd Amount Applied(Kg/ha)"},
                    {"id": "Fert_4_DOY", "name": "DOY 4th Fertilizer Applied"},
                    {"id": "Fert_4_Kg", "name": "4th Amount Applied(Kg/ha)"},
                    {"id": "CropPrice", "name": "Crop Price"},
                    {"id": "NFertCost", "name": "Fertilizer Cost"},
                    {"id": "SeedCost", "name": "Seed Cost"},
                    {"id": "OtherVariableCosts", "name": "Other Variable Costs"},
                    {"id": "FixedCosts", "name": "Fixed Costs"},
                ]),
                data=[
                    dict(**{param: "N/A" for param in sce_col_names}) for i in range(1, 2)
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
            ]),

            dbc.Form([ # INPUTS AFFECTING ALL SCENARIOS AND RUN DSSAT
              dbc.FormGroup([ # Enterprise Budgeting Yield Adjustment Factor
                dbc.Label("15) Enterprise Budgeting Yield Adjustment Factor", html_for="yield-multiplier", sm=3, className="p-2", align="start", ),
                dbc.Col([
                  dbc.Input(type="number", id="yield-multiplier", value=1, min=0, max=2, step=0.1, required="required", ),
                  dbc.FormText("(e.g., 90% reduction => 0.9)"),
                ],
                className="py-2",
                xl=9,
                ),
              ],
              row=True
              ),
              dbc.FormGroup([ # Approximate Growing Season
                dbc.Label("16) Critical growing period to relate rainfall amount with crop yield", html_for="season-slider"),
                dbc.FormText("Selected period is used to sort drier/wetter years based on the seasonal total rainfall"),
                dcc.RangeSlider(
                  id="season-slider",
                  min=1, max=12, step=1,
                  marks={1: "Jan", 2: "Feb",3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"},
                  value=[6, 9]
                ),
              ],
              ),
              html.Br(),
              html.Div( ## RUN DSSAT BUTTON
                dbc.Button(id="simulate-button-state", 
                children="Simulate all scenarios (Run DSSAT)",
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
                html.B("Simulation Graphs"),
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
                html.B("Download Simulated Yield CSV"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div([
                    html.Div([ # ORIGINAL CSV STUFF
                      dbc.Row([
                        dbc.Col(
                          dbc.Button(id="btn_csv_yield", 
                          children="Simulated Yield", 
                          className="d-block mx-auto",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                        dbc.Col(
                          dbc.Button(id="btn_csv_Pexe", 
                          children="Prob. of Exceedance", 
                          className="d-block mx-auto",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                        dbc.Col(
                          dbc.Button(id="btn_csv_rain", 
                          children="Seasonal Rainfall", 
                          className="d-block mx-auto",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                      ],
                      className="m-1",
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

          html.Div([ # ENTERPRISE BUDGETING
            html.Div([
              html.Header(
                html.B("Enterprise Budgeting"),
              className=" card-header",
              ),
              html.Div([
                html.Br(),
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
                  html.B("Download Enterprise Budgeting CSV"),
                className=" card-header"
                ),
                html.Div([
                  html.Br(),
                  dbc.Button(id="btn_csv_EB", 
                  children="Download", 
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
              ],),
            ]),
          ],
          id="EB-figures",
          style={"display": "none"},
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

DSSAT_PATH_SHORT = "/DSSAT/dssat-base-files"  #for linux systemn

DSSAT_PATH = os.getcwd() + DSSAT_PATH_SHORT   #for linux systemn

#https://community.plotly.com/t/loading-when-opening-localhost/7284
#I suspect that this is related to the JS assets from the CDN not loading properly - perhaps because they are blocked by your firewall or some other reason.
#You can load the assets locally by setting:
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

cultivar_options = {
    "MZ": ["CIMT01 BH540","CIMT02 MELKASA-1","CIMT17 BH660-FAW-40%", "CIMT19 MELKASA2-FAW-40%", "CIMT21 MELKASA-LowY"],
    "WH": ["CI2021 KT-KUB", "CI2022 RMSI", "CI2023 Meda wolabu", "CI2024 Sofumer", "CI2025 Hollandi", "CI2018 ET-MED", "CI2019 ET-LNG"],
    "SG": ["IB0020 ESH-1","IB0020 ESH-2","IB0027 Dekeba","IB0027 Melkam","IB0027 Teshale"]
}

#==============================================================
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
    Output("cultivar-dropdown", "options"),
    Input("crop-radio", "value"))
def set_cultivar_options(selected_crop):
    return [{"label": i, "value": i} for i in cultivar_options[selected_crop]]

@app.callback(
    Output("cultivar-dropdown", "value"),
    Input("cultivar-dropdown", "options"))
def set_cultivar_value(available_options):
    return available_options[0]["value"]

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
    else:
        if existing_sces.empty:
            return {"display": "none"}
        else:
            return {"display": "none"} if existing_sces.sce_name.values[0] == "N/A" or set(existing_sces.CropPrice.values) == {"-99"} else {}

#==============================================================
@app.callback(Output("scenario-table", "data"),
                Input("write-button-state", "n_clicks"),
                State("ETstation", "value"),
                State("trimester1", "value"),
                State("AN1", "value"),
                State("BN1", "value"),
                State("AN2", "value"),
                State("BN2", "value"),
                # State("year1", "value"),
                # State("year2", "value"),
                State("plt-date-picker", "date"),
                State("crop-radio", "value"),
                State("cultivar-dropdown", "value"),
                State("ETsoil", "value"),
                State("ini-H2O", "value"),
                State("ini-NO3", "value"),
                State("plt-density", "value"),
                State("sce-name", "value"),
                # State("target-year", "value"),
                State("fert_input", "value"),
                State("fert-day1","value"),
                State("fert-amt1","value"),
                State("fert-day2","value"),
                State("fert-amt2","value"),
                State("fert-day3","value"),
                State("fert-amt3","value"),
                State("fert-day4","value"),
                State("fert-amt4","value"),
                State("EB_radio", "value"),
                State("crop-price","value"),
                State("seed-cost","value"),
                State("fert-cost","value"),
                State("fixed-costs","value"),
                State("variable-costs","value"),
                State("scenario-table","data")
            )
def make_sce_table(
    n_clicks, station, trimester, AN1, BN1, AN2, BN2, planting_date, crop, cultivar, soil_type, 
    initial_soil_moisture, initial_soil_no3_content, planting_density, scenario, #target_year, 
    fert_app, 
    fd1, fa1,
    fd2, fa2,
    fd3, fa3,
    fd4, fa4,
    EB_radio,
    crop_price,
    seed_cost,
    fert_cost,
    fixed_costs,
    variable_costs,
    sce_in_table
):

    existing_sces = pd.DataFrame(sce_in_table)

    if ( # first check that all required editable inputs have been given
            scenario == None
        # or  start_year == None
        # or  end_year == None
        # or  target_year == None
        or  planting_date == None
        or  planting_density == None
        or (
                fert_app == "Fert"
            and (
                    fd1 == None or fa1 == None
                or  fd2 == None or fa2 == None
                or  fd3 == None or fa3 == None
                or  fd4 == None or fa4 == None
            ) 
        )
        or (
                EB_radio == "EB_Yes"
            and (
                    crop_price == None
                or  seed_cost == None
                or  fert_cost == None
                or  fixed_costs == None
                or  variable_costs == None
            )
        )
    ):
        return existing_sces

    # convert integer inputs to string
    # start_year = str(start_year)
    # end_year = str(end_year)
    # target_year = str(target_year)
    planting_density = str(planting_density)

    # Make a new dataframe to return to scenario-summary table
    current_sce = pd.DataFrame({
        "sce_name": [scenario], "Trimester1": [trimester], "AN1": [AN1],"BN1": [BN1],"AN2": [AN2],"BN2": [BN2],
        "Crop": [crop], "Cultivar": [cultivar[7:]], "stn_name": [station], "Plt-date": [planting_date[5:]], 
         "soil": [soil_type], "iH2O": [initial_soil_moisture], 
        "iNO3": [initial_soil_no3_content], "plt_density": [planting_density], #"TargetYr": [target_year], 
        "Fert_1_DOY": ["-99"], "Fert_1_Kg": ["-99"], "Fert_2_DOY": ["-99"], "Fert_2_Kg": ["-99"], 
        "Fert_3_DOY": ["-99"], "Fert_3_Kg": ["-99"], "Fert_4_DOY": ["-99"], "Fert_4_Kg": ["-99"], 
        "CropPrice": ["-99"], "NFertCost": ["-99"], "SeedCost": ["-99"], "OtherVariableCosts": ["-99"], "FixedCosts": ["-99"]
    })

    #=====================================================================
    # #Update dataframe for fertilizer inputs
    current_fert = pd.DataFrame(columns=["DAP", "NAmount"])
    fert_valid = True
    if fert_app == "Fert":
        current_fert = pd.DataFrame({
            "DAP": [fd1, fd2, fd3, fd4, ],
            "NAmount": [fa1, fa2, fa3, fa4, ],
        })

        fert_frame =  pd.DataFrame({
            "Fert_1_DOY": [fd1], "Fert_1_Kg": [fa1],
            "Fert_2_DOY": [fd2], "Fert_2_Kg": [fa2],
            "Fert_3_DOY": [fd3], "Fert_3_Kg": [fa3],
            "Fert_4_DOY": [fd4], "Fert_4_Kg": [fa4],
        })
        current_sce.update(fert_frame)

        if (
                (fd1 < 0 or 365 < fd1) or fa1 < 0
            or  (fd2 < 0 or 365 < fd2) or fa2 < 0
            or  (fd3 < 0 or 365 < fd3) or fa3 < 0
            or  (fd4 < 0 or 365 < fd4) or fa4 < 0
        ):
            fert_valid = False

    #=====================================================================
    # Write SNX file
    writeSNX_main_hist(DSSAT_PATH,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                        planting_density,scenario,fert_app, current_fert)
    writeSNX_main_frst(DSSAT_PATH,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                        planting_density,scenario,fert_app, current_fert)
    #=====================================================================
    # #Update dataframe for Enterprise Budgeting inputs
    EB_valid = True
    if EB_radio == "EB_Yes":
        EB_frame =  pd.DataFrame({
            "CropPrice": [crop_price],
            "NFertCost": [seed_cost],
            "SeedCost": [fert_cost],
            "OtherVariableCosts": [fixed_costs],
            "FixedCosts": [variable_costs],
        })
        current_sce.update(EB_frame)

        if (
                crop_price < 0
            or  seed_cost < 0
            or  fert_cost < 0
            or  fixed_costs < 0
            or  variable_costs < 0
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
        and int(current_sce.FirstYear.values[0]) >= 1981 and int(current_sce.FirstYear.values[0]) <= 2018
        and int(current_sce.LastYear.values[0]) >= 1981 and int(current_sce.LastYear.values[0]) <= 2018
        and int(current_sce.TargetYr.values[0]) >= 1981 and int(current_sce.TargetYr.values[0]) <= 2018
        and float(current_sce.plt_density.values[0]) >= 1 and float(current_sce.plt_density.values[0]) <= 300
        and planting_date_valid and fert_valid and EB_valid
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
        return data
    else:
        return existing_sces.to_dict("rows")


#===============================
#2nd callback to run ALL scenarios
@app.callback(  # Simulation Figures
                Output(component_id="yieldbox-container", component_property="children"),
                Output(component_id="yieldcdf-container", component_property="children"),
                Output(component_id="yieldtimeseries-container", component_property="children"),
                Output(component_id="yield-BN-container", component_property="children"),
                Output(component_id="yield-NN-container", component_property="children"),
                Output(component_id="yield-AN-container", component_property="children"),
                Output(component_id="yieldtables-container", component_property="children"),
                Output("memory-yield-table", "data"),
                # EB Figures
                Output(component_id="EBbox-container", component_property="children"),
                Output(component_id="EBcdf-container", component_property="children"),
                Output(component_id="EBtimeseries-container", component_property="children"),
                Output(component_id="EBtables-container", component_property="children"),
                Output("memory-EB-table", "data"),
                # Inputs
                Input("simulate-button-state", "n_clicks"),
                State("scenario-table","data"), ### scenario summary table
                State("yield-multiplier", "value"),
                State("season-slider", "value"), #EJ (5/13/2021) for seasonal total rainfall
                prevent_initial_call=True,
              )

def run_create_figure(n_clicks, sce_in_table, multiplier, slider_range):
    if n_clicks is None:
        raise PreventUpdate
        return 
    else: 
        # 1) Read saved scenario summaries and get a list of scenarios to run
        scenarios = pd.DataFrame(sce_in_table)
        sce_numbers = len(scenarios.sce_name.values)
        
        EB_sces = scenarios[scenarios["CropPrice"] != "-99"]
        num_EB_sces = len(EB_sces.sce_name.values)
        if (
                num_EB_sces > 0 
            and (multiplier == None or multiplier < 0 or 2 < multiplier)
        ):
            return [
                # simulation graphs
                html.Div(""),html.Div(""),html.Div(""),html.Div(""),html.Div(""),html.Div(""),html.Div(""),html.Div(""),
                # EB graphs
                html.Div(""),html.Div(""),html.Div(""),html.Div(""),html.Div(""),
            ]

        TG_yield = []
        #EJ(5/3/2021) run DSSAT for each scenarios with individual V47
        #EJ(5/18/2021)variables for extracting seasonal total rainfall
        m1, m2 = slider_range
        m_doys_list = [1,32,60,91,121,152,182,213,244,274,305,335]
        m_doye_list = [31,59,90,120,151,181,212,243,273,304,334,365]
        sdoy = m_doys_list[m1-1]  #first doy of the target season
        edoy = m_doye_list[m2-1]  #last doy of the target season

        for i in range(sce_numbers):
            scenario = scenarios.sce_name.values[i]
            # EJ(5/18/2021) extract seasonal rainfall total
            firstyear = int(scenarios.FirstYear[i])
            lastyear = int(scenarios.LastYear[i])
            WTD_fname = path.join(DSSAT_PATH, scenarios.stn_name[i]+".WTD")
            df_obs = read_WTD(WTD_fname,firstyear, lastyear)  # === Read daily observations into a dataframe (note: Feb 29th was skipped in df_obs)
            df_season_rain = season_rain_rank(df_obs, sdoy, edoy)  #get indices of the sorted years based on SCF1 => df_season_rain.columns = ["YEAR","season_rain", "Rank"]  
            #==============end of # EJ(5/18/2021) extract seasonal rainfall total

            # 2) Write V47 file
            temp_dv7 = path.join(DSSAT_PATH, f"DSSBatch_template_{scenarios.Crop[i]}.V47")

            dv7_fname = path.join(DSSAT_PATH, "DSSBatch.V47")
            fr = open(temp_dv7, "r")  # opens temp DV4 file to read
            fw = open(dv7_fname, "w")
            # read template and write lines
            for line in range(0, 10):
                temp_str = fr.readline()
                fw.write(temp_str)

            temp_str = fr.readline()
            SNX_fname = path.join(DSSAT_PATH, f"ET{scenarios.Crop[i]}{scenario}.SNX")

            new_str2 = "{0:<95}{1:4s}".format(SNX_fname, repr(1).rjust(4)) + temp_str[99:]
            fw.write(new_str2)
            fr.close()
            fw.close()
            #=====================================================================
            #3) Run DSSAT executable
            os.chdir(DSSAT_PATH)  #change directory
            if scenarios.Crop[i] == "WH":
                args = "./dscsm047 CSCER047 B DSSBatch.V47"
            elif scenarios.Crop[i] == "MZ":
                args = "./dscsm047 MZCER047 B DSSBatch.V47"
            else:  # SG
                args = "./dscsm047 SGCER047 B DSSBatch.V47"

            fout_name = f"ET{scenarios.Crop[i]}{scenario}.OSU"
            arg_mv = f"cp Summary.OUT {fout_name}"

            os.system(args) 
            os.system(arg_mv) 
            #===========>end of for linux system

            #4) read DSSAT output => Read Summary.out from all scenario output
            dssat_results=pd.read_csv(fout_name,delim_whitespace=True ,skiprows=3)
            HWAM = dssat_results.iloc[:,20].values  #read 21th column only
            EXPERIMENT = dssat_results.iloc[:,7].values  #read 4th column only
            PDAT = dssat_results.iloc[:,13].values  #read 14th column only
            ADAT = dssat_results.iloc[:,15].values  #read 14th column only
            MDAT = dssat_results.iloc[:,16].values  #read 14th column only    
            YEAR = dssat_results.iloc[:,13].values//1000

            doy = repr(PDAT[0])[4:]
            target = scenarios.TargetYr[i] + doy
            yr_index = np.argwhere(PDAT == int(target))

            TG_yield_temp = HWAM[yr_index[0][0]]

            # Make a new dataframe for plotting
            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT, "HWAM":HWAM,"RAIN":df_season_rain.season_rain.values,"RANK":df_season_rain.Rank.values}
            current_plots = pd.DataFrame (data, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM", "RAIN", "RANK"])

            if i==0:
                all_plots = current_plots.copy()
            else:
                all_plots = current_plots.append(all_plots, ignore_index=True)

            TG_yield = [TG_yield_temp]+TG_yield

        all_plots = all_plots.round({"RAIN": 0})  #Round a DataFrame to a variable number of decimal places.
        yield_min = np.min(all_plots.HWAM.values)  #to make a consistent yield scale for exceedance curve =>Fig 4,5,6
        yield_max = np.max(all_plots.HWAM.values)
        x_val = np.unique(all_plots.EXPERIMENT.values)

        #4) Make a boxplot
        yld_box = px.box(all_plots, x="EXPERIMENT", y="HWAM", title="Yield Boxplot")
        yld_box.add_scatter(x=x_val,y=TG_yield, mode="markers") #, mode="lines+markers") #"lines")
        yld_box.update_xaxes(title= "Scenario Name [*Note:Red dot(s) represents yield(s) based on the weather of target year]")
        yld_box.update_yaxes(title= "Yield [kg/ha]")
        # # return fig

        yld_exc = go.Figure()
        for i in x_val:
            x_data = all_plots.HWAM[all_plots["EXPERIMENT"]==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pall_plots
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            yld_exc.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode="lines+markers",
                        name=i[4:]))
        # Edit the layout
        yld_exc.update_layout(title="Yield Exceedance Curve",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]")

        #make a new dataframe to save into CSV
        yr_val = np.unique(all_plots.YEAR.values)
        df_out = pd.DataFrame({"YEAR":yr_val})

        yld_t_series = go.Figure()
        BN_exc = go.Figure() #yield exceedance curve using only BN category
        NN_exc = go.Figure()  #yield exceedance curve using only NN category
        AN_exc = go.Figure()  #yield exceedance curve using only AN category
        for i in x_val:
            x_data = all_plots.YEAR[all_plots["EXPERIMENT"]==i].values
            y_data = all_plots.HWAM[all_plots["EXPERIMENT"]==i].values
            yield_rank = y_data.argsort().argsort() + 1 #<<<<<<==================
            yield_Pexe = np.around(1-[1.0/len(y_data)] * yield_rank, 2) #<<<<<<=====probability of exceedance,  round to the given number of decimals.
            rain_data = all_plots.RAIN[all_plots["EXPERIMENT"]==i].values  # EJ(5/18/2021) seasonal rainfall total
            rain_rank = all_plots.RANK[all_plots["EXPERIMENT"]==i].values  # EJ(5/18/2021) rank of seasonal rainfall total

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
        yld_t_series.update_layout(title="Yield Time-Series",
                        xaxis_title="Year",
                        yaxis_title="Yield [kg/ha]")
        BN_exc.update_layout(title="Yield Exceedance [Dry category]",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        BN_exc.update_xaxes(range=[yield_min, yield_max])
        NN_exc.update_layout(title="Yield Exceedance [Normal category]",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        NN_exc.update_xaxes(range=[yield_min, yield_max])
        AN_exc.update_layout(title="Yield Exceedance [Wet category]",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        AN_exc.update_xaxes(range=[yield_min, yield_max])

        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(DSSAT_PATH, "simulated_yield.csv")
        df_out.to_csv(fname, index=False)
        #print({"label": i, "value": i} for i in list(df_out.columns))

        # EB Figures:
        TG_GMargin = []

        #EJ(5/3/2021) Read DSSAT output for each scenarios
        EB_df = pd.DataFrame (data, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM","NICM","GMargin"])
        for i in range(num_EB_sces):
            os.chdir(DSSAT_PATH)  #change directory  #check if needed or not
            sname = EB_sces.sce_name.values[i]
            fout_name = f"ET{EB_sces.Crop[i]}{sname}.OSU"

            df_OUT=pd.read_csv(fout_name,delim_whitespace=True ,skiprows=3)
            HWAM = df_OUT.iloc[:,20].values  #read 21th column only
            HWAM = np.multiply(HWAM, float(multiplier)) #EJ(6/5/2021) added multiplier
            EXPERIMENT = df_OUT.iloc[:,7].values  #read 4th column only
            PDAT = df_OUT.iloc[:,13].values  #read 14th column only
            ADAT = df_OUT.iloc[:,15].values  #read 14th column only
            MDAT = df_OUT.iloc[:,16].values  #read 14th column only    
            YEAR = df_OUT.iloc[:,13].values//1000
            HWAM = np.multiply(HWAM, float(multiplier))
            HWAM[HWAM < 0]=0 #==> if HWAM == -99, consider it as "0" yield (i.e., crop failure)
            NICM = dssat_results.iloc[:,39].values  #read 40th column only,  #NICM   Tot N app kg/ha Inorganic N applied (kg [N]/ha)
            #Compute gross margin
            GMargin=HWAM*float(EB_sces.CropPrice[i])- float(EB_sces.NFertCost[i])*NICM - float(EB_sces.SeedCost[i]) - float(EB_sces.OtherVariableCosts[i]) - float(EB_sces.FixedCosts[i])
            # GMargin_data[0:len(HWAM),x]

            TG_GMargin_temp = np.nan
            if int(EB_sces.TargetYr[i]) <= int(EB_sces.LastYear[i]):
                doy = repr(PDAT[0])[4:]
                target = EB_sces.TargetYr[i] + doy
                yr_index = np.argwhere(PDAT == int(target))
                TG_GMargin_temp = GMargin[yr_index[0][0]]

            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT, "HWAM":HWAM,"NICM":NICM, "GMargin":GMargin}  #EJ(6/5/2021) fixed
            EB_temp_df = pd.DataFrame (data, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM","NICM","GMargin"])  #EJ(6/5/2021) fixed

            if i==0:
                EB_df = EB_temp_df.copy()
            else:
                EB_df = EB_df.append(EB_temp_df, ignore_index=True)

            TG_GMargin.append(TG_GMargin_temp)

        # adding column name to the respective columns
        EB_df.columns =["EXPERIMENT", "YEAR","PDAT", "ADAT","HWAM","NICM","GMargin"]
        x_val = np.unique(EB_df.EXPERIMENT.values)
        EB_box = px.box(EB_df, x="EXPERIMENT", y="GMargin", title="Gross Margin Boxplot")
        EB_box.add_scatter(x=x_val,y=TG_GMargin, mode="markers") #, mode="lines+markers") #"lines")
        EB_box.update_xaxes(title= "Scenario Name")
        EB_box.update_yaxes(title= "Gross Margin[Birr/ha]")

        EB_cdf = go.Figure()
        for i in x_val:
            x_data = EB_df.GMargin[EB_df["EXPERIMENT"]==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            EB_cdf.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode="lines+markers",
                        name=i))
        # Edit the layout
        EB_cdf.update_layout(title="Gross Margin Exceedance Curve",
                        xaxis_title="Gross Margin[Birr/ha]",
                        yaxis_title="Probability of Exceedance [-]")

        #make a new dataframe to save into CSV
        yr_val = np.unique(EB_df.YEAR.values)
        EB_df_out = pd.DataFrame({"YEAR":yr_val})

        EB_tseries = go.Figure()
        for i in x_val:
            x_data = EB_df.YEAR[EB_df["EXPERIMENT"]==i].values
            y_data = EB_df.GMargin[EB_df["EXPERIMENT"]==i].values
            y_data = y_data.astype(int) #EJ(6/5/2021)

            ##make a new dataframe to save into CSV
            df_temp = pd.DataFrame({i:y_data})
            EB_df_out = pd.concat([EB_df_out, df_temp], axis=1)

            EB_tseries.add_trace(go.Scatter(x=x_data, y=y_data,
                        mode="lines+markers",
                        name=i))
        # Edit the layout
        EB_tseries.update_layout(title="Gross Margin Time-Series",
                        xaxis_title="Year",
                        yaxis_title="Gross Margin[Birr/ha]")
        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(DSSAT_PATH, "simulated_yield_GMargin.csv")
        EB_df_out.to_csv(fname, index=False)

        return [
            # Simulations
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
            # EB
            dcc.Graph(id="EB-boxplot", figure = EB_box, config = graph.config, ),
            dcc.Graph(id="EB-exceedance", figure = EB_cdf, config = graph.config, ),
            dcc.Graph(id="EB-ts", figure = EB_tseries, config = graph.config, ),
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in EB_df_out.columns],
                data=EB_df_out.to_dict("records"),
                style_cell={"whiteSpace": "normal","height": "auto",},),
            EB_df_out.to_dict("records")
        ]
#==============================================================
@app.callback(
    Output("column-dropdown", "value"),
    Input("column-dropdown", "options"))
def set_column_value(available_options):
    return [available_options[i]["value"] for i in range(len(available_options))]

# =============================================
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
    #write dataframe into CSV file for debugging
    df_season_rain.to_csv("C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\df_season_rain.csv", index=False)
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