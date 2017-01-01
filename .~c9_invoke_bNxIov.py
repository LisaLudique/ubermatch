import random
#from driverAgents import DriverAgent, Passenger
from itertools import combinations
import itertools as itertools
import pdb

class State:
    def __init__(self, pos, passengers, carrying, graph, traffic, neighbors):
        #self.driver = driver
        self.pos = pos #driver position
        self.passengers = passengers # passengers still left on graph
        self.carrying = carrying # passengers being carried by driver
        self.graph = graph
        self.traffic = traffic 
        self.neighbors = neighbors #dictionary with nodes as keys and list of neighbor nodes as value

        self.capacity = 4
        
    def __str__(self):
        s = ""
        s += "position:" + str(self.pos) + " passengers:" + str([p.getIndex() for p in self.passengers]) + " carrying:" + str([p.getIndex() for p in self.carrying]) 
        return s
        #return "hi"
        
    def getGraph(self):
        return self.graph
        
    def getCapacity(self):
        return self.capacity
        
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
        return self.neighbors
    
    def getSuccessor(self, action): # return set of successor states, should take in an action
        #for neighbor in self.nodeNeighbors:
            #getPassengers = [] 
            #for passenger in self.passengers: 
                #if (neighbor == passenger.getPos()):
                    #getPassengers.append(passenger) #list of passengers at neighbor node
                    
        if type(action) is int: #action is a number of the node to go to
            #currentState = State(self.pos, self.passengers, self.carrying, self.graph, self.traffic, self.neighbors)
            nextState = State(action, self.passengers, self.carrying, self.graph, self.traffic, self.neighbors)
            
        #def __init__(self, pos, passengers, carrying, graph, traffic, neighbors):
        elif action[0] == "Pickup": #Pickup passenger of certain index with probability 1:
            nextState = State(self.pos, self.passengers.remove(action[1]), self.carrying.append(action[1]), self.graph, self.traffic, self.neighbors)
        elif action[0] == "Dropoff": #Dropoff with probability 1:
            nextState = State

        return nextState

class MarkovDecisionProcess:
    def __init__(self, startPassengers, graph, traffic, neighbors, gamma=.2):
        self.startPassengers = startPassengers
        self.graph = graph 
        self.traffic = traffic
        self.neighbors = neighbors
        self.gamma = gamma

    def getStates(self):
        """
        Return a list of all states in the MDP.
        Not generally possible for large MDPs.
        """
        # return state.getSuccessor()
        # get list of successor states
        # or all possible nodes (driver location) times which passengers are/aren't on graph times of the passengers that aren't on the graph which are being carried by driver
        #input = ['a', 'b', 'c', 'd']
        
        states = [self.getStartState()]
        output = sum([map(list, combinations(self.startPassengers, i)) for i in range(len(self.startPassengers) + 1)], [])
        passengerCombos = sum([map(list, combinations(self.startPassengers, i)) for i in range(len(self.startPassengers) + 1)], [])
        carCombos = sum([map(list, combinations(self.startPassengers, i)) for i in range(len(self.startPassengers) + 1)], [])
        for driverPos in self.graph.nodes(): # for all driver positions
            for passengerCombo in passengerCombos: #for all passenger arrangements
                for carCombo in carCombos:  #for all car combos 
                    state = State(driverPos, passengerCombo, carCombo, self.graph, self.traffic, self.neighbors)
                    if state not in states:
                        states.append(state)
        return states
        
    def getStartState(self):
        """
        Return the start state of the MDP.
        """
        # state: def __init__(self, pos, passengers, carrying, graph, traffic, neighbors):
        return State(self.graph.nodes()[0],  self.startPassengers, [], self.graph, self.traffic, self.neighbors)

    def getPossibleMoves(self, state):
        # legal actions dictionary
        """
        Return list of possible actions from 'state'
        """
        legalActions = self.neighbors[state.getPos()]
        if len(state.getCarrying()) < state.getCapacity() and self.pickUp(state):
            legalActions.append(("Pickup", self.pickUp(state)))
        if self.dropOff(state):
            legalActions.append(("Dropoff", self.dropOff(state)))
        return legalActions
        
    def pickUp(self, state):
        """
        Sees if location matches one of the passenger on the graph's positions, returns passenger
        """
        for passenger in state.getPassengers():
            if state.g== passenger.getPos():
                return passenger # or the passenger index
        return None
        
    def dropOff(self, state):
        """
        Sees if location matches one of the passenger dropoff locations, returns updated driver carrying list. 
        or returns passenger like in pickUp?
        """
        #leavingPassengers = [] 
        for passenger in state.getPassengers(): 
            if state.getPos() == passenger.getDestination(): 
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
        
        Note; in Q-Learning and reinforcment
        learning in general, we do not know these
        probabilities nor do we directly model them.
        """
        if type(action) is int:
            # action is a node number
            # state: def __init__(self, pos, passengers, carrying, graph, traffic, neighbors):
            go = (state.getSuccessor(action), self.traffic[(state.getPos(), action)])
            stay = (state, 1 - self.traffic[(state.getPos(), action)])
            answer = [go] + [stay]
            return answer
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