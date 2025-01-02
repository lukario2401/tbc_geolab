from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from ext import app, db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_required, login_user
from models import Product, User, Like
from forms import ProductForm, RegisterForm, LoginForm, DropDatabaseForm
from flask_login import logout_user
from flask import render_template
from flask_login import login_required, current_user

users = {
    "luka": {"name": "Luka", "username": "Lukario", "age": 24, "img": "Porsche_9/11_2021_edition.png", "role": "user"},
    "noctis": {"name": "Noctis", "username": "Chair", "age": 0, "img": "I_used_to_have_a_home_too.png", "role": "mvp"},
    "mad": {"name": "Mad", "username": "Prince", "age": 0, "img": "there_is_blood_on_your_hands_sunless.png", "role": "vip"},
    "sin": {"name": "Sin", "username": "Of_Solace", "age": 20, "img": "There_is_nothing_more_despicable_then_a_slave_who_begins_to_trust_there_master.png", "role": "vip"},
    "weaver": {"name": "Weaver", "username": "--unknown--", "age": 24, "img": "First_born_Of_The_Forgot_god.png", "role": "admin"}
}


@app.route("/", methods=["GET"])
def index():
    form = ProductForm()
    products = Product.query.all()
    return render_template("/index.html", products=products, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


@app.route('/profile')
@login_required
def profile():
    form = DropDatabaseForm()
    return render_template('profile.html', user=current_user, form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

        new_user = User(username=username, email=email, password_hash=hashed_password,role="user")

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = ProductForm()
    if request.method == "POST":
        if form.validate_on_submit():
            price = float(form.price.data) if form.price.data else 0.0

            new_product = Product(
                name=form.name.data,
                img=form.img.data,
                price=price
            )
            db.session.add(new_product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("index"))
    return render_template("add.html", form=form)


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit(product_id):
    product = Product.query.get_or_404(product_id)

    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = float(form.price.data)
        product.img = form.img.data

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', product=product, form=form)


@app.route("/like/<int:product_id>", methods=["POST"])
@login_required
def like_product(product_id):
    product = Product.query.get_or_404(product_id)

    existing_like = Like.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if existing_like:
        return jsonify({"success": False, "message": "You have already liked this product."})

    product.likes += 1
    like = Like(user_id=current_user.id, product_id=product.id)
    db.session.add(like)
    db.session.commit()

    return jsonify({"success": True, "new_like_count": product.likes})


@app.route('/drop_database', methods=['POST'])
@login_required
def drop_database():
    if current_user.role == 'admin':
        db.drop_all()
        db.create_all()
        return "Database dropped and recreated!", 200
    else:
        return "Unauthorized", 403


with app.app_context():
    admin_user = User.query.filter_by(username='weaver').first()
    if not admin_user:
        hashed_password = generate_password_hash('securepassword', method='pbkdf2:sha256')
        admin = User(username='weaver', email='spell@gmail.com', password_hash=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin user already exists!")
