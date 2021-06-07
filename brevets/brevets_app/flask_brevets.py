"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import acp_db     # Database interactions
import json
import logging

###
# Globals
###
app = flask.Flask(__name__)


###
# Pages
###
@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')

@app.route("/display_results")
def display_results():
    return flask.render_template("display_results.html",
                                items=acp_db.get_times())

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', default=999, type=float)
    dist = request.args.get('dist', default=999, type=float)
    start_time = request.args.get('start', default=arrow.now(), type=str)
    start_time = arrow.get(start_time)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    open_time = acp_times.open_time(km, dist, start_time).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, dist, start_time).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/_submit_values", methods=["POST"])
def _submit_values():
    app.logger.debug("Got a submit request")
    entries = json.loads(request.form.get('entries'))      # Get the results from the request
    app.logger.debug(entries)
    # Drop the table
    acp_db.clear_table()

    insertion_result = True

    for entry in entries:
        insertion_result = acp_db.insert_time(entry)
        if not insertion_result:
            break

    # Return the results
    result = {"delivered": insertion_result}
    return flask.jsonify(response=result)

#############

if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port 5000")
    app.run(port="5000", host="0.0.0.0")
