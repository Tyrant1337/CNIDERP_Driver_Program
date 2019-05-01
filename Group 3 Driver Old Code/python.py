import numpy as np

ROW_COUNT =6
COLUMN_COUNT= 7
def create_board():
    board = np.zeros((6,7))
    return board
def drop_piece(board,row,col,piece):
    board[row][column]= piece
def is_valid_loc(board,column):
    return board[5][column] ==0

def get_nex_open_row(board,column):
    for r in range(ROW_COUNT):
        if board[r][column]==0:
            return r
def print_board(board):
    print(np.flip(board, 0))
def winning_move(board, piece):
    for c in range (COLUMN_COUNT-3):
     for r in range(ROW_COUNT):
         if board[r][c]==piece and board[r][c+1] == piece and board[r][c+2]== piece and board[r][r+3]:
             return True

#check vertical locations for win

board = create_board()
print_board(board)
game_over = False
turn = 0
while not game_over:
    #ask for player 1
    if turn==0:
        column= int (input("player one enter your selection from 0-6:"))

        if is_valid_loc(board,column):
             row = get_nex_open_row(board,column)
        drop_piece(board,row,column,1)
#ask for player 2 info
    else:
        column = int(input("player two enter your selection from 0-6:"))
    if is_valid_loc(board,column):
        row = get_nex_open_row(board,column)
        drop_piece(board,row,column,2)
        if winning_move(board,1):
            turn += 1
            turn = turn % 2

