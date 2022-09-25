# !/usr/bin/python
# -*- coding: utf-8 -*-

from dash import Dash, html, dcc
import plotly.graph_objs as go


import pandas as pd
import regex as re
import config

data = pd.read_csv(config.PATH_TO_DATA)
data.rename(columns={'query': 'q'}, inplace=True)
data_copy = data.copy() #data_copy - "сырые данные"

#расчет метрики "бесполезности"
data.q = data.q.str.lower().str.split(',')
#раскладываем команды по спискам
intos, froms, joins = [], [], []

for x in data.q:
    for g in x:
        if 'join' in g:
            joins.append(g)
        if 'into' in g:
            intos.append(g)

for x in data[data.loguser.str.contains('dev')].q:
    for g in x:
        if 'from' in g:
            froms.append(g)

#регулярным выражением вырезаем название таблицы из команды
intos_tbs = [re.search('tbl_\d*', x).group(0) for x in intos]
froms_tbs = [re.search('tbl_\d*', x).group(0) for x in froms]
joins_tbs = [re.search('tbl_\d*', x).group(0) for x in joins]

# функция для датафрейма
def create_df(input_data, column):
    df = pd.DataFrame(data = input_data, columns=['col']).groupby('col').agg({'col': 'count'})
    df.columns= [column]
    df.reset_index(inplace=True)
    return df

# функция для объединения
def merge_df(data1, data2):
    data = data1.merge(data2, on ='col', how='outer')
    data = data.fillna(0)
    return data

# сводный даатфрейм
df = merge_df(merge_df(create_df(froms_tbs, 'count_froms'),create_df(joins_tbs, 'count_joins')),create_df(intos_tbs, 'count_intos'))
# для получения корректных результатов при делении добавим 1 в знаменатель
df.count_froms = df.count_froms + 1
# определяем метрику "бесполезности"
df['useless'] = round(df['count_intos'] / df['count_froms'])
df.fillna(0, inplace=True)
#включаем опцию, где inf (бесконечность) считаем как NaN
pd.set_option('mode.use_inf_as_na', True)
# ТОП-10 "бесполезных таблиц"
df.sort_values(by = 'useless', ascending = False, inplace = True)
top = df.head(10)
top = top.drop(columns=['count_joins'])
top.columns = ['Название таблицы', 'Кол-во from', 'Кол-во into', 'Уровень бесполезности']

#Распределение пользователей по кол-ву запросов
# сгруппируем по пользователям
data_users = data.groupby('loguser').agg({'rn':'nunique'}).sort_values('rn', ascending=False).reset_index().rename(columns={'rn':'count_rn'})
# разделим пользователей
etl_users = data_users[data_users['loguser'].str.startswith('etl')]
dev_users = data_users[data_users['loguser'].str.startswith('dev')]

# разделим значения в запросах по запятой и сгруппируем по пользователю
data_copy['count_q'] = data_copy['q'].apply(lambda x: x.split(","))
data_count_q = data_copy.explode('count_q')
df_exp = data_count_q.copy()
data_count_q = data_count_q.groupby('loguser').agg({'count_q':'count'}).sort_values('count_q', ascending=False).reset_index()
# разделим пользователей
etl_count_q = data_count_q[data_count_q['loguser'].str.startswith('etl')]
dev_count_q = data_count_q[data_count_q['loguser'].str.startswith('dev')]

df_exp = df_exp.groupby(['loguser','count_q']).agg({'count_q':'count'}).rename(columns={'count_q':'q'})
df_exp = df_exp.reset_index()
df_exp['tab'] = [re.search('tbl_\d*', x).group(0) for x in df_exp['count_q']]
df_exp = df_exp[['loguser', 'q', 'tab']]
df_exp = df_exp.rename(columns={'q':'count'}).sort_values('count', ascending=False)
df_heatmap = df_exp.set_index('tab')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    children=[
        # формируем html
        html.H1('Анализ работы хранилища данных на основании обработки логов'),
        html.Div(children=[html.P('Для анализа другого файла с логами замените путь в файле config.py')]),
        html.Div(children=[
            dcc.Graph(
                figure={
                    'data': [
                        go.Table(
                            header=dict(values=list(top.columns),
                                        fill_color='grey',
                                        font=dict(color='white'),
                                        line_color='darkslategray',
                                        align='center'),
                            cells=dict(values=[top['Название таблицы'],
                                               top['Кол-во from'],
                                               top['Кол-во into'],
                                               top['Уровень бесполезности']],
                                       fill_color=[
                                           ['red', 'red', 'red',
                                            'lightcoral', 'lightcoral', 'lightcoral',
                                            'yellow', 'yellow', 'yellow', 'yellow']*4],
                                       line_color='darkslategray',
                                       align='center'))
                    ],
                }
            ),
        ], ),
        html.Div(children=[
            dcc.Graph(
                figure={
                    'data': [
                        go.Bar(
                            x=etl_users.head(10)['loguser'],
                            y=etl_users.head(10)['count_rn'],
                            name='top_etl_users',
                        )
                    ],
                    'layout': go.Layout(
                        xaxis={'title': 'Логин пользователя'},
                        yaxis={'title': 'Количество запросов'},
                        title='ТОП-10 "etl"-пользователей по количеству запросов',
                    ),
                }
            ),
            ], className = 'five columns'),
        html.Div(children=[
            dcc.Graph(
                figure={
                    'data': [
                        go.Bar(
                            x=dev_count_q.head(10)['loguser'],
                            y=dev_users.head(10)['count_rn'],
                            name='top_dev_users',
                        )
                    ],
                    'layout': go.Layout(
                        xaxis={'title': 'Логин пользователя'},
                        yaxis={'title': 'Количество запросов'},
                        title='ТОП-10 "dev"-пользователей по количеству запросов',
                    ),
                },
            ),
            ], className = 'five columns'),
    html.Div(children=[
            dcc.Graph(
                figure={
                    'data': [
                        go.Bar(
                            x=etl_count_q.head(10)['loguser'],
                            y=etl_count_q.head(10)['count_q'],
                            name='top_etl_users',
                        )
                    ],
                    'layout': go.Layout(
                        xaxis={'title': 'Логин пользователя'},
                        yaxis={'title': 'Количество действий в запросах'},
                        title='ТОП-10 "etl"-пользователей по количеству действий в запросах',
                    ),
                }
            ),
            ], className = 'five columns'),
        html.Div(children=[
            dcc.Graph(
                figure={
                    'data': [
                        go.Bar(
                            x=dev_count_q.head(10)['loguser'],
                            y=dev_count_q.head(10)['count_q'],
                            name='top_dev_users',
                        )
                    ],
                    'layout': go.Layout(
                        xaxis={'title': 'Логин пользователя'},
                        yaxis={'title': 'Количество действий в запросах'},
                        title='ТОП-10 "dev"-пользователей по количеству действий в запросах',
                    ),
                },
            ),
            ], className = 'five columns')
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)