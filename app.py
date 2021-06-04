import dash
import pandas as pd
import numpy as np
import pathlib
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import plotly.express as px
import plotly.graph_objects as go

from dash.dependencies import Input, Output, State
from dash_extensions import Download
from dash.exceptions import PreventUpdate
# from helpers import make_dash_table, create_plot

from os import path # path
import os
import subprocess  #to run executable
from datetime import date
import datetime    #to convert date to doy or vice versa
import calendar

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v5.12.1/css/all.css",
    ],
  #  meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    prevent_initial_callbacks=True,  #to prevent "Callback failed: the server did not respond." message thttps://community.plotly.com/t/callback-error-when-the-app-is-started/46345/2
)

server = app.server

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

DSSAT_FILES_DIR_SHORT = "/dssat_files_dir/"  #for linux systemn

DSSAT_FILES_DIR = os.getcwd() + DSSAT_FILES_DIR_SHORT   #for linux systemn

#https://community.plotly.com/t/loading-when-opening-localhost/7284
#I suspect that this is related to the JS assets from the CDN not loading properly - perhaps because they are blocked by your firewall or some other reason.
#You can load the assets locally by setting:
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

#column names for scenario summary table:EJ(5/3/2021)
sce_col_names=["sce_name", "Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","TargetYr",
                 "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                 "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"]

cultivar_options = {
    "MZ": ["CIMT01 BH540-Kassie","CIMT02 MELKASA-Kassi","CIMT17 BH660-FAW-40%", "CIMT19 MELKASA2-FAW-40%", "CIMT21 MELKASA-LowY"],
    "WH": ["CI2021 KT-KUB", "CI2022 RMSI", "CI2023 Meda wolabu", "CI2024 Sofumer", "CI2025 Hollandi"],
    "SG": ["IB0020 ESH-1","IB0020 ESH-2","IB0027 Dekeba","IB0027 Melkam","IB0027 Teshale"]
}
# Wdir_path = "C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\"
Wdir_path = DSSAT_FILES_DIR    #for linux systemn

SIMAGRI_LOGOS = app.get_asset_url("ethioagroclimate.png")

app.layout = html.Div( ## MAIN APP DIV
[
  dcc.Store(id="memory-yield-table"),  #to save fertilizer application table
  dcc.Store(id="memory-sorted-yield-table"),  #to save fertilizer application table
  dcc.Store(id="memory-EB-table"),  #to save fertilizer application table

  # NAVBAR
  dbc.Navbar([
    # LOGO & BRAND
    html.A(
      # Use row and col to control vertical alignment of logo / brand
      dbc.Row([
        dbc.Col(html.Img(src=SIMAGRI_LOGOS)),
        dbc.Col(dbc.NavbarBrand("SIMAGRI-Ethiopia", className="ml-3 font-weight-bold"),className="my-auto"),
      ],
      align ="left",
      no_gutters=True,
      ),
    href="#",
    ),
    # NAV ITEMS
    dbc.Nav([
      dbc.NavItem(dbc.NavLink("Historical Analysis", href="#historical"),),
      dbc.NavItem(dbc.NavLink("Forecast Analysis", href="#forecast")),
      dbc.NavItem(dbc.NavLink("About", href="#about")),
    ],
    navbar=True,
    ),
  ],
  color="white",
  dark=False
  ),

  html.Div( ## HISTORICAL: INPUT AND GRAPHS
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
                    dbc.Label("1) Scenario Name", html_for="sce-name"),
                    dbc.Input(type="text", id="sce-name", minLength=4, maxLength=4),
                  ],),
                  dbc.FormGroup([ # Station
                    dbc.Label("2) Station", html_for="ETstation"),
                    dcc.Dropdown(
                      id="ETstation",
                      options=[
                        {"label": "Melkasa", "value": "MELK"},
                        {"label": "Awassa", "value": "AWAS"},
                        {"label": "Bako", "value": "BAKO"},
                        {"label": "Mahoni", "value": "MAHO"}
                      ],
                      value="MELK"
                    ),
                  ],),
                  dbc.FormGroup([ # Crop
                    dbc.Label("3) Crop", html_for="crop-radio"),
                    dcc.RadioItems(
                      id="crop-radio",
                      # options=[{"label": k, "value": k} for k in cultivar_options.keys()],
                      options = [
                        {"label": "Maize", "value": "MZ"}, 
                        {"label": "Wheat", "value": "WH"}, 
                        {"label": "Sorghum", "value": "SG"},
                      ],
                      labelStyle = {"display": "inline-block","margin-right": 10},
                      value="MZ"
                    ),
                  ],),
                  dbc.FormGroup([ # Cultivar
                    dbc.Label("4) Cultivar", html_for="cultivar-dropdown"),
                    dcc.Dropdown(
                      id="cultivar-dropdown", 
                      options=[
                        {"label": "CIMT01 BH540-Kassie", "value": "CIMT01 BH540-Kassie"},
                        {"label": "CIMT02 MELKASA-Kassi", "value": "CIMT02 MELKASA-Kassi"},
                        {"label": "CIMT17 BH660-FAW-40%", "value": "CIMT17 BH660-FAW-40%"},
                        {"label": "CIMT19 MELKASA2-FAW-40%", "value": "CIMT19 MELKASA2-FAW-40%"},
                        {"label": "CIMT21 MELKASA-LowY", "value": "CIMT21 MELKASA-LowY"},], 
                      value="CIMT02 MELKASA-Kassi"
                    ),
                  ],),

                  #  type="number"
                    # dbc.FormGroup([ # Start Year
                    #   dbc.Label("5) Start Year", html_for="year1"),
                    #   dbc.Input(type="number", id="year1", placeholder="YYYY", value="1981", min=1981, max=2018, ),
                    #   dbc.FormText("(No earlier than 1981)"),
                    # ],),
                    # dbc.FormGroup([ # End Year
                    #   dbc.Label("6) End Year", html_for="year2"),
                    #   dbc.Input(type="number", id="year2", placeholder="YYYY", value="2018", min=1981, max=2018, ),
                    #   dbc.FormText("(No later than 2018)"),
                    # ],),
                    # dbc.FormGroup([ # Year to Highlight
                    #   dbc.Label("7) Year to Highlight", html_for="target-year"),
                    #   dbc.Input(type="number", id="target-year", placeholder="YYYY", min=1981, max=2018, ),
                    #   dbc.FormText("Target year can a specific year you remember (e.g., drought year) and want to compare with a full climatology distribution"),
                    # ],),

                  # type="text"
                  dbc.FormGroup([ # Start Year
                    dbc.Label("5) Start Year", html_for="year1"),
                    dbc.Input(type="text", id="year1", placeholder="YYYY", value="1981",),
                    dbc.FormText("(No earlier than 1981)"),
                  ],),
                  dbc.FormGroup([ # End Year
                    dbc.Label("6) End Year", html_for="year2"),
                    dbc.Input(type="text", id="year2", placeholder="YYYY", value="2018",),
                    dbc.FormText("(No later than 2018)"),
                  ],),
                  dbc.FormGroup([ # Year to Highlight
                    dbc.Label("7) Year to Highlight", html_for="target-year"),
                    dbc.Input(type="text", id="target-year", placeholder="YYYY",),
                    dbc.FormText("Target year can a specific year you remember (e.g., drought year) and want to compare with a full climatology distribution"),
                  ],),

                  html.Div([ #5
                    html.Div("5) Years"),
                    dbc.FormText("Available years are from 1981 to 2018"),
                    html.Span("From "),
                    html.Span(" to "),
                    html.Br(),                 
                  ], className="d-none"),
                  dbc.FormGroup([ # Soil Type
                    dbc.Label("8) Soil Type", html_for="ETsoil"),
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
                      value="ETET001_18"
                    ),
                  ],),
                  dbc.FormGroup([ # Soil Water Condition
                    dbc.Label("9) Soil Water Condition", html_for="ini-H2O"),
                    dcc.Dropdown(
                      id="ini-H2O", 
                      options=[
                        {"label": "30% of AWC", "value": "0.3"},
                        {"label": "50% of AWC", "value": "0.5"},
                        {"label": "70% of AWC", "value": "0.7"},
                        {"label": "100% of AWC", "value": "1.0"},
                      ], 
                      value="0.5"  
                    ),
                  ],),
                  dbc.FormGroup([ # Initial NO3 Condition
                    dbc.Label("10) Initial NO3 Condition", html_for="ini-NO3"),
                    dcc.Dropdown(
                      id="ini-NO3", 
                      options=[
                        {"label": "High(65 N kg/ha)", "value": "H"},
                        {"label": "Low(23 N kg/ha)", "value": "L"},
                      ], 
                      value="L"
                    ),                                      
                  ],),
                  dbc.FormGroup([ # Planting Date
                    dbc.Label("11) Planting Date", html_for="plt-date-picker"),
                    dbc.FormText("Only Monthly and Date are counted"),
                    dcc.DatePickerSingle(
                    id="plt-date-picker",
                    min_date_allowed=date(2021, 1, 1),
                    max_date_allowed=date(2021, 12, 31),
                    initial_visible_month=date(2021, 6, 5),
                    date=date(2021, 6, 15)
                    ),
                  ],),
                  # type="number"    
                    # dbc.FormGroup([ # Planting Density
                    #   dbc.Label("12) Planting Density", html_for="plt-density"),
                    #   dbc.Input(type="number", id="plt-density", value=1, min=1, max=250),
                    #   dbc.FormText([
                    #     html.Span(" plants/m"),
                    #     html.Sup("2"),
                    #   ]),
                    # ],),

                  # type="text"
                  dbc.FormGroup([ # Planting Density
                    dbc.Label("12) Planting Density", html_for="plt-density"),
                    dbc.Input(type="text", id="plt-density", value="1"),
                    dbc.FormText([
                      html.Span(" plants/m"),
                      html.Sup("2"),
                    ]),
                  ],),
                  dbc.FormGroup([ # Fertilizer Application
                    dbc.Label("13) Fertilizer Application", html_for="fert_input"),
                    dcc.RadioItems(
                      id="fert_input",
                      options=[
                        {"label": "Fertilizer", "value": "Fert"},
                        {"label": "No Fertilizer", "value": "No_fert"},
                      ],
                      labelStyle = {"display": "inline-block","margin-right": 10},
                      value="No_fert"
                    ),
                  ],),
                  dbc.FormGroup([ # FERTILIZER INPUT TABLE
                    dash_table.DataTable(id="fert-table",
                      style_cell = {
                        "font_family": "sans-serif",
                        "whiteSpace": "normal",
                        "font_size": "14px",
                        "text_align": "center"
                      },
                      columns=([
                        {"id": "DAP", "name": "Days After Planting"},
                        {"id": "NAmount", "name": "Amount of N in kg/ha"},
                      ]),
                      data=[
                        dict(**{param: 0 for param in ["DAP", "NAmount"]}) for i in range(1, 5)
                      ],
                      # Days After Planting
                      # Amount of N in kg/ha
                      style_cell_conditional=[
                        {"if": {"id": "DAP"}, "width": "30%"}, # Failed component prop type: Invalid component prop (when app.run_server() Debug=True)
                        {"if": {"id": "NAmount"}, "width": "30%"},
                      ],
                      editable=True    
                    ),
                  ],
                  id="fert-table-Comp", 
                  className="w-50",
                  style={"display": "none"},
                  ),
                  dbc.FormGroup([ # Enterprise Budgeting?
                    dbc.Label("14) Enterprise Budgeting?", html_for="EB_radio"),
                    dcc.RadioItems(
                      id="EB_radio",
                      options=[
                        {"label": "Yes", "value": "EB_Yes"},
                        {"label": "No", "value": "EB_No"},
                      ],
                      labelStyle = {"display": "inline-block","margin-right": 10},
                      value="EB_No"
                    ),
                  ]),
                  dbc.FormGroup([ # ENTERPRISE BUDGETING TABLE
                    dash_table.DataTable(id="EB-table",
                      style_cell = {
                      "font_family": "sans-serif", #"cursive",
                      "whiteSpace": "normal",
                      "font_size": "14px",
                      "text_align": "center"},
                      columns=([
                        {"id": "CropPrice", "name": "Crop Price"},
                        {"id": "NFertCost", "name": "Fertilizer Cost"},
                        {"id": "SeedCost", "name": "Seed Cost"},
                        {"id": "OtherVariableCosts", "name": "Other Variable Costs"},
                        {"id": "FixedCosts", "name": "Fixed Costs"},
                      ]),
                      data=[
                        dict(**{param: 0 for param in ["CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"]}) for i in range(1, 2)
                      ],
                      style_cell_conditional=[
                        {"if": {"id": "CropPrice"}, "width": "20%"}, # Failed component prop type: Invalid component prop (when app.run_server() Debug=True)
                        {"if": {"id": "NFertCost"}, "width": "20%"},
                      ],
                      editable=True
                    ),

                    html.Div([
                      html.Div("Unit: Crop Price [ETB/kg], Fertilizer Cost [ETB/N kg], Seed Cost [ETB/kg], Other Variable Costs [ETB/ha], Fixed Costs [ETB/ha]"),
                      html.Div("Calculation =>  Gross Margin [ETB/ha] = Revenues [ETB/ha] - Variable Costs [ETB/ha] - Fixed Costs [ETB/ha]"),
                      html.Ul([
                        html.Li("Revenues [ETB/ha] = Yield [kg/ha] * Crop Price [ETB/kg]"),
                        html.Li("Variable costs for fertilizer [ETB/ha] = N Fertilizer amount [N kg/ha] * cost [ETB/N kg]"),
                        html.Li("Variable costs for seed purchase [ETB/ha]"), # = Planting Density in #9 [plants/m2] *10000 [m2/ha]* Seed Cost [ETB/plant]"),
                        html.Div("**(reference: the price of hybrid maize seed from the MOA was about 600 ETB/100 kg compared to 50-80 ETB/100 kg for local maize seed purchased in the local market (ETB 7 = US$ 1)."),
                        html.Li("Other variable costs [ETB/ha] may include pesticide, insurance, labor etc."),
                        html.Li("Fixed costs [ETB/ha] may include interests for land, machinery etc."),
                      ]),
                    ]),
                  ],
                  id="EB-table-Comp", 
                  className="w-100",
                  style={"display": "none"},
                  ),
                  # INPUT FORM END
                ], 
                className="p-3"
                ),
              className="overflow-auto",
              style={"height": "67vh"},
              ),

              html.Div([ # SCENARIO TABLE
                # Deletable summary table : EJ(5/3/2021)
                html.Header(html.B("Scenarios"), className="card-header",),
                html.Div([
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
                    {"id": "iH2O", "name": "Initial Soil Water Content"},
                    {"id": "iNO3", "name": "Initial Soil Nitrate Content"},
                    {"id": "TargetYr", "name": "Target Year"},
                    {"id": "1_Fert(DOY)", "name": "DOY 1st Fertilizer Applied"},
                    {"id": "1_Fert(Kg/ha)", "name": "1st Amount Applied (Kg/ha)"},
                    {"id": "2_Fert(DOY)", "name": "DOY 2nd Fertilizer Applied"},
                    {"id": "2_Fert(Kg/ha)", "name": "2nd Amount Applied(Kg/ha)"},
                    {"id": "3_Fert(DOY)", "name": "DOY 3rd Fertilizer Applied"},
                    {"id": "3_Fert(Kg/ha)", "name": "3rd Amount Applied(Kg/ha)"},
                    {"id": "4_Fert(DOY)", "name": "DOY 4th Fertilizer Applied"},
                    {"id": "4_Fert(Kg/ha)", "name": "4th Amount Applied(Kg/ha)"},
                    {"id": "CropPrice", "name": "Crop Price"},
                    {"id": "NFertCost", "name": "Fertilizer Cost"},
                    {"id": "SeedCost", "name": "Seed Cost"},
                    {"id": "OtherVariableCosts", "name": "Other Variable Costs"},
                    {"id": "FixedCosts", "name": "Fixed Costs"},
                  ]),
                  data=[
                    dict(**{param: "N/A" for param in sce_col_names}) for i in range(1, 2)
                  ],
                  editable=True,
                  row_deletable=True
                  ) 
                ],
                id="sce-table-Comp", 
                className="overflow-auto block",
                ),
                # end of Deletable summary table : EJ(5/3/2021)
              ]),

              dbc.FormGroup([ # SUBMIT - ADD SCENARIO
                dbc.Button(id="write-button-state", 
                n_clicks=0, 
                children="Create or Add a new Scenario", 
                className="w-75 d-block mx-auto",
                color="primary"
                ),
              ]),
            ]),

            html.Div([ # AFTER SCENARIO TABLE
              dbc.FormGroup([ # Approximate Growing Season
                dbc.Label("15) Approximate Growing Season", html_for="season-slider"),
                dbc.FormText("This growing season is used to sort drier/wetter years based on the seasonal total rainfall"),
                dcc.RangeSlider(
                  id="season-slider",
                  min=1, max=12, step=1,
                  marks={1: "Jan", 2: "Feb",3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"},
                  value=[6, 9]
                ),
              ]),

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
                    html.Div([
                      dbc.Spinner(children=[html.Div(id="yieldbox-container")], size="lg", color="primary", type="border", fullscreen=True,),
                      html.Div(id="yieldcdf-container"),  #exceedance curve
                      html.Div(id="yieldtimeseries-container"),  #time-series
                      dbc.Row([
                        dbc.Col(
                          html.Div(id="yield-BN-container", 
                          # style={"width": "33%", "display": "inline-block"}
                          ),
                        md=4),
                        dbc.Col(
                          html.Div(id="yield-NN-container", 
                          # style={"width": "33%", "display": "inline-block"}
                          ),
                        md=4),
                        dbc.Col(
                          html.Div(id="yield-AN-container", 
                          # style={"width": "33%", "display": "inline-block"}
                          ),
                        md=4),
                      ]),
                    ], 
                    className="plot-container plotly"),
                  className="js-plotly-plot"
                  )
                ], 
                id="simulation-graphs", 
                # className="dash-graph ddk-graph", 
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
                html.B("Simulated Yield Original CSV"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div([
                    html.Div([ # ORIGINAL CSV STUFF
                      html.Br(),

                      dbc.Button(id="btn_csv", 
                      children="Download CSV for Simulated Yield", 
                      className="w-75 d-block mx-auto",
                      color="secondary"
                      ),
                      # dcc.Download(id="download-dataframe-csv"),
                      Download(id="download-dataframe-csv"),
                      html.Div(id="yieldtables-container", 
                      className="overflow-auto",
                      style={"height": "10vh"},
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
          
          html.Div( # SORTED CSV
            html.Div([
              html.Header(
                html.B("Simulated Yield Sorted CSV"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div([
                    html.Div([ # SORTING CONTROLS AND BUTTON
                      html.Br(),
                      html.Div([
                        html.Span("(i) Select a column name to sort: "),
                        html.Div([dcc.Dropdown(id="column-dropdown", options=[{"label": "YEAR", "value": "YEAR"},],value="YEAR")]),
                      ],
                      ),
                      html.Br(),
                      html.Div([
                        html.Span("(ii) Yield adjustment factor: "),
                        dbc.Input(id="yield-multiplier", type="text", placeholder="Enter ", value = "1"),
                        html.Span(" (e.g., 90% reduction => 0.9)"),  
                      ]),
                      html.Br(),
                      dbc.Button(id="btn_table_sort", 
                      children="Click to update and sort the Datatable by the selected column name", 
                      className="w-75 d-block mx-auto",
                      color="info"
                      ),
                      html.Br(),   
                      dbc.Button(id="btn_csv2", 
                      children="Download SORTED CSV for Simulated Yield", 
                      className="w-75 d-block mx-auto",
                      color="secondary"
                      ),
                      # dcc.Download(id="download-dataframe-csv"),
                      Download(id="download-dataframe-csv2"),
                      html.Div(id="yieldtables-container2", 
                      className="overflow-auto",
                      style={"height": "10vh"},
                      ),  #sorted yield simulated output
                    ],
                    ),
                  ],
                  ),
                ], 
                id="sorted-yield-csv-table", className="dash-table-container"
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
              html.Div(
                html.Div([
                  html.Div(
                    html.Div([
                      html.Br(),
                      dbc.Button(id="EB-button-state", 
                      children="Display figures for Enterprise Budgets", 
                      className="w-75 d-block mx-auto",
                      color="danger"
                      ),
                      html.Br(),
                      html.Div(id="EBbox-container"), 
                      html.Div(id="EBcdf-container"),  #exceedance curve
                      html.Div(id="EBtimeseries-container"), #exceedance curve
                      html.Br(),
                      dbc.Button(id="btn_csv_EB", 
                      children="Download CSV file for Enterprise Budgeting", 
                      className="w-75 d-block mx-auto",
                      color="secondary"
                      ),
                      # dcc.Download(id="download-dataframe-csv"),
                      Download(id="download-dataframe-csv_EB"),
                      html.Div(id="EBtables-container", className="w-50"),   #yield simulated output
                    ], 
                    className="plot-container plotly"),
                  className="js-plotly-plot",
                  )
                ], 
                id="enterprise-budgeting", className="dash-graph ddk-graph", style={"height": "20vh"}
                ),
              ),
            ], 
            ),
          ),
        ], 
        className="block card"
        )
      ],
      md=7,
      className="p-1",
      ),
    ],
    className="m-1"
    ),
  ),


  html.Div([ # NAVIGATE TO THESE SECTIONS
    html.Div( ## FORECAST -- HIDDEN FOR NOW
      "HISTORICAL",
    className="d-none",
    ),
    html.Div( ## ABOUT SIMAGRI -- HIDDEN FOR NOW
      dbc.Row( # HEADER AND DESCRIPTION
        dbc.Col([
          dbc.Row(
            # dbc.Col(
            #   html.Div([
            #     html.H4("Climate-Agriculture Modeling Decision Support Tool for Ethiopia"),
            #     html.H4("(Historical Analysis)"),
            #   ],
            #   className="card text-uppercase",
            #   ),
            # md=9,
            # className="mx-auto"
            # )
          ),
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
        ],
        className="text-center"
        )
      ),
    className="d-none",
    ),
  ],
  ),

],
)

