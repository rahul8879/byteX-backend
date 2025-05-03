from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from api.database import Base

class Registration(Base):
    """Model for storing basic user registrations (interest in the course)"""
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False)
    country_code = Column(String(10), nullable=False)
    heard_from = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False)

class Enrollment(Base):
    """Model for storing full course enrollments"""
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    country_code = Column(String(10), nullable=False)
    current_role = Column(String(100), nullable=False)
    experience = Column(String(20), nullable=False)
    programming_experience = Column(String(20), nullable=False)
    goals = Column(Text, nullable=False)
    heard_from = Column(String(50), nullable=True)
    preferred_batch = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False)
    payment_status = Column(Boolean, default=False)

class MasterclassRegistration(Base):
    """Model for storing masterclass registrations"""
    __tablename__ = "masterclass_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False)
    country_code = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False)
    attended = Column(Boolean, default=False)
