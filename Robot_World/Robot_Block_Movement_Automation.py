import time
from heapq import *
import functools
import copy
import math
import random
import matplotlib as mppp
import matplotlib.pyplot as plt
mppp.use('Agg')
import os.path
import subprocess
import numpy as np
from matplotlib import colors
from mpl_toolkits.mplot3d import Axes3D

infinity = float("inf")

class RobotWorld:
    "The idea is that a RobotWorld is the datatype that goes in the queue."
    def __init__(self,width,length,height,initial,goal):
        self.hand = {'location' : (0,0,0), 'held' : None, 'closed?' : False}
        self.width, self.length, self.height = width, length, height
        self.blocks, self.goal = initial, goal
        self.cost, self.title = 0, ''
        assert(initial.keys() == goal.keys()) #there can't be blocks without a goal state, or goal states with a block that is not initialized.
        self.colormap, possible_colors = {}, set(colors.cnames.keys()) #for the sake of the visualization, not important to the function of RobotWorlds.
        for blockname in self.blocks:
            self.colormap[blockname] = possible_colors.pop()
    def __lt__(self,other):
        "Not meaningful, but necessary for RobotWorld to interact with a heapq"
        return True
    # The actions return the change in cost
    def moveUp(self):
        (x,y,z) = self.hand['location']
        if z < (self.height - 1):
            self.hand['location'] = (x,y,z+1)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y,z+1)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveUp' action occuring? The hand is as far up as it can go.")
            return 0
    def moveDown(self):
        (x,y,z) = self.hand['location']
        if z > 0:
            self.hand['location'] = (x,y,z-1)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y,z-1)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveDown' action occuring? The hand is on the floor.")
            return 0
    def moveLeft(self):
        (x,y,z) = self.hand['location']
        if y > 0:
            self.hand['location'] = (x,y-1,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y-1,z)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveLeft' action occuring? The hand is on the left edge.")
            return 0
    def moveRight(self):
        (x,y,z) = self.hand['location']
        if y < (self.length - 1):
            self.hand['location'] = (x,y+1,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y+1,z)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveRight' action occuring? The hand is on the right edge.")
            return 0
    def moveForward(self):
        (x,y,z) = self.hand['location']
        if x < (self.width - 1):
            self.hand['location'] = (x+1,y,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x+1,y,z)
            self.cost += 1
            return 1.0
        else:
            print("Why is the 'moveForward' action occuring? The hand is on the front edge.")
            return 0
    def moveBackward(self):
        (x,y,z) = self.hand['location']
        if x > 0:
            self.hand['location'] = (x-1,y,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x-1,y,z)
            self.cost += 1
            return 1.0
        else:
            print("Why is the 'moveBackward' action occuring? The hand is on the back edge.")
            return 0
    # the reason for the handOpen and handClose actions to have non-zero costs is to prevent the search from considering the "I'll close my hand on this block" and "I'll open and close my hand on this block 20 million times" as equivalent.
    def handOpen(self):
        if not self.hand['closed?']:
            print("Why is the 'handOpen' action occuring? The hand is already open.")
            return 0
        self.hand['closed?'] = False
        if self.hand['held']:
            self.hand['held'] = None
            self.cost += 0.1
            return 0.1
    def handClose(self):
        if self.hand['closed?']:
            print("Why is the 'handClose' action occuring? The hand is already closed.")
            return 0
        else:
            for (name,location) in self.blocks.iteritems():
                if location == self.hand['location']:
                    self.hand['held'] = name
                    self.hand['closed?'] = True
                    self.cost += 0.1
                    return 0.1
            print("Why did the 'handClose' action occur? There is no block here at {}".format(str(self.hand['location'])))
            return 0
    def isGoal(self):
        return self.blocks == self.goal
    def allowedActions(self):
        def alreadyThere(coord):
            for (block_name, block_coord) in self.blocks.iteritems():
                if (block_coord == coord) and (block_coord == self.goal[block_name]):
                    return True
            return False
        possibilities = ['close','forward','backward','left','right','up','down']
        if self.hand['closed?'] and alreadyThere(self.hand['location']): #try to open first if its a good idea
            possibilities = ['open'] + possibilities
        # Removing the close action if 'alreadyThere' is True could lead to problems in a 3D world, or even rare scenarios in a 2D world.
        # This is not relevant to the worlds here, but this should be removed if we re-use this for planning.
        if self.hand['closed?'] or (self.hand['location'] not in self.blocks.values()) or (alreadyThere(self.hand['location'])):
            possibilities.remove('close')
        (x,y,z) = self.hand['location']
        if x == 0: possibilities.remove('backward')
        if x == (self.length - 1): possibilities.remove('forward')
        if y == 0: possibilities.remove('left')
        if y == (self.width - 1): possibilities.remove('right')
        if z == 0: possibilities.remove('down')
        if z == (self.height - 1): possibilities.remove('up')
        if self.hand['closed?'] and ('open' not in possibilities): #try to put 'open' at the end, so moving around happens before
            possibilities = possibilities + ['open']               #pointless opening and closing.
        return possibilities
    def do(self,action):
        '''action is a string indicating an action for the RobotWorld to do. These strings come from the 'allowedActions' method, and are part of the process of
           iterating over neighboring nodes in the graph.'''
        if (action == 'up'): return self.moveUp()
        elif (action == 'down'): return self.moveDown()
        elif (action == 'left'): return self.moveLeft()
        elif (action == 'right'): return self.moveRight()
        elif (action == 'forward'): return self.moveForward()
        elif (action == 'backward'): return self.moveBackward()
        elif (action == 'open'): return self.handOpen()
        elif (action == 'close'): return self.handClose()
        else: print("Unexpected action {}".format(action))
    def visualize(self,serial_number):
        '''The blocks are colored according to their identity (exactly one color per block). These are persistent over time, so a block with a certain name in one frame of the animation will have the same color in all other frames.
           The triangles of the same color as a block indicate where the block's goal location is.
           The title 'cost=<number>' at the top indicates the cumulative cost of actions so far to bring the RobotWorld into its current state.
           The cross indicates the location of the robot hand.
        '''
        fig = plt.figure()
        axis = fig.add_subplot(111,projection='3d')
        axis.set_xlim(0, self.width)
        axis.set_ylim(0, self.length)
        axis.set_zlim(0, self.height)
        axis.set_xlabel('X Axis')
        axis.set_ylabel('Y Axis')
        axis.set_zlabel('Z Axis')
        n = len(self.blocks)
        for block in self.blocks.iteritems():
            blockname, coord = block
            axis.scatter(coord[0], coord[1], coord[2], s=500, marker=(4,0), c=self.colormap[blockname])
            target = self.goal[blockname]
            axis.scatter(target[0], target[1], target[2], s=300, marker=(3,0), c=self.colormap[blockname])
        robo_x, robo_y, robo_z = self.hand['location']
        axis.scatter(robo_x,robo_y,robo_z,s=500,marker='+', c='black')
        axis.set_title("cost={}".format(str(self.cost)))
        plt.savefig("snapshots/{}_{}.png".format(self.title,str(serial_number)))
        plt.close()

