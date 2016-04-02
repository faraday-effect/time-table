from . import db

organization_member = db.Table('organization_member',
                               db.Column('organization_id', db.String(64), db.ForeignKey('organization.id')),
                               db.Column('person_id', db.String(64), db.ForeignKey('person.id')))

board_member = db.Table('board_member',
                        db.Column('board_id', db.String(64), db.ForeignKey('board.id')),
                        db.Column('person_id', db.String(64), db.ForeignKey('person.id')))


class Organization(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)
    members = db.relationship('Person', secondary=organization_member, backref='organizations')

    def __repr__(self):
        return "<Organization '{}'>".format(self.display_name)


class Person(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    def __repr__(self):
        return "<Person '{}'>".format(self.full_name)


class Board(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    members = db.relationship('Person', secondary=board_member, backref='boards')
    # self.lists = lists

    def __repr__(self):
        return "<Board '{}'>".format(self.name)
