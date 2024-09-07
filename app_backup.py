# Import packages
import dash
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

#Local
from data import report

# Initialize the app
app = Dash()

server = app.server

# Load JSON data
json_data = report.consumptions_by_nit.json()

data = []
for entry in json_data:
    process_status = entry["processStatus"]
    consolidado_values = entry["consumption"]["consolidados"]
    
    # If there are values in 'consolidados', aggregate them
    total_consolidado = sum(consolidado_values.values()) if consolidado_values else 0
    
    # Append the data to the list
    data.append({"processStatus": process_status, "totalConsolidado": total_consolidado})

# Convert the data into a pandas DataFrame
df = pd.DataFrame(data)

# Inspect DataFrame (optional, for debugging)
print(df.head())

# Step 2: Initialize the Dash app
app = dash.Dash(__name__)

# Step 3: Layout of the Dash app
app.layout = html.Div([
    html.H1("Consolidado by Process Status"),
    
    # Graph component to display the data
    dcc.Graph(id='consolidado-graph'),
])

# Step 4: Callback to update the graph
@app.callback(
    Output('consolidado-graph', 'figure'),
    Input('consolidado-graph', 'id')  # Dummy input to trigger the callback
)
def update_graph(input_value):
    # Bar chart showing consolidado by process status
    fig = px.bar(
        df,
        x='processStatus',
        y='totalConsolidado',
        title='Consolidado by Process Status',
        labels={'processStatus': 'Process Status', 'totalConsolidado': 'Total Consolidado'},
        color='processStatus',  # Optional: Color bars by process status for distinction
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)

# if __name__ == '__main__':
#     app.run_server(port=8080,debug=True)