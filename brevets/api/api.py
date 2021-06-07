from flask import Flask, jsonify, Response, request
from flask_restful import Resource, Api
import logging
from pymongo import MongoClient
import os

app = Flask(__name__)
api = Api(app)

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

# Returns a list of all open and close times
class listAll(Resource):
    def get(self, file_type='json'):
        k = request.args.get('k')
        return get_API_results(['open', 'close'], file_type, k)

# Returns a list of all open times
class listOpenOnly(Resource):
    def get(self, file_type='json'):
        k = request.args.get('k')
        return get_API_results(['open'], file_type, k)

# Returns a list of all close times
class listCloseOnly(Resource):
    def get(self, file_type='json'):
        k = request.args.get('k')
        return get_API_results(['close'], file_type, k)

# List of resources
api.add_resource(listAll, '/listAll', '/listAll/<string:file_type>')
api.add_resource(listOpenOnly, '/listOpenOnly', '/listOpenOnly/<string:file_type>')
api.add_resource(listCloseOnly, '/listCloseOnly', '/listCloseOnly/<string:file_type>')


if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)