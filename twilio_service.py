import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

# Check if credentials are set
if not account_sid:
    logger.error("TWILIO_ACCOUNT_SID is not set in environment variables")
if not auth_token:
    logger.error("TWILIO_AUTH_TOKEN is not set in environment variables")
if not twilio_phone:
    logger.error("TWILIO_PHONE_NUMBER is not set in environment variables")

# Log Twilio configuration (without sensitive data)
logger.info(f"Twilio configuration loaded. Using phone number: {twilio_phone}")

# Initialize Twilio client
try:
    client = Client(account_sid, auth_token)
    logger.info("Twilio client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Twilio client: {str(e)}")
    client = None

def send_otp(phone_number: str, otp: str):
    """Send OTP via Twilio SMS"""
    if not client:
        error_msg = "Twilio client not initialized. Check your credentials."
        logger.error(error_msg)
        raise Exception(error_msg)
        
    try:
        logger.info(f"Sending OTP to {phone_number}")
        
        # Format phone number if needed
        if not phone_number.startswith('+'):
            logger.warning(f"Phone number {phone_number} doesn't start with '+'. This might cause issues.")
        
        message = client.messages.create(
            body=f"Your RByte.ai verification code is: {otp}",
            from_=twilio_phone,
            to=phone_number
        )
        logger.info(f"OTP sent successfully to {phone_number}. Message SID: {message.sid}")
        return message.sid
    except TwilioRestException as e:
        error_code = e.code
        error_msg = e.msg
        logger.error(f"Twilio error {error_code}: {error_msg} when sending to {phone_number}")
        
        # Provide more specific error messages based on common Twilio error codes
        if error_code == 21614:
            raise Exception(f"Invalid phone number format: {phone_number}")
        elif error_code == 21608:
            raise Exception(f"Unverified phone number: {phone_number}. In trial mode, you can only send to verified numbers.")
        elif error_code == 20003:
            raise Exception("Authentication error. Check your Twilio credentials.")
        else:
            raise Exception(f"Twilio error: {error_msg}")
    except Exception as e:
        logger.error(f"Error sending OTP to {phone_number}: {str(e)}")
        raise Exception(f"Failed to send OTP: {str(e)}")

def verify_otp(phone_number: str, otp: str):
    """
    This function is a placeholder for a more complex OTP verification system.
    In this implementation, the actual verification is done in the API endpoint.
    """
    pass


def send_sms_to_owner(name: str, phone: str, email: str):
    # Load credentials from environment
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
    owner_phone = "+919152091676"  # Your personal mobile

    if not all([account_sid, auth_token, twilio_phone, owner_phone]):
        raise ValueError("Missing one or more Twilio environment variables.")

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Compose and send message
    message_body = f"""
    📣 New Masterclass Registration

    👤 Name: {name}
    📞 Phone: {phone}
    📧 Email: {email}
    """

    message = client.messages.create(
        body=message_body,
        from_=twilio_phone,
        to=owner_phone
    )

    return message.sid  # Optional: useful for logging