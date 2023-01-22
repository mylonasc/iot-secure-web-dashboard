import os

HOSTNAME='your-server-here' # can be localhost. 
PORT = 5000 # 

# For filling the following fields, check out the microsoft guide for setting up 
# Azure AD B2C: 
# (section 6.5)
#   https://learn.microsoft.com/en-us/azure/active-directory-b2c/configure-authentication-sample-python-web-app?tabs=linux
b2c_tenant = "<example tenant>" 
signupsignin_user_flow = "B2C_1_signupsignin1"
signupsignin_user_flow = "B2C_1_signin_only_user_flow"
# signupsignin_user_flow='B2C_1_whatever-test'

editprofile_user_flow = "B2C_1_profileediting1"

resetpassword_user_flow = "B2C_1_passwordreset1"  # Note: Legacy setting.

authority_template = "https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{user_flow}"

# CLIENT_ID = "Enter_the_Application_Id_here" # Application (client) ID of app registration
CLIENT_ID='cccccc-cccc-cccc-cccc-cccccccccccc'
CLIENT_SECRET='<example_secret>'

AUTHORITY = authority_template.format(
    tenant=b2c_tenant, user_flow=signupsignin_user_flow)
B2C_PROFILE_AUTHORITY = authority_template.format(
    tenant=b2c_tenant, user_flow=editprofile_user_flow)

B2C_RESET_PASSWORD_AUTHORITY = authority_template.format(
    tenant=b2c_tenant, user_flow=resetpassword_user_flow)

REDIRECT_PATH = "/getAToken"  

# This is the API resource endpoint
ENDPOINT = 'http://{hostname}:{port}'.format(hostname = HOSTNAME, port= PORT)

# These are the scopes you've exposed in the web API app registration in the Azure portal
SCOPE = []  # Example with two exposed scopes: ["demo.read", "demo.write"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
