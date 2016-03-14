import json

from flask import Flask, render_template

from trello import TrelloAPI, Board

app = Flask(__name__)
trello = TrelloAPI()


@app.route('/')
def board_list():
    boards = [{'id': board['id'], 'name': board['name']} for board in trello.get_boards_by_organization('tuisd')]
    return render_template('board-list.html', boards=boards)


@app.route('/board/<id>')
def board_detail(id):
    board = Board.from_json(trello.get_board_details_by_board_id(id))
    return render_template('board-detail.html', board=board)


if __name__ == '__main__':
    app.run(debug=True)
