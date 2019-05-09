# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 11:06:49 2019

@author: Lil-G
"""
import random
import sys
import json

sys.stderr.write("Program Started\n")


#Starting Info from Driver
playernum = int(sys.argv[2])
width = int(sys.argv[4])
height = int(sys.argv[6])



'''
playernum = 1
width = 7
height = 6
'''

#Set opponent ID
if playernum is 1:
	notplayernum = 2
else:
	notplayernum = 1

#Initilize empty game grid
grid = []
for y in range(0, height):
	new = []
	for x in range(0, width):
		new.append(0)
	grid.append(new)


'''FUNCTION'''
#Updates grid with program readable symbols
def populategrid(state):
	givengrid = state['grid']
	for col in range(0, width):
		myy = height - 1	
		for row in range(0, height):
			if givengrid[col][row] is playernum:
				grid[myy][col] = '+'
			elif givengrid[col][row] is notplayernum:
				grid[myy][col] = '-'
			else:
				grid[myy][col] = 0
			myy = myy - 1

'''FUNCTION'''
#Prints grid for visual inspection				
def printgrid():
	for y in range (height - 1, -1, -1):
		for x in range(0, width):
			print(" | ", end='')
			print(grid[y][x], end='')
		print(" |")


'''FUNCTION'''
#Determine location to move to		
def attackmode():
	for y in range(0, height):
		for x in range(0, width):
			#initial If
			if grid[y][x] is '+':
				#Up Left Direction
				if ( y + 1) < height and ( x - 1) >= 0 and grid[y + 1][x - 1] is not '-':
					if grid[y + 1][x - 1] is not '+':
						grid[y + 1][x - 1] = grid[y + 1][x - 1 ] + 1
					elif ( y + 2) < height and ( x - 2) >= 0 and grid[y + 2][x - 2] is not '-':
						if grid[y + 2][x - 2] is not '+':
							grid[y + 2][x - 2] = grid[y + 2][x - 2] + 3
						elif ( y + 3) < height and ( x - 3) >= 0 and grid[y + 3][x - 3] is not '-':
							if grid[y + 3][x - 3] is not '+':
								grid[y + 3][x - 3] = grid[y + 3][x - 3] + 99
				#Up Direction				
				if ( y + 1) < height and grid[y + 1][x] is not '-':
					if grid[y + 1][x] is not '+':
						grid[y + 1][x] = grid[y + 1][x] + 2
					elif ( y + 2) < height and grid[y + 2][x] is not '-':
						if grid[y + 2][x] is not '+':
							grid[y + 2][x] = grid[y + 2][x] + 4
						elif ( y + 3) < height and grid[y + 3][x] is not '-':
							if grid[y + 3][x] is not '+':
								grid[y + 3][x] = grid[y + 3][x] + 99
				#Up Right Direction
				if ( y + 1) < height and ( x + 1 ) < width and grid[y + 1][x + 1] is not '-':
					if grid[y + 1][x + 1] is not '+':
						grid[y + 1][x + 1] = grid[y + 1][x + 1] + 1
					elif ( y + 2) < height and ( x + 2 ) < width and grid[y + 2][x + 2] is not '-':
						if grid[y + 2][x + 2] is not '+':
							grid[y + 2][x + 2] = grid[y + 2][x + 2] + 3
						elif ( y + 3) < height and ( x + 3 ) < width and grid[y + 3][x + 3] is not '-':
							if grid[y + 3][x + 3] is not '+':
								grid[y + 3][x + 3] = grid[y + 3][x + 3] + 99
				#Left Direction
				if ( x - 1 ) >= 0 and grid[y][x - 1] is not '-':
					if grid[y][x - 1] is not '+':
						grid[y][x - 1] = grid[y][x - 1] + 1
					elif ( x - 2 ) >= 0 and grid[y][x - 2] is not '-':
						if grid[y][x - 2] is not '+':
							grid[y][x - 2] = grid[y][x - 2] + 5
						elif ( x - 3 ) >= 0 and grid[y][x - 3] is not '-':
							if grid[y][x - 3] is not '+':
								grid[y][x - 3] = grid[y][x - 3] + 99
				#Right Direction
				if ( x + 1 ) < width and grid[y][x + 1] is not '-':
					if grid[y][x + 1] is not '+':
						grid[y][x + 1] = grid[y][x + 1] + 1
					elif ( x + 2 ) < width and grid[y][x + 2] is not '-':
						if grid[y][x + 2] is not '+':
							grid[y][x + 2] = grid[y][x + 2] + 5
						elif ( x + 3 ) < width and grid[y][x + 3] is not '-':
							if grid[y][x + 3] is not '+':
								grid[y][x + 3] = grid[y][x + 3] + 99
				#Down Left Direction
				if ( x - 1 ) >= 0 and (y - 1) >= 0 and grid[y - 1][x - 1] is not '-':
					if grid[y - 1][x - 1] is not '+':
						grid[y - 1][x - 1] = grid[y - 1][x - 1] + 1
					elif ( x - 2 ) >= 0 and (y - 2) >= 0 and grid[y - 2][x - 2] is not '-':
						if grid[y - 2][x - 2] is not '+':
							grid[y - 2][x - 2] = grid[y - 2][x - 2] + 3
						elif ( x - 3 ) >= 0 and (y - 3) >= 0 and grid[y - 3][x - 3] is not '-':
							if grid[y - 3][x - 3] is not '+':
								grid[y - 3][x - 3] = grid[y - 3][x - 3] + 99
				#Down Right Direction
				if (y - 1) >= 0 and (x + 1) < width and grid[y - 1][x + 1] is not '-':
					if grid[y - 1][x + 1] is not '+':
						grid[y - 1][x + 1] = grid[y - 1][x + 1] + 1
					elif (y - 2) >= 0 and (x + 2) < width and grid[y - 2][x + 2] is not '-':
						if grid[y - 2][x + 2] is not '+':
							grid[y - 2][x + 2] = grid[y - 2][x + 2] + 3
						elif (y - 3) >= 0 and (x + 3) < width and grid[y - 3][x + 3] is not '-':
							if grid[y - 3][x + 3] is not '+':
								grid[y - 3][x + 3] = grid[y - 3][x + 3] + 99
			#initial else
			else:
				continue

'''FUNCTION'''
#Determine where to move piece
def pickmove():
	highest = 0
	move = int(width/2)
	for x in range(0, width):
		for y in range(0, height):
			if grid[y][x] is not '+' and grid[y][x] is not '-':
				if grid[y][x] > highest:
					highest = grid[y][x]
					move = x
					break
	decision = []
	decision.append(move)
	#print("highest: ", highest)
	#print("move: ", move)
	return move
		




'''MAIN LOOP'''
for line in sys.stdin:
	sys.stderr.write(line)
	state = json.loads(line)
	populategrid(state)
	attackmode()
	action = {}
	action['move'] = pickmove()
	msg = json.dumps(action)
	sys.stderr.write(msg + '\n')
	sys.stdout.write(msg + '\n')
	sys.stdout.flush()

'''
#Close Everything
sys.stdin.close()
sys.stdout.close()
sys.stderr.close()
'''