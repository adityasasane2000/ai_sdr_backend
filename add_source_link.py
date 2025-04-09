from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

def add_source_link_column():
    # Connect to the database
    connection = engine.connect()
    
    try:
        # Check if the column already exists
        result = connection.execute(text("PRAGMA table_info(prospects)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'source_link' not in columns:
            print("Adding source_link column to prospects table...")
            connection.execute(text("ALTER TABLE prospects ADD COLUMN source_link TEXT"))
            print("Column added successfully!")
        else:
            print("source_link column already exists in prospects table.")
    except Exception as e:
        print(f"Error adding column: {str(e)}")
    finally:
        connection.close()

if __name__ == "__main__":
    add_source_link_column()
