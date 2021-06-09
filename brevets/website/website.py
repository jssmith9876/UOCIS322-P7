from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask.json import jsonify
from werkzeug.wrappers import response
from flask_login import (LoginManager, current_user, login_required,
                        login_user, logout_user, UserMixin, 
                        confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, PasswordField, validators
from pymongo import MongoClient
from passlib.apps import custom_app_context as pwd_context
import requests
import logging
import json
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


# Helper Functions
def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def hash_password(password):
    return pwd_context.encrypt(password)

class User(UserMixin):
    def __init__(self, id, name, token):
        self.id = id
        self.name = name
        self.token = token

    # Override the get_id function to keep the user's token
    def get_id(self):
        return [self.id, self.token]

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
    current_id = user_id[0]
    current_token = user_id[1]

    found_users = list(db.userdb.find( { 'id': current_id } ))
    if (len(found_users) > 0):
        return User(current_id, found_users[0]["username"], current_token)
    else:
        return None

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

        r = requests.get("http://restapi:5000/token", params={'username': username, 'password': password})

        if (r.status_code == 200):
            response_content = json.loads(r.text)
            remember = request.form.get("remember", "false") == "true"
            new_user = User(response_content['id'], username, response_content['token'])
            if (login_user(new_user, remember=remember)):
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(400)
                return redirect(next or url_for('home'))
        elif (r.status_code == 401):
            flash(r.text)
        else:
            flash("Something went wrong.")
    

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

        new_user["password"] = hash_password(new_user["password"])

        # Send the user to the API
        r = requests.post("http://restapi:5000/register", data=new_user)

        # Get the response, and act accordingly
        flash(r.text)
        if (r.text == "You have been registered!"):
            NUM_REGISTERED += 1
        
    return render_template('register.html', form=form)

@app.route('/_get_data')
def _get_data():
    ret_type = request.args.get('ret_type')
    file_type = request.args.get('file_type')
    k = request.args.get('k')
    
    # Get the correct api based on the arguments given
    app.logger.debug(f"Current token: {current_user.token}")
    url = "http://restapi:5000/" + ret_type + "/" + file_type + "?k=" + k + "&token=" + current_user.token
    r = requests.get(url)

    if (r.status_code == 401):
        abort(401)

    return r.text
    


if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)