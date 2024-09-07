# Import packages
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Local import
from data import report

# Load JSON data
json_data = report.consumptions.json()

# Flatten the JSON data into a DataFrame
flat_data = []
for entry in json_data:
    nit = entry["nit"]
    total_amount_consumption = entry["consumption"]["totalAmountConsumption"]
    
    # Flatten the nested "firmaSeguroMethod"
    for method in entry["consumption"]["firmaSeguroMethod"]:
        flat_data.append({
            "nit": nit,
            "totalAmountConsumption": total_amount_consumption,
            "balanceTypeId": method["balanceTypeId"],
            "signatureMethodId": method["signatureMethodId"],
            "authenticationMethodId": method["authenticationMethodId"],
            "amountConsumed": method["amountConsumed"]
        })

# Convert the flattened data into a DataFrame
df = pd.DataFrame(flat_data)

# Register page
dash.register_page(__name__)

# Layout
layout = html.Div([
    html.H1("Consumos por NIT"),
    
    # Dropdown for selecting NIT
    dcc.Dropdown(
        id='nit-dropdown',
        options=[{'label': nit, 'value': nit} for nit in df['nit'].unique()],
        value=df['nit'].unique()[0],  # Set the default value
        clearable=False
    ),
    
    # Graph component to display the data
    dcc.Graph(id='consumption-graph'),
])

# Callback to update the graph based on the selected NIT
@callback(
    Output('consumption-graph', 'figure'),
    Input('nit-dropdown', 'value')
)
def update_graph(selected_nit):
    # Filter data based on selected NIT
    filtered_df = df[df['nit'] == selected_nit]

    # Bar chart showing the amount consumed per signature method
    fig = px.bar(
        filtered_df,
        x='signatureMethodId',
        y='amountConsumed',
        color='balanceTypeId',
        barmode='group',
        title=f'Consumos para el NIT {selected_nit}',
        labels={'signatureMethodId': 'Metodo de Firma', 'amountConsumed': 'Cantidad Consumida'}
    )

    return fig
