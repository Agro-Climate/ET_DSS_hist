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

app = dash.Dash(
    __name__,
  #  meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    prevent_initial_callbacks=True,  #to prevent "Callback failed: the server did not respond." message thttps://community.plotly.com/t/callback-error-when-the-app-is-started/46345/2
)

server = app.server

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

DSSAT_FILES_DIR_SHORT = "/dssat_files_dir/"

DSSAT_FILES_DIR = os.getcwd() + DSSAT_FILES_DIR_SHORT

# # Testing
# os.chdir(DSSAT_FILES_DIR)
# args = "./DSCSM047.EXE CSCER047 B DSSBatch.V47"
# os.system(args) 

#https://community.plotly.com/t/loading-when-opening-localhost/7284
#I suspect that this is related to the JS assets from the CDN not loading properly - perhaps because they are blocked by your firewall or some other reason.
#You can load the assets locally by setting:
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

#column names for scenario summary table:EJ(5/3/2021)
sce_col_names=["sce_name", "Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","TargetYr",
                 "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                 'CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts']

cultivar_options = {
    'MZ': ["CIMT01 BH540-Kassie","CIMT02 MELKASA-Kassi","CIMT17 BH660-FAW-40%", "CIMT19 MELKASA2-FAW-40%", "CIMT21 MELKASA-LowY"],
    'WH': ["CI2021 KT-KUB", "CI2022 RMSI", "CI2023 Meda wolabu", "CI2024 Sofumer", "CI2025 Hollandi"],
    'SG': ["IB0020 ESH-1","IB0020 ESH-2","IB0027 Dekeba","IB0027 Melkam","IB0027 Teshale"]
}
Wdir_path = DSSAT_FILES_DIR
app.layout = html.Div(
    [
        dcc.Store(id='memory-yield-table'),  #to save fertilizer application table
        dcc.Store(id='memory-EB-table'),  #to save fertilizer application table
        html.Div(
            dbc.Row([html.Img(src=app.get_asset_url("ethioagroclimate.png"))], className="app__banner")
            # [html.Img(src=app.get_asset_url("ethioagroclimate.png"))], className="app__banner"
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Climate-Agriculture Modeling Decision Support Tool for Ethiopia (Historical Analysis)",
                            className="uppercase title"
                        ),
                    ],
                    className="app__header",
                    ),
                html.Br(),
                html.Div(children='''
                    CAMDT is a tool designed to guide decision-makers in adopting appropriate crop and management practices that can improve crop yields given a seasonal climatic condition.
                ''', style={'textAlign': 'Left'}),
                # html.Span("CAMDT  ", className="uppercase bold", style={'textAlign': 'Center'}),
                # html.Span(
                #     "is a tool designed to guide decision-makers in adopting appropriate crop and management practices that can improve crop yields given a seasonal climatic condition."
                #     , style={'textAlign': 'Center'}
                # ),
                html.Br(),
                html.Div(children='''
                    Smart planning of annual crop production requires consideration of possible scenarios.
                    The CAMDT tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
                    The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
                    in collaboration with the Ethiopian Institute of Agricultural Research (EIAR). 
                    The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
                    and evaluation of long-term effects, considering interactions of various factors.
                ''', style={'textAlign': 'Left'}),

            ]),
        html.Br(),
        html.Div(children = [
            dbc.Row([
                dbc.Col(html.Span("1) Select a crop to simulate", className="uppercase bold"),width="auto"),
                ]),
            # dcc.Dropdown(id='CropType', options=[{'label': 'Maize', 'value': 'MZ'}], #,{'label': 'Wheat', 'value': 'WH'},{'label': 'Sorghum', 'value': 'SG'}],
            #         value='MZ'),
            dcc.RadioItems(
                id='crop-radio',
                # options=[{'label': k, 'value': k} for k in cultivar_options.keys()],
                options = [{'label': 'Maize', 'value': 'MZ'}, {'label': 'Wheat', 'value': 'WH'}, {'label': 'Sorghum', 'value': 'SG'},],

                labelStyle = {'display': 'inline-block','margin-right': 10},
                value='MZ'
                ),
            ], style={"width": "50%"},),
            
        html.Br(),
        html.Div([
            dbc.Row([
                dbc.Col(html.Span("2) Select a station name for analysis", className="uppercase bold"),width="auto"),
                ]),
            dcc.Dropdown(id='ETstation', options=[{'label': 'Melkasa', 'value': 'MELK'},{'label': 'Awassa', 'value': 'AWAS'},{'label': 'Bako', 'value': 'BAKO'},{'label': 'Mahoni', 'value': 'MAHO'}],
                    value='MELK')
            ],style={"width": "50%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                dbc.Col(html.Span("3) Type years to simulate", className="uppercase bold")),
                ]),
            dbc.Row([
                dbc.Col(html.Span("*Note: Available years are from 1981 to 2018")),
                ]),
            html.Span("From [YYYY] "),
            dcc.Input(id="year1", type="text", placeholder="Enter first year to simulate", value = '1981'),
            html.Span("  to [YYYY] "),
            dcc.Input(id="year2", type="text", placeholder="Enter last year to simulate", value = '2018'),    
            html.Br(),                 
            ]),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("4) Select Planting Date", className="uppercase bold", style={'textAlign': 'Center'}),
                ],align="start",
                ),
            dbc.Row([
                html.Span("Only Monthly and Date are counted (i.e., selected year is ignored)"),
                ],align="start",
                ),
            dbc.Row([
                dbc.Col(
                    dcc.DatePickerSingle(
                    id='plt-date-picker',
                    min_date_allowed=date(2021, 1, 1),
                    max_date_allowed=date(2021, 12, 31),
                    initial_visible_month=date(2021, 6, 5),
                    date=date(2021, 6, 15)
                    ),align="start"),
                ],align="start",
                ),
            # ],style={'columnCount': 2}),
            ]),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("5) Select Cultivar to simulate", className="uppercase bold"), #, style={'textAlign': 'Center'}),
                ]),
            dbc.Row([
                # dcc.Dropdown(id='ETMZcultivar', options=[{'label': 'CIMT01 BH540-Kassie', 'value': 'CIMT01 BH540-Kassie'},
                #                                         {'label': 'CIMT02 MELKASA-Kassi', 'value': 'CIMT02 MELKASA-Kassi'},
                #                                         {'label': 'CIMT17 BH660-FAW-40%', 'value': 'CIMT17 BH660-FAW-40%'},
                #                                         {'label': 'CIMT19 MELKASA2-FAW-40%', 'value': 'CIMT19 MELKASA2-FAW-40%'},
                #                                         {'label': 'CIMT21 MELKASA-LowY', 'value': 'CIMT21 MELKASA-LowY'},], 
                #             value='CIMT01 BH540-Kassie'),
                # dcc.Dropdown(id='cultivar-dropdown'),
                dcc.Dropdown(id='cultivar-dropdown', options=[{'label': 'CIMT01 BH540-Kassie', 'value': 'CIMT01 BH540-Kassie'},
                                                        {'label': 'CIMT02 MELKASA-Kassi', 'value': 'CIMT02 MELKASA-Kassi'},
                                                        {'label': 'CIMT17 BH660-FAW-40%', 'value': 'CIMT17 BH660-FAW-40%'},
                                                        {'label': 'CIMT19 MELKASA2-FAW-40%', 'value': 'CIMT19 MELKASA2-FAW-40%'},
                                                        {'label': 'CIMT21 MELKASA-LowY', 'value': 'CIMT21 MELKASA-LowY'},], 
                            value='CIMT01 BH540-Kassie'),
                ],align="start",
                ),
            # ],style={'columnCount': 2}),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("6) Select Soil type to simulate", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.Dropdown(id='ETsoil', options=[{'label': 'ETET000010(AWAS,L)', 'value': 'ETET000010'},
                                                    {'label': 'ETET000_10(AWAS,L, shallow)', 'value': 'ETET000_10'},
                                                    {'label': 'ETET000011(BAKO,C)', 'value': 'ETET000011'},
                                                    {'label': 'ETET001_11(BAKO,C,shallow)', 'value': 'ETET001_11'},
                                                    {'label': 'ETET000018(MELK,L)', 'value': 'ETET000018'},
                                                    {'label': 'ETET001_18(MELK,L,shallow)', 'value': 'ETET001_18'},
                                                    {'label': 'ETET000015(KULU,C)', 'value': 'ETET000015'},
                                                    {'label': 'ETET001_15(KULU,C,shallow)', 'value': 'ETET001_15'},
                                                    {'label': 'ET00990066(MAHO,C)', 'value': 'ET00990066'},
                                                    {'label': 'ET00990_66(MAHO,C,shallow)', 'value': 'ET00990_66'},
                                                    {'label': 'ET00920067(KOBO,CL)', 'value': 'ET00920067'},
                                                    {'label': 'ET00920_67(KOBO,CL,shallow)', 'value': 'ET00920_67'},
                                                    {'label': 'ETET000022(MIES, C)', 'value': 'ETET000022'},
                                                    {'label': 'ETET001_22(MIES, C, shallow', 'value': 'ETET001_22'},
                                                    ], 
                            value='ETET001_18'),
                ],align="start",
                ),
            # ],style={'columnCount': 2}),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("7) Select initial soil water condition", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.Dropdown(id='ini-H2O', options=[{'label': '30% of AWC', 'value': '0.3'},
                                                    {'label': '50% of AWC', 'value': '0.5'},
                                                    {'label': '70% of AWC', 'value': '0.7'},
                                                    {'label': '100% of AWC', 'value': '1.0'},], 
                            value='0.7'),
                ],align="start",
                ),
            ],style={"width": "50%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("8) Select initial NO3 condition", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.Dropdown(id='ini-NO3', options=[{'label': 'High(65 N kg/ha)', 'value': 'H'},
                                                    {'label': 'Low(23 N kg/ha)', 'value': 'L'},], 
                            value='H'),
                ],align="start",
                ),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("9) Enter Planting Density", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.Input(id="plt-density", type="text", placeholder="Enter planting density"),
                # html.Span(" [plants / m<sup>2</sup> ]"),
                html.Span(" [plants / m"),
                html.Span("2", style={'vertical-align': 'super'}),
                html.Span("] "),
                ],align="start",
                ),
            ],style={"width": "80%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("10) Fertilizer Application", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                html.Span("*Note: DAP(days after planting), Amount (N kg/ha)"),
                ],align="start",
                ),
            dbc.Row([
                dcc.RadioItems(id="fert_input",
                    options=[
                        {'label': 'Fertilizer', 'value': 'Fert'},
                        {'label': 'No Fertilizer', 'value': 'No_fert'},],
                    value='No_fert'),
                    ],align="start",
                ),
            ],style={"width": "80%"},),
        html.Br(),
        # html.Div(id="fert-table",style={"width": "40%"}),
        html.Div([
            dash_table.DataTable(id='fert-table',
                style_cell = {
                'font_family': 'sans-serif', #'cursive',
               #'minWidth': '50px', 'width': '50px', 'maxWidth': '50px',
                'whiteSpace': 'normal',
                'font_size': '14px',
                'text_align': 'center'},
                columns=(
                    [{'id': p, 'name': p} for p in ['DAP', 'NAmount']]
                ),
                data=[
                    dict(**{param: -99 for param in ['DAP', 'NAmount']}) for i in range(1, 5)
                    # dict(**{param: 0 for param in params}) for i in range(1, 5)
                ],
                style_cell_conditional=[
                    {'if': {'id': 'DAP'},
                    'width': '30%'},
                    {'if': {'id': 'NAmount'},
                    'width': '30%'},
                ],
                editable=True)
                # row_deletable=True)  
                # fill_width=False, editable=True)
                ],id='fert-table-Comp', style={"width": "20%",'display': 'none'},), # 'display': 'block'
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("11) Enter a Scenario name ", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.Input(id="sce-name", type="text", placeholder="Enter a scenario name.."),
                html.Span("(only 4 characters)"),
                ],align="start",
                ),
            ],style={"width": "60%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("12) Target year to compare with ", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.Input(id="target-year", type="text", placeholder="Enter a specific year.."),
                html.Span("[YYYY]"),
                ],align="start",
                ),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("13) Simple Enterprise Budgeting?", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.RadioItems(id="EB_radio",
                    options=[
                        {'label': 'Yes', 'value': 'EB_Yes'},
                        {'label': 'No', 'value': 'EB_No'},],
                    value='EB_No'),
                    ],align="start",
                ),
            ],style={"width": "50%"},),
        html.Br(),
        html.Div([
            dbc.Row([
            dash_table.DataTable(id='EB-table',
                style_cell = {
                'font_family': 'sans-serif', #'cursive',
                'whiteSpace': 'normal',
                'font_size': '14px',
                'text_align': 'center'},
                columns=(
                    [{'id': p, 'name': p} for p in ['CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts']]
                ),
                data=[
                    dict(**{param: -99 for param in ['CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts']}) for i in range(1, 2)
                ],
                style_cell_conditional=[
                    {'if': {'id': 'CropPrice'},
                    'width': '20%'},
                    {'if': {'id': 'NFertCost'},
                    'width': '20%'},
                ],
                editable=True)
            ]),
            dbc.Row([
                html.Span("Unit: CropPrice[Birr/kg], NFertCost[Birr/N kg], SeedCost [Birr/kg], OtherVariableCosts[Birr/ha], FixedCosts[Birr/ha]"),
                ],align="start",
                ),
            dbc.Row([
                html.Span(" Calculation =>  Gross Margin [Birr/ha] = Revenues [Birr/ha] - Variable Costs [Birr/ha] - Fixed Costs [Birr/ha]"),
                ],align="start",
                ),
            dbc.Row([
                html.Span("  - Revenues [Birr/ha] = Yield [kg/ha] * Crop Price [Birr/kg]"),
                ],align="start",
                ),  
            dbc.Row([
                html.Span("  - Variable costs for fertilizer [Birr/ha] = N Fertilizer amount [N kg/ha] * cost [Birr/N kg]"),
                ],align="start",
                ),  
            dbc.Row([
                html.Span("  - Variable costs for seed purchase [Birr/ha]"), # = Planting Density in #9 [plants/m2] *10000 [m2/ha]* Seed Cost [Birr/plant]"),
                ],align="start",
                ),  
            dbc.Row([
                html.Span(" **(reference: the price of hybrid maize seed from the MOA was about 600 Birr/100 kg compared to 50-80 Birr/100 kg for local maize seed purchased in the local market (Birr 7 = US$ 1)."),
                ],align="start",
                ),  
            dbc.Row([
                html.Span("  - Other variable costs [Birr/ha] may include pesticide, insurance, labor etc."),
                ],align="start",
                ), 
            dbc.Row([
                html.Span("  - Fixed costs [Birr/ha] may include interests for land, machinery etc."),
                ],align="start",
                ), 
                ],id='EB-table-Comp', style={"width": "20%",'display': 'none'},), # 'display': 'block'
        html.Br(),       
        html.Div([
            html.Button(id='write-button-state', n_clicks=0, children='Create or Add a new Scenario', 
                style={"width": "50%",'background-color': '#4CAF50'}),  #https://www.w3schools.com/css/css3_buttons.asp
        ],),
        html.Br(),   
        # Deletable summary table : EJ(5/3/2021)
        html.Div([
            dash_table.DataTable(id='scenario-table',
                columns=(
                    [{'id': p, 'name': p} for p in sce_col_names]
                ),
                data=[
                    dict(**{param: 'N/A' for param in sce_col_names}) for i in range(1, 2)
                ],
                editable=True,
                row_deletable=True) 
                # fill_width=False, editable=True)
                ],id='sce-table-Comp', style={"width": "100%",'display': 'block'},), # 'display': 'block', 'none'
        html.Br(),
        # end of Deletable summary table : EJ(5/3/2021)

        html.Br(),
        html.Div([
            html.Button(id='simulate-button-state', children='Simulate all scenarios (Run DSSAT)',style={"width": "50%",'background-color': '#008CBA'}), #blue
        ],),
        html.Br(),
        # dbc.Progress("25%", value=25),
        # dbc.Progress(id="progress"),
       # dbc.Spinner(children=[dcc.Graph(id = 'yield_boxplot')],size='lg',color='primary',type='border'),
        #dcc.Graph(id='yield_boxplot'),
        #EJ(4/17/2021)example:https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/DataTable/datatable_intro_and_sort.py
        dbc.Spinner(children=[html.Div(id='yieldbox-container')], size="lg", color="primary", type="border", fullscreen=True,),
        # html.Div(id='yieldbox-container'),  #boxplot
        html.Div(id='yieldcdf-container'),  #exceedance curve
        html.Div(id='yieldtimeseries-container'),  #time-series
        html.Br(),
        html.Button("Download CSV file for Simulated Yield", id="btn_csv"),
        # dcc.Download(id="download-dataframe-csv"),
        Download(id="download-dataframe-csv"),
        html.Div(id='yieldtables-container', style = {'width': '50%'}),  #yield simulated output
        html.Br(),
        html.Div([
            html.Button(id='EB-button-state', children='Display figures for Enterprise Budgets',style={"width": "50%",'background-color': '#f44336'}), #red
        ],),
        html.Br(),
        html.Div(id='EBbox-container'), 
        html.Div(id='EBcdf-container'),  #exceedance curve
        html.Div(id='EBtimeseries-container'), #exceedance curve
        html.Br(),
        html.Button("Download CSV file for Enterprise Budgeting", id="btn_csv_EB"),
        # dcc.Download(id="download-dataframe-csv"),
        Download(id="download-dataframe-csv_EB"),
        html.Div(id='EBtables-container', style = {'width': '50%'}),   #yield simulated output
        html.Br()
    ])
