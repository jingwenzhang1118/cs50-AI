"""
Tic Tac Toe Player
"""

import copy, math


X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    num_x = 0
    num_o = 0
    for row in board:
        num_x += row.count(X)
        num_o += row.count(O)     
    
    if num_x <= num_o:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions
    


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    status = copy.deepcopy(board)
    if action not in actions(board):
        raise Exception("Invalid action")
    else:
        row, col = action
        status[row][col] = player(board)
        return status


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    num_row = len(board)
    num_col = len(board[0])
    for i in range(num_col):
        if all(x == board[i][0] for x in board[i]) and board[i][0] is not None:
            return board[i][0]
    if all(board[i][i] == board [0][0] for i in range(num_row)) and board[0][0] is not None:
        return board[0][0]
    if all(board[i][num_col - 1 -i] == board[0][2] for i in range(num_col)) and board[0][2] is not None:
        return board[0][2]
    for j in range(num_col):
        if all(board[i][j] == board[0][j] for i in range(num_row)) and board[0][j] is not None:
            return board[0][j]
    return None
    
        


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or not actions:
        return True
    else:
        return False
    


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        if winner(board) == X:
            return 1
        elif winner(board) == O:
            return -1
        else:
            return 0
    

def max_value(board):
    if terminal(board):
        return utility(board)
    
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
        return v

def min_value(board):
    if terminal(board):
        return utility(board)
    
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
        return v



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == "X":
        plays = []
        if actions(board):
            for action in actions(board):
                plays.append((min_value(result(board, action)), action))
            return sorted(plays, key=lambda x: x[0], reverse=True)[0][1]

    else:
        plays = []
        if actions(board):
            for action in actions(board):
                plays.append((max_value(result(board, action)), action))
            return sorted(plays, key=lambda x: x[0])[0][1]


'''
def max_value(board):
    if terminal(board):
        return utility(board), None
    
    v = -math.inf
    move = None
    for action in actions(board):
        value, act = min_value(result(board, action))
        if value > v:
            v = value
            move = act
            if v == 1:
                return v, move
    return v, move

def min_value(board):
    if terminal(board):
        return utility(board), None
    
    v = math.inf
    move = None
    for action in actions(board):
        value, act = max_value(result(board, action))
        if value < v:
            v = value
            move = act
            if v == -1:
                return v, move
    return v, move



    if player(board) == "X":
        value_X = {}
        for action in actions(board):
            while True:
                if terminal(result(board, action)):
                    value_X["action"] = utility(result(board,action))
                    break                 
                else:
                    board = result(board, action)
                    action = minimax(result(board, action))
        return max(value_X, key=value_X.get)
    else:
        value_O = {}
        for action in actions(board):
            while True:
                if terminal(result(board, action)):
                    value_O["action"] = utility(result(board,action))
                    break
                else:
                    board = result(board, action)
                    action = minimax(result(board, action))
        return min(value_O, key=value_O.get)
'''



    
