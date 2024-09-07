import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url = os.getenv('DEVURL')

# The API endpoint
auth = f"{url}/api/v1/Auth/SignIn"
get_all_consumptions = f'{url}/api/v1/Balance/get-all-consumption?initial_date=2024-01-01&final_date=2024-08-28'
get_consumptions_by_nit = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit=1012402467&userAppId=0&initial_date=2024-01-01&final_date=2024-08-28'

# Access environment variables
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

# data to auth
data = {
    "email": email,
    "password": password
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
