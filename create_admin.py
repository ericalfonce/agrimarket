import psycopg2
import uuid
from werkzeug.security import generate_password_hash
from config import Config

def create_admin(phone, password, name="Admin User"):
    try:
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT
        )
        cur = conn.cursor()

        # Generate unique ID and hash password
        admin_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)

        # Insert admin user
        cur.execute("""
            INSERT INTO users (id, name, phone, password_hash, role)
            VALUES (%s, %s, %s, %s, 'admin')
        """, (admin_id, name, phone, hashed_password))

        conn.commit()
        print(f"Admin '{name}' created successfully with phone: {phone}")

    except Exception as e:
        print("Error creating admin:", e)

    finally:
        cur.close() # type: ignore
        conn.close() # type: ignore

if __name__ == "__main__":
    # Replace with your desired admin credentials
    create_admin("0748348996", "FavAdmin!", "FavAdmin")
