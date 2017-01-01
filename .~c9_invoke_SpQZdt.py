import random
#from driverAgents import DriverAgent, Passenger
from itertools import combinations
import itertools as itertools
import pdb

class State:
    def __init__(self, pos, graph, traffic, passengers, carrying, driver, myNeighbors):
        self.passengers = passengers # passengers still left on graph
        self.carrying = carrying # passengers being carried by driver
        self.traffic = traffic 
        self.driver = driver
        self.nodeNeighbors = myNeighbors #dictionary with nodes as keys and list of neighbor nodes as value
        self.graph = graph
        
    def __str__(self):
        s = "position:", self.pos, "passengers:", self.passengers, "carrying:", self.
            
    def getGraph(self):
        return self.graph
        
    def getPos(self):
        return self.driver.getPos()
    
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
        return self.nodeNeighbors
    
    def getSuccessor(self, action): # return set of successor states, should take in an action
        successors = set()
        #for neighbor in self.nodeNeighbors:
            #getPassengers = [] 
            #for passenger in self.passengers: 
                #if (neighbor == passenger.getPos()):
                    #getPassengers.append(passenger) #list of passengers at neighbor node
        if type(action) is int: #action is a number of the node to go to
            successors.add(self)
            nextState = State(action, self.graph, self.traffic, self.passengers, self.carrying, self.driver, self.nodeNeighbors)
            successors.add(nextState)
        elif action[0] == "Pickup": #Pickup passenger of certain index with probability 1:
            nextState = State(self.getPos(), self.graph, self.traffic, self.passengers.remove(action[1]), self.carrying.append(action[1]), self.driver, self.nodeNeighbors)
            successors.add(nextState)
        elif action[0] == "Dropoff": #Dropoff with probability 1:
            nextState = State(self.getPos(), self.graph, self.traffic, self.passengers, self.carrying.remove(action[1]), self.driver, self.nodeNeighbors)
            successors.add(nextState)
 
        return successors
                

class MarkovDecisionProcess:
    def __init__(self, graph, traffic, passengers, startPassengers, driver, neighbors, gamma=.2): 
        self.gamma = gamma
        self.graph = graph 
        self.neighbors = neighbors
        self.traffic = traffic
        self.passengers = passengers 
        self.driver = driver
        self.startPassengers = startPassengers
        self.pos = driver.getPos()

    def getStates(self):
        """
        Return a list of all states in the MDP.
        Not generally possible for large MDPs.
        """
        # return state.getSuccessor()
        # get list of successor states
        # or all possible nodes (driver location) times which passengers are/aren't on graph times of the passengers that aren't on the graph which are being carried by driver
        #input = ['a', 'b', 'c', 'd']
        
        states = []
        output = sum([map(list, combinations(self.passengers, i)) for i in range(len(self.passengers) + 1)], [])
        passengerCombos = sum([map(list, combinations(self.passengers, i)) for i in range(len(self.passengers) + 1)], [])
        carCombos = sum([map(list, combinations(self.passengers, i)) for i in range(len(self.passengers) + 1)], [])
        
        for driverPos in self.graph.nodes(): # for all driver positions
            for passengerCombo in passengerCombos: #for all passenger arrangements
                for carCombo in carCombos:  #for all car combos 
                    #if (len(carCombo) <= self.driver.getCapacity()):
                    states.append(State(driverPos, self.graph, self.traffic, passengerCombo, carCombo, self.driver, self.neighbors[driverPos]))
        return states
        
    def getStartState(self):
        """
        Return the start state of the MDP.
        """
        return State(0, self.graph, self.traffic, self.startPassengers, [], self.driver, self.neighbors[0])

    def getPossibleMoves(self, state):
        # legal actions dictionary
        """
        Return list of possible actions from 'state'
        """
        legalActions = self.neighbors[state.getPos()]
        if len(self.driver.carrying) < self.driver.capacity and self.pickUp():
            legalActions.append(("Pickup", self.pickUp()))
        if self.dropOff():
            legalActions.append(("Dropoff", self.dropOff()))
        return legalActions
        
    def pickUp(self):
        """
        Sees if location matches one of the passenger on the graph's positions, returns passenger
        """
        for passenger in self.passengers:
            if self.pos == passenger.getPos():
                return passenger # or the passenger index
        return None
        
    def dropOff(self):
        """
        Sees if location matches one of the passenger dropoff locations, returns updated driver carrying list. 
        or returns passenger like in pickUp?
        """
        #leavingPassengers = [] 
        for passenger in self.driver.getPassengers(): 
            if self.pos == passenger.getDestination(): 
                return passenger
        return None
        #for person in leavingPassengers: 
            #self.driver.carrying.remove(person)
            #self.passengers.remove(person)
        
        
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
        if type(action) is int:
            # action is a node number
            go = (State(action, self.graph, self.traffic, self.passengers, self.driver.getPassengers(), self.driver, self.neighbors), self.traffic[(state.getPos(), action)])
            stay = (state, 1 - self.traffic[(state.getPos(), action)])
            return [go] + [stay]
        elif action[0] == "Dropoff" or action[0] == "Pickup":
            return [(state.getSuccessor(action), 1)]


    def getReward(self, state, action):
        """
        Get the reward for the state, action, nextState transition.
        Not available in reinforcement learning.
        """
        # living cost if action ISN'T dropping off passenger
        # small incentive for picking someone up
        # big incentive for dropping someone off
        # otherwise access passenger, get profit
        # return incentive for a terminal state?
        if type(action) is int:
            return -5
        elif action[0] == "Dropoff": #Dropoff
            return action[1].getProfit() # return profit corresponding to passenger i
        elif action[0] == "Pickup": #Pickup
            return 50 # small incentive


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