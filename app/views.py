from flask import Flask, render_template, session, flash, url_for, redirect, g, request
from app import app, db, login_manager
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import LoginUser, SignupUser, Dashboard, EditProfile
from models import User, Content, Comment, Profile
from werkzeug.security import generate_password_hash
import flask.ext.whooshalchemy as whooshalchemy

@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
	return User.query.get(id)
	
@app.route('/')
def index():
	if g.user.is_authenticated():
		return redirect(url_for('dashboard'))
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
		newuser = User(username=form.username.data, pwdhash=generate_password_hash(form.password.data), email=form.email.data, name=form.name.data)
		db.session.add(newuser)
		db.session.commit()
		return redirect(url_for('dashboard'))
	return render_template('signup.html', form=form)

@app.route('/profile')
@login_required
def profile():
	id = g.user.get_id()
	form = Dashboard()
	instance = db.session.query(User).filter_by(id=id).all()
	return render_template('profile.html', instance=instance, app=app, form=form)

@app.route('/profile/<int:id>')
@login_required
def showprofileid(id):
	form = Dashboard()
	instance = db.session.query(User).filter_by(id=id).all()
	return render_template('showprofile.html', instance=instance, app=app, form=form)

@app.route('/profile/<string:username>')
@login_required
def showprofilename(username):
	form = Dashboard()
	profile = db.session.query(Profile).filter_by(username=username).first()
	user = db.session.query(User).filter_by(id=g.user.get_id()).first()
	instance = db.session.query(User).filter_by(username=username).all()
	posts = db.session.query(Content).filter_by(author=username).order_by(Content.id.desc())
	return render_template('showprofile.html', instance=instance, app=app, posts=posts, user=user, form=form, profile=profile)

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
	newstatus = Content(status=form.update.data, author=author.username)
	db.session.add(newstatus)
	db.session.commit()
	return redirect(url_for('dashboard'))

@app.route('/postcomment/<int:id>', methods=['POST'])
@login_required
def postComment(id):
	form = Dashboard()
	auth_id = int(g.user.get_id())
	if form.validate_on_submit():
		return redirect(url_for('dashboard'))
	comment = Comment(comment=form.comment.data, post_id=id, author_id=auth_id)
	db.session.add(comment)
	db.session.commit()
	url = str(url_for('comments', id=id))
	return redirect(url+'#'+str(comment.id))

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
	form = Dashboard()
	return render_template('about.html', form=form)

@app.route('/dosearch', methods = ['POST'])
@login_required
def search():
    form = Dashboard()
    return redirect(url_for('search_results', query=form.search.data))

@app.route('/search/<query>')
@login_required
def search_results(query):
    results = Content.query.whoosh_search(query).all()
    form = Dashboard()
    user = db.session.query(User).filter_by(id=g.user.get_id()).first()
    return render_template('search_results.html', query = query, results = results, app=app, user=user, form=form)

@app.route('/comments/<int:id>')
@login_required
def comments(id):
	form = Dashboard()
	post = db.session.query(Content).filter_by(id=id).first()
	user = db.session.query(User).filter_by(id=g.user.get_id()).first()
	instance = db.session.query(Comment).filter_by(post_id=id)
	return render_template('showcomments.html', instance=instance, form=form, app=app, post=post, user=user, id=id)

@app.route('/deletecomment/<int:id>')
@login_required
def deletecomment(id):
	delete = db.session.query(Comment).filter_by(id=id).first()
	author = db.session.query(User).filter_by(id=g.user.get_id()).first()
	if delete.author_id == author.id:
		db.session.delete(delete)
		db.session.commit()
		flash("Comment deleted!")
	else:
		flash("You are not authorized to do that.")
	return redirect(url_for('comments', id=delete.post_id))

@app.route('/editprofile/<string:username>')
@login_required
def editprofile(username):
	user = db.session.query(User).filter_by(id=g.user.get_id()).first()
	if user.username == username:
		form = Dashboard()
		sform = EditProfile()
		profile = db.session.query(Profile).filter_by(username=username).first()
		return render_template('editprofile.html', form=form, sform=sform, username=username, profile=profile)
	else:
		flash("You are not authorized to do that.")
		return redirect(url_for('dashboard'))

@app.route('/updateprofile', methods=['POST'])
@login_required
def updateprofile():
	form = EditProfile()
	author = db.session.query(User).filter_by(id=g.user.get_id()).first()
	post = db.session.query(Profile).first()
	if post == None:
		profile = Profile(username=author.username, website=form.website.data, interests=form.interests.data, contact=form.contact.data, bio=form.bio.data, dp=form.dp.data)
		db.session.add(profile)
		db.session.commit()
		return redirect(url_for('dashboard'))
	else:
		sform = EditProfile(request.form, post)
		sform.populate_obj(post)
		db.session.add(post)	
		db.session.commit()
		flash("Your profile has been modified.")	
		return redirect(url_for('dashboard'))
	return redirect(url_for('dashboard'))