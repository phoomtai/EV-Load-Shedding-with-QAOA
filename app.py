from dash import Dash, dcc, html, Input, Output, dash_table, callback, State, ctx
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
from settings import config
import time
from openqaoa import QAOA
from openqaoa.problems import Knapsack
import pprint
from compute.data import parse_contents
from compute.algorithm import compute_knapsack

app = Dash(name=config.app_name, assets_folder='assets', external_stylesheets=[dbc.themes.LUX])
app.title = config.app_name

navigation_bar = dbc.Nav(className="nav nav-pills", children=[
    dbc.NavItem(html.Img(src=app.get_asset_url('logo.png'), style={'width':'25%'})),
    dbc.NavItem(html.Div([
        dbc.NavLink("About", href="/", id="about-popover", active=False),
        dbc.Popover(id="about", is_open=False, target="about-popover", children=[
            dbc.PopoverHeader("About Us"), dbc.PopoverBody(config.about)
        ])
    ])),
    
    dbc.DropdownMenu(label="Links", nav=True, children=[
        dbc.DropdownMenuItem([html.I(className="fa fa-linkedin"), "  Contacts"], href=config.contacts, target="_blank"),
        dbc.DropdownMenuItem([html.I(className="fa fa-github"), "  GitHub"], href=config.code, target="_blank"),
        ]) 
       
])
@app.callback(output=[Output(component_id="about", component_property="is_open"), 
                      Output(component_id="about-popover", component_property="active")], 
              inputs=[Input(component_id="about-popover", component_property="n_clicks")], 
              state=[State("about","is_open"), State("about-popover","active")]
)
def about_popover(n, is_open, active):
    if n:
        return not is_open, active
    return is_open, active


Inputs = dbc.Form([
    
    dbc.Label("Select a base unit", html_for="select_unit_dropdown"),
    dcc.Dropdown(
        options=['Watt','kW','MW','GW'],
        id='select_unit_dropdown',
        placeholder='Please Select base unit'
        ),
    html.Br(),html.Br(),
    dbc.Label("Please put your maximum capacity :  ", html_for="maximum_capacity"),
    dcc.Input(id="max_cap", type="number" , placeholder="Put your maximum capacity here"),
    
    html.Br(),html.Br(),
    dbc.Label("Please put your electric consumption :  ", html_for="electric_consumption"),
    dcc.Input(id="elec_consump", type="number" , placeholder="Put your electric consumption here"),

    html.Br(),html.Br(),
    dbc.Label("Please Low priority load as a list :  ", html_for="electric_available"),
    dash_table.DataTable(
        id='low_priority',
        columns=([{'id': 'Name', 'name': 'Name'}]+
                 [{'id': 'Load consumption', 'name': 'Load consumption'}]+
                 [{'id': 'Value', 'name': 'Value'}]),
        data=[{'Name': '', 'Load consumption': '', 'Value': ''}],
        row_deletable=True,
        editable=True,
            ),
    html.Button('Add Row', id='editing-rows-button', n_clicks=0),

    html.Br(),html.Br(),
    dbc.Label("Or Upload your file here :  ", html_for="upload_file"),
    dcc.Upload(id='upload_file', children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={'width':'100%', 'height':'60px', 'lineHeight':'60px', 'borderWidth':'1px', 'borderStyle':'dashed',
                      'borderRadius':'5px', 'textAlign':'center', 'margin':'10px'}),
    html.Div(id='excel-name', style={"marginLeft":"10px"}),
    
    
    html.Br(),html.Br(),
    dbc.Col(dbc.Button("Run", id="run",color="primary")),
    html.Div(id='testtest')
    
])

# block wrong input
@callback(
    Output('run','disabled'),
    Input('max_cap', 'value'),Input('elec_consump', 'value')
)
def state_userInput(max_cap,elec_consump):
    if any (v is None for v in [max_cap,elec_consump]):
        return False
    elif max_cap < elec_consump or max_cap == elec_consump:
        return True
    else:
        return False

# adding row to table
@callback(
    Output('low_priority', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('low_priority', 'data'),
    State('low_priority', 'columns')
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

# data processing and compute
@callback(
    Output('solution_output', 'children'),
    Output('testtest', 'children'),
    Input('low_priority','data'), 
    Input('run','n_clicks'),
    Input('max_cap', 'value'),
    Input('elec_consump', 'value'),
    State('upload_file','contents'),
    State('upload_file', 'filename'),
    State('upload_file', 'last_modified'),
    Input('select-algorithm','value')
)
def display_output_test(rows, run_botton, max_cap, elec_consump, list_of_contents, list_of_names, list_of_dates, algorithm):
    if list_of_contents is not None:
        childrens = [parse_contents(list_of_contents, list_of_names, list_of_dates)]
        if "run" == ctx.triggered_id:
            return compute_knapsack(max_cap, elec_consump, childrens[0][1], algorithm), None
        else:
            return None, None
    elif list_of_contents is None:
        if "run" == ctx.triggered_id:
            return compute_knapsack(max_cap, elec_consump,rows, algorithm), None
        else:
            return None, None
    else:
        return None, None
    

# Convert uploaded file to a pandas dataframe
@callback(Output('output-data-upload', 'children'),
              Input('upload_file', 'contents'),
              State('upload_file', 'filename'),
              State('upload_file', 'last_modified')
              )
def update_output(list_of_contents, list_of_names, list_of_dates):
    print(list_of_names)
    if list_of_contents is not None:
        childrens = [
            parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return childrens[0][0]

main_body = dbc.Row([
    dcc.ConfirmDialog(
        id='confirm',
        message='You put your maximum capacity less than your electric consumption, please check again',
        ),
    dbc.Col(md=3,children=[
        Inputs,
        html.Br(),html.Br(),html.Br(),
    ]),
    
    dbc.Col(md=9,children=[
            dbc.Spinner([
                dcc.RadioItems(
                    ['Linear Programming', 'Quantum Computing'],id='select-algorithm',
                ),
                # dbc.Badge(html.A('Download', id='download-excel', download="tables.xlsx", href="", target="_blank"), color="success", pill=True),
                html.Div(id='output-data-upload'),
                html.Hr(),
                html.Div(id='solution_output'),
            ])
    ]),
])

# block wrong input by warning sign
@callback(
    Output('confirm','displayed'),
    Input('max_cap', 'value'),Input('elec_consump', 'value')
)
def warn(max_cap,elec_consump):
    if any (v is None for v in [max_cap,elec_consump]):
        return False
    elif max_cap < elec_consump or max_cap == elec_consump:
        time.sleep(2.5)
        return True
    else:
        return False

    

app.layout = dbc.Container(fluid=True, children=[
    navigation_bar,
    html.Br(),html.Br(),html.Br(),
    main_body,
]
)
if __name__ == '__main__':
    app.run(debug=True)