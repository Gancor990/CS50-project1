# Project 1

Harvard CS50 - Web Programming with Python and JavaScript

## :gear: Work in progress

Project utilising Python Flask and SQLAlchemy to create a dymanic site consisting of a database of books with implementation of Goodreads API.

### Requirements

 - [x] Registration - users can register with website (password hashed with SHA256)

 - [x] Login - users can login with credentials

 - [x] Logout - users can log out of site

 - [x] Import - imports book CSV into PostgreSQL database

 - [x] Search - can search for book based on ISBN, title and author with matches, if any, displayed

 - [ ] Book Page - contains book details and user reviews

 - [x] Review Submission - contained within book page if user has not yet left a review

 - [x] Goodreads Review Data - return Goodreads average rating and number of ratings via API call

 - [x] API Access - GET request available with /api/<isbn> returning a JSON response in following format:

    {
        "title": "Memory",
        "author": "Doug Lloyd",
        "year": 2015,
        "isbn": "1632168146",
        "review_count": 28,
        "average_score": 5.0
    }


### Welcome page
----------------
![](https://i.imgur.com/GyBhLH1.png)

### Registration
----------------
![](https://i.imgur.com/T4QjnPv.png)

### Book search
---------------
![](https://i.imgur.com/4e8rile.png)
