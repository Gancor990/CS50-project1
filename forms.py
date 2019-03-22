from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class BookSearch(FlaskForm):
    isbn = StringField('ISBN')
    title = StringField('Title')
    author = StringField('Author')
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    rating = RadioField('Rating', choices = [('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    review = TextAreaField('Submit Review', validators=[Length(min=5, max=200)])
    submit = SubmitField('Submit')
