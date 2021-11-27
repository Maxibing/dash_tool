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
from pathlib import Path
from global_parameters import *
from mysql_operation import *
from functools import partial

# 获取菜单
DATA_SUMMARY = get_category_summary(mysql_connect())
DATA_TYPE_CHECKLIST = get_main_and_sub_module(DATA_SUMMARY)


##########################################################################################
'''页面布局'''
##########################################################################################

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
        # 数据选择框，下拉框形式显示所有主模块(已去重)，数据库存储位置：[summary_test_data_category]-[main_module]
        html.Div(
            dcc.Dropdown(
                id="DataType",
                options=[{
                    'label': i,
                    'value': i
                } for i in DATA_TYPE_CHECKLIST.keys()],
                # 默认选中第一个主模块
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


##########################################################################################
'''回调函数'''
##########################################################################################

# 第一级选项回调，根据主模块筛选对应子模块，数据库存储位置：[summary_test_data_category]-[sub_module]
@app.callback(Output('l1_options', 'options'), [Input('DataType', 'value')])
def l1_options_update(DataType):
    return [{'label': i, 'value': i} for i in DATA_TYPE_CHECKLIST[DataType]]


# 第一级选项默认值，默认选中当前主模块下的第一个子模块
@app.callback(Output('l1_options', 'value'), [Input('DataType', 'value')])
def l1_value_update(DataType):
    return DATA_TYPE_CHECKLIST[DataType][0]


# 表格回调，显示子模块列表详细内容，数据库存储名就是sub_module字段的值
@app.callback(Output('table', 'columns'), Output('table', 'data'),
              Output('table', 'selected_rows'), [Input('l1_options', 'value')])
def table_update(l1_options):
    try:
        df = get_table_data(l1_options)
        return [{
            'name': i,
            'id': i
        } for i in df.columns], df.to_dict('records'), []
    except:
        return [], [], []


# 更新绘图，勾选的测试数据变化时更新
@app.callback(Output("data_display", "figure"), [
    Input("table", "selected_rows"),
    Input("table", "data"),
    Input('l1_options', 'value')
])
def data_graph_update(selected_rows, data, sub_module):
    # 如果没有勾选任何数据，则返回空
    if len(selected_rows) == []:
        return
    # 根据勾选的子模块，查找记录
    sub_record = DATA_SUMMARY[DATA_SUMMARY["sub_module"] == sub_module]
    # 获取绘图类型
    figure_type = sub_record["figure_type"].values[0]
    # 没有对应的绘图函数 ，直接返回
    if not DRAW_FUNCTIONS.__contains__(figure_type):
        return
    # 有对应的绘图函数，调用对应的绘图函数并返回
    _draw_func = partial(eval(DRAW_FUNCTIONS[figure_type]), selected_rows,
                         data, sub_record)

    return _draw_func()


##########################################################################################
'''绘图函数定义'''
##########################################################################################

# 折线图
def figure_lines(selected_rows, data, sub_record):
    # 获取测试数据类型
    data_type = sub_record["data_type"].values[0]
    # 获取折线标题
    plot_title = sub_record["plot_title"].values[0]
    # x,y轴对应参数
    x_type, y_type = sub_record["draw_parameters"].values[0].split(",")
    # 拼接绘图参数
    traces = []
    # 按勾选的测试数据分别绘制折线图
    for i in selected_rows:
        # 获取测试数据
        _test_data = partial(eval(DATA_GET_FUCNTIONS[data_type]), data[i])()
        # 如果获取测试数据失败，则跳过该条数据记录
        if _test_data.empty:
            continue
        # 添加折线图
        traces.append(
            go.Scatter(x=_test_data[x_type],
                       y=_test_data[y_type],
                       name=plot_title))
    # x,y轴名称
    xy_title = [x_type, y_type]
    # x,y轴格式及绘图标题
    design = go.Layout(xaxis=dict(title=xy_title[0],
                                  titlefont=dict(color="red",
                                                 family="STHeiti",
                                                 size=15)),
                       yaxis=dict(title=xy_title[1],
                                  titlefont=dict(color="red",
                                                 family="STHeiti",
                                                 size=15)),
                       title=dict(text=sub_record["sub_module"].values[0],
                                  font=dict(color="green",
                                            family="STHeiti",
                                            size=20)))

    # 返回绘图数据
    return dict(data=traces, layout=design)


##########################################################################################
'''测试数据获取'''
##########################################################################################

def get_csv_data(sub_table):
    # 尝试获取测试数据，如果获取失败，则返回空df
    try:
        return pd.read_csv(Path(MAIN_PATH) / sub_table["test_data"])
    except:
        return pd.DataFrame()


if __name__ == '__main__':
    app.run_server(host="192.168.29.128", port=8040, debug=True)
    # app.run_server(port=8023, debug=True)
