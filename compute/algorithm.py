import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from openqaoa import QAOA
from openqaoa.problems import Knapsack
import pprint
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State, ctx
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from pulp import LpMinimize, LpMaximize , LpStatus, lpSum, LpVariable,LpProblem
import pulp


def compute_knapsack(installed_cap, used_cap, data_table, algorithm):
    availble_cap = installed_cap - used_cap
    df = pd.DataFrame(data_table, columns=['Name', 'Load consumption', 'Value'])
    df['Load consumption'] = df['Load consumption'].astype(int)
    df['Value'] = df['Value'].astype(int)
    data_array = df.to_numpy()
    name = data_array[:,0].tolist()
    weigth = data_array[:,1].tolist()
    values = data_array[:,2].tolist()
    if algorithm == 'Quantum Computing':
        knapsack = Knapsack(values=values, weights=weigth, weight_capacity=availble_cap, penalty=120)
        knapsack_qubo = knapsack.qubo
        q = QAOA()
        q.compile(knapsack_qubo)
        q.optimize(knapsack_qubo)
        child = q.result.lowest_cost_bitstrings()
        return f'{child}'
    else:
        model = LpProblem(name='Knapsack',sense=LpMaximize)
        x = {i: LpVariable(name=f'n{i}',cat='Binary') for i in range(np.size(weigth))}
        
        model += lpSum(x[i] * weigth[i] for i in range(np.size(weigth))) <= availble_cap
        
        model += lpSum(x[i]*values[i] for i in range(np.size(weigth)) )
        
        model.solve()
        model_var = ''
        i = 0
        for var in model.variables():
            model_var += f'{name[i]} : {var.value()} \n\n'
            i += 1
        return f'objective values is : {model.objective.value()} \n status is : {model_var}'
        


# df = pd.DataFrame({'Name' : ['A','B','C','D'],
#                    'Load Consumption': [10,20,30,40],
#                    'Value': [100,200,300,250]})
# a = compute_knapsack(100,50,df)
# print(a)