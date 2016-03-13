import requests
import json


class TrelloAPI(object):
    def __init__(self):
        with open("trello-keys.json", "r") as f:
            self.auth_params = json.load(f)

    def get(self, url_path, params={}):
        params.update(self.auth_params)
        url = "https://trello.com/1/" + url_path

        response = requests.get(url, params=params)
        print response.request.url
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
