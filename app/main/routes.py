from flask import render_template, flash, redirect, request, url_for
from app import db
from app.main.forms import BookForm, SendBookListForm, EditBookForm
from app.models import User, Book
from app.email import send_book_list_email, send_email
from app.main import bp
from flask_login import current_user, login_required

@bp.route('/')
@bp.route('/index')
@login_required
def index():
  books = current_user.owned_books()
  return render_template('index.html',title='Home Page',books=books)



@bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
  if current_user.is_authenticated:
    form = BookForm()
    if form.validate_on_submit():
      book = Book(title=form.title.data, author=form.author.data, date_of_purchase=form.date_of_purchase.data, notes=form.notes.data)
      db.session.add(book)
      current_user.add_book_owned(book)
      db.session.commit()
      flash('Book added!')
      return redirect(url_for('main.index'))
    return render_template('add_book.html', title='Add Book', form=form)
  return redirect(url_for('auth/login'))

@bp.route('/send_book_list', methods=['GET', 'POST'])
def send_book_list():
  if current_user.is_authenticated:
    books = current_user.owned_books()
    form = SendBookListForm()
    if form.validate_on_submit():
      send_book_list_email(current_user, form.recipient.data, books)
      flash('Booklist sent!')
      return redirect(url_for('main.index'))
    return render_template('send_book_list.html', title="Send Book List", books=books, form=form) 
  return redirect(url_for('auth/login'))

@bp.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
  if current_user.is_authenticated:
    book = Book.query.filter_by(id=id).first_or_404()
    form = EditBookForm()
    if form.validate_on_submit():
      book.title = form.title.data
      book.author = form.author.data
      book.date_of_purchase = form.date_of_purchase.data
      book.notes = form.notes.data
      db.session.commit()
      flash('Book updated!')
      return redirect(url_for('main.index'))
    elif request.method == 'GET':
      form.title.data = book.title
      form.author.data = book.author
      form.date_of_purchase.data = book.date_of_purchase
      form.notes.data = book.notes
    return render_template('edit_book.html', title="Edit Book", form=form)