#==============================================================
#Dynamic call back for sorting datatable by a column name
@app.callback(Output(component_id="yieldtables-container2", component_property="children"),
                Output("memory-sorted-yield-table", "data"),
                # Input("column-dropdown", "value"),
                Input("btn_table_sort", "n_clicks"),
                State("memory-yield-table", "data"),
                State("yield-multiplier", "value"),
                State("column-dropdown", "value"),
                prevent_initial_call=True,
            )
def sort_table(n_clicks, yield_table, multiplier, col_name):
    if n_clicks: 
        df =pd.DataFrame(yield_table)
        df_out = df.sort_values(by=[col_name])
        col = df_out.columns
        for i in range(1,len(col),3):
            temp=df_out.iloc[:,[i]].mul(float(multiplier))  #multiply yield adjustment factor
            temp=temp.astype(int)
            # temp.round(0)  #Round a DataFrame to a variable number of decimal places.
            df_out.iloc[:,i]=temp.values
        return [
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in df_out.columns],data=df_out.to_dict("records"),
                style_table={"overflowX": "auto"}, 
                style_cell={   # all three widths are needed
                    "minWidth": "10px", "width": "10px", "maxWidth": "30px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis", }),
            df_out.to_dict("records")
            ]

#call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv2", "data"),
    Input("btn_csv2", "n_clicks"),
    State("memory-sorted-yield-table", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, yield_data):
    # print(yield_data)
    df =pd.DataFrame(yield_data)
    return dcc.send_data_frame(df.to_csv, "simulated_yield_sorted.csv")
