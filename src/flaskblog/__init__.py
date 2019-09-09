from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Init App
app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = 'df7b0f856d91890dc122de81bed9e25e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login before accesing your profile!'
login_manager.login_message_category = 'danger'

from flaskblog import routes