from O365 import Account
import os

def get_ms_account():
    credentials = (os.getenv('AZURE_CLIENT_ID'), os.getenv('AZURE_CLIENT_SECRET'))
    protocol = 'microsoft_graph'
    scopes = ['https://graph.microsoft.com/.default']
    account = Account(credentials, auth_flow_type='credentials', tenant_id=os.getenv('AZURE_TENANT_ID'))
    
    if account.authenticate():
        return account
    return None