def graphsearch(queue,queue_modification,timeout,visualize=False):
    "The things that I can think to say about graphsearch are mentioned in the directions on the website. If you have questions, email me at aseewald@indiana.edu"
    t0 = time.time()
    visited, history = [], []
    solution_info = {'cost' : infinity, 'num_expanded' : infinity, 'walltime' : infinity}
    while len(queue) > 0:
        if timeout == 0:
            print("Ran out of time for thinking")
            print("The queue is of size: {}".format(len(queue)))
            return solution_info
        queue, expanded = queue_modification(queue,visited)
        visited.append(expanded)
        if expanded.isGoal():
            tf = time.time()
            history.append(expanded)
            solution_info['cost'] = expanded.cost
            solution_info['num_expanded'] = len(history)
            solution_info['walltime'] = tf - t0
            print("The solution's cost is: {}, and involved expanding {} verticies".format(str(expanded.cost), str(len(history))))
            print("Finding the solution involved {} seconds of walltime".format(str(tf - t0)))
            print("----------------------------------------------------------------------------------")
            if visualize:
                for (i, world) in enumerate(history):
                    world.visualize(i)
            return solution_info
        else:
            timeout -= 1
            history.append(expanded)
    print("No possible actions left. And you may ask yourself, well, how did I get here? You may tell yourself, this is not my beautiful search algorithm.")
    return solution_info

def duplicateWorld(world,worlds):
    "You may want to test if a world is in some visited set. This function is needed to define a more loose idea of equality, so that worlds with different accumulated costs are considered equivalent."
    for w in worlds:
        if (w.hand == world.hand) and (w.blocks == world.blocks):
            return True
    return False

# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

