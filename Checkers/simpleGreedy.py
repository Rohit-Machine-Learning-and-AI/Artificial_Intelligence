import gamePlay
from copy import deepcopy
from getAllPossibleMoves import getAllPossibleMoves

'''
Simple Greedy just has a simple evaluation function where my coins should be more than my opponent's
A move on the board which maximizes my coins is the best move
'''
def evaluation(board, color):
    # Evaluation function 1
    # Count how many more pieces I have than the opponent
    
    opponentColor = gamePlay.getOpponentColor(color)
    
    value = 0
    # Loop through all board positions
    for piece in range(1, 33):
        xy = gamePlay.serialToGrid(piece)
        x = xy[0]
        y = xy[1]
                
        if board[x][y].upper() == color.upper():
            value = value + 1
        elif board[x][y].upper() == opponentColor.upper():
            value = value - 1
    
    return value

def nextMove(board, color, time, movesRemaining):
    moves = getAllPossibleMoves(board, color)
    #Trying to find the move where I have best score
    best = None
    for move in moves:
        newBoard = deepcopy(board)
        gamePlay.doMove(newBoard,move)
        moveVal = evaluation(newBoard, color)
        if best == None or moveVal > best:
            bestMove = move
            best = moveVal
    return bestMove