#==============================================================
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
    return cultivar_options[0]["value"]
#==============================================================
#call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State("memory-yield-table", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, yield_data):
    # print(yield_data)
    df =pd.DataFrame(yield_data)
    return dcc.send_data_frame(df.to_csv, "simulated_yield.csv")
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
    # print(EB_data)
    df =pd.DataFrame(EB_data)
    return dcc.send_data_frame(df.to_csv, "simulated_yield_EB.csv")
#=================================================   
#call back to "show/hide" fertilizer input table
@app.callback(Output("fert-table-Comp", component_property="style"),
              Input("fert_input", component_property="value"))
def show_hide_table(visibility_state):
    if visibility_state == "Fert":
        return {"width": "30%","display": "block"}  #{"display": "block"}   
    if visibility_state == "No_fert":
        return {"width": "30%","display": "none"} #"display": "none"} 
#==============================================================
#call back to "show/hide" Enterprise Budgetting input table
@app.callback(Output("EB-table-Comp", component_property="style"),
              Input("EB_radio", component_property="value"))
def show_hide_EBtable(visibility_state):
    if visibility_state == "EB_Yes":
        return {"width": "80%","display": "block"}  #{"display": "block"}   
    if visibility_state == "EB_No":
        return {"width": "80%","display": "none"} #"display": "none"} 
