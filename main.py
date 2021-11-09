#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description     :
@Date     :2021/11/08 17:24:02
@Author      :xbMa
'''

import pandas as pd
import plotly.graph_objs as go
import dash
import dash_table
import dash_core_components as dcc  # 交互式组件
import dash_html_components as html  # 代码转html

from dash.dependencies import Input, Output  # 回调

from global_parameters import *

app = dash.Dash()

# 页面布局
app.layout = html.Div(children=[
    # 标题
    html.H1(children=TITLE, style={"color": "green"}),
    # 说明
    html.Div(
        children='''Dash: A web application to present nurlink test data.''',
        style={"color": "gray"}),
    # 空一行
    html.Br(),
    # 测试数据选项
    html.Div([
        # 数据选择标题
        html.Div(html.Label("数据选择"), style={
            'font-size': '25',
        }),
        # 数据选择框
        html.Div(dcc.Dropdown(id="DataType",
                              options=[{
                                  'label': i,
                                  'value': i
                              } for i in list(DATA_TYPE_CHECKLIST.keys())],
                              value=list(DATA_TYPE_CHECKLIST.keys())[0]),
                 style={
                     'margin-top': 10,
                     'width': '10%'
                 }),
    ]),
    # 分隔线
    html.Hr(),
    # 第一级选项菜单
    dcc.RadioItems(id='l1_options'),
    # 表格
    dash_table.DataTable(id='table',
                        columns = [],
                        data = [],
                        row_selectable="multi",
                        selected_rows=[],
                        page_action="native",
                        page_current= 0,
                        page_size= 10,
                        ),
])


# 第一级选项回调
@app.callback(Output('l1_options', 'options'), [Input('DataType', 'value')])
def l1_options_update(value):
    return [{'label': i, 'value': i} for i in DATA_TYPE_CHECKLIST[value]]


# 第一级选项默认值
@app.callback(Output('l1_options', 'value'), [Input('DataType', 'value')])
def l1_value_update(DataType):
    return  DATA_TYPE_CHECKLIST[DataType][0]

# 表格回调
@app.callback(Output('table', 'columns'), Output('table', 'data'), [Input('DataType', 'value'), Input('l1_options', 'value')])
def table_columns_update(DataType, l1_options):
    if DataType == "ADC" and l1_options == "Sensor":
        df = get_data(SENSOR)

    if DataType == "ADC" and l1_options == "VDD":
        df = get_data(VDD)

    return [{'name': i, 'id': i} for i in df.columns], df.to_dict('records')

def get_data(path):
    df = pd.read_csv(path)
    return df


if __name__ == '__main__':
    app.run_server(host="192.168.29.128", debug=True)
    # app.run_server(host="192.168.0.107", debug=True)
