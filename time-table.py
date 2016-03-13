import json
import re

from trello import TrelloAPI


def pprint_json(obj):
    print json.dumps(obj, indent=2)


class TrelloCollection(object):
    @classmethod
    def add(cls, instance):
        cls.instance_by_trello_id[instance.trello_id] = instance

    @classmethod
    def find(cls, trello_id):
        return cls.instance_by_trello_id[trello_id]

    @classmethod
    def all(cls):
        return cls.instance_by_trello_id.itervalues()


class Person(TrelloCollection):
    instance_by_trello_id = { }

    def __init__(self, trello_id, first_name, last_name):
        self.trello_id = trello_id
        self.first_name = first_name
        self.last_name = last_name
        self.add(self)

    @classmethod
    def from_json(cls, person_json):
        names = re.split(r'[_\s]+', person_json['fullName'])
        first_name = names[0].capitalize()
        last_name = " ".join(names[1:]).capitalize()
        return Person(person_json['id'], first_name, last_name)

    def __repr__(self):
        return "<Person '{} {}'>".format(self.first_name, self.last_name, self.trello_id)


class TimeEntry(TrelloCollection):
    instance_by_trello_id = { }

    def __init__(self, trello_id, time_stamp, person, spent, estimated, comment, card):
        self.trello_id = trello_id
        self.time_stamp = time_stamp
        self.person = person
        self.spent = spent
        self.estimated = estimated
        self.comment = comment
        self.card = card
        card.add_time_entry(self)
        self.add(self)

    @classmethod
    def from_json(cls, time_json):
        person = Person.find(time_json['memberCreator']['id'])
        card = Card.find(time_json['data']['card']['id'])
        m = re.match(r"^plus! (?P<spent>[\d\.]+)/(?P<est>[\d\.]+)\s*(?P<cmt>.*)",
                     time_json['data']['text'])
        return cls(time_json['id'], time_json['date'], person,
                   float(m.group('est')), float(m.group('spent')), m.group('cmt'),
                   card)

    def __repr__(self):
        return "<Time '{}' {}/{}>".format(self.person, self.spent, self.estimated)


class Card(TrelloCollection):
    instance_by_trello_id = { }

    def __init__(self, trello_id, name, desc, url, list):
        self.trello_id = trello_id
        self.name = name
        self.desc = desc
        self.url = url
        self.list = list
        list.add_card(self)
        self.time_entries = [ ]
        self.add(self)

    @classmethod
    def from_json(cls, card_json):
        list = List.find(card_json['idList'])
        return cls(card_json['id'], card_json['name'],
                   card_json['desc'], card_json['shortUrl'],
                   list)

    def add_time_entry(self, time_entry):
        self.time_entries.append(time_entry)

    def __repr__(self):
        return "<Card '{}' [{}]>".format(self.name,
                                         ', '.join([ str(te) for te in self.time_entries]))


class List(TrelloCollection):
    instance_by_trello_id = { }

    def __init__(self, trello_id, name):
        self.trello_id = trello_id
        self.name = name
        self.cards = [ ]
        self.add(self)

    @classmethod
    def from_json(cls, list_json):
        return cls(list_json['id'], list_json['name'])

    def add_card(self, card):
        self.cards.append(card)

    def __repr__(self):
        return "<List '{}'>".format(self.name)


class Board(TrelloCollection):
    instance_by_trello_id = { }

    def __init__(self, trello_id, name, url, members, lists):
        self.trello_id = trello_id
        self.name = name
        self.url = url
        self.members = members
        self.lists = lists
        self.add(self)

    @classmethod
    def from_json(cls, board_json):
        members = [ Person.from_json(membership['member'])
                    for membership in board_json['memberships'] ]
        lists = [ List.from_json(list_json)
                  for list_json in board_json['lists'] if not list_json['closed'] ]
        for card_json in board_json['cards']:
            Card.from_json(card_json)
        for time_entry_json in board_json['actions']:
            TimeEntry.from_json(time_entry_json)
        return cls(board_json['id'], board_json['name'], board_json['shortUrl'], members, lists)

    def __repr__(self):
        return "<Board '{}' [{}] [{}] [{}]>".format(self.name,
                                                    ', '.join([ str(m) for m in self.members]),
                                                    ', '.join([ str(l) for l in self.lists]),
                                                    ', '.join([str(c) for c in self.cards]))


trello = TrelloAPI()

for board_id in trello.get_board_ids_by_organization('tuisd'):
    board_json = trello.get_board_details_by_board_id(board_id)
    pprint_json(board_json)
    board = Board.from_json(board_json)
    print board
    exit(1)

for member_json in trello.get_members_by_organization('tuisd')['members']:
    Person.from_json(member_json)

for board_json in trello.get_boards_by_organization('tuisd'):
    Board.from_json(board_json)

for person in Person.all():
    print person

for board in Board.all():
    print board
