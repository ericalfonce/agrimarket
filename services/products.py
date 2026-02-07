from flask import Blueprint, request, redirect, url_for, session, render_template
from .db import get_db

products_bp = Blueprint('products', __name__)

# Farmer adds product
@products_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session.get('role') != 'farmer':
        return "Access denied", 403

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']
        location = request.form['location']

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (name, price, quantity, location, farmer_id) VALUES (%s,%s,%s,%s,%s)",
            (name, price, quantity, location, session['user_id'])
        )
        conn.commit()
        cur.close()
        return redirect(url_for('products.add_product'))

    return render_template('products.html', action="add")


# Buyer views products
@products_bp.route('/view-products')
def view_products():
    if 'user_id' not in session or session.get('role') != 'buyer':
        return "Access denied", 403

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, price, quantity, location FROM products")
    products = cur.fetchall()
    cur.close()

    return render_template('products.html', products=products, action="view")