#==============================================================
#Dynamic call back for different cultivars for a selected target crop
@app.callback(
    Output('cultivar-dropdown', 'options'),
    Input('crop-radio', 'value'))
def set_cultivar_options(selected_crop):
    return [{'label': i, 'value': i} for i in cultivar_options[selected_crop]]

@app.callback(
    Output('cultivar-dropdown', 'value'),
    Input('cultivar-dropdown', 'options'))
def set_cultivar_value(available_options):
    return cultivar_options[0]['value']
#==============================================================
#call back to save df into a csv file
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State('memory-yield-table', 'data'),
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
    State('memory-EB-table', 'data'),
    prevent_initial_call=True,
)
def func(n_clicks, EB_data):
    # print(EB_data)
    df =pd.DataFrame(EB_data)
    return dcc.send_data_frame(df.to_csv, "simulated_yield_EB.csv")
#=================================================   
#call back to "show/hide" fertilizer input table
@app.callback(Output('fert-table-Comp', component_property='style'),
              Input('fert_input', component_property='value'))
def show_hide_table(visibility_state):
    if visibility_state == 'Fert':
        return {"width": "30%",'display': 'block'}  #{'display': 'block'}   
    if visibility_state == 'No_fert':
        return {"width": "30%",'display': 'none'} #'display': 'none'} 
