from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template, send_from_directory, request, jsonify, Flask, Response
import json
import StringIO
import os

app = Flask(__name__)
app.debug = True
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

@app.route('/frontend/<template>')
def templates(template):
    return render_template(template)
  
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(os.path.dirname(__file__)+'/js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(os.path.dirname(__file__)+'/css', path)

@app.route("/")
def index():
    return render_template("hello.jade", render_template=render_template)

import templates
import hosts
import containers


