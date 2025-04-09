from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Channel

def check_db():
    db = SessionLocal()
    try:
        print("=== Users ===")
        users = db.query(User).all()
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Name: {user.full_name}, Admin: {user.is_admin}")
            if not user.is_admin:
                print("  Assigned Channels:")
                for channel in user.channels:
                    print(f"  - {channel.name}")
        
        print("\n=== Channels ===")
        channels = db.query(Channel).all()
        for channel in channels:
            print(f"ID: {channel.id}, Name: {channel.name}, Description: {channel.description}")
            print("  Assigned SDRs:")
            for sdr in channel.sdrs:
                print(f"  - {sdr.full_name} ({sdr.email})")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
    print("\nDatabase check completed")