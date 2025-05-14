import os
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form, Request,Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import Optional
import random
import string
from datetime import datetime, timedelta
import logging
from sqlalchemy import desc
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from database import SessionLocal, engine, Base
import models as models
import schemas as schemas
from twilio_service import send_otp, verify_otp

# Create database tables
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

app = FastAPI(title="RByte.ai API", description="Backend API for RByte.ai AI Engineering Course")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins like ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In-memory OTP storage (in production, use Redis or another persistent store)
otp_store = {}

@app.get("/")
def read_root():
    return {"message": "Welcome to RByte.ai API"}

@app.post("/api/send-otp", response_model=schemas.OTPResponse)
async def send_otp_endpoint(phone_data: schemas.PhoneNumber):
    """Send OTP to the provided phone number using Twilio"""
    phone = phone_data.phone
    country_code = phone_data.country_code
    
    # Format phone number for Twilio
    formatted_phone = f"{country_code}{phone}"
    
    # Generate a 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    try:
        # Send the randomly generated OTP via Twilio
        send_otp(formatted_phone, otp)
        
        # Store OTP with expiration time (5 minutes)
        otp_store[formatted_phone] = {
            "otp": otp,
            "expires_at": datetime.now() + timedelta(minutes=5)
        }
        
        logger.info(f"OTP sent to {formatted_phone}: {otp}")
        return {"success": True, "message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@app.post("/api/verify-otp", response_model=schemas.OTPVerificationResponse)
async def verify_otp_endpoint(verification_data: schemas.OTPVerification):
    """Verify the OTP provided by the user"""
    phone = verification_data.phone
    country_code = verification_data.country_code
    otp_code = verification_data.otp
    
    formatted_phone = f"{country_code}{phone}"
    logger.info(f"Verifying OTP for phone: {formatted_phone}")
    
    # Check if OTP exists and is valid
    if formatted_phone not in otp_store:
        logger.warning(f"No OTP found for phone: {formatted_phone}")
        raise HTTPException(status_code=400, detail="No OTP was sent to this number")
    
    stored_otp = otp_store[formatted_phone]
    
    # Check if OTP has expired
    if datetime.now() > stored_otp["expires_at"]:
        logger.warning(f"OTP expired for phone: {formatted_phone}")
        del otp_store[formatted_phone]
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # Verify OTP
    if stored_otp["otp"] != otp_code:
        logger.warning(f"Invalid OTP for phone: {formatted_phone}")
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Clear the OTP after successful verification
    logger.info(f"OTP verified successfully for phone: {formatted_phone}")
    del otp_store[formatted_phone]
    
    return {"success": True, "message": "OTP verified successfully"}

@app.post("/api/register", response_model=schemas.RegistrationResponse)
async def register_user(
    registration: schemas.Registration,
    db: Session = Depends(get_db)
):
    """Register a new user interested in the course"""
    # Create new registration record
    db_registration = models.Registration(
        name=registration.name,
        email=registration.email,
        phone=registration.phone,
        country_code=registration.country_code,
        heard_from=registration.heard_from,
        created_at=datetime.now()
    )
    
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    
    return {"success": True, "message": "Registration successful", "id": db_registration.id}

@app.post("/api/enroll", response_model=schemas.EnrollmentResponse)
async def enroll_user(
    enrollment: schemas.Enrollment,
    db: Session = Depends(get_db)
):
    """Enroll a user in the AI Engineering course"""
    # Create new enrollment record
    db_enrollment = models.Enrollment(
        name=enrollment.name,
        email=enrollment.email,
        phone=enrollment.phone,
        country_code=enrollment.country_code,
        current_role=enrollment.current_role,
        experience=enrollment.experience,
        programming_experience=enrollment.programming_experience,
        goals=enrollment.goals,
        heard_from=enrollment.heard_from,
        preferred_batch=enrollment.preferred_batch,
        created_at=datetime.now()
    )
    
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    
    return {"success": True, "message": "Enrollment successful", "id": db_enrollment.id}

@app.get("/api/curriculum", response_class=FileResponse)
async def get_curriculum():
    """Return the curriculum PDF"""
    # Path to the PDF file and make more secure
    pdf_path = "static/RByte.ai – AI Engineering Professional Program (3).pdf"
    
    # Check if file exists
    if not os.path.isfile(pdf_path):
        raise HTTPException(status_code=404, detail="Curriculum PDF not found")
    
    # Return the PDF file
    return FileResponse(
        pdf_path, 
        media_type="application/pdf",
        filename="RByte.ai_AI_Engineering_Curriculum.pdf"
    )

@app.post("/api/masterclass-register", response_model=schemas.MasterclassResponse)
async def register_for_masterclass(
    masterclass: schemas.MasterclassRegistration,
    db: Session = Depends(get_db)
):
    """Register a user for the free masterclass"""
    # Create new masterclass registration record
    db_masterclass = models.MasterclassRegistration(
        name=masterclass.name,
        phone=masterclass.phone,
        country_code=masterclass.country_code,
        email=masterclass.email,
        created_at=datetime.now()
    )
    
    db.add(db_masterclass)
    db.commit()
    db.refresh(db_masterclass)
    
    return {"success": True, "message": "Masterclass registration successful", "id": db_masterclass.id}

@app.get("/api/test-otp/{phone}")
async def test_otp(phone: str, country_code: str = "+91"):
    """Test endpoint to send an OTP to a specific phone number"""
    try:
        formatted_phone = f"{country_code}{phone}"
        logger.info(f"Test sending OTP to: {formatted_phone}")
        
        # Generate a random 6-digit OTP for testing
        test_otp = ''.join(random.choices(string.digits, k=6))
        
        # Send the OTP
        message_sid = send_otp(formatted_phone, test_otp)
        
        # Store OTP with expiration time (5 minutes)
        otp_store[formatted_phone] = {
            "otp": test_otp,
            "expires_at": datetime.now() + timedelta(minutes=5)
        }
        
        logger.info(f"Test OTP sent to {formatted_phone}: {test_otp}")
        return {
            "success": True, 
            "message": f"Test OTP sent successfully to {formatted_phone}",
            "message_sid": message_sid,
            "otp": test_otp  # Include OTP in response for testing purposes only
        }
    except Exception as e:
        logger.error(f"Error in test OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send test OTP: {str(e)}")

@app.get("/api/debug/status")
async def debug_status():
    """Debug endpoint to check server status and configuration"""
    try:
        # Check Twilio configuration
        twilio_config = {
            "account_sid_set": bool(os.getenv("TWILIO_ACCOUNT_SID")),
            "auth_token_set": bool(os.getenv("TWILIO_AUTH_TOKEN")),
            "phone_number_set": bool(os.getenv("TWILIO_PHONE_NUMBER")),
            "phone_number": os.getenv("TWILIO_PHONE_NUMBER")
        }
        
        # Check database connection
        db = SessionLocal()
        db_connected = True
        try:
            # Try a simple query
            db.execute("SELECT 1")
        except Exception as e:
            db_connected = False
            db_error = str(e)
        finally:
            db.close()
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "twilio_config": twilio_config,
            "database": {
                "connected": db_connected,
                "error": db_error if not db_connected else None
            },
            "otp_store_size": len(otp_store)
        }
    except Exception as e:
        logger.error(f"Error in debug status endpoint: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    
# New endpoints to fetch all registrations, enrollments, and masterclass registrations
@app.get("/api/registrations", response_model=schemas.PaginatedResponse)
async def get_all_registrations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all course registrations with pagination"""
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total = db.query(models.Registration).count()
        
        # Get registrations with pagination
        registrations = db.query(models.Registration)\
            .order_by(desc(models.Registration.created_at))\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        # Log the query results
        logger.info(f"Registrations query returned {len(registrations)} results")
        logger.info(f"Total registrations count: {total}")
        
        # Calculate total pages
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # If requested page is greater than total pages and total pages is not zero, return first page
        if page > total_pages and total_pages > 0:
            page = 1
            offset = 0
            registrations = db.query(models.Registration)\
                .order_by(desc(models.Registration.created_at))\
                .offset(offset)\
                .limit(page_size)\
                .all()
        
        # Convert to Pydantic models - using model_validate instead of from_orm
        registration_items = [schemas.RegistrationItem.model_validate(reg) for reg in registrations]
        
        return {
            "items": registration_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error fetching registrations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch registrations: {str(e)}")

@app.get("/api/enrollments", response_model=schemas.PaginatedResponse)
async def get_all_enrollments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all course enrollments with pagination"""
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total = db.query(models.Enrollment).count()
        
        # Get enrollments with pagination
        enrollments = db.query(models.Enrollment)\
            .order_by(desc(models.Enrollment.created_at))\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        # Log the query results
        logger.info(f"Enrollments query returned {len(enrollments)} results")
        logger.info(f"Total enrollments count: {total}")
        
        # Calculate total pages
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # If requested page is greater than total pages and total pages is not zero, return first page
        if page > total_pages and total_pages > 0:
            page = 1
            offset = 0
            enrollments = db.query(models.Enrollment)\
                .order_by(desc(models.Enrollment.created_at))\
                .offset(offset)\
                .limit(page_size)\
                .all()
        
        # Convert to Pydantic models - using model_validate instead of from_orm
        enrollment_items = [schemas.EnrollmentItem.model_validate(enroll) for enroll in enrollments]
        
        return {
            "items": enrollment_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error fetching enrollments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch enrollments: {str(e)}")

@app.get("/api/masterclass-registrations", response_model=schemas.PaginatedResponse)
async def get_all_masterclass_registrations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all masterclass registrations with pagination"""
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total = db.query(models.MasterclassRegistration).count()
        
        # Get masterclass registrations with pagination
        masterclass_registrations = db.query(models.MasterclassRegistration)\
            .order_by(desc(models.MasterclassRegistration.created_at))\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        # Log the query results
        logger.info(f"MasterclassRegistrations query returned {len(masterclass_registrations)} results")
        logger.info(f"Total masterclass_registrations count: {total}")
        
        # Calculate total pages
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # If requested page is greater than total pages and total pages is not zero, return first page
        if page > total_pages and total_pages > 0:
            page = 1
            offset = 0
            masterclass_registrations = db.query(models.MasterclassRegistration)\
                .order_by(desc(models.MasterclassRegistration.created_at))\
                .offset(offset)\
                .limit(page_size)\
                .all()
        
        # Convert to Pydantic models - using model_validate instead of from_orm
        masterclass_items = [schemas.MasterclassRegistrationItem.model_validate(reg) for reg in masterclass_registrations]
        
        return {
            "items": masterclass_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error fetching masterclass registrations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch masterclass registrations: {str(e)}")

@app.get("/api/all-leads")
async def get_all_leads(
    db: Session = Depends(get_db)
):
    """Get all leads (registrations, enrollments, and masterclass registrations)"""
    try:
        # Get counts
        registrations_count = db.query(models.Registration).count()
        enrollments_count = db.query(models.Enrollment).count()
        masterclass_count = db.query(models.MasterclassRegistration).count()
        
        # Get the most recent leads from each category
        recent_registrations = db.query(models.Registration)\
            .order_by(desc(models.Registration.created_at))\
            .limit(5)\
            .all()
        
        recent_enrollments = db.query(models.Enrollment)\
            .order_by(desc(models.Enrollment.created_at))\
            .limit(5)\
            .all()
        
        recent_masterclass = db.query(models.MasterclassRegistration)\
            .order_by(desc(models.MasterclassRegistration.created_at))\
            .limit(5)\
            .all()
        
        # Convert to dictionaries manually instead of using Pydantic models
        registration_items = []
        for reg in recent_registrations:
            registration_items.append({
                "id": reg.id,
                "name": reg.name,
                "email": reg.email,
                "phone": reg.phone,
                "country_code": reg.country_code,
                "heard_from": reg.heard_from,
                "created_at": reg.created_at.isoformat() if reg.created_at else None
            })
        
        enrollment_items = []
        for enroll in recent_enrollments:
            enrollment_items.append({
                "id": enroll.id,
                "name": enroll.name,
                "email": enroll.email,
                "phone": enroll.phone,
                "country_code": enroll.country_code,
                "current_role": enroll.current_role,
                "experience": enroll.experience,
                "programming_experience": enroll.programming_experience,
                "goals": enroll.goals,
                "heard_from": enroll.heard_from,
                "preferred_batch": enroll.preferred_batch,
                "created_at": enroll.created_at.isoformat() if enroll.created_at else None,
                "payment_status": enroll.payment_status
            })
        
        masterclass_items = []
        for reg in recent_masterclass:
            masterclass_items.append({
                "id": reg.id,
                "name": reg.name,
                "email": reg.email,
                "phone": reg.phone,
                "country_code": reg.country_code,
                "created_at": reg.created_at.isoformat() if reg.created_at else None,
                "attended": reg.attended
            })
        
        return {
            "counts": {
                "registrations": registrations_count,
                "enrollments": enrollments_count,
                "masterclass_registrations": masterclass_count,
                "total_leads": registrations_count + enrollments_count + masterclass_count
            },
            "recent_leads": {
                "registrations": registration_items,
                "enrollments": enrollment_items,
                "masterclass_registrations": masterclass_items
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching all leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch all leads: {str(e)}")

@app.get("/api/debug/tables")
async def debug_tables():
    """Debug endpoint to check all tables and their record counts"""
    from debug_database import check_database_tables
    
    try:
        results = check_database_tables()
        return results
    except Exception as e:
        logger.error(f"Error in debug tables endpoint: {str(e)}")
        return {"error": str(e)}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
