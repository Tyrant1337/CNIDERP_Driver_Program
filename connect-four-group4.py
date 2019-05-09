##**************************************************************##
##
##Group 4: Engineering?
##Team Lead: Julia
##Members: Daniel, Davis, Kat, Sharvita
##
##Will play Connect 4 on any dimension semi
##intelligently.
##**DEMO VERSION: FOR 4/15/2019 CLASS ONLY**
##**NOT A FINISHED PRODUCT**
##**Makes zero guarantee of winning
##**Has been tested using provided driver/graphical environment
##**and plays nicely, does not crash and CAN play to a draw.
##**Has NOT been tested using any other driver/graphical setup.
##
## a) Uncommenting elif vert_ok in s:  meh.append(r)
##will give vertical and horizontal same weight.
## b) Include the following two sections to give
##horizontal offence and defence same weight:
##elif player not in hor and flag == 0 and 0 not in under:
##and
##elif player not in hor and flag == 1:
##
##Areas of improvement:
## 1) List of meh moves can be handled better.  Instead
##of giving all moves equal weight before randomy
##choosing, maybe reduce list to single best meh move
##and just return that list of one element.  Also
##meh can be expanded to build more sequences.
## 2) Meh only plays offense, maybe include defensive
##strategy?
## 3) List of ok moves still doesn't check if row
##beneath is properly populated.
## 4) Before removing element from moves list
##ensure its absolutely necessary.
##
##Might play around with:
## 1) All the opening if else/if statements to ensure list meh
##gets a lot of moves, see 1 from above.
##
##**STRANGE ISSUE I DONT UNDERSTAND AND CANT DUPLICATE!
##**ALSO UNSURE IF EVEN STILL EXISTS, NEED MORE TESTING
##After changing board dimensions via
##gui Edit->Preferences Width or Row, algo SOMETIMES returns a
##full column and crashes game.  This does not always happen.
##Changing dimensions inside graphical-driver.rkt at
##define HEIGHT and define WIDTH does not cause this behavior.
##Maybe because changes to .rkt file need save and then reload
##of game board to take effect??
##
##**************************************************************##


import random
import sys
import json

sys.stderr.write("Connect Four - Python\n")

# This is fragile and relies on the fact that the driver always passes the
# command line arguments in the order --player <p> --width <w> --height <h>.
player = int(sys.argv[2]) # --player <p>
width = int(sys.argv[4]) # --width <w>
height = int(sys.argv[6]) # --height <h>

sys.stderr.write("player = " + str(player) + '\n')
sys.stderr.write(" width = " + str(width) + '\n')
sys.stderr.write("height = " + str(height) + '\n')


