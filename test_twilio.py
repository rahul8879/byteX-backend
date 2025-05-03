import os
from twilio.rest import Client
from dotenv import load_dotenv

def test_twilio_connection():
    """Test Twilio connection and credentials"""
    # Load environment variables
    load_dotenv()
    
    # Get Twilio credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Print configuration (without auth token for security)
    print(f"Twilio Account SID: {account_sid[:5]}...{account_sid[-5:]}")
    print(f"Twilio Phone Number: {twilio_phone}")
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Get account info to verify credentials
        account = client.api.accounts(account_sid).fetch()
        
        print(f"Successfully connected to Twilio!")
        print(f"Account Status: {account.status}")
        print(f"Account Type: {account.type}")
        
        return True
    except Exception as e:
        print(f"Error connecting to Twilio: {str(e)}")
        return False

if __name__ == "__main__":
    test_twilio_connection()
