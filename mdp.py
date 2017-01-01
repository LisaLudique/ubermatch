import random
from itertools import combinations
import itertools as itertools
import pdb

class State:
    def __init__(self, pos, passengers, carrying, graph, traffic, neighbors):
        self.pos = pos # driver position
        self.passengers = passengers # passengers still left on graph by index list
        self.carrying = carrying # passengers being carried by driver by index list
        self.graph = graph # map as graph with nodes and edges
        self.traffic = traffic # dictionary mapping transition probabilities to edges
        self.neighbors = neighbors # dictionary with nodes as keys and list of neighbor nodes as value
        self.capacity = 4 # maximum number of passengers a driver can carry

    def __str__(self):
        """
        Stringify a state
        """
        s = ""
        if self.passengers: 
            if self.carrying: 
                s += "position:#" + str(self.pos) + "#passengers:#" + str(sorted(self.passengers)) + "#carrying:#" + str(sorted(self.carrying))
            else: 
                s += "position:#" + str(self.pos) + "#passengers:#" + str(sorted(self.passengers)) + "#carrying:#" + str([])
        else:
            if self.carrying: 
                s += "position:#" + str(self.pos) + "#passengers:#" + str([]) + "#carrying:#" + str(sorted(self.carrying))
            else: 
                s += "position:#" + str(self.pos) + "#passengers:#" + str([]) + "#carrying:#" + str([])
        return s
    
    def getGraph(self):
        return self.graph
        
    def getCapacity(self):
        return self.capacity
        
    def getPos(self):
        return self.pos
    
    def getPassengers(self):
        return self.passengers
    
    def getCarrying(self):
        return self.carrying
        
    def getTraffic(self):  
        return self.traffic
    
    def getNeighbors(self):
        return self.neighbors
    
    def getSuccessor(self, action):
        """ 
        Given an action, returns the successor state resulting from that action being performed successfully 
        """
        if type(action) is int: #action is a number of the node to go to
            return State(action, self.passengers, self.carrying, self.graph, self.traffic, self.neighbors)
        elif action[0] == "Pickup": # Pick up passenger of certain index with probability 1 ("Pickup", passenger index)
            if action[1] in self.passengers: 
                return State(self.pos, self.passengers.remove(action[1]), self.carrying.append(action[1]), self.graph, self.traffic, self.neighbors)
        elif action[0] == "Dropoff": # Drop off passenger of certain index with probability 1 ("Dropoff", passenger index)
            if action[1] in self.carrying:
                return State(self.pos, self.passengers, self.carrying.remove(action[1]), self.graph, self.traffic, self.neighbors)
        # otherwise state is the same
        return State(self.pos, self.passengers, self.carrying, self.graph, self.traffic, self.neighbors)

class MarkovDecisionProcess:
    def __init__(self, startPassengers, graph, traffic, neighbors, iterations,gamma=.5):
        self.startPassengers = startPassengers # starting configuration of passengers on map as dict from indices to 3-tuples
        self.graph = graph # map as graph with nodes and edges
        self.traffic = traffic # dictionary mapping transition probabilities to edges
        self.neighbors = neighbors # dictionary with nodes as keys and list of neighbor nodes as value
        self.gamma = gamma # discount factor, determined through trial and error
        self.capacity = 4 # maximum number of passengers a driver can carry
        self.iterations = iterations
    
    def getIterations(self): 
        return self.iterations

    def getStates(self):
        """
        Return a list of all states in the MDP.
        Not generally practical for large MDPs.
        """
        states = [self.getStartState()]
        passengerCombos = sum([map(list, combinations(self.startPassengers.keys(), i)) for i in range(len(self.startPassengers.keys()) + 1)], [])
        carCombos = sum([map(list, combinations(self.startPassengers.keys(), i)) for i in range(len(self.startPassengers.keys()) + 1)], [])
        for driverPos in self.graph.nodes(): # for all driver positions
            for passengerCombo in passengerCombos: # for all passenger arrangements on map
                for carCombo in carCombos:  # for all passenger arrangements in car 
                    if len(carCombo) <= self.capacity and not list(set(passengerCombo) & set(carCombo)):
                        state = State(driverPos, passengerCombo, carCombo, self.graph, self.traffic, self.neighbors)
                        if state not in states:
                            states.append(state)
        #for s in states:
            #print s
        return states
        
    def getStartState(self):
        """
        Return the start state of the MDP.
        """
        return State(self.graph.nodes()[0],  self.startPassengers.keys(), [], self.graph, self.traffic, self.neighbors)

    def getPossibleMoves(self, state):
        """
        Return list of possible actions from 'state'
        """
        legalActions = self.neighbors[state.getPos()]
        if (len(state.getCarrying()) < state.getCapacity() and self.pickUp(state) != None and ("Pickup", self.pickUp(state)) not in legalActions):
            legalActions.append(("Pickup", self.pickUp(state)))
        if (self.dropOff(state) != None and ("Dropoff", self.dropOff(state)) not in legalActions):
            legalActions.append(("Dropoff", self.dropOff(state)))
    
        return legalActions
        
    def pickUp(self, state):
        """
        Sees if location matches one of the passenger on the graph's positions, returns passenger
        """
        if state.getPassengers():
            passengers = state.getPassengers()
            for passenger in passengers:
                if state.getPos() == self.startPassengers[passenger][0] and len(state.getCarrying()) < state.getCapacity():
                    return passenger # passenger index
        return None
        
    def dropOff(self, state):
        """
        Sees if location matches one of the passenger dropoff locations, returns updated driver carrying list. 
        or returns passenger like in pickUp?
        """
        if state.getCarrying():
            passengers = state.getCarrying()
            for passenger in passengers: 
                if state.getPos() == self.startPassengers[passenger][1]:
                    return passenger
        return None
        
        
    def getTransitionStatesAndProbs(self, state, action):
        """
        Returns list of (nextState, prob) pairs
        representing the states reachable
        from 'state' by taking 'action' along
        with their transition probabilities.
        
        Note; in Q-Learning and reinforcment
        learning in general, we do not know these
        probabilities nor do we directly model them.
        """
        if action in self.getPossibleMoves(state):
            if type(action) is int:
                go = (state.getSuccessor(action), self.traffic[(state.getPos(), action)])
                stay = (state, 1 - self.traffic[(state.getPos(), action)])
                answer = [go] + [stay]
                return answer
            elif action[0] == "Dropoff" or action[0] == "Pickup":
                #print state
                #print action
                #print state.getSuccessor(action)
                return [(state.getSuccessor(action), 1)]
            else:
                return []
        return []

    def getReward(self, state, action):
        """
        Get the reward for the state, action, nextState transition.
        Not available in reinforcement learning.
        """
        if type(action) is int:
            return -5
        elif action[0] == "Dropoff": #Dropoff
            passenger = self.startPassengers[action[1]]
            return passenger[2]
        elif action[0] == "Pickup": #Pickup
            passenger = self.startPassengers[action[1]]
            return 50 # small incentive
        else:
            return 0

    def isTerminal(self, state):
        """
        Returns true if the current state is a terminal state.  By convention,
        a terminal state has zero future rewards.  Sometimes the terminal state(s)
        may have no possible actions.  It is also common to think of the terminal
        state as having a self-loop action 'pass' with zero reward; the formulations
        are equivalent.
        """
        if not state.getPassengers() and not state.getCarrying():
            return True
        return False