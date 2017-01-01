import matplotlib.pyplot as plt
import networkx as nx
import random
import copy
 
class Layout:
    def __init__(self, nodes, edges, traffic, passengers, drivers):
        self.passengers = passengers 
        self.nodes = nodes 
        self.edges = edges 
        self.traffic = traffic 
        self.drivers = drivers
        
    def getPassengers(self): 
        return self.passengers 
        
    def getNodes(self): 
        return self.nodes 
        
    def getEdges(self): 
        return self.edges 
        
    def getTraffic(self): 
        return self.traffic 
        
    def getDrivers(self): 
        return self.drivers
            
            