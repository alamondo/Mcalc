import os
from app import app, db
from app.forms import LoginForm, AddingForm, CatAddingForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Spending, UserCategory, UserCategoryIncome, Income
from datetime import datetime
from sqlalchemy import extract
from copy import deepcopy
from flask import request
from werkzeug.urls import url_parse

from flask import Flask

# app = Flask(__name__)


def redirect_url(default='index'):
    print(request.args)
    print(request.referrer)
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/icon'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('landing.html')


@app.route('/index')
@login_required
def index():

    user_income_categories = UserCategoryIncome.query.filter(UserCategoryIncome.user_id == current_user.id,
                                                             ).all()

    sum = 0

    for each in user_income_categories:
        income_list = Income.query.filter(Income.category == each.id,
                                          extract('month', Spending.timestamp) == datetime.today().month,
                                          extract('year', Spending.timestamp) == datetime.today().year
                                          ).all()
        for each_list_element in income_list:
            sum += each_list_element.value

    cat_list = []
    cat_id_list = []

    for each in current_user.spending:
        if not (each.category in cat_id_list):
            selected_category = UserCategory.query.filter(UserCategory.id == each.category).first()
            if selected_category is not None:
                cat_list.append(selected_category)
                cat_id_list.append(selected_category.id)

    cat_val_dict = {}

    val_sum = 0

    for each in cat_list:

        spending_list = Spending.query.filter(Spending.user_id == current_user.id,
                                              Spending.category == each.id,
                                              extract('month', Spending.timestamp) == datetime.today().month,
                                              extract('year', Spending.timestamp) == datetime.today().year
                                              ).all()

        cat_val_dict[each.value] = 0
        for iterator in spending_list:
            cat_val_dict[each.value] += iterator.value
            val_sum += iterator.value

    balance = 0

    balance = sum - val_sum

    return render_template('index.html', title='Home', sum=sum, balance=balance)


@app.route('/day')
@login_required
def day():

    cat_list = []
    cat_id_list = []

    for each in current_user.spending:
        if not(each.category in cat_id_list):
            selected_category = UserCategory.query.filter(UserCategory.id == each.category).first()
            cat_list.append(selected_category)
            cat_id_list.append(selected_category.id)

    cat_val_dict = {}

    val_sum = 0

    for each in cat_list:
        spending_list = Spending.query.filter(Spending.user_id == current_user.id,
                                              Spending.category == each.id,
                                              extract('day', Spending.timestamp) >= datetime.today().day
                                              ).all()

        cat_val_dict[each.value] = 0
        for iterator in spending_list:
            cat_val_dict[each.value] += iterator.value
            val_sum += iterator.value

    cat_val_dict = dict(sorted(cat_val_dict.items(), key=lambda x: x[1], reverse=True))

    key_list = list(cat_val_dict.keys())

    for each in key_list:
        if cat_val_dict[each] == 0:
            del cat_val_dict[each]

    return render_template('bars.html', title='Home', cat_val_dict=cat_val_dict, valsum=val_sum)


@app.route('/month')
@login_required
def month():

    cat_list = []
    cat_id_list = []

    for each in current_user.spending:
        if not(each.category in cat_id_list):
            selected_category = UserCategory.query.filter(UserCategory.id == each.category).first()
            cat_list.append(selected_category)
            cat_id_list.append(selected_category.id)

    cat_val_dict = {}

    val_sum = 0

    for each in cat_list:

        spending_list = Spending.query.filter(Spending.user_id == current_user.id,
                                              Spending.category == each.id,
                                              extract('month', Spending.timestamp) == datetime.today().month,
                                              extract('year', Spending.timestamp) == datetime.today().year
                                              ).all()

        cat_val_dict[each.value] = 0
        for iterator in spending_list:
            cat_val_dict[each.value] += iterator.value
            val_sum += iterator.value

    cat_val_dict = dict(sorted(cat_val_dict.items(), key=lambda x: x[1], reverse=True))

    key_list = list(cat_val_dict.keys())

    for each in key_list:
        if cat_val_dict[each] == 0:
            del cat_val_dict[each]

    return render_template('bars.html', title='Home', cat_val_dict=cat_val_dict, valsum=val_sum)


@app.route('/all')
@login_required
def all_records():

    user_spending = current_user.spending.order_by(Spending.timestamp.desc())
    dictionary = {}
    i = 1
    for each in user_spending:
        year = each.timestamp.strftime("%Y")
        month = each.timestamp.strftime("%B")
        day = each.timestamp.strftime("%d")

        if year not in dictionary.keys():
            dictionary[year] = {}
        if month not in dictionary[year].keys():
            dictionary[year][month] = {}
        if day not in dictionary[year][month].keys():
            dictionary[year][month][day] = {}

        dictionary[year][month][day][i] = each
        i += 1

    for year in dictionary:
        for month in dictionary[year]:
            for day in dictionary[year][month]:
                day_sum = 0
                for record in dictionary[year][month][day]:
                    selected = dictionary[year][month][day][record]
                    day_sum += float(selected.value)

                dictionary[year][month][day]['daily_sum'] = day_sum

    return render_template('all.html', title='Home',
                           user_spending=dictionary)


