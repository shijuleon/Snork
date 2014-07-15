from app import app, db
from models import User
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, validators, TextAreaField, PasswordField, ValidationError
from werkzeug.security import check_password_hash
import re

#Registration validation functions
def check_username_avail(form, field):
	taken = User.query.filter_by(username=form.username.data).first()
	if taken:
		raise ValidationError("Sorry, this username is already registered.")

def check_username_chars(form, field):	
	contains_space = False
	if re.search(r'[\s]', form.username.data):
		contains_space = True
	if contains_space:
		raise ValidationError("Your username can't contain spaces.")

def check_username_len(form, field):
	if len(form.username.data) > 32:
		raise ValidationError("Your username is too long.")

def check_email_avail(form, field):
	taken = User.query.filter_by(email=form.email.data).first()
	if taken:
		raise ValidationError("Sorry, this email is already registered.")

#Login validation functions
def check_username(form, field):
	check = User.query.filter_by(username=form.username.data).first()
	if not check:
		raise ValidationError("The username you entered is not correct.")

def check_password(form, field):
	user = User.query.filter_by(username=form.username.data).first()
	if user != None:
		password = user.pwdhash
		check = check_password_hash(password, form.password.data)
		if not check:
			raise ValidationError("The password you entered is not correct.")

#Admin validation functions
def check_admin_username(form, field):
	pass

def check_admin_password(form, field):
	pass

def check_comment(form, field):
	if len(form.comment.data) < 1:
		raise ValidationError("Please enter a comment")

class SignupUser(Form):
	username = TextField('Username', [validators.required("Please enter an username: "), check_username_avail, check_username_chars, check_username_len])
	password = PasswordField('Password', [validators.required("Please enter a password: ")])
	email =	TextField('Email', [validators.required("Please enter your email"), validators.Email(), check_email_avail])
	name = TextField('Name (optional)')
	recaptcha = RecaptchaField()

class LoginUser(Form):
	username = TextField('Username', [validators.required("Please enter your username: "), check_username])
	password = PasswordField('Password', [validators.required("Please enter your password"), check_password])

class LoginAdmin(Form):
	username = TextField('Username', [validators.required("Please enter your username: "), check_admin_username])
	password = PasswordField('Password', [validators.required("Please enter your password"), check_admin_password])

class Dashboard(Form):
	update = TextAreaField("What's up?", [validators.required("Please enter some text.")])
	search = TextField("What's up?")
	comment = TextField("Comment", [validators.required("Please enter a comment")])

class EditProfile(Form):
	website = TextField('Website')
	interests = TextField('Your interests')
	contact = TextField('How should someone contact you?')
	bio = TextField('Something about you')
	dp = TextField('Profile picture')