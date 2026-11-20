import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    user_id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), default="user") # "user" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")
    vehicles = relationship("Vehicle", back_populates="user")

class Admin(Base):
    __tablename__ = "admins"
    admin_id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(120), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ParkingLocation(Base):
    __tablename__ = "parking_locations"
    location_id = Column(String(36), primary_key=True, default=gen_uuid)
    location_name = Column(String(150), nullable=False)
    address = Column(String(255), nullable=False)
    total_slots = Column(Integer, default=50)
    hourly_rate = Column(Float, default=30.0) # Tariff per hour in INR
    image_url = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    slots = relationship("ParkingSlot", back_populates="location", cascade="all, delete-orphan")
    history = relationship("ParkingHistory", back_populates="location")
    predictions = relationship("Prediction", back_populates="location")

class ParkingSlot(Base):
    __tablename__ = "parking_slots"
    slot_id = Column(String(36), primary_key=True, default=gen_uuid)
    location_id = Column(String(36), ForeignKey("parking_locations.location_id"), nullable=False)
    slot_number = Column(String(20), nullable=False)
    slot_type = Column(String(50), default="Regular") # "Regular", "EV Charging", "Accessible"
    status = Column(String(30), default="Available") # "Available", "Occupied", "Reserved"

    location = relationship("ParkingLocation", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot")

class Vehicle(Base):
    __tablename__ = "vehicles"
    vehicle_id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    vehicle_number = Column(String(30), nullable=False)
    vehicle_type = Column(String(30), default="Car") # Car, SUV, Bike
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vehicles")

class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    slot_id = Column(String(36), ForeignKey("parking_slots.slot_id"), nullable=False)
    vehicle_number = Column(String(30), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    booking_status = Column(String(30), default="Confirmed") # Confirmed, Checked-in, Completed, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    slot = relationship("ParkingSlot", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    session = relationship("ParkingSession", back_populates="booking", uselist=False)
    ticket = relationship("QRTicket", back_populates="booking", uselist=False)

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(String(36), primary_key=True, default=gen_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.booking_id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), default="UPI / Card")
    payment_status = Column(String(30), default="Successful") # Pending, Successful, Failed
    payment_date = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payment")

class ParkingSession(Base):
    __tablename__ = "parking_sessions"
    session_id = Column(String(36), primary_key=True, default=gen_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.booking_id"), nullable=False)
    entry_time = Column(DateTime, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    duration = Column(Integer, default=0) # Duration in minutes
    total_amount = Column(Float, default=0.0)
    session_status = Column(String(30), default="Active") # Active, Completed

    booking = relationship("Booking", back_populates="session")

class QRTicket(Base):
    __tablename__ = "qr_tickets"
    ticket_id = Column(String(36), primary_key=True, default=gen_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.booking_id"), nullable=False)
    qr_code_data = Column(Text, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    ticket_status = Column(String(30), default="Active") # Active, Used, Expired

    booking = relationship("Booking", back_populates="ticket")

class ParkingHistory(Base):
    __tablename__ = "parking_history"
    history_id = Column(String(36), primary_key=True, default=gen_uuid)
    location_id = Column(String(36), ForeignKey("parking_locations.location_id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    total_slots = Column(Integer, nullable=False)
    occupied_slots = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)

    location = relationship("ParkingLocation", back_populates="history")

class Prediction(Base):
    __tablename__ = "predictions"
    prediction_id = Column(String(36), primary_key=True, default=gen_uuid)
    location_id = Column(String(36), ForeignKey("parking_locations.location_id"), nullable=False)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    target_time = Column(DateTime, nullable=False)
    predicted_occupancy = Column(Float, nullable=False) # e.g. 75.5 %
    predicted_available_slots = Column(Integer, nullable=False)
    model_version = Column(String(50), default="v1.0-RandomForest")

    location = relationship("ParkingLocation", back_populates="predictions")
