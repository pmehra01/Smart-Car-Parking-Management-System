import os
import json
import random
from datetime import datetime, timedelta
import pandas as pd
from database import engine, Base, SessionLocal
from models import (
    User, Admin, ParkingLocation, ParkingSlot, Vehicle,
    Booking, Payment, ParkingSession, QRTicket, ParkingHistory
)

def seed():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded
    if db.query(ParkingLocation).first():
        print("Database already has records, skipping seed.")
        db.close()
        return

    print("Seeding initial users and admins...")
    # Admin
    admin = User(
        user_id="admin-001",
        name="Chief Admin",
        email="admin@parking.com",
        password_hash="admin123", # For demonstration
        phone="+91 9876543210",
        role="admin"
    )
    db.add(admin)

    # Demo User
    demo_user = User(
        user_id="user-001",
        name="Rahul Sharma",
        email="user@example.com",
        password_hash="user123",
        phone="+91 9123456789",
        role="user"
    )
    db.add(demo_user)

    # Demo Vehicle
    demo_vehicle = Vehicle(
        vehicle_id="veh-001",
        user_id="user-001",
        vehicle_number="KA-01-MJ-5566",
        vehicle_type="Car"
    )
    db.add(demo_vehicle)

    print("Seeding parking locations and slots...")
    locations_data = [
        {
            "id": "loc-1",
            "name": "City Center Mall Parking",
            "address": "MG Road, Commercial Plaza, Central District",
            "slots": 50,
            "rate": 40.0,
            "image": "https://images.unsplash.com/photo-1590674899484-d5640e854abe?w=800&auto=format&fit=crop&q=60"
        },
        {
            "id": "loc-2",
            "name": "Apollo Hospital Parking",
            "address": "Bannerghatta Main Rd, Healthcare District",
            "slots": 30,
            "rate": 30.0,
            "image": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?w=800&auto=format&fit=crop&q=60"
        },
        {
            "id": "loc-3",
            "name": "Cyber Tech Park Zone A",
            "address": "Electronic City Phase 1, IT Hub",
            "slots": 80,
            "rate": 50.0,
            "image": "https://images.unsplash.com/photo-1573348722427-f1d6819fdf98?w=800&auto=format&fit=crop&q=60"
        },
        {
            "id": "loc-4",
            "name": "Metro Station P1",
            "address": "Indiranagar Metro Station Interchange",
            "slots": 40,
            "rate": 20.0,
            "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&auto=format&fit=crop&q=60"
        }
    ]

    for loc in locations_data:
        pl = ParkingLocation(
            location_id=loc["id"],
            location_name=loc["name"],
            address=loc["address"],
            total_slots=loc["slots"],
            hourly_rate=loc["rate"],
            image_url=loc["image"]
        )
        db.add(pl)

        # Generate slots
        for s in range(1, loc["slots"] + 1):
            slot_type = "Regular"
            if s <= 4:
                slot_type = "EV Charging"
            elif s <= 8:
                slot_type = "Accessible"

            # Random status for demo realistic look (60% available, 30% occupied, 10% reserved)
            rand_val = random.random()
            if rand_val < 0.65:
                status = "Available"
            elif rand_val < 0.90:
                status = "Occupied"
            else:
                status = "Reserved"

            slot = ParkingSlot(
                slot_id=f"{loc['id']}-S{s:02d}",
                location_id=loc["id"],
                slot_number=f"P-{s:02d}",
                slot_type=slot_type,
                status=status
            )
            db.add(slot)

    db.commit()

    # Create one initial sample confirmed booking with QR ticket
    sample_booking = Booking(
        booking_id="BK-2026-DEMO01",
        user_id="user-001",
        slot_id="loc-1-S05",
        vehicle_number="KA-01-MJ-5566",
        start_time=datetime.utcnow() + timedelta(hours=1),
        end_time=datetime.utcnow() + timedelta(hours=3),
        booking_status="Confirmed"
    )
    db.add(sample_booking)

    sample_payment = Payment(
        payment_id="PAY-DEMO01",
        booking_id="BK-2026-DEMO01",
        amount=80.0,
        payment_method="UPI",
        payment_status="Successful"
    )
    db.add(sample_payment)

    ticket_data = json.dumps({
        "booking_id": "BK-2026-DEMO01",
        "location": "City Center Mall Parking",
        "slot": "P-05",
        "vehicle": "KA-01-MJ-5566",
        "valid_until": (datetime.utcnow() + timedelta(hours=3)).isoformat()
    })

    sample_ticket = QRTicket(
        ticket_id="TKT-DEMO01",
        booking_id="BK-2026-DEMO01",
        qr_code_data=ticket_data,
        ticket_status="Active"
    )
    db.add(sample_ticket)

    # Load history if CSV exists
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historical_parking_data.csv")
    if os.path.exists(csv_path):
        print("Importing sample historical records into database...")
        df = pd.read_csv(csv_path)
        # Take latest 500 records to keep DB fast
        recent_records = df.tail(500)
        for _, r in recent_records.iterrows():
            rec = ParkingHistory(
                location_id=r["location_id"],
                timestamp=datetime.fromisoformat(str(r["timestamp"])),
                total_slots=int(r["total_slots"]),
                occupied_slots=int(r["occupied_slots"]),
                available_slots=int(r["available_slots"])
            )
            db.add(rec)

    db.commit()
    db.close()
    print("Database seeded successfully with locations, slots, demo booking, and historical data!")

if __name__ == "__main__":
    seed()
