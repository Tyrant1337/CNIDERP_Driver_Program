import numpy as np

ROW_COUNT =6
COLUMN_COUNT= 7
def create_board():
    board = np.zeros((6,7))
    return board
def drop_piece(board,row,col,piece):
    pass
def is_valid_loc(board,column):
    return board[5][column] ==0

def get_nex_open_row(board,column):
    for r in range(ROW_COUNT):
        if board[r][column]==0:
            return r
board=create_board()
print (board)
game_over = False
turn = 0
while not game_over:
    #ask for player 1
    if turn==0:
        column= int (input("player one enter your selection from 0-6:"))

    else:
        column = int(input("player two enter your selection from 0-6:"))

    turn +=1
    turn = turn % 2

