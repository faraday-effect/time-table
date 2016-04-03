from flask.ext.script import Manager

from app import create_app, db
from app.trello import TrelloAPI
from app.models import Organization, Person, Board

app = create_app()
manager = Manager(app)
trello = TrelloAPI()


@manager.command
def rebuild_db():
    db.drop_all()
    db.create_all()


@manager.command
def refresh_from_trello():
    for org_json in trello.get_organizations():
        org, created = Organization.get_or_create(id=org_json['id'],
                                                  name=org_json['name'],
                                                  display_name=org_json['displayName'])
        if created:
            db.session.add(org)

        for member_json in trello.get_members_by_organization(org.name):
            member, created = Person.get_or_create_json(member_json)
            if created:
                db.session.add(member)
                org.members.append(member)

        for board_json in trello.get_boards_by_organization(org.name):
            board, created = Board.get_or_create_json(board_json)
            if created:
                db.session.add(board)

                for member_id in (membership['idMember'] for membership in board_json['memberships']):
                    member = Person.query.get(member_id)
                    if member is None:
                        member = Person.from_json(trello.get_member_by_id(member_id))
                        print "FETCHED MEMBER NOT IN ORG {}".format(member)
                        db.session.add(member)
                    board.members.append(member)
                    print "ADDED MEMBER {}".format(member)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
