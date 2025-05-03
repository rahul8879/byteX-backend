# RByte.ai Backend API

This is the backend API for the RByte.ai AI Engineering Course website.

## Features

- OTP verification using Twilio
- Registration and enrollment data storage in SQLite
- Curriculum PDF download endpoint
- Masterclass registration

## Setup

1. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

2. Configure environment variables:
   - Create a `.env` file with your Twilio credentials
   - Example:
     \`\`\`
     TWILIO_ACCOUNT_SID=your_account_sid
     TWILIO_AUTH_TOKEN=your_auth_token
     TWILIO_PHONE_NUMBER=your_twilio_phone_number
     \`\`\`

3. Run the server:
   \`\`\`
   python run.py
   \`\`\`

4. Access the API documentation at:
   \`\`\`
   http://localhost:8000/docs
   \`\`\`

## API Endpoints

- `POST /api/send-otp`: Send OTP to a phone number
- `POST /api/verify-otp`: Verify OTP
- `POST /api/register`: Register interest in the course
- `POST /api/enroll`: Enroll in the course
- `GET /api/curriculum`: Download curriculum PDF
- `POST /api/masterclass-register`: Register for a masterclass

## Database

The application uses SQLite for data storage. The database file is `rbyte_ai.db`.
# byteX-backend
