import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Channel
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def init_db():
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                is_admin=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Admin user created with ID: {admin.id}")
        else:
            print("Admin user already exists")

        # Check if SDR user exists
        sdr = db.query(User).filter(User.email == "sdr@example.com").first()
        if not sdr:
            print("Creating SDR user...")
            sdr = User(
                email="sdr@example.com",
                hashed_password=get_password_hash("sdr123"),
                full_name="SDR User",
                is_admin=False
            )
            db.add(sdr)
            db.commit()
            db.refresh(sdr)
            print(f"SDR user created with ID: {sdr.id}")
        else:
            print("SDR user already exists")

        # Create channels if they don't exist
        channels = ["Twitter", "LinkedIn", "Instagram", "Facebook", "Email"]
        for channel_name in channels:
            channel = db.query(Channel).filter(Channel.name == channel_name).first()
            if not channel:
                print(f"Creating channel: {channel_name}")
                channel = Channel(
                    name=channel_name,
                    description=f"{channel_name} prospecting channel"
                )
                db.add(channel)
                db.commit()
                db.refresh(channel)
                print(f"Channel created with ID: {channel.id}")
            else:
                print(f"Channel {channel_name} already exists")

        # Assign channels to SDR
        if sdr:
            for channel_name in channels:
                channel = db.query(Channel).filter(Channel.name == channel_name).first()
                if channel and channel not in sdr.channels:
                    print(f"Assigning channel {channel_name} to SDR")
                    sdr.channels.append(channel)
            
            db.commit()
            print("Channels assigned to SDR")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(init_db())
    print("Database initialized successfully")