def depthFirst(queue,visited):

    sr,currWorld = heappop(queue)
    a=currWorld.allowedActions()
    queueWorlds=[]
    if currWorld.isGoal():
        return queue,currWorld
    l=len(queue)

#making a list of worlds presently in the queue to later check for duplication before pushing
    for i in range(0,l):
        queueWorlds.append(queue[i][1])

#pushing neighbors if not in visited or queue
    for i in a:
#making a deep copy because neighbor changes after each iteration
        neighbor = copy.deepcopy(currWorld)
        neighbor.do(i)
        if not duplicateWorld(neighbor,visited):
            if not duplicateWorld(neighbor,queueWorlds):
                heappush(queue,(sr-1,neighbor))

    return queue,currWorld

# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

def breadthFirst(queue,visited):
    sr,currWorld=heappop(queue)
    queueWorlds=[]

#making a list of worlds presently in the queue to later check for duplication before pushing
    for i in range(0,len(queue)):
        queueWorlds.append(queue[i][1])

    neighbor=copy.deepcopy(currWorld)
    
#pushing neighbors if not in visited or queue
    for i in currWorld.allowedActions():
#making a deep copy because neighbor changes after each iteration
        neighbor=copy.deepcopy(currWorld)
        neighbor.do(i)
        if not duplicateWorld(neighbor,visited):
            if not duplicateWorld(neighbor,queueWorlds):
                heappush(queue,(sr+1,neighbor))
    
    return queue,currWorld
    
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

def h_euc(cw):
    a=cw.hand['location']
    if cw.hand['closed?']:
#cal dist bet hand and held block's goal
        b=cw.goal[cw.hand['held']]
        value = (abs(a[0]-b[0])*(a[0]-b[0]) + abs(a[1]-b[1])*(a[1]-b[1]) + abs(a[2]-b[2])*(a[2]-b[2]))
    else:
#cal dist to the closest block
        b=cw.blocks['A']
        bmin=999
        for i in cw.blocks:
          if(cw.blocks[i]!=cw.goal[i]):
            bloc=cw.blocks[i]
            total=(abs(a[0]-bloc[0])*(a[0]-bloc[0]) + abs(a[1]-bloc[1])*(a[1]-bloc[1]) + abs(a[2]-bloc[2])*(a[2]-bloc[2]))
            if total<bmin:
                bmin=total
                b=bloc
        value = (abs(a[0]-b[0])*(a[0]-b[0]) + abs(a[1]-b[1])*(a[1]-b[1]) + abs(a[2]-b[2])*(a[2]-b[2]))
    return value

# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

def h_man(cw):
    a=cw.hand['location']
    if cw.hand['closed?']:
#cal dist bet hand and held block's goal
        b=cw.goal[cw.hand['held']]
        value = (abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2]))
    else:
#cal dist to the closest block
        b=cw.blocks['A']
        bmin=999
        for i in cw.blocks:
          if(cw.blocks[i]!=cw.goal[i]):
            bloc=cw.blocks[i]
            total=(abs(a[0]-bloc[0]) + abs(a[1]-bloc[1]) + abs(a[2]-bloc[2]))            
            if total<bmin:
                bmin=total
                b=bloc
        value = (abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2]))
    return value
	
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

def bestFirst(queue,visited,heuristic):

#used to determine the opposite action to be taken, useful while handling the block in another's goal case
    def opposite(j):
        if j=='forward': return 'backward'
        elif j=='backward': return 'forward'
        elif j=='right': return 'left'
        elif j=='left': return 'right'
        return j

    sr,currWorld=heappop(queue)
    a=currWorld.allowedActions()
    queueWorlds=[]
#making a list of worlds presently in the queue to later check for duplication before pushing
    for i in range(0,len(queue)):
        queueWorlds.append(queue[i][1])

#handling block at another's goal state - starts (discussed with Rohit Patil)
    for i in currWorld.blocks:
        if (currWorld.hand['location'] == currWorld.goal[i]) and (currWorld.hand['held']==i) and ('open' in a):
            for k in currWorld.blocks:
                if (currWorld.hand['location'] == currWorld.blocks[k]):
                    if i==k:
                        pass
                    else:    
                        for j in ('forward','right','backward','left'):
                            if (j in a):
                      		currWorld.do(j)
                      		currWorld.handOpen()
