from app import db, login
from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

books_owned = db.Table(
  'books_owned',
  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
  db.Column('book_id', db.Integer, db.ForeignKey('book.id'))
)

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  confirmed = db.Column(db.Boolean, nullable=False, default=False)
  owned = db.relationship(
    'Book', secondary=books_owned,
    primaryjoin=(books_owned.c.user_id == id),
    #secondaryjoin=(books_owned.c.book_id == id),
    backref=db.backref('books_owned',lazy='dynamic'), 
    lazy='dynamic')

  def __repr__(self):
    return '<User {}>'.format(self.username)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def add_book_owned(self, book):
    if not self.owns_book(book):
      self.owned.append(book)
  
  def remove_book_owned(self, book):
    if self.owns_book(book):
      self.owned.remove(book)

  def owns_book(self, book):
    return self.owned.filter(
      books_owned.c.book_id == book.id).count() > 0

  def owned_books(self):
    return Book.query.join(
      books_owned, (books_owned.c.book_id == Book.id)).filter(
        books_owned.c.user_id == self.id).order_by(
          Book.date_of_purchase.desc())

@login.user_loader
def load_user(id):
  return User.query.get(int(id))

class Book(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(120), index=True)
  author = db.Column(db.String(64), index=True)
  date_of_purchase = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  notes = db.Column(db.String(180))

  def __repr__(self):
    return '<Book {}'.format(self.body)

# class BooksOwned(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#   book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

