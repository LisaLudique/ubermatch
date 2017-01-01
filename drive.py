"""
In order to kick off all the code, run the command: 

python drive.py 

Drive.py holds the main code for running situations with drivers and passengers.
Terminates once all passengers have been dropped off at their destination.
"""
import matplotlib.pyplot as plt
import networkx as nx
import random
import copy
import sys
from driverAgents import DriverAgent
from layout import Layout
from mdp import State, MarkovDecisionProcess
import pdb
import webbrowser
import time


"""
RANDOMLY GENERATE BASE GRAPH

Generates graph with [5, 10) nodes. 
Each node is a location on a map.
"""

def undostr(str_state): 
    split_space = str_state.split("#") 
    pos = int(split_space[1])
    
    passengers = [int(p.replace(',', '')) for p in (split_space[3].strip('[]')).split()]

    carrying = [int(c.replace(',', '')) for c in (split_space[5].strip('[]')).split()]
    return State(pos, passengers, carrying, graph, traffic, neighbors)
   
    
graph = None 
traffic = {} 
neighbors = {}

def master_run(n_nodes, n_passengers, n_iterations): 
    graph = nx.complete_graph(n_nodes) 
    edges = graph.edges()  # list of edges in format [(a, b), (a, c), (c, d)]
    nodes = graph.nodes() # list of nodes in format [0, 1, 2, 3, 4, 5]
    
    # make all streets two way
    initedges = copy.deepcopy(edges)
    if not initedges: 
        edges.append((graph.nodes()[0], graph.nodes()[0]))
    else: 
        for edge in initedges:
            # add self loops 
            edges.append((edge[1], edge[0]))
            edges.append((edge[1], edge[1]))
            edges.append((edge[0], edge[0]))
        
    #neighbors = {}
    for node in nodes: 
        tempneighbors = filter(lambda x: x[0] == node, edges)
        newNeighbors = []
        for x in tempneighbors: 
            newNeighbors.append(x[1])
        neighbors[node] = newNeighbors
        
    """
    GENERATE TRANSITION PROBABILITIES
    
    Every node has x neighbors. Each edge from the current node to a neighbor is associated with some transition probability 
    representing traffic at that time. 
    """
    # make a dictionary instead of a list 
    
    for node in nodes: 
        nodeNeighbors = filter(lambda x: x[0] == node, edges) 
        probabilities = random.sample(range(1, 100), len(nodeNeighbors))
        normalize = sum(probabilities)
        #traffic = {}
        index = 0
        for x in nodeNeighbors: 
            traffic[x] = probabilities[index]/float(normalize)
            index += 1

    """
    GENERATE MAP DISTANCES
    
    Every node has x neighbors. Each edge from the current node to a neighbor is associated with some distance
    distances is a dictionary with edges as keys and distances as values
    
    """
    distances = {}

    for edge in edges: 
        distance = random.randrange(1, 100)
        distances[edge] = distance 
        distances[(edge[1], edge[0])] = distance  #add flipped edge
     

    """
    GENERATE PASSENGERS 
    
    Randomly assign [1, 20) passengers to locations on the map. 
    Generates a list of passengers [0,5,3,2,5] where each element corresponds to a node. 
    """
    
    passengers = {}  # List of passenger objects
    num_passengers = n_passengers #random.randrange(1, 20)
    for passenger in range(n_passengers):
        pos = 0 
        destination = 0
        
        # regenerate as long as there is no valid path from the position to the destination 
        temp = copy.deepcopy(nodes)
        while True: 
            pos = temp[random.sample(xrange(len(temp)), 1)[0]]
            temp.remove(pos)
            destination = 0
            if not temp:    
                destination = pos
            else:
                destination = random.sample(temp, 1)[0]
            if nx.has_path(graph, pos, destination):
                break
        path = nx.shortest_path(graph,source=pos,target=destination)  
       # associate a profit to every passenger based on the travel distance
       # path is a list of nodes
        profit = 0
        for stepnum in range(len(path) - 1): 
            profit += distances[(path[stepnum], path[stepnum + 1])] 
        passengers[len(passengers)] = (pos, destination, profit)

    
    """
    GENERATE DRIVERS 
    
    Randomly assign [1, 20) passengers to locations on the map. 
    Generates a list of passengers [0,5,3,2,5] where each element corresponds to a node. 
    """
    
    drivers = [] # list of driver objects
    num_drivers = 1
    for driver in range(num_drivers):
        pos = random.sample(nodes, 1)[0]
        drivers.append(DriverAgent(pos, len(drivers), edges, neighbors))
    

    """
    Output organization
    """    
    
    
    
    mdp = MarkovDecisionProcess(passengers, graph, traffic, neighbors, n_iterations)
    policy = drivers[0].policyIterate(mdp)
    
    
    reward1 = 0
    for p in policy: 
        reward1 += drivers[0].expectedUtility(policy[p], undostr(p), drivers[0].getValues(), mdp)
    
    brute_policy = drivers[0].bruteForce(mdp)
    reward2 = 0
    for p in brute_policy: 
        reward2 += drivers[0].expectedUtility(brute_policy[p], undostr(p), drivers[0].getValues(), mdp)
    #print reward1, reward2


for n in range(50):
    start = time.time()
    # nodes, passengers, iteration
    master_run(n + 1, 1, 1)
    end = time.time()
    print(end - start)

"""
data genearation for various gamma values
"""


# sys.stdout = open('gamma', 'a')
# gamma = 0

# for i in range(100):
#     gamma = 0
#     while (gamma <= 1):
#         mdp = MarkovDecisionProcess(passengers, graph, traffic, neighbors, gamma)
#         policy = drivers[0].policyIterate(mdp)
#         # print "GRAPH", graph.nodes()
#         # print "EDGES", graph.edges()
#         # print "POLICY"
#         # for p in policy :
#         #     print p, policy[p]
            
#         # track rewards 
        
#         reward1 = 0
#         for p in policy: 
#             reward1 += drivers[0].expectedUtility(policy[p], undostr(p), drivers[0].getValues(), mdp)
        
#         # brute_policy = drivers[0].bruteForce(mdp)
#         # reward2 = 0
#         # for p in brute_policy: 
#         #     reward2 += drivers[0].expectedUtility(brute_policy[p], undostr(p), drivers[0].getValues(), mdp)
        
#         print gamma, reward1
        
#         gamma += .1