#takes held block to the neighbor, comes back and picks up the goal-blocking block and tries to take it to its goal
                      		currWorld.do(opposite(j))
                      		currWorld.handClose()
                      		for l in queue:
                                    t,tw=heappop(queue)         
                                    t=t+100
                                    heappush(queue,(t,tw))
                                heappush(queue,(0,currWorld))
                                break
                        break
#handling block at another's goal state - ends

    flag=False
    flag2=False
#to avoid random dropping         
    if currWorld.hand['closed?'] and currWorld.goal[currWorld.hand['held']]!=currWorld.hand['location'] :
        a.remove('open')
    for i in a:
#making a deep copy because neighbor changes after each iteration
        neighbor=copy.deepcopy(currWorld)
        neighbor.do(i)

        if i=='close':
            neighborbkp=copy.deepcopy(neighbor)
            flag=True
        if i=='open':
            neighborbkp2=copy.deepcopy(neighbor)
            flag2=True
              
#pushing neighbors if not in visited or queue
        if not duplicateWorld(neighbor,visited):
            if not duplicateWorld(neighbor,queueWorlds):             
                heappush(queue,(heuristic(neighbor),neighbor))

#pop, increment & push all but the 'close' world (discussed with Rohit Patil)
    if(flag):          
        for l in queue:
            if l[1].hand['location']!=neighborbkp.hand['location']:
                    t,tw=heappop(queue)         
                    t=t+100
                    heappush(queue,(t,tw))
        heappush(queue,(0,neighborbkp))
                    
#pop, increment & push all but the 'open' world
    if(flag2):
        for l in queue:
            if l[1].hand['location']!=neighborbkp2.hand['location']:
                    t,tw=heappop(queue)         
                    t=t+100
                    heappush(queue,(t,tw))
        heappush(queue,(0,neighborbkp2))      
                                        
    return queue,currWorld


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

def aStar(queue,visited,heuristic):

#used to determine the opposite action to be taken, useful while handling the block in another's goal case
    def opposite(j):
        if j=='forward': return 'backward'
        elif j=='backward': return 'forward'
        elif j=='right': return 'left'
        elif j=='left': return 'right'
        return j

    sr,currWorld=heappop(queue)
    a=currWorld.allowedActions()
    queueWorlds=[]
#making a list of worlds presently in the queue to later check for duplication before pushing
    for i in range(0,len(queue)):
        queueWorlds.append(queue[i][1])

#handling block at another's goal state - starts
    for i in currWorld.blocks:
        if (currWorld.hand['location'] == currWorld.goal[i]) and (currWorld.hand['held']==i) and ('open' in a):
            for k in currWorld.blocks:
                if (currWorld.hand['location'] == currWorld.blocks[k]):
                    if i==k:
                        pass
                    else:    
                        for j in ('forward','right','backward','left'):
                            if (j in a):
                      		currWorld.do(j)
                      		currWorld.handOpen()
#takes held block to the neighbor, comes back and picks up the goal-blocking block and tries to take it to its goal
                      		currWorld.do(opposite(j))
                      		currWorld.handClose()
                      		for l in queue:
                                    t,tw=heappop(queue)         
                                    t=t+100
                                    heappush(queue,(t,tw))
                                heappush(queue,(0,currWorld))
                                break
                        break
#handling block at another's goal state - ends

    flag=False
    flag2=False
#to avoid random dropping         
    if currWorld.hand['closed?'] and currWorld.goal[currWorld.hand['held']]!=currWorld.hand['location'] :
        a.remove('open')
    for i in a:
#making a deep copy because neighbor changes after each iteration
        neighbor=copy.deepcopy(currWorld)
        neighbor.do(i)

        if i=='close':
            neighborbkp=copy.deepcopy(neighbor)
            flag=True
        if i=='open':
            neighborbkp2=copy.deepcopy(neighbor)
            flag2=True
              
#pushing neighbors if not in visited or queue
        if not duplicateWorld(neighbor,visited):
            if not duplicateWorld(neighbor,queueWorlds):
#adding the cost till node and cost from node to destination
                heappush(queue,(neighbor.cost+heuristic(neighbor),neighbor))

#pop, increment & push all but the 'close' world
    if(flag):          
        for l in queue:
            if l[1].hand['location']!=neighborbkp.hand['location']:
                    t,tw=heappop(queue)         
                    t=t+100
                    heappush(queue,(t,tw))
        heappush(queue,(0,neighborbkp))
                    
