from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Book

class UserModelCase(unittest.TestCase):
  def setUp(self):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()

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

if __name__ == '__main__':
  unittest.main(verbosity=2)