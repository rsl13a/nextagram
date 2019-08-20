from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf import Form
from flask_login import LoginManager, logout_user, login_user, current_user
from wtforms import StringField, PasswordField, validators, TextAreaField
from werkzeug import secure_filename
from braintree_helper import gateway
import os
from helpers import upload_file_to_s3
from google_oauth import oauth
from models.images import Images

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)
oauth.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.get_by_id(user_id)


@app.route('/')
def index():
    return render_template('users.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/signin/success')
def signin_success():
    flash("Successfully signed in")
    return render_template('signin_success.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup/success')
def signup_success():
    flash("Successfully signed up")
    return render_template('signup_success.html')


@app.route('/signout')
def signout():
    logout_user()
    flash("Successfully signed out")
    return redirect('signout.html')


@app.route('/donation_payment')
def donation():
    flash("You are welcome to donate ")
    return render_template('donation_payment.html')


@app.route('/followers')
def followers():
    return render_template('followers.html')


@app.route('/user', methods=['GET', 'POST'])
def profile_upload():
    if request.method == 'POST':
        f = request.files['user_file']
        f.filename = secure_filename(f.filename)

        image = Images(path=f.filename, user=current_user.id)
        image.save()
        print(upload_file_to_s3(f))
        return redirect(url_for('users.show',username=current_user.username))


@app.route("/client_token", methods=["GET"])
def client_token():
    client_token = gateway.client_token.generate()
    return render_template('donation.html', client_token=client_token)


@app.route("/checkout", methods=["POST"])
def create_purchase():
    nonce_from_the_client = request.form["payment_method_nonce"]

    result = gateway.transaction.sale({
        "amount": "10.00",
        "payment_method_nonce": nonce_from_the_client,
        "options": {
            "submit_for_settlement": True
        }
    })

    if result.is_success:
        flash("Thank you for the donation ")
        return render_template('donation_success.html')

    flash("Please try to donate again")
    return render_template('donation_fail.html')


@app.route('/sessions/new/google', methods=['GET'])
def google_login():
    redirect_url = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_url)


@app.route('/sessions/authorize/google', methods=['GET'])
def authorize():
    token = oauth.google.authorize_access_token()
    response = oauth.google.get(
        'https://www.googleapis.com/oauth2/v2/userinfo')
    email = response.json()['email']
    from models.user import User
    user = User.get_or_none(User.email == email)
    if not user:
        return render_template('fail_login.html', message='Fail!')
    login_user(user)
    # Flash message = "Welcome back user"
    return render_template('signin_success.html', message='Success!')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
