import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

url = os.getenv('DEVURL')

# Set date range
current_date = datetime.now().date()
initial_start_date = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
initial_end_date = current_date.strftime('%Y-%m-%d')

# The API endpoint
auth = f"{url}/api/v1/Auth/SignIn"
get_all_consumptions = f'{url}/api/v1/Balance/get-all-consumption?initial_date={initial_start_date}&final_date={current_date}'
get_consumptions_by_nit = f'{url}/api/v1/Balance/get-all-consumption-by-nit?nit=1012402467&initial_date={initial_start_date}&final_date={current_date}'

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
