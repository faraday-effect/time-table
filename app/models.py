import re

from dateutil import parser

from . import db
from . import trello

organization_member = db.Table('organization_member',
                               db.Column('organization_id', db.String(64), db.ForeignKey('organization.id')),
                               db.Column('person_id', db.String(64), db.ForeignKey('person.id')))

board_member = db.Table('board_member',
                        db.Column('board_id', db.String(64), db.ForeignKey('board.id')),
                        db.Column('person_id', db.String(64), db.ForeignKey('person.id')))


class ModelMixin(object):
    @classmethod
    def get_or_create(cls, from_json):
        instance = cls.query.get(from_json['id'])
        if instance is None:
            instance = cls.from_json(from_json)
            print "{} CREATED".format(instance)
        else:
            print "{} exists".format(instance)
        return instance


class Person(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    time_entries = db.relationship('TimeEntry', backref='person')

    @classmethod
    def from_json(cls, person_json):
        names = [name.capitalize() for name in re.split(r'[_\s]+', person_json['fullName'])]
        first_name = names[0]
        last_name = " ".join(names[1:])
        person = cls(id=person_json['id'],
                     first_name=first_name,
                     last_name=last_name)
        db.session.add(person)
        return person

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    def __repr__(self):
        return "<Person '{}'>".format(self.full_name)


class Organization(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)
    members = db.relationship('Person', secondary=organization_member, backref='organizations')

    @classmethod
    def from_json(cls, org_json):
        org_name = org_json['name']
        org = cls(id=org_json['id'],
                  name=org_name,
                  display_name=org_json['displayName'],
                  members=[Person.get_or_create(member_json) for member_json in trello.get_members_by_organization(org_name)])
        db.session.add(org)
        return org

    def __repr__(self):
        return "<Organization '{}'>".format(self.display_name)


class Board(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    members = db.relationship('Person', secondary=board_member, backref='boards')
    lists = db.relationship('CardList', backref='board')

    @classmethod
    def from_json(cls, board_json):
        return cls(id=board_json['id'],
                   name=board_json['name'],
                   members=[Person.get_or_create(member_json) for member_json in board_json['members']],
                   lists=[CardList.get_or_create(list_json) for list_json in board_json['lists']])

    def __repr__(self):
        return "<Board '{}'>".format(self.name)


class CardList(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    closed = db.Column(db.Boolean)
    board_id = db.Column(db.String(64), db.ForeignKey('board.id'))
    cards = db.relationship('Card', backref='card_list')

    @classmethod
    def from_json(cls, list_json):
        list_id = list_json['id']
        card_list = cls(id=list_id,
                        name=list_json['name'],
                        closed=list_json['closed'],
                        cards=[Card.get_or_create(card_json) for card_json in trello.get_cards_by_list_id(list_id)])
        db.session.add(card_list)
        return card_list

    def __repr__(self):
        return "<CardList '{}'>".format(self.name)


class Card(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.String(255))
    list_id = db.Column(db.String(64), db.ForeignKey('card_list.id'))
    time_entries = db.relationship('TimeEntry', backref='card')

    @classmethod
    def from_json(cls, card_json):
        card_id = card_json['id']
        card = cls(id=card_id,
                   name=card_json['name'],
                   desc=card_json['desc'],
                   time_entries=[TimeEntry.get_or_create(time_json) for time_json in trello.get_actions_by_card_id(card_id)])
        db.session.add(card)
        return card

    def __repr__(self):
        return "<Card '{}'>".format(self.name)


class TimeEntry(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    datetime = db.Column(db.DateTime())
    spent = db.Column(db.REAL)
    estimated = db.Column(db.REAL)
    comment = db.Column(db.String(255))
    person_id = db.Column(db.String(64), db.ForeignKey('person.id'))
    card_id = db.Column(db.String(64), db.ForeignKey('card.id'))

    time_card_re = re.compile(r"""
                        ^plus!\s+
                        (?P<who>[@\w]+)?\s*
                        (?P<asof>-\d+d)?\s*
                        (?P<spent>-?[\d\.]+)/(?P<est>-?[\d\.]+)\s*
                        (?P<cmt>.*)
                    """, re.VERBOSE)

    @classmethod
    def from_json(cls, time_json):
        entry_id=time_json['id']
        entry_datetime=parser.parse(time_json['date'])
        entry_person=Person.get_or_create(time_json['memberCreator'])

        text = time_json['data']['text']
        m = cls.time_card_re.match(text)

        if m is None:
            print "WARNING: text '{}' didn't match".format(text)
            time_entry = cls(id=entry_id,
                             datetime=entry_datetime,
                             person=entry_person,
                             spent=0.0,
                             estimated=0.0,
                             comment=text)
        else:
            time_entry = cls(id=entry_id,
                             datetime=entry_datetime,
                             person=entry_person,
                             spent=float(m.group('spent')),
                             estimated=float(m.group('est')),
                             comment=m.group('cmt'))
        db.session.add(time_entry)
        return time_entry

    def __repr__(self):
        return "<Time '{}' S{}/E{}>".format(self.person.full_name, self.spent, self.estimated)
