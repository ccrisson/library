from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Required
from app.models import User

class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
  username = StringField('Username',validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Register')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError('Please use a diffrent username.')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError('Please use a diffrent email address.')

class BookForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired()])
  author = StringField('Author', validators=[DataRequired()])
  date_of_purchase = DateField('Date of Purchase', format='%Y-%m-%d')
  notes = TextAreaField('Notes')
  submit = SubmitField('Add to my Library')

class SendBookListForm(FlaskForm):
  recipient = StringField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Send Book List')