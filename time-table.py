import json

from flask import Flask, render_template

from trello import TrelloAPI, Board

app = Flask(__name__)
trello = TrelloAPI()


@app.route('/')
def org_list():
    orgs = [{'name': org['name'], 'displayname': org['displayName']} for org in trello.get_organizations()]
    return render_template('org-list.html', orgs=orgs)


@app.route('/orgs/<id>')
def org_detail(id):
    boards = [{'id': board['id'], 'name': board['name']} for board in trello.get_boards_by_organization(id)]
    return render_template('board-list.html', boards=boards)


@app.route('/boards/<id>')
def board_detail(id):
    board = Board.from_json(trello.get_board_details_by_board_id(id))
    return render_template('board-detail.html', board=board)


if __name__ == '__main__':
    app.run(debug=True)
