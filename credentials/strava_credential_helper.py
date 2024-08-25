import json

def get_credentials() -> dict:
    with open('credentials/strava_api_token.json', 'r') as f:
        credentials = json.loads(f.read())
    return credentials

def set_credentials(credentials:dict) -> None:
    with open('credentials/strava_api_token.json', 'w') as f:
        f.write(json.dumps(credentials))

def get_strava_api_token() -> str:
    credentials = get_credentials()
    return credentials['access_token']

def set_strava_api_token(new_token: str) -> None:
    credentials = get_credentials()
    credentials['access_token'] = new_token
    set_credentials(credentials)

def get_strava_refresh_token() -> str:
    credentials = get_credentials()
    return credentials['refresh_token']

def strava_refresh_token(new_token: str) -> None:
    credentials = get_credentials()
    credentials['refresh_token'] = new_token
    set_credentials(credentials)

def get_or_refresh_token():
    pass