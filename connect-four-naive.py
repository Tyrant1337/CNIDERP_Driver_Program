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
    grid = state['grid']
    moves = []
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
