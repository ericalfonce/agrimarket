import uuid
import psycopg2
from werkzeug.security import generate_password_hash
from config import Config  # make sure Config has DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def create_admin(phone, password):
    hashed_password = generate_password_hash(password)
    admin_id = str(uuid.uuid4())

    conn = psycopg2.connect(
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )
    cur = conn.cursor()

    # Insert admin into users table
    cur.execute("""
        INSERT INTO users (id, phone, password_hash, role)
        VALUES (%s, %s, %s, 'admin')
        """, (admin_id, phone, hashed_password))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Admin created successfully with phone {phone}")

# Example usage
create_admin("0748348996", "FavAdmin!")
