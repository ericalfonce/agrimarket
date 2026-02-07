# services/orders.py
from flask import Blueprint, render_template, session, redirect, url_for
from services.db import get_db

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor()

    role = session.get('role')
    user_id = session.get('user_id')

    if role == 'farmer':
        # Farmers see orders for their products
        cur.execute("""
            SELECT o.id, p.name, o.quantity, o.total_price, u.name 
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN users u ON o.buyer_id = u.id
            WHERE p.farmer_id = %s
        """, (user_id,))
    elif role == 'buyer':
        # Buyers see their own orders
        cur.execute("""
            SELECT o.id, p.name, o.quantity, o.total_price, u.name 
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN users u ON p.farmer_id = u.id
            WHERE o.buyer_id = %s
        """, (user_id,))
    else:
        cur.close()
        return "Access Denied"

    orders = cur.fetchall()
    cur.close()
    return render_template('orders.html', orders=orders)