#==============================================================
@app.callback(Output("scenario-table", "data"),
                # Output("intermediate-value", "children"),
                Input("write-button-state", "n_clicks"),
                State("ETstation", "value"),  #input 1
                State("year1", "value"),      #input 2
                State("year2", "value"),      #input 3
                State("plt-date-picker", "date"),  #input 4
                # State("ETMZcultivar", "value"),   #input 5
                State("crop-radio", "value"),  #input 50
                State("cultivar-dropdown", "value"),   #input 5
                State("ETsoil", "value"),         #input 6
                State("ini-H2O", "value"),        #input 7           
                State("ini-NO3", "value"),        #input 8
                State("plt-density", "value"),    #input 9
                State("sce-name", "value"),       #input 10
                State("target-year", "value"),    #input 11
                # State("intermediate-value", "children"),  #input 12 scenario summary table
                State("fert_input", "value"),     ##input 13 fertilizer yes or no
                State("fert-table","data"), ###input 14 fert input table
                State("EB_radio", "value"),     ##input 15 Enterprise budgeting yes or no
                State("EB-table","data"), #Input 16 Enterprise budget input
                State("scenario-table","data") ###input 17 scenario summary table
            )
def make_sce_table(n_clicks, station, start_year, end_year, planting_date, crop, cultivar, soil_type, initial_soil_moisture, initial_soil_no3_content, planting_density, scenario,
                  targetyear, fert_app, fert_in_table, EB_radio, EB_in_table, sce_in_table):
    # print(station)  #MELK
    # print(start_year)  #1981
    # print(end_year)  #2014
    # print(planting_date)  #2021-06-15
    # print(cultivar)  #CIMT01 BH540-Kassie
    # print(soil_type)  #ETET001_18
    # print(initial_soil_moisture)  #0.7
    # print(initial_soil_no3_content)  #H
    # print(planting_density)  #6
    # print(scenario)  #scenario name
    # print(targetyear)  #target year as a benchmark
    # print(station2)  #scenario summary
    # print(station3)  #fertilizler or no-fertilizer
    # print(station4)  #fertilizler summary
    # print("station5:",EB_in_table)  #scenario summary

    # 2) Read fertilizer application information
    if fert_app == "Fert":
        # print("fert-table in callback make_sce_table= {}".format(fert_in_table))
        df_fert =pd.DataFrame(fert_in_table)
        # print("fert-table in callback make_sce_table= {}".format(df_fert))
    else: #if no fertilizer, then an empty df with an arbitrary column
        df_fert = pd.DataFrame(columns=["DAP", "NAmount"]) 

    # 3) Read Enterprise budget input
    if EB_radio == "EB_Yes":
        # print("EB-table in callback make_sce_table= {}".format(EB_in_table))
        df_EB =pd.DataFrame(EB_in_table)
        # print("EB-table in callback make_sce_table= {}".format(df_EB))
    else: #if no EB analysis
        df_EB = pd.DataFrame(columns=["sce_name","Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                 "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                 "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"]) 
    #Make a new dataframe to return to scenario-summary table
    df = pd.DataFrame(
        [[scenario, crop, cultivar[7:], station, planting_date[5:], start_year, end_year, soil_type, initial_soil_moisture, initial_soil_no3_content, planting_density, targetyear,
            "-99", "-99", "-99", "-99","-99", "-99","-99", "-99", "-99","-99", "-99","-99", "-99"]],
        columns=["sce_name","Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                 "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                 "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"],)
    # data = df.to_dict("rows")
    data = [{"sce_name": None,"Crop": None, "Cultivar": None, "stn_name": None, "Plt-date": None, "FirstYear": None, "LastYear": None, "soil": None,
             "iH2O": None, "iNO3": None, "plt_density": None, "TargetYr": None,
             "1_Fert(DOY)": None,"1_Fert(Kg/ha)": None,"2_Fert(DOY)": None,"2_Fert(Kg/ha)": None, "3_Fert(DOY)": None,"3_Fert(Kg/ha)": None, "4_Fert(DOY)": None,"4_Fert(Kg/ha)": None,
             "CropPrice": None,"NFertCost": None,"SeedCost": None,"OtherVariableCosts": None, "FixedCosts": None}] 
    # columns =  [{"name": i, "id": i,} for i in (df.columns)]
    dff = df.copy()

    if n_clicks:  
        #=====================================================================
        #1) Write SNX file
        writeSNX_main_hist(Wdir_path,station,start_year,end_year,planting_date,crop, cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                           planting_density,scenario,fert_app, df_fert)
        #=====================================================================
        # #Make a new dataframe for fertilizer inputs
        if fert_app == "Fert" and EB_radio == "EB_Yes":
            #Make a new dataframe
            df = pd.DataFrame(
                [[scenario, crop, cultivar[7:], station, planting_date[5:],start_year, end_year, soil_type, initial_soil_moisture, initial_soil_no3_content, planting_density,targetyear, 
                df_fert.DAP.values[0], df_fert.NAmount.values[0], df_fert.DAP.values[1], df_fert.NAmount.values[1],
                df_fert.DAP.values[2], df_fert.NAmount.values[2],df_fert.DAP.values[3], df_fert.NAmount.values[3],
                df_EB.CropPrice.values[0], df_EB.NFertCost.values[0], df_EB.SeedCost.values[0], df_EB.OtherVariableCosts.values[0],
                df_EB.FixedCosts.values[0]]],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"],)
        elif fert_app == "Fert" and EB_radio == "EB_No":
            #Make a new dataframe
            df = pd.DataFrame(
                [[scenario, crop, cultivar[7:], station, planting_date[5:],start_year, end_year, soil_type, initial_soil_moisture, initial_soil_no3_content,planting_density, targetyear, 
                df_fert.DAP.values[0], df_fert.NAmount.values[0], df_fert.DAP.values[1], df_fert.NAmount.values[1],
                df_fert.DAP.values[2], df_fert.NAmount.values[2],df_fert.DAP.values[3], df_fert.NAmount.values[3],
                "-99","-99", "-99","-99", "-99"]],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"],)
        elif fert_app == "No_fert" and EB_radio == "EB_Yes":
            #Make a new dataframe
            df = pd.DataFrame(
                [[scenario, crop, cultivar[7:], station, planting_date[5:],start_year, end_year, soil_type, initial_soil_moisture, initial_soil_no3_content, planting_density,targetyear, 
                 "-99", "-99", "-99", "-99","-99", "-99","-99", "-99",
                df_EB.CropPrice.values[0], df_EB.NFertCost.values[0], df_EB.SeedCost.values[0], df_EB.OtherVariableCosts.values[0],
                df_EB.FixedCosts.values[0]]],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"],)
        else:  #no fertilizer application & No EB analyze
            df = pd.DataFrame(
                [[scenario, crop, cultivar[7:], station, planting_date[5:],start_year, end_year, soil_type, initial_soil_moisture, initial_soil_no3_content,planting_density, targetyear, 
                 "-99", "-99", "-99", "-99","-99", "-99","-99", "-99","-99","-99", "-99","-99", "-99"]],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        "CropPrice", "NFertCost", "SeedCost","OtherVariableCosts","FixedCosts"],)           
        data = df.to_dict("rows")
        # columns =  [{"name": i, "id": i,} for i in (df.columns)]

    if n_clicks == 1:
        dff = df.copy()
        data = dff.to_dict("rows")
    elif n_clicks > 1:
        # # Read previously saved scenario summaries  https://dash.plotly.com/sharing-data-between-callbacks
        # dff = pd.read_json(intermediate, orient="split")
        dff = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        dff = dff.append(df, ignore_index=True)
        data = dff.to_dict("rows")
    # print(data)
    return data
    # return dash_table.DataTable(data=data, columns=columns,row_deletable=True), dff.to_json(date_format="iso", orient="split")

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
                Output("column-dropdown", "options"), #EJ(5/19/2021) update dropdown list for sorting a datatable
                Input("simulate-button-state", "n_clicks"),
                # State("target-year", "value"),       #input 11
                # State("intermediate-value", "children") #scenario summary table
                State("scenario-table","data"), ### scenario summary table
                State("season-slider", "value"), #EJ (5/13/2021) for seasonal total rainfall
                prevent_initial_call=True,
              )

def run_create_figure(n_clicks, sce_in_table, slider_range):
    if n_clicks is None:
        raise PreventUpdate
        return 
    else: 
        # 1) Read saved scenario summaries and get a list of scenarios to run
        # dff = pd.read_json(intermediate, orient="split")
        dff = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        # print(dff)
        sce_numbers = len(dff.sce_name.values)
        # Wdir_path = "C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\"
        Wdir_path = DSSAT_FILES_DIR   #for linux system
        TG_yield = []

        #EJ(5/3/2021) run DSSAT for each scenarios with individual V47
            #EJ(5/18/2021)variables for extracting seasonal total rainfall
        m1, m2 = slider_range
        m_doys_list = [1,32,60,91,121,152,182,213,244,274,305,335]
        m_doye_list = [31,59,90,120,151,181,212,243,273,304,334,365]
        sdoy = m_doys_list[m1-1]  #first doy of the target season
        edoy = m_doye_list[m2-1]  #last doy of the target season

        for i in range(sce_numbers):
            # EJ(5/18/2021) extract seasonal rainfall total
            firstyear = int(dff.FirstYear[i])
            lastyear = int(dff.LastYear[i])
            WTD_fname = path.join(Wdir_path, dff.stn_name[i]+".WTD")
            df_obs = read_WTD(WTD_fname,firstyear, lastyear)  # === Read daily observations into a dataframe (note: Feb 29th was skipped in df_obs)
            df_season_rain = season_rain_rank(df_obs, sdoy, edoy)  #get indices of the sorted years based on SCF1 => df_season_rain.columns = ["YEAR","season_rain", "Rank"]  
            #==============end of # EJ(5/18/2021) extract seasonal rainfall total

            # 2) Write V47 file
            if dff.Crop[i] == "WH":
                temp_dv7 = path.join(Wdir_path, "DSSBatch_template_WH.V47")
            elif dff.Crop[i] == "MZ":
                temp_dv7 = path.join(Wdir_path, "DSSBatch_template_MZ.V47")
            else:  # SG
                temp_dv7 = path.join(Wdir_path, "DSSBatch_template_SG.V47")

            dv7_fname = path.join(Wdir_path, "DSSBatch.V47")
            fr = open(temp_dv7, "r")  # opens temp DV4 file to read
            fw = open(dv7_fname, "w")
            # read template and write lines
            for line in range(0, 10):
                temp_str = fr.readline()
                fw.write(temp_str)

            temp_str = fr.readline()
            sname = dff.sce_name.values[i]
            # SNX_fname = path.join(Wdir_path, "ETMZ"+sname+".SNX")
            if dff.Crop[i] == "WH":
                SNX_fname = path.join(Wdir_path, "ETWH"+sname+".SNX")
            elif dff.Crop[i] == "MZ":
                SNX_fname = path.join(Wdir_path, "ETMZ"+sname+".SNX")
            else:  # SG
                SNX_fname = path.join(Wdir_path, "ETSG"+sname+".SNX")

            # On Linux system, we don"t need to do this:
            # SNX_fname = SNX_fname.replace("/", "\\")
            new_str2 = "{0:<95}{1:4s}".format(SNX_fname, repr(1).rjust(4)) + temp_str[99:]
            fw.write(new_str2)
            fr.close()
            fw.close()
            #=====================================================================
            #3) Run DSSAT executable
            os.chdir(Wdir_path)  #change directory  #check if needed or not
            # if dff.Crop[i] == "WH":
            #     args = "DSCSM047.EXE CSCER047 B DSSBatch.v47"
            #     fout_name = path.join(Wdir_path, "ETWH"+sname+".OSU")
            # elif dff.Crop[i] == "MZ":
            #     args = "DSCSM047.EXE MZCER047 B DSSBatch.v47"
            #     fout_name = path.join(Wdir_path, "ETMZ"+sname+".OSU")
            # else:  # SG
            #     args = "DSCSM047.EXE SGCER047 B DSSBatch.v47"
            #     fout_name = path.join(Wdir_path, "ETSG"+sname+".OSU")
            # subprocess.call(args) ##Run executable with argument  , stdout=FNULL, stderr=FNULL, shell=False)
            #===========>for linux system
            if dff.Crop[i] == "WH":
                args = "./DSCSM047.EXE CSCER047 B DSSBatch.V47"
                # args = "./DSCSM047.EXE B DSSBatch.V47"
                fout_name = "ETWH"+sname+".OSU"
                arg_mv = "cp Summary.OUT "+ "ETWH"+sname+".OSU" #"cp Summary.OUT $fout_name"
                # fout_name = path.join(Wdir_path, "ETWH"+sname+".OSU")
            elif dff.Crop[i] == "MZ":
                args = "./DSCSM047.EXE MZCER047 B DSSBatch.V47"
                fout_name = "ETMZ"+sname+".OSU"
                arg_mv = "cp Summary.OUT "+ "ETMZ"+sname+".OSU" #"cp Summary.OUT $fout_name"
                # fout_name = path.join(Wdir_path, "ETMZ"+sname+".OSU")
            else:  # SG
                args = "./DSCSM047.EXE SGCER047 B DSSBatch.V47"
                fout_name = "ETSG"+sname+".OSU"
                arg_mv = "cp Summary.OUT "+ "ETSG"+sname+".OSU"# "cp Summary.OUT $fout_name"
                # fout_name = path.join(Wdir_path, "ETSG"+sname+".OSU")

            os.system(args) 
            os.system(arg_mv) 
            #===========>end of for linux system

            #4) read DSSAT output => Read Summary.out from all scenario output
            # fout_name = path.join(Wdir_path, "SUMMARY.OUT")
            df_OUT=pd.read_csv(fout_name,delim_whitespace=True ,skiprows=3)
            HWAM = df_OUT.iloc[:,20].values  #read 21th column only
            EXPERIMENT = df_OUT.iloc[:,7].values  #read 4th column only
            PDAT = df_OUT.iloc[:,13].values  #read 14th column only
            ADAT = df_OUT.iloc[:,15].values  #read 14th column only
            MDAT = df_OUT.iloc[:,16].values  #read 14th column only    
            YEAR = df_OUT.iloc[:,13].values//1000
            if int(dff.TargetYr[i]) <= int(dff.LastYear[i]):
                doy = repr(PDAT[0])[4:]
                target = dff.TargetYr[i] + doy
                yr_index = np.argwhere(PDAT == int(target))
                # print("target year:", int(dff.TargetYr[i]) )
                # print("last sim year:", int(dff.LastYear[i]))
                # print("PDAT:", PDAT)
                # print("target:", target)
                # print("yr_index:", yr_index[0][0])
                TG_yield_temp = HWAM[yr_index[0][0]]
            else: 
                TG_yield_temp = np.nan

            # Make a new dataframe for plotting
            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT, "HWAM":HWAM,"RAIN":df_season_rain.season_rain.values,"RANK":df_season_rain.Rank.values}
            temp_df = pd.DataFrame (data, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM", "RAIN", "RANK"])

            if i==0:
                df = temp_df.copy()
            else:
                df = df.append(temp_df, ignore_index=True)
                
            TG_yield.append(TG_yield_temp)

        df = df.round({"RAIN": 0})  #Round a DataFrame to a variable number of decimal places.
        yield_min = np.min(df.HWAM.values)  #to make a consistent yield scale for exceedance curve =>Fig 4,5,6
        yield_max = np.max(df.HWAM.values)
        x_val = np.unique(df.EXPERIMENT.values)
        # print(df)
        # print("x_val={}".format(x_val))
        #4) Make a boxplot
        # df = px.data.tips()
        # fig = px.box(df, x="time", y="total_bill")
        # fig.show()s
        # fig.update_layout(transition_duration=500)
        # df = px.data.tips()
        # fig = px.box(df, x="Scenario Name", y="Yield [kg/ha]")
        fig = px.box(df, x="EXPERIMENT", y="HWAM", title="Yield Boxplot")
        fig.add_scatter(x=x_val,y=TG_yield, mode="markers") #, mode="lines+markers") #"lines")
        fig.update_xaxes(title= "Scenario Name [*Note:Red dot(s) represents yield(s) based on the weather of target year]")
        fig.update_yaxes(title= "Yield [kg/ha]")
        # # return fig

        fig2 = go.Figure()
        for i in x_val:
            x_data = df.HWAM[df["EXPERIMENT"]==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            fig2.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode="lines+markers",
                        name=i[4:]))
        # Edit the layout
        fig2.update_layout(title="Yield Exceedance Curve",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]")

        #make a new dataframe to save into CSV
        yr_val = np.unique(df.YEAR.values)
        df_out = pd.DataFrame({"YEAR":yr_val})

        fig3 = go.Figure()
        fig4 = go.Figure() #yield exceedance curve using only BN category
        fig5 = go.Figure()  #yield exceedance curve using only NN category
        fig6 = go.Figure()  #yield exceedance curve using only AN category
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

            fig3.add_trace(go.Scatter(x=x_data, y=y_data,
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
            fig4.add_trace(go.Scatter(x=x_data, y=Fx_scf, mode="lines+markers", name=i[4:]))
            #2)NN
            mask = np.logical_and(rain_rank > BN_thres, rain_rank <= NN_thres)
            x_data = y_data[mask]
            # x_data = y_data[rain_rank > BN_thres & rain_rank <= NN_thres]
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve
            fig5.add_trace(go.Scatter(x=x_data, y=Fx_scf, mode="lines+markers", name=i[4:]))
            #3)AN
            x_data = y_data[rain_rank > NN_thres]
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve
            fig6.add_trace(go.Scatter(x=x_data, y=Fx_scf, mode="lines+markers", name=i[4:]))
            #====================================================                
        # Edit the layout
        fig3.update_layout(title="Yield Time-Series",
                        xaxis_title="Year",
                        yaxis_title="Yield [kg/ha]")
        fig4.update_layout(title="Yield Exceedance [Dry category]",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        fig4.update_xaxes(range=[yield_min, yield_max])
        fig5.update_layout(title="Yield Exceedance [Normal category]",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        fig5.update_xaxes(range=[yield_min, yield_max])
        fig6.update_layout(title="Yield Exceedance [Wet category]",
                        xaxis_title="Yield [kg/ha]",
                        yaxis_title="Probability of Exceedance [-]",
                        legend=dict(yanchor="bottom", y=0.1, xanchor="left", x=0.01))
        fig6.update_xaxes(range=[yield_min, yield_max])

        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_yield.csv")
        df_out.to_csv(fname, index=False)
        #print({"label": i, "value": i} for i in list(df_out.columns))

        return [
            dcc.Graph(id="yield-boxplot",figure=fig), 
            dcc.Graph(id="yield-exceedance",figure=fig2),
            dcc.Graph(id="yield-ts",figure=fig3),
            dcc.Graph(id="yield-BN_exceedance",figure=fig4),
            dcc.Graph(id="yield-NN_exceedance",figure=fig5),
            dcc.Graph(id="yield-AN_exceedance",figure=fig6),
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in df_out.columns],data=df_out.to_dict("records"),
                style_table={"overflowX": "auto"}, 
                style_cell={   # all three widths are needed
                    "minWidth": "10px", "width": "10px", "maxWidth": "30px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis", }),
            df_out.to_dict("records"),
            [{"label": i, "value": i} for i in list(df_out.columns)]
            ]
#==============================================================
#==============================================================
#Dynamic call back for update dropdown values, before datatable filtering by col name
# @app.callback(
#     Output("column-dropdown", "options"),
#     Input("btn_table_sort", "n_clicks"),
#     State("memory-yield-table", "data"),
#     prevent_initial_call=True,
#     )
# def set_column_options(n_clicks, yield_table):
#     df =pd.DataFrame(yield_table)
#     return [{"label": i, "value": i} for i in list(df.columns)]
#==============================================================
#==============================================================
@app.callback(
    Output("column-dropdown", "value"),
    Input("column-dropdown", "options"))
def set_column_value(available_options):
    # print(available_options)
    # return cultivar_options[0]["value"]
    return [available_options[i]["value"] for i in range(len(available_options))]

#Last callback to create figures for Enterprise budgeting
@app.callback(Output(component_id="EBbox-container", component_property="children"),
                Output(component_id="EBcdf-container", component_property="children"),
                Output(component_id="EBtimeseries-container", component_property="children"),
                Output(component_id="EBtables-container", component_property="children"),
                Output("memory-EB-table", "data"),
                Input("EB-button-state", "n_clicks"),
                State("scenario-table","data") ### scenario summary table
              )

def EB_figure(n_clicks, sce_in_table):
    if n_clicks is None:
        raise PreventUpdate
        return 
    else: 
        # 1) Read saved scenario summaries and get a list of scenarios to run
        dff = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        # print("Callback EB_figure:", dff)
        # print("Callback EB_figure:", sce_in_table)
        sce_numbers = len(dff.sce_name.values)
        # Wdir_path = "C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\"
        Wdir_path = DSSAT_FILES_DIR  #for linux system
        os.chdir(Wdir_path)  #change directory  #check if needed or not
        TG_GMargin = []

        #EJ(5/3/2021) Read DSSAT output for each scenarios
        for i in range(sce_numbers):
            sname = dff.sce_name.values[i]
            if dff.Crop[i] == "WH":
                fout_name = path.join(Wdir_path, "ETWH"+sname+".OSU")
            elif dff.Crop[i] == "MZ":
                fout_name = path.join(Wdir_path, "ETMZ"+sname+".OSU")
            else:  # SG
                fout_name = path.join(Wdir_path, "ETSG"+sname+".OSU")

            #4) read DSSAT output => Read Summary.out from all scenario output
            df_OUT=pd.read_csv(fout_name,delim_whitespace=True ,skiprows=3)
            HWAM = df_OUT.iloc[:,20].values  #read 21th column only
            EXPERIMENT = df_OUT.iloc[:,7].values  #read 4th column only
            PDAT = df_OUT.iloc[:,13].values  #read 14th column only
            ADAT = df_OUT.iloc[:,15].values  #read 14th column only
            MDAT = df_OUT.iloc[:,16].values  #read 14th column only    
            YEAR = df_OUT.iloc[:,13].values//1000
            NICM = df_OUT.iloc[:,39].values  #read 40th column only,  #NICM   Tot N app kg/ha Inorganic N applied (kg [N]/ha)
            HWAM[HWAM < 0]=0 #==> if HWAM == -99, consider it as "0" yield (i.e., crop failure)
            #Compute gross margin
            GMargin=HWAM*float(dff.CropPrice[i])- float(dff.NFertCost[i])*NICM - float(dff.SeedCost[i]) - float(dff.OtherVariableCosts[i]) - float(dff.FixedCosts[i])
            # GMargin_data[0:len(HWAM),x]
            if int(dff.TargetYr[i]) <= int(dff.LastYear[i]):
                doy = repr(PDAT[0])[4:]
                target = dff.TargetYr[i] + doy
                yr_index = np.argwhere(PDAT == int(target))
                TG_GMargin_temp = GMargin[yr_index[0][0]]
            else: 
                TG_GMargin_temp = np.nan

            # # Make a new dataframe for plotting
            # df1 = pd.DataFrame({"EXPERIMENT":EXPERIMENT})
            # df2 = pd.DataFrame({"PDAT":PDAT})
            # df3 = pd.DataFrame({"ADAT":ADAT})
            # df4 = pd.DataFrame({"HWAM":HWAM})
            # df5 = pd.DataFrame({"YEAR":YEAR})
            # df6 = pd.DataFrame({"NICM":NICM})
            # df7 = pd.DataFrame({"GMargin":GMargin})
            # temp_df = pd.concat([df1.EXPERIMENT,df5.YEAR, df2.PDAT, df3.ADAT, df4.HWAM, df6.NICM, df7.GMargin], ignore_index=True, axis=1)

            data = {"EXPERIMENT":EXPERIMENT, "YEAR":YEAR, "PDAT": PDAT, "ADAT":ADAT, "HWAM":HWAM,"NICM":NICM, "GMargin":GMargin, "RAIN":df_season_rain.season_rain.values,"RANK":df_season_rain.Rank.values}
            temp_df = pd.DataFrame (data, columns = ["EXPERIMENT","YEAR", "PDAT","ADAT","HWAM", "RAIN", "RANK"])

            if i==0:
                df = temp_df.copy()
            else:
                df = df.append(temp_df, ignore_index=True)

            TG_GMargin.append(TG_GMargin_temp)

        # adding column name to the respective columns
        df.columns =["EXPERIMENT", "YEAR","PDAT", "ADAT","HWAM","NICM","GMargin"]
        x_val = np.unique(df.EXPERIMENT.values)
        # print(df)
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
            dcc.Graph(id="EB-boxplot",figure=fig), 
            dcc.Graph(id="EB-exceedance",figure=fig2),
            dcc.Graph(id="EB-ts",figure=fig3),
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in df_out.columns],
                data=df_out.to_dict("records"),
                style_cell={"whiteSpace": "normal","height": "auto",},),
            df_out.to_dict("records")
            ]

