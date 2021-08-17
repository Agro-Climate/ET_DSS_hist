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
import time

import graph

from apps.colombia.write_SNX import writeSNX_clim, writeSNX_frst 
from apps.ethiopia.run_WGEN import run_WGEN  # Downscaling method 1) WGEN (weather generator) to make 100 synthetic daily weather data
from apps.colombia.write_WTH import write_WTH   #save WTH from the output fo WGEN
# from apps.ethiopia.run_FResampler import run_FResampler  # Downscaling method 1) FResampler 
# from apps.ethiopia.write_WTH_FR import write_WTH_FR   #save WTH from the output fo FREsampler

sce_col_names=[ "sce_name", "Trimester1", "AN1","BN1", "AN2","BN2",
                "Crop", "Cultivar","stn_name", "PltDate", #"FirstYear", "LastYear", 
                "soil","iH2O","iNO3","plt_density", #"TargetYr",
                "Fert_1_DOY","Fert_1_Kg","Fert_2_DOY","Fert_2_Kg","Fert_3_DOY","Fert_3_Kg","Fert_4_DOY","Fert_4_Kg",
                "IR_1_DOY", "IR_1_amt","IR_2_DOY", "IR_2_amt","IR_3_DOY","IR_3_amt",
                "IR_4_DOY","IR_4_amt","IR_5_DOY","IR_5_amt","AutoIR_depth","AutoIR_thres", "AutoIR_eff",
                "CropPrice", "NFertCost", "SeedCost","IrrigCost", "OtherVariableCosts","FixedCosts"
]


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
                "Simulation Input (Forecast)",
              ),
            className=" card-header",
            ),

            dbc.Form([ ## INPUT FORM
              html.Div( # SCROLLABLE FORM
                html.Div([ # FORM START
                  dbc.FormGroup([ # Scenario
                    dbc.Label("1) Scenario Name", html_for="sce-name_frst", sm=3, className="p-2", align="start", ),
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
                    dbc.Label("2) Station", html_for="COstation_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                      id="COstation_frst",
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
                      dbc.Label("Observed Weather:", html_for="COstation_frst", className="p-2", align="start", ),
                      dbc.Row([
                        dbc.Col(
                          dbc.FormGroup([
                            dbc.Input(type="text", id="obs_1st", disabled="disabled" ),
                          ],),
                        ),
                        dbc.Col(
                          dbc.Label("to", html_for="trimester1", sm=3, className="p-0",),
                        ),
                        dbc.Col(
                          dbc.FormGroup([
                            dbc.Input(type="text", id="obs_last", disabled="disabled" ),
                          ],),
                        ),
                      ],),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Seasonal climate forecast EJ(7/25/2021)
                    dbc.Label("3) Seasonal Climate Forecast", html_for="SCF", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      html.Div([ # SEASONAL CLIMATE FORECAST
                        html.Div([ # 1st trimester
                          dbc.Row([
                            dbc.Col(
                              dbc.Label("1st trimester:", html_for="trimester1", className="p-2", align="start", ),
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
                                  dbc.Input(type="number", id="AN1", value=40, min="0", max="100", step="0.1", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="BN1", value=20, min="0", max="100", step="0.1", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  dbc.Input(type="number", id="NN1", value=40, disabled="disabled", required="required", ),
                                ],),
                              ),
                            ],),
                            dbc.Row([
                              dbc.FormText([
                                ""
                              ],
                              id="trimester1-error-msg",
                              style= {"display": "none"}
                              ),
                            ]),
                          ]),
                        ]),
                        html.Div([ # 2nd trimester
                          dbc.Row([
                            dbc.Col(
                              dbc.Label("2nd trimester:", html_for="SCF2", className="p-2", align="start", ),
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
                            dbc.Row([
                              dbc.FormText([
                                ""
                              ],
                              id="trimester2-error-msg",
                              style= {"display": "none"}
                              ),
                            ]),
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
                    dbc.Label("4) Crop", html_for="crop-radio_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                      id="crop-radio_frst",
                      # options=[{"label": k, "value": k} for k in cultivar_options.keys()],
                      options = [
                        {"label": "Drybean", "value": "BN"},
                        {"label": "Maize", "value": "MZ"},
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
                    dbc.Label("5) Cultivar", html_for="cultivar-dropdown_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="cultivar-dropdown_frst",
                        options=[
                          {"label": "DK234", "value": "CI0002 DK234"},
                          {"label": "FNC3056", "value": "CI0003 FNC3056"},
                          {"label": "DK7088", "value": "CI0004 DK7088"},
                          {"label": "P30F35", "value": "CI0001 P30F35"},],
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
                  dbc.FormGroup([ # Soil Type
                    dbc.Label("6) Soil Type", html_for="COsoil_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="COsoil_frst",
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
                    dbc.Label("7) Initial Soil Water Condition", html_for="ini-H2O_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="ini-H2O_frst",
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
                    dbc.Label("8) Initial Soil NO3 Condition", html_for="ini-NO3_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.Dropdown(
                        id="ini-NO3_frst",
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
                    dbc.Label("9) Planting Date", html_for="plt-date-picker_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.DatePickerSingle(
                      id="plt-date-picker_frst",
                      # min_date_allowed=date(2021, 1, 1),
                      # max_date_allowed=date(2021, 12, 31),
                      initial_visible_month=date(2021, 6, 5),
                      display_format="DD/MM/YYYY",
                      date=date(2021, 6, 15),
                      ),
                      # dbc.FormText("Only Month and Date are counted"), #for forecast mode, year does matter.
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Planting Density
                    dbc.Label(["10) Planting Density", html.Span(" (plants/m"), html.Sup("2"), html.Span(")"), ], html_for="plt-density_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="plt-density_frst", value=5, min=1, max=300, step=0.1, required="required", ),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.FormGroup([ # Fertilizer Application
                    dbc.Label("11) Fertilizer Application", html_for="fert_input_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="fert_input_frst",
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
                              dbc.Input(type="number", id="fert-day1_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt1_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("2nd", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day2_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt2_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("3rd", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day3_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt3_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("4th", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-day4_frst", value=0, min="0", max="365", required="required", ),
                            ],),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-amt4_frst", value=0, min="0", step="0.1", required="required", ),
                            ],),
                          ),
                        ],),
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
                  dbc.FormGroup([ # Irrigation
                    dbc.Label("12) Irrigation", html_for="irrig_input", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="irrig_input_frst",
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
                            id="ir_method_frst",
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
                                  dbc.Input(type="number", id="irrig-day1_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("1st", html_for="irrig-mt1", ),
                                  dbc.Input(type="number", id="irrig-amt1_frst", value=0, min="0", step="0.1", required="required", ),
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
                                  dbc.Input(type="number", id="irrig-day2_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("2nd", html_for="irrig-amt2", ),
                                  dbc.Input(type="number", id="irrig-amt2_frst", value=0, min="0", step="0.1", required="required", ),
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
                                  dbc.Input(type="number", id="irrig-day3_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("3rd", html_for="irrig-amt3", ),
                                  dbc.Input(type="number", id="irrig-amt3_frst", value=0, min="0", step="0.1", required="required", ),
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
                                  dbc.Input(type="number", id="irrig-day4_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("4th", html_for="irrig-amt4", ),
                                  dbc.Input(type="number", id="irrig-amt4_frst", value=0, min="0", step="0.1", required="required", ),
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
                                  dbc.Input(type="number", id="irrig-day5_frst", value=0, min="0", max="365", required="required", ),
                                ],),
                              ),
                              dbc.Col(
                                dbc.FormGroup([
                                  # dbc.Label("5th", html_for="irrig-amt5", ),
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
                              dbc.Label("Management soil depth", html_for="ir_depth", ),
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
                              dbc.Label("Threshold", html_for="ir_threshold", ),
                            ),
                            dbc.Col([
                              dbc.Input(type="number", id="ir_threshold_frst", value=50, min=1, max=100, step=0.1, required="required", ),
                              dbc.FormText("(% of max available water holding capacity)"),
                            ],),
                          ],
                          className="py-2",
                          ),
                          dbc.Row([  #efficiency fraction
                            dbc.Col(
                              dbc.Label("Irrigation efficiency fraction", html_for="ir_eff", ),
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
                    dbc.Label("13) Enterprise Budgeting?", html_for="EB_radio_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dcc.RadioItems(
                        id="EB_radio_frst",
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
                            dbc.Label("Crop Price", html_for="crop-price_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="crop-price_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[USD/kg]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Fertilizer Price", html_for="fert-cost_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fert-cost_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[USD/N kg]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Seed Cost", html_for="seed-cost_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="seed-cost_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[USD/ha]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Irrigation Cost", html_for="irrigation-cost", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="irrigation-cost_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[USD/mm]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Other Variable Costs", html_for="variable-costs_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="variable-costs_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[USD/ha]"),
                            ],),
                          ),
                        ],),
                        dbc.Row([
                          dbc.Col(
                            dbc.Label("Fixed Costs", html_for="fixed-costs_frst", className="text-center", ),
                          ),
                          dbc.Col(
                            dbc.FormGroup([
                              dbc.Input(type="number", id="fixed-costs_frst", value=0, min=0, step=0.1, required="required", ),
                              dbc.FormText("[USD/ha]"),
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
              html.Header(html.B("Scenarios"), className="card-header",),
              dbc.FormGroup([ # SUBMIT - ADD SCENARIO
                dbc.Button(id="write-button-state_frst",
                n_clicks=0,
                children="Create or Add a new Scenario",
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
                    {"id": "sce_name", "name": "Scenario Name"},
                    {"id": "Trimester1", "name": "Trimester1"},  #First trimester e.g., JJA
                    {"id": "AN1", "name": "AN1"},  #AN of the first trimeter
                    {"id": "BN1", "name": "BN1"},  #BN of the first trimester
                    {"id": "AN2", "name": "AN2"},  #AN of the second (following) trimester
                    {"id": "BN2", "name": "BN2"},  #BN of the second (following) trimester
                    {"id": "Crop", "name": "Crop"},
                    {"id": "Cultivar", "name": "Cultivar"},
                    {"id": "stn_name", "name": "Station"},
                    {"id": "Plt_date", "name": "Planting Date"},
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
                    {"id": "IrrigCost", "name": "Irrigation Cost"},
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
              html.Div([
                dbc.Row([ # IMPORT/DOWNLOAD SCENARIOS
                  dbc.Col(
                    dcc.Upload([
                      html.Div([
                        html.Div(html.B("Import Scenarios:")),
                        "Drag and Drop or ",
                        dcc.Link("Select a File", href="", )
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
                        # "textAlign": "center",
                        "background-color": "lightgray"
                    },
                    ),
                  ),
                  dbc.Col([
                    dbc.Button(
                      "Download Scenarios",
                    id="download-btn-sce-fcst", 
                    n_clicks=0, 
                    className="w-75 h-50 d-block mx-auto m-4",
                    color="secondary"
                    ),
                    dcc.Download(id="download-sce-fcst")
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
                      id="download-sce-fcst-error",
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
                html.B("Simulation Graphs (Forecast)"),
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
                            dbc.Label("Scenario Name", html_for="sname_cdf", sm=3, align="start", ),
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
                html.B("Download Simulated Yield CSV"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div([
                    html.Div([ # ORIGINAL CSV
                      dbc.Row([
                        dbc.Col("", xs=4, className="p-2"),
                        dbc.Col(
                          dbc.Button(id="btn_csv_yield_frst",
                          children="Simulated Yield",
                          className="d-block mx-auto w-100",
                          color="secondary",
                          ),
                        xs=4,
                        className="p-2"
                        ),
                        dbc.Col("", xs=4, className="p-2"),
                      ],
                      className="m-1",
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
                html.B("Enterprise Budgeting"),
              className=" card-header",
              ),
              html.Div([
                dbc.Form([ # EB FIGURES
                  dbc.FormGroup([ # Enterprise Budgeting Yield Adjustment Factor
                    dbc.Label("Enterprise Budgeting Yield Adjustment Factor", html_for="yield-multiplier_frst", sm=3, className="p-2", align="start", ),
                    dbc.Col([
                      dbc.Input(type="number", id="yield-multiplier_frst", value=1, min=0, max=2, step=0.1, required="required", ),
                      dbc.FormText("Enter a multiplier to account for a margin of error."),
                    ],
                    className="py-2",
                    xl=9,
                    ),
                  ],
                  row=True
                  ),
                  dbc.Button(id="EB-button-state_frst",
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
                  html.B("Download Enterprise Budgeting CSV"),
                className=" card-header"
                ),
                html.Div([
                  dbc.Row([
                    dbc.Col("", xs=4, className="p-2"),
                    dbc.Col(
                      dbc.Button(id="btn_csv_EB_frst", 
                      children="Download", 
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
              ],),
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

# # is this needed?
DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

DSSAT_FILES_DIR_SHORT = "/DSSAT/dssat-base-files"  #for linux systemn

DSSAT_FILES_DIR = os.getcwd() + DSSAT_FILES_DIR_SHORT   #for linux systemn

#https://community.plotly.com/t/loading-when-opening-localhost/7284
#I suspect that this is related to the JS assets from the CDN not loading properly - perhaps because they are blocked by your firewall or some other reason.
#You can load the assets locally by setting:
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

cultivar_options = {
    # "MZ": ["CIMT01 BH540-Kassie","CIMT02 MELKASA-Kassi","CIMT17 BH660-FAW-40%", "CIMT19 MELKASA2-FAW-40%", "CIMT21 MELKASA-LowY"],
    "MZ": ["CIMT01 BH540","CIMT02 MELKASA-1","CIMT17 BH660-FAW-40%", "CIMT19 MELKASA2-FAW-40%", "CIMT21 MELKASA-LowY"],
    "WH": ["CI2021 KT-KUB", "CI2022 RMSI", "CI2023 Meda wolabu", "CI2024 Sofumer", "CI2025 Hollandi", "CI2018 ET-MED", "CI2019 ET-LNG"],
    "SG": ["IB0020 ESH-1","IB0020 ESH-2","IB0027 Dekeba","IB0027 Melkam","IB0027 Teshale"]
}


# Wdir_path = "C:\\IRI\\Dash_ET_forecast\\ET_forecast_windows\\TEST_ET\\"
Wdir_path = DSSAT_FILES_DIR    #for linux systemn

#==============================================================
#call back to update the first & last weather observed dates
@app.callback(Output("obs_1st", component_property="value"),
              Output("obs_last", component_property="value"),
              Input("COstation_frst", component_property="value"))
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
    return [{"label": i, "value": i} for i in cultivar_options[selected_crop]]

@app.callback(
    Output("cultivar-dropdown_frst", "value"),
    Input("cultivar-dropdown_frst", "options"))
def set_cultivar_value(available_options):
    return available_options[0]["value"]
#==============================================================
#1) for yield - call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv-yield_frst", "data"),
    Input("btn_csv_yield_frst", "n_clicks"),
    State("memory-yield-table_frst","data"), 
    # State("yield-table", "data"),
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
        yld_exc.update_layout(title="Yield Exceedance Curve for a Selected Scenario",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]")
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
        rain1.update_layout(title="[Trimester #1] Rainfall ",
                        xaxis_title="Rainfall [mm]",
                        yaxis_title="Probability of Exceedance [-]")
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
        rain2.update_layout(title="[Trimester #2] Rainfall Total ",
                        xaxis_title="Rainfall [mm]",
                        yaxis_title="Probability of Exceedance [-]")
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
#=================================================    
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
    else:
        if existing_sces.empty:
            return {"display": "none"}
        else:
            return {"display": "none"} if existing_sces.sce_name.values[0] == "N/A" or set(existing_sces.CropPrice.values) == {-99} else {}

#==============================================================
# callback for downloading scenarios
@app.callback(Output("download-sce-fcst", "data"),
              Output("download-sce-fcst-error", component_property="style"),
              Input("download-btn-sce-fcst", "n_clicks"),
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
    return [dcc.send_data_frame(scenarios.to_csv, f"simagri_CO_fcst_scenarios_{timestamp}.csv"), {"display": "none"}]
#==============================================================
# submit to scenario table or import CSV
@app.callback(Output("scenario-table_frst", "data"),
                Input("write-button-state_frst", "n_clicks"),
                State("COstation_frst", "value"),
                State("trimester1", "value"),
                State("AN1", "value"),
                State("BN1", "value"),
                State("AN2", "value"),
                State("BN2", "value"),
                # State("year1", "value"),
                # State("year2", "value"),
                State("plt-date-picker_frst", "date"),
                State("crop-radio_frst", "value"),
                State("cultivar-dropdown_frst", "value"),
                State("COsoil_frst", "value"),
                State("ini-H2O_frst", "value"),
                State("ini-NO3_frst", "value"),
                State("plt-density_frst", "value"),
                State("sce-name_frst", "value"),
                # State("target-year", "value"),
                State("fert_input_frst", "value"),
                State("fert-day1_frst","value"),
                State("fert-amt1_frst","value"),
                State("fert-day2_frst","value"),
                State("fert-amt2_frst","value"),
                State("fert-day3_frst","value"),
                State("fert-amt3_frst","value"),
                State("fert-day4_frst","value"),
                State("fert-amt4_frst","value"),
                State("irrig_input_frst", "value"),     ## irrigation option
                State("ir_method_frst", "value"),     ##irrigation method in case "on reported date"
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
                State("ir_depth_frst", "value"), #autmomatic irrigaiton
                State("ir_threshold_frst", "value"),
                State("ir_eff_frst", "value"),
                State("EB_radio_frst", "value"),
                State("crop-price_frst","value"),
                State("seed-cost_frst","value"),
                State("fert-cost_frst","value"),
                State("irrigation-cost_frst","value"),
                State("fixed-costs_frst","value"),
                State("variable-costs_frst","value"),
                State("scenario-table_frst","data")
            )
def make_sce_table(
    n_clicks, station, trimester, AN1, BN1, AN2, BN2, planting_date, crop, cultivar, soil_type, 
    initial_soil_moisture, initial_soil_no3_content, planting_density, scenario, #target_year, 
    fert_app, 
    fd1, fa1,
    fd2, fa2,
    fd3, fa3,
    fd4, fa4,
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

    if ( # first check that all required inputs have been given
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
        return existing_sces

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
        "Fert_1_DOY": [-99], "Fert_1_Kg": [-99], "Fert_2_DOY": [-99], "Fert_2_Kg": [-99], 
        "Fert_3_DOY": [-99], "Fert_3_Kg": [-99], "Fert_4_DOY": [-99], "Fert_4_Kg": [-99], 
        "IR_method": [-99], #Irrigation on reported date
        "IR_1_DOY": [-99], "IR_1_amt": [-99],
        "IR_2_DOY": [-99], "IR_2_amt": [-99],
        "IR_3_DOY": [-99], "IR_3_amt": [-99],
        "IR_4_DOY": [-99], "IR_4_amt": [-99],
        "IR_5_DOY": [-99], "IR_5_amt": [-99],
        "AutoIR_depth":  [-99], "AutoIR_thres": [-99], "AutoIR_eff": [-99], #Irrigation automatic
        "CropPrice": [-99], "NFertCost": [-99], "SeedCost": [-99],"IrrigCost": [-99], "OtherVariableCosts": [-99], "FixedCosts": [-99]
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
    # writeSNX_main_hist(Wdir_path,station,start_year,end_year,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
    #                     planting_density,scenario,fert_app, current_fert)
    writeSNX_clim(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                        planting_density,scenario,fert_app, current_fert, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)  #This is differnt from writeSNX_main_hist in the historical analysis
    writeSNX_frst(Wdir_path,station,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                        planting_density,scenario,fert_app, current_fert, irrig_app, irrig_method, current_irrig, ir_depth,ir_threshold, ir_eff)
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

        if not (re.match("\d\d", dd) and re.match("\d\d", mm)):# and re.match("2021", yyyy)): EJ(7/27/2021) to allow hindcast simulation (e.g., 2001)
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
@app.callback(Output(component_id="yieldbox-container_frst", component_property="children"),
              Output(component_id="yieldcdf-container_frst", component_property="children"),
              Output("fcst-yieldtables-container", "children"),
              Output("sname_cdf", "options"),
              Output("memory-yield-table_frst", "data"),
              Input("simulate-button-state_frst", "n_clicks"),
              State("scenario-table_frst","data"), ### scenario summary table
              # State("season-slider", "value"), #EJ (5/13/2021) for seasonal total rainfall
              prevent_initial_call=True,
)

def run_create_figure(n_clicks, sce_in_table): #, slider_range):
    if n_clicks is None:
        raise PreventUpdate
        return 
    else: 
        # 1) Read saved scenario summaries and get a list of scenarios to run
        # dff = pd.read_json(intermediate, orient="split")
        scenarios = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        sce_numbers = len(scenarios.sce_name.values)
        # Wdir_path = "C:\\IRI\\Dash_ET_forecast\\ET_forecast_windows\\TEST_ET\\"  #for windows
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
              #1)WGEN
              df_wgen = run_WGEN(scenarios[i:i+1], tri_doylist, Wdir_path)  #pass subset of summary table => NOTE: the scenario names are in reverse order and thus last scenario is selected first
              write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)   #by taking into account planting and approximate harvesting dates
            #   #2)FResampler
            #   df_wgen = run_FResampler(scenarios[i:i+1], tri_doylist, Wdir_path)  
            #   write_WTH_FR(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)  
            else:
              if station == scenarios.stn_name.values[i-1] and trimester == scenarios.Trimester1.values[i-1]:
                if AN1 == scenarios.AN1.values[i-1] and BN1 == scenarios.BN1.values[i-1] and AN2 == scenarios.AN2.values[i-1] and BN2 == scenarios.BN2.values[i-1]:
                  #No need to run WGEN again => use df_wgen from previous scenario
                  write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path) 
                else:
                  #1)WGEN
                  df_wgen = run_WGEN(scenarios[i:i+1], tri_doylist, Wdir_path)
                  write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)
                #   #2)FResampler
                #   df_wgen = run_FResampler(scenarios[i:i+1], tri_doylist, Wdir_path)  
                #   write_WTH_FR(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)  
              else:
                #1)WGEN
                df_wgen = run_WGEN(scenarios[i:i+1], tri_doylist, Wdir_path)
                write_WTH(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path)
                # #2)FResampler
                # df_wgen = run_FResampler(scenarios[i:i+1], tri_doylist, Wdir_path)  
                # write_WTH_FR(scenarios[i:i+1], df_wgen, WTD_fname, Wdir_path) 
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
            #1-1) Run DSSAT executable for BOTh climatolgoy & forecast => Simulation resutls from both runs are in one Summary.out file
            os.chdir(Wdir_path)  #change directory
            if scenarios.Crop[i] == "BN":
                args = "./dscsm047 CRGRO047 B DSSBatch.V47" #===========>for linux system
                # args = "DSCSM047.EXE CSCER047 B DSSBatch.v47"  #===========>for windows
                # fout_name = path.join(Wdir_path, "ETWH"+scenario+".OSU")   #===========>for windows
            else: # scenarios.Crop[i] == "MZ":
                args = "./dscsm047 MZCER047 B DSSBatch.V47"  #===========>for linux system
                # args = "DSCSM047.EXE MZCER047 B DSSBatch.v47" #===========>for windows
                # # fout_name = path.join(Wdir_path, "COMZ"+scenario+".OSU") #===========>for windows

            fout_name = f"CL{scenarios.Crop[i]}{scenario}.OSU"  #simulation start for climatolgoy first
            arg_mv = f"mv Summary.OUT {fout_name}"   #Q: Do we need this? => Yes, DSSAT-Linux does not allow FNAME=Y, and generate only summary.out

            os.system(args) 
            os.system(arg_mv) 
            #=====================================================================
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
            WTH_fname = path.join(Wdir_path, scenarios.sce_name[i]+ '_all.WTH') #+repr(scenarios.PltDate[i])[3:5] +"99.WTH")  # e.g., aaaa2199.WTH
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
        yld_box = px.box(df, x="SNAME", y="HWAM", color="RUN", title="Yield Boxplot")
        yld_box.add_scatter(x=x_val2, y=TG_yield, mode="markers", 
            marker=dict(color='LightSkyBlue', size=10, line=dict(color='MediumPurple', width=2))) #, mode="lines+markers") #"lines")
        yld_box.update_xaxes(title= "Scenario Name [*Note:LightBlue dot(s) represents simulated yield(s) using observed weather of the planting year]")
        yld_box.update_yaxes(title= "Yield [kg/ha]")

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
        yld_exc.update_layout(title="Exceedance Curves of Forecasted Yield for All Scenarios",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]")
        yld_exc.update_yaxes(range=[0, 1])

        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_yield_first.csv")
        df.to_csv(fname, index=False)  #EJ(7/27/2021) check 
        #print({"label": i, "value": i} for i in list(df_out.columns))
        dic_sname = [{"label": i, "value": i} for i in np.unique(df.SNAME.values)]   #check
        return [
            dcc.Graph(id="yield-boxplot", figure = yld_box, config = graph.config, ), 
            dcc.Graph(id="yield-exceedance", figure = yld_exc, config = graph.config, ),
            dash_table.DataTable(columns = [{"name": i, "id": i} for i in df.columns],data=df.to_dict("records"),
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
            dic_sname, #EJ(7/27/2021)
            df.to_dict("records"),   #df_out.to_dict("records"),    #EJ(7/27/2021) check 
        ]
#Last callback to create figures for Enterprise budgeting
@app.callback(Output(component_id="EBbox-container_frst", component_property="children"),
                Output(component_id="EBcdf-container_frst", component_property="children"),
                Output(component_id="EBtables-container_frst", component_property="children"),
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

        # Wdir_path = DSSAT_FILES_DIR  #for linux system
        # os.chdir(Wdir_path)  #change directory  #check if needed or not
        TG_GMargin = []

        #EJ(5/3/2021) Read DSSAT output for each scenarios
        for i in range(sce_numbers):
            sname = EB_sces.sce_name.values[i]
            # fout_name = path.join(Wdir_path, f"ET{EB_sces.Crop[i]}{sname}.OSU")
            fout_name = path.join(Wdir_path, f"CL{EB_sces.Crop[i]}{sname}.OSU")

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
        gmargin_box = px.box(df, x="SNAME", y="GMargin", color="RUN", title="Gross Margin Boxplot")
        gmargin_box.add_scatter(x=x_val2, y=TG_GMargin, mode="markers", 
            marker=dict(color='LightSkyBlue', size=10, line=dict(color='MediumPurple', width=2))) #, mode="lines+markers") #"lines")
        gmargin_box.update_xaxes(title= "Scenario Name [*Note:LightBlue dot(s) represents gross margin using the simulated yield(s) with observed weather in the planting year]")
        gmargin_box.update_yaxes(title= "Gross Margin[Birr/ha]")

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
        gmargin_exc.update_layout(title="Gross Margin Exceedance Curve",
                        xaxis_title="Gross Margin[Birr/ha]",
                        yaxis_title="Probability of Exceedance [-]")

        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_Gmargin_frst.csv")
        df.to_csv(fname, index=False)  #EJ(7/27/2021) check 
        return [
            dcc.Graph(id="EB-boxplot", figure = gmargin_box, config = graph.config, ),
            dcc.Graph(id="EB-exceedance", figure = gmargin_exc, config = graph.config, ),
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict("records"),
                style_cell={"whiteSpace": "normal","height": "auto",},
            ),
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
    # # #write dataframe into CSV file for debugging
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