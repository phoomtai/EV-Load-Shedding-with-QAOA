import pandas as pd
import io
import base64
import numpy as np
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State, ctx
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
from settings import config
import time
import datetime

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return [html.Div([
        html.Hr(),
        html.H5(filename),

        dash_table.DataTable(
            df.to_dict('records')
            ,[{'name': i, 'id': i} for i in df.columns]
        ),
    ]),df.to_dict('records')
            ]