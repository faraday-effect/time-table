from flask.ext.script import Manager

from app import create_app, db, trello
from app.models import Organization, Person, Board

app = create_app()
manager = Manager(app)


@manager.command
def rebuild_db():
    """Rebuild the database from scratch"""
    db.drop_all()
    db.create_all()


@manager.command
def refresh_orgs():
    """Refresh all organizations from Trello"""
    for org_json in trello.get_organizations():
        Organization.get_or_create(org_json)
    db.session.commit()


@manager.command
def refresh_boards():
    """Refresh from Trello the boards of all organizations"""
    for org in Organization.query.all():
        for board_id in trello.get_board_ids_by_organization(org.name):
            Board.get_or_create(trello.get_board_by_id(board_id))
    db.session.commit()


@manager.command
def refresh_all():
    """Refresh everything from Trello"""
    refresh_orgs()
    refresh_boards()


if __name__ == '__main__':
    manager.run()
