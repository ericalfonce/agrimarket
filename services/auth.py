from flask import Blueprint, request, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from services.db import get_db
import uuid
from datetime import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth')

# ---------------- Register ----------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']  # farmer, buyer

        hashed_password = generate_password_hash(password)

        user_id = str(uuid.uuid4())
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (id, name, phone, password_hash, role, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, name, phone, hashed_password, role, 'active', datetime.now()))
        conn.commit()
        cur.close()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

# ---------------- Login ----------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, phone, password_hash, role FROM users WHERE phone=%s", (phone,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session.clear()
            session['user_id'] = user[0]
            session['role'] = user[4]

            if user[4] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[4] == 'farmer':
                return redirect(url_for('products'))
            elif user[4] == 'buyer':
                return redirect(url_for('products'))
        else:
            return render_template('login.html', error="Invalid phone or password")

    return render_template('login.html')

# ---------------- Logout ----------------
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
