import json

from flask import Flask, render_template

from trello import TrelloAPI, Board

def pprint_json(obj):
    print json.dumps(obj, indent=2)


app = Flask(__name__)
trello = TrelloAPI()

@app.route('/')
def board_list():
    boards = [{'id': board['id'], 'name': board['name']}
              for board in trello.get_boards_by_organization('tuisd')]
    return render_template('board-list.html', boards=boards)

@app.route('/board/<id>')
def board_detail(id):
    board = Board.from_json(trello.get_board_details_by_board_id(id))
    return render_template('board-detail.html', board=board)

#
# for board_id in trello.get_board_ids_by_organization('tuisd'):
#     board_json = trello.get_board_details_by_board_id(board_id)
# #    pprint_json(board_json)
#     board = Board.from_json(board_json)
#     print board
# #
#     exit(1)
# for member_json in trello.get_members_by_organization('tuisd')['members']:
#     Person.from_json(member_json)
#
# for board_json in trello.get_boards_by_organization('tuisd'):
#     Board.from_json(board_json)
#
# for person in Person.all():
#     print person
#
# for board in Board.all():
#     print board

if __name__ == '__main__':
    app.run(debug=True)
