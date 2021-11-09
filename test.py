import dash
import dash_table
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')


if __name__ == '__main__':
    data=df.to_dict('records')
    print(data)