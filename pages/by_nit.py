# Import packages
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from urllib.parse import parse_qs, urlparse
import locale
from datetime import datetime, timedelta
import pytz
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

url = os.getenv('DEVURL')

# Local import
from data import report

# Set locale to Spanish
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Utility function for authentication
def authenticate():
    """Authenticate and return a token."""
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    auth_url = f"{url}/api/v1/Auth/SignIn"
    response = requests.post(auth_url, json={"email": email, "password": password})

    if response.status_code == 200:
        try:
            return response.json().get('access_token')
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode authentication response")
    else:
        print(f"Authentication failed with status code {response.status_code}")
    return None

# Utility function for fetching data
def fetch_data(api_endpoint, headers):
    """Fetch data from an API endpoint with given headers."""
    response = requests.get(api_endpoint, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode response")
    else:
        print(f"Failed to fetch data with status code {response.status_code}")
    return None

# Function to build data from API response
def build_data_from_api(json_data):
    """Convert JSON response to DataFrame."""

    data = []
    for entry in json_data:
        process_status = entry["processStatus"]
        consumption = entry["consumption"]

        # Extract fields as is
        tipo_creacion = consumption.get('tipoCreacion', {})
        
        # Append data if valid
        if isinstance(tipo_creacion, dict):
            data.append({
                "processStatus": process_status,
                "totalConsolidado": sum(consumption.get('consolidados', {}).values()),
                "tipoCreacion": tipo_creacion,
                "tipoProceso": consumption.get('tipoProceso', {}),
                "tipoAutenticacion": consumption.get('tipoAutenticacion', {}),
                "consolidados": consumption.get('consolidados', {})
            })

    return pd.DataFrame(data)

def get_total_processes(json_data):
    total_processes = 0

    for entry in json_data:
        process_status = entry["processStatus"]
        
        # Increment the count if the status is not 'Borrador'
        if process_status != 'Borrador':
            tipo_creacion = entry['consumption'].get('tipoCreacion', {})
            total_processes += tipo_creacion.get('BackOffice', 0) + tipo_creacion.get('API', 0)

    return total_processes

def get_total_processes_signed(json_data):
    total_processes = 0

    for entry in json_data:
        process_status = entry["processStatus"]
        
        # Increment the count if the status is not 'Borrador'
        if process_status == 'Exitoso':
            tipo_creacion = entry['consumption'].get('tipoCreacion', {})
            total_processes += tipo_creacion.get('BackOffice', 0) + tipo_creacion.get('API', 0)

    return total_processes

def get_total_signatures(json_data):
    # Initialize a dictionary to hold the sums
    tipo_autenticacion_sum = {'Llamada': 0, 'SMS': 0, 'Email': 0, 'WhatsApp': 0}
    total_sum = 0  # Variable to hold the total sum of all methods

    data = []
    for entry in json_data:
        process_status = entry["processStatus"]
        consumption = entry["consumption"]

        if process_status != 'Borrador':
            # Sum the tipoAutenticacion counts
            for method, count in consumption['tipoAutenticacion'].items():
                tipo_autenticacion_sum[method] += count
                total_sum += count  # Add to total sum

        # Extract fields as is
        tipo_creacion = consumption.get('tipoCreacion', {})
        
    print(tipo_autenticacion_sum)
    print("Total sum of all tipoAutenticacion:", total_sum)

    return total_sum

# Define the Bogotá time zone
bogota_tz = pytz.timezone('America/Bogota')

# Set date range
current_date = datetime.now(bogota_tz).date()
initial_start_date = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
initial_end_date = current_date.strftime('%Y-%m-%d')


# Register page
dash.register_page(__name__)

# Layout
layout = html.Div([
    html.Div([
        html.H1('Mis consumos', style={'color': '#173179', 'text-transform': 'uppercase', 'text-align': 'left', 'margin': '0', 'font-size': '22px', 'flex-grow': '1'}),
        html.Div([
            html.Div(id='total_signatures', style={'display': 'inline-block', 'width': '150px', 'padding': '10px', 'margin-bottom': '20px', 'color': '#fff', 'background': '#72d06a', 'text-align': 'center'}),
            html.Div(id='total_processes', style={'display': 'inline-block', 'width': '150px', 'padding': '10px', 'margin-bottom': '20px', 'color': '#fff', 'background': '#2b5e7f', 'text-align': 'center'}),
            html.Div(id='total_processes_signed', style={'display': 'inline-block', 'width': '250px', 'padding': '10px', 'margin-bottom': '20px', 'color': '#fff', 'background': '#f7c042', 'text-align': 'center'}),
        ], style={'display': 'flex', 'column-gap': '20px'}),
    ], style={'display':'flex', 'justify-content':'flex-end', 'column-gap':'20px', 'margin-top': '20px', 'margin-bottom': '20px'}),
    
    html.Div([
        html.Div([
            html.Span('Usuario', className='filter_label'),
            dcc.Dropdown(
                id='users-dropdown',
                value=0,  # Default value
                clearable=True,
                placeholder='Seleccionar usuario',
                className='hidden-dropdown',
                style={'height': '42px'},
            ),
        ], style={'display': 'flex', 'width': '25%', 'flex-direction': 'column'}),
        html.Div([
            html.Span('Estado', className='filter_label'),
            dcc.Dropdown(
                id='status-dropdown',
                clearable=False,
                style={'height': '42px', 'width': '100%'}
            ),
        ], style={'display': 'flex', 'width': '20%', 'flex-direction': 'column'}),
        html.Div([
            html.Span('Fecha', className='filter_label'),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=initial_start_date, 
                end_date=initial_end_date, 
                max_date_allowed=current_date,    
                display_format='YYYY-MM-DD',
            ),
        ], style={'display': 'flex', 'height': '30px', 'flex-direction': 'column'}),
    ], style={'display':'flex', 'justify-content':'flex-end', 'column-gap':'20px', 'margin-top': '20px', 'margin-bottom': '20px'}),

    html.Div([
        html.Div([
            dcc.Loading(
                id="loading-1",
                type="dot",
                overlay_style={"visibility":"visible", "filter": "blur(3px)"},
                children=dcc.Graph(id='consolidados', style={'height': '350px'}), 
            )
        ], style={'background': '#fff', 'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),
       
        html.Div([
            dcc.Loading(
                id="loading-1",
                type="dot",
                overlay_style={"visibility":"visible", "filter": "blur(3px)"},
                children=dcc.Graph(id='consolidado-graph', style={'height': '350px'}),
            )
        ], style={'background': '#fff', 'display': 'inline-block', 'width': '49%', 'border':'1px solid #ccc'}),
      
    ], className="box"),

    html.Div([
        html.Div([
            dcc.Loading(
                id="loading-1",
                type="dot",
                overlay_style={"visibility":"visible", "filter": "blur(3px)"},
                children=dcc.Graph(id='tipo-proceso-donut', style={'height': '350px'}),
            )
        ], style={'background': '#fff', 'display': 'inline-block', 'width': '33%', 'border':'1px solid #ccc'}),

        html.Div([
            dcc.Loading(
                id="loading-1",
                type="dot",
                overlay_style={"visibility":"visible", "filter": "blur(3px)"},
                children=dcc.Graph(id='tipo-creacion-donut', style={'height': '350px'}),
            )
        ], style={'background': '#fff', 'display': 'inline-block', 'width': '33%', 'border':'1px solid #ccc'}),
        
        html.Div([
            dcc.Loading(
                id="loading-1",
                type="dot",
                overlay_style={"visibility":"visible", "filter": "blur(3px)"},
                children=dcc.Graph(id='auth-methods', style={'height': '350px'})
            ),
            dcc.Location(id='url', refresh=False)  # Location component to get the URL
        ], style={'background': '#fff', 'display': 'inline-block', 'width': '33%', 'border':'1px solid #ccc'}),
        
    ], className="box"),

    # Dummy component to use as an Input trigger for the callback
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Trigger once immediately (1 second after page load)
        n_intervals=0  # Start at zero intervals
    )
])

# Generic callback for fetching data and updating visualizations
def create_figure_from_data(df, selected_status, metric):
    # Filter data and create figure based on chart type
    if metric == 'auth_method':
        filtered_df = df[df['processStatus'] == selected_status]
        # Extract the tipoCreacion dictionary
        tipo_auth_dict = filtered_df.iloc[0]['tipoAutenticacion']
        
        # Convert the dictionary to a DataFrame
        auth_df = pd.DataFrame(list(tipo_auth_dict.items()), columns=['Tipo Autenticacion', 'Count'])

        fig = px.bar(
            auth_df,
            x='Tipo Autenticacion',
            y='Count',
            labels={'x': 'Método', 'Count': 'Total'},
            title=f'Firmas por tipo de Autenticación',
            color='Tipo Autenticacion',
            text='Count',
        )

        # Update the layout to position the text on top of each bar
        fig.update_traces(textposition='inside')   

        return fig
    elif metric == 'creation_type':
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
    elif metric == 'process_type':
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

    elif metric == 'consolidated':
        filtered_df = df[df['processStatus'] == selected_status]

        consolidados_dict = filtered_df.iloc[0]['consolidados']
        consolidados_df = pd.DataFrame(list(consolidados_dict.items()), columns=['Month', 'Count'])
        
        # Convert 'Month' to datetime format including year
        consolidados_df['Month'] = pd.to_datetime(consolidados_df['Month'] + '01', format='%Y%m%d')

        # Format 'Month' to show month and year
        consolidados_df['Month'] = consolidados_df['Month'].dt.strftime('%B %Y')

        fig = px.line(
            consolidados_df, 
            x="Month", 
            y="Count",
            title='Procesos por mes',
            labels={'Month': 'Mes', 'Count': 'Total mes'},
            text='Count'
        )

        # Add text labels on the line chart
        fig.update_traces(textposition="middle left")
        
        return fig

    # Add more chart types as needed
    return px.bar()

@callback(
    Output('status-dropdown', 'options'),
    Output('status-dropdown', 'value'),
    Output('total_signatures', 'children'),
    Output('total_processes', 'children'),
    Output('total_processes_signed', 'children'),
    Input('url', 'search'),
    Input('users-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def initial_data(search, user_filter, start_date, end_date,):
    if search:
        # Remove the leading '?' character from the search string
        query_params = parse_qs(search[1:])
        # Extract 'nit' parameter; returns a list, so use [0] to get the value
        nit = query_params.get('nit', [None])[0]
        user = query_params.get('user', [None])[0]
    else:
        nit = None
        user = 0
    
    if user_filter and user_filter > 0:
        user = user_filter

    if start_date:
        initial_start_date = start_date

    if end_date:
        current_date = end_date
    
    if nit:
        # Prepare initial data for layout
        get_consumptions_by_nit = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit={nit}&initial_date={initial_start_date}&final_date={current_date}&&userAppId={user}'
        token = authenticate()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        consumptions_by_nit = fetch_data(get_consumptions_by_nit, headers=headers)

        logger.info(f'URL: -------{get_consumptions_by_nit}')
            
        json_data = consumptions_by_nit
        print(json_data)
        df = build_data_from_api(json_data)
        total_signatures = get_total_signatures(json_data)
        total_processes = get_total_processes(json_data)
        total_processes_signed = get_total_processes_signed(json_data)

        total_signatures_html = html.Div([
            html.Span('Total de firmas'),
            html.H3(f'{total_signatures}')
        ])
        
        total_signatures_signed_html = html.Div([
            html.Span('Total de procesos finalizados'),
            html.H3(f'{total_processes_signed}')
        ])

        total_processes_html = html.Div([
            html.Span("Total de procesos"),
            html.H3(f"{total_processes}")
        ])
        
        status_options = [{'label': status, 'value': status} for status in df['processStatus'].unique()]

        default_value=df['processStatus'].unique()[4] if not df.empty else None  # Default value
            
        return status_options, default_value, total_signatures_html, total_processes_html, total_signatures_signed_html

    return [], None


@callback(
    Output('users-dropdown', 'options'),
    Output('users-dropdown', 'className'),  # Add an output to control the dropdown's style
    Input('url', 'search')  # 'search' contains the URL parameters
)
def display_users_by_nit(search):
    # Extract the 'nit' parameter from the URL
    if search:
        # Remove the leading '?' character from the search string
        query_params = parse_qs(search[1:])
        # Extract 'nit' parameter; returns a list, so use [0] to get the value
        nit = query_params.get('nit', [None])[0]
        user = query_params.get('user', [None])[0]
    else:
        nit = None
        user = None

    if nit:
        # Construct the get_users_by_nit URL using the extracted 'nit'
        get_users_by_nit = f'{url}/api/v1/Company/GetAllUsersByNit/{nit}'

        #Authenticate
        token = authenticate()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Fetch users by 'nit' using the constructed URL
        users_by_nit_response = requests.get(get_users_by_nit, headers=headers)

        if users_by_nit_response.status_code == 200:
            users_by_nit = users_by_nit_response.json()

            if user != '0':
                dropdown_class = 'hidden-dropdown'
                dropdown_options = []
            else:
                dropdown_class = 'show-dropdown'
                # Create dropdown options from the users
                dropdown_options = [{'label': user['fullName'], 'value': user['id']} for user in users_by_nit]
            
            return dropdown_options, dropdown_class
        else:
            return f"Failed to retrieve data: {users_by_nit_response.text}"
    else:
        return "No 'nit' parameter provided in the URL."

# Callback to update the consolidado graph
@callback(
    Output('consolidado-graph', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('url', 'href'),  
    Input('status-dropdown', 'value'),
    Input('users-dropdown', 'value'),
)
def update_consolidado_graph(start_date, end_date, href, selected_status, user_filter):
    nit = ''

    if href:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        nit = query_params.get('nit', [None])[0]  # Get 'nit' from query parameters
        user = query_params.get('user', [None])[0]  # Get 'user' from query parameters
   
    # API URL with dynamic dates
    # api_url = f'{url}/api/v1/Balance/get-all-consumption?initial_date={start_date}&final_date={end_date}'
    user_id = 0
    if user and int(user) > 0:
        user_id = user
    elif user_filter and user_filter > 0:
        user_id = user_filter

    api_url = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit={nit}&userAppId={user_id}&initial_date={start_date}&final_date={end_date}'
    
    # Access environment variables
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')

    # Data for authentication
    data = {
        "email": email,
        "password": password
    }

    # A POST request to the API
    auth = f"{url}/api/v1/Auth/SignIn"
    response = requests.post(auth, json=data)

    if response.status_code != 200:
        print(f"Authentication failed with status code {response.status_code}")
        return px.bar(x=[], y=[], title="Error: Failed to authenticate")  # Return empty plot on auth failure

    try:
        res_json = response.json()
        token = res_json['access_token']
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode authentication response")
        return px.bar(x=[], y=[], title="Error: Invalid auth response")  # Return empty plot on invalid auth response

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Make API request to get data
    consumptions = requests.get(api_url, headers=headers)
    if consumptions.status_code != 200:
        print(f"Failed to fetch consumption data with status code {consumptions.status_code}")
        empty_df = pd.DataFrame({'x': [], 'y': []})
        return px.bar(empty_df, x=[], y=[], title="Error: Failed to fetch data")  # Return empty plot on data fetch failure

    try: 
        json_data = consumptions.json() # Parse JSON response
        # Convert the data into a pandas DataFrame
        data = []
        df = build_data_from_api(json_data)
        df = df[df['processStatus'] != 'TODOS']

        if (selected_status.lower() != 'todos'):
            filtered_df = df[df['processStatus'] == selected_status]
            df = filtered_df


    except requests.exceptions.JSONDecodeError:
        print("Failed to decode consumption data response")
        return px.bar(
            x=['Llamada', 'SMS', 'Email', 'WhatsApp'],
            y=[0, 0, 0, 0],
            labels={'x': 'Método', 'y': 'Total'},
            title='Datos no encontrados',
            text=[0, 0, 0, 0]
        )

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
    fig.update_traces(textposition='inside')
    
    return fig

# Callback to update the tipoCreacion donut chart based on selected process status
@callback(
    Output('tipo-creacion-donut', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('url', 'href'),  
    Input('status-dropdown', 'value'),
    Input('users-dropdown', 'value'),
)
def update_tipo_creacion_donut(start_date, end_date, href, selected_status, user_filter):
    nit = ''

    if href:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        nit = query_params.get('nit', [None])[0]  # Get 'nit' from query parameters
        user = query_params.get('user', [None])[0]  # Get 'user' from query parameters
   
    # API URL with dynamic dates
    # api_url = f'{url}/api/v1/Balance/get-all-consumption?initial_date={start_date}&final_date={end_date}'
    user_id = 0
    if user and int(user) > 0:
        user_id = user
    elif user_filter and user_filter > 0:
        user_id = user_filter

    token = authenticate()
    if not token:
        return px.bar(x=[], y=[], title="Error: Failed to authenticate")  # Empty plot on auth failure

    headers = {"Authorization": f"Bearer {token}"}
    api_url = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit={nit}&initial_date={start_date}&final_date={end_date}&&userAppId={user_id}'
    json_data = fetch_data(api_url, headers)
    if not json_data:
        empty_df = pd.DataFrame({'x': [], 'y': []})
        return px.bar(empty_df, x='x', y='y', title="Error: Failed to fetch data")

    df = build_data_from_api(json_data)
    return create_figure_from_data(df, selected_status, 'creation_type')


# Callback to update the tipoCreacion donut chart based on selected process status
@callback(
    Output('tipo-proceso-donut', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('url', 'href'),  
    Input('status-dropdown', 'value'),
    Input('users-dropdown', 'value'),
)
def update_tipo_proceso_donut(start_date, end_date, href, selected_status, user_filter):
    nit = ''

    if href:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        nit = query_params.get('nit', [None])[0]  # Get 'nit' from query parameters
        user = query_params.get('user', [None])[0]  # Get 'user' from query parameters
   
    # API URL with dynamic dates
    # api_url = f'{url}/api/v1/Balance/get-all-consumption?initial_date={start_date}&final_date={end_date}'
    user_id = 0
    if user and int(user) > 0:
        user_id = user
    elif user_filter and user_filter > 0:
        user_id = user_filter

    token = authenticate()
    if not token:
        return px.bar(x=[], y=[], title="Error: Failed to authenticate")  # Empty plot on auth failure

    headers = {"Authorization": f"Bearer {token}"}
    api_url = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit={nit}&initial_date={start_date}&final_date={end_date}&&userAppId={user_id}'
    json_data = fetch_data(api_url, headers)
    if not json_data:
        empty_df = pd.DataFrame({'x': [], 'y': []})
        return px.bar(empty_df, x='x', y='y', title="Error: Failed to fetch data")

    df = build_data_from_api(json_data)
    return create_figure_from_data(df, selected_status, 'process_type')
    

# Callback to update the consolidados graph
@callback(
    Output('consolidados', 'figure'),
    # Output("consolidados", "children"),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('url', 'href'),  
    Input('status-dropdown', 'value'),
    Input('users-dropdown', 'value'),
)
def update_consolidados(start_date, end_date, href, selected_status, user_filter):
    nit = ''

    if href:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        nit = query_params.get('nit', [None])[0]  # Get 'nit' from query parameters
        user = query_params.get('user', [None])[0]  # Get 'user' from query parameters
   
    # API URL with dynamic dates
    # api_url = f'{url}/api/v1/Balance/get-all-consumption?initial_date={start_date}&final_date={end_date}'
    user_id = 0
    if user and int(user) > 0:
        user_id = user
    elif user_filter and user_filter > 0:
        user_id = user_filter

    token = authenticate()
    if not token:
        return px.bar(x=[], y=[], title="Error: Failed to authenticate")  # Empty plot on auth failure

    headers = {"Authorization": f"Bearer {token}"}
    api_url = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit={nit}&userAppId={user_id}&initial_date={start_date}&final_date={end_date}'
    json_data = fetch_data(api_url, headers)
    if not json_data:
        empty_df = pd.DataFrame({'x': [], 'y': []})
        return px.bar(empty_df, x='x', y='y', title="Error: Failed to fetch data")

    df = build_data_from_api(json_data)
    return create_figure_from_data(df, selected_status, 'consolidated')


# Callback to update the auth methods graph
@callback(
    Output('auth-methods', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('url', 'href'),  
    Input('status-dropdown', 'value'),
    Input('users-dropdown', 'value'),
)
def update_auth_methods(start_date, end_date, href, selected_status, user_filter): 
    nit = ''

    if href:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        nit = query_params.get('nit', [None])[0]  # Get 'nit' from query parameters
        user = query_params.get('user', [None])[0]  # Get 'user' from query parameters
   
    # API URL with dynamic dates
    user_id = 0
    if user and int(user) > 0:
        user_id = user
    elif user_filter and user_filter > 0:
        user_id = user_filter

    token = authenticate()
    if not token:
        return px.bar(x=[], y=[], title="Error: Failed to authenticate")  # Empty plot on auth failure

    headers = {"Authorization": f"Bearer {token}"}
    api_url = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit={nit}&initial_date={start_date}&final_date={end_date}&&userAppId={user_id}'

    json_data = fetch_data(api_url, headers)
    if not json_data:
        empty_df = pd.DataFrame({'x': [], 'y': []})
        return px.bar(empty_df, x='x', y='y', title="Error: Failed to fetch data")

    df = build_data_from_api(json_data)
    return create_figure_from_data(df, selected_status, 'auth_method')

   
