import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table

from datetime import date
from dash_extensions import Download

import form

scenario_name = dbc.FormGroup([ # Scenario
      dbc.Label("1) Scenario Name", html_for="sce-name", sm=3, className="p-0", align="start", ),
      dbc.Col([
        dbc.Input(type="text", id="sce-name", value="", minLength=4, maxLength=4, required="required", ),
      ],
      xl=9,
      ),
    ],
    row=True
    )

station = dbc.FormGroup([ # Station
      dbc.Label("2) Station", html_for="ETstation", sm=3, className="p-0", align="start", ),
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
        ),
      ],
      xl=9,
      ),
    ],
    row=True
    )


crop = dbc.FormGroup([ # Crop
      dbc.Label("3) Crop", html_for="crop-radio", sm=3, className="p-0", align="start", ),
      dbc.Col([
        dcc.RadioItems(
          id="crop-radio",
          # options=[{"label": k, "value": k} for k in cultivar_options.keys()],
          options = [
            {"label": "Maize", "value": "MZ"}, 
            {"label": "Wheat", "value": "WH"}, 
            {"label": "Sorghum", "value": "SG"},
          ],
          labelStyle = {"display": "inline-block","margin-right": 10},
          value="MZ",
        ),
      ],
      xl=9,
      ),
    ],
    row=True
    )


cultivar = dbc.FormGroup([ # Cultivar
      dbc.Label("4) Cultivar", html_for="cultivar-dropdown", sm=3, className="p-0", align="start", ),
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
        ),
      ],
      xl=9,
      ),
    ],
    row=True
    )


start_year = dbc.FormGroup([ # Start Year
      dbc.Label("5) Start Year", html_for="year1", sm=3, className="p-0", align="start", ),
      dbc.Col([
        dbc.Input(type="number", id="year1", placeholder="YYYY", value="1981", min=1981, max=2018, required="required", ),
        dbc.FormText("(No earlier than 1981)"),
      ],
      xl=9,
      ),
    ],
    row=True
    )

end_year = dbc.FormGroup([ # End Year
      dbc.Label("6) End Year", html_for="year2", sm=3, className="p-0", align="start", ),
      dbc.Col([
        dbc.Input(type="number", id="year2", placeholder="YYYY", value="2018", min=1981, max=2018, required="required", ),
        dbc.FormText("(No later than 2018)"),
      ],
      xl=9,
      ),
    ],
    row=True
    )

target_year = dbc.FormGroup([ # Year to Highlight
      dbc.Label("7) Year to Highlight", html_for="target-year", sm=3, className="p-0", align="start", ),
      dbc.Col([
        dbc.Input(type="number", id="target-year", placeholder="YYYY", value="2015",min=1981, max=2018, required="required", ),
        dbc.FormText("Type a specific year you remember (e.g., drought year) and want to compare with a full climatology distribution"),
      ],
      xl=9,
      ),
    ],
    row=True
    )

soil_type = dbc.FormGroup([ # Soil Type
      dbc.Label("8) Soil Type", html_for="ETsoil", sm=3, className="p-0", align="start", ),
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
        ),
      ],
      xl=9,
      ),
    ],
    row=True
    )

init_soil_water_cond = dbc.FormGroup([ # Initial Soil Water Condition
      dbc.Label("9) Initial Soil Water Condition", html_for="ini-H2O", sm=3, className="p-0", align="start", ),
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
        ),
      ],
      xl=9,
      ),
    ],
    row=True
    )


init_soil_no3_cond = dbc.FormGroup([ # Initial NO3 Condition
      dbc.Label("10) Initial Soil NO3 Condition", html_for="ini-NO3", sm=3, className="p-0", align="start", ),
      dbc.Col([
        dcc.Dropdown(
          id="ini-NO3", 
          options=[
            {"label": "High(65 N kg/ha)", "value": "H"},
            {"label": "Low(23 N kg/ha)", "value": "L"},
          ], 
          value="L",
        ),                
      ],
      xl=9,
      ),
    ],
    row=True
    )

