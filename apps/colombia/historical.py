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
import bisect   # an element into sorted list

import graph

sce_col_names=[ "sce_name", "Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","TargetYr",
                "Fert_1_DOY","N_1_Kg", "Fert_2_DOY","N_2_Kg","Fert_3_DOY","N_3_Kg",
                "Fert_4_DOY","N_4_Kg","IR_1_DOY", "IR_1_amt","IR_2_DOY", "IR_2_amt","IR_3_DOY","IR_3_amt",
                "IR_4_DOY","IR_4_amt","IR_5_DOY","IR_5_amt","AutoIR_depth","AutoIR_thres", "AutoIR_eff",
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
                    dbc.Label("1) Scenario Name", html_for="sce-name", sm=3, align="start", ),
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
                      options=[
                        {"label": "Cerete", "value": "CTUR"},
                        {"label": "Espinal", "value": "CNAT"},
                        {"label": "La Union", "value": "CUNI"},
                        {"label": "Cucharo El", "value": "CUCH"},
                        {"label": "Esc Agr Mogotes", "value": "EAMO"},
                        {"label": "Zapatoca", "value": "ZAPA"},
                      ],
                      value="CTUR",
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
                    dbc.Label("3) Crop", html_for="crop-radio", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                      id="crop-radio",
                      # options=[{"label": k, "value": k} for k in cultivar_options.keys()],
                      options = [
                        {"label": "Drybean", "value": "BN"},
                        {"label": "Maize", "value": "MZ"},
                      ],
                      labelStyle = {"display": "inline-block","marginRight": 10},
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
                    dbc.Label("4) Cultivar", html_for="cultivar-dropdown", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="cultivar-dropdown",
                        options=[
                          {"label": "CI0002 DK234", "value": "CI0002 DK234"},
                          {"label": "CI0003 FNC3056", "value": "CI0003 FNC3056"},
                          {"label": "CI0004 DK7088", "value": "CI0004 DK7088"},
                          {"label": "CI0001 P30F35", "value": "CI0001 P30F35"},],
                        value="CI0002 DK234",
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
                    dbc.Label("5) Start Year", html_for="year1", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="year1", placeholder="YYYY", value="1980", min=1980, max=2015, required="required", ),
                      dbc.FormText("(No earlier than 1980)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # End Year
                    dbc.Label("6) End Year", html_for="year2", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="year2", placeholder="YYYY", value="2015", min=1980, max=2015,   required="required", ),
                      dbc.FormText("(No later than 2015)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Year to Highlight
                    dbc.Label("7) Year to Highlight", html_for="target-year", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="target-year", placeholder="YYYY", value="2015",min=1980, max=2018,   required="required", ),
                      dbc.FormText("Type a specific year you remember (e.g., drought year) and want to compare with a full climatology distribution"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Soil Type
                    dbc.Label("8) Soil Type", html_for="COsoil", sm=3, align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="COsoil",
                        options=[
                          {"label": "CCCereteC1(SICL)", "value": "CCCereteC1"},
                          {"label": "CCCienaga0(SIC)", "value": "CCCienaga0"},
                          {"label": "CCCienaga1(SIC)", "value": "CCCienaga1"},
                          {"label": "CCCienaga2(SIC)", "value": "CCCienaga2"},
                          {"label": "CCTolima01(SL)", "value": "CCTolima01"},
                          {"label": "CCBuga0001(SL)", "value": "CCBuga0001"},
                          {"label": "CCBuga2013(CL)", "value": "CCBuga2013"},
                          {"label": "CCBuga2014(CL)", "value": "CCBuga2014"},
                          {"label": "CCEspi2013(SL)", "value": "CCEspi2013"},
                          {"label": "CCEspi2014(SL)", "value": "CCEspi2014"},
                          {"label": "CCCere2013(SICL)", "value": "CCCere2013"},
                          {"label": "CCCere2014(SICL)", "value": "CCCere2014"},
                        ],
                        value="CCCereteC1",
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
                    dbc.Label("9) Initial Soil Water Condition", html_for="ini-H2O", sm=3, align="start", ),
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
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Initial NO3 Condition
                    dbc.Label(["10) Initial Soil NO3 Condition", html.Span("  ([N kg/ha] in top 30cm soil)"), ],html_for="ini-NO3", sm=3, align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="ini-NO3", value="20.1",min=1, max=150, step=0.1, required="required", ),
                      dbc.FormText("[Reference] Low Nitrate: 20 N kg/ha (~ 4.8 ppm), High Nitrate: 85 N kg/ha (~20 ppm)"),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Date
                    dbc.Label("11) Planting Date", html_for="plt-date-picker", sm=3, align="start", ),
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
                    dbc.Label(["12) Planting Density", html.Span(" (plants/m"), html.Sup("2"), html.Span(")"), ], html_for="plt-density", sm=3, align="start", ),
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
                    dbc.Label("13) N Fertilizer Application", html_for="fert_input", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="fert_input",
                        options=[
                          {"label": "Fertilizer", "value": "Fert"},
                          {"label": "No Fertilizer", "value": "No_fert"},
                        ],
                        labelStyle = {"display": "inline-block","marginRight": 10},
                        value="No_fert",
                      ),
                      html.Div([ # FERTILIZER INPUT TABLE
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("No.", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.Label("Days After Planting", className="text-center", ),
                          ),
                          # dbc.Col(
                          #   dbc.Label("Depth(cm)", className="text-center", ),
                          # ),
                          dbc.Col(
                            dbc.Label("N (kg/ha)", className="text-center", ),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("1st", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day1", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          # dbc.Col(
                          #   dbc.FormGroup([
                          #     # dbc.Label("1st", html_for="depth1", ),
                          #     dbc.Input(type="number", id="depth1", value=0, min="0", step="0.1", required="required", ),
                          #   ],),
                          # ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="N-amt1", value=0, min="0", step="0.1", required="required", ),
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
                          # dbc.Col(
                          #   dbc.FormGroup([
                          #     # dbc.Label("2nd", html_for="depth2", ),
                          #     dbc.Input(type="number", id="depth2", value=0, min="0", step="0.1", required="required", ),
                          #   ],),
                          # ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="N-amt2", value=0, min="0", step="0.1", required="required", ),
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
                          # dbc.Col(
                          #   dbc.FormGroup([
                          #     # dbc.Label("3rd", html_for="depth3", ),
                          #     dbc.Input(type="number", id="depth3", value=0, min="0", step="0.1", required="required", ),
                          #   ],),
                          # ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="N-amt3", value=0, min="0", step="0.1", required="required", ),
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
                          # dbc.Col(
                          #   dbc.FormGroup([
                          #     # dbc.Label("4th", html_for="depth4", ),
                          #     dbc.Input(type="number", id="depth4", value=0, min="0", step="0.1", required="required", ),
                          #   ],),
                          # ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="N-amt4", value=0, min="0", step="0.1", required="required", ),
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
                  dbc.FormGroup([ # Irrigation
                    dbc.Label("15) Irrigation", html_for="irrig_input", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="irrig_input",
                        options=[
                          {"label": " No irrigation", "value": "No_irrig"},
                          {"label": " On Reported Dates", "value": "repr_irrig"},
                          {"label": " Automatic when required", "value": "auto_irrig"}
                        ],
                        labelStyle = {"display": "block","marginRight": 10},
                        value="No_irrig",
                      ),
                      html.Div([
                        html.Div([ # "on reported dates"
                          #irrigation method
                          dbc.Label("Irrigation method", html_for="extr_P", align="start", ),
                          dcc.Dropdown(
                            id="ir_method",
                            options=[
                              {"label": "Sprinkler", "value": "IR004"},
                              {"label": "Furrow", "value": "IR001"},
                              {"label": "Flood", "value": "IR001"},
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
                                dbc.Label("Days After Planting", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.Label("Amount of Water [mm]", className="text-center", ),
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
                                  # dbc.Label("1st", html_for="irrig-day1", ),
                                  dbc.Input(type="number", id="irrig-day1", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("1st", html_for="irrig-mt1", ),
                                  dbc.Input(type="number", id="irrig-amt1", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("2nd", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("2nd", html_for="irrig-day2", ),
                                  dbc.Input(type="number", id="irrig-day2", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("2nd", html_for="irrig-amt2", ),
                                  dbc.Input(type="number", id="irrig-amt2", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("3rd", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("3rd", html_for="irrig-day3", ),
                                  dbc.Input(type="number", id="irrig-day3", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("3rd", html_for="irrig-amt3", ),
                                  dbc.Input(type="number", id="irrig-amt3", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("4th", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("4th", html_for="irrig-day4", ),
                                  dbc.Input(type="number", id="irrig-day4", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("4th", html_for="irrig-amt4", ),
                                  dbc.Input(type="number", id="irrig-amt4", value=0, min="0", step="0.1", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.Col(
                                dbc.Label("5th", className="text-center", ),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("5th", html_for="irrig-day5", ),
                                  dbc.Input(type="number", id="irrig-day5", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("5th", html_for="irrig-amt5", ),
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
                              dbc.Label("Management soil depth", html_for="ir_depth", ),
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
                              dbc.Label("Threshold", html_for="ir_threshold", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_threshold", value=50, min=1, max=100, step=0.1, required="required", ),
                              dbc.FormText("(% of max available water trigging irrigation)"),
                            ],),
                          ],
                          className="py-2",
                          ),
                          dbc.Row([  #efficiency fraction
                            dbc.Col(
                              dbc.Label("Irrigation efficiency fraction", html_for="ir_eff", ),
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
                    dbc.Label("16) Enterprise Budgeting?", html_for="EB_radio", sm=3, align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="EB_radio",
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
                            dbc.Label("Crop Price", html_for="crop-price", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="crop-price", value="0", min="0", step="0.1", required="required", ),
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
                              dbc.Input(type="number", id="fert-cost", value="0", min="0", step="0.1", required="required", ),
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
                              dbc.Input(type="number", id="seed-cost", value="0", min="0", step="0.1", required="required", ),
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
                              dbc.Input(type="number", id="variable-costs", value="0", min="0", step="0.1", required="required", ),
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
                              dbc.Input(type="number", id="fixed-costs", value="0", min="0", step="0.1", required="required", ),
                              dbc.FormText("[ETB/ha]"),
                            ],),
                          ),
                        ],),
                        # Tutorial link here is hardcoded
                        dbc.FormText(
                          html.Span([
                            "See the ",
                            html.A("Tutorial", target="_blank", href="https://sites.google.com/iri.columbia.edu/simagri-colombia/simagri-tutorial"),
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
                    {"id": "Crop", "name": "Crop"},
                    {"id": "Cultivar", "name": "Cultivar"},
                    {"id": "stn_name", "name": "Station"},
                    {"id": "Plt-date", "name": "Planting Date"},
                    {"id": "FirstYear", "name": "First Year"},
                    {"id": "LastYear", "name": "Last Year"},
                    {"id": "soil", "name": "Soil Type"},
                    {"id": "iH2O", "name": "Initial H2O"}, #"Initial Soil Water Content"},
                    {"id": "iNO3", "name": "Initial NO3"}, #"Initial Soil Nitrate Content"},
                    {"id": "TargetYr", "name": "Target Yr"},
                    {"id": "Fert_1_DOY", "name": "FDOY(1)"},
                    {"id": "N_1_Kg", "name": "N(Kg/ha)(1)"},
                    {"id": "Fert_2_DOY", "name": "FDOY(2)"},
                    {"id": "N_2_Kg", "name": "N(Kg/ha)(2)"},
                    {"id": "Fert_3_DOY", "name": "FDOY(3)"},
                    {"id": "N_3_Kg", "name": "N(Kg/ha)(3)"},
                    {"id": "Fert_4_DOY", "name": "FDOY(4)"},
                    {"id": "N_4_Kg", "name": "N(Kg/ha)(4)"},
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

            html.Div([ # AFTER SCENARIO TABLE
              dbc.FormGroup([ # Approximate Growing Season
                dbc.Label("17) Critical growing period to relate rainfall amount with crop yield", html_for="season-slider"),
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
                html.B("Enterprise Budgeting"),
              className=" card-header",
              ),
              html.Div([
                dbc.Form([ # EB FIGURES
                  dbc.FormGroup([ # Enterprise Budgeting Yield Adjustment Factor
                    dbc.Label("Enterprise Budgeting Yield Adjustment Factor", html_for="yield-multiplier", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="yield-multiplier", value=1, min=0, max=2, step=0.1, required="required", ),
                      dbc.FormText("Enter a multiplier to account for a margin of error."),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.Button(id="EB-button-state", 
                  children="Display figures for Enterprise Budgets", 
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
    "BN": ["IF2011 CALIMA","IB2011 JAMAPA","IB0028 Jatu Rong","IB0094 Perola_Alex"],
    "MZ": ["CI0002 DK234","CI0003 FNC3056","CI0004 DK7088", "CI0001 P30F35"]
}
soil_options = {
    "BN": ["CCCereteC1(SICL)","CCCienaga0(SIC)","CCCienaga1(SIC)",
          "CCCienaga2(SIC)","CCTolima01(SL)","CCBuga0001(SL)","CCBuga2013(CL)",
          "CCBuga2014(CL)","CCEspi2013(SL)","CCEspi2014(SL)","CCCere2013(SICL)","CCCere2014(SICL)"],
    "MZ": ["CCCereteC1(SICL)","CCCienaga0(SIC)","CCCienaga1(SIC)",
          "CCCienaga2(SIC)","CCTolima01(SL)","CCBuga0001(SL)","CCBuga2013(CL)",
          "CCBuga2014(CL)","CCEspi2013(SL)","CCEspi2014(SL)","CCCere2013(SICL)","CCCere2014(SICL)"]
}

Wdir_path = DSSAT_FILES_DIR    #for linux systemn

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
#=============================================================
#Dynamic call back for different soils for a selected target crop
@app.callback(
    Output("COsoil", "options"),
    Input("crop-radio", "value"))
def set_soil_options(selected_crop):
    return [{"label": i, "value": i} for i in soil_options[selected_crop]]

@app.callback(
    Output("COsoil", "value"),
    Input("COsoil", "options"))
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
#============end of EJ(6/7/2021)
#=================================================
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
        if existing_sces.sce_name.values[0] == "N/A" or set(existing_sces.CropPrice.values) == {"-99"}:
            return {"display": "none"}
        else:
            return {}

#==============================================================
@app.callback(Output("scenario-table", "data"),
                Input("write-button-state", "n_clicks"),
                State("SNstation", "value"),
                State("year1", "value"),
                State("year2", "value"),
                State("plt-date-picker", "date"),
                State("crop-radio", "value"),
                State("cultivar-dropdown", "value"),
                State("COsoil", "value"),
                State("ini-H2O", "value"),
                State("ini-NO3", "value"),
                State("plt-density", "value"),
                State("sce-name", "value"),
                State("target-year", "value"),
                State("fert_input", "value"),
                State("fert-day1","value"),
                State("N-amt1","value"),
                State("fert-day2","value"),
                State("N-amt2","value"),
                State("fert-day3","value"),
                State("N-amt3","value"),
                State("fert-day4","value"),
                State("N-amt4","value"),
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
                State("fixed-costs","value"),
                State("variable-costs","value"),
                State("scenario-table","data")
            )
def make_sce_table(
    n_clicks, station, start_year, end_year, planting_date, crop, cultivar, soil_type,
    initial_soil_moisture, initial_soil_no3, planting_density, scenario, target_year,
    fert_app,
    fd1, fN1,
    fd2, fN2,
    fd3, fN3,
    fd4, fN4,
    irrig_app,
    irrig_method,
    #on reported date
    ird1, iramt1,
    ird2, iramt2,
    ird3, iramt3,
    ird4, iramt4,
    ird5, iramt5,
    #automatic when required
    ir_depth,ir_threshold, ir_eff,
    #EB
    EB_radio,
    crop_price,
    seed_cost,
    fert_cost,
    fixed_costs,
    variable_costs,
    sce_in_table
):

    existing_sces = pd.DataFrame(sce_in_table)

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
                    fd1 == None or fN1 == None
                or  fd2 == None or fN2 == None
                or  fd3 == None or fN3 == None
                or  fd4 == None or fN4 == None
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
                or  fixed_costs == None
                or  variable_costs == None
            )
        )
    ):
        return existing_sces

    # convert integer inputs to string
    start_year = str(start_year)
    end_year = str(end_year)
    target_year = str(target_year)
    planting_density = str(planting_density)

    # Make a new dataframe to return to scenario-summary table
    current_sce = pd.DataFrame({
        "sce_name": [scenario], "Crop": [crop], "Cultivar": [cultivar[7:]], "stn_name": [station], "Plt-date": [planting_date[5:]],
        "FirstYear": [start_year], "LastYear": [end_year], "soil": [soil_type], "iH2O": [initial_soil_moisture],
        "iNO3": [initial_soil_no3], "plt_density": [planting_density], "TargetYr": [target_year],
        "Fert_1_DOY": ["-99"], "N_1_Kg": ["-99"],
        "Fert_2_DOY": ["-99"], "N_2_Kg": ["-99"],
        "Fert_3_DOY": ["-99"], "N_3_Kg": ["-99"],
        "Fert_4_DOY": ["-99"], "N_4_Kg": ["-99"],
        "IR_method": ["-99"], 
        #Irrigation on reported date
        "IR_1_DOY": ["-99"], "IR_1_amt": ["-99"],
        "IR_2_DOY": ["-99"], "IR_2_amt": ["-99"],
        "IR_3_DOY": ["-99"], "IR_3_amt": ["-99"],
        "IR_4_DOY": ["-99"], "IR_4_amt": ["-99"],
        "IR_5_DOY": ["-99"], "IR_5_amt": ["-99"],
        #Irrigation automatic
        "AutoIR_depth":  ["-99"], "AutoIR_thres": ["-99"], "AutoIR_eff": ["-99"],
        "CropPrice": ["-99"], "NFertCost": ["-99"], "SeedCost": ["-99"], "OtherVariableCosts": ["-99"], "FixedCosts": ["-99"],
    })

    #=====================================================================
    # #Update dataframe for fertilizer inputs
    fert_valid = True
    current_fert = pd.DataFrame(columns=["DAP", "FDEP", "NAmount"]) #, "PAmount", "KAmount"])
    if fert_app == "Fert":
        current_fert = pd.DataFrame({
            "DAP": [fd1, fd2, fd3, fd4, ],
            "NAmount": [fN1, fN2, fN3, fN4, ],
        })

        fert_frame =  pd.DataFrame({
            "Fert_1_DOY": [fd1], "N_1_Kg": [fN1],
            "Fert_2_DOY": [fd2], "N_2_Kg": [fN2],
            "Fert_3_DOY": [fd3], "N_3_Kg": [fN3],
            "Fert_4_DOY": [fd4], "N_4_Kg": [fN4],
        })
        current_sce.update(fert_frame)
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
                        planting_density,scenario,fert_app, current_fert, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
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
        and int(current_sce.FirstYear.values[0]) >= 1980 and int(current_sce.FirstYear.values[0]) <= 2018
        and int(current_sce.LastYear.values[0]) >= 1980 and int(current_sce.LastYear.values[0]) <= 2018
        and int(current_sce.TargetYr.values[0]) >= 1980 and int(current_sce.TargetYr.values[0]) <= 2018
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
        return data
    else:
        return existing_sces.to_dict("rows")


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
            # SNX_fname = path.join(Wdir_path, "ETMZ{scenario}.SNX")
            SNX_fname = path.join(Wdir_path, f"CO{scenarios.Crop[i]}{scenario}.SNX")

            # On Linux system, we don"t need to do this:
            # SNX_fname = SNX_fname.replace("/", "\\")
            new_str2 = "{0:<95}{1:4s}".format(SNX_fname, repr(1).rjust(4)) + temp_str[99:]
            fw.write(new_str2)
            fr.close()
            fw.close()
            #=====================================================================
            #3) Run DSSAT executable
            os.chdir(Wdir_path)  #change directory  #check if needed or not
            if scenarios.Crop[i] == "BN":
                args = "./dscsm047 CRGRO047 B DSSBatch.V47"
                # args = "./DSCSM047.EXE CRGRO047 B DSSBatch.V47"
                # args = "./dscsm047 B DSSBatch.V47"
            else: # scenarios.Crop[i] == "MZ":
                args = "./dscsm047 MZCER047 B DSSBatch.V47"
                # args = "./DSCSM047.EXE MZCER047 B DSSBatch.V47"
            fout_name = f"CO{scenarios.Crop[i]}{scenario}.OSU"
            arg_mv = f"mv Summary.OUT {fout_name}"
            
            print("!!BEFORE run DSSAT!!") ## DSSAT NOT EXECUTING WELL
            os.system(args)
            os.system(arg_mv)
            print("!!AFTER run DSSAT!!")
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
        yld_box = px.box(df, x="EXPERIMENT", y="HWAM", title="Yield Boxplot")
        yld_box.add_scatter(x=x_val,y=TG_yield, mode="markers") #, mode="lines+markers") #"lines")
        yld_box.update_xaxes(title= "Scenario Name [*Note:Red dot(s) represents yield(s) based on the weather of target year]")
        yld_box.update_yaxes(title= "Yield [kg/ha]")

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
        yld_exc.update_layout(title="Yield Exceedance Curve",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]")

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
        fname = path.join(Wdir_path, "simulated_yield.csv")
        df_out.to_csv(fname, index=False)
        #print({"label": i, "value": i} for i in list(df_out.columns))

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
        current_sces = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        EB_sces = current_sces[current_sces["CropPrice"] != "-99"]
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
            fout_name = path.join(Wdir_path, f"CO{EB_sces.Crop[i]}"+sname+".OSU")
            
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
            HWAM[HWAM < 0]=0 #==> if HWAM == -99, consider it as "0" yield (i.e., crop failure)
            #Compute gross margin
            GMargin=HWAM*float(EB_sces.CropPrice[i])- float(EB_sces.NFertCost[i])*NICM - float(EB_sces.SeedCost[i]) - float(EB_sces.OtherVariableCosts[i]) - float(EB_sces.FixedCosts[i])

            TG_GMargin_temp = np.nan
            if int(EB_sces.TargetYr[i]) <= int(EB_sces.LastYear[i]):
                doy = repr(PDAT[0])[4:]
                target = EB_sces.TargetYr[i] + doy
                yr_index = np.argwhere(PDAT == int(target))
                TG_GMargin_temp = GMargin[yr_index[0][0]]

            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT, "HWAM":HWAM,"NICM":NICM, "GMargin":GMargin}  #EJ(6/5/2021) fixed
            temp_df = pd.DataFrame (data, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM","NICM","GMargin"])  #EJ(6/5/2021) fixed

            if i==0:
                df = temp_df.copy()
            else:
                df = temp_df.append(df, ignore_index=True)

            TG_GMargin = [TG_GMargin_temp]+TG_GMargin

        # adding column name to the respective columns
        df.columns =["EXPERIMENT", "YEAR","PDAT", "ADAT","HWAM","NICM","GMargin"]
        x_val = np.unique(df.EXPERIMENT.values)
        fig = px.box(df, x="EXPERIMENT", y="GMargin", title="Gross Margin Boxplot")
        fig.add_scatter(x=x_val,y=TG_GMargin, mode="markers") #, mode="lines+markers") #"lines")
        fig.update_xaxes(title= "Scenario Name")
        fig.update_yaxes(title= "Gross Margin[Birr/ha]")

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
        fig2.update_layout(title="Gross Margin Exceedance Curve",
                        xaxis_title="Gross Margin[Birr/ha]",
                        yaxis_title="Probability of Exceedance [-]")

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
        fig3.update_layout(title="Gross Margin Time-Series",
                        xaxis_title="Year",
                        yaxis_title="Gross Margin[Birr/ha]")
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
                        irrig_app, irrig_method, df_irrig, ir_depth,ir_threshold, ir_eff):

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
    temp_snx = path.join(Wdir_path, f"CO{crop}TEMP.SNX")
    snx_name = f"CO{crop}"+scenario[:4]+".SNX"

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
    # if p_sim == "P_yes":  #EJ(7/8/2021) Addd Soil Analysis section if P is simulated
    #   SA = "1"
    # else:
    #   SA = "0"
    SA = "0"
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
    SOL_file = path.join(Wdir_path, "CC.SOL")
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

    # #EJ(7/8/2021) Addd Soil Analysis section if P is simulated
    # if p_sim == "P_yes":
    #   fw.write('*SOIL ANALYSIS'+ "\n")
    #   fw.write('@A SADAT  SMHB  SMPX  SMKE  SANAME'+ "\n")
    #   fw.write(' 1 '+ ICDAT + ' SA011 SA002 SA014  -99'+ "\n")
    #   fw.write('@A  SABL  SADM  SAOC  SANI SAPHW SAPHB  SAPX  SAKE  SASC'+ "\n")
    #   soil_depth, SADM, SAOC, SANI, SAPHW = get_soil_SA(SOL_file, ID_SOIL)
    #   if p_level == 'V':  #very low
    #     SAPX = '   2.0'
    #   elif p_level == 'L':  #Low
    #     SAPX = '   7.0'
    #   elif p_level == 'M':  #Medium
    #     SAPX = '  12.0'
    #   else:   #high
    #     SAPX = '  18.0'
    #   for i in range(0, len(soil_depth)):
    #     new_str = ' 1'+ repr(soil_depth[i]).rjust(6) + repr(SADM[i]).rjust(6) + repr(SAOC[i]).rjust(6) + repr(SANI[i]).rjust(6) + repr(SAPHW[i]).rjust(6)+ '   -99' + SAPX + '   -99   -99'+"\n"
    #     fw.write(new_str)

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
    if fert_app == "Fert":
        df_fert = df_fert.astype(float)
        df_filtered = df_fert[(df_fert["DAP"] >= 0)] # & (df_fert["NAmount"] >= 0)]
        fert_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        FDATE = df_filtered.DAP.values
        FMCD = "FE005"  #Urea
        FACD = 'AP002' #Broadcast, incorporated    #"AP001"  #Broadcast, not incorporated
        FDEP = "2"   #2cm    5cm depth
        FAMN = df_filtered.NAmount.values
        FAMP = -99  #df_filtered.PAmount.values
        FAMK = -99  #df_filtered.KAmount.values

        if fert_count > 0:   # fertilizer applied
            for i in range(fert_count):
                # new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + " " + FMCD.rjust(5) + " " + FACD.rjust(5) + " " + FDEP.rjust(5) + " " + repr(FAMN[i]).rjust(5) + " " + repr(FAMP[i]).rjust(5) + " " + repr(FAMK[i]).rjust(5) + temp_str[44:]
                new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + " " + FMCD.rjust(5) + " " + FACD.rjust(5) + " " + FDEP.rjust(5) + " " + repr(FAMN[i]).rjust(5) + " " + repr(FAMP).rjust(5) + " " + repr(FAMK).rjust(5) + temp_str[44:]
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
    # if p_sim == "P_yes":  #if phosphorous simulation is "on"
    #     fw.write(' 1 OP              Y     Y     Y     Y     N     N     N     N     D'+ "\n")
    # else:
    #     fw.write(' 1 OP              Y     Y     Y     N     N     N     N     N     D'+ "\n")
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
            soil_depth = line[33:37]
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
# def get_soil_SA(SOL_file, ID_SOIL):
#     # SOL_file=Wdir_path.replace("/","\\") + "\\SN.SOL"
#     # initialize
#     depth_layer = []
#     SADM = [] #bulk density
#     SAOC = [] #organic carbon %
#     SANI = [] #total nitrogen %
#     SAPHW = [] #pH in water
#     soil_flag = 0
#     count = 0
#     fname = open(SOL_file, "r")  # opens *.SOL
#     for line in fname:
#         if ID_SOIL in line:
#             soil_depth = line[33:37]
#             soil_flag = 1
#         if soil_flag == 1:
#             count = count + 1
#             if count >= 7:
#                 depth_layer.append(int(line[0:6]))
#                 SADM.append(float(line[43:49]))
#                 SAOC.append(float(line[49:55]))
#                 SANI.append(float(line[73:79]))
#                 SAPHW.append(float(line[79:85]))
#                 if line[3:6].strip() == soil_depth.strip():
#                     fname.close()
#                     break
#     return depth_layer, SADM, SAOC, SANI, SAPHW

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