#pop, increment & push all but the 'open' world
    if(flag2):
        for l in queue:
            if l[1].hand['location']!=neighborbkp2.hand['location']:
                    t,tw=heappop(queue)         
                    t=t+100
                    heappush(queue,(t,tw))
        heappush(queue,(0,neighborbkp2))      
                                        
    return queue,currWorld

# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

def run(world,title,heuristics,timeout=5000):
    solutions = []

#DFS    
    queue = []
    world0 = copy.deepcopy(world)
    world0.title=(title + '_DFS')
    heappush(queue,(0,world0))
    print("Doing Depth First Search  on {}:".format(title))
    solutions.append(graphsearch(queue, depthFirst, timeout))

#BFS
    queue = []
    world1 = copy.deepcopy(world)
    world1.title=(title + '_BFS')
    heappush(queue,(0,world1))
    print("Doing Breadth First Search on {}:".format(title))
    solutions.append(graphsearch(queue, breadthFirst, timeout))

    for h in heuristics:
        queue, hname = [], str(h).split(' ')[1]
#BEST FIRST
        world2 = copy.deepcopy(world)
        world2.title=(title + hname + '_BestFirst')
        heappush(queue,(0,world2))
        bestFirst_h = functools.partial(bestFirst,heuristic=h)
        print("Doing Best First with heuristic {} on {}:".format(hname,title))
        solutions.append(graphsearch(queue, bestFirst_h, timeout))

#ASTAR
        queue = []
        world4 = copy.deepcopy(world)
        world4.title=(title + hname + '_Astar')
        heappush(queue,(0,world4))
        aStar_h = functools.partial(aStar,heuristic=h)
        print("Doing A* with heuristic {} on {}:".format(hname,title))
        solutions.append(graphsearch(queue, aStar_h, timeout))
    return solutions

def experiment(heuristics,described_worlds):
    data = [run(world,title,heuristics,timeout=1000) for (world,title) in described_worlds]
    fig, axes = plt.subplots(nrows=len(described_worlds))
    fig.set_size_inches(20,30)
    if len(described_worlds) == 1: # a hack to get consistent indexing behavoir from matplotlib.
        axes = [axes]
    color_codes = random.sample(colors.cnames.keys(), len(described_worlds) * (2 + 2 * len(heuristics)))
    labels = ['DFS','BFS']
    for heuristic in heuristics:
        hname = str(heuristic).split(' ')[1]
        labels.append('Best_' + hname)
        labels.append('A*_' + hname)
    # set the legend of the figure to correspond to colors.
    for (i, solutions) in enumerate(data): #2 because discard breadthFirst and depthFirst b/c no heuristic.
        axes[i].set_title(described_worlds[i][1])
        axes[i].set_xlabel("verticies expanded")
        axes[i].set_ylabel("cost of solution")
        for (j, solution) in enumerate(solutions):
           print("{} is {}".format(labels[j], color_codes[j]))
           if solution['cost'] == infinity:
               pass
           else:
               axes[i].scatter(solution['num_expanded'],solution['cost'], color=color_codes[j], label=labels[j])

    path = 'C:\Users\Rohit\Desktop\snapshots'
    filename="experiment.png"
    filename = os.path.join(path, filename)
    plt.savefig(filename)
    #plt.savefig("experiment.png")
    plt.close()

#if not os.path.exists("snapshots"):
#    if subprocess.call(["mkdir","snapshots"]) != 0:
#        print("Failed to make a directory to store images in.")


hs = {h_man,h_euc} #this is a set, put your heuristic functions in here.
presolved = RobotWorld(4,4,1,{'A' : (3,3,0), 'B' : (3,1,0)}, {'A' : (3,3,0), 'B' : (3,1,0)})
#run(presolved,'presolved',hs)
easy = RobotWorld(5,5,1,{'A' : (1,0,0), 'B' : (3,1,0)}, {'A' : (1,1,0), 'B' : (3,1,0)})
#run(easy,'easy',hs)
medium = RobotWorld(6,6,1,{'A' : (1,1,0), 'B' : (3,1,0)}, {'A' : (4,4,0), 'B' : (4,5,0)})
#run(medium,'medium',hs)
hard = RobotWorld(10,10,1,{'A' : (1,0,0), 'B' : (9,9,0), 'C' : (4,4,0)}, {'A' : (4,4,0), 'B' : (1,0,0), 'C' : (9,9,0)})
#run(hard,'hard',hs)
experiment(hs, [(easy,'easy'), (medium, 'medium'), (hard, 'hard')])