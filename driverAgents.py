import networkx as nx
import random
import mdp
import numpy as np
import pdb 
import sys

class DriverAgent:
    """
    Represents an Uber driver
    """
    def __init__(self, pos, index, edges, neighbors):
        self.pos = pos # Starting position of driver
        self.index = index  # Index of driver (zero-indexed as there is only one)
        self.values = {} # Dictionary mapping states to values/utilities
        
    def getValues(self): 
        """
        Return values table
        """
        return self.values
                
    def bruteForce(self, MarkovDecisionProcess): 
        """
        Randomized policy against which we test our policy
        """
        policy = {} 
        for s in MarkovDecisionProcess.getStates(): 
            index = np.random.choice(xrange(len(MarkovDecisionProcess.getPossibleMoves(s))))
            policy[str(s)] = MarkovDecisionProcess.getPossibleMoves(s)[index]
        return policy
            
    def policyIterate(self, MarkovDecisionProcess):
        """
        Solve MDP by policy iteration
        """
        policy = {}
        # initialize the policy to have random legal actions for each state
        for s in MarkovDecisionProcess.getStates():
            if len(MarkovDecisionProcess.getPossibleMoves(s)) == 0:
                policy[str(s)] = s.getPos()
            else:
                index = np.random.choice(xrange(len(MarkovDecisionProcess.getPossibleMoves(s))))
                policy[str(s)] = MarkovDecisionProcess.getPossibleMoves(s)[index]
                
        # initialize the values table to have initial utility 0 for all states
        for s in MarkovDecisionProcess.getStates():
            self.values[str(s)] = 0
       
        while True: # runs until policy converges
            unchanged = True
            
            # evaluate current policy and get updated values for each state
            self.values = self.policyEvaluate(policy, self.values, MarkovDecisionProcess)
            
            for s in MarkovDecisionProcess.getStates():
                bestUtility = None
                for a in MarkovDecisionProcess.getPossibleMoves(s):
                    if self.expectedUtility(a, s, self.values, MarkovDecisionProcess) > bestUtility:
                        bestUtility = a # argmax (indicates action resulting in highest expected utility for the state)
                if MarkovDecisionProcess.getPossibleMoves(s):
                    if bestUtility != policy.get(str(s), random.choice(MarkovDecisionProcess.getPossibleMoves(s))):
                        policy[str(s)] = bestUtility
                        unchanged = False # policy was altered
            if unchanged:
                return policy # policy converged
                
    def expectedUtility(self, action, state, values, MarkovDecisionProcess):
        """
        Calculate expected utility given a state and an action.
        """
        probs = 0
        for (s1, p) in MarkovDecisionProcess.getTransitionStatesAndProbs(state, action):
            probs += p * values.get(s1, 0)
        probs *= MarkovDecisionProcess.gamma
        expectation = MarkovDecisionProcess.getReward(state, action) + probs
        return expectation

        
    def policyEvaluate(self, policy, values, MarkovDecisionProcess):
        """
        Return an updated utility mapping values from each state in the MDP to its utility, using an approximation (modified policy iteration).
        """
        for i in xrange(MarkovDecisionProcess.getIterations()):
            for s in MarkovDecisionProcess.getStates():
                probs = 0
                if not (list(set(s.carrying) & set(s.passengers))):
                    for (s1, p) in MarkovDecisionProcess.getTransitionStatesAndProbs(s, policy[str(s)]):
                        probs += p * values.get(s1, 0)
                    probs *= MarkovDecisionProcess.gamma
                    if not MarkovDecisionProcess.getPossibleMoves(s): 
                        values[s] = MarkovDecisionProcess.getReward(s, []) + probs
                    else:
                        values[s] = MarkovDecisionProcess.getReward(s, policy.get(str(s), random.choice(MarkovDecisionProcess.getPossibleMoves(s)))) + probs
        return values
    
    def getPos(self):
        return self.pos
    
    def getIndex(self): 
        return self.index   