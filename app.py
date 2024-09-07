import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

server = app.server

app.layout = html.Div([
    html.H1('Métricas Firma Seguro'),
    html.Div([
        html.Span(
            dcc.Link(f"{page['name']}", href=page["relative_path"]),
            style={'display': 'inline-block', 'margin': '0 10px'}  # Inline style with margin between links
        )
        for page in dash.page_registry.values()
    ]),
    dash.page_container
])

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)