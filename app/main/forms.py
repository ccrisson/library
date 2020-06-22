from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError, Email
from app.models import User

class BookForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired()])
  author = StringField('Author', validators=[DataRequired()])
  date_of_purchase = DateField('Date of Purchase', format='%Y-%m-%d')
  notes = TextAreaField('Notes')
  submit = SubmitField('Add to my Library')

class SendBookListForm(FlaskForm):
  recipient = StringField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Send Book List')

class EditBookForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired()])
  author = StringField('Author', validators=[DataRequired()])
  date_of_purchase = DateField('Date of Purchase', format='%Y-%m-%d')
  notes = TextAreaField('Notes')
  submit = SubmitField('Edit Book')