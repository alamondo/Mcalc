from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AddingForm(FlaskForm):
    note = StringField('Note')
    value = StringField('Value', validators=[DataRequired()])
    # category = StringField('Category')
    category = SelectField('Category', choices=[], coerce=int)
    submit = SubmitField('Add')


class CatAddingForm(FlaskForm):
    category = StringField('Category')
    submit = SubmitField('Add')
