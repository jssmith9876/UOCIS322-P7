from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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