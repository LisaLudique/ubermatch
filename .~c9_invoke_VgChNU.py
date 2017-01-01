import random
from itertools import combinations

class State:
    def __init__(self, pos, graph, traffic, passengers, carrying, driver, myNeighbors):
        self.passengers = passengers # passengers still left on graph, should we make this a dict?
        self.carrying = carrying # passengers being carried by driver
        self.nodes = nodes 
        self.edges = edges 
        self.pos
        self.traffic = traffic 
        self.drivers = drivers
        self.distances = distances
        self.nodeNeighbors = myNeighbors #dictionary with nodes as keys and list of neighbor nodes as value
    
    def getGraph(self):
        return self.graph
        
    def getPos(self):
        return self.pos
    
    def getPassengers(self):
        # list of passengers in entire world
        return self.passengers
    
    def getCarrying(self):
        # list of passengers in the car 
        return self.carrying
        
    def getTraffic(self):
        # preprocessed dictionary with edges as keys and probs as values.
        return self.traffic
    
    def getNeighbors(self):
        return nodeNeighbors
    
    def getSuccessor(self, action): # return set of successor states, should take in an action?
        successors = ()
        if action == ("Pickup", i): #Pickup passenger of certain index with probability 1:
            nextState = State(self.pos, self.graph, self.traffic, self.passengers.remove(i), self.carrying.append(i), self.driver, self.neighbors)
            successors.append(nextState)
        elif action == ("Dropoff", i): #Dropoff with probability 1:
            nextState = State(self.pos, self.graph, self.traffic, self.passengers, self.carrying.remove(i), self.driver)
            successors.append(nextState)
        else: #action is a number of the node to go to
            successors.append(self)
            nextState = State(action, self.graph, self.traffic, self.passengers, self.carrying, self.driver)
            successors.append(nextState)
        return successors
                

class MarkovDecisionProcess:
    def __init__(self,graph, neighbors, traffic, passengers, drivers, gamma=.2): 
        self.gamma = gamma
        self.graph = graph 
        self.neighbors = neighbors
        self.traffic = traffic
        self.passengers = passengers 
        self.drivers = drivers

    def getStates(self, state):
        """
        Return a list of all states in the MDP.
        Not generally possible for large MDPs.
        """
        # return state.getSuccessor()
        # get list of successor states
        # or all possible nodes (driver location) times which passengers are/aren't on graph times of the passengers that aren't on the graph which are being carried by driver
        states = []

        #input = ['a', 'b', 'c', 'd']
        # this is supposed to spit out all combinations of passengers left on graph...idk if it works tho LOL
        # we would use this for passengers, and for carrying remove any elements of length greater than capacity?
        output = sum([map(list, combinations(self.passengers, i)) for i in range(len(self.passengers) + 1)], [])
        
        for driverPos in graph.nodes:
            for passengersOnGraph in output:
                for passengersInCar in [x for x in output if len(x) <= self.capacity]:
            # how to iterate over passenger positions?
                    states.append(State(driverPos, graph, traffic, passengersOnGraph, passengersInCar, drivers, self.neighbors[node]))
        
        
    def getStartState(self):
        """
        Return the start state of the MDP.
        """
        return State(0, self.graph, self.traffic, [], [], self.driver, self.neighbors[0])

    def getPossibleMoves(self, state):
        # legal actions dictionary
        """
        Return list of possible actions from 'state'
        """
        legalActions = self.neighbors[state.getPos()]
        # function: if len(carrying) < capacity and position is equal to a position of a passenger on the map, pickup is possible
        # function: if position is at a destination of a passenger being carried, dropoff is possible
        return self.neighbors[state.getPos()]
        #TODO - also account for drop/off + pickup
        
    def pickUp(self):
        """
        Sees if location matches one of the passenger on the graph's positions, returns list of passengers
        """
        for p in self.passengers:
            if self.pos == p.getPos():
                return p # or the passenger index
        return None
        
    def dropOff(self):
        """
        Sees if location matches one of the passenger droppoff locations, returns updated driver carrying list. 
        """
        
        
    def getTransitionStatesAndProbs(self, state, action):
        #traffic
        """
        Returns list of (nextState, prob) pairs
        representing the states reachable
        from 'state' by taking 'action' along
        with their transition probabilities.
        Note that in Q-Learning and reinforcment
        learning in general, we do not know these
        probabilities nor do we directly model them.
        """
        abstract

    def getReward(self, state, action, nextState):
        """
        Get the reward for the state, action, nextState transition.
        Not available in reinforcement learning.
        """
        # living cost if action ISN'T dropping off passenger
        # small incentive for picking someone up
        # big incentive for dropping someone off
        # otherwise access passenger, get profit
        # return incentive for a terminal state?
        if action == ("Dropoff", i): #Dropoff
            return i.getProfit() # return profit corresponding to passenger i
        elif action == ("Pickup", i): #Pickup
            return 50 # small incentive
        else:
            return -5 #living cost

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
        # check that all passengers have been dropped off