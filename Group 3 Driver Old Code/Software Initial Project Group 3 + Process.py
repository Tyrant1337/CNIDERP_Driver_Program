import json
from subprocess import Popen, PIPE
from sys import executable, argv


class Game:
    def __init__(self, height, width, goal):
        # pass as argument for player program file
        # self.playerfile = playerfile
        self.gBoard = Board(height, width, goal)
        self.height = height
        self.width = width
        self.goal = goal
        self.p1error = open("player1error.txt", "w")
        self.p2error = open("player2error.txt", "w")


    # return 1 if player 1 wins, 2 if player 2 wins, 0 if game continues, 3 if no moves left
    def playTurn(self, playerNum):
        # get the move from the player (currently just randomly generates a valid column)
        colIndex = self.getMove(playerNum)

        # add the move to the board, which returns the row it was placed
        rowIndex = self.gBoard.makeMove(colIndex, playerNum)

        # print the board to the screen
        self.gBoard.printBoard()

        # check if there is a win
        if self.gBoard.checkIfWon(rowIndex, colIndex, playerNum):
            # indicate the player won
            return playerNum
        # if the latest placed piece is in the top row, check if grid is full
        elif rowIndex == 0:
            if self.gBoard.checkIfFull():
                # indicate a cats game
                return 3
        else:
            # indicate there is no win yet
            return 0


    # this is called once to play the game
    def playGame(self):
        # initalize turnCode
        turnCode = 0

        # player 1 goes first
        turn = 1
        # continuously loop until game ends
        while (True):
            # play the turn, which returns the turn code
            turnCode = self.playTurn(turn)

            # if it's 1 or 2, that player won
            if turnCode == 1:
                print("Player 1 wins")
                return turnCode
            elif turnCode == 2:
                print("Player 2 wins")
                return turnCode
            # if -1, board is filled up
            elif turnCode == 3:
                print("Cats game")
                return turnCode
            # otherwise, change whose turn it is
            else:
                if turn == 1:
                    turn = 2
                else:
                    turn = 1


    # this gets the move from the player whose turn it is
    # right now it just generates a random valid column number
    # uses checkIfValid to make sure move is valid
    def getMove(self, turn):
        player1 = Popen(
            [executable, "connect-four-group4.py", "1", "1", str(self.width), str(self.width), str(self.height),
             str(self.height)],
            stdin=PIPE, stdout=PIPE, stderr=self.p1error)

        player2 = Popen(
            [executable, "connect-four-group4.py", "2", "2", str(self.width), str(self.width), str(self.height),
             str(self.height)],
            stdin=PIPE, stdout=PIPE, stderr=self.p2error)
        players = player1, player2
        turn -= 1

        while (True):
            # send current board to player on stdout
            myboard = json.dumps(self.gBoard.grid)
            myboard = (myboard + '\n').encode("utf-8")
            players[turn].stdin.write(myboard)
            players[turn].stdin.flush()

            # get move from player program
            move = json.loads(players[turn].stdout.readline())
            move = int(move["move"])
            print("Player " + str(turn + 1) + " move: " + str(move))

            # check if move is valid, return move if it's good
            if self.checkIfValid(move):
                return move


    # tests whether move sent to driver is valid
    # returns true if valid and false otherwise
    def checkIfValid(self, column):
        # if an inbounds column and if that columns' highest row is unoccupied
        if column < self.gBoard.width and column >= 0 and self.gBoard.grid["grid"][column][0] == 0:
            return True
        return False


