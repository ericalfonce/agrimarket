from flask import Blueprint, session, redirect, url_for, render_template, request
from .db import get_db

admin_bp = Blueprint('admin', __name__)

# View/manage users
@admin_bp.route('/manage-users', methods=['GET', 'POST'])
def manage_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return "Access denied", 403

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')

        if action == 'delete':
            cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        elif action == 'toggle_status':
            cur.execute(
                "UPDATE users SET status = CASE WHEN status='active' THEN 'inactive' ELSE 'active' END WHERE id=%s",
                (user_id,)
            )
        conn.commit()

    cur.execute("SELECT id, name, phone, role, status FROM users")
    users = cur.fetchall()
    cur.close()

    return render_template('admin_users.html', users=users)


# View/manage products
@admin_bp.route('/manage-products', methods=['GET', 'POST'])
def manage_products():
    if 'user_id' not in session or session.get('role') != 'admin':
        return "Access denied", 403

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        conn.commit()

    cur.execute("SELECT id, name, price, quantity, location FROM products")
    products = cur.fetchall()
    cur.close()

    return render_template('admin_products.html', products=products)
