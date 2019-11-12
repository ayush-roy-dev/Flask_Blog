from flask import Blueprint, render_template, redirect, url_for, flash, request
from flaskblog import db, bcrypt
from flaskblog.users.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.models import User, Post
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        passwd = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=passwd)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=False)
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('main.home'))
    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Succesfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Invalid email or password!', 'danger ')
    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account/<int:user_id>", methods=['GET', 'POST'])
@login_required
def account(user_id):
    user = User.query.get(user_id)
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    form = UpdateAccountForm()
    if current_user.id == user.id:
        if form.validate_on_submit():
            if form.picture.data:
                picture_fn_name = save_picture(form.picture.data)
                current_user.image_file = picture_fn_name
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('users.account', user_id=current_user.id))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
    return render_template("account.html", title="Account", image_file=image_file, form=form, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expred token!', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        passwd = bcrypt.generate_password_hash(form.password.data)
        user.password = passwd
        db.session.commit()
        flash('You password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template("reset_password.html", title="Reset Password", form=form)
