from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
from data_models import db, Author, Book

# -----------------------------
# Flask app setup
# -----------------------------
app = Flask(__name__)
app.secret_key = "moja_tajna_123456"  # 🔑 Secret key for flash

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def home():
    search_query = request.args.get("q", "")
    sort_by = request.args.get("sort", "title")

    books = Book.query

    if search_query:
        search = f"%{search_query}%"
        books = books.join(Author).filter(
            (Book.title.ilike(search)) | (Author.name.ilike(search))
        )

    if sort_by == "title":
        books = books.order_by(Book.title)
    elif sort_by == "author":
        books = books.join(Author).order_by(Author.name)

    books = books.all()
    return render_template("home.html", books=books, search_query=search_query)

# -----------------------------
# Add Author
# -----------------------------
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    success = None
    if request.method == "POST":
        name = request.form["name"]
        birth_date_str = request.form["birth_date"]
        death_date_str = request.form.get("date_of_death")

        birth_date = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
        date_of_death = datetime.strptime(death_date_str, "%d-%m-%Y").date() if death_date_str else None

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        success = f"Author {name} added successfully!"
        flash(success, "success")

    return render_template("add_author.html", success=success)

# -----------------------------
# Add Book
# -----------------------------
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    success = None
    authors = Author.query.all()
    if request.method == "POST":
        title = request.form["title"]
        isbn = request.form["isbn"]
        year = int(request.form["publication_year"])
        author_id = int(request.form["author_id"])

        book = Book(title=title, isbn=isbn, publication_year=year, author_id=author_id)
        db.session.add(book)
        db.session.commit()
        success = f"Book {title} added successfully!"
        flash(success, "success")

    return render_template("add_book.html", authors=authors, success=success)

# -----------------------------
# Delete Book
# -----------------------------
@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{book.title}' deleted!", "success")
    return redirect(url_for("home"))

# -----------------------------
# Delete Author
# -----------------------------
@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash(f"Author '{author.name}' and all their books deleted!", "success")
    return redirect(url_for("home"))

# -----------------------------
# Rate Book (Bonus #4)
# -----------------------------
@app.route("/book/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id):
    book = Book.query.get_or_404(book_id)
    rating = request.form.get("rating")
    if rating:
        book.rating = int(rating)
        db.session.commit()
        flash(f"Rating for '{book.title}' updated to {book.rating}/10", "success")
    return redirect(url_for("home"))

# -----------------------------
# AI Book Suggestion (Bonus #5)
# -----------------------------
@app.route("/suggest_book")
def suggest_book():
    # Ova ruta može da šalje podatke ChatGPT-u ili API-ju, trenutno samo placeholder
    books = Book.query.all()
    return render_template("suggest_book.html", books=books)

# -----------------------------
# Book detail page
# -----------------------------
@app.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)  # Get book by ID or return 404
    return render_template("book_detail.html", book=book)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # kreira tabele ako ne postoje
    app.run(debug=True)