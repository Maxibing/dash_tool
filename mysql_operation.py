#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description     :
@Date     :2021/11/10 15:48:25
@Author      :xbMa
'''

import MySQLdb
import pandas as pd

from global_parameters import MySql_Host, MySql_UserName, MySql_PassWord, MySql_DataBase


def mysql_connect():
    return MySQLdb.connect(MySql_Host, MySql_UserName, MySql_PassWord, MySql_DataBase)


if __name__ == "__main__":
    mysql =  mysql_connect()
    
    sql = "SELECT * FROM summary_test_data_category"
    
    df = pd.read_sql(sql, con=mysql)

    print(df)
    
    mysql.close()
