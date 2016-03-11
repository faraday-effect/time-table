import json

from trello import TrelloAPI


def pprint_json(obj):
    print json.dumps(obj, indent=2)


trello = TrelloAPI()
#card = trello.get_card('56d662b7e6b18f1ca45c3619')
# pprint_json(card)
pprint_json([{'name': org['name'], 'fullname': org['displayName']} for org in trello.get_organizations()])
pprint_json([board['name'] for board in trello.get_boards_by_organization('tuisd')])
pprint_json([member['fullName'] for member in trello.get_members_by_organization('tuisd')['members']])
