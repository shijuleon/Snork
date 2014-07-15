from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from datetime import datetime
import flask.ext.whooshalchemy as whooshalchemy

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	pwdhash = db.Column(db.String(80))
	email = db.Column(db.String(60), unique=True)
	name = db.Column(db.String(60))
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
	__searchable__ = ['status', 'author']
	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.Text)
	author = db.Column(db.String)
	pub_dtime = db.Column(db.Integer, default=datetime.now().strftime("%A, %B %d, %Y, %H:%M"))

class Comment(db.Model):
	__tablename__ = 'comments'
	__searchable__ = ['comment']
	id = db.Column(db.Integer, primary_key=True)
	comment = db.Column(db.String)
	post_id = db.Column(db.Integer)
	author_id = db.Column(db.Integer)
	pub_dtime = db.Column(db.Integer, default=datetime.now().strftime("%A, %B %d, %Y, %H:%M"))

class Profile(db.Model):
	__tablename__ = 'profile'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String)
	website = db.Column(db.String)
	interests = db.Column(db.Text)
	contact = db.Column(db.String)
	bio = db.Column(db.Text)
	dp = db.Column(db.String)

whooshalchemy.whoosh_index(app, Content)
whooshalchemy.whoosh_index(app, Comment)