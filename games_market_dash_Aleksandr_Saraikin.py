import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go


def get_data_frame():
    """
        Считывание и предобработка данных
    """
    df = pd.read_csv('games.csv').dropna()
    df_2000_2022 = df[(df['Year_of_Release'] >= 2000) & (df['Year_of_Release'] <= 2022)]
    return df_2000_2022


def get_amount_games(data):
    '''
    :param data: DataFrame
    :return: Колисчество строк
    '''
    return len(data)


def get_mean_user_score(data):
    '''
    Преобразование колонки с оценками и вычисление среднего
        :param data: DataFrame
        :return: Среднее значение пользовательских оценок
    '''
    no_tbd_df = data[data['User_Score'] != 'tbd']
    no_tbd_df['User_Score'] = no_tbd_df['User_Score'].apply(lambda x: float(x))
    mean = no_tbd_df['User_Score'].mean()
    return round(mean, 3)


def get_mean_critic_score(data):
    '''
    Преобразование колонки с оценками и вычисление среднего
        :param data: DataFrame
        :return: Среднее значение оценок критиков
    '''
    mean = data['Critic_Score'].mean()
    return round(mean, 3)


def numeric_func(x):
    '''
    Преобразование возрастног рейтинга в числовой формат
    :param x: Экземпляр
    :return: Возрастной рейтинг в числовом формате
    '''
    if x == 'E':
        return 7
    if x == 'T':
        return 12
    if x == 'M':
        return 16
    if x == 'E10+':
        return 10
    else:
        return np.nan

'''Создание темы для отрисовки графиков'''

solar_theme = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor='#002b36',
        plot_bgcolor='#073642',
        font=dict(color='#839496'),
        title=dict(font=dict(size=24, color='#93a1a1')),
        xaxis=dict(
            gridcolor='#586e75',
            zerolinecolor='#586e75',
            linecolor='#586e75',
            tickfont=dict(color='#839496')
        ),
        yaxis=dict(
            gridcolor='#586e75',
            zerolinecolor='#586e75',
            linecolor='#586e75',
            tickfont=dict(color='#839496')
        ),
        legend=dict(
            font=dict(size=12, color='#93a1a1'),
            bgcolor='#073642',
            bordercolor='#586e75'
        ),
        colorway=['#268bd2', '#2aa198', '#859900', '#b58900', '#cb4b16', '#dc322f',
                  '#6c71c4', '#d33682', '#4e9a06', '#c4a000', '#ce5c00']
    )
)

# Добавление темы в список доступных тем
pio.templates['solar_theme'] = solar_theme

# Установка темы по умолчанию
pio.templates.default = 'solar_theme'

# Установка темы и инициализация приложения
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.SOLAR])
# Получение данных
data = get_data_frame()

'''Инициализация и настройка фильтров'''

years_selector = dcc.RangeSlider(
    id='range-slider',
    min=min(data['Year_of_Release']),
    max=max(data['Year_of_Release']),
    marks={'2000': '2000', '2005': '2005', '2010': '2010',
           '2015': '2015'},
    step=1,
    value=[2000, 2016]
)

platforms = data['Platform'].unique()
platform_options = []
for k in platforms:
    platform_options.append({'label': k, 'value': k})
    
platform_selector = dcc.Dropdown(
    id='platform_dropdown',
    options=platform_options,
    value=platforms,
    multi=True,
    style={'backgroundColor': 'transparent'}
)

genres = data['Genre'].unique()
genre_options = []
for k in genres:
    genre_options.append({'label': k, 'value': k})

genre_selector = dcc.Dropdown(
    id='genre_dropdown',
    options=genre_options,
    value=genres,
    multi=True,
    style={'backgroundColor': 'transparent'}
)

'''Инициализация и настройка основного слоя приложения'''

