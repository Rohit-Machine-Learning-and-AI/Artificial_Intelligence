#!/usr/bin/python -tt

import time

#----------------------------------------------------
#prints the current board
def print_board():
    for i in range(0,3):
        for j in range(0,3):
            print map[i][j],
            if j != 2:
                print "|",
        print ""

#----------------------------------------------------
#check if the game is over and if yes, who wins
def check_done():
    for i in range(0,3):
        if map[i][0]==map[i][1]==map[i][2] \
           or map[0][i]==map[1][i]==map[2][i] \
           or map[0][0]==map[1][1]==map[2][2] \
           or map[2][0]==map[1][1]==map[0][2]:
            if turn=='X':
                return "\nO Wins !!\n"
            else:
                return "\nX Wins !!\n"
    for i in range(0,3):
        for j in range(0,3):
            if map[i][j]>=1 and map[i][j]<=9:
                return "Game on"
    return "Match ends in a draw"

#----------------------------------------------------
#find row index corresponding to number n
def findx(n):
    if n==1 or n==2 or n==3: return 0
    elif n==4 or n==5 or n==6: return 1
    else: return 2

#----------------------------------------------------
#find column index corresponding to number n
def findy(n):
    if n==1 or n==4 or n==7: return 0
    elif n==2 or n==5 or n==8: return 1
    else: return 2    

#----------------------------------------------------
#check whether location n is available for marking
def isFree(n):
    if map[findx(n)][findy(n)]=='X' or map[findx(n)][findy(n)]=='O':
        return False
    return True

#----------------------------------------------------
#change turn either from player to computer or vice versa
def changeTurn():
    global turn
    if turn=='X':
        turn='O'
    else:
        turn='X'

#----------------------------------------------------
#to help the computer determine whether it's X or O
def whosCpu():
    global player
    if player=='X':
        return 'O'
    else:
        return 'X'

#----------------------------------------------------
#if l is marked at position n, does it lead to a victory
def isWin(n,l):
##    print "isWin"
    #map2=map creates an alias, not a copy
    map2=[[0 for x in range(3)] for x in range(3)]
    
    for i in range(0,3):
        for j in range(0,3):
            map2[i][j]=map[i][j]
    map2[findx(n)][findy(n)]=l
    
    for i in range(0,3):
        if map2[i][0]==map2[i][1]==map2[i][2] \
           or map2[0][i]==map2[1][i]==map2[2][i] \
           or map2[0][0]==map2[1][1]==map2[2][2] \
           or map2[2][0]==map2[1][1]==map2[0][2]:
            return True
    return False

#----------------------------------------------------
#code for player's turn
def humanPlay():
    global player
    print 
    print_board()
    print "\nYour Turn, Please enter the place you want to mark:",
    
    try:
        v=input()
        if v<1 or v>9:
            print "Invalid input. Please enter positive numbers from the above table"
        else:
    ##        print map[findx(v)][findy(v)]
            if map[findx(v)][findy(v)]=='X' or map[findx(v)][findy(v)]=='O':
                print 'Position already marked, choose another spot'
            else:
                map[findx(v)][findy(v)]=player
                changeTurn()
                print_board()
    except NameError:
        print "Please enter a numerical value between 1 and 9."
    except SyntaxError:
        print "Enter something"

#----------------------------------------------------
#code for computer's turn
def cpuPlay():
    cpu=whosCpu()
    print '\nMy Turn',
    for i in (1,2,3):
        print '.',
        time.sleep(0.3)
    print
    global turn

    for i in range(1,9):
        if isFree(i):
            if isWin(i,cpu):
##                print 'win'
                map[findx(i)][findy(i)]=cpu
                changeTurn()
                return

    for i in range(1,9):
        if isFree(i):
            if isWin(i,player):
##                print 'block'
                map[findx(i)][findy(i)]=cpu
                changeTurn()
                return

    #Below 3 steps' approach referred from inventwithpython.com
    for i in (1,3,7,9):
        if isFree(i):
##            print 'corners'
            map[findx(i)][findy(i)]=cpu
            changeTurn()
            return

    if isFree(5):
##        print 'center'
        map[findx(5)][findy(5)]=cpu
        changeTurn()
        return

    for i in (2,4,6,8):
        if isFree(i):
##            print 'sides'
            map[findx(i)][findy(i)]=cpu
            changeTurn()
            return

#----------------------------------------------------
#Main program

restart='y'
while restart.upper()=='Y':
    map=[[1,2,3],[4,5,6],[7,8,9]]
    print "\n\nWelcome to a game of Tic Tac Toe\n"

    XO=True
    while XO:
        player=raw_input("Do you want to be X or O?\n")
        player=player.upper()
        if player=='X':
            print "You are X and you get to play first."
            XO=False
        elif player=='O':
            print "Great! I'll take X and start the game. All the Best"
            XO=False
        else:
            print "Incorrect Input.",

    turn='X'

    if player=='X':
        while check_done()=="Game on":
            if turn=='X':
                humanPlay()
            else:
                cpuPlay()
            c=check_done()
            if c!="Game on":
                print c

    else:
        while check_done()=="Game on":
            if turn=='X':
                cpuPlay()
            else:
                humanPlay()
            c=check_done()
            if c!="Game on":
                print c

    print "Final board:"
    print_board()
    restart=raw_input("Wanna play again? (Y):")

print "\n\nThanks for playing\n\n"
