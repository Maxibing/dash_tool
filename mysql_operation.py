#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description     :
@Date     :2021/11/10 15:48:25
@Author      :xbMa
'''

import MySQLdb
import pandas as pd

from global_parameters import MySql_Host, MySql_UserName, MySql_PassWord, MySql_DataBase, MySql_Summary_Category

'''
mysql_connect() -- Connect mysql by global parameters.

get_category_summary() -- Get summary category of test data by mysql.

get_main_and_sub_module() -- Get select types for web.

    Inpput example:
    +----------------------------------+-----+
    | main_module |   sub_module       | ... |
    +----------------------------------+-----+
    |   ADC       |  ADC_CHANNEL_1     | ... |
    +----------------------------------+-----+
    |   ADC       |    ADC_VDD         | ... |
    +----------------------------------+-----+
    |  ThroughPut | Throught_UpLink    | ... |
    +----------------------------------+-----+
    |  ThroughPut |Throught_DownLink   | ... |
    +----------------------------------+-----+

    Output example:
    {'ADC': ['ADC_CHANNEL_1', 'ADC_VDD'], 'ThroughPut': ['Throught_UpLink', 'Throught_DownLink']}

get_draw_data() -- return the parameters for figure draw.
    {"x": x_type, "y": y_type,"plot_title": plot_title, "origin_data": origin_data}


'''


def mysql_connect():
    return MySQLdb.connect(MySql_Host, MySql_UserName, MySql_PassWord, MySql_DataBase)


def mysql_close(sql_con):
    sql_con.close()


def get_category_summary(sql_con):
    sql = f"SELECT * FROM {MySql_Summary_Category}"
    return pd.read_sql(sql, con=sql_con)


def get_main_and_sub_module(df_summary):
    # main_module 去重，取所有不重复元素
    main_module = df_summary["main_module"].unique()
    # 生成数据类型字典，key是main_module， 元素是main_module的子模块
    modules = dict()
    for m in main_module:
        modules[m] = list(
            df_summary[df_summary["main_module"] == m]["sub_module"])

    return modules


def get_table_data(table):
    sql = f"SELECT * FROM {table}"
    return pd.read_sql(sql, con=mysql_connect())


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


if __name__ == "__main__":
    mysql = mysql_connect()
    df_summary = get_category_summary(mysql)
    sql = f"SELECT * FROM adc_channel_1"
    file_path = pd.read_sql(sql, con=mysql)["test_data"][0]
    print(file_path)
    data = pd.read_csv(file_path)
    print(data)
