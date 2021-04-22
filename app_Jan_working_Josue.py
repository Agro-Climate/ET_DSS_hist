import dash
import pandas as pd
import numpy as np
import pathlib
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import plotly.express as px

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from helpers import make_dash_table, create_plot

from os import path # path
import os
import subprocess  #to run executable
from datetime import date
import datetime    #to convert date to doy or vice versa

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

DSSAT_FILES_DIR_SHORT = "/dssat_files_dir/"

DSSAT_FILES_DIR = os.getcwd() + DSSAT_FILES_DIR_SHORT

app.layout = html.Div(
    [
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
                # html.Div(children='''
                #     CAMDT is a tool designed to guide decision-makers in adopting appropriate crop and management practices that can improve crop yields given a seasonal climatic condition.
                # ''', style={'textAlign': 'Center'}),
                # # html.Span("CAMDT  ", className="uppercase bold", style={'textAlign': 'Center'}),
                # # html.Span(
                # #     "is a tool designed to guide decision-makers in adopting appropriate crop and management practices that can improve crop yields given a seasonal climatic condition."
                # #     , style={'textAlign': 'Center'}
                # # ),
                # html.Br(),
                # html.Div(children='''
                #     Smart planning of annual crop production requires consideration of possible scenarios.
                #     The CAMDT tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
                #     The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
                #     in collaboration with the Ethiopian Institute of Agricultural Research (EIAR). 
                #     The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
                #     and evaluation of long-term effects, considering interactions of various factors.
                # ''', style={'textAlign': 'Center'}),

            ]),
        html.Div([
            dbc.Row([
                dbc.Col(html.Span("1) Select a station name for analysis", className="uppercase bold"),width="auto"),
                ]),
            dcc.Dropdown(id='ETstation', options=[{'label': 'Melkasa', 'value': 'MELK'},{'label': 'Awassa', 'value': 'AWAS'},{'label': 'Bako', 'value': 'BAKO'},{'label': 'Mahoni', 'value': 'MAHO'}],
                    value='MELK'),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                dbc.Col(html.Span("2) Type years to simulate", className="uppercase bold")),
                ]),
            dbc.Row([
                dbc.Col(html.Span("*Note: Available years are from 1981 to 2018")),
                ]),
            html.Span("From [YYYY] "),
            dcc.Input(id="year1", type="text", placeholder="Enter first year to simulate"),
            html.Span("  to [YYYY] "),
            dcc.Input(id="year2", type="text", placeholder="Enter last year to simulate"),    
            html.Br(),                 
            ]),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("3) Select Planting Date", className="uppercase bold", style={'textAlign': 'Center'}),
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
                html.Span("4) Select Cultivar to simulate", className="uppercase bold"), #, style={'textAlign': 'Center'}),
                ]),
            dbc.Row([
                dcc.Dropdown(id='ETMZcultivar', options=[{'label': 'CIMT01 BH540-Kassie', 'value': 'CIMT01 BH540-Kassie'},
                                                        {'label': 'CIMT02 MELKASA-Kassi', 'value': 'CIMT02 MELKASA-Kassi'},
                                                        {'label': 'CIMT17 BH660-FAW-40%', 'value': 'CIMT17 BH660-FAW-40%'},
                                                        {'label': 'CIMT19 MELKASA2-FAW-40%', 'value': 'CIMT19 MELKASA2-FAW-40%'},
                                                        {'label': 'CIMT21 MELKASA-LowY', 'value': 'CIMT21 MELKASA-LowY'},
                                                        ], 
                            value='CIMT01 BH540-Kassie'),
                ],align="start",
                ),
            # ],style={'columnCount': 2}),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("5) Select Soil type to simulate", className="uppercase bold"),
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
                html.Span("6) Select initial soil water condition", className="uppercase bold"),
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
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("7) Select initial NO3 condition", className="uppercase bold"),
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
                html.Span("8) Enter Planting Density", className="uppercase bold"),
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
                html.Span("9) Enter Scenario name ", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                dcc.Input(id="sce-name", type="text", placeholder="Enter scenario name.."),
                html.Span("(only 4 characters)"),
                ],align="start",
                ),
            ],style={"width": "60%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("10) Target year to compare with ", className="uppercase bold"),
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
            html.Button(id='write-button-state', n_clicks=0, children='Create or Add a new Scenario', 
                style={'background-color': '#4CAF50'}),  #https://www.w3schools.com/css/css3_buttons.asp
        ],),
        # html.Div(id='output-state'),
        html.Br(),
        html.Div(id="table-summary",style={"width": "50%"}),
        html.Br(),

        # Hidden div inside the app that stores the intermediate value
        html.Div(id='intermediate-value', style={'display': 'none'}),

        # html.Div(id="number-output"),
        html.Br(),
        # html.Div([
        #     html.Button(id='simulate-button-state', n_clicks=0, children='Simulate all scenarios (Run DSSAT)',style={'background-color': '#008CBA'}), #blue
        # ],),
        html.Div([
            html.Button(id='simulate-button-state', children='Simulate all scenarios (Run DSSAT)',style={'background-color': '#008CBA'}), #blue
        ],),
        html.Br(),
        # dbc.Progress("25%", value=25),
        # dbc.Progress(id="progress"),
        dbc.Spinner(children=[dcc.Graph(id = 'yield_boxplot')],size='lg',color='primary',type='border'),
        # dcc.Graph(id='yield_boxplot'),
    ])

