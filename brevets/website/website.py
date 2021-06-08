from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import (LoginManager, current_user, login_required,
                        login_user, logout_user, UserMixin, 
                        confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, PasswordField, validators
from pymongo import MongoClient
import requests
import logging
import os

"""
Database stuff
"""
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetdb

"""
Login stuff
"""
class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25, 
                         message=u"Username must be between 2 and 25 characters!"),
        validators.InputRequired(u"Username is required")
    ])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
                         message=u"Password must be between 2 and 25 characters!"),
        validators.InputRequired(u"Password is required")
    ])
    remember = BooleanField("Remember me")

class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25, 
                         message=u"Username must be between 2 and 25 characters!"),
        validators.InputRequired(u"Username is required")
    ])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
                         message=u"Password must be between 2 and 25 characters!"),
        validators.InputRequired(u"Password is required"),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

USERS = {
    1: User(u"1", u"jordan", u"password1"),
    2: User(u"2", u"other", u"password2")
}

USER_NAMES = dict((u.name, u) for u in USERS.values())

app = Flask(__name__)
app.secret_key = "and the cats in the cradle and the silver spoon"

app.config.from_object(__name__)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return USERS[int(user_id)]

login_manager.init_app(app)

"""
Routes
"""
@app.route('/')
@app.route('/index')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if (form.validate_on_submit() and request.method == "POST" and 
        "username" in request.form and "password" in request.form):
        username = request.form["username"]
        password = request.form["password"]

        for user in USERS.values():
            if username == user.name and password == user.password:
                remember = request.form.get("remember", "false") == "true"
                if login_user(USER_NAMES[username], remember=remember):
                    flash("Logged in!")
                    flash("I'll remember you") if remember else None
                    next = request.args.get("next")
                    if not is_safe_url(next):
                        abort(400)
                    return redirect(next or url_for('home'))
                else:
                    flash("Sorry, but you could not be logged in.")
        else:
            flash(u"Invalid username or password.")

    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("home"))


NUM_REGISTERED = 0

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if (form.validate_on_submit() and request.method == "POST"):
        global NUM_REGISTERED
        new_user = {
            "id": str(NUM_REGISTERED),
            "username": request.form["username"],
            "password": request.form["password"]
        }

        # Make sure the username is not already in use
        for user in list(db.userdb.find()):
            if user["username"] == new_user["username"]:
                flash("Sorry, that username is already in use!")
                return redirect(url_for('register'))
        else:
            try:
                db.userdb.insert_one(new_user)
                flash("You have been registered!")
                NUM_REGISTERED += 1
            except Exception as e:
                flash("Sorry, but you could not be registered.")
                return redirect(url_for('register'))
        
    return render_template('register.html', form=form)

@app.route('/_get_data')
def _get_data():
    ret_type = request.args.get('ret_type')
    file_type = request.args.get('file_type')
    k = request.args.get('k')
    
    # Get the correct api based on the arguments given
    url = "http://restapi:5000/" + ret_type + "/" + file_type + "?k=" + k
    r = requests.get(url)
    return r.text
    


if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)