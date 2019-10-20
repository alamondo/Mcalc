from app import app, db
from app.forms import LoginForm, AddingForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Spending
from datetime import datetime
from sqlalchemy import extract
from copy import deepcopy
from flask import request
from werkzeug.urls import url_parse

from flask import Flask

#app = Flask(__name__)


@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('landing.html')


@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/day')
@login_required
def day():

    cat_list = []

    for each in current_user.spending:
        if not(each.category in cat_list):
            cat_list.append(each.category)

    cat_val_dict = {}

    valsum = 0

    for each in cat_list:
        spending_list = Spending.query.filter(Spending.user_id == current_user.id,
                                              Spending.category == each,
                                              # Spending.timestamp.date() == datetime.utcnow().date(),
                                              extract('day', Spending.timestamp) >= datetime.today().day
                                              ).all()

        cat_val_dict[each] = 0
        for iterator in spending_list:
            cat_val_dict[each] += iterator.value
            valsum += iterator.value

    cat_val_dict = dict(sorted(cat_val_dict.items(), key=lambda x: x[1], reverse=True))

    key_list = list(cat_val_dict.keys())

    for each in key_list:
        if cat_val_dict[each] == 0:
            del cat_val_dict[each]

    return render_template('bars.html', title='Home', cat_val_dict=cat_val_dict, valsum=valsum)


@app.route('/month')
@login_required
def month():

    cat_list = []

    for each in current_user.spending:
        if not(each.category in cat_list):
            cat_list.append(each.category)

    cat_val_dict = {}

    valsum = 0

    for each in cat_list:

        spending_list = Spending.query.filter(Spending.user_id == current_user.id,
                                              Spending.category == each,
                                              ).all()

    #TODO add month filter to query

        cat_val_dict[each] = 0
        for iterator in spending_list:
            cat_val_dict[each] += iterator.value
            valsum += iterator.value

    cat_val_dict = dict(sorted(cat_val_dict.items(), key=lambda x: x[1], reverse=True))

    #TODO add clearing empty categories

    return render_template('bars.html', title='Home', cat_val_dict=cat_val_dict, valsum=valsum)


@app.route('/all')
@login_required
def all_records():
    return render_template('all.html', title='Home',
                           user_spending=current_user.spending.order_by(Spending.timestamp.desc()))


@app.route('/<record_id>', methods=['GET', 'POST'])
@login_required
def detail(record_id):
    return render_template('detail.html', title='Home',
                           record=Spending.query.get(record_id))


@app.route('/detail/<category>')
@login_required
def cat_detail(category):
    cat_spending = Spending.query.filter(Spending.user_id == current_user.id,
                                         Spending.category == category).all()
    return render_template('cat_detail.html', title='Home',
                           category_list=cat_spending, category_name=category)


@app.route('/delete/<record_id>')
@login_required
def delete(record_id):
    record_to_delete = Spending.query.get(record_id)
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect(url_for('all_records'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_spending():
    form = AddingForm()
    if form.validate_on_submit():
        spend = Spending(user_id=current_user.id, note=form.note.data,
                         category=form.category.data, value=float(form.value.data))
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