@app.callback(Output('table-summary', 'children'),
                Output('intermediate-value', 'children'),
                Input('write-button-state', 'n_clicks'),
                State('ETstation', 'value'),  #input 1
                State('year1', 'value'),      #input 2
                State('year2', 'value'),      #input 3
                State('plt-date-picker', 'date'),  #input 4
                State('ETMZcultivar', 'value'),   #input 5
                State('ETsoil', 'value'),         #input 6
                State('ini-H2O', 'value'),        #input 7           
                State('ini-NO3', 'value'),        #input 8
                State('plt-density', 'value'),    #input 9
                State('sce-name', 'value'),       #input 10
                State('intermediate-value', 'children')  #scenario summary table
            )
def make_sce_table(n_clicks, input1,input2,input3,input4,input5,input6,input7,input8,input9,input10,intermediate):
    print(input1)  #MELK
    print(input2)  #1981
    print(input3)  #2014
    print(input4)  #2021-06-15
    print(input5)  #CIMT01 BH540-Kassie
    print(input6)  #ETET001_18
    print(input7)  #0.7
    print(input8)  #H
    print(input9)  #6
    print(input10)  #scenario name

    #Make a new dataframe
    df = pd.DataFrame(
        [[n_clicks, input10, input5[7:], input1, input4[5:],input2, input3, input6]],
        columns=["count", "sce_name", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil"],)
    # data = df.to_dict('rows')
    data = [{'count': None, 'sce_name': None, 'Cultivar': None, 'stn_name': None, 'Plt-date': None, 'FirstYear': None, 'LastYear': None, 'soil': None}] 
    columns =  [{"name": i, "id": i,} for i in (df.columns)]
    dff = df.copy()

    if n_clicks:  
        #=====================================================================
        Wdir_path = DSSAT_FILES_DIR
        # Wdir_path = 'TEST\\'
        #1) Write SNX file
        writeSNX_main_hist(Wdir_path,input1,input2,input3,input4,input5,input6,input7,input8,input9,input10)
        #=====================================================================
        #Make a new dataframe
        df = pd.DataFrame(
            [[n_clicks, input10, input5[7:], input1, input4[5:],input2, input3, input6]],
            columns=["count", "sce_name", "Cultivar","stn_name", "Plt-date", "FirstYear", "LastYear", "soil"],)
        data = df.to_dict('rows')
        columns =  [{"name": i, "id": i,} for i in (df.columns)]

    if n_clicks == 1:
        dff = df.copy()
        data = dff.to_dict('rows')
    elif n_clicks > 1:
        # Read previously saved scenario summaries  https://dash.plotly.com/sharing-data-between-callbacks
        dff = pd.read_json(intermediate, orient='split')
        dff = dff.append(df, ignore_index=True)
        data = dff.to_dict('rows')

    return dash_table.DataTable(data=data, columns=columns), dff.to_json(date_format='iso', orient='split')

#===============================
#2nd callback to run ALL scenarios
@app.callback(Output('yield_boxplot', 'figure'),
                Input('simulate-button-state', 'n_clicks'),
                State('target-year', 'value'),       #input 11
                State('intermediate-value', 'children')  #scenario summary table
              )
def run_create_figure(n_clicks, tyear, intermediate):
    if n_clicks is None:
        raise PreventUpdate
    else: 
        # Testing
        # Wdir_path = DSSAT_FILES_DIR
        # os.chdir(Wdir_path)
        # args = "./DSCSM047.EXE MZCER047 B DSSBatch.V46"
        # os.system(args) 

        # 1) Read saved scenario summaries and get a list of scenarios to run
        dff = pd.read_json(intermediate, orient='split')
        sce_numbers = len(dff.sce_name.values)

        # 2) Write V47 file
        Wdir_path = DSSAT_FILES_DIR
        temp_dv7 = path.join(Wdir_path, "DSSBatch_template_MZ.V47")
        dv7_fname = path.join(Wdir_path, "DSSBatch.V47")
        fr = open(temp_dv7, "r")  # opens temp DV4 file to read
        fw = open(dv7_fname, "w")
        # read template and write lines
        for line in range(0, 10):
            temp_str = fr.readline()
            fw.write(temp_str)

        temp_str = fr.readline()
        for i in range(sce_numbers):
            sname = dff.sce_name.values[i]
            SNX_fname = path.join(Wdir_path, "ETMZ"+sname+".SNX")
            # SNX_fname = SNX_fname.replace("/", "\\")
            new_str2 = '{0:<95}{1:4s}'.format(SNX_fname, repr(1).rjust(4)) + temp_str[99:]
            fw.write(new_str2)

        fr.close()
        fw.close()
        #=====================================================================
        #3) Run DSSAT executable
        os.chdir(Wdir_path)  #change directory  #check if needed o rnot
        ## Windows:
        # args = "DSCSM047.EXE MZCER047 B DSSBatch.v47"
        # subprocess.call(args) ##Run executable with argument  , stdout=FNULL, stderr=FNULL, shell=False)

        ## Linux:
        args = "./DSCSM047.EXE MZCER047 B DSSBatch.V47"
        os.system(args) 

        #4) read DSSAT output => Read Summary.out from all scenario output
        # fout_name = path.join(Wdir_path, "SUMMARY.OUT")
        fout_name = path.join(Wdir_path, "Summary.OUT")
        df_OUT=pd.read_csv(fout_name, delim_whitespace=True ,skiprows=3)
        HWAM = df_OUT.iloc[:,21].values  #read 21th column only
        EXPERIMENT = df_OUT.iloc[:,7].values  #read 4th column only
        PDAT = df_OUT.iloc[:,14].values  #read 14th column only
        ADAT = df_OUT.iloc[:,16].values  #read 14th column only
        MDAT = df_OUT.iloc[:,17].values  #read 14th column only    
        TG_yield = []
        for i in range(sce_numbers):
            # year1 = dff.FirstYear[i]
            # year2 = dff.LastYear[i]
            # nyear = int(year2) - int(year1) +1
            # exp_id = dff.sce_name.values[i]
            # exp_index = np.argwhere(EXPERIMENT == exp_id)
            # yield_hist[:nyear,i] = HWAM[exp_index[0][0]]

            #Extract yield from a distinctive year to compare  => EJ(11/30/2020)
            # PDAT = df_OUT.iloc[:,14].values  #read 14th column only
            doy = repr(PDAT[0])[4:]
            # target = repr(tyear) + doy
            target = tyear + doy
            yr_index = np.argwhere(PDAT == int(target))
            TG_yield.append(HWAM[yr_index[0][0]])

        # Make a new dataframe for plotting
        # Make a new dataframe for plotting
        df1 = pd.DataFrame({'EXPERIMENT':EXPERIMENT})
        df2 = pd.DataFrame({'PDAT':PDAT})
        df3 = pd.DataFrame({'ADAT':ADAT})
        df4 = pd.DataFrame({'HWAM':HWAM})
        df = pd.concat([df1.EXPERIMENT, df2.PDAT, df3.ADAT, df4.HWAM], axis=1)
        x_val = np.unique(df.EXPERIMENT.values)

        #4) Make a boxplot
        # df = px.data.tips()
        # fig = px.box(df, x="time", y="total_bill")
        # fig.show()s
        # fig.update_layout(transition_duration=500)
        # df = px.data.tips()
        # fig = px.box(df, x="Scenario Name", y="Yield [kg/ha]")
        fig = px.box(df, x="EXPERIMENT", y="HWAM")
        fig.add_scatter(x=x_val,y=TG_yield, mode='lines')
        fig.update_xaxes(title= 'Scenario Name')
        fig.update_yaxes(title= 'Yield [kg/ha]')
        return fig
    return

# =============================================
def writeSNX_main_hist(Wdir_path,input1,input2,input3,input4,input5,input6,input7,input8,input9,input10):
    # print('check writeSNX_main')
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
    crop = 'MZ' #EJ(1/6/2021) temporary

    #1) make SNX
    temp_snx = path.join(Wdir_path, "ETMZTEMP.SNX")
    snx_name = 'ETMZ'+input10[:4]+'.SNX'
    SNX_fname = path.join(Wdir_path, snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    # read lines 1-9 from temp file
    for line in range(0, 14):
        temp_str = fr.readline()
        fw.write(temp_str)

    MI = '0' 
    MF = '1'
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
        FL.rjust(3), '1 0 0 ERiMA DCC1                 1',
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
    temp_str = fr.readline()  #  1     0 FE005 AP002 
    fw.write(temp_str)
    temp_str = fr.readline()  #  1    45 FE005 AP002
    fw.write(temp_str)

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


# if __name__ == "__main__":
#     app.run_server(debug=True)

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(debug=False,
                   host="0.0.0.0",
                   port=port)