# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 15:12:41 2019

@author: bamar
"""

#import random
import sys
import json
import multiprocessing


class game:
    
    def __init__(self, height, width, goal):
        self.gBoard = board(self, height, width, goal)
        self.turn = 1
        #must figure out where to direct these streams
        self.p1in = sys.stdin
        self.p1out = sys.stdout
        self.p1err = sys.stderr
        self.p2in = sys.stdin
        self.p2out = sys.stdout
        self.p2err = sys.stderr
        #start the 2 player processes here

     def sendBoard(boardString):
     #creating a pipe
     #parent_conn, child_conn = multiprocessing.Pipe()
     #creating new processes
     #p1 = multiprocessing.Process(target=sender, args=(parent_conn,msgs))


    #return 1 if player 1 wins, 2 if player 2 wins, 0 if game continues, -1 if no moves left, -2 if invalid
    def playTurn(self, playerNum, theMove):
        # check if move is valid
        row = self.gBoard.makeMove(theMove, playerNum)
        if row == None:
            return -2
        winner = self.gBoard.checkIfWon(row, theMove, playerNum)
        if winner:
            return playerNum
        else:
            for row in self.gBoard.grid:
                for cell in row:
                    if cell == 0:
                        return 0
            return -1


    def playGame(self):
        turnCode = 0
        turn = 1
        move = 0
        while(True):
            if turn == 1:
                move = self.p1in.readline()
            else:
                move = self.p2in.readline()
            turnCode = self.playTurn(turn, move)
            if turnCode == 1:
                print("Player 1 wins")
                return turnCode
            elif turnCode == 2:
                print("Player 2 wins")
                return turnCode
            elif turnCode == -1:
                print("Cats game")
                return turnCode
            elif turnCode == -2:
                print("Invalid move")
                #turn needs to stay with current player
                if turn == 1:
                    turn = 2
                else:
                    turn = 1
            #send board to appropriate player
            if turn == 1:
                json.dump(self.gBoard.grid, self.p2out)
                turn = 2
            else:
                json.dump(self.gBoard.grid, self.p1out)
                turn = 1

        
    

class board:
    
    #initalizes board
    #height = # of rows
    #width = # of columns
    #goal = how many to get in a row
    def __init__(self, height, width, goal):
        self.height = height
        self.width = width
        self.goal = goal
        #initialize grid at correct width and height
        self.grid = [[0 for x in range(height)] for y in range(width)]
        #set player 1 to go first

    def checkIfWon(self, newRowNum, newColNum, playerNum):
        # if self.checkVertical(newRowNum, newColNum, playerNum) or self.checkHorizontal(newRowNum, newColNum, playerNum) or self.checkDiagonal(newRowNum, newColNum, playerNum):
        #     return True
        if self.checkAllDirections(newRowNum, newColNum, playerNum):
            return True
        return False

    def checkAllDirections(self, newRowNum, newColNum, playerNum):
        directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
        for x, y in directions:
            ret = self.checkDirection(newRowNum, newColNum, y, x, playerNum)
            if ret >= self.goal:
                return True
        return False


    # def checkIfWon(self, newRowNum, newColNum, playerNum):
    #     if self.checkVertical(newRowNum, newColNum, playerNum) or self.checkHorizontal(newRowNum, newColNum, playerNum) or self.checkDiagonal(newRowNum, newColNum, playerNum):
    #         return True
    #     return False
    #
    # def checkVertical(self, newRowNum, newColNum, playerNum):
    #     below = self.checkDirection(newRowNum, newColNum, 1, 0, playerNum)
    #     if below + 1 >= self.goal:
    #         return True
    #     return False
    #
    # def checkHorizontal(self, newRowNum, newColNum, playerNum):
    #     left = self.checkDirection(newRowNum, newColNum, 0, -1, playerNum)
    #     print(left)
    #     right = self.checkDirection(newRowNum, newColNum, 0, 1, playerNum)
    #     print(right)
    #     if left + right + 1 >= self.goal:
    #         print("Hoizontal win")
    #         return True
    #     return False
    #
    # def checkDiagonal(self, newRowNum, newColNum, playerNum):
    #     if self.checkLeftUp2RightDown(newRowNum, newColNum, playerNum) or self.checkLeftDown2RightUp(newRowNum, newColNum, playerNum):
    #         return True
    #     return False
    #
    # def checkLeftUp2RightDown(self, newRowNum, newColNum, playerNum):
    #     leftUp = self.checkDirection(newRowNum, newColNum, -1, -1, playerNum)
    #     rightDown = self.checkDirection(newRowNum, newColNum, 1, 1, playerNum)
    #     if leftUp + rightDown + 1 >= self.goal:
    #         return True
    #     return False
    #
    # def checkLeftDown2RightUp(self, newRowNum, newColNum, playerNum):
    #     leftDown = self.checkDirection(newRowNum, newColNum, 1, -1, playerNum)
    #     rightUp = self.checkDirection(newRowNum, newColNum, -1, 1, playerNum)
    #     if leftDown + rightUp + 1 >= self.goal:
    #         return True
    #     return False
    #
    # def checkDirection(self, newRowNum, newColNum, colDir, rowDir, playerNum):
    #     for count in range(0, self.goal-2):
    #         #check if out of bounds
	# 		#note: the + 1's are used to skip the spot that the latest added piece occupies
    #         if self.inBounds(newRowNum + ((count+1)*rowDir), newColNum + ((count+1)*colDir)) == False:
    #             return count
    #         #if the spot is not the player whose turn it is
    #         if self.grid[newColNum + (colDir+1*count)][newRowNum+(rowDir*(count+1))] != playerNum:
    #             print(count)
    #             return count
    #     #if it reaches here, have already found a win, return goal-1 which with the new spot is a win
    #     return self.goal-1
        
    #takes a row index and column index and returns whether it is in bounds or not
    def inBounds(self, rowIndex, colIndex):
        if rowIndex < 0 or rowIndex > self.width:
            return False
        if colIndex < 0 or colIndex > self.height:
            return False
        return True
        
    #make a move
    def makeMove(self, column, playerNum):
        #starting from lowest column...
        for each in range(self.height-1, -1, -1):
            #if row is empty...
            if self.grid[column][each] == 0:
                #put the move there
                self.grid[column][each] = playerNum
                #return the row 
                return each
        return None
            
    #prints the board 
    def printBoard(self):
        for row in range(0, self.height):
            for column in range(0, self.width):
                print(self.grid[column][row], end=" ")
            print()
                
    #convert the board to a json
    def getBoardAsJSON(self):
        j = json.dumps(self.grid)
        return j
    
    

j = json.loads('{"move" : "4"}')
print(j["move"])
gb = board(6, 7, 4)
gb.makeMove(3,1)
gb.makeMove(3,1)
gb.makeMove(3,1)
gb.makeMove(3,1)

cmd = ['C:/Users/bamar/.spyder-py3/Baseball/dummyPlayer.py', '6', '7']

p = multiprocessing.Process()
p.start()
print(p.pid)
#if pid == 0:
#    process = subprocess.call(cmd, shell=True)
#else:
#    gb.printBoard()
#    print(process)
#    print(gb.getBoardAsJSON())
#    print(os.getpid())



    