#==============================================================
#call back to "show/hide" Enterprise Budgetting input table
@app.callback(Output('EB-table-Comp', component_property='style'),
              Input('EB_radio', component_property='value'))
def show_hide_EBtable(visibility_state):
    if visibility_state == 'EB_Yes':
        return {"width": "80%",'display': 'block'}  #{'display': 'block'}   
    if visibility_state == 'EB_No':
        return {"width": "80%",'display': 'none'} #'display': 'none'} 
#==============================================================
@app.callback(Output('scenario-table', 'data'),
                # Output('intermediate-value', 'children'),
                Input('write-button-state', 'n_clicks'),
                State('ETstation', 'value'),  #input 1
                State('year1', 'value'),      #input 2
                State('year2', 'value'),      #input 3
                State('plt-date-picker', 'date'),  #input 4
                # State('ETMZcultivar', 'value'),   #input 5
                State('crop-radio', 'value'),  #input 50
                State('cultivar-dropdown', 'value'),   #input 5
                State('ETsoil', 'value'),         #input 6
                State('ini-H2O', 'value'),        #input 7           
                State('ini-NO3', 'value'),        #input 8
                State('plt-density', 'value'),    #input 9
                State('sce-name', 'value'),       #input 10
                State('target-year', 'value'),    #input 11
                # State('intermediate-value', 'children'),  #input 12 scenario summary table
                State('fert_input', 'value'),     ##input 13 fertilizer yes or no
                State('fert-table','data'), ###input 14 fert input table
                State('EB_radio', 'value'),     ##input 15 Enterprise budgeting yes or no
                State('EB-table','data'), #Input 16 Enterprise budget input
                State('scenario-table','data') ###input 17 scenario summary table
            )
