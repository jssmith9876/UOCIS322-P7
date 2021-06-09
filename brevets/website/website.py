from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from flask_login import (LoginManager, current_user, login_required,
                        login_user, logout_user, UserMixin)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt as hash_method
import requests
import logging
import json

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


# Hashing method
SECRET_KEY = 'test1234'
def hash_password(password):
    return hash_method.using(salt=SECRET_KEY).encrypt(password)

class User(UserMixin):
    def __init__(self, id, name, token):
        self.id = id
        self.name = name
        self.token = token

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
    # Make sure a username/token are already in the session
    if ("username" in session.keys() and "token" in session.keys()):
        return User(user_id, session["username"], session["token"])
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

def resolve_login(response_content, username, remember):
    new_user = User(response_content['id'], username, response_content['token'])
    if (login_user(new_user, remember=remember)):
        # Store the user information in the session
        session["username"] = username
        session["token"] = response_content["token"]
        return True
    else:
        return False

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if (form.validate_on_submit() and request.method == "POST" and 
        "username" in request.form and "password" in request.form):
        username = request.form["username"]
        password = request.form["password"]

        r = requests.get("http://restapi:5000/token", params={'username': username, 'password': hash_password(password)})

        if (r.status_code == 200):
            remember = request.form.get("remember", "false") == "true"
            login_result = resolve_login(json.loads(r.text), username, remember)
            if (login_result):
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(400)
                return redirect(next or url_for('home'))
            else:
                flash("Sorry, you could not be logged in.")
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

# To count the number 
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
        reg_resp = requests.post("http://restapi:5000/register", data=new_user)

        # Get the response, and act accordingly
        flash(reg_resp.text)
        if (reg_resp.status_code == 201):
            # Try to log the newly registered user in
            log_resp = requests.get("http://restapi:5000/token", params={'username': new_user["username"], 'password': new_user["password"]})
            if (log_resp.status_code == 200):
                login_result = resolve_login(json.loads(log_resp.text), new_user["username"], False)
                if (login_result):
                    flash("Logged in!")
                    next = request.args.get("next")
                    if not is_safe_url(next):
                        abort(400)
                    return redirect(next or url_for('home'))
                else:
                    flash("Sorry, you could not be logged in.")
            elif (log_resp.status_code == 401):
                flash(log_resp.text)
            else:
                flash("Something went wrong.")
            
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