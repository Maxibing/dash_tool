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

'''
页面布局
'''
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
                              } for i in DATA_TYPE_CHECKLIST],
                              value=DATA_TYPE_CHECKLIST[0]),
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
    return [{'label': i, 'value': i} for i in eval(DataType)]


# 第一级选项默认值
@app.callback(Output('l1_options', 'value'), [Input('DataType', 'value')])
def l1_value_update(DataType):
    return eval(DataType)[0]

# 表格回调
@app.callback(Output('table', 'columns'), Output('table', 'data'), [Input('l1_options', 'value')])
def table_update(l1_options):
    try:
        df = get_table_data(eval(l1_options))
        return [{'name': i, 'id': i} for i in df.columns], df.to_dict('records')
    except:
        return [], []

# 更新绘图
@app.callback(Output("data_display", "figure"), [Input("table", "selected_rows"), Input("table", "data")])
def data_graph_update(selected_rows, data):
    print(selected_rows)
    print(data)
    if len(selected_rows) == []:
        return
    
    traces = []
    for i in selected_rows:
        df = get_table_data(data[i]["Data_Source"])

        traces.append(go.Scatter(x=df["Set"], y=df["Actual_Error"], name=dfVersionz["Version"]))



    design = go.Layout(xaxis=dict(title="Set"),
                       yaxis=dict(title="Actual_Error"))

    return dict(data=traces, layout=design)


'''
其他接口
'''
def get_table_data(path):
    df = pd.read_csv(path)
    return df


if __name__ == '__main__':
    app.run_server(host="192.168.29.128", debug=True)
    # app.run_server(host="192.168.0.109", debug=True)