app.layout = html.Div([
    dbc.Row(
        dbc.Col(html.H1('Анализ данных игровой индустрии'),
                width={'offset': 3})
    ),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.P('Фильтр по годам'),
            html.Div(years_selector,
                     style={'backgroundColor': 'transparent'})
        ], width={'size': 3, 'offset': 1}),
        dbc.Col([
            html.P('Фильтр платформ'),
            html.Div(platform_selector,
                     style={'backgroundColor': 'transparent'})
        ], width={'size': 4}),
        dbc.Col([
            html.P('Фильтр жанров'),
            html.Div(genre_selector,
                     style={'backgroundColor': 'transparent'})
        ], width={'size': 4})
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='stacked_area_chart'),
            ])
        ], width={'size': 8}),
        dbc.Col([
            html.Div(id='table',
                        style={'backgroundColor': 'transparent'})
        ], width={'size': 4})
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='chart_scatter')
        ], width={'size': 6}),
        dbc.Col([
            dcc.Graph(id='bar_chart')
        ], width={'size': 6})
    ])
], style={'margin-right': '30px',
          'margin-left': '30px'})

'''Обработка отфильрованных данных и изменение графиков/таблиц'''

@app.callback(
    [Output('chart_scatter', 'figure'),
     Output('bar_chart', 'figure'),
     Output('stacked_area_chart', 'figure'),
     Output('table', 'children')],
    [Input(component_id='range-slider', component_property='value'),
     Input(component_id='platform_dropdown', component_property='value'),
     Input(component_id='genre_dropdown', component_property='value')]
)
def update_chart(year_range, selected_platforms, selected_genres):
    chart_data = data[(data['Year_of_Release'] >= year_range[0]) &
                      (data['Year_of_Release'] <= year_range[1]) &
                      (data['Platform'].isin(selected_platforms)) &
                      (data['Genre'].isin(selected_genres))]
    fig_scatter = px.scatter(chart_data.sort_values('User_Score'), 'User_Score', 'Critic_Score', 'Genre',
                             title='Рейтинг игроков / Рейтинг критиков',
                             labels={'User_Score': 'Рейтинг игроков', 'Critic_Score': 'Рейтинг критиков'}
                             )

    chart_data['Numeric_Rating'] = chart_data['Rating'].apply(numeric_func)
    temp_df = pd.concat([chart_data['Genre'], chart_data['Rating'].apply(numeric_func)], axis=1)
    mean_rating_genres = temp_df.groupby('Genre')['Rating'].agg(['mean']).reset_index()
    fig_bar = px.bar(mean_rating_genres, 'Genre', 'mean',
           title='Средний возрастной рейтинг по жанрам',
           labels={'Genre': 'Жанр', 'mean': 'Средний Рейтинг'})

    df_pivot = chart_data.pivot_table(index='Year_of_Release',
                                      columns='Platform',
                                      aggfunc='size',
                                      fill_value=0).reset_index()
    fig_stacked_area = px.area(df_pivot, x='Year_of_Release',
                               y=df_pivot.columns[1:],
                               title='Выпуск игр по годам и платформам',
                               labels={'value': 'Количество', 'Year_of_Release': 'Год'}
                               )

    amount_games = get_amount_games(chart_data)
    mean_user_score = get_mean_user_score(chart_data)
    mean_critic_score = get_mean_critic_score(chart_data)

    table_df = pd.DataFrame({'Параметр': ['Количество игр','Средняя оценка игроков', 'Средняя оценка критиков'],
                            'Значение': [amount_games, mean_user_score, mean_critic_score]})

    table = dash_table.DataTable(data=table_df.to_dict('records'),
                                 columns=[{'name': i, 'id': i} for i in table_df.columns],
                                 style_cell={
                                     'padding': '10px',
                                     'textAlign': 'center',
                                     'backgroundColor': 'transparent'
                                 },
                            )

    return fig_scatter, fig_bar, fig_stacked_area, table

# Запускаем приложение
if __name__ == '__main__':
    app.run_server(debug=True)
