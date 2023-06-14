from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, PasswordField
from wtforms.widgets import TextArea
from wtforms.validators import EqualTo, Length

class EntryCreateForm(FlaskForm):
    text = StringField('Text', widget=TextArea())
    submit = SubmitField('Send')

class LoginForm(FlaskForm):
    login = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Log in')

class RegisterForm(FlaskForm):
    login = StringField('Username')
    password = PasswordField('Password', validators=[Length(8, 64), EqualTo('password_confirm')])
    password_confirm = PasswordField('Confirm Password')
    key = StringField('Registration Key')
    submit = SubmitField('Register')
