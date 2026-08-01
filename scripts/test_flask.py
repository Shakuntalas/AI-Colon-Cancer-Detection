import os
import requests
import warnings
warnings.filterwarnings("ignore")

def test_flask_app():
    # Attempt to access the running flask app
    url = "http://127.0.0.1:5000"
    try:
        res = requests.get(url)
        print(f"Status Code: {res.status_code}")
        print("Connected to Flask!")
    except Exception as e:
        print("Flask is not accessible:", e)

if __name__ == "__main__":
    test_flask_app()
