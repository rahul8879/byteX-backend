from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class PhoneNumber(BaseModel):
    phone: str
    country_code: str = "+91"

class OTPRequest(BaseModel):
    phone_number: str
    country_code: str = "+91"

class OTPVerify(BaseModel):
    phone_number: str
    country_code: str = "+91"
    otp: str

class OTPVerification(BaseModel):
    phone: str
    country_code: str = "+91"
    otp: str

class OTPResponse(BaseModel):
    success: bool
    message: str

class OTPVerificationResponse(BaseModel):
    success: bool
    message: str

class Registration(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    country_code: str = "+91"
    heard_from: Optional[str] = None

class RegistrationResponse(BaseModel):
    success: bool
    message: str
    id: int

class Enrollment(BaseModel):
    name: str
    email: str
    phone: str
    country_code: str = "+91"
    current_role: str
    experience: str
    programming_experience: str
    goals: str
    heard_from: Optional[str] = None
    preferred_batch: str

class EnrollmentResponse(BaseModel):
    success: bool
    message: str
    id: int

class MasterclassRegistration(BaseModel):
    name: str
    phone: str
    country_code: str = "+91"
    email: Optional[str] = None

class MasterclassResponse(BaseModel):
    success: bool
    message: str
    id: int

# New response models for listing records
class RegistrationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: Optional[str] = None
    phone: str
    country_code: str
    heard_from: Optional[str] = None
    created_at: datetime

class EnrollmentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str
    phone: str
    country_code: str
    current_role: str
    experience: str
    programming_experience: str
    goals: str
    heard_from: Optional[str] = None
    preferred_batch: str
    created_at: datetime
    payment_status: bool

class MasterclassRegistrationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: Optional[str] = None
    phone: str
    country_code: str
    created_at: datetime
    attended: bool

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
