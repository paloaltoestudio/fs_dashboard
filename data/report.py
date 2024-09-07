import requests

# The API endpoint
auth = "https://pruebas.firmaseguro.co/api/v1/Auth/SignIn"
get_all_consumptions = 'https://pruebas.firmaseguro.co/api/v1/Balance/get-all-consumption?initial_date=2024-01-01&final_date=2024-08-28'
get_consumptions_by_nit = 'https://pruebas.firmaseguro.co/api/v1/Balance/get-all-consumption-by-nit?nit=1012402467&userAppId=0&initial_date=2024-01-01&final_date=2024-08-28'

# Data to be sent
data = {
  "email": "hola@firmaseguro.co",
  "password": "%AL1h45g6Jw0PChDKKSXRpcFnw"
}

# A POST request to the API
response = requests.post(auth, json=data)

res_json = response.json()
token = res_json['access_token']

headers = {
    "Authorization": f"Bearer {token}"
}


consumptions = requests.get(get_all_consumptions, headers=headers)
consumptions_by_nit = requests.get(get_consumptions_by_nit, headers=headers)

if __name__ == 'main':
  # Print the response
  print(consumptions.json())
