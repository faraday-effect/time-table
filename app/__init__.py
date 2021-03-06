import os

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

from .trello import TrelloAPI

db = SQLAlchemy()
trello = TrelloAPI()

def create_app():
    """Application factory function."""
    app = Flask(__name__)

    db_path = os.path.join(os.getcwd(), 'time-table.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}'.format(db_path)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    db.init_app(app)

    # Routes and error packages
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