def make_sce_table(n_clicks, input1,input2,input3,input4,input50,input5,input6,input7,input8,input9,input10,
                  input11, fert_app, fert_in_table, EB_radio, EB_in_table, sce_in_table):
    # print(input1)  #MELK
    # print(input2)  #1981
    # print(input3)  #2014
    # print(input4)  #2021-06-15
    # print(input5)  #CIMT01 BH540-Kassie
    # print(input6)  #ETET001_18
    # print(input7)  #0.7
    # print(input8)  #H
    # print(input9)  #6
    # print(input10)  #scenario name
    # print(input11)  #target year as a benchmark
    # print(input12)  #scenario summary
    # print(input13)  #fertilizler or no-fertilizer
    # print(input14)  #fertilizler summary
    # print('input15:',EB_in_table)  #scenario summary

    # 2) Read fertilizer application information
    if fert_app == 'Fert':
        # print('fert-table in callback make_sce_table= {}'.format(fert_in_table))
        df_fert =pd.DataFrame(fert_in_table)
        # print('fert-table in callback make_sce_table= {}'.format(df_fert))
    else: #if no fertilizer, then an empty df with an arbitrary column
        df_fert = pd.DataFrame(columns=["DAP", "NAmount"]) 

    # 3) Read Enterprise budget input
    if EB_radio == 'EB_Yes':
        # print('EB-table in callback make_sce_table= {}'.format(EB_in_table))
        df_EB =pd.DataFrame(EB_in_table)
        # print('EB-table in callback make_sce_table= {}'.format(df_EB))
    else: #if no EB analysis
        df_EB = pd.DataFrame(columns=["sce_name","Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                 "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                 'CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts']) 
    #Make a new dataframe to return to scenario-summary table
    df = pd.DataFrame(
        [[input10, input50, input5[7:], input1, input4[5:],input2, input3, input6, input7, input8, input9, input11,
            '-99', '-99', '-99', '-99','-99', '-99','-99', '-99', '-99','-99', '-99','-99', '-99']],
        columns=["sce_name","Crop", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                 "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                 'CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts'],)
    # data = df.to_dict('rows')
    data = [{'sce_name': None,'Crop': None, 'Cultivar': None, 'stn_name': None, 'Plt-date': None, 'FirstYear': None, 'LastYear': None, 'soil': None,
             'iH2O': None, 'iNO3': None, 'plt_density': None, 'TargetYr': None,
             '1_Fert(DOY)': None,'1_Fert(Kg/ha)': None,'2_Fert(DOY)': None,'2_Fert(Kg/ha)': None, '3_Fert(DOY)': None,'3_Fert(Kg/ha)': None, '4_Fert(DOY)': None,'4_Fert(Kg/ha)': None,
             'CropPrice': None,'NFertCost': None,'SeedCost': None,'OtherVariableCosts': None, 'FixedCosts': None}] 
    # columns =  [{"name": i, "id": i,} for i in (df.columns)]
    dff = df.copy()

    if n_clicks:  
        #=====================================================================
        #1) Write SNX file
        writeSNX_main_hist(Wdir_path,input1,input2,input3,input4,input50, input5,input6,input7,input8,
                           input9,input10,fert_app, df_fert)
        #=====================================================================
        # #Make a new dataframe for fertilizer inputs
        if fert_app == 'Fert' and EB_radio == 'EB_Yes':
            #Make a new dataframe
            df = pd.DataFrame(
                [[input10, input50, input5[7:], input1, input4[5:],input2, input3, input6, input7, input8, input9,input11, 
                df_fert.DAP.values[0], df_fert.NAmount.values[0], df_fert.DAP.values[1], df_fert.NAmount.values[1],
                df_fert.DAP.values[2], df_fert.NAmount.values[2],df_fert.DAP.values[3], df_fert.NAmount.values[3],
                df_EB.CropPrice.values[0], df_EB.NFertCost.values[0], df_EB.SeedCost.values[0], df_EB.OtherVariableCosts.values[0],
                df_EB.FixedCosts.values[0]]],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        'CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts'],)
        elif fert_app == 'Fert' and EB_radio == 'EB_No':
            #Make a new dataframe
            df = pd.DataFrame(
                [[input10, input50, input5[7:], input1, input4[5:],input2, input3, input6, input7, input8,input9, input11, 
                df_fert.DAP.values[0], df_fert.NAmount.values[0], df_fert.DAP.values[1], df_fert.NAmount.values[1],
                df_fert.DAP.values[2], df_fert.NAmount.values[2],df_fert.DAP.values[3], df_fert.NAmount.values[3],
                '-99','-99', '-99','-99', '-99']],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        'CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts'],)
        elif fert_app == 'No_fert' and EB_radio == 'EB_Yes':
            #Make a new dataframe
            df = pd.DataFrame(
                [[input10, input50, input5[7:], input1, input4[5:],input2, input3, input6, input7, input8, input9,input11, 
                 '-99', '-99', '-99', '-99','-99', '-99','-99', '-99',
                df_EB.CropPrice.values[0], df_EB.NFertCost.values[0], df_EB.SeedCost.values[0], df_EB.OtherVariableCosts.values[0],
                df_EB.FixedCosts.values[0]]],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        'CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts'],)
        else:  #no fertilizer application & No EB analyze
            df = pd.DataFrame(
                [[input10, input50, input5[7:], input1, input4[5:],input2, input3, input6, input7, input8,input9, input11, 
                 '-99', '-99', '-99', '-99','-99', '-99','-99', '-99','-99','-99', '-99','-99', '-99']],
                columns=["sce_name", "Crop","Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil","iH2O","iNO3","plt_density","TargetYr",
                        "1_Fert(DOY)","1_Fert(Kg/ha)","2_Fert(DOY)","2_Fert(Kg/ha)","3_Fert(DOY)","3_Fert(Kg/ha)","4_Fert(DOY)","4_Fert(Kg/ha)",
                        'CropPrice', 'NFertCost', 'SeedCost','OtherVariableCosts','FixedCosts'],)           
        data = df.to_dict('rows')
        # columns =  [{"name": i, "id": i,} for i in (df.columns)]

    if n_clicks == 1:
        dff = df.copy()
        data = dff.to_dict('rows')
    elif n_clicks > 1:
        # # Read previously saved scenario summaries  https://dash.plotly.com/sharing-data-between-callbacks
        # dff = pd.read_json(intermediate, orient='split')
        dff = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        dff = dff.append(df, ignore_index=True)
        data = dff.to_dict('rows')
    # print(data)
    return data
    # return dash_table.DataTable(data=data, columns=columns,row_deletable=True), dff.to_json(date_format='iso', orient='split')