def valid_moves(state):
    """Returns the valid moves for the state as a list of integers."""
    grid = state['grid'] #list of lists, the game board by columns starting upper left corner
    moves = [] #list of valid column moves
    offence = [] #list of moves that will win the game for us
    defence = [] #list of opponent moves that will win game
    ok = [] #list of moves that would be good to make
    meh = [] #list of so so moves
    connect = 4 #length of winning sequence


    #If middle of bottom row is empty play there and return
    r = int(width/2)
    if grid[r][height-1] == 0:
        offence.append(r)
        return offence
    

    #These are the non-full columns, IE can accept a move
    #At this point available columns/moves are equally weighted at 1
    #Might play with this fact later
    for i in range(width):
        if grid[i][0] == 0:
            moves.append(i)


    ##Checking if we received a full game board.  This should never happen
    ##but doesn't hurt to make sure.
    if len(moves) == 0:
        sys.stderr.write("CRITICAL ERROR: WE RECEIVED A FULL GAME BOARD!\n")
        sys.stderr.write("Graceful exit is playing column 0 and hoping ")
        sys.stderr.write("for the best.\n")
        offence.append(0)
        return offence


    #Who is player and who is opponent
    if player == 1:
        opponent = 2
        good = '01010' #need a better way for these
        good1 = '00110'
        good2 = '01100'
        bad = '02020'
        bad1 = '00220'
        bad2 = '02200'
        
    else:
        opponent = 1
        good = '02020'
        good1 = '02200'
        good2 = '00220'
        bad = '01010'
        bad1 = '01100'
        bad2 = '00110'
        
        
    #Vertical placement, cheap and easy and bulletproof
    vert_wn = '0' + ''.join(str(player) for x in range(connect-1))
    vert_ls = '0' + ''.join(str(opponent) for x in range(connect-1))
    vert_ok = '0' + ''.join(str(player) for x in range(connect-2))
    r = -1
    for list in grid:
        r += 1
        s = ''.join(str(x) for x in list)
        if vert_wn in s:    offence.append(r)
        elif vert_ls in s:  defence.append(r)
        #elif vert_ok in s:  meh.append(r)
        #uncomment above line if we want give vertical movemet equal weight as horizontal/diagnol movement
        #My vote is comment it out and give more weight to horizontal/diagnol greater flexability

        
    #Horizontal and diagnol placement
    for x in range(width-connect+1):
        a = grid[x]
        b = grid[x+1]
        c = grid[x+2]
        d = grid[x+3]
        for y in range(height):
            flag = 1
            if y != height-1:
                w = y + 1
                under = a[w:w+1] + b[w:w+1] + c[w:w+1] + d[w:w+1]
                flag = 0
            hor = a[y:y+1] + b[y:y+1] + c[y:y+1] + d[y:y+1]
            count = sum(hor) #horizontal checking
            if opponent not in hor and count == player*3 and flag == 0 and 0 not in under:
                sys.stderr.write("hori winning move not on bottom\n")
                if hor[0] == 0:   offence.append(x)
                elif hor[1] == 0: offence.append(x+1)
                elif hor[2] == 0: offence.append(x+2)
                elif hor[3] == 0: offence.append(x+3)
            elif opponent not in hor and count == player*3 and flag == 1:
                sys.stderr.write("hori winning move on bottom\n")
                if hor[0] == 0:   offence.append(x)
                elif hor[1] == 0: offence.append(x+1)
                elif hor[2] == 0: offence.append(x+2)
                elif hor[3] == 0: offence.append(x+3)
            elif player not in hor and count == opponent*3 and flag == 0 and 0 not in under:
                sys.stderr.write("hori losing move not on bottom\n")
                if hor[0] == 0:   defence.append(x)
                elif hor[1] == 0: defence.append(x+1)
                elif hor[2] == 0: defence.append(x+2)
                elif hor[3] == 0: defence.append(x+3)
            elif player not in hor and count == opponent*3 and flag == 1:
                sys.stderr.write("hori losing move on bottom\n")
                if hor[0] == 0:   defence.append(x)
                elif hor[1] == 0: defence.append(x+1)
                elif hor[2] == 0: defence.append(x+2)
                elif hor[3] == 0: defence.append(x+3)
            elif player not in hor and count == opponent*3 and flag == 0 and 0 in under:
                sys.stderr.write("hori losing move not on bottom IF WE SET IT UP\n")
                if hor[0] == 0 and x in moves:     moves.remove(x)
                elif hor[1] == 0 and x+1 in moves: moves.remove(x+1)
                elif hor[2] == 0 and x+2 in moves: moves.remove(x+2)
                elif hor[3] == 0 and x+3 in moves: moves.remove(x+3)
            elif opponent not in hor and flag == 0 and 0 not in under:
                sys.stderr.write("hori winning setup move not on bottom\n")
                if hor[1] == 0:   meh.append(x+1)
                elif hor[2] == 0: meh.append(x+2)
                elif hor[3] == 0: meh.append(x+3)
                elif hor[0] == 0: meh.append(x)
            elif opponent not in hor and flag == 1:
                sys.stderr.write("hori winning setup move on bottom\n")
                if hor[2] == 0:   meh.append(x+2)
                elif hor[1] == 0: meh.append(x+1)
                elif hor[0] == 0: meh.append(x)
                elif hor[3] == 0: meh.append(x+3)
            if y < height-connect+1: #diagnol checking
                w = y + 1
                hor = a[y:y+1] + b[y+1:y+2] + c[y+2:y+3] + d[y+3:y+4]
                count = sum(hor)
                if y < height-connect:
                    under = a[w:w+1] + b[w+1:w+2] + c[w+2:w+3] + d[w+3:y+4]
                elif y == height-connect:
                    under = a[w:w+1] + b[w+1:w+2] + c[w+2:w+3]                    
                if opponent not in hor and count == player*3 and 0 not in under:
                    sys.stderr.write("backslash winning move\n")
                    if hor[0] == 0:   offence.append(x)
                    elif hor[1] == 0: offence.append(x+1)
                    elif hor[2] == 0: offence.append(x+2)
                    elif hor[3] == 0: offence.append(x+3)
                elif player not in hor and count == opponent*3 and 0 not in under:
                    sys.stderr.write("backslash losing move\n")
                    if hor[0] == 0:   defence.append(x)
                    elif hor[1] == 0: defence.append(x+1)
                    elif hor[2] == 0: defence.append(x+2)
                    elif hor[3] == 0: defence.append(x+3)
                elif player not in hor and count == opponent*3 and 0 in under:
                    sys.stderr.write("backslash losing move IF WE SET IT UP\n")
                    if hor[0] == 0 and x in moves:     moves.remove(x)
                    elif hor[1] == 0 and x+1 in moves: moves.remove(x+1)
                    elif hor[2] == 0 and x+2 in moves: moves.remove(x+2)
                hor = a[y+3:y+4] + b[y+2:y+3] + c[y+1:y+2] + d[y:y+1]
                count = sum(hor)
                if y < height-connect:
                    under = a[w+3:w+4] + b[w+2:w+3] + c[w+1:w+2] + d[w:w+1]
                elif y == height-connect:
                    under = b[w+2:w+3] + c[w+1:w+2] + d[w:w+1]
                if opponent not in hor and count == player*3 and 0 not in under:
                    sys.stderr.write("forwardslash winning move\n")
                    if hor[0] == 0:   offence.append(x)
                    elif hor[1] == 0: offence.append(x+1)
                    elif hor[2] == 0: offence.append(x+2)
                    elif hor[3] == 0: offence.append(x+3)
                elif player not in hor and count == opponent*3 and 0 not in under:
                    sys.stderr.write("forwardslash losing move\n")
                    if hor[0] == 0:   defence.append(x)
                    elif hor[1] == 0: defence.append(x+1)
                    elif hor[2] == 0: defence.append(x+2)
                    elif hor[3] == 0: defence.append(x+3)
                elif player not in hor and count == opponent*3 and 0 in under:
                    sys.stderr.write("forwardslash losing move IF WE SET IT UP\n")
                    if hor[1] == 0 and x+1 in moves:   moves.remove(x+1)
                    elif hor[2] == 0 and x+2 in moves: moves.remove(x+2)
                    elif hor[3] == 0 and x+3 in moves: moves.remove(x+3)

                    
    #For handling sequences that can guarantee victory/defeat in two moves.  Horizontal only.
    #01010 02020 00110 01100 02200 or 00220 on the horizontal.  This works but assumes row
    #beneath is adequately populated, not the best but checking if in moves[] helps.
    transpose = zip(*grid)
    for list in transpose:
        s = ''.join(str(y) for y in list)
        if good in s:
            x = s.find(good)
            x+=2
            sys.stderr.write("found " + good + " at " + str(x) + "\n")
            if x in moves:
                ok.append(x)
        elif good1 in s:
            x = s.find(good1)
            x+=1
            sys.stderr.write("found " + good1 + " at " + str(x) + "\n")
            if x in moves:
                ok.append(x)
        elif good2 in s:
            x = s.find(good2)
            x+=3
            sys.stderr.write("found " + good2 + " at " + str(x) + "\n")
            if x in moves:
                ok.append(x)
        elif bad in s: 
            x = s.find(bad)
            x+=2
            sys.stderr.write("found " + bad + " at " + str(x) + "\n")
            if x in moves:
                ok.append(x)
        elif bad1 in s:
            x = s.find(bad1)
            x+=1
            sys.stderr.write("found " + bad1 + " at " + str(x) + "\n")
            if x in moves:
                ok.append(x)
        elif bad2 in s: 
            x = s.find(bad2)
            x+=3
            sys.stderr.write("found " + bad2 + " at " + str(x) + "\n")
            if x in moves:
                ok.append(x)


    #Removing bad moves from meh and having a list of unique members, need a cleaner way to do this
    meh1 = []
    map(lambda x: not x in meh1 and meh1.append(x), meh)
    for x in meh1:
        if x in moves:
            meh1.remove(x)


    #Time to return a move
    if len(offence) > 0:
        sys.stderr.write("playing offence\n")
        return offence
    elif len(defence) > 0:
        if len(defence) > 1:
            sys.stderr.write("multiple opponent winning moves, no bueno\n")
        sys.stderr.write("playing defence\n")
        return defence
    elif len(ok) > 0:
        sys.stderr.write("playing ok\n")
        return ok
    elif len(meh1) > 0:
        sys.stderr.write("playing meh\n")
        return meh1
    elif len(moves) > 0:
        sys.stderr.write("playing almost random, tried not to make a bad move\n")
        return moves

    sys.stderr.write("playing random\n")
    for i in range(width):
        if grid[i][0] == 0:
            moves.append(i)        
    return moves

    
# Loop reading the state from the driver and writing a random valid move.
for line in sys.stdin:
    sys.stderr.write(line)
    state = json.loads(line)
    action = {}
    action['move'] = random.choice(valid_moves(state))
    msg = json.dumps(action)
    sys.stderr.write(msg + '\n')
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


# Be a nice program and close the ports.
sys.stdin.close()
sys.stdout.close()
sys.stderr.close()
