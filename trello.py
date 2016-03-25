import requests
import json
import re

from dateutil import parser


class TrelloAPI(object):
    def __init__(self):
        with open("trello-keys.json", "r") as f:
            self.auth_params = json.load(f)

    def get(self, url_path, params={}):
        params.update(self.auth_params)
        url = "https://trello.com/1/" + url_path

        response = requests.get(url, params=params)
        if response.status_code != 200:
            request = response.request
            raise RuntimeError("{} request {} returned {}".format(request.method,
                                                                  request.url,
                                                                  response.status_code))
        return response.json()

    def get_card(self, card_id):
        return self.get("card/{}".format(card_id),
                        params={"actions": "commentCard",
                                "members": "true",
                                "fields": "id,dateLastActivity,name"})

    def get_organizations(self):
        return self.get("members/my/organizations")

    def get_boards_by_organization(self, org_name):
        return self.get("organizations/{}/boards".format(org_name),
                        params={'filter': 'open'})

    def get_board_ids_by_organization(self, org_name):
        return [ json['id'] for json in self.get("organizations/{}/boards".format(org_name),
                                                 params={'filter': 'open',
                                                         'fields': 'id'}) ]

    def get_members_by_organization(self, org_name):
        return self.get("organizations/{}".format(org_name),
                        params={'members': 'all'})

    def get_board_details_by_board_id(self, board_id):
        return self.get("boards/{}".format(board_id),
                        params={'organization': 'true',
                                'cards': 'all',
                                'lists': 'all',
                                'actions': 'commentCard',
                                'memberships_member': 'true',
                                'memberships': 'all',
                                'memberships_member_fields': 'fullName,username,memberType,initials'})


class TrelloCollection(object):
    @classmethod
    def add(cls, instance):
        cls.instance_by_trello_id[instance.trello_id] = instance

    @classmethod
    def find(cls, trello_id):
        if trello_id not in cls.instance_by_trello_id:
            raise RuntimeError("No {} with ID {}".format(cls, trello_id))
        return cls.instance_by_trello_id[trello_id]

    @classmethod
    def all(cls):
        return cls.instance_by_trello_id.itervalues()


class Person(TrelloCollection):
    instance_by_trello_id = {}

    def __init__(self, trello_id, first_name, last_name):
        self.trello_id = trello_id
        self.first_name = first_name
        self.last_name = last_name
        self.time_entries = []
        self.add(self)

    @classmethod
    def from_json(cls, person_json):
        names = [name.capitalize() for name in re.split(r'[_\s]+', person_json['fullName'])]
        first_name = names[0]
        last_name = " ".join(names[1:])
        return Person(person_json['id'], first_name, last_name)

    def add_time_entry(self, time_entry):
        self.time_entries.append(time_entry)

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    @property
    def total_time(self):
        spent = estimated = 0
        for time_entry in self.time_entries:
            spent += time_entry.spent
            estimated += time_entry.estimated
        return {'spent': spent, 'estimated': estimated}

    def __repr__(self):
        return "<Person '{} {}'>".format(self.first_name, self.last_name, self.trello_id)


class TimeEntry(TrelloCollection):
    instance_by_trello_id = {}

    def __init__(self, trello_id, datetime, person, who, as_of, spent, estimated, comment, card):
        self.trello_id = trello_id
        self.datetime = datetime
        self.person = person
        self.who = who
        self.as_of = as_of
        self.spent = spent
        self.estimated = estimated
        self.comment = comment
        self.card = card
        card.add_time_entry(self)
        self.add(self)

    time_card_re = re.compile(r"""
                        ^plus!\s+
                        (?P<who>[@\w]+)?\s*
                        (?P<asof>-\d+d)?\s*
                        (?P<spent>-?[\d\.]+)/(?P<est>-?[\d\.]+)\s*
                        (?P<cmt>.*)
                    """, re.VERBOSE)

    @classmethod
    def from_json(cls, time_json):
        person = Person.find(time_json['memberCreator']['id'])
        card = Card.find(time_json['data']['card']['id'])
        text = time_json['data']['text']

        m = cls.time_card_re.match(text)
        if m is None:
            print "Text '{}' didn't match".format(text)
            return None

        time_entry = cls(time_json['id'], parser.parse(time_json['date']), person,
                         m.group('who'), m.group('asof'), float(m.group('spent')), float(m.group('est')), m.group('cmt'),
                         card)
        person.add_time_entry(time_entry)
        return time_entry

    def __repr__(self):
        return "<Time '{}' {}/{}>".format(self.person, self.spent, self.estimated)


