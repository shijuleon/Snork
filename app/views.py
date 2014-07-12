from flask import Flask, render_template, session, flash, url_for, redirect, g, Markup
from app import app, db
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import login_manager
from forms import LoginUser, SignupUser, Dashboard
from models import User, Content
from werkzeug.security import generate_password_hash

@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
	return User.query.get(id)
	
@app.route('/')
def index():
	if session.get('user_logged_in'):
		redirect(url_for('dashboard'))
	return render_template('index.html', app=app)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('dashboard'))
	form = LoginUser()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		login_user(user)
		return redirect(url_for('dashboard'))	
	return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupUser()
	if form.validate_on_submit():
		newuser = User(username=form.username.data, pwdhash=generate_password_hash(form.password.data), email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data)
		db.session.add(newuser)
		db.session.commit()
		redirect(url_for('dashboard'))
	return render_template('signup.html', form=form)

@app.route('/profile')
@login_required
def profile():
	id = g.user.get_id()
	instance = db.session.query(User).filter_by(id=id).all()
	return render_template('profile.html', instance=instance, app=app)

@app.route('/profile/<int:id>')
def showprofileid(id):
	instance = db.session.query(User).filter_by(id=id).all()
	return render_template('showprofile.html', instance=instance, app=app)

@app.route('/profile/<string:username>')
def showprofilename(username):
	user = db.session.query(User).filter_by(id=g.user.get_id()).first()
	instance = db.session.query(User).filter_by(username=username).all()
	posts = db.session.query(Content).filter_by(author=username).all()
	return render_template('showprofile.html', instance=instance, app=app, posts=posts, user=user)

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
	form = Dashboard()
	user = db.session.query(User).filter_by(id=g.user.get_id()).first()
	instance = db.session.query(Content).order_by(Content.id.desc())
	return render_template('dashboard.html', form=form, instance=instance, user=user, app=app)

@app.route('/postupdate', methods=['POST'])
@login_required
def postUpdate():
	author = db.session.query(User).filter_by(id=g.user.get_id()).first()
	form = Dashboard()
	if form.validate_on_submit():
		newstatus = Content(status=form.update.data, author=author.username)
		db.session.add(newstatus)
		db.session.commit()
	return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
@login_required
def deletepost(id):
	delete = db.session.query(Content).filter_by(id=id).first()
	author = db.session.query(User).filter_by(id=g.user.get_id()).first()
	if delete.author == author.username:
		db.session.delete(delete)
		db.session.commit()
		flash("Post deleted!")
	else:
		flash("You are not authorized to do that.")
	return redirect(url_for('dashboard'))

@app.route('/about')
def about():
	return render_template('about.html')