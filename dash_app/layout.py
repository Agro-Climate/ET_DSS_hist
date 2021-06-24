import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

def layout():
    return html.Div(
    [
        dcc.Store(id='memory-yield-table'),  #to save fertilizer application table
        dcc.Store(id='memory-sorted-yield-table'),  #to save fertilizer application table
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
                html.Span("4) Select a Planting Date", className="uppercase bold", style={'textAlign': 'Center'}),
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
                html.Span("5) Select a Cultivar to simulate", className="uppercase bold"), #, style={'textAlign': 'Center'}),
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
                            value='CIMT02 MELKASA-Kassi'),
                ],align="start",
                ),
            # ],style={'columnCount': 2}),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("6) Select a Soil type to simulate", className="uppercase bold"),
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
                            value='0.5'),
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
                            value='L'),
                ],align="start",
                ),
            ],style={"width": "40%"},),
        html.Br(),
        html.Div([
            dbc.Row([
                html.Span("9) Enter a Planting Density", className="uppercase bold"),
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
                html.Span("*Note: Target year can a specific year you remember (e.g., drought year) and want to compare with a full climatology distribution"),
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
            dbc.Row([
                html.Span("14) Approximate growing season", className="uppercase bold"),
                ],align="start",
                ),
            dbc.Row([
                html.Span("*Note: This growing season is used to sort drier/wetter years based on the seasonal total rainfall"),
                ],align="start",
                ),
            dbc.Row([
                dcc.RangeSlider(id='season-slider',
                    min=1, max=12, step=1,
                    marks={1: 'Jan', 2: 'Feb',3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'},
                    value=[6, 9]
                ) ,
                    ],align="start",
                ),
            ],style={"width": "80%"},),
        
        html.Br(),
        html.Div([
            html.Button(id='simulate-button-state', children='Simulate all scenarios (Run DSSAT)',
                        style={"width": "50%",'background-color': '#008CBA'}), #blue
        ],),
        html.Br(),
        html.Div([
            dbc.Row(
                dbc.Col(
                    html.Span("====================================================================", style={'color': 'black', 'font-style': 'italic', 'font-weight': 'bold'}),
                    width={"size": 6, "offset": 3},
                    ),
                ),
            dbc.Row(
                dbc.Col(
                    html.Span("----------------------------- Post-Simulation Analysis --------------------------------", style={'color': 'black', 'font-style': 'italic', 'font-weight': 'bold'}),
                    width={"size": 10, "offset": 3},
                    ),
                ),
            dbc.Row([
                html.Span("====================================================================",style={'color': 'black', 'font-style': 'italic', 'font-weight': 'bold'}),
                ],justify="center",
                ),
            ],style={"width": "80%"},),
        # dbc.Progress("25%", value=25),
        # dbc.Progress(id="progress"),
       # dbc.Spinner(children=[dcc.Graph(id = 'yield_boxplot')],size='lg',color='primary',type='border'),
        #dcc.Graph(id='yield_boxplot'),
        #EJ(4/17/2021)example:https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/DataTable/datatable_intro_and_sort.py
        dbc.Spinner(children=[html.Div(id='yieldbox-container')], size="lg", color="primary", type="border", fullscreen=True,),

        # html.Div(id='yieldbox-container'),  #boxplot
        html.Div(id='yieldcdf-container'),  #exceedance curve
        html.Div(id='yieldtimeseries-container'),  #time-series
        html.Div(id='yield-BN-container', style={"width": "33%", 'display': 'inline-block'}),
        html.Div(id='yield-NN-container', style={"width": "33%", 'display': 'inline-block'}),
        html.Div(id='yield-AN-container', style={"width": "33%", 'display': 'inline-block'}),
        html.Br(),
        html.Button("Download CSV file for Simulated Yield", id="btn_csv",
                    style={"width": "50%",'background-color': '#e7e7e7','color': 'black'}), #gray
        # dcc.Download(id="download-dataframe-csv"),
        Download(id="download-dataframe-csv"),
        html.Div(id='yieldtables-container', style = {'width': '100%'}),  #yield simulated output
        html.Br(),
        html.Div([
            dbc.Row(
                [
                    dbc.Col(html.Span("(i) Select a column name to sort: "), width=4),
                    dbc.Col(html.Div([dcc.Dropdown(id='column-dropdown', options=[{'label': 'YEAR', 'value': 'YEAR'},],value='YEAR')]), width=4),
                ],align="start",
                #justify="start",
            ),
            ],style={"width": "30%"},),
        html.Br(),
        html.Div([
            html.Span("(ii) Yield adjustment factor: "),
            dcc.Input(id="yield-multiplier", type="text", placeholder="Enter ", value = '1'),
            html.Span(" (e.g., 90% reduction => 0.9)"),  
            html.Br(),                 
            ]),
        html.Div([
            dbc.Row([
                html.Button("Click to update and sort the Datatable by the selected column name", id="btn_table_sort",
                            style={'background-color': 'white', 'color':'black', 'border':'2px solid #4CAF50'}), #green),
                ],align="start",
                ),
            ],style={"width": "30%"},),
        html.Br(),   
        html.Button("Download CSV file for SORTED Simulated Yield", id="btn_csv2",
                    style={"width": "50%",'background-color': '#e7e7e7','color': 'black'}), #gray),
        # dcc.Download(id="download-dataframe-csv"),
        Download(id="download-dataframe-csv2"),
        html.Div(id='yieldtables-container2', style = {'width': '100%'}),  #sorted yield simulated output
        html.Br(),
        html.Div([
            html.Button(id='EB-button-state', children='Display figures for Enterprise Budgets',
                    style={"width": "50%",'background-color': '#f44336'}), #red
        ],),
        html.Br(),
        html.Div(id='EBbox-container'), 
        html.Div(id='EBcdf-container'),  #exceedance curve
        html.Div(id='EBtimeseries-container'), #exceedance curve
        html.Br(),
        html.Button("Download CSV file for Enterprise Budgeting", id="btn_csv_EB",
                    style={"width": "50%",'background-color': '#e7e7e7','color': 'black'}), #gray),
        # dcc.Download(id="download-dataframe-csv"),
        Download(id="download-dataframe-csv_EB"),
        html.Div(id='EBtables-container', style = {'width': '50%'}),   #yield simulated output

        html.Br()
    ])
