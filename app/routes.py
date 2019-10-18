from app import app, db
from app.forms import LoginForm, AddingForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Spending
from flask import request
from werkzeug.urls import url_parse

from flask import Flask

#app = Flask(__name__)


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_spending():
    form = AddingForm()
    if form.validate_on_submit():
        spend = Spending(user_id=current_user.id, note=form.note.data, category=form.category.data, value=float(form.value.data))
        db.session.add(spend)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', title='Adding', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing'))
