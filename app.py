import os
import dash
from dash import Dash, html, dcc

# Get the base path from the environment variable (default to '/'). ex: /dashboard/
requests_pathname_prefix = os.getenv('REQUESTS_PATHNAME_PREFIX', '/')
routes_pathname_prefix = os.getenv('ROUTES_PATHNAME_PREFIX', '/')

app = Dash(__name__, use_pages=True, serve_locally=False, requests_pathname_prefix=requests_pathname_prefix, routes_pathname_prefix=routes_pathname_prefix,)

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
