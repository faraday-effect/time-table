import re

from . import db

organization_member = db.Table('organization_member',
                               db.Column('organization_id', db.String(64), db.ForeignKey('organization.id')),
                               db.Column('person_id', db.String(64), db.ForeignKey('person.id')))

board_member = db.Table('board_member',
                        db.Column('board_id', db.String(64), db.ForeignKey('board.id')),
                        db.Column('person_id', db.String(64), db.ForeignKey('person.id')))


class ModelMixin(object):
    @classmethod
    def get_or_create(cls, **kwargs):
        created = False
        instance = cls.query.get(kwargs['id'])
        if instance is None:
            instance = cls(**kwargs)
            created = True
        instance.print_status(created)
        return instance, created

    @classmethod
    def get_or_create_json(cls, from_json):
        created = False
        instance = cls.query.get(from_json['id'])
        if instance is None:
            instance = cls.from_json(from_json)
            created = True
        instance.print_status(created)
        return instance, created

    def print_status(self, created):
        if created:
            print "Created {}".format(self)
        else:
            print "{} exists".format(self)


class Organization(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)
    members = db.relationship('Person', secondary=organization_member, backref='organizations')

    @classmethod
    def from_json(cls, org_json):
        return Organization(id=org_json['id'],
                            name=org_json['name'],
                            display_name=org_json['displayName'])

    def __repr__(self):
        return "<Organization '{}'>".format(self.display_name)


class Person(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)

    @classmethod
    def from_json(cls, person_json):
        names = [name.capitalize() for name in re.split(r'[_\s]+', person_json['fullName'])]
        first_name = names[0]
        last_name = " ".join(names[1:])
        return Person(id=person_json['id'],
                      first_name=first_name,
                      last_name=last_name)

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    def __repr__(self):
        return "<Person '{}'>".format(self.full_name)


class Board(db.Model, ModelMixin):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    members = db.relationship('Person', secondary=board_member, backref='boards')
    # self.lists = lists

    @classmethod
    def from_json(cls, board_json):
        return Board(id=board_json['id'],
                     name=board_json['name'])

    def __repr__(self):
        return "<Board '{}'>".format(self.name)