#===============================
#2nd callback to run ALL scenarios
@app.callback(Output(component_id='yieldbox-container', component_property='children'),
                Output(component_id='yieldcdf-container', component_property='children'),
                Output(component_id='yieldtimeseries-container', component_property='children'),
                Output(component_id='yieldtables-container', component_property='children'),
                Output('memory-yield-table', 'data'),
                Input('simulate-button-state', 'n_clicks'),
                # State('target-year', 'value'),       #input 11
                # State('intermediate-value', 'children') #scenario summary table
                State('scenario-table','data') ### scenario summary table
              )

def run_create_figure(n_clicks, sce_in_table):
    if n_clicks is None:
        raise PreventUpdate
        return 
    else: 
        # 1) Read saved scenario summaries and get a list of scenarios to run
        # dff = pd.read_json(intermediate, orient='split')
        dff = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        print(dff)
        sce_numbers = len(dff.sce_name.values)
        Wdir_path = DSSAT_FILES_DIR
        TG_yield = []

        #EJ(5/3/2021) run DSSAT for each scenarios with individual V47
        for i in range(sce_numbers):
            # 2) Write V47 file
            if dff.Crop[i] == 'WH':
                temp_dv7 = path.join(Wdir_path, "DSSBatch_template_WH.V47")
            elif dff.Crop[i] == 'MZ':
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
            if dff.Crop[i] == 'WH':
                SNX_fname = path.join(Wdir_path, "ETWH"+sname+".SNX")
            elif dff.Crop[i] == 'MZ':
                SNX_fname = path.join(Wdir_path, "ETMZ"+sname+".SNX")
            else:  # SG
                SNX_fname = path.join(Wdir_path, "ETSG"+sname+".SNX")

            new_str2 = '{0:<95}{1:4s}'.format(SNX_fname, repr(1).rjust(4)) + temp_str[99:]
            fw.write(new_str2)
            fr.close()
            fw.close()
            #=====================================================================
            #3) Run DSSAT executable
            os.chdir(Wdir_path)  #change directory  #check if needed or not
            if dff.Crop[i] == 'WH':
                # args = "./DSCSM047.EXE CSCER047 B DSSBatch.V47"
                args = "./DSCSM047.EXE B DSSBatch.V47"
                fout_name = "ETWH"+sname+".OSU"
                arg_mv = "cp Summary.OUT "+ "ETWH"+sname+".OSU" #"cp Summary.OUT $fout_name"
                # fout_name = path.join(Wdir_path, "ETWH"+sname+".OSU")
            elif dff.Crop[i] == 'MZ':
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
                # print('target year:', int(dff.TargetYr[i]) )
                # print('last sim year:', int(dff.LastYear[i]))
                # print('PDAT:', PDAT)
                # print('target:', target)
                # print('yr_index:', yr_index[0][0])
                TG_yield_temp = HWAM[yr_index[0][0]]
            else: 
                TG_yield_temp = np.nan

            # Make a new dataframe for plotting
            df1 = pd.DataFrame({'EXPERIMENT':EXPERIMENT})
            df2 = pd.DataFrame({'PDAT':PDAT})
            df3 = pd.DataFrame({'ADAT':ADAT})
            df4 = pd.DataFrame({'HWAM':HWAM})
            df5 = pd.DataFrame({'YEAR':YEAR})
            temp_df = pd.concat([df1.EXPERIMENT,df5.YEAR, df2.PDAT, df3.ADAT, df4.HWAM], axis=1)
            if i==0:
                df = temp_df.copy()
            else:
                df = df.append(temp_df, ignore_index=True)
                
            TG_yield.append(TG_yield_temp)

        x_val = np.unique(df.EXPERIMENT.values)
        # print(df)
        # print('x_val={}'.format(x_val))
        #4) Make a boxplot
        # df = px.data.tips()
        # fig = px.box(df, x="time", y="total_bill")
        # fig.show()s
        # fig.update_layout(transition_duration=500)
        # df = px.data.tips()
        # fig = px.box(df, x="Scenario Name", y="Yield [kg/ha]")
        fig = px.box(df, x="EXPERIMENT", y="HWAM", title='Yield Boxplot')
        fig.add_scatter(x=x_val,y=TG_yield, mode='markers') #, mode='lines+markers') #'lines')
        fig.update_xaxes(title= 'Scenario Name [*Note:Red dot(s) represents yield(s) based on the weather of target year]')
        fig.update_yaxes(title= 'Yield [kg/ha]')
        # # return fig

        fig2 = go.Figure()
        for i in x_val:
            x_data = df.HWAM[df['EXPERIMENT']==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            fig2.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode='lines+markers',
                        name=i))
        # Edit the layout
        fig2.update_layout(title='Yield Exceedance Curve',
                        xaxis_title='Yield [kg/ha]',
                        yaxis_title='Probability of Exceedance [-]')
        # fig3.update_yaxes(title= 'Probability of Exceedance [-]')
        # fig3.update_xaxes(title= 'Yield [kg/ha]')

        # fig3 = px.line(df, x="YEAR", y="HWAM", color='EXPERIMENT', title='Yield Time-series')
        # fig3.update_xaxes(title= 'Year')
        # fig3.update_yaxes(title= 'Yield [kg/ha]')

        #make a new dataframe to save into CSV
        yr_val = np.unique(df.YEAR.values)
        df_out = pd.DataFrame({'YEAR':yr_val})

        fig3 = go.Figure()
        for i in x_val:
            x_data = df.YEAR[df['EXPERIMENT']==i].values
            y_data = df.HWAM[df['EXPERIMENT']==i].values

            ##make a new dataframe to save into CSV
            df_temp = pd.DataFrame({i:y_data})
            df_out = pd.concat([df_out, df_temp], axis=1)

            fig3.add_trace(go.Scatter(x=x_data, y=y_data,
                        mode='lines+markers',
                        name=i))
        # Edit the layout
        fig3.update_layout(title='Yield Time-Series',
                        xaxis_title='Year',
                        yaxis_title='Yield [kg/ha]')
        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_yield.csv")
        df_out.to_csv(fname, index=False)


        return [
            dcc.Graph(id='yield-boxplot',figure=fig), 
            dcc.Graph(id='yield-exceedance',figure=fig2),
            dcc.Graph(id='yield-ts',figure=fig3),
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in df_out.columns],data=df_out.to_dict('records'),
                style_table={'overflowX': 'auto'}, 
                style_cell={   # all three widths are needed
                    'minWidth': '10px', 'width': '10px', 'maxWidth': '30px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis', }),
            df_out.to_dict('records')
            ]

    # return

