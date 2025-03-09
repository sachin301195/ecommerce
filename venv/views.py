from flask import Flask, Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Product, HST, Billing, BillDetails, CompanyInfo, Inventory_OUT
from . import db
import base64, stripe
import pdfkit
from datetime import datetime,timezone
import io
from flask import send_file

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
    return render_template('home.html', products=products, user=current_user)

def save_image(base64_string):
    return base64.b64decode(base64_string)  # Convert Base64 to binary before saving

@views.route('/category/<category>')
def category(category):
    products = Product.query.filter(Product.categories.ilike(f"%{category}%")).all()
    return render_template('home.html', products=products, user=current_user)

@views.route('/about')
def about():
    return render_template('about.html', user=current_user)

# Flask route for cart functionality
@views.route('/cart', methods=['GET']) 
@login_required
def view_cart():
    cart = session.get('cart', [])  # Ensure cart is initialized as a list
    if not isinstance(cart, list):
        session['cart'] = []
        session.modified = True

    product_ids = [item['id'] for item in cart if isinstance(item, dict)]  # Ensure correct format
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    # Convert image data to base64 (for proper rendering in HTML)
    for product in products:
        if product.image_data:
            product.image_base64 = base64.b64encode(product.image_data).decode('utf-8')

    # Attach quantity to each product
    for product in products:
        product.quantity = next((item['quantity'] for item in cart if isinstance(item, dict) and 'id' in item and item['id'] == product.id), 1)

    # Calculate subtotal (before tax)
    subtotal = sum(product.unit_price * product.quantity for product in products)

    # Get user's province
    user_province = current_user.province if current_user.province else None

    # Fetch the HST value from the database based on the user's province
    hst_value = 0  # Default to 0 if province is not found
    if user_province:
        hst_entry = HST.query.filter_by(province=user_province).first()
        if hst_entry:
            hst_value = hst_entry.hst_value  # Using the correct column name

    # Calculate HST amount
    hst_amount = subtotal * (hst_value / 100)

    # Calculate total price including HST
    total_price = subtotal + hst_amount

    return render_template(
        'cart.html',
        products=products,
        cart=cart,
        subtotal=subtotal,
        hst_amount=hst_amount,
        total_price=total_price,
        user=current_user
    )

# Add to Cart
@views.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
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
@login_required
def remove_from_cart(product_id):
    """Remove a product from the cart."""
    cart = session.get('cart', [])

    session['cart'] = [item for item in cart if isinstance(item, dict) and item['id'] != product_id]
    session.modified = True

    flash("Product removed from the cart.", "success")
    return redirect(url_for('views.view_cart'))

@views.route('/cart/update/<int:product_id>', methods=['POST'])
@login_required
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
    return render_template('contact.html',user=current_user)

@views.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Here, you can handle the form data, e.g., save to a database or send an email
    print(f"New contact form submission:\nName: {name}\nEmail: {email}\nMessage: {message}")

    flash("Your message has been sent successfully!", "success")
    return redirect(url_for('views.contact'))

@views.route('/cart/buy_now/<int:product_id>', methods=['POST'])
@login_required
def buy_now(product_id):
    """Add a product to the cart and immediately redirect to the cart."""
    product = Product.query.get_or_404(product_id)

    if 'cart' not in session or not isinstance(session['cart'], list):
        session['cart'] = []  # Ensure the cart is a list

    # Check if product already exists in the cart
    for item in session['cart']:
        if isinstance(item, dict) and item['id'] == product.id:
            item['quantity'] += 1  # Increase quantity if already in cart
            break
    else:
        session['cart'].append({'id': product.id, 'quantity': 1})  # Add as a new item

    session.modified = True  # Save session changes

    # Redirect user to the cart page
    return redirect(url_for('views.view_cart'))



@views.route('/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        # Get the total price from the submitted form
        total_price = float(request.form.get('total_price', 0))
        
        if total_price <= 0:
            flash("Invalid total price.", "error")
            return redirect(url_for('views.view_cart'))
        
        # Get user's HST rate
        user_hst = HST.query.filter_by(province=current_user.province).first()
        hst_rate = user_hst.hst_value if user_hst else 0

        # Calculate HST amount based on the total price
        total_hst = total_price * (hst_rate / (100 + hst_rate))  # Extract HST from total
        subtotal = total_price - total_hst  # Get subtotal before tax
        
    
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
            success_url=url_for('views.success', bill_total=total_price, bill_hst=total_hst, bill_subtotal=subtotal, _external=True, user=current_user),
            cancel_url=url_for('views.cancel', _external=True, user=current_user),
        )
         # Store session ID to retrieve later
        session['checkout_session_id'] = checkout_session.id
        session['bill_total'] = total_price
        session['bill_hst'] = total_hst
        session['bill_subtotal'] = subtotal

        # Redirect to Stripe payment page
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('views.view_cart'))


