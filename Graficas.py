import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

# Cargar datos
df = pd.read_csv("Balaji Fast Food Sales.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date']).sort_values(by='date').reset_index(drop=True)

# Inicializar app
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server
app.title = "Dashboard de Ventas"

# Layout
app.layout = dbc.Container([
    html.H3('Dashboard de Ventas - Balaji Fast Food', className="text-center text-primary mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Rango de Tiempo"),
            dcc.RadioItems(
                id='range-selector',
                options=[
                    {'label': 'Último mes', 'value': 'month'},
                    {'label': 'Último semestre', 'value': 'sem'},
                    {'label': 'Último año', 'value': 'year'},
                ],
                value='year',
                inline=True,
                className="mb-3"
            )
        ], width=6),

        dbc.Col([
            html.Label("Tipo de gráfico adicional"),
            dcc.Dropdown(
                id='scatter-type',
                options=[
                    {'label': 'Box Plot', 'value': 'box'},
                    {'label': 'Barras por Producto', 'value': 'bar'},
                ],
                value='bar',
                clearable=False
            )
        ], width=6)
    ]),

    html.Br(),

    dcc.RangeSlider(
        id='range-slider',
        min=0,
        max=len(df) - 1,
        value=[0, len(df) - 1],
        marks={i: df['date'].dt.strftime('%Y-%m')[i] for i in range(0, len(df), max(1, len(df)//10))},
        step=1,
        tooltip={"placement": "bottom", "always_visible": False}
    ),

    html.Br(),

    dbc.Button("Cambiar orientación de gráfico de barras", id="toggle-bar", color="primary", className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart'), width=6),
        dbc.Col(dcc.Graph(id='bar-chart'), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-chart'), width=6),
        dbc.Col(dcc.Graph(id='pie-chart'), width=6),
    ])
], fluid=True)

# Callback
@app.callback(
    Output('line-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('scatter-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Input('range-slider', 'value'),
    Input('range-selector', 'value'),
    Input('scatter-type', 'value'),
    Input('toggle-bar', 'n_clicks'),
    State('bar-chart', 'figure')
)
def update_graphs(slider_range, range_type, scatter_type, n_clicks, bar_fig_state):
    df_filtered = df.iloc[slider_range[0]:slider_range[1] + 1]

    if range_type == 'month':
        df_filtered = df_filtered[df_filtered['date'] > df['date'].max() - pd.DateOffset(months=1)]
    elif range_type == 'sem':
        df_filtered = df_filtered[df_filtered['date'] > df['date'].max() - pd.DateOffset(months=6)]
    elif range_type == 'year':
        df_filtered = df_filtered[df_filtered['date'] > df['date'].max() - pd.DateOffset(years=1)]

    # Gráfico de línea
    line_fig = px.line(df_filtered, x='date', y='transaction_amount', title='Ventas Totales en el Tiempo')

    # Gráfico de barras principal con orientación
    orientation = 'v'
    if n_clicks and n_clicks % 2 == 1:
        orientation = 'h'

    bar_df = df_filtered.groupby('item_type')['transaction_amount'].sum().reset_index()
    if orientation == 'v':
        bar_fig = px.bar(bar_df, x='item_type', y='transaction_amount', title='Ventas por Tipo de Producto (Vertical)')
    else:
        bar_fig = px.bar(bar_df, y='item_type', x='transaction_amount', orientation='h',
                         title='Ventas por Tipo de Producto (Horizontal)')

    # Gráfico adicional (antes era scatter, ahora es dinámico)
    if scatter_type == 'box':
        scatter_fig = px.box(df_filtered, x='item_type', y='item_price',
                             title='Distribución de Precios por Tipo')
    else:  # 'bar'
        product_df = df_filtered.groupby('item_name')['quantity'].sum().reset_index()
        scatter_fig = px.bar(product_df, x='item_name', y='quantity', title='Cantidad Vendida por Producto')

    # Pie chart
    pie_df = df_filtered.groupby('item_name')['transaction_amount'].sum().reset_index()
    pie_fig = px.pie(pie_df, names='item_name', values='transaction_amount', title='Proporción de Ventas por Producto')

    return line_fig, bar_fig, scatter_fig, pie_fig

if __name__ == '__main__':
    app.run(debug=True)
