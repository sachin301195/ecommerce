from flask import Flask, render_template, redirect, url_for, flash, Blueprint, request, session
from .models import User, HST, Product, AuthenticationAdmin, CompanyInfo
from . import db
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import base64

cpanel = Blueprint('cpanel', __name__)

# Admin Login
@cpanel.route('/cpanel/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        # Check admin credentials
        admin = AuthenticationAdmin.query.filter_by(login=login).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_authenticated'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('cpanel.cpanel_admin'))
        else:
            flash('Invalid login credentials.', 'danger')

    return render_template('admin_login.html')


# Admin Logout
@cpanel.route('/cpanel/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('cpanel.admin_login'))

# Terminate Admin Session on Non-Admin Page Access
@cpanel.before_app_request
def terminate_admin_session():
    non_admin_endpoints = ['views.home', 'views.view_cart']
    if request.endpoint in non_admin_endpoints and session.get('admin_authenticated'):
        session.pop('admin_authenticated', None)
        flash('Admin session terminated.', 'warning')


# Admin Dashboard
@cpanel.route('/cpanel')
def cpanel_admin():
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    
    # Fetch data for the admin dashboard
    users = User.query.all()  # Fetch all users
    hst_rates = HST.query.all()  # ✅ Fetch HST rates
    products = Product.query.all()  # Fetch all products
    company_info = CompanyInfo.query.first()
    
     # ✅ Ensure product images are base64 encoded
    for product in products:
        if product.image_data and not isinstance(product.image_data, str):  
            product.image_data = base64.b64encode(product.image_data).decode('utf-8')
    
    return render_template("cpanel.html", users=users, user={'is_authenticated': session.get('admin_authenticated')}, hst_rates=hst_rates, products=products, company_info=company_info)

# Add Product
@cpanel.route('/cpanel/products/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        unit_price = request.form.get('unit_price', type=float)
        qte_max = request.form.get('qte_max', type=int)
        qte_refill = request.form.get('qte_refill', type=int)
        qte_alert = request.form.get('qte_alert', type=int)
        reference = request.form.get('reference')
        categories = request.form.get('categories')
        description = request.form.get('description')
        
        # Handle image upload
        image = request.files.get('image')
        image_data = image.read() if image else None

        # Add the product to the database
        new_product = Product(
            name=name,
            unit_price=unit_price,
            qte_max=qte_max,
            qte_refill=qte_refill,
            qte_alert=qte_alert,
            reference=reference,
            categories=categories,
            description=description,
            image_data=image_data
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('cpanel.cpanel_admin') + '#products')

    return render_template('add_product.html', user=current_user)

# Edit and Delete Products (as implemented in your code)
@cpanel.route('/cpanel/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.unit_price = float(request.form['unit_price'])
        product.qte_max = int(request.form['qte_max'])
        product.qte_refill = int(request.form['qte_refill'])
        product.qte_alert = int(request.form['qte_alert'])
        product.reference = request.form['reference']

        # Handle optional image update
        image_file = request.files['image']
        if image_file:
            product.image = image_file.read()  # Update binary image data

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('cpanel.cpanel_admin') + '#products')

    return render_template('edit_product.html', product=product, user=current_user)


@cpanel.route('/cpanel/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')

    return redirect(url_for('cpanel.cpanel_admin') + '#products')

# CRUD for Users (already implemented)

@cpanel.route('/cpanel/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    return redirect(url_for('cpanel.cpanel_admin'))

@cpanel.route('/cpanel/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        try:
            user.first_name = request.form['first_name']
            user.last_name = request.form['last_name']
            user.email = request.form['email']
            user.phone_number = request.form['phone_number']
            user.address = request.form['address']
            user.postal_code = request.form['postal_code']
            user.city = request.form['city']
            user.province = request.form['province']
            user.country = request.form['country']
            
            db.session.commit()
            flash('User information updated successfully!', 'success')
            return redirect(url_for('cpanel.cpanel_admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')

    return render_template('edit_user.html', user=user)

def get_hst_for_user(user):
    """Fetch the HST value for a user based on their province."""
    hst_entry = HST.query.filter_by(province=user.province).first()
    return hst_entry.hst_value if hst_entry else 0  # Default to 0 if no entry exists

@cpanel.route('/cpanel/hst/add', methods=['GET', 'POST'])
def add_hst():
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    if request.method == 'POST':
        province = request.form['province']
        hst_value = float(request.form['rate'])  # Match the field name `hst_value`

        # Use `hst_value` instead of `rate`
        new_hst = HST(province=province, hst_value=hst_value)
        db.session.add(new_hst)
        db.session.commit()
        
        flash(f"HST rate for {province} added successfully!", "success")
        return redirect(url_for('cpanel.cpanel_admin') + '#hst')

    return render_template('hst_form.html', action="Add")

# ✅ Edit HST Route
@cpanel.route('/cpanel/hst/edit/<int:hst_id>', methods=['GET', 'POST'])
def edit_hst(hst_id):
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    hst = HST.query.get_or_404(hst_id)

    if request.method == 'POST':
        hst.province = request.form['province']
        hst.rate = float(request.form['rate'])

        db.session.commit()
        flash(f"HST rate for {hst.province} updated!", "success")
        return redirect(url_for('cpanel.cpanel_admin') + '#hst')

    return render_template('hst_form.html', action="Edit", hst=hst)

# ✅ Delete HST Route
@cpanel.route('/cpanel/hst/delete/<int:hst_id>', methods=['POST'])
def delete_hst(hst_id):
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))
    hst = HST.query.get_or_404(hst_id)
    db.session.delete(hst)
    db.session.commit()

    flash(f"HST rate for {hst.province} deleted!", "success")
    return redirect(url_for('cpanel.cpanel_admin') + '#hst')

@cpanel.route('/cpanel/company_info', methods=['POST'])
def update_company_info():
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))

    company_info = CompanyInfo.query.first()
    if not company_info:
        company_info = CompanyInfo()

    # Update company information
    company_info.name = request.form['name']
    company_info.email = request.form['email']
    company_info.phone = request.form['phone']
    company_info.address = request.form['address']
    company_info.website = request.form.get('website')

    db.session.add(company_info)
    db.session.commit()

    flash('Company information updated successfully!', 'success')
    return redirect(url_for('cpanel.cpanel_admin') + '#company-info')

@cpanel.route('/cpanel/company_info/edit', methods=['GET', 'POST'])
def edit_company_info():
    if not session.get('admin_authenticated'):
        flash('You must be logged in as an admin to access this page.', 'danger')
        return redirect(url_for('cpanel.admin_login'))

    company_info = CompanyInfo.query.first()
    if request.method == 'POST':
        if not company_info:
            company_info = CompanyInfo()  # Create a new record if it doesn't exist

        # Update fields
        company_info.name = request.form['name']
        company_info.email = request.form['email']
        company_info.phone = request.form['phone']
        company_info.address = request.form['address']
        company_info.website = request.form.get('website')

        db.session.add(company_info)
        db.session.commit()

        flash('Company information updated successfully!', 'success')
        return redirect(url_for('cpanel.cpanel_admin') + '#company-info')

    return render_template('edit_company_info.html', company_info=company_info)



