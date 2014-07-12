from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object('app.config')
db = SQLAlchemy(app)

from flask.ext.login import LoginManager, login_user


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "/login"

from app import views

db.create_all()