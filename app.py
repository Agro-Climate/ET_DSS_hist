import dash
import pandas as pd
import pathlib
import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from helpers import make_dash_table, create_plot

from os import path # path
import os
import subprocess  #to run executable
from datetime import date

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

app.layout = html.Div(
    [
        html.Div(
            [html.Img(src=app.get_asset_url("ethioagroclimate.png"))], className="app__banner"
            # html.Img(src=app.get_asset_url("SIMAGRI_CO_logo.gif"))], className="app__banner"
        ),
        html.Div(
            [
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
                        ''', style={'textAlign': 'left'}),
                        # html.Span("CAMDT  ", className="uppercase bold", style={'textAlign': 'left'}),
                        # html.Span(
                        #     "is a tool designed to guide decision-makers in adopting appropriate crop and management practices that can improve crop yields given a seasonal climatic condition."
                        #     , style={'textAlign': 'left'}
                        # ),
                        html.Br(),
                        html.Div(children='''
                            Smart planning of annual crop production requires consideration of possible scenarios.
                            The CAMDT tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
                            The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
                            in collaboration with the Ethiopian Institute of Agricultural Research (EIAR). 
                            The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
                            and evaluation of long-term effects, considering interactions of various factors.
                        ''', style={'textAlign': 'Center'}),
                    ]),
            ]),
        html.Div([
            html.Br(),
            html.Span("1) Select a station name for analysis", className="uppercase bold", style={'textAlign': 'left'}),
            # html.Span("a station name for analysis.", style={'textAlign': 'left'}),
            html.Div(["Weather station: ",
                    dcc.Dropdown(id='mystation', options=[{'label': 'Melkasa', 'value': 'MELK'},{'label': 'Awassa', 'value': 'AWAS'},{'label': 'Bako', 'value': 'BAKO'},{'label': 'Mahoni', 'value': 'MAHO'}],
                    value='MELK')]),
            # html.H2(children='Period considered for the simulation:'),
            html.Br(),
            html.Span("2) Period considered for the simulation (first and last year [YYYY])", className="uppercase bold", style={'textAlign': 'left'}),
            # html.Div(["First year to simulate: ",
            #         dcc.Input(id='year1', placeholder='Enter a value ...', value='1981', type='text')]),
            # html.Div(["Last year to simulate: ",
            #         dcc.Input(id='year2', placeholder='Enter a value ...', value='2018', type='text')]),
            html.Br(),
            dcc.Input(id="year1", type="text", placeholder="Enter the first year to simulate ..."),
            dcc.Input(id="year2", type="text", placeholder="Enter the last year to simulate ..."),
            html.Br(),
            html.Span("3) Select Planting Date", className="uppercase bold", style={'textAlign': 'left'}),
            dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=date(2021, 1, 1),
                    max_date_allowed=date(2021, 12, 31),
                    initial_visible_month=date(2021, 6, 5),
                    date=date(2021, 6, 15)
                    ),
            html.Br(),    
            ],style={'columnCount': 2}),
        html.Div([
            html.Span("4) Select Cultivar to simulate", className="uppercase bold", style={'textAlign': 'left'}),
            html.Div(["Maize Cultivar: ",
                    dcc.Dropdown(id='ETMZcultivar', options=[{'label': 'CIMT01 BH540-Kassie', 'value': 'CIMT01 BH540-Kassie'},
                                                            {'label': 'CIMT02 MELKASA-Kassi', 'value': 'CIMT02 MELKASA-Kassi'},
                                                            {'label': 'CIMT17 BH660-FAW-40%', 'value': 'CIMT17 BH660-FAW-40%'},
                                                            {'label': 'CIMT19 MELKASA2-FAW-40%', 'value': 'CIMT19 MELKASA2-FAW-40%'},
                                                            {'label': 'CIMT21 MELKASA-LowY', 'value': 'CIMT21 MELKASA-LowY'},
                                                            ], 
                                value='CIMT01 BH540-Kassie')]),
            html.Br(),
            html.Span("5) Select Soil type to simulate", className="uppercase bold", style={'textAlign': 'left'}),
            html.Div(["Soil: ",
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
                                value='ETET001_18')]),
            html.Br(),
            html.Span("6) Select initial soil water condition", className="uppercase bold", style={'textAlign': 'left'}),
            html.Br(),
            html.Span("7) Select initial NO3 condition", className="uppercase bold", style={'textAlign': 'left'}),
            html.Br(),
            html.Span("8) Select Planting Density", className="uppercase bold", style={'textAlign': 'left'}),
            html.Br(),
            html.Button(id='submit-button-state', n_clicks=0, children='Run DSSAT'),
            html.Div(id='output-state'),
            dcc.Graph(id='yield_boxplot'),
        ],style={'columnCount': 2}),
        # html.Div(id="number-output"),
    ])

# @app.callback(Output('yield_boxplot', 'figure'),
@app.callback(Output('output-state', 'children'),
              [Input('submit-button-state', 'n_clicks')],
              [State('mystation', 'value')])
def update_figure(n_clicks, input1):
    print(input1)
    #1) make SNX
    temp_snx = path.join("C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\", "ETMZTEMP.SNX")
    snx_name = 'ETMZ'+input1+'.SNX'
    SNX_fname = path.join("C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\\", snx_name)
    fr = open(temp_snx, "r")  # opens temp SNX file to read
    fw = open(SNX_fname, "w")  # opens SNX file to write
    for i in range(20):
        temp_str = fr.readline()
        fw.write(temp_str)
    temp_str = fr.readline()
    new_str = temp_str[0:12] + input1 + temp_str[16:]  #replace weather station name
    fw.write(new_str)
    for i in range(41):
        temp_str = fr.readline()
        fw.write(temp_str)
    fw.close()
    #2) Run DSSAT executable
    Wdir_path = 'C:\\IRI\\Python_Dash\\ET_DSS_hist\\TEST\\'
    os.chdir(Wdir_path)  #change directory  #check if needed o rnot
    args = "DSCSM047.EXE MZCER047 B DSSBatch.v47"
    subprocess.call(args) ##Run executable with argument  , stdout=FNULL, stderr=FNULL, shell=False)

    #3) read DSSAT output
    #4) Make a boxplot
    # df = px.data.tips()
    # fig = px.box(df, x="time", y="total_bill")
    # fig.show()s
    # fig.update_layout(transition_duration=500)

    # return fig
    return u'Selected statoin is  "{}" '.format(input1)

if __name__ == "__main__":
    app.run_server(debug=True)
