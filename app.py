import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True, serve_locally=False)

server = app.server

app.layout = html.Div([
    html.Div([
        html.Span(
            dcc.Link(f"{page['name']}", href=page["relative_path"]),
            style={'display': 'none', 'margin': '0 10px'}  # Inline style with margin between links
        )
        for page in dash.page_registry.values()
    ]),
    dash.page_container
])

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)
