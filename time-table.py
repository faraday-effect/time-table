import json
import re

from trello import TrelloAPI


def pprint_json(obj):
    print json.dumps(obj, indent=2)


class Person(object):
    def __init__(self, first_name, last_name, trello_id):
        self.first_name = first_name
        self.last_name = last_name
        self.trello_id = trello_id
        self.person_by_trello_id[self.trello_id] = self

    person_by_trello_id = { }

    @classmethod
    def find_person_by_trello_id(cls, trello_id):
        return cls.person_by_trello_id[trello_id]

    @classmethod
    def all_persons(cls):
        return cls.person_by_trello_id.itervalues()

    def __repr__(self):
        return "Person({}, {}, {})".format(self.first_name, self.last_name, self.trello_id)


class Board(object):
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def __str__(self):
        return "{} {}".format(self.name, ', '.join([ str(m) for m in self.members]))

trello = TrelloAPI()

for member in trello.get_members_by_organization('tuisd')['members']:
    names = re.split(r'[_\s]+', member['fullName'])
    first_name = names[0].capitalize()
    last_name = " ".join(names[1:]).capitalize()
    person = Person(first_name, last_name, member['id'])

for board in trello.get_boards_by_organization('tuisd'):
    name = board['name']
    members = [ ]
    for membership in board['memberships']:
        person = Person.find_person_by_trello_id(membership['idMember'])
        members.append(person)
    board = Board(name, members)
    print board
