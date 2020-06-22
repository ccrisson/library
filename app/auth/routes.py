from flask import render_template, flash, redirect, request, url_for, current_app
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app.email import send_email
from app.models import User
from config import Config



@bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('main.index'))
    login_user(user, remember=form.remember_me.data)
    if user.confirmed == False:
      flash('This account is not confirmed!')
      logout_user()
      return redirect(url_for('auth.login'))
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('main.index')
    return redirect(next_page)
  return render_template('auth/login.html',title='Sign In',form=form)

@bp.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    email = form.email.data
    token = s.dumps(email, salt='email-confirm')
    link = url_for('auth.confirm_email', token=token, _external=True)
    body = 'Your link is {}'.format(link)
    send_email('Confirm Email', sender=current_app.config['ADMINS'][0], recipients=[email],text_body=body, html_body=body )
    user = User(username=form.username.data, email=form.email.data, confirmed=False)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Thank you for registering. Please check you email for your confimation link.')
    return redirect(url_for('auth.login'))
  return render_template('auth/register.html', title='Register', form=form)

@bp.route('/confirm_email/<token>')
def confirm_email(token):
  try:
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    email = s.loads(token, salt='email-confirm', max_age=1000000)
  except SignatureExpired:
    flash('The link has expired')
    return redirect(url_for('auth.login'))
  user = User.query.filter_by(email=email).first_or_404()
  if user.confirmed:
    flash('Account already confirmed')
  else:
    user.confirmed = True
    db.session.add(user)
    db.session.commit()
    flash('You have confirmed your account.')
  return redirect(url_for('auth.login'))