#===============================
#Last callback to create figures for Enterprise budgeting
@app.callback(Output(component_id='EBbox-container', component_property='children'),
                Output(component_id='EBcdf-container', component_property='children'),
                Output(component_id='EBtimeseries-container', component_property='children'),
                Output(component_id='EBtables-container', component_property='children'),
                Output('memory-EB-table', 'data'),
                Input('EB-button-state', 'n_clicks'),
                State('scenario-table','data') ### scenario summary table
              )

def EB_figure(n_clicks, sce_in_table):
    if n_clicks is None:
        raise PreventUpdate
        return 
    else: 
        # 1) Read saved scenario summaries and get a list of scenarios to run
        dff = pd.DataFrame(sce_in_table)  #read dash_table.DataTable into pd df #J(5/3/2021)
        print('Callback EB_figure:', dff)
        print('Callback EB_figure:', sce_in_table)
        sce_numbers = len(dff.sce_name.values)
        Wdir_path = DSSAT_FILES_DIR
        os.chdir(Wdir_path)  #change directory  #check if needed or not
        TG_GMargin = []

        #EJ(5/3/2021) Read DSSAT output for each scenarios
        for i in range(sce_numbers):
            sname = dff.sce_name.values[i]
            if dff.Crop[i] == 'WH':
                fout_name = path.join(Wdir_path, "ETWH"+sname+".OSU")
            elif dff.Crop[i] == 'MZ':
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

            # Make a new dataframe for plotting
            df1 = pd.DataFrame({'EXPERIMENT':EXPERIMENT})
            df2 = pd.DataFrame({'PDAT':PDAT})
            df3 = pd.DataFrame({'ADAT':ADAT})
            df4 = pd.DataFrame({'HWAM':HWAM})
            df5 = pd.DataFrame({'YEAR':YEAR})
            df6 = pd.DataFrame({'NICM':NICM})
            df7 = pd.DataFrame({'GMargin':GMargin})
            temp_df = pd.concat([df1.EXPERIMENT,df5.YEAR, df2.PDAT, df3.ADAT, df4.HWAM, df6.NICM, df7.GMargin], ignore_index=True, axis=1)
            if i==0:
                df = temp_df.copy()
            else:
                df = df.append(temp_df, ignore_index=True)

            TG_GMargin.append(TG_GMargin_temp)

        # adding column name to the respective columns
        df.columns =['EXPERIMENT', 'YEAR','PDAT', 'ADAT','HWAM','NICM','GMargin']
        x_val = np.unique(df.EXPERIMENT.values)
        print(df)
        fig = px.box(df, x="EXPERIMENT", y="GMargin", title='Gross Margin Boxplot')
        fig.add_scatter(x=x_val,y=TG_GMargin, mode='markers') #, mode='lines+markers') #'lines')
        fig.update_xaxes(title= 'Scenario Name')
        fig.update_yaxes(title= 'Gross Margin[Birr/ha]')

        fig2 = go.Figure()
        for i in x_val:
            x_data = df.GMargin[df['EXPERIMENT']==i].values
            x_data = np.sort(x_data)
            fx_scf = [1.0/len(x_data)] * len(x_data) #pdf
            Fx_scf= 1.0-np.cumsum(fx_scf)  #for exceedance curve

            fig2.add_trace(go.Scatter(x=x_data, y=Fx_scf,
                        mode='lines+markers',
                        name=i))
        # Edit the layout
        fig2.update_layout(title='Gross Margin Exceedance Curve',
                        xaxis_title='Gross Margin[Birr/ha]',
                        yaxis_title='Probability of Exceedance [-]')

        #make a new dataframe to save into CSV
        yr_val = np.unique(df.YEAR.values)
        df_out = pd.DataFrame({'YEAR':yr_val})

        fig3 = go.Figure()
        for i in x_val:
            x_data = df.YEAR[df['EXPERIMENT']==i].values
            y_data = df.GMargin[df['EXPERIMENT']==i].values

            ##make a new dataframe to save into CSV
            df_temp = pd.DataFrame({i:y_data})
            df_out = pd.concat([df_out, df_temp], axis=1)

            fig3.add_trace(go.Scatter(x=x_data, y=y_data,
                        mode='lines+markers',
                        name=i))
        # Edit the layout
        fig3.update_layout(title='Gross Margin Time-Series',
                        xaxis_title='Year',
                        yaxis_title='Gross Margin[Birr/ha]')
        #save simulated yield outputs into a csv file <<<<<<=======================
        fname = path.join(Wdir_path, "simulated_yield_GMargin.csv")
        df_out.to_csv(fname, index=False)
        return [
            dcc.Graph(id='EB-boxplot',figure=fig), 
            dcc.Graph(id='EB-exceedance',figure=fig2),
            dcc.Graph(id='EB-ts',figure=fig3),
            dash_table.DataTable(columns=[{"name": i, "id": i} for i in df_out.columns],
                data=df_out.to_dict('records'),
                style_cell={'whiteSpace': 'normal','height': 'auto',},),
            df_out.to_dict('records')
            ]

