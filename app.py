from dash import Dash, html

app = Dash()

app.layout = [html.Div(children='Hello World')]

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)

# if __name__ == '__main__':
#     app.run_server(port=8080,debug=True)