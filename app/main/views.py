from flask import render_template

from app.models import Organization
from trello import TrelloAPI, Board
from . import main
trello = TrelloAPI()


@main.route('/fetch')
def fetch():
    for org in trello.get_organizations():
        Organization(id=org['id'],
                     name=org['name'],
                     display_name=org['displayName'])
    return "Fetched orgs"


@main.route('/')
def org_list():
    return "hello"
    # return render_template('org-list.html', orgs=Organization.query.all())


@main.route('/orgs/<id>')
def org_detail(id):
    boards = [{'id': board['id'], 'name': board['name']} for board in trello.get_boards_by_organization(id)]
    return render_template('app/main/templates/board-list.html', boards=boards)


@main.route('/boards/<id>')
def board_detail(id):
    board = Board.from_json(trello.get_board_details_by_board_id(id))
    return render_template('app/main/templates/board-detail.html', board=board)