from urllib import parse
from flask import Flask, jsonify, Response, request
from flask_restful import Resource, Api, reqparse
import logging
from pymongo import MongoClient
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)
import json
import os

app = Flask(__name__)
api = Api(app)

# Request parser
parser = reqparse.RequestParser()
parser.add_argument('id')
parser.add_argument('username')
parser.add_argument('password')

SECRET_KEY = 'test1234@#$'

# Stuff for database interaction
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetdb

def get_times():
    return list(db.brevetdb.find())

###
# APIs
###
def get_API_results(desired_keys, return_type, k):
    # Get the times from the db
    data = get_times()

    # We always want the miles and km
    desired_keys += ['miles', 'km']
    
    # To avoid Nonetype issues with query parameters
    if k is not None:
        num_times = min(len(data), int(k))
    else:
        num_times = len(data)
    
    # Fill the result with only desired values
    times = {}
    for i in range(num_times):
        ind = int(data[i]['index'])
        times[ind] = {key: data[i][key] for key in desired_keys}

    app.logger.debug(f"Got a {return_type} request")

    # Return the json
    if (return_type == 'json'):
        return jsonify(times)
    
    # Return the csv
    elif (return_type == 'csv'):
        # Get the headings based off of the desired keys
        csv_str = ",".join(desired_keys) + "\n"
        # For each checkpoint, format as csv
        for time in times.values():
            for key in desired_keys:
                csv_str += time[key]
                if (key != desired_keys[-1]):
                    csv_str += ","
            csv_str += "\n"
        
        # Return the response as plain text (for '\n' to work)
        return Response(csv_str, mimetype='text/plain')

def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return "Expired token!"    # valid token, but expired
    except BadSignature:
        return "Invalid token!"    # invalid token
    return True

# Returns a list of all open and close times
class listAll(Resource):
    def get(self, file_type='json'):
        k = request.args.get('k')
        token = request.args.get('token')
        is_auth = verify_auth_token(token)
        if (is_auth == True):
            return get_API_results(['open', 'close'], file_type, k)
        else:
            return Response(is_auth, status=401)

# Returns a list of all open times
class listOpenOnly(Resource):
    def get(self, file_type='json'):
        k = request.args.get('k')
        token = request.args.get('token')
        is_auth = verify_auth_token(token)
        if (is_auth == True):
            return get_API_results(['open'], file_type, k)
        else:
            return Response(is_auth, status=401)

# Returns a list of all close times
class listCloseOnly(Resource):
    def get(self, file_type='json'):
        k = request.args.get('k')
        token = request.args.get('token')
        is_auth = verify_auth_token(token)
        if (is_auth == True):
            return get_API_results(['close'], file_type, k)
        else:
            return Response(is_auth, status=401)

# For logging in and registering
def hash_password(password):
    return pwd_context.encrypt(password)

def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

class register(Resource):
    def post(self):
        new_user = parser.parse_args()

        # Check if the username already exists
        for user in list(db.userdb.find()):
            if (user["username"] == new_user["username"]):
                return Response("Sorry, that username is already in use!", status=400)
        else:
            try:
                #new_user["password"] = hash_password(new_user["password"])
                db.userdb.insert_one(new_user)
                return Response("You have been registered!", status=201)
            except Exception as e:
                return Response("Sorry, but you could not be registered.", status=400)

        # app.logger.debug(args)

def generate_auth_token(expiration=600):
   s = Serializer(SECRET_KEY, expires_in=expiration)
   return s.dumps({'id': 5, 'name': 'Ryan'})

class token(Resource):
    def get(self):
        credentials = parser.parse_args()

        for user in list(db.userdb.find()):
            if credentials["username"] == user["username"] and verify_password(credentials["password"], user["password"]):
                token = generate_auth_token()
                return ({'token': token.decode('utf-8'), 'duration': 600, 'id': user['id']}, 200)
        else:
            return Response("Invalid username or password.", status=401)
                


# List of resources
# List info resources
api.add_resource(listAll, '/listAll', '/listAll/<string:file_type>')
api.add_resource(listOpenOnly, '/listOpenOnly', '/listOpenOnly/<string:file_type>')
api.add_resource(listCloseOnly, '/listCloseOnly', '/listCloseOnly/<string:file_type>')

# Login/Registration resources
api.add_resource(register, '/register')
api.add_resource(token, '/token')



if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)