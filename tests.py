from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Book
from config import Config
from flask_mail import Mail
from app.email import send_book_list_email, send_email

class TestConfig(Config):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app(TestConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_password_hashing(self):
    u = User(username='tim', email='tim@the.com')
    u.set_password('hat')
    self.assertFalse(u.check_password('cat'))
    self.assertTrue(u.check_password('hat'))

  def test_add_book_owned(self):
    u = User(username='tim', email='tim@the.com')
    b = Book(title='The Brothers\' War',
      author='Grubb, Jeff',
      date_of_purchase=datetime.utcnow(),
      notes='Test Notes')
    db.session.add(u)
    db.session.add(b)
    db.session.commit()
    self.assertEqual(u.owned.all(), [])
    
    u.add_book_owned(b)
    db.session.commit()
    self.assertTrue(u.owns_book(b))
    self.assertEqual(u.owned.count(), 1)
    self.assertEqual(u.owned.first().author, 'Grubb, Jeff')

    u.remove_book_owned(b)
    db.session.commit()
    self.assertFalse(u.owns_book(b))
    self.assertEqual(u.owned.count(), 0)
  
  def test_send_email(self):
    subject = 'test'
    sender='test@testing.io'
    recipients=['testing@testing.io']
    text_body='text mctest'
    html_body='<div>testing</div>'
    mail = Mail(self.app)
    with mail.record_messages() as outbox:
      send_email(subject, sender, recipients, text_body, html_body)
      assert len(outbox) == 1
      assert outbox[0].subject == "test"
      assert outbox[0].sender == sender
      assert outbox[0].recipients == recipients
      assert outbox[0].body == text_body

  def test_send_book_list_email(self):
    u = User(username='tim', email='tim@the.com')
    b1title = 'hello'
    b2title = 'world'
    b1 = Book(title=b1title,
      author='b',
      date_of_purchase=datetime.utcnow(),
      notes='Test Notes')
    b2 = Book(title=b2title,
      author='d',
      date_of_purchase=datetime.utcnow(),
      notes='Test Notes')
    
    db.session.add(u)
    db.session.add(b1)
    db.session.add(b2)
    db.session.commit()
    u.add_book_owned(b1)
    u.add_book_owned(b2)
    db.session.commit()
    b = u.owned_books()
    subject = 'test'
    sender='test@testing.io'
    recipients='testing@testing.io'
    text_body='text mctest'
    html_body='<div>testing</div>'
    mail = Mail(self.app)
    with mail.record_messages() as outbox:
      send_book_list_email(u, recipients, b)
      assert len(outbox) == 1
      book1 = outbox[0].body.find('hello')
      book2 = outbox[0].body.find('world')
      assert book1 > 0
      assert book2 > 0
    

if __name__ == '__main__':
  unittest.main(verbosity=2)