import json
import time
from stravalib import Client

def get_credentials() -> dict:
    with open('credentials/strava_api_token.json', 'r') as f:
        credentials = json.loads(f.read())
    return credentials

def set_credentials(credentials:dict) -> None:
    with open('credentials/strava_api_token.json', 'w') as f:
        f.write(json.dumps(credentials))

def get_or_refresh_token():
    c = Client()
    cred = get_credentials()

    if time.time() > cred['expires_at']:
        refresh_response = c.refresh_access_token(
            client_id=cred['client_id'], client_secret=cred['client_secret'], refresh_token=cred['refresh_token']
        )

        cred['access_token'] = refresh_response["access_token"]
        cred['refresh_token'] = refresh_response["refresh_token"]
        cred['expires_at'] = refresh_response["expires_at"]
        set_credentials(cred)
    return cred