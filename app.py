import requests
import os
from flask import Flask, redirect, request
import base64
import time

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
USERNAME = os.getenv("USERNAME")
SCOPE=os.getenv("SCOPE")
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
credentials_base64 = base64.b64encode(credentials.encode()).decode()

@app.route('/')
def home():
    return """
        <h1>Spotify Authorization Flow</h1>
        <p>This is a simple Flask application demonstrating Spotify authorization flow.</p>
        <p><strong>/authorize:</strong> Redirects the user to Spotify authorization page.</p>
        <p><strong>/callback:</strong> Handles the callback from Spotify after user authorization.</p>
        <p><strong>/refresh-token:</strong> Refreshes the access token using the refresh token.</p>
        <p><strong>Note:</strong> Make sure to provide the refresh token in the parameters. Example: <a href="http://127.0.0.1:5000/refresh-token?refresh_token={YOUR_REFRESH_TOKEN}">http://127.0.0.1:5000/refresh-token?refresh_token={YOUR_REFRESH_TOKEN}</a></p>
    """

@app.route('/authorize')
def authorize():
    authorize_url=f"https://accounts.spotify.com/authorize"
    authorize_params={
        "response_type": 'code',
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI
    }
    return redirect(authorize_url + '?' + '&'.join([f'{key}={value}' for key, value in authorize_params.items()]))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    authorize_url=f"https://accounts.spotify.com/api/token"
    form= {
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": 'authorization_code'
    }
    headers= {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {credentials_base64}"
      }
    print("Authorization Code:", code)
    response=requests.post(url=authorize_url,headers=headers,data=form)
    data=response.json()
    return {
        "access_token": data['access_token'],
        "refresh_token": data['refresh_token'],
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "playlist-modify-private user-read-email user-read-private",
        "token_generated_time":time.time(),
        "token_expire_time":time.time()+3600
    }

@app.route('/refresh-token')
def refreshToken():
    refresh_token=request.args.get('refresh_token')
    refresh_url="https://accounts.spotify.com/api/token"
    refresh_headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {credentials_base64}"
    }
    refresh_body={
        "grant_type":"refresh_token",
        "refresh_token": refresh_token
    }
    
    response=requests.post(url=refresh_url,headers=refresh_headers,data=refresh_body)
    if response.status_code == 200:
        data=response.json()
        return {
        "access_token": data['access_token'],
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "playlist-modify-private user-read-email user-read-private",
        "token_generated_time":time.time(),
        "token_expire_time":time.time()+3600
        }



# if __name__ == '__main__':
#     app.run(debug=True)