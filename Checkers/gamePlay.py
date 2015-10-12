import sys
import time
import getopt
from copy import deepcopy

def getOpponentColor(color):
	# Returns the opposing color 'w' or 'r'
	
	if color.lower() == 'r':
		return 'w'
	elif color.lower() == 'w':
		return 'r'
	else:
		return ' '
		
def isCapturePossibleFromPosition(board, x, y):
	# Returns whether (x,y) piece can make a capture at this time
	
	opponent = getOpponentColor(board[x][y])
	# Check whether a jump possible to all four directions	
	if canMoveToPosition(board, x, y, x-2, y-2) == True:
		return True	
	if canMoveToPosition(board, x, y, x-2, y+2) == True:
		return True	
	if canMoveToPosition(board, x, y, x+2, y-2) == True:
		return True	
	if canMoveToPosition(board, x, y, x+2, y+2) == True:
		return True	
			
	return False
	
def isCapturePossible(board, color):
	# Returns whether any of the <color> pieces can make a capture at this time
	
	# Loop through all board positions
	for piece in range(1, 33):
		xy = serialToGrid(piece)
		x = xy[0]
		y = xy[1]
		
		# Check whether this board position is our color
		if board[x][y].upper() == color.upper():
			if isCapturePossibleFromPosition(board, x, y) == True:
				return True
						
	return False
	
def doMovePosition(board, x1, y1, x2, y2):
	# Will alter the board, may need to make a deepcopy() before calling this function
	# Will perform the move action
	# The move can be a simple move or a capture (but not multiple capture)
	# Make sure to call canMoveToPosition()/isLegalMove()
	# 	before this function to make sure this move is legal
	# Returns True/False, if it is a capture move or not
	
	isCapture = False
	
	board[x2][y2] = board[x1][y1]
	board[x1][y1] = ' '
	
	if abs(x1-x2) == 2: # It's a capture move
		board[(x1+x2)/2][(y1+y2)/2] = ' '
		isCapture = True
		
	if x2 == 0 or x2 == 7:
		# Make it a king, even if it already is a king, we don't care
		board[x2][y2] = board[x2][y2].upper()
		
	return isCapture
	
def doMove(board, move):
	# Will alter the board, may need to make a deepcopy() before calling this function
	# Will perform all the move actions from the move list	
	# Make sure to call isLegalMove() before this function to make sure this move is legal
	
	# Get the starting move position
	xy = serialToGrid(move[0])
	x1 = xy[0]
	y1 = xy[1]
	
	# Loop through 2nd to last items on the move list
	for i in range(1, len(move)):
		xy = serialToGrid(move[i])
		x2 = xy[0]
		y2 = xy[1]
		
		# Perform the move
		_ = doMovePosition(board, x1, y1, x2, y2)

		# Preparing for next loop
		x1 = x2
		y1 = y2

def canMoveToPosition(board, x1, y1, x2, y2):
	# Check whether (x1,y1) can move to (x2,y2) in one move (plain or capture)
	
	if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x1 > 7 or y1 > 7 or x2 > 7 or y2 > 7:
		return False
		
	color = board[x1][y1]
	if color == ' ':
		return False
	if board[x2][y2] != ' ':
		return False
	x1_x2 = abs(x1-x2)
	y1_y2 = abs(y1-y2)
	if x1_x2 != 1 and x1_x2 != 2:
		return False
	if x1_x2 != y1_y2:
		return False
	if color == 'w' and x2 > x1:	# White men cannot move down
		return False
	if color == 'r' and x2 < x1:	# Red men cannot move up
		return False
	if x1_x2 == 2: # It could be a capture move
		if board[(x1+x2)/2][(y1+y2)/2].lower() != getOpponentColor(color):
			# Middle piece must be opponent
			return False
	return True
	