# =============================================
# def writeSNX_main_hist(Wdir_path,input1,input2,input3,input4,input5,input6,input7,input8,input9,input10):
def writeSNX_main_hist(Wdir_path,input1,input2,input3,input4,crop,input5,input6,input7,input8,
                       input9,input10,fert_app, df_fert):    
    # print('check writeSNX_main')
    # print(input1)  #MELK
    # print(input2)  #1981
    # print(input3)  #2014
    # print(input4)  #2021-06-15
    # print(input50)  #MZ crop type
    # print(input5)  #CIMT01 BH540-Kassie
    # print(input6)  #ETET001_18
    # print(input7)  #0.7
    # print(input8)  #H
    # print(input9)  #6
    # print(input10)  #scenario name
    WSTA = input1
    NYERS = repr(int(input3) - int(input2) + 1)
    plt_year = input2
    if input4 is not None:
        date_object = date.fromisoformat(input4)
        date_string = date_object.strftime('%B %d, %Y')
        plt_doy = date_object.timetuple().tm_yday
        # print(date_string)  #June 15, 2021 
        # print(plt_doy)  #166
    PDATE = plt_year[2:] + repr(plt_doy).zfill(3)
        #   IC_date = first_year * 1000 + (plt_doy - 1)
        #   PDATE = repr(first_year)[2:] + repr(plt_doy).zfill(3)
        # ICDAT = repr(IC_date)[2:]
    ICDAT = plt_year[2:] + repr(plt_doy-1).zfill(3)  #Initial condition => 1 day before planting
    SDATE = ICDAT
    INGENO = input5[0:6]  
    CNAME = input5[7:]  
    ID_SOIL = input6
    PPOP = input9  #planting density
    i_NO3 = input8  # self.label_04.cget("text")[0:1]  #self.NO3_soil.getvalue()[0][0:1] #'H' #or 'L'
    IC_w_ratio = float(input7)
    # crop = 'MZ' #EJ(1/6/2021) temporary

    #1) make SNX
    if crop == 'WH':
        temp_snx = path.join(Wdir_path, "TEMP_ETWH.SNX")
        snx_name = 'ETWH'+input10[:4]+'.SNX'
    elif crop == 'MZ':
        temp_snx = path.join(Wdir_path, "TEMP_ETMZ.SNX")
        snx_name = 'ETMZ'+input10[:4]+'.SNX'
    else:  # SG
        temp_snx = path.join(Wdir_path, "TEMP_ETSG.SNX")
        snx_name = 'ETSG'+input10[:4]+'.SNX'
    # # temp_snx = path.join(Wdir_path, "ETMZTEMP.SNX")
    # temp_snx = path.join(Wdir_path, "TEMP_ETMZ.SNX")
    # snx_name = 'ETMZ'+input10[:4]+'.SNX'
    SNX_fname = path.join(Wdir_path, snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    # read lines 1-9 from temp file
    for line in range(0, 14):
        temp_str = fr.readline()
        fw.write(temp_str)

    MI = '0' 
    if fert_app == 'Fert':
        MF = '1'
    else: 
        MF = '0'
    # MF = '1'
    SA = '0'
    IC = '1'
    MP = '1'
    MR = '0'
    MC = '0'
    MT = '0'
    ME = '0'
    MH = '0'
    SM = '1'
    temp_str = fr.readline()
    FL = '1'
    fw.write('{0:3s}{1:31s}{2:3s}{3:3s}{4:3s}{5:3s}{6:3s}{7:3s}{8:3s}{9:3s}{10:3s}{11:3s}{12:3s}{13:3s}'.format(
        FL.rjust(3), '1 0 0 ET-SIMAGRI                 1',
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
    ID_FIELD = WSTA + '0001'
    WSTA_ID =  WSTA
    fw.write(
        '{0:2s} {1:8s}{2:5s}{3:3s}{4:6s}{5:4s}  {6:10s}{7:4s}'.format(FL.rjust(2), ID_FIELD, WSTA_ID.rjust(5),
                                                                        '       -99   -99   -99   -99   -99   -99 ',
                                                                        SLTX.ljust(6), SLDP.rjust(4), ID_SOIL,
                                                                        ' -99'))
    fw.write(" \n")
    temp_str = fr.readline()  # 1 -99      CCER       -99   -99 DR000   -99   -99
    temp_str = fr.readline()  # @L ...........XCRD ...........YCRD .....ELEV
    fw.write(temp_str)
    temp_str = fr.readline()  # 1             -99             -99       -99   ==> skip
    # ================write *FIELDS - second section
    fw.write('{0:2s} {1:89s}'.format(FL.rjust(2),
                                    '            -99             -99       -99               -99   -99   -99   -99   -99   -99'))
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
            if i_NO3 == 'H':
                SNO3 = '15'  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # i_NO3 == 'L':
                SNO3 = '5'  # **EJ(5/27/2015)
        elif nline == 1:  # second layer
            temp_SH2O = IC_w_ratio * (fc[nline] - wp[nline]) + wp[nline]  # EJ(6/25/2015): initial AWC=70% of maximum AWC
            if i_NO3 == 'H':
                SNO3 = '2'  # **EJ(4/29/2020) used one constant number regardless of soil types
            else:  # elif i_NO3 == 'L':
                SNO3 = '.5'  # **EJ(4/29/2020) used one constant number regardless of soil types
        else:
            temp_SH2O = fc[nline]  # float
            SNO3 = '0'  # **EJ(5/27/2015)
        SH2O = repr(temp_SH2O)[0:5]  # convert float to string
        new_str = temp_str[0:5] + repr(soil_depth[nline]).rjust(3) + ' ' + SH2O.rjust(5) + temp_str[14:22] + SNO3.rjust(4) + "\n"
        fw.write(new_str)
    fw.write("  \n")
    # print('ICDAT= {0}'.format(ICDAT))  #test here
    # print('fc[0]= {0}'.format(fc[0] ))  #test here
    # print('test after writing init')  #test here
    for nline in range(0, 10):
        temp_str = fr.readline()
        # print temp_str
        if temp_str[0:9] == '*PLANTING':
            break

    fw.write(temp_str)  # *PLANTING DETAILS
    temp_str = fr.readline()  # @P PDATE EDATE
    fw.write(temp_str)
    # write *PLANTING DETAILS
    temp_str = fr.readline()
    PPOE = PPOP #planting density 
    new_str = temp_str[0:3] + PDATE + '   -99' + PPOP.rjust(6) + PPOE.rjust(6) + temp_str[26:]
    fw.write(new_str)
    fw.write("  \n")
    # print('PPOE = {0}'.format(PPOE))  #test here
    # write *IRRIGATION AND WATER MANAGEMENT, if irrigation on reported dates
    # skip irrigation for now   #EJ(1/6/2021) temporary

    # write *FERTILIZERS (INORGANIC)
    #get fertilizer info using dash_table.DataTable(https://dash.plotly.com/datatable/callbacks
    #use editable datatable https://dash.plotly.com/datatable/editable
    for nline in range(0, 20):
        temp_str = fr.readline()
        # print temp_str
        if temp_str[0:12] == '*FERTILIZERS':
            break
    fw.write(temp_str)  # *FERTILIZERS (INORGANIC)
    temp_str = fr.readline()  # @F FDATE  FMCD  FACD 
    fw.write(temp_str)
    temp_str = fr.readline()  #1     0 FE005 AP001     5    30   -99   -99   -99   -99   -99   -99
#-0------------        # write *FERTILIZERS (INORGANIC)
    if fert_app == 'Fert':
        print(df_fert)
        df_fert = df_fert.astype(float)
        df_filtered = df_fert[(df_fert["DAP"] >= 0) & (df_fert["NAmount"] >= 0)]
        fert_count = len(df_filtered)  #Get the number of rows: len(df)  => May need more error-checking
        FDATE = df_filtered.DAP.values
        FMCD = 'FE005'  #Urea
        FACD = 'AP001'  #Broadcast, not incorporated    
        FDEP = '5'   #5cm depth
        FAMN = df_filtered.NAmount.values
        FAMP = '-99'
        FAMK = '-99'

        if fert_count > 0:   # fertilizer applied
            for i in range(fert_count):
                new_str = temp_str[0:5] + repr(int(FDATE[i])).rjust(3) + ' ' + FMCD.rjust(5) + ' ' + FACD.rjust(5) + ' ' + FDEP.rjust(5) + ' ' + repr(FAMN[i]).rjust(5) + ' ' + FAMP.rjust(5) + ' ' + FAMK.rjust(5) + temp_str[44:]
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
        if temp_str[0:11] == '*SIMULATION':
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
    fw.write(' 1 OP              Y     Y     Y     N     N     N     N     N     D'+ "\n")
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
    # if self._Setting.DSSATSetup2.rbIrrigation.get() == 0:  # automatic when required
    #     IMDEP = self._Setting.DSSATSetup2.IA_mng_depth.getvalue()
    #     ITHRL = self._Setting.DSSATSetup2.IA_threshold.getvalue()
    #     IREFF = self._Setting.DSSATSetup2.IA_eff_fraction.getvalue()
    #     fw.write(' 1 IR          ' + IMDEP.rjust(5) + ITHRL.rjust(6) + '   100 GS000 IR001    10'+ IREFF.rjust(6)+ "\n")
    # else:
    #     # new_str = temp_str[0:39] + IMETH + temp_str[44:]
    #     fw.write(temp_str)

    # read lines from temp file
    for line in range(0, 7):
        temp_str = fr.readline()
        fw.write(temp_str)

    fr.close()
    fw.close()
    return
# =============================================
# def writeV47_main_hist(Wdir_path,sname,crop):  # sname includes full path
#     sname = sname.replace("/", "\\")
#     if crop == 'WH':
#         temp_dv7 = path.join(Wdir_path, "DSSBatch_template_WH.V47")
#     elif crop == 'MZ':
#         temp_dv7 = path.join(Wdir_path, "DSSBatch_template_MZ.V47")
#     else:  ##'SG':
#         temp_dv7 = path.join(Wdir_path, "DSSBatch_template_SG.V47")

#     dv7_fname = path.join(Wdir_path, "DSSBatch.V47")
#     fr = open(temp_dv7, "r")  # opens temp DV4 file to read
#     fw = open(dv7_fname, "w")
#     # read template and write lines
#     for line in range(0, 10):
#         temp_str = fr.readline()
#         fw.write(temp_str)

#     temp_str = fr.readline()
#     new_str2 = '{0:<95}{1:4s}'.format(sname, repr(1).rjust(4)) + temp_str[99:]
#     fw.write(new_str2)

#     fr.close()
#     fw.close()

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

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run_server(debug=False,
                   host="0.0.0.0",
                   port=port)
