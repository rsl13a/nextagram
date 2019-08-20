from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from flask_login import current_user, login_user
from models.images import Images


users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/', methods=['POST'])
def create():
    username = request.form['username']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    password = request.form['password']
    email = request.form['email']

    hashed_password = generate_password_hash(password)

    u = User(username=username, first_name=first_name,
             last_name=last_name, password=hashed_password, email=email)
    u.save()
    return render_template('signup_success.html', first_name=first_name)


@users_blueprint.route('/<username>', methods=['GET'])
def show(username):
    user = User.get_or_none(User.username == username)
    images = Images.select().where(Images.user_id == user.id)
    return render_template('users/show.html', user=user, images=images)


@users_blueprint.route('/search', methods=['POST'])
def search():
    user = User.get_or_none(
        User.username == request.form.get('username-search'))
    if user:
        return redirect(url_for('users.show', username=user.username))
    else:
        flash("User does not exist.")
        return render_template("users/show.html", user=current_user)


@users_blueprint.route('/signin', methods=["POST"])
def signin():
    username = request.form['username']
    password = request.form['password']

    user = User.get_or_none(User.username == username)

    if not user:
        flash('No such username exists')
        return redirect(url_for('signin'))

    if not check_password_hash(user.password, password):
        flash('Incorrect password')
        return redirect(url_for('signin'))

    login_user(user)
    return redirect(url_for('signin_success'))


@users_blueprint.route('/<id>/edit', methods=["GET"])
def edit(id):
    if not current_user.is_authenticated:
        return redirect(url_for('signin'))
    else:
        user = User.get_by_id(id)
        if current_user == user:
            return render_template('users/edit.html', user=user)
        else:
            return redirect(url_for('index'))


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    new_email = request.form.get('new_email')
    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')

    user = User.get_by_id(id)

    user.username = new_username
    user.email = new_email
    user.password = new_password
    user.save()

    flash('Profile successfully updated')
    return redirect(url_for('users.show', username=current_user.username))
