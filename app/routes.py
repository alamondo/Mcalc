from app import app, db
from app.forms import LoginForm, AddingForm, CatAddingForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Spending, UserCategory
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
            cat_list.append(UserCategory.query.filter(UserCategory.id == each.category).first())

    cat_val_dict = {}

    valsum = 0

    for each in cat_list:
        spending_list = Spending.query.filter(Spending.user_id == current_user.id,
                                              Spending.category == each.id,
                                              extract('day', Spending.timestamp) >= datetime.today().day
                                              ).all()

        cat_val_dict[each.value] = 0
        for iterator in spending_list:
            cat_val_dict[each.value] += iterator.value
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
            cat_list.append(UserCategory.query.filter(UserCategory.id == each.category).first())

    cat_val_dict = {}

    valsum = 0

    for each in cat_list:

        spending_list = Spending.query.filter(Spending.user_id == current_user.id,
                                              Spending.category == each.id,
                                              extract('month', Spending.timestamp) == datetime.today().month,
                                              extract('year', Spending.timestamp) == datetime.today().year
                                              ).all()

        cat_val_dict[each.value] = 0
        for iterator in spending_list:
            cat_val_dict[each.value] += iterator.value
            valsum += iterator.value

    cat_val_dict = dict(sorted(cat_val_dict.items(), key=lambda x: x[1], reverse=True))

    key_list = list(cat_val_dict.keys())

    for each in key_list:
        if cat_val_dict[each] == 0:
            del cat_val_dict[each]

    return render_template('bars.html', title='Home', cat_val_dict=cat_val_dict, valsum=valsum)


@app.route('/all')
@login_required
def all_records():

    cat_dict = {}
    for each in current_user.categories:
        if not (each.value in cat_dict.keys()):
            cat_dict[each.id] = each.value
    print(cat_dict)
    #TODO category name printing
    return render_template('all.html', title='Home',
                           user_spending=current_user.spending.order_by(Spending.timestamp.desc()),
                           cat_dict=cat_dict)


@app.route('/<record_id>', methods=['GET', 'POST'])
@login_required
def detail(record_id):
    return render_template('detail.html', title='Home',
                           record=Spending.query.get(record_id))


@app.route('/detail/<category>')
@login_required
def cat_detail(category):
    cat_spending = Spending.query.filter(Spending.user_id == current_user.id,
                                         Spending.category == UserCategory.query.filter(
                                                                    UserCategory.value == category
                                                                    ).first().id)
    return render_template('cat_detail.html', title='Home',
                           category_list=cat_spending, category_name=category)


@app.route('/delete/<record_id>')
@login_required
def delete(record_id):
    print('a')
    record_to_delete = Spending.query.get(record_id)
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect(url_for('all_records'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_spending():
    form = AddingForm()
    #TODO select field styling
    cat_list = []
    for each in current_user.categories:
        if not(each.value in cat_list):
            cat_list.append((each.id, each.value))

    form.category.choices = cat_list

    if form.validate_on_submit():
        category = UserCategory.query.filter(UserCategory.user_id == current_user.id,
                                             UserCategory.id == form.category.data,
                                             ).first()
        spend = Spending(user_id=current_user.id, note=form.note.data,
                         category=category.id, value=float(form.value.data))
        db.session.add(spend)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', title='Adding', form=form, cat_list=cat_list)


@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CatAddingForm()
    if form.validate_on_submit():
        cat = UserCategory(user_id=current_user.id, value=form.category.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_cat.html', title='Adding', form=form)


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
