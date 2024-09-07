# Import packages
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import locale

# Local import
from data import report

# Set locale to Spanish
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # For Linux/Mac

# Load JSON data
json_data = report.consumptions_by_nit.json()

# Prepare data for visualization
data = []
for entry in json_data:
    process_status = entry["processStatus"]
    consumption = entry["consumption"]
    
    # Extract 'tipoCreacion' as is
    consolidados = consumption.get('consolidados', {})
    
    # Extract 'tipoCreacion' as is
    tipo_creacion = consumption.get('tipoCreacion', {})
    
    # Extract 'tipoProceso' as is
    tipo_proceso = consumption.get('tipoProceso', {})
    
    # Extract 'tipoAutenticacion' as is
    tipo_autenticacion = consumption.get('tipoAutenticacion', {})

    # If 'tipoCreacion' is a dictionary, append it to the data
    if isinstance(tipo_creacion, dict):
        data.append({
            "processStatus": process_status,
            "consolidados": consolidados,  # Store it as a dictionary
            "totalConsolidado": sum(consumption.get('consolidados', {}).values()),
            "tipoCreacion": tipo_creacion,  # Store it as a dictionary
            "tipoProceso": tipo_proceso,  # Store it as a dictionary
            "tipoAutenticacion": tipo_autenticacion,  # Store it as a dictionary
        })

# Convert the data into a pandas DataFrame
df = pd.DataFrame(data)

print(df.head())

# Register page
dash.register_page(__name__)

