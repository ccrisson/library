from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, BookForm, SendBookListForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.models import User, Book
from app.email import send_book_list_email, send_email
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/')
@app.route('/index')
@login_required
def index():
  books = current_user.owned_books()
  return render_template('index.html',title='Home Page',books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('index'))
    login_user(user, remember=form.remember_me.data)
    if user.confirmed == False:
      flash('This account is not confirmed!')
      logout_user()
      return redirect(url_for('login'))
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('index')
    return redirect(next_page)
  return render_template('login.html',title='Sign In',form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    email = form.email.data
    token = s.dumps(email, salt='email-confirm')
    link = url_for('confirm_email', token=token, _external=True)
    body = 'Your link is {}'.format(link)
    send_email('Confirm Email', sender=app.config['ADMINS'][0], recipients=[email],text_body=body, html_body=body )
    user = User(username=form.username.data, email=form.email.data, confirmed=False)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Thank you for registering. Please check you email for your confimation link.')
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
  try:
    email = s.loads(token, salt='email-confirm', max_age=1000000)
  except SignatureExpired:
    flash('The link has expired')
    return redirect(url_for('login'))
  user = User.query.filter_by(email=email).first_or_404()
  if user.confirmed:
    flash('Account already confirmed')
  else:
    user.confirmed = True
    db.session.add(user)
    db.session.commit()
    flash('You have confirmed your account.')
  return redirect(url_for('login'))

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
  if current_user.is_authenticated:
    form = BookForm()
    if form.validate_on_submit():
      book = Book(title=form.title.data, author=form.author.data, date_of_purchase=form.date_of_purchase.data, notes=form.notes.data)
      db.session.add(book)
      current_user.add_book_owned(book)
      db.session.commit()
      flash('Book added!')
      return redirect(url_for('index'))
    return render_template('add_book.html', title='Add Book', form=form)
  return redirect(url_for('login'))

@app.route('/send_book_list', methods=['GET', 'POST'])
def send_book_list():
  if current_user.is_authenticated:
    books = current_user.owned_books()
    form = SendBookListForm()
    if form.validate_on_submit():
      send_book_list_email(current_user, form.recipient.data, books)
    return render_template('send_book_list.html', title="Send Book List", books=books, form=form) 
  return redirect(url_for('login'))