import requests
import string
import random

# --- CONFIGURATION ---
# Get your credentials from https://www.linkedin.com/developers
CLIENT_ID = '77hpfpf5cv4m4t'
CLIENT_SECRET = '***REMOVED***.ASm4Xw=='

# This must match EXACTLY what you put in the Developer Portal
REDIRECT_URI = 'http://localhost:8000/callback' 

# --- FUNCTIONS ---

def generate_auth_url():
    # We are asking for permission to post as YOU (w_member_social)
    scopes = ['openid', 'profile', 'w_member_social', 'email']
    state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"state={state}&"
        f"scope={'%20'.join(scopes)}"
    )
    return auth_url

def get_access_token(auth_code):
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url, data=data)
    return response.json()

def get_user_urn(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
    if response.status_code != 200:
        print("Error fetching user ID:", response.text)
        return None
    user_data = response.json()
    return user_data.get('sub') # 'sub' is your unique Member ID

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("\n--- LINKEDIN BOT SETUP ---\n")
    print("1. Click this link to authorize your bot:")
    print("-" * 60)
    print(generate_auth_url())
    print("-" * 60)
    
    print("\n2. After you log in, you will see a 'This site can't be reached' error.")
    print("   THIS IS SUCCESS! Look at the URL bar at the top.")
    print("   It will look like: http://localhost:8000/callback?code=THIS_IS_THE_CODE&state=...")
    
    auth_code = input("\n3. Copy the code (between code= and &state) and paste it here: ")
    
    # Clean up the code just in case extra spaces were pasted
    auth_code = auth_code.strip()
    
    print("\nExchanging code for token...")
    token_data = get_access_token(auth_code)
    
    if 'access_token' in token_data:
        access_token = token_data['access_token']
        print("\nGetting your User ID...")
        user_urn = get_user_urn(access_token)
        
        print("\n" + "="*40)
        print("SUCCESS! SAVE THESE TWO VALUES:")
        print("="*40)
        print(f"ACCESS_TOKEN: {access_token}")
        print(f"USER_URN:     {user_urn}")
        print("="*40)
    else:
        print("\nError! Could not get token.")
        print("Server Response:", token_data)