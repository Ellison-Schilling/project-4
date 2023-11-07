"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import sys

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


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
    # Arugments
    km = request.args.get('km', 999, type=float)
    date = request.args.get('date', 0, type=str)

    distance = request.args.get('distance', 0, type=float)  # Request the time given
    time = request.args.get('time', 0, type=str)    # Request the time specified

    # Checking
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))

    # Formating date_time
    date_time = date + ' ' + time + ':00'   # Fix how the date is put in to include the time as well
    arrow_time = arrow.get(date_time, 'YYYY-MM-DD HH:mm:ss')    # Formats the date_time into arrow

    open_time = arrow.get(acp_times.open_time(km, distance, arrow_time))
    
    # Happens on invalid input simply does not return anything helpful
    if open_time == None:
        return None

    open_time = arrow.get(open_time)

    close_time = acp_times.close_time(km, distance, arrow_time)
    
    # Happens on invalid input does not return anything helpful
    if open_time == None:
        return None

    close_time = arrow.get(close_time)  

    result = {"open": open_time.format('YYYY-MM-DD HH:mm'), "close": close_time.format('YYYY-MM-DD HH:mm')}

    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
