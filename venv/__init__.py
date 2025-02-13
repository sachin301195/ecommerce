from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
from flask_login import LoginManager
import base64

db = SQLAlchemy()
DB_NAME = "database.db"
    
def create_app():
    app = Flask(__name__)
    app.jinja_env.filters['b64encode'] = b64encode
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs' # Used for session management
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
    migrate = Migrate(app, db)
    

    from .views import views
    from .auth import auth
    from .cpanel import cpanel
    
  
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(cpanel, url_prefix='/')
    
    
    from .models import User
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    @app.context_processor
    def inject_user():
        return {'user': {'is_authenticated': session.get('admin_authenticated', False)}}    
    
    return app


from .models import AuthenticationAdmin
'''
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
'''
        
def create_database(app):
    if not path.exists(DB_NAME):  # Use the correct path for `DB_NAME`
        db.create_all(app=app)
        print('Created Database!')
        
def create_admin_user(app):
    with app.app_context():
        if not AuthenticationAdmin.query.filter_by(login="admin").first():
            new_admin = AuthenticationAdmin(
                login="admin",
                password=generate_password_hash("adminpassword", method="pbkdf2:sha256")
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")

def b64encode(value):
    if value is not None:
        return base64.b64encode(value).decode('utf-8')
    return None
   

