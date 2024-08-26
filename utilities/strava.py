# Example token refresh
# curl -X POST https://www.strava.com/api/v3/oauth/token \
#   -d client_id=ReplaceWithClientID \
#   -d client_secret=ReplaceWithClientSecret \
#   -d grant_type=refresh_token \
#   -d refresh_token=ReplaceWithRefreshToken

from credentials import strava_credential_helper as s
import time
import requests

credentials = s.get_or_refresh_token()
access_token = credentials['access_token']
response = requests.get('https://website.example/id', headers={'Authorization': f'access_token {access_token}'})
