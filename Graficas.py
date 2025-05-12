import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Cargar datos
df = pd.read_csv("Balaji Fast Food Sales.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date']).sort_values(by='date').reset_index(drop=True)

# Inicializar app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server
app.title = "Dashboard de Ventas"

# Layout
app.layout = dbc.Container([
    html.H1('Dashboard de Ventas - Balaji Fast Food', className="text-center text-primary mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([

                    dbc.Button("Cambiar orientación", id="toggle-bar", color="primary", className="mb-2"),
                    dcc.Graph(id='bar-chart')
                ])
            ), width=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Dropdown(
                        id='scatter-type',
                        options=[
                            {'label': 'Box Plot', 'value': 'box'},
                            {'label': 'Barras por Producto', 'value': 'bar'},
                        ],
                        value='bar',
                        clearable=False,
                        className="mb-2"
                    ),
                    dcc.Graph(id='scatter-chart')
                ])
            ), width=6
        ),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id='line-chart')
                ])
            ), width=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id='pie-chart')
                ])
            ), width=6
        ),
    ])
], fluid=True)

# Callback
@app.callback(
    Output('line-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('scatter-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Input('scatter-type', 'value'),
    Input('toggle-bar', 'n_clicks'),
)
def update_graphs(scatter_type, n_clicks_bar):
    df_filtered = df  # Ya no se filtra por rango de fechas

    # Gráfico de línea
    line_fig = px.line(df_filtered, x='date', y='transaction_amount', title='Ventas Totales en el Tiempo')
    line_fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="Todo")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    # Gráfico de barras principal con orientación
    orientation = 'v'
    if n_clicks_bar and n_clicks_bar % 2 == 1:
        orientation = 'h'

    bar_df = df_filtered.groupby('item_type')['transaction_amount'].sum().reset_index()
    if orientation == 'v':
        bar_fig = px.bar(bar_df, x='item_type', y='transaction_amount', title='Ventas por Tipo de Producto (Vertical)')
    else:
        bar_fig = px.bar(bar_df, y='item_type', x='transaction_amount', orientation='h',
                         title='Ventas por Tipo de Producto (Horizontal)')

    # Gráfico adicional
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
