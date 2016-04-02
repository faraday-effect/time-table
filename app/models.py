import os


class Organization(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return "<Organization '{}'>".format(self.display_name)


class Person(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)

    @property
    def full_name(self):
        return " ".join(self.first_name, self.last_name)

    def __repr__(self):
        return "<Person '{}'>".format(self.full_name)