# Layout
layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='status-dropdown',
                options=[{'label': status, 'value': status} for status in df['processStatus'].unique()],
                value=df['processStatus'].unique()[0],  # Default value
                clearable=False,
            ),
        ], style={'display': 'inline-block', 'width': '20%'}),
    ], style={'display':'flex', 'justify-content':'flex-end', 'margin-top': '20px', 'margin-bottom': '20px'}),

    html.Div([
        # Main graph for consolidado by month
        html.Div([
            dcc.Graph(id='consolidados', style={'height': '350px'}),
        ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),  
        
        # Main graph for consolidado by process status
        html.Div([
            dcc.Graph(id='consolidado-graph', style={'height': '350px'}),
        ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),  
        
      
    ], style={'display':'flex', 'column-gap': '20px', 'margin-bottom': '20px'}),

    html.Div([
        html.Div([
            # Donut chart for tipoCreacion
            dcc.Graph(id='tipo-proceso-donut', style={'height': '350px'}),
        ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),

        html.Div([
            # Donut chart for tipoCreacion
            dcc.Graph(id='tipo-creacion-donut', style={'height': '350px'}),
        ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),
        
        # html.Div([
        #     # Donut chart for tipoAutenticacion
        #     dcc.Graph(id='tipo-autenticacion', style={'height': '350px'}),
        # ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),

    ], style={'display':'flex', 'column-gap': '20px'}),

    # Dummy component to use as an Input trigger for the callback
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Trigger once immediately (1 second after page load)
        n_intervals=0  # Start at zero intervals
    )
])

# Callback to update the consolidado graph
@callback(
    Output('consolidado-graph', 'figure'),
    Input('interval-component', 'n_intervals')  # Dummy input
)
def update_consolidado_graph(n_intervals):
    # Bar chart showing consolidado by process status with numbers on top of each bar
    fig = px.bar(
        df,
        y='processStatus',
        x='totalConsolidado',
        orientation='h',
        title='Procesos por estado',
        labels={'processStatus': 'Estado', 'totalConsolidado': 'Total Consolidado'},
        color='processStatus',
        text='totalConsolidado'  # Display the total consolidado value on top of each bar
    )

    # Update the layout to position the text on top of each bar
    fig.update_traces(textposition='outside')
    
    return fig

# Callback to update the tipoCreacion donut chart based on selected process status
@callback(
    Output('tipo-creacion-donut', 'figure'),
    Input('status-dropdown', 'value')  # Input from the status dropdown
)
def update_tipo_creacion_donut(selected_status):
    # Filter the data based on the selected process status
    filtered_df = df[df['processStatus'] == selected_status]

    # Debugging: Print the filtered DataFrame
    print(f"Filtered DataFrame for status '{selected_status}':\n{filtered_df}")

    # Check if there's any data available
    if filtered_df.empty:
        # If no data available, return an empty figure with a message
        fig = px.pie(
            names=['No Data Available'],
            values=[1],
            title=f'Tipo Creacion for Status: {selected_status}',
            hole=0.4
        )
    else:
        # Extract the tipoCreacion dictionary
        tipo_creacion_dict = filtered_df.iloc[0]['tipoCreacion']
        
        # Convert the dictionary to a DataFrame
        donut_df = pd.DataFrame(list(tipo_creacion_dict.items()), columns=['Tipo Creacion', 'Count'])
        
        # Create the donut chart
        fig = px.pie(
            donut_df,
            names='Tipo Creacion',
            values='Count',
            title=f'Procesos por tipo de creación',
            hole=0.4  # Create a donut chart
        )

        if donut_df['Count'].sum() == 0:
            fig.add_annotation(
                text=f"No hay resultados para {selected_status}",
                font=dict(
                    family="Arial, sans-serif",
                    size=18,
                    color="#000"
                ),
                align="center",
                xref="paper", 
                yref="paper",
                x=0.3, 
                y=0.5, 
                showarrow=False
            )
        
    return fig

# Callback to update the tipoCreacion donut chart based on selected process status
@callback(
    Output('tipo-proceso-donut', 'figure'),
    Input('status-dropdown', 'value')  # Input from the status dropdown
)
def update_tipo_proceso_donut(selected_status):
    # Filter the data based on the selected process status
    filtered_df = df[df['processStatus'] == selected_status]

    # Check if there's any data available
    if filtered_df.empty:
        # If no data available, return an empty figure with a message
        fig = px.pie(
            names=['No Data Available'],
            values=[1],
            title=f'Tipo Creacion for Status: {selected_status}',
            hole=0.4
        )
    else:
        # Extract the tipoCreacion dictionary
        tipo_proceso_dict = filtered_df.iloc[0]['tipoProceso']
        
        # Convert the dictionary to a DataFrame
        donut_df = pd.DataFrame(list(tipo_proceso_dict.items()), columns=['Tipo Proceso', 'Count'])
        
        # Create the donut chart
        fig = px.pie(
            donut_df,
            names='Tipo Proceso',
            values='Count',
            title=f'Procesos por tipo de proceso',
            hole=0.4  # Create a donut chart
        )

        if donut_df['Count'].sum() == 0:
            fig.add_annotation(
                text=f"No hay resultados para {selected_status}",
                font=dict(
                    family="Arial, sans-serif",
                    size=18,
                    color="#000"
                ),
                align="center",
                xref="paper", 
                yref="paper",
                x=0.3, 
                y=0.5, 
                showarrow=False
            )
        
    return fig

# Callback to update the consolidado graph
# @callback(
#     Output('tipo-autenticacion', 'figure'),
#     Input('status-dropdown', 'value')
# )
# def update_tipo_autenticacion(selected_status):
#     # Filter the data based on the selected process status
#     filtered_df = df[df['processStatus'] == selected_status]

#     # Check if there's any data available
#     if filtered_df.empty:
#         # If no data available, return an empty figure with a message
#         fig = px.pie(
#             names=['No Data Available'],
#             values=[1],
#             title=f'Tipo Creacion for Status: {selected_status}',
#             hole=0.4
#         )
#     else:
#         # Extract the tipoCreacion dictionary
#         tipo_autenticacion_dict = filtered_df.iloc[0]['tipoAutenticacion']

#         # Convert the dictionary to a DataFrame
#         aut_df = pd.DataFrame(list(tipo_autenticacion_dict.items()), columns=['TipoAutenticacion', 'Count'])
#         print("aut ", aut_df)

#         # Bar chart showing consolidado by process status with numbers on top of each bar
#         fig = px.bar(
#             aut_df,
#             x='TipoAutenticacion',
#             y='Count',
#             title='Procesos por estado',
#             # labels={'processStatus': 'Estado', 'totalConsolidado': 'Total Consolidado'},
#             # color='processStatus',
#             # text='totalConsolidado'  # Display the total consolidado value on top of each bar
#         )

#     # Update the layout to position the text on top of each bar
#     fig.update_traces(textposition='outside')
    
#     return fig

# Callback to update the consolidados graph
@callback(
    Output('consolidados', 'figure'),
    Input('status-dropdown', 'value')
)
def update_consolidados(selected_status):
    # Filter the data based on the selected process status
    filtered_df = df[df['processStatus'] == selected_status]

    # Extract the tipoCreacion dictionary
    consolidados_dict = filtered_df.iloc[0]['consolidados']

    # consolidados_df = pd.DataFrame(dict(
    #     date=list(consolidados_dict.keys()),
    #     value=list(consolidados_dict.values())
    # ))

    # Convert the dictionary to a DataFrame
    consolidados_df = pd.DataFrame(list(consolidados_dict.items()), columns=['Month', 'Count'])
    
    # Convert 'date' column to a datetime format
    consolidados_df['Month'] = pd.to_datetime(consolidados_df['Month'] + '01', format='%Y%m%d')

    # Format 'date' to show month name
    consolidados_df['Month'] = consolidados_df['Month'].dt.strftime('%B')

    print(consolidados_df)

    # Bar chart showing consolidado by process status with numbers on top of each bar
    # fig = px.bar(
    #     consolidados_df,
    #     x='Month',
    #     y='Count',
    #     title='Procesos por mes',
    #     text='Count'  # Display the total consolidado value on top of each bar
    # )

    # # Update the layout to position the text on top of each bar
    # fig.update_traces(textposition='outside')

    fig = px.line(
        consolidados_df, 
        x="Month", 
        y="Count",
        title='Procesos por mes',
        labels={'Month': 'Mes', 'Count': 'Total mes'},
        text='Count'
    )

    # Add text labels on the line chart
    fig.update_traces(textposition="top center")
    
    return fig


