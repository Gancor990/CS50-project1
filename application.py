import os, requests

from flask import Flask, session, render_template, url_for, flash, redirect, jsonify, request
from flask_session import Session
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import scoped_session, sessionmaker

# hashed password functions
from werkzeug.security import generate_password_hash, check_password_hash

# form classes 
from forms import RegistrationForm, LoginForm, BookSearch, ReviewForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '9db738effd3cd1d8c911b53b5e245cd4'

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://jffkwmeunskbbw:e8549f0b2c6670317d16aa9b98fda22a7d077561ff0f2a82bd9990e4633d8033@ec2-54-75-226-5.eu-west-1.compute.amazonaws.com:5432/d6o5n45bfj7p4a")
db = scoped_session(sessionmaker(bind=engine))

# front page route
@app.route("/")
@app.route("/home")
def index():
        return render_template('home.html', username=session["user_name"])

# registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # generate hashed password
        hashed_password = generate_password_hash(form.password.data, method="sha256") 
        
        if form.password.data != form.confirm_password.data:
            flash(f"Passwords do not match")
            return redirect(url_for('register'))     
        else:
            db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)", 
                {"username": form.username.data, "email": form.email.data, "password": hashed_password })
            db.commit()

            flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for('index'))

    return render_template('register.html', title='Register', form=form)

# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        password = form.password.data
        email = form.email.data

        result = db.execute("SELECT id, username, password FROM users WHERE email LIKE :email", {"email": email}).fetchone()
        db_hash = result.password
        username = result.username
        user_id = result.id
        
        if not result:
            flash(f"Login unsuccessful - no user found with that email address!", 'danger')
            return render_template("login.html", message="No such user with that email address!", form=form)

        elif db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount == 1:
            if check_password_hash(db_hash, password):
                flash(f"Logged in as {username}!", 'success')

                session["logged_in"] = True
                session["user_id"] = user_id
                session["user_name"] = username
                return render_template("home.html", username=session["user_name"])
        else:
            flash(f"Login unsuccessful - please try again!", 'danger')
            return redirect(url_for('index'))

    return render_template('login.html', title='Login', form=form)

# logout route
@app.route("/logout")
def logout():

    session["logged_in"] = False
    session["user_id"] = None
    session["user_name"] = None

    return render_template('logout.html')

# search route
@app.route("/search", methods=["GET", "POST"])
def search():
    form = BookSearch()

    if form.validate_on_submit():

        isbn = "%" + form.isbn.data + "%" 
        book_title = "%" + form.title.data + "%"
        author = "%" + form.author.data + "%"

        # book database search - amount of raw SQL due to the specification of the project
        if author == "%%" and book_title == "%%" and isbn == "%%":
            flash(f"Please enter some values!", 'danger')
            return render_template('search.html', title="Book search", form=form)
        elif not isbn == "%%":
            if author == "%%" and book_title == "%%":
                book_res = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",{"isbn": isbn}).fetchall()
            elif not author == "%%" and book_title == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:author) AND isbn LIKE :isbn",
                                    {"author": author, "isbn": isbn}).fetchall()
            else:
                book_res = db.execute(
                    "SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn AND LOWER(author) LIKE LOWER(:author)",
                    {"book_title": book_title, "isbn": isbn, "author": author}).fetchall()
        elif not book_title == "%%":
            if author == "%%" and isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:book_title)",{"book_title": book_title}).fetchall()
            elif not author == "%%" and isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:book_title) AND LOWER(author) LIKE LOWER(:author)",
                                    {"author": author, "book_title": book_title}).fetchall()
            else:
                book_res = db.execute(
                    "SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn AND LOWER(author) LIKE LOWER(:author)",
                    {"book_title": book_title, "isbn": isbn, "author": author}).fetchall()
        elif not author == "%%":
            if book_title == "%%" and isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:author)",{"author": author}).fetchall()
            elif book_title == "%%" and not isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn",
                                    {"book_title": book_title, "isbn": isbn}).fetchall()
            else:
                book_res = db.execute(
                    "SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn AND LOWER(author) LIKE LOWER(:author)",
                    {"book_title": book_title, "isbn": isbn, "author": author}).fetchall()

        return render_template('results.html', title="Search results", results=book_res)

    return render_template('search.html', title="Book search", form=form)

# book details route
@app.route("/bookdetail/<string:book_id>", methods=["GET", "POST"])
def bookdetail(book_id):
    form = ReviewForm()
    query_isbn = f"%{book_id}%".lower()
    
    # select book from database
    book_res = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn LIMIT 1",{"isbn": query_isbn}).fetchone()
    # check if user has existing review in database
    user_existing_review = db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_name = :user_name",
                            {"isbn": query_isbn, "user_name": session["user_name"]}).fetchone()
    # request Goodreads data
    goodreads_request = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6vsh1pJmzHPFQE7G6jppw", "isbns": book_id})
    # select other user reviews from database
    other_user_reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn EXCEPT SELECT * FROM reviews WHERE user_name = :user_name",
                            {"isbn": query_isbn, "user_name": session["user_name"]}).fetchall()
  
    info = goodreads_request.json()
    goodreads_rating = float(info['books'][0]['average_rating'])
    goodreads_rating_num = int(info['books'][0]['ratings_count'])

    if user_existing_review:
        # if the user has an existing review, display that review
        return render_template(
            'bookdetail.html', book=book_res, review=user_existing_review, goodreads_rating=goodreads_rating, 
            rating_num=goodreads_rating_num, other_users=other_user_reviews)

    if form.validate_on_submit():
        # submit review and rating to the database
        rating = form.rating.data
        review = form.review.data

        db.execute(
            "INSERT INTO reviews (user_name, rating, review, isbn) VALUES (:user_name, :rating, :review, :isbn)",
            {"user_name": session["user_name"], "rating": rating, "review": review, "isbn": query_isbn })
        db.commit()

        flash(f"Your review has been submitted!", 'success')

    return render_template('bookdetail.html', book=book_res, form=form, goodreads_rating=goodreads_rating, 
            rating_num=goodreads_rating_num, other_users=other_user_reviews)

# API route
@app.route("/api/<isbn>", methods=["GET"])
def apicall(isbn):
    """Return details about a book"""
    goodreads_request = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6vsh1pJmzHPFQE7G6jppw", "isbns": isbn})
  
    info = goodreads_request.json()
    goodreads_rating = float(info['books'][0]['average_rating'])
    goodreads_rating_num = int(info['books'][0]['ratings_count'])

    query_isbn = f"%{isbn}%".lower()

    book = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn LIMIT 1",{"isbn": query_isbn}).fetchone()

    if book is None:
        return jsonify({"error": "Invalid book ISBN"}), 404
    else:
        response = {
            "title": book.title, 
            "author": book.author, 
            "year": book.year, 
            "isbn": book.isbn,
            "review_count": goodreads_rating,
            "average_score": goodreads_rating_num
        }
        return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