plt_date = dbc.FormGroup([ # Planting Date
      dbc.Label("11) Planting Date", html_for="plt-date-picker", sm=3, className="p-0", align="start", ),
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
      xl=9,
      ),
    ],
    row=True
    )

plt_dens = dbc.FormGroup([ # Planting Density
      dbc.Label(["12) Planting Density", html.Span(" (plants/m"), html.Sup("2"), html.Span(")"), ], html_for="plt-density", sm=3, className="p-0", align="start", ),
      dbc.Col([
        dbc.Input(type="number", id="plt-density", value=5, min=1, max=300, step=0.1, required="required", ),
      ],
      xl=9,
      ),
    ],
    row=True
    )

fert_application = dbc.FormGroup([ # Fertilizer Application
      dbc.Label("13) Fertilizer Application", html_for="fert_input", sm=3, className="p-0", align="start", ),
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
        html.Div([ # FERTILIZER INPUT TABLE
          dbc.Row([
            dbc.Col(
              dbc.Label("Days After Planting", className="text-center", ),
            ),
            dbc.Col(
              dbc.Label("Amount of N (kg/ha)", className="text-center", ),
            ),
          ],),
          dbc.Row([
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("1st", html_for="fert-day1", ),
                dbc.Input(type="number", id="fert-day1", value=0, min="0", max="365", required="required", ),
              ],),
            ),
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("1st", html_for="fert-amt1", ),
                dbc.Input(type="number", id="fert-amt1", value=0, min="0", step="0.1", required="required", ),
              ],),
            ),
          ],),
          dbc.Row([
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("2nd", html_for="fert-day2", ),
                dbc.Input(type="number", id="fert-day2", value=0, min="0", max="365", required="required", ),
              ],),
            ),
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("2nd", html_for="fert-amt2", ),
                dbc.Input(type="number", id="fert-amt2", value=0, min="0", step="0.1", required="required", ),
              ],),
            ),
          ],),
          dbc.Row([
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("3rd", html_for="fert-day3", ),
                dbc.Input(type="number", id="fert-day3", value=0, min="0", max="365", required="required", ),
              ],),
            ),
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("3rd", html_for="fert-amt3", ),
                dbc.Input(type="number", id="fert-amt3", value=0, min="0", step="0.1", required="required", ),
              ],),
            ),
          ],),
          dbc.Row([
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("4th", html_for="fert-day4", ),
                dbc.Input(type="number", id="fert-day4", value=0, min="0", max="365", required="required", ),
              ],),
            ),
            dbc.Col(
              dbc.FormGroup([
                dbc.Label("4th", html_for="fert-amt4", ),
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
      xl=9,
      ),
    ],
    row=True
    )

EB = dbc.FormGroup([ # Enterprise Budgeting?
      dbc.Label("14) Enterprise Budgeting?", html_for="EB_radio", sm=3, className="p-0", align="start", ),
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
        html.Div([ # ENTERPRISE BUDGETING TABLE
          dbc.Row([
            dbc.Col([  
              dbc.FormGroup([
                dbc.Label("Crop Price", html_for="crop-price", style={"height": "7vh"}, align="start", ),
                dbc.Input(type="number", id="crop-price", value="0", min="0", step="0.1", required="required", ),
                dbc.FormText("[ETB/kg]"),
              ]),
            ],),
            dbc.Col([  
              dbc.FormGroup([
                dbc.Label("Fertilizer Price", html_for="fert-cost", style={"height": "7vh"}, align="start", ),
                dbc.Input(type="number", id="fert-cost", value="0", min="0", step="0.1", required="required", ),
                dbc.FormText("[ETB/N kg]"),
              ]),
            ],),
            dbc.Col([  
              dbc.FormGroup([
                dbc.Label("Seed Cost", html_for="seed-cost", style={"height": "7vh"}, align="start", ),
                dbc.Input(type="number", id="seed-cost", value="0", min="0", step="0.1", required="required", ),
                dbc.FormText("[ETB/ha]"),
              ]),
            ],),
            dbc.Col([  
              dbc.FormGroup([
                dbc.Label("Other Variable Costs", html_for="variable-costs", style={"height": "7vh"}, align="start", ),
                dbc.Input(type="number", id="variable-costs", value="0", min="0", step="0.1", required="required", ),
                dbc.FormText("[ETB/ha]"),
              ]),
            ],),
            dbc.Col([  
              dbc.FormGroup([
                dbc.Label("Fixed Costs", html_for="fixed-costs", style={"height": "7vh"}, align="start", ),
                dbc.Input(type="number", id="fixed-costs", value="0", min="0", step="0.1", required="required", ),
                dbc.FormText("[ETB/ha]"),
              ]),
            ],),
          ],),
          dbc.FormText("See the Tutorial for more details of calculation"),
        ],
        id="EB-table-Comp", 
        className="w-100",
        style={"display": "none"},
        ),
      ],
      xl=9,
      ),
    ],
    row=True
    )

