import random
import gamePlay
from getAllPossibleMoves import getAllPossibleMoves

def nextMove(board, color, time, movesRemaining):
    '''Just play randomly among the possible moves'''
    moves = getAllPossibleMoves(board, color)    
    bestMove = moves[random.randint(0,len(moves) - 1)]
    return bestMove