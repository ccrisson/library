from flask_mail import Message
from threading import Thread
from flask import render_template
from app import app, mail

def send_async_email(app, msg):
  with app.app_context():
    mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
  msg = Message(subject, sender=sender, recipients=recipients)
  msg.body = text_body
  msg.html = html_body
  Thread(target=send_async_email, args=(app, msg)).start()

def send_book_list_email(user, recipients, book_list):
  send_email('book list', sender=app.config['ADMINS'][0], recipients=[recipients], text_body = render_template('email/book_list.txt', user=user, books=book_list), html_body=render_template('email/book_list.html', user=user, books=book_list))

  