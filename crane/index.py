from crane.webserver import app

import os
from flask import render_template, send_from_directory

@app.route('/frontend/<template>')
def templates(template):
    return render_template(template)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(os.path.dirname(__file__)+'/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(os.path.dirname(__file__)+'/css', path)


@app.route('/fonts/<path:path>')
def send_font(path):
    return send_from_directory(os.path.dirname(__file__)+'/css/fonts', path)


@app.route("/")
def index():
    return render_template("crane.jade", render_template=render_template)