@app.route('/categories')
@login_required
def categories():

    return render_template('categories.html', title='Home',
                           user_categories=current_user.categories)


@app.route('/<record_id>', methods=['GET', 'POST'])
@login_required
def detail(record_id):
    return render_template('detail.html', title='Home',
                           record=Spending.query.get(record_id))


@app.route('/income')
@login_required
def income():

    user_income_categories = UserCategoryIncome.query.filter(UserCategoryIncome.user_id == current_user.id).all()
    sum = 0
    income_dict = {}
    for each in user_income_categories:
        cat_sum = 0
        income_list = Income.query.filter(Income.category == each.id).all()
        for each_list_element in income_list:
            cat_sum += each_list_element.value
            sum += each_list_element.value

        income_dict[each.value] = cat_sum

    return render_template('income.html', income_dict=income_dict, sum=sum)


@app.route('/add_income_category', methods=['GET', 'POST'])
@login_required
def add_income_category():
    form = CatAddingForm()
    if form.validate_on_submit():
        cat = UserCategoryIncome(user_id=current_user.id, value=form.category.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_cat.html', title='Adding', form=form)


@app.route('/add_i', methods=['GET', 'POST'])
@login_required
def add_income():
    form = AddingForm()
    # TODO select field styling
    cat_list = []
    for each in current_user.income_categories:
        if not (each.value in cat_list):
            cat_list.append((each.id, each.value))

    form.category.choices = cat_list

    if form.validate_on_submit():
        category = UserCategoryIncome.query.filter(UserCategoryIncome.user_id == current_user.id,
                                                   UserCategoryIncome.id == form.category.data,
                                                   ).first()
        new_income = Income(user_id=current_user.id, note=form.note.data,
                            category=category.id, value=float(form.value.data))
        db.session.add(new_income)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', title='Adding', form=form, cat_list=cat_list)


@app.route('/detail/<category>')
@login_required
def cat_detail(category):
    cat_spending = Spending.query.filter(Spending.user_id == current_user.id,
                                         Spending.category == UserCategory.query.filter(
                                                                    UserCategory.value == category
                                                                    ).first().id)

    cat_id = UserCategory.query.filter(UserCategory.value == category).first().id

    return render_template('cat_detail.html', title='Home',
                           category_list=cat_spending, category_name=category, cat_id=cat_id)


@app.route('/delete/<record_id>')
@login_required
def delete(record_id):
    record_to_delete = Spending.query.get(record_id)
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect(url_for('all_records'))


@app.route('/cat_delete/<category_id>')
@login_required
def cat_delete(category_id):

    record_to_delete = UserCategory.query.get(category_id)
    print(record_to_delete)
    db.session.delete(record_to_delete)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_spending():
    form = AddingForm()

    prev_url = redirect_url()

    cat_list = []
    for each in current_user.categories:
        if not(each.value in cat_list):
            cat_list.append((each.id, each.value))

    form.category.choices = cat_list
    # print(form.time.data)
    # print(datetime.today())
    # form = ContactForm(request.form)

    if form.validate_on_submit():
        category = UserCategory.query.filter(UserCategory.user_id == current_user.id,
                                             UserCategory.id == form.category.data,
                                             ).first()
        spend = Spending(user_id=current_user.id, note=form.note.data,
                         category=category.id, value=float(form.value.data),
                         timestamp=form.time.data)
        db.session.add(spend)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        print(prev_url)

    return render_template('add.html', title='Adding', form=form, cat_list=cat_list)


@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CatAddingForm()
    if form.validate_on_submit():
        cat = UserCategory(user_id=current_user.id, value=form.category.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('add_cat.html', title='Adding', form=form)


@app.route('/edit/<record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):

    record_to_edit = Spending.query.get(record_id)

    form = AddingForm()

    cat_list = []
    for each in current_user.categories:
        if not (each.value in cat_list):
            cat_list.append((each.id, each.value))

    form.category.choices = cat_list

    if request.method == "GET":

        form.time.default = record_to_edit.timestamp
        form.value.default = int(record_to_edit.value)
        form.note.default = record_to_edit.note
        form.category.default = record_to_edit.category
        form.process()

    if form.validate_on_submit():
        category = UserCategory.query.filter(UserCategory.user_id == current_user.id,
                                             UserCategory.id == form.category.data,
                                             ).first()
        record_to_edit = Spending.query.get(record_id)
        record_to_edit.note = form.note.data
        record_to_edit.category = category.id
        record_to_edit.value = form.value.data
        record_to_edit.timestamp = form.time.data
        db.session.flush()
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_record.html', title='Adding', form=form, cat_list=cat_list)


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


@app.route('/profileinfo')
def profile():
    return render_template('profile_info.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
