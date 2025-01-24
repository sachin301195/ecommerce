from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)            



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('FirstName')
        last_name = request.form.get('LastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        phone_number = request.form.get('PhoneNumber')
        email = request.form.get('email')
        address = request.form.get('Address')
        postal_code = request.form.get('PostalCode')
        city = request.form.get('City')
        province = request.form.get('Province')
        country = request.form.get('Country')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(address) < 2:
            flash('Address must be greater than 1 character.', category='error')
        elif len(postal_code) < 2:
            flash('Postal Code must be greater than 1 character.', category='error')
        elif len(city) < 2:
            flash('City name must be greater than 1 character.', category='error')
        elif len(province) < 2:
            flash('Province name must be greater than 1 character.', category='error')
        elif len(country) < 2:
            flash('Country name must be greater than 1 character.', category='error')    
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'),last_name=last_name, phone_number=phone_number, address=address,postal_code=postal_code,city=city,province=province,country=country)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # First, let's fetch the current user's information from the database
    user = current_user  # Using Flask-Login's current_user, it's already the authenticated user
    
    if request.method == 'POST':
        # When the user submits the form, we update their information
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        postal_code = request.form['postal_code']
        city = request.form['city']
        province = request.form['province']
        country = request.form['country']
        
        # Update the current user's details in the database
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.address = address
        user.postal_code = postal_code
        user.city = city
        user.province = province
        user.country = country
        
        db.session.commit()

        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.profile'))  # Redirect to the profile page after updating

    # GET request: Display the current user's information in the form
    return render_template('profile.html', user=user)

        
    

