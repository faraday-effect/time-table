from flask import render_template

from . import app


from trello import TrelloAPI, Board
trello = TrelloAPI()


@app.route('/fetch')
def fetch():
    for org in trello.get_organizations():
        models.Organization(id=org['id'],
                            name=org['name'],
                            display_name=org['displayName'])
    return "Fetched orgs"

@app.route('/recreate-db')
def recreate_db():
    models.drop_db()
    models.create_db()
    return "DB recreated"


@app.route('/')
def org_list():
    return "hello"
    # return render_template('org-list.html', orgs=Organization.query.all())


@app.route('/orgs/<id>')
def org_detail(id):
    boards = [{'id': board['id'], 'name': board['name']} for board in trello.get_boards_by_organization(id)]
    return render_template('app/main/templates/board-list.html', boards=boards)


@app.route('/boards/<id>')
def board_detail(id):
    board = Board.from_json(trello.get_board_details_by_board_id(id))
    return render_template('app/main/templates/board-detail.html', board=board)


if __name__ == '__main__':
    app.run(debug=True)
