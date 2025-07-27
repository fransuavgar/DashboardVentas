"""
Archivo: app_dashboard.py
Descripción: Dashboard interactivo con Dash, filtros por fecha y pestañas visuales.
"""

import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# 📥 Cargar datos limpios
try:
    df = pd.read_csv("C:\\Users\\FranciscoSuavitaGarc\\Documents\\INCCATERCERCUATRIMESTRE\\P6-AnalisisyVerificaciondeAlgoritmos\\Semana12\\TrabajoEntrega\\ProyectoVentas\\Datos_Ventas_Tienda_Limpio.csv")
    df = df.rename(columns={'Total Venta': 'Total_Venta'})  # Renombrar para consistencia
    df = df.loc[:, ~df.columns.duplicated()]  # Eliminar columnas duplicadas
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Mes'] = df['Fecha'].dt.month
    print("✅ Archivo limpio cargado correctamente.")
except FileNotFoundError:
    print("❌ Archivo limpio no encontrado. Asegúrate de ejecutar limpieza_datos.py primero.")
    exit()

# ⚠️ Verificar columna 'Categoria'
has_categoria = 'Categoria' in df.columns
categorias = df['Categoria'].unique() if has_categoria else []

# 🎛️ Crear la app
app = dash.Dash(__name__)
app.title = "📊 Dashboard de Ventas"
server = app.server

min_fecha = df['Fecha'].min()
max_fecha = df['Fecha'].max()

# 📋 Diseño del dashboard
app.layout = html.Div([
    html.H1("📊 Dashboard Interactivo de Ventas", style={'textAlign': 'center', 'color': '#003366'}),

    html.Div([
        html.Label("📅 Selecciona un rango de fechas:"),
        dcc.DatePickerRange(
            id='filtro-fechas',
            start_date=min_fecha,
            end_date=max_fecha,
            min_date_allowed=min_fecha,
            max_date_allowed=max_fecha
        ),
        html.Br(), html.Br(),
        html.Label("🗂️ Selecciona categoría (opcional):"),
        dcc.Dropdown(
            id='filtro-categoria',
            options=[{'label': cat, 'value': cat} for cat in categorias] if has_categoria else [],
            value=categorias[0] if has_categoria else None,
            placeholder="(No hay categorías disponibles)" if not has_categoria else "Selecciona una categoría",
            disabled=not has_categoria
        )
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px', 'verticalAlign': 'top'}),

    html.Div([
        dcc.Tabs(id='tabs-dashboard', value='tab-general', children=[
            dcc.Tab(label='📈 Visión General', value='tab-general'),
            dcc.Tab(label='🏆 Top Productos', value='tab-top'),
            dcc.Tab(label='📉 Tendencias', value='tab-tendencias'),
            dcc.Tab(label='🎓 Créditos', value='tab-creditos'),
        ]),
        html.Div(id='contenido-pestanas', style={'padding': '20px'})
    ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top'})
])

# 🔁 Lógica de actualización del contenido
@app.callback(
    Output('contenido-pestanas', 'children'),
    Input('tabs-dashboard', 'value'),
    Input('filtro-fechas', 'start_date'),
    Input('filtro-fechas', 'end_date'),
    Input('filtro-categoria', 'value')
)
def actualizar_contenido(pestana, fecha_inicio, fecha_fin, categoria):
    try:
        df_filtrado = df[(df['Fecha'] >= fecha_inicio) & (df['Fecha'] <= fecha_fin)]

        if has_categoria and categoria:
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria]

        if df_filtrado.empty:
            return html.Div("⚠️ No hay datos para mostrar con los filtros seleccionados.", style={"color": "red"})

        if pestana == 'tab-general':
            if 'Mes' in df_filtrado.columns and 'Total_Venta' in df_filtrado.columns:
                ventas_mes = df_filtrado.groupby('Mes')['Total_Venta'].sum().reset_index()
                fig = px.bar(ventas_mes, x='Mes', y='Total_Venta', title='📆 Ventas Totales por Mes')
                return dcc.Graph(figure=fig)

        elif pestana == 'tab-top':
            if 'Producto' in df_filtrado.columns and 'Cantidad' in df_filtrado.columns:
                top10 = df_filtrado.groupby('Producto')['Cantidad'].sum().sort_values(ascending=False).head(10).reset_index()
                fig = px.bar(top10, x='Producto', y='Cantidad', title='🏆 Top 10 Productos Más Vendidos')
                return dcc.Graph(figure=fig)

        elif pestana == 'tab-tendencias':
            if 'Fecha' in df_filtrado.columns and 'Total_Venta' in df_filtrado.columns:
                tendencia = df_filtrado.groupby('Fecha')['Total_Venta'].sum().reset_index()
                fig = px.line(tendencia, x='Fecha', y='Total_Venta', title='📈 Tendencia de Ventas en el Tiempo')
                return dcc.Graph(figure=fig)

        elif pestana == 'tab-creditos':
            return html.Div([
                html.H3("🎓 Créditos del Proyecto TOP VENTAS", style={"textAlign": "center"}),
                html.H4("Universidad INCCA de Colombia", style={"textAlign": "center"}),
                html.P("Análisis y Verificación de Algoritmos", style={"textAlign": "center"}),
                html.P("Docente LEIDY J. CIFUENTES S.", style={"textAlign": "center"}),
                html.Br(),
                html.Ul([
                    html.Li("FRANCISCO SUAVITA GARCIA"),
                    html.Li("MAURICIO ANDRES MORENO QUIÑONES"),
                    html.Li("EBER EVELIO RINCON RIVAS"),
                    html.Li("JAVIER MAURICIO CASTRO"),
                    html.Li("MOSIAH PARGAS"),
                    html.Li("JOHAN ANDREY CAMPOS TAVERA"),
                ], style={"fontSize": "18px", "marginLeft": "20%"}),
                html.Br(),
                html.P("© 2025 - Todos los derechos reservados", style={"textAlign": "center", "color": "gray"})
            ])

        return html.Div("⚠️ No se pudo generar la visualización. Verifica tus datos.")

    except Exception as e:
        return html.Div(f"❌ Error interno: {str(e)}", style={"color": "red"})

# 🚀 Ejecutar servidor local
if __name__ == '__main__':
    app.run(debug=True)
