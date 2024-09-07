# Import packages
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from urllib.parse import parse_qs, urlparse
import locale

# Local import
from data import report

# Set locale to Spanish
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # For Linux/Mac

# Load JSON data
json_data_all = report.consumptions.json()
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
        
      
    ], className="box"),

    html.Div([
        html.Div([
            # Donut chart for tipoCreacion
            dcc.Graph(id='tipo-proceso-donut', style={'height': '350px'}),
        ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),

        html.Div([
            # Donut chart for tipoCreacion
            dcc.Graph(id='tipo-creacion-donut', style={'height': '350px'}),
        ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),
        
        html.Div([
            # Chart for Auth Method
            dcc.Graph(id='auth-methods', style={'height': '350px'}),
            dcc.Location(id='url', refresh=False)  # Location component to get the URL
        ], style={'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),
        
        
    ], className="box"),

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
                x=0.1, 
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
                x=0.1, 
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


# Callback to update the auth methods graph
@callback(
    Output('auth-methods', 'figure'),
    Input('url', 'href')  # Use 'href' to get the full URL including query params
)
def update_auth_methods(href):
    # Step 1: Parse the 'href' to extract query parameters
    if href:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        nit = query_params.get('nit', [None])[0]  # Get 'nit' from query parameters

        if nit:
            # Step 2: Filter data for a specific nit
            filtered_data = next((item for item in json_data_all if item['nit'] == nit), None)

            # Step 3: Initialize the counts for each authentication method
            auth_methods = {
                1: "Llamada",
                2: "SMS",
                3: "Email",
                4: "WhatsApp"
            }

            # Initialize counts for each authentication method with 0
            auth_method_consumption = {name: 0 for name in auth_methods.values()}

            # Step 3: Count occurrences of each authentication method
            if filtered_data:
                for entry in filtered_data['consumption']['firmaSeguroMethod']:
                    auth_method_name = auth_methods.get(entry['authenticationMethodId'])
                    if auth_method_name:
                        auth_method_consumption[auth_method_name] += entry['amountConsumed']

            # Step 4: Prepare data for the bar chart
            x = list(auth_method_consumption.keys())  # ['Llamada', 'SMS', 'Email', 'WhatsApp']
            y = list(auth_method_consumption.values())  # Summed 'amountConsumed' values

            # Step 5: Create the bar graph using Plotly
            fig = px.bar(
                x=x,
                y=y,
                labels={'x': 'Método', 'y': 'Total'},
                title=f'Firmas por tipo de Autenticación',
                color=x,
                text=y
            )

            # Update the layout to position the text on top of each bar
            fig.update_traces(textposition='outside')   

            return fig

        # Return an empty figure if no nit is provided or found
        return px.bar(
            x=['Llamada', 'SMS', 'Email', 'WhatsApp'],
            y=[0, 0, 0, 0],
            labels={'x': 'Authentication Method', 'y': 'Count'},
            title='No Data Available'
        )