class Card(TrelloCollection):
    instance_by_trello_id = {}

    def __init__(self, trello_id, name, desc, url, list):
        self.trello_id = trello_id
        self.name = name
        self.desc = desc
        self.url = url
        self.list = list
        list.add_card(self)
        self.time_entries = []
        self.add(self)

    @classmethod
    def from_json(cls, card_json):
        parent_list = CardList.find(card_json['idList'])
        return cls(card_json['id'], card_json['name'],
                   card_json['desc'], card_json['shortUrl'],
                   parent_list)

    def add_time_entry(self, time_entry):
        self.time_entries.append(time_entry)

    @property
    def has_time_logged(self):
        return len(self.time_entries) > 0

    @property
    def total_time_spent(self):
        return reduce(lambda total, entry: total + entry.spent, self.time_entries, 0)

    @property
    def total_time_estimated(self):
        return reduce(lambda total, entry: total + entry.estimated, self.time_entries, 0)

    @property
    def total_time_remaining(self):
        return self.total_time_estimated - self.total_time_spent

    def __repr__(self):
        return "<Card '{}' [{}]>".format(self.name,
                                         ', '.join([str(te) for te in self.time_entries]))


class CardList(TrelloCollection):
    instance_by_trello_id = {}

    def __init__(self, trello_id, name, closed):
        self.trello_id = trello_id
        self.name = name
        self.closed = closed
        self.cards = []
        self.add(self)

    @classmethod
    def from_json(cls, list_json):
        return cls(list_json['id'], list_json['name'], list_json['closed'])

    def add_card(self, card):
        self.cards.append(card)

    @property
    def has_time_logged(self):
        return any([card.has_time_logged for card in self.cards])

    @property
    def total_time_spent(self):
        return reduce(lambda total, card: total + card.total_time_spent, self.cards, 0)

    @property
    def total_time_estimated(self):
        return reduce(lambda total, card: total + card.total_time_estimated, self.cards, 0)

    @property
    def total_time_remaining(self):
        return self.total_time_estimated - self.total_time_spent

    def __repr__(self):
        return "<CardList '{}' [{}]>".format(self.name,
                                             ', '.join([str(c) for c in self.cards]))


class Board(TrelloCollection):
    instance_by_trello_id = {}

    def __init__(self, trello_id, name, url, members, lists):
        self.trello_id = trello_id
        self.name = name
        self.url = url
        self.members = members
        self.lists = lists
        self.add(self)

    @classmethod
    def from_json(cls, board_json):
        members = [Person.from_json(membership['member'])
                   for membership in board_json['memberships']]
        lists = [CardList.from_json(list_json)
                 for list_json in board_json['lists']]
        for card_json in board_json['cards']:
            Card.from_json(card_json)
        for time_entry_json in board_json['actions']:
            text = time_entry_json['data']['text']
            if text.startswith('plus!'):
                TimeEntry.from_json(time_entry_json)
            else:
                print "Skipped {}".format(text)
        return cls(board_json['id'], board_json['name'], board_json['shortUrl'], members, lists)

    def __repr__(self):
        return "<Board '{}' [{}] [{}]>".format(self.name,
                                               ', '.join([ str(m) for m in self.members]),
                                               ', '.join([ str(l) for l in self.lists]))