def isLegalMove(board, move, color):
	# Check whether move (a list) is a legal move in the board for <color> piece
	
	if len(move) < 2:		
		return False;
		
	# Get the starting move position
	xy = serialToGrid(move[0])
	x1 = xy[0]
	y1 = xy[1]
	
	if board[x1][y1].lower() != color.lower():		
		return False
		
	# See whether a capture is possible, if possible the player must capture
	isCaptureMove = isCapturePossible(board, color)
	
	# If not a capture move, there should be only 2 items in the move list
	if isCaptureMove == False and len(move) != 2:	
		return False	
	
	# Temp board
	tempBoard = deepcopy(board)
	
	# Loop through 2nd to last items on the move list
	for i in range(1, len(move)):
		xy = serialToGrid(move[i])
		x2 = xy[0]
		y2 = xy[1]
		
		if canMoveToPosition(tempBoard, x1, y1, x2, y2) == False:			
			return False
		
		# Perform the move		
		if isCaptureMove != doMovePosition(tempBoard, x1, y1, x2, y2):			
			return False
					
		# Preparing for next loop
		x1 = x2
		y1 = y2
	
	# Check whether the jump is complete
	# whether any more jump can be made from the last position
	if isCaptureMove == True:
		if isCapturePossibleFromPosition(tempBoard, x1, y1) == True:			
			return False	
	
	return True
	
def isAnyMovePossible(board, color):
	# Returns whether any of the <color> pieces can make a valid move (plain or capture) at this time
		
	# Loop through all board positions
	for piece in range(1, 33):
		xy = serialToGrid(piece)
		x = xy[0]
		y = xy[1]
		
		# Check whether this board position is our color
		if board[x][y].upper() == color.upper():
			if canMoveToPosition(board, x, y, x-1, y-1) == True:			
				# Can move to top left
				return True
			if canMoveToPosition(board, x, y, x-1, y+1) == True:			
				# Can move to top right
				return True
			if canMoveToPosition(board, x, y, x+1, y-1) == True:			
				# Can move to bottom left
				return True
			if canMoveToPosition(board, x, y, x+1, y+1) == True:			
				# Can move to bottom right
				return True
	
	# If it can capture, it has moves
	if isCapturePossible(board, color) == True:
		return True
		
	return False
	
def countPieces(board, color):
	# Return number of <color> pieces (man or king) there are
	
	count = 0
	
	# Loop through all board positions
	for piece in range(1, 33):
		xy = serialToGrid(piece)
		x = xy[0]
		y = xy[1]
		
		# Check whether this board position is our color
		if board[x][y].upper() == color.upper():
			count = count + 1
	
	return count
	