def ET_hist_form():
    layout = html.Div(
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
              scenario_name,
              station,
              crop,
              cultivar,
              start_year,
              end_year,
              target_year,
              soil_type,
              init_soil_water_cond,
              init_soil_no3_cond,
              plt_date,
              plt_dens,
              fert_application,
              EB,
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
                {"id": "iH2O", "name": "Initial Soil Water Content"},
                {"id": "iNO3", "name": "Initial Soil Nitrate Content"},
                {"id": "TargetYr", "name": "Target Year"},
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
                dict(**{param: "N/A" for param in form.sce_col_names}) for i in range(1, 2)
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
            dbc.Label("15) Critical growing period to relate rainfall amount with crop yield", html_for="season-slider"),
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
    )
    return layout

def ET_hist_graphs():
    layout = html.Div([
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
            html.B("Simulated Yield Original CSV"),
          className=" card-header"
          ),
          html.Div(
            html.Div([
              html.Div([
                html.Div([ # ORIGINAL CSV STUFF
                  dbc.Row([
                    dbc.Col(
                      dbc.Button(id="btn_csv_yield", 
                      children="Download CSV for Simulated Yield", 
                      className="w-100 d-block mx-auto",
                      color="secondary",
                      ),
                    md=4,
                    ),
                    dbc.Col(
                      dbc.Button(id="btn_csv_Pexe", 
                      children="Download CSV for Prob. of Exceedance", 
                      className="w-100 d-block mx-auto",
                      color="secondary",
                      ),
                    md=4,
                    ),
                    dbc.Col(
                      dbc.Button(id="btn_csv_rain", 
                      children="Download CSV for Seasonal Rainfall", 
                      className="w-100 d-block mx-auto",
                      color="secondary",
                      ),
                    md=4,
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
                  #EJ(6/7/2021) to download each column separately into a csv
                  dbc.Button(id="btn_csv2_yield", 
                  children="Download CSV for SORTED simulated Yield", 
                  className="w-75 d-block mx-auto",
                  color="secondary"
                  ),
                  html.Br(),
                  dbc.Button(id="btn_csv2_rain", 
                  children="Download CSV for SORTED seasonal rainfall", 
                  className="w-75 d-block mx-auto",
                  color="secondary"
                  ),
                  html.Br(),
                  dbc.Button(id="btn_csv2_Pexe", 
                  children="Download CSV for SORTED prob. of exceedance", 
                  className="w-75 d-block mx-auto",
                  color="secondary"
                  ),
                  #   Download(id="download-dataframe-csv2"),
                  Download(id="download-dataframe-csv2-yield"),
                  Download(id="download-dataframe-csv2-rain"),
                  Download(id="download-dataframe-csv2-Pexe"),
                
                  #end of EJ(6/7/2021) update
                  html.Div(id="yieldtables-container2", 
                  className="overflow-auto",
                  style={"height": "20vh"},
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
      className="d-none",
      ),
  

      html.Div( # ENTERPRISE BUDGETING
        html.Div([
          html.Header(
            html.B("Enterprise Budgeting"),
          className=" card-header",
          ),
          html.Div([
            html.Br(),
            dbc.Button(id="EB-button-state", 
            children="Display figures for Enterprise Budgets", 
            className="w-75 d-block mx-auto",
            color="danger"
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

            html.Div([
              html.Br(),
              dbc.Button(id="btn_csv_EB", 
              children="Download CSV file for Enterprise Budgeting", 
              className="w-75 d-block mx-auto",
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
    )
    return layout


def ET_hist():
    layout = dbc.Row([
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
                  scenario_name,
                  station,
                  crop,
                  cultivar,
                  start_year,
                  end_year,
                  target_year,
                  soil_type,
                  init_soil_water_cond,
                  init_soil_no3_cond,
                  plt_date,
                  plt_dens,
                  fert_application,
                  EB,
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
                    {"id": "iH2O", "name": "Initial Soil Water Content"},
                    {"id": "iNO3", "name": "Initial Soil Nitrate Content"},
                    {"id": "TargetYr", "name": "Target Year"},
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
                    dict(**{param: "N/A" for param in form.sce_col_names}) for i in range(1, 2)
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
                dbc.Label("15) Critical growing period to relate rainfall amount with crop yield", html_for="season-slider"),
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
                html.B("Simulated Yield Original CSV"),
              className=" card-header"
              ),
              html.Div(
                html.Div([
                  html.Div([
                    html.Div([ # ORIGINAL CSV STUFF
                      dbc.Row([
                        dbc.Col(
                          dbc.Button(id="btn_csv_yield", 
                          children="Download CSV for Simulated Yield", 
                          className="w-100 d-block mx-auto",
                          color="secondary",
                          ),
                        md=4,
                        ),
                        dbc.Col(
                          dbc.Button(id="btn_csv_Pexe", 
                          children="Download CSV for Prob. of Exceedance", 
                          className="w-100 d-block mx-auto",
                          color="secondary",
                          ),
                        md=4,
                        ),
                        dbc.Col(
                          dbc.Button(id="btn_csv_rain", 
                          children="Download CSV for Seasonal Rainfall", 
                          className="w-100 d-block mx-auto",
                          color="secondary",
                          ),
                        md=4,
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
                      #EJ(6/7/2021) to download each column separately into a csv
                      dbc.Button(id="btn_csv2_yield", 
                      children="Download CSV for SORTED simulated Yield", 
                      className="w-75 d-block mx-auto",
                      color="secondary"
                      ),
                      html.Br(),
                      dbc.Button(id="btn_csv2_rain", 
                      children="Download CSV for SORTED seasonal rainfall", 
                      className="w-75 d-block mx-auto",
                      color="secondary"
                      ),
                      html.Br(),
                      dbc.Button(id="btn_csv2_Pexe", 
                      children="Download CSV for SORTED prob. of exceedance", 
                      className="w-75 d-block mx-auto",
                      color="secondary"
                      ),
                      #   Download(id="download-dataframe-csv2"),
                      Download(id="download-dataframe-csv2-yield"),
                      Download(id="download-dataframe-csv2-rain"),
                      Download(id="download-dataframe-csv2-Pexe"),
                    
                      #end of EJ(6/7/2021) update
                      html.Div(id="yieldtables-container2", 
                      className="overflow-auto",
                      style={"height": "20vh"},
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
          className="d-none",
          ),
      

          html.Div( # ENTERPRISE BUDGETING
            html.Div([
              html.Header(
                html.B("Enterprise Budgeting"),
              className=" card-header",
              ),
              html.Div([
                html.Br(),
                dbc.Button(id="EB-button-state", 
                children="Display figures for Enterprise Budgets", 
                className="w-75 d-block mx-auto",
                color="danger"
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

                html.Div([
                  html.Br(),
                  dbc.Button(id="btn_csv_EB", 
                  children="Download CSV file for Enterprise Budgeting", 
                  className="w-75 d-block mx-auto",
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
    )
    return layout