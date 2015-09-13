from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

from crane.config import config


app = Flask(__name__)
app.debug = True
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(config['database']['db_path'])
db = SQLAlchemy(app)
