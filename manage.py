from flask.ext.script import Manager

from app import create_app
from app import db

app = create_app()
manager = Manager(app)


@manager.command
def rebuild_db():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    manager.run()
