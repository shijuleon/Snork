from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from datetime import datetime

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	pwdhash = db.Column(db.String(80))
	email = db.Column(db.String(60), unique=True)
	firstname = db.Column(db.String(60))
	lastname = db.Column(db.String(60))
	acc_created = db.Column(db.String, default=datetime.now().strftime("%A, %B %d, %Y, %H:%M"))

	def is_authenticated(self):
		return True
	
	def is_active(self):
		return True

	def is_anonymous(self):
		return False
	
	def get_id(self):
		return unicode(self.id)	
	
	def __repr__(self):
		return '<User %r>' % self.username

class Content(db.Model):
	__tablename__ = 'content'
	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.Text)
	author = db.Column(db.String)
	pub_dtime = db.Column(db.Integer, default=datetime.now().strftime("%A, %B %d, %Y, %H:%M"))