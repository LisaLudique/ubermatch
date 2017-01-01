import random
from driverAgents import DriverAgent, Passenger
from itertools import combinations

class State:
    def __init__(self, pos, graph, traffic, passengers, carrying, driver, myNeighbors):
        self.passengers = passengers # passengers still left on graph
        self.carrying = carrying # passengers being carried by driver
        self.traffic = traffic 
        self.driver = driver
        self.nodeNeighbors = myNeighbors #dictionary with nodes as keys and list of neighbor nodes as value
        self.graph = graph
    
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
    
    def getSuccessor(self, action): # return set of successor states, should take in an action?
        successors = set()
        for neighbor in self.nodeNeighbors:
            getPassengers = [] 
            for passenger in self.passengers: 
                if (neighbor == passenger.getPos()):
                    getPassengers.append(passenger) #list of passengers at neighbor node
                        
            if action == ("Pickup", neighbor): #Pickup passenger of certain index with probability 1:
            
                nextState = State(self.pos, self.graph, self.traffic, self.passengers -= getPassengers, self.carrying += getPassengers, self.driver, self.neighbors)
                successors.add(nextState)
            elif action == ("Dropoff", neighbor): #Dropoff with probability 1:
                nextState = State(self.pos, self.graph, self.traffic, self.passengers, self.carrying.remove(i), self.driver)
                successors.add(nextState)
            else: #action is a number of the node to go to
                successors.add(self)
                nextState = State(action, self.graph, self.traffic, self.passengers, self.carrying, self.driver)
                successors.add(nextState)
        return successors
                

class MarkovDecisionProcess:
    def __init__(self, graph, neighbors, traffic, passengers, driver, gamma=.2): 
        self.gamma = gamma
        self.graph = graph 
        self.neighbors = neighbors
        self.traffic = traffic
        self.passengers = passengers 
        self.driver = driver
        self.pos = driver.getPos()

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
        #output = sum([map(list, combinations(self.passengers, i)) for i in range(len(self.passengers) + 1)], [])
        passengerCombos = [] 
        for i in range(0, len(self.passengers) + 1): 
            passengerCombos += itertools.combinations(self.passengers, i)
            
        carCombos = [] 
        for i in range(0, self.driver.getCapacity() + 1):
            carCombos += itertools.combinations(self.passengers, i)
        
        for driverPos in self.graph.nodes:
            for passengerCombo in passengerCombos:
                for carCombo in carCombos: 
                    if (len(carCombo) + len(passengerCombo) == len(self.passengers)):
                        states.append(State(driverPos, self.graph, self.traffic, passengerCombo, carCombo, self.driver, self.neighbors[driverPos]))
        
        
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
        if len(self.driver.carrying) < self.driver.capacity and pickUp:
            legalActions.append("Pickup", self.pickUp())
        # function: if position is at a destination of a passenger being carried, dropoff is possible
        if self.dropOff():
            legalActions.append("Dropoff", self.dropOff)
        return legalActions
        #return self.neighbors[state.getPos()]
        #TODO - also account for drop/off + pickup
        
    def pickUp(self):
        """
        Sees if location matches one of the passenger on the graph's positions, returns passenger
        """
        for p in self.passengers:
            if self.pos == p.getPos():
                return p # or the passenger index
        return None
        
    def dropOff(self):
        """
        Sees if location matches one of the passenger dropoff locations, returns updated driver carrying list. 
        or returns passenger like in pickUp?
        """
        leavingPassengers = [] 
        for passenger in self.driver.getPassengers(): 
            if (self.pos == passenger.getDestination()): 
                leavingPassengers.append(passenger)
        return leavingPassengers
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
        if action == ("Dropoff", i) or action == ("Pickup", i):
            return [(state.getSuccessor(action), 1)]
        else:
            # action is a node number
            go = (action, self.traffic[action])
            stay = (action, 1 - self.traffic[action])
            return [go] + [stay]

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