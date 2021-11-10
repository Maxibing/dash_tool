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
from mysql_operation import *

# 获取菜单
DATA_SUMMARY = get_category_summary(mysql_connect())
DATA_TYPE_CHECKLIST = get_main_and_sub_module(DATA_SUMMARY)

'''
页面布局
'''
app = dash.Dash()
app.layout = html.Div(children=[
    # 标题
    html.H1(children=DASH_TITLE, style={"color": "green"}),
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
                              } for i in DATA_TYPE_CHECKLIST.keys()],
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
    dash_table.DataTable(
        id='table',
        columns=[],
        data=[],
        row_selectable="multi",
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
    ),
    # 画图
    dcc.Graph(id="data_display", figure={})
])
'''
回调函数
'''


# 第一级选项回调
@app.callback(Output('l1_options', 'options'), [Input('DataType', 'value')])
def l1_options_update(DataType):
    return [{'label': i, 'value': i} for i in DATA_TYPE_CHECKLIST[DataType]]


# 第一级选项默认值
@app.callback(Output('l1_options', 'value'), [Input('DataType', 'value')])
def l1_value_update(DataType):
    return DATA_TYPE_CHECKLIST[DataType][0]


# 表格回调
@app.callback(Output('table', 'columns'), Output('table', 'data'),
              [Input('l1_options', 'value')])
def table_update(l1_options):
    try:
        df = get_table_data(l1_options)
        return [{
            'name': i,
            'id': i
        } for i in df.columns], df.to_dict('records')
    except:
        return [], []


# 更新绘图
@app.callback(Output("data_display", "figure"),
              [Input("table", "selected_rows"),
               Input("table", "data"),
               Input('l1_options', 'value')])
def data_graph_update(selected_rows, data, sub_module):
    if len(selected_rows) == []:
        return

    traces = []
    for i in selected_rows:
        _data = get_draw_data(data[i], sub_module)

        traces.append(
            go.Scatter(x=_data["origin_data"][_data["x"]],
                       y=_data["origin_data"][_data["y"]],
                       name=data[i][_data["plot_title"]]))
    xy_title = DATA_SUMMARY[DATA_SUMMARY["sub_module"]
                            == sub_module]["draw_parameters"][0].split(",")
    design = go.Layout(xaxis=dict(title=xy_title[0]),
                       yaxis=dict(title=xy_title[1]))

    return dict(data=traces, layout=design)


def get_draw_data(sub_table, sub_module):
    sub_record = DATA_SUMMARY[DATA_SUMMARY["sub_module"] == sub_module]
    figure_type = sub_record["figure_type"][0]
    data_type = sub_record["data_type"][0]
    plot_title = sub_record["plot_title"][0]
    if figure_type == None and data_type == "csv":
        x_type, y_type = sub_record["draw_parameters"][0].split(",")
        origin_data = pd.read_csv(sub_table["test_data"])
        result = {"x": x_type, "y": y_type,
                  "plot_title": plot_title, "origin_data": origin_data}

        return result


if __name__ == '__main__':
    # app.run_server(host="192.168.29.128", port=8050, debug=True)
    app.run_server(port=6513, debug=True)
