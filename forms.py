from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class DropDatabaseForm(FlaskForm):
    submit = SubmitField('Drop Database')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = DecimalField('Product Price', validators=[DataRequired()])
    img = StringField('Product Image URL', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

def validate_product_form(data):

    name = data.get("name", "").strip()
    img = data.get("img", "").strip()
    price = data.get("price", "").strip()

    if not name or len(name) < 3:
        flash("Product name must be at least 3 characters long.", "error")
        return False

    if not img or not img.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
        flash("Image URL must end with .jpg, .jpeg, .png, or .gif.", "error")
        return False

    try:
        price = float(price)
        if price <= 0:
            raise ValueError
    except ValueError:
        flash("Price must be a positive number.", "error")
        return False

    return True
