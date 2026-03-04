import os
from twilio.rest import Client
from dotenv import load_dotenv
import sys

def verify_twilio_credentials():
    """Verify Twilio credentials are correctly configured"""
    # Load environment variables
    load_dotenv()
    
    # Get Twilio credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Check if credentials are set
    if not account_sid:
        print("ERROR: TWILIO_ACCOUNT_SID is not set in environment variables")
        return False
    
    if not auth_token:
        print("ERROR: TWILIO_AUTH_TOKEN is not set in environment variables")
        return False
    
    if not twilio_phone:
        print("ERROR: TWILIO_PHONE_NUMBER is not set in environment variables")
        return False
    
    print(f"Twilio phone number: {twilio_phone}")
    
    # Try to initialize Twilio client
    try:
        client = Client(account_sid, auth_token)
        
        # Try to fetch account info to verify credentials
        account = client.api.accounts(account_sid).fetch()
        print(f"Successfully connected to Twilio account: {account.friendly_name}")
        
        # Check if the phone number exists in the account
        try:
            numbers = client.incoming_phone_numbers.list(phone_number=twilio_phone)
            if numbers:
                print(f"Phone number {twilio_phone} is valid and belongs to your account")
            else:
                print(f"WARNING: Phone number {twilio_phone} was not found in your account")
                return False
        except Exception as e:
            print(f"Error checking phone number: {str(e)}")
            return False
        
        return True
    except Exception as e:
        print(f"Error connecting to Twilio: {str(e)}")
        return False

if __name__ == "__main__":
    print("Verifying Twilio credentials...")
    success = verify_twilio_credentials()
    
    if success:
        print("\nTwilio credentials are valid!")
        sys.exit(0)
    else:
        print("\nTwilio credential verification failed!")
        sys.exit(1)
