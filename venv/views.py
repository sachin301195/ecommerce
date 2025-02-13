from flask import Flask, Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Product
from . import db
import base64, stripe
from flask_mail import Message

views = Blueprint('views', __name__)


# Stripe keys (replace with your test keys from the Stripe dashboard)
stripe.api_key = "sk_test_51Qn2rWFgyYm4yVkmBtMlQaHX15ylG21xlakAQMD3PVzRyfwCUrPDYgeX6hMMNLPOpp2NEpofOhsL7uKPD2kcjTub00ztmqGY4P"  # Secret key
STRIPE_PUBLIC_KEY = "pk_test_51Qn2rWFgyYm4yVkm7hS6e8NLaE5J0SmtrynaJj3UdlzDgUWsaXdraiCK2fqo7rgsdVoNKDSFn16KUxTMwrAUlliN00nh2jXYMb"  # Publishable key

@views.route('/')
def home():
    products = Product.query.all()  # Fetch all products from the database
    return render_template("home.html", user=current_user, products=products)

@views.route('/search')
def search():
    query = request.args.get('query')
    products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    return render_template('home.html', products=products)

@views.route('/category/<category>')
def category(category):
    products = Product.query.filter(Product.categories.ilike(f"%{category}%")).all()
    return render_template('home.html', products=products)

@views.route('/about')
def about():
    return render_template('about.html')

# Flask route for cart functionality
# Flask route for cart functionality
@views.route('/cart', methods=['GET'])
def view_cart():
    """View the cart with product details fetched from the database."""
    cart = session.get('cart', [])  # Ensure cart is initialized as a list
    if not isinstance(cart, list):
        session['cart'] = []
        session.modified = True

    product_ids = [item['id'] for item in cart if isinstance(item, dict)]  # Ensure correct format
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    # Convert image data to base64 (for proper rendering in HTML)
    for product in products:
        if product.image_data:
            product.image_data = base64.b64encode(product.image_data).decode('utf-8')

    # Attach quantity to each product
    for product in products:
        product.quantity = next((item['quantity'] for item in cart if isinstance(item, dict) and 'id' in item and item['id'] == product.id), 1)


    # Calculate total price
    total_price = sum(product.unit_price * product.quantity for product in products)

    return render_template('cart.html', products=products, cart=cart, total_price=total_price)

# Add to Cart
@views.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add a product to the shopping cart, ensuring the correct data format."""
    product = Product.query.get_or_404(product_id)

    if 'cart' not in session or not isinstance(session['cart'], list):
        session['cart'] = []  # Reset cart if corrupted

    # Check if product already exists in the cart
    for item in session['cart']:
        if isinstance(item, dict) and item['id'] == product.id:
            item['quantity'] += 1
            flash(f"{product.name} quantity updated in the cart.", "success")
            break
    else:
        session['cart'].append({'id': product.id, 'quantity': 1})  # Store as dict
        flash(f"{product.name} added to the cart!", "success")

    session.modified = True  # Save session changes

    # Stay on the same page after adding the item
    return redirect(request.referrer or url_for('views.home'))

# Remove from Cart
@views.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Remove a product from the cart."""
    cart = session.get('cart', [])

    session['cart'] = [item for item in cart if isinstance(item, dict) and item['id'] != product_id]
    session.modified = True

    flash("Product removed from the cart.", "success")
    return redirect(url_for('views.view_cart'))

@views.route('/cart/update/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    """Update the quantity of a product in the shopping cart."""
    cart = session.get('cart', [])

    for item in cart:
        if item['id'] == product_id:
            new_quantity = int(request.form.get('quantity', 1))
            item['quantity'] = max(1, new_quantity)  # Ensure at least 1
            flash(f"Quantity updated to {item['quantity']}.", 'success')
            break

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('views.view_cart'))

@views.route('/contact')
def contact():
    return render_template('contact.html')

@views.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Here, you can handle the form data, e.g., save to a database or send an email
    print(f"New contact form submission:\nName: {name}\nEmail: {email}\nMessage: {message}")

    flash("Your message has been sent successfully!", "success")
    return redirect(url_for('views.contact'))

@views.route('/checkout', methods=['POST'])
def checkout():
    try:
        # Get the total price from the submitted form
        total_price = float(request.form.get('total_price', 0))

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'cad',
                        'product_data': {
                            'name': 'Cart Total Payment',
                        },
                        'unit_amount': int(total_price * 100),  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )

        # Redirect to Stripe payment page
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('views.view_cart'))

@views.route('/success')
def success():
    # Clear the cart
    session['cart'] = []
    session.modified = True

    # Render a success page with redirection to the home page
    return render_template('success.html')

@views.route('/cancel')
def cancel():
    # Render a cancel page with redirection to the cart
    return render_template('cancel.html')