@views.route('/success')
@login_required
def success():
    """Handle successful payment and generate an invoice"""

    session_id = session.get('checkout_session_id')
    if not session_id:
        flash("Invalid session. Try again.", "error")
        return redirect(url_for('views.view_cart'))

    checkout_session = stripe.checkout.Session.retrieve(session_id)

    if not checkout_session or checkout_session.payment_status != "paid":
        flash("Payment not completed.", "error")
        return redirect(url_for('views.view_cart'))

    # Retrieve cart details from session
    cart = session.get('cart', [])  # Ensure cart has data
    total_price = session.get('bill_total', 0)
    total_hst = session.get('bill_hst', 0)
    subtotal = session.get('bill_subtotal', 0)

    if not cart or total_price <= 0:
        flash("Invalid order details.", "error")
        return redirect(url_for('views.view_cart'))

    # Get user's HST ID (if applicable)
    user_hst = HST.query.filter_by(province=current_user.province).first()
    hst_id = user_hst.id if user_hst else None  # Allow NULL if not found

    # Create new billing record
    new_bill = Billing(
        Date=datetime.now(timezone.utc),
        Quantity=sum(item['quantity'] for item in cart),  # Total quantity of all items
        Total_BT=subtotal,
        Total_HST=total_hst,
        Total_Net=total_price,
        Client_ID=current_user.id,
        Observations="Payment processed via Stripe",
        HST_ID=hst_id
    )
    db.session.add(new_bill)
    db.session.commit()

    print(f"✅ New Bill Created - ID: {new_bill.Billing_ID}")  # Debugging log

    # Add purchased products to BillDetails
    for item in cart:
        product = Product.query.get(item['id'])
        if product:
            bill_detail = BillDetails(
                Billing_ID=new_bill.Billing_ID,
                Product_ID=product.id,
                Price=product.unit_price,
                Quantity=item['quantity'],  # 🔹 Ensure correct quantity is stored
                Created_At=datetime.now(timezone.utc),
                Updated_At=datetime.now(timezone.utc)
            )
            db.session.add(bill_detail)
            
            # ✅ Check if the product already exists in Inventory_OUT
            inventory_out = Inventory_OUT.query.filter_by(Product_ID=product.id).first()

            if inventory_out:  # If the product already has an Inventory_OUT entry, update it
                inventory_out.QTE += item['quantity']  # Increase the quantity sold
                inventory_out.Total_Amount = inventory_out.QTE * product.unit_price
                inventory_out.Updated_At = datetime.now(timezone.utc)
                print(f"📉 Inventory_OUT updated for {product.name} - New Quantity: {inventory_out.QTE}")
            else:  # If no Inventory_OUT record exists, create a new one
                inventory_out = Inventory_OUT(
                    Date=datetime.now(timezone.utc).date(),
                    QTE=item['quantity'],
                    Total_Amount=item['quantity'] * product.unit_price,
                    Product_ID=product.id,
                    Created_At=datetime.now(timezone.utc),
                    Updated_At=datetime.now(timezone.utc)
                )
                db.session.add(inventory_out)
                print(f"📉 New Inventory_OUT entry created for {product.name} - Quantity: {item['quantity']}")



    db.session.commit()

    # Clear session data
    session.pop('bill_total', None)
    session.pop('bill_hst', None)
    session.pop('bill_subtotal', None)
    session.pop('cart', None)  # Clear the cart
    session.modified = True

    flash("Checkout successful! Your order has been placed.", "success")
    
    return redirect(url_for('views.home', user=current_user))
    

@views.route('/cancel')
@login_required
def cancel():
    # Render a cancel page with redirection to the cart
    return render_template('cancel.html',user=current_user)

@views.route('/bills')
@login_required
def user_bills():
    bills = Billing.query.filter_by(Client_ID=current_user.id).all()
    return render_template('bills.html', bills=bills, user=current_user)


@views.route('/bill/<int:bill_id>', methods=['GET'])
@login_required
def view_bill(bill_id):
    """Display the bill details with company and client information"""

    bill = Billing.query.get_or_404(bill_id)
    bill_details = BillDetails.query.filter_by(Billing_ID=bill.Billing_ID).all()

    # Fetch company details (Assuming you have a Company model)
    company = CompanyInfo.query.first()  # Fetch the first company record

    # Fetch client details
    client = User.query.get(bill.Client_ID)

    return render_template("bill.html", bill=bill, bill_details=bill_details, company=company, client=client, user=current_user)

@views.route('/bill/download/<int:bill_id>', methods=['GET'])
@login_required
def download_bill(bill_id):
    """Generate and download the bill as a PDF"""
    bill = Billing.query.get_or_404(bill_id)
    bill_details = BillDetails.query.filter_by(Billing_ID=bill.Billing_ID).all()

    # Fetch company details
    company = CompanyInfo.query.first()  # ✅ Ensure company info is retrieved

    # Fetch client details
    client = User.query.get(bill.Client_ID)

    if not company:
        flash("Company information not found!", "error")
        return redirect(url_for('views.user_bills'))

    # Render the HTML template with data
    rendered = render_template("bill_pdf.html", 
                               bill=bill, 
                               bill_details=bill_details, 
                               company=company, 
                               client=client)
    
    # Convert HTML to PDF
    pdf = pdfkit.from_string(rendered, False)
    
    response = send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"invoice_{bill.Billing_ID}.pdf"
    )
    
    return response


@views.route('/orders')
@login_required
def orders():
    """Display all the orders of the logged-in user"""
    bills = Billing.query.filter_by(Client_ID=current_user.id).order_by(Billing.Date.desc()).all()
    return render_template('orders.html', bills=bills, user=current_user)