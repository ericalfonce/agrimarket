from flask import Flask, render_template, redirect, url_for, session
from services.auth import auth 
from services.db import get_db
from services.orders import orders_bp
from flask import request, session, redirect, url_for
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from services.db import get_db
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change to a secure key
app.register_blueprint(orders_bp)
app.register_blueprint(auth)
# -----------------------
# Landing Page
# -----------------------
@app.route('/')
def landing():
    return render_template('landing.html')

# -----------------------
# About Page
# -----------------------
@app.route('/about')
def about():
    return render_template('about.html')

# -----------------------
# Contact Page
# -----------------------
@app.route('/contact')
def contact():
    return render_template('contact.html')

# -----------------------
# Home/Dashboard Redirect after login
# -----------------------
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    role = session.get('role')

    if role == 'admin':
        return redirect(url_for('manage_users'))  # Admin dashboard
    elif role == 'farmer':
        return redirect(url_for('products'))  # Farmer dashboard
    elif role == 'buyer':
        return redirect(url_for('products'))  # Buyer sees products
    else:
        return redirect(url_for('landing'))

# -----------------------
# Admin Manage Users
# -----------------------

# Dummy routes for URLs in templates

@app.route('/admin/manage-users')
def manage_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone, role FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('admin_users.html', users=users)
# Edit user
@app.route('/admin/edit-user/<user_id>')
def edit_user(user_id):
    # Placeholder page for editing user
    return f"Edit user {user_id} page coming soon"

# Delete user
@app.route('/admin/delete-user/<user_id>')
def delete_user(user_id):
    # Placeholder page for deleting user
    return f"Delete user {user_id} page coming soon"


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor()

    # Fetch users
    cur.execute("SELECT id, name, phone, role FROM users")
    users = cur.fetchall()

    # Fetch products
    cur.execute("SELECT id, name, price, quantity FROM products")
    products = cur.fetchall()
    cur.close()

    return render_template('admin_dashboard.html', users=users, products=products)


# Edit product
@app.route('/admin/edit-product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        quantity = request.form.get('quantity')

        cur.execute("""
            UPDATE products
            SET name = %s, price = %s, quantity = %s
            WHERE id = %s
        """, (name, price, quantity, product_id))
        conn.commit()
        cur.close()
        return redirect(url_for('admin_dashboard'))

    cur.execute("SELECT id, name, price, quantity FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()
    return render_template('edit_product.html', product=product)


# Delete product
@app.route('/admin/delete-product/<product_id>')
def delete_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cur.close()
    return redirect(url_for('admin_dashboard'))



# ------------------ Products & Cart Routes ------------------

# Products page (shows all products; farmers can add, buyers can add to cart)
@app.route('/products', methods=['GET', 'POST'])
def products():
    conn = get_db()
    cur = conn.cursor()

    # Farmer adds a product
    if request.method == 'POST' and session.get('role') == 'farmer':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']
        location = request.form['location']

        cur.execute(
            "INSERT INTO products (id, name, price, quantity, location, farmer_id) VALUES (%s,%s,%s,%s,%s,%s)",
            (str(uuid.uuid4()), name, price, quantity, location, session['user_id'])
        )
        conn.commit()

    # Fetch all products
    cur.execute("SELECT id, name, price, quantity, location FROM products")
    products_list = cur.fetchall()
    cur.close()

    return render_template('products.html', products=products_list)


# Buyer adds product to cart
@app.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session or session.get('role') != 'buyer':
        return "Access denied", 403

    quantity = int(request.form.get('quantity', 1))
    conn = get_db()
    cur = conn.cursor()

    # Check if cart table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id UUID PRIMARY KEY,
            user_id UUID,
            product_id UUID,
            quantity INTEGER
        )
    """)
    conn.commit()

    # Check if this product is already in user's cart
    cur.execute(
        "SELECT id, quantity FROM cart WHERE user_id=%s AND product_id=%s",
        (session['user_id'], product_id)
    )
    item = cur.fetchone()

    if item:
        # Update quantity if already in cart
        new_qty = item[1] + quantity
        cur.execute("UPDATE cart SET quantity=%s WHERE id=%s", (new_qty, item[0]))
    else:
        # Insert new cart item
        cur.execute(
            "INSERT INTO cart (id, user_id, product_id, quantity) VALUES (%s,%s,%s,%s)",
            (str(uuid.uuid4()), session['user_id'], product_id, quantity)
        )

    conn.commit()
    cur.close()
    return redirect(url_for('orders'))


# Orders page (buyers see their cart to checkout; farmers see all orders)
@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor()

    if session.get('role') == 'buyer':
        # Buyer sees their cart
        cur.execute("""
            SELECT p.name, p.price, c.quantity
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id=%s
        """, (session['user_id'],))
        orders_list = cur.fetchall()
    else:
        # Farmer sees orders of their products
        cur.execute("""
            SELECT p.name, p.price, c.quantity, u.phone
            FROM cart c
            JOIN products p ON c.product_id = p.id
            JOIN users u ON c.user_id = u.id
            WHERE p.farmer_id=%s
        """, (session['user_id'],))
        orders_list = cur.fetchall()

    cur.close()
    return render_template('orders.html', orders=orders_list)

if __name__ == '__main__':
    app.run(debug=True)