# =============================================
# def writeSNX_main_hist(Wdir_path,station,start_year,end_year,planting_date,cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,planting_density,scenario):
def writeSNX_main_hist(Wdir_path,station,start_year,end_year,planting_date,crop,cultivar,soil_type,initial_soil_moisture,initial_soil_no3_content,
                       planting_density,scenario,fert_app, df_fert):    
    # print("check writeSNX_main")
    # print(station)  #MELK
    # print(start_year)  #1981
    # print(end_year)  #2014
    # print(planting_date)  #2021-06-15
    # print(crop)  #MZ crop type
    # print(cultivar)  #CIMT01 BH540-Kassie
    # print(soil_type)  #ETET001_18
    # print(initial_soil_moisture)  #0.7
    # print(initial_soil_no3_content)  #H
    # print(planting_density)  #6
    # print(scenario)  #scenario name
    WSTA = station
    NYERS = repr(int(end_year) - int(start_year) + 1)
    plt_year = start_year
    if planting_date is not None:
        date_object = date.fromisoformat(planting_date)
        date_string = date_object.strftime("%B %d, %Y")
        plt_doy = date_object.timetuple().tm_yday
        # print(date_string)  #June 15, 2021 
        # print(plt_doy)  #166
    PDATE = plt_year[2:] + repr(plt_doy).zfill(3)
        #   IC_date = first_year * 1000 + (plt_doy - 1)
        #   PDATE = repr(first_year)[2:] + repr(plt_doy).zfill(3)
        # ICDAT = repr(IC_date)[2:]
    ICDAT = plt_year[2:] + repr(plt_doy-1).zfill(3)  #Initial condition => 1 day before planting
    SDATE = ICDAT
    INGENO = cultivar[0:6]  
    CNAME = cultivar[7:]  
    ID_SOIL = soil_type
    PPOP = planting_density  #planting density
    i_NO3 = initial_soil_no3_content  # self.label_04.cget("text")[0:1]  #self.NO3_soil.getvalue()[0][0:1] #"H" #or "L"
    IC_w_ratio = float(initial_soil_moisture)
    # crop = "MZ" #EJ(1/6/2021) temporary

    #1) make SNX
    if crop == "WH":
        temp_snx = path.join(Wdir_path, "TEMP_ETWH.SNX")
        snx_name = "ETWH"+scenario[:4]+".SNX"
    elif crop == "MZ":
        temp_snx = path.join(Wdir_path, "TEMP_ETMZ.SNX")
        snx_name = "ETMZ"+scenario[:4]+".SNX"
    else:  # SG
        temp_snx = path.join(Wdir_path, "TEMP_ETSG.SNX")
        snx_name = "ETSG"+scenario[:4]+".SNX"
    # # temp_snx = path.join(Wdir_path, "ETMZTEMP.SNX")
    # temp_snx = path.join(Wdir_path, "TEMP_ETMZ.SNX")
    # snx_name = "ETMZ"+scenario[:4]+".SNX"
    SNX_fname = path.join(Wdir_path, snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    # read lines 1-9 from temp file
    for line in range(0, 14):
        temp_str = fr.readline()
        fw.write(temp_str)

    MI = "0" 
    if fert_app == "Fert":
        MF = "1"
    else: 
        MF = "0"
    # MF = "1"
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
    SOL_file = path.join(Wdir_path, "ET.SOL")
    # soil_depth, wp, fc, nlayer = get_soil_IC(SOL_file, ID_SOIL)
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
    temp_str = fr.readline()
    for nline in range(0, nlayer):
        if nline == 0:  # first layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "15"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # i_NO3 == "L":
                SNO3 = "5"  # **EJ(5/27/2015)
        elif nline == 1:  # second layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == "H":
                SNO3 = "2"  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # elif i_NO3 == "L":
                SNO3 = ".5"  # **EJ(4/29/2020) used one constant number regardless of soil types
        else:
            temp_SH2O = fc[nline]  # float
            SNO3 = "0"  # **EJ(5/27/2015)
        SH2O = repr(temp_SH2O)[0:5]  # convert float to string
        new_str = temp_str[0:5] + repr(soil_depth[nline]).rjust(3) + " " + SH2O.rjust(5) + temp_str[14:22] + SNO3.rjust(4) + "\n"
        fw.write(new_str)
    fw.write("  \n")
    # print("ICDAT= {0}".format(ICDAT))  #test here
    # print("fc[0]= {0}".format(fc[0] ))  #test here
    # print("test after writing init")  #test here
    for nline in range(0, 10):
        temp_str = fr.readline()
        # print temp_str
        if temp_str[0:9] == "*PLANTING":
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
    # print("PPOE = {0}".format(PPOE))  #test here
    # write *IRRIGATION AND WATER MANAGEMENT, if irrigation on reported dates
    # skip irrigation for now   #EJ(1/6/2021) temporary

    # write *FERTILIZERS (INORGANIC)
    #get fertilizer info using dash_table.DataTable(https://dash.plotly.com/datatable/callbacks
    #use editable datatable https://dash.plotly.com/datatable/editable
    for nline in range(0, 20):
        temp_str = fr.readline()
        # print temp_str
        if temp_str[0:12] == "*FERTILIZERS":
            break
    fw.write(temp_str)  # *FERTILIZERS (INORGANIC)
    temp_str = fr.readline()  # @F FDATE  FMCD  FACD 
    fw.write(temp_str)
    temp_str = fr.readline()  #1     0 FE005 AP001     5    30   -99   -99   -99   -99   -99   -99
#-0------------        # write *FERTILIZERS (INORGANIC)
    if fert_app == "Fert":
        # print(df_fert)
        df_fert = df_fert.astype(float)
        df_filtered = df_fert[(df_fert["DAP"] >= 0) & (df_fert["NAmount"] >= 0)]
        fert_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        FDATE = df_filtered.DAP.values
        FMCD = "FE005"  #Urea
        FACD = "AP001"  #Broadcast, not incorporated    
        FDEP = "5"   #5cm depth
        FAMN = df_filtered.NAmount.values
        FAMP = "-99"
        FAMK = "-99"

        if fert_count > 0:   # fertilizer applied
            for i in range(fert_count):
                new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + " " + FMCD.rjust(5) + " " + FACD.rjust(5) + " " + FDEP.rjust(5) + " " + repr(FAMN[i]).rjust(5) + " " + FAMP.rjust(5) + " " + FAMK.rjust(5) + temp_str[44:]
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
        # print temp_str
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
    fw.write(" 1 OP              Y     Y     Y     N     N     N     N     N     D"+ "\n")
    temp_str = fr.readline()  # @N METHODS
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 ME
    fw.write(temp_str)
    temp_str = fr.readline()  # @N MANAGEMENT
    fw.write(temp_str)
    temp_str = fr.readline()  # 1 MA
    # new_str = temp_str[0:25] + IRRIG + temp_str[26:31] + FERTI + temp_str[32:]
    # fw.write(new_str)
    fw.write(temp_str)
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
#===============================================================
# if __name__ == "__main__":
#     # app.run_server(debug=True)
#     app.run_server(debug=False)  #https://github.com/plotly/dash/issues/108

#===>for linux system
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run_server(debug=False,
                   host="0.0.0.0",
                   port=port)
#===>end of for linux system