import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from os import path # path
import os
import subprocess  #to run executable
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Climate-Agriculture Modeling Decision Tool for Ethiopia (Historical Analysis)',
            style={'textAlign': 'center','color': 'black'}),

    html.Div(children='''
        The CAMDT is a tool designed to guide decision-makers in adopting appropriate crop and management practices 
        that can improve crop yields given a seasonal climatic condition.
    ''', style={'textAlign': 'left','color': 'black'}),
    html.Br(),
    html.Div(children='''
        Smart planning of annual crop production requires consideration of possible scenarios.
        The CAMDT tool adopts crop simulation models included in the DSSAT package (Decision Support System for Agrotechnology Transfer). 
        The methodology was developed by the IRI (International Research Institute for Climate and Society / Columbia University) 
        in collaboration with the Ethiopian Institute of Agricultural Research (EIAR). 
        The purpose of this tool is to support decision-making of the producer or technical advisor, which facilitates discussion of optimal production strategies, risks of technology adoption, 
        and evaluation of long-term effects, considering interactions of various factors.
    ''', style={'textAlign': 'left','color': 'black'}),
    html.Br(),
    html.Div(children='''
        To start your "what-if" scenario analysis, please select appropirate inputs and click the "run" butten at the end.
    ''', style={'textAlign': 'left','color': 'black'}),
            
    html.Br(),
    html.H2(children='Climate'),
    html.Div([
        html.Div(["Weather station: ",
                dcc.Dropdown(id='mystation', options=[{'label': 'Bambey', 'value': 'CNRA'},{'label': 'Nioro', 'value': 'NRIP'},{'label': 'Sinthio', 'value': 'SNTH'}],
                value='SNTH')]),
    html.H2(children='Period considered for the simulation:'),
        html.Div(["First year to simulate: ",
                dcc.Input(id='year1', placeholder='Enter a value ...', value=' ', type='text')]),
        html.Div(["Last year to simulate: ",
                dcc.Input(id='year2', placeholder='Enter a value ...', value=' ', type='text')]),
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
    temp_snx = path.join("C:\\IRI\\Dash_test\\Senegal\\", "SESGTEMP.SNX")
    snx_name = 'SESG'+input1+'.SNX'
    SNX_fname = path.join("C:\\IRI\\Dash_test\\Senegal\\", snx_name)
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
    Wdir_path = 'C:\\IRI\\Dash_test\\Senegal\\'
    os.chdir(Wdir_path)  #change directory  #check if needed o rnot
    args = "DSCSM047.EXE SGCER047 B DSSBatch.v47"
    subprocess.call(args) ##Run executable with argument  , stdout=FNULL, stderr=FNULL, shell=False)

    #3) read DSSAT output
    #4) Make a boxplot
    # df = px.data.tips()
    # fig = px.box(df, x="time", y="total_bill")
    # fig.show()s
    # fig.update_layout(transition_duration=500)

    # return fig
    return u'Selected statoin is  "{}" '.format(input1)

if __name__ == '__main__':
    app.run_server(debug=True)