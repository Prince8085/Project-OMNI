import os
import requests
from dotenv import load_dotenv

load_dotenv('config/.env')
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    exit()

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"✅ Successfully connected with API Key.")
        print(f"Available 2.0 Models:")
        for m in models:
            if '2.0' in m['name']:
                print(f" - {m['name']}")
        
        if not found_2_0:
            print("\n⚠️ WARNING: 'gemini-2.0-flash' was NOT found in the list.")
            print("This explains the 404 error. The model name is likely incorrect or not available to this key.")
    else:
        print(f"❌ API Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Connection failed: {e}")