class Board:
    # initalizes board
    # height = # of rows
    # width = # of columns
    # goal = how many to get in a row
    def __init__(self, height, width, goal):
        self.grid = {}
        self.grid["grid"] = [[0] * height for i in range(width)]
        self.height = height
        self.width = width
        self.goal = goal


    # check if grid has no spots left
    # returns true if full, false otherwise
    def checkIfFull(self):
        for column in range(0, self.width):
            # if any column's highest piece is 0, return false
            if self.grid["grid"][column][0] == 0:
                return False
        # otherwise, return true
        return True


    # calls checkVertical, checkHorizontal, and checkDiagonal
    # if any return true, return true. If not, return false
    def checkIfWon(self, newRowIndex, newColIndex, playerNum):
        if self.checkVertical(newRowIndex, newColIndex, playerNum) or \
                self.checkHorizontal(newRowIndex, newColIndex, playerNum) or \
                self.checkDiagonal(newRowIndex, newColIndex, playerNum):
            return True
        return False


    # checks if there are 3 of that player's pieces under that player's last placed piece
    # note: don't need to check above because pieces can't be above it per the game rules
    def checkVertical(self, newRowIndex, newColIndex, playerNum):
        below = self.checkDirection(newRowIndex, newColIndex, 0, 1, playerNum)
        if below + 1 >= self.goal:
            return True
        return False


    # checks to the left and right of the piece, checks if there are 4 in a row horizontally
    def checkHorizontal(self, newRowIndex, newColIndex, playerNum):
        left = self.checkDirection(newRowIndex, newColIndex, -1, 0, playerNum)
        # print(left)
        right = self.checkDirection(newRowIndex, newColIndex, 1, 0, playerNum)
        # print(right)
        if left + right + 1 >= self.goal:
            # print("Hoizontal win")
            return True
        return False


    # calls checkLeftUp2DownRight and checkLeftDown2RightUp
    # if either returns true, return true, otherwise return false
    def checkDiagonal(self, newRowIndex, newColIndex, playerNum):
        if self.checkLeftUp2RightDown(newRowIndex, newColIndex, playerNum) or \
                self.checkLeftDown2RightUp(newRowIndex, newColIndex, playerNum):
            return True
        return False


    # checks to the left up and down right for matching pieces, checks if more than 4 in a row
    def checkLeftUp2RightDown(self, newRowIndex, newColIndex, playerNum):
        leftUp = self.checkDirection(newRowIndex, newColIndex, -1, -1, playerNum)
        rightDown = self.checkDirection(newRowIndex, newColIndex, 1, 1, playerNum)
        if leftUp + rightDown + 1 >= self.goal:
            return True
        return False


    # checks to the left down and right up for matching pieces, checks if more than 4 in a row
    def checkLeftDown2RightUp(self, newRowIndex, newColIndex, playerNum):
        leftDown = self.checkDirection(newRowIndex, newColIndex, 1, -1, playerNum)
        rightUp = self.checkDirection(newRowIndex, newColIndex, -1, 1, playerNum)
        if leftDown + rightUp + 1 >= self.goal:
            return True
        return False


    # takes a row index and column index and returns whether it is in bounds or not
    def inBounds(self, rowIndex, colIndex):
        if rowIndex < 0 or rowIndex > self.height - 1:
            return False
        if colIndex < 0 or colIndex > self.width - 1:
            return False
        return True


    # make a move
    # this returns the row the piece was placed in
    def makeMove(self, column, playerNum):
        # starting from lowest column...
        for row in range(self.height - 1, -1, -1):
            # if row is empty...
            if self.grid["grid"][column][row] == 0:
                # put the move there
                self.grid["grid"][column][row] = playerNum
                # return the row
                return row


    # prints the board
    # prints it as it should appear rather than in column-major format
    def printBoard(self):
        for row in range(0, self.height):
            for column in range(0, self.width):
                print(self.grid["grid"][column][row], end=" ")
            print()
        print()


    # colDir of -1 means to decrease the colIndex as you search
    # rowDir of 1 means to increase the rowIndex as you search
    def checkDirection(self, newRowIndex, newColIndex, colDir, rowDir, playerNum):
        for count in range(0, self.goal - 1):
            # get the next indexes to check
            # note: the + 1's are used to skip the spot that the latest added piece occupies
            nextRowIndex = int(newRowIndex) + ((int(count + 1)) * int(rowDir))
            nextColIndex = newColIndex + ((count + 1) * colDir)
            # check if out of bounds
            if self.inBounds(nextRowIndex, nextColIndex) == False:
                return count
                # if the spot is not the player whose turn it is
            if self.grid["grid"][nextColIndex][nextRowIndex] != playerNum:
                # print(count)
                return count
        # if it reaches here, have already found a win, return goal-1 which with the new spot is a win
        return self.goal - 1


# playerfile = str(argv[0])

height = 6
width = 7
goal = 4

newGame = Game(height, width, goal)
newGame.playGame()
