import os

from flask import Flask, session, render_template, url_for, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import scoped_session, sessionmaker

# importing hashed password funcs
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegistrationForm, LoginForm, BookSearch

app = Flask(__name__)

app.config['SECRET_KEY'] = '9db738effd3cd1d8c911b53b5e245cd4'

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://jffkwmeunskbbw:e8549f0b2c6670317d16aa9b98fda22a7d077561ff0f2a82bd9990e4633d8033@ec2-54-75-226-5.eu-west-1.compute.amazonaws.com:5432/d6o5n45bfj7p4a")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@app.route("/home")
def index():
    if not session.get('logged_in'):
        return render_template('welcome.html')
    else:
        return render_template('home.html', username=session["user_name"])

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
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

@app.route("/logout")
def logout():

    session["logged_in"] = False
    session["user_id"] = None
    session["user_name"] = None

    return render_template('logout.html')

@app.route("/search", methods=["GET", "POST"])
def search():
    form = BookSearch()

    if form.validate_on_submit():

        isbn = "%" + form.isbn.data + "%" 
        book_title = "%" + form.title.data + "%"
        author = "%" + form.author.data + "%"

        if author == "%%" and book_title == "%%" and isbn == "%%":
            flash(f"Please enter some values!", 'danger')
            return render_template('search.html', title="Book search", form=form)
        elif not isbn == "%%":
            if author == "%%" and book_title == "%%":
                book_res = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",{"isbn": isbn}).fetchall()
            elif not author == "%%" and book_title == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:author) AND isbn LIKE :isbn",{"author": author, "isbn": isbn}).fetchall()
            else:
                book_res = db.execute(
                    "SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn AND LOWER(author) LIKE LOWER(:author)",
                    {"book_title": book_title, "isbn": isbn, "author": author}).fetchall()
        elif not book_title == "%%":
            if author == "%%" and isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:book_title)",{"book_title": book_title}).fetchall()
            elif not author == "%%" and isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:book_title) AND LOWER(author) LIKE LOWER(:author)",{"author": author, "book_title": book_title}).fetchall()
            else:
                book_res = db.execute(
                    "SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn AND LOWER(author) LIKE LOWER(:author)",
                    {"book_title": book_title, "isbn": isbn, "author": author}).fetchall()
        elif not author == "%%":
            if book_title == "%%" and isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:author)",{"author": author}).fetchall()
            elif book_title == "%%" and not isbn == "%%":
                book_res = db.execute("SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn",{"book_title": book_title, "isbn": isbn}).fetchall()
            else:
                book_res = db.execute(
                    "SELECT * FROM books WHERE LOWER(book_title) LIKE LOWER(:book_title) AND isbn LIKE :isbn AND LOWER(author) LIKE LOWER(:author)",
                    {"book_title": book_title, "isbn": isbn, "author": author}).fetchall()
        return render_template('results.html', title="Search results", results=book_res)
    return render_template('search.html', title="Book search", form=form)

if __name__ == '__main__':
    app.run(debug=True)

