import os

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    """Application factory function."""
    app = Flask(__name__)

    db_path = os.path.join(os.getcwd(), 'time-table.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}'.format(db_path)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    return app
