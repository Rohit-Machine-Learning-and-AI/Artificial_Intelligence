# -*- coding: utf-8 -*-
import gamePlay
from getAllPossibleMoves import getAllPossibleMoves
from copy import deepcopy

global mycolor

def evaluation(board):
    global mycolor
    color = mycolor
    opponentColor = gamePlay.getOpponentColor(color)    
    pawn, king, corner, edge, front, defence, defended_pawns = 0, 0, 0, 0, 0, 0, 0
    
    for piece in range(1, 33):
        x, y = gamePlay.serialToGrid(piece)
        coin = board[x][y]

#pawns and kings
        if coin.upper() == color.upper():
            pawn += 1
            if coin == color.upper():
                king += 1
        else:
            pawn -= 1
            if coin == opponentColor.upper():
                king -= 1                

#corner  - safe against attacks              
        if piece in (4,29):
            if color == coin:  corner += 1
            else:              corner -= 1

#edge - edges are safe, so coins must try to go there           
        if piece in (5,13,21,12,20,28):
            if color == coin:   edge += 1
            else:               edge -= 1

#front - if a pawn is <= 3 steps from becoming a king      
        if coin == 'r':
            if piece > 20:
                if color == 'r':     front += 1
                else:                front -= 1
        else:
            if piece < 13:
                if color == 'w':     front += 1
                else:                front -= 1
                
#defended_pawns - if a pawn cannot be attacked
        if coin == 'r' and x > 0 and y > 0 and y < 7 and board[x-1][y+1].upper() == coin.upper() and board[x-1][y-1].upper() == coin.upper():
            if color == 'r':    defended_pawns += 1
            else:               defended_pawns -= 1   
        elif x < 7 and y > 0 and y < 7 and board[x+1][y+1].upper() == coin.upper() and board[x+1][y-1].upper() == coin.upper():
            if color == 'w':    defended_pawns += 1
            else:               defended_pawns -= 1   

#my_defence - the bottom row must not be moved unless opponent arrives, provides the best defence
    for piece in range(1, 5):
        if color == coin == 'r': defence += 1
    for piece in range(29, 33):
        if color == coin == 'w': defence += 1

# Order of importance(descending) is 1.last layer defence 2.number of kings,
#3.number of pawns, 4.defend most pawns, 5.corner, 6.edges, 7.attack(front)
    return (3*pawn + 7*king + 0.34*corner + 0.33*edge + 0.2*front + 25*defence + 0.5*defended_pawns)

####################################################################################
####################################################################################
    
def minimax(board, maxP, color, alpha, beta, depth):
#calculates maximum when maxP is True and minimum otherwise
    infty = float('inf')
    moves = getAllPossibleMoves(board, color)
    opponentColor = gamePlay.getOpponentColor(color)
    if maxP:
        if moves == [] or depth == 0:
            return [], evaluation(board)
        best_score = -infty
        best_move = moves[0]
        for move in moves:
            boardTemp = deepcopy(board)
            gamePlay.doMove(boardTemp,move)
            m,score = minimax(boardTemp,False,opponentColor,alpha,beta,depth-1)
            if score > best_score:
                best_move = move
                best_score = score
            alpha = max(alpha,score)
#Beta cut-off
            if alpha >= beta:
                break
    else:
        if moves == [] or depth == 0:
            return [], evaluation(board)
        best_score = infty
        best_move = moves[0]
        for move in moves:
            boardTemp = deepcopy(board)
            gamePlay.doMove(boardTemp,move)
            m,score = minimax(boardTemp,True,opponentColor,alpha,beta,depth-1)
            if score < best_score:
                best_move = move
                best_score = score
            beta = min(beta,score)
#Alpha cut-off
            if alpha >= beta:
                break
                
    return best_move, best_score

####################################################################################
####################################################################################

def nextMove(board, color, time, movesRemaining):
    global mycolor
    mycolor = color
    infty = float('inf')
    depth = 5
    bestMove,s = minimax(board, True, color, -infty, infty, depth)
    return bestMove
    