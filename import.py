import os
import csv

from flask import Flask, session, render_template, url_for, flash, redirect
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://jffkwmeunskbbw:e8549f0b2c6670317d16aa9b98fda22a7d077561ff0f2a82bd9990e4633d8033@ec2-54-75-226-5.eu-west-1.compute.amazonaws.com:5432/d6o5n45bfj7p4a")
db = scoped_session(sessionmaker(bind=engine))

def main():
    """
    Imports books.csv into PostgreSQL database
    """
    f = open("books.csv")
    reader = csv.reader(f)

    for isbn,title,author,year in reader:
        db.execute(
                "INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",{"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book - {title} - by author - {author}")
    db.commit()

if __name__=="__main__":
    main()