def serialToGrid(serial):
	# Given a piece's serial 1-32 it will return the board grid position (0,0)~(7,7)
	
	return ((serial-1)//4, 2*((serial-1)%4)+1-((serial-1)//4)%2)

def newBoard():
	# Create a new board, 2D array of characters
	# 'r' for red man, 'w' for white man
	# 'R' for red king, 'W' for white king
	# ' ' for empty
		
	board = []
	for i in range(8):
		board.append([' ']*8)
	
	for i in range(1,13):
		xy = serialToGrid(i)
		x = xy[0]
		y = xy[1]
		board[x][y] = 'r'
		
	for i in range(21,33):
		xy = serialToGrid(i)
		x = xy[0]
		y = xy[1]
		board[x][y] = 'w'
	
	return board

def printBoard(board):
	# Print a board
	numberedBoard = [
					['  ', '1 ', '  ', '2 ', '  ', '3 ', '  ', '4 '],
					['5 ', '  ', '6 ', '  ', '7 ', '  ', '8 ', '  '],
					['  ', '9 ', '  ', '10', '  ', '11', '  ', '12'],
					['13', '  ', '14', '  ', '15', '  ', '16', '  '],
					['  ', '17', '  ', '18', '  ', '19', '  ', '20'],
					['21', '  ', '22', '  ', '23', '  ', '24', '  '],
					['  ', '25', '  ', '26', '  ', '27', '  ', '28'],
					['29', '  ', '30', '  ', '31', '  ', '32', '  ']
					]
	print '-'*33, '\t', '-'*41
	for i in range(0,8):		
		print '|',
		print ' | '.join(board[i]), '|'	, '\t|' , ' | '.join(numberedBoard[i]), '|'
		print '-'*33, '\t', '-'*41
	
def playGame(p1, p2, verbose, t = 1):
	# Takes as input two functions p1 and p2 (each of which
	# calculates a next move given a board and player color),
	# and returns a tuple containing 
	# the final board, 
	# pieces left for red,
	# pieces left for white,
	# and status message "Drawn"/"Won"/"Timeout"/"Bad Move"
	
	board = newBoard()
	printBoard(board)
	print
	currentColor = 'r'
	nextColor = 'w'
	p1time = t
	p2time = t
	p1realTime = t
	p2realTime = t
	movesRemaining = 150
	
	while isAnyMovePossible(board, currentColor) == True:
		tempBoard = deepcopy(board)
		t1 = time.time()
		nextMove = p1(tempBoard, currentColor, p1time, movesRemaining)
		t2 = time.time()
		p1time = p1time - (t2 - t1)
		p1realTime = p1realTime - (t2 - t1)
		if (p1realTime < 0):
			if currentColor == "r":
				return (board, 0, 24, "Timeout")
			else:
				return (board, 24, 0, "Timeout")
		if isLegalMove(board, nextMove, currentColor) == True:			
			doMove(board, nextMove)
			
		else:
			if currentColor == "r":
				return (board, -1, 1, "Bad Move: %s" %str(nextMove))
			else:
				return (board, 1, -1, "Bad Move: %s" %str(nextMove))

		(p1, p2) = (p2, p1)
		(p1time, p2time) = (p2time, p1time)
		(currentColor, nextColor) = (nextColor, currentColor)
		if verbose == True:
			printBoard(board)
			print "Pieces remaining:", currentColor, "=", countPieces(board, currentColor),
			print nextColor, "=", countPieces(board, nextColor), "Moves left =", movesRemaining
			print "Clock remaining: %s=%f, %s=%f" %(currentColor, p1time, nextColor, p2time)
			
		movesRemaining = movesRemaining - 1
		if movesRemaining == 0:
			return (board, countPieces(board, 'r'), countPieces(board, 'w'), "Drawn")
			
	return (board, countPieces(board, 'r'), countPieces(board, 'w'), "Won")


if __name__ == "__main__":

	try:
		optlist,args = getopt.getopt(sys.argv[1:],'vt:')
	except getopt.error:
		print "Usage: python %s {-v} {-t time} player1 player2" % (sys.argv[0])
		exit()

	verbose = False
	clockTime = 150.0
	for (op,opVal) in optlist:
		if (op == "-v"):
			verbose = True
		if (op == "-t"):
			clockTime = float(opVal)
	exec("from " + args[0] + " import nextMove")
	p1 = nextMove
	exec("from " + args[1] + " import nextMove")
	p2 = nextMove

	result = playGame(p1, p2, verbose, clockTime)	

	printBoard(result[0])
	
	if result[3] == "Drawn":
		if result[1] > result[2]:
			print "Ran Out Of Moves :: %s Wins %s Loses (%d to %d)" %(args[0], args[1], result[1], result[2]),
		elif result[1] < result[2]:
			print "Ran Out Of Moves :: %s Wins %s Loses (%d to %d)" %(args[1], args[0], result[2], result[1]),
		else:
			print "Ran Out Of Moves :: TIE %s, %s, (%d to %d)" % (args[0], args[1], result[1], result[2])
	elif result[3] == "Won":
		if result[1] > result[2]:
			print "%s Wins %s Loses (%d to %d)" %(args[0], args[1], result[1], result[2]),
		elif result[1] < result[2]:
			print "%s Wins %s Loses (%d to %d)" %(args[1], args[0], result[2], result[1]),
	else:
		if result[1] > result[2]:
			print "%s Wins %s Loses (%d to %d) TIMEOUT" %(args[0], args[1], result[1], result[2]),
		elif result[1] < result[2]:
			print "%s Wins %s Loses (%d to %d) TIMEOUT" %(args[1], args[0], result[2], result[1]),		
		
		
		
		
		
		