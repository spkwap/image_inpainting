from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, DataRequired, Email, EqualTo
from wtforms import ValidationError
from models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username is required."),
        Length(min=4, max=150, message="Username must be between 4 and 150 characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Invalid email address."),
        Length(max=120, message="Email address must not exceed 120 characters.")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required."),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please choose another one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message="Username is required.")])
    password = PasswordField('Password', validators=[InputRequired(message="Password is required.")])
