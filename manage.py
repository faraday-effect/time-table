import re

from flask.ext.script import Manager

from app import create_app, db
from app.trello import TrelloAPI
from app.models import Organization, Person

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
        org = Organization.query.get(org_json['id'])
        if org is None:
            org = Organization(id=org_json['id'],
                               name=org_json['name'],
                               display_name=org_json['displayName'])
            db.session.add(org)
            print "Added org {}".format(org.display_name)
        else:
            print "Org {} exists".format(org.display_name)

        for member_json in trello.get_members_by_organization(org_json['name']):
            member = Person.query.get(member_json['id'])
            if member is None:
                names = [name.capitalize() for name in re.split(r'[_\s]+', member_json['fullName'])]
                first_name = names[0]
                last_name = " ".join(names[1:])
                member = Person(id=member_json['id'],
                                first_name=first_name,
                                last_name=last_name)
                db.session.add(member)
                org.members.append(member)
                print "Added person {}".format(member.full_name)
            else:
                print "Person {} exists".format(member.full_name)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
