import itertools
import re

#from utils import *

# a game node


class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.name = str(row)+","+str(col)
        self.adj = ["", "", "", ""]  # up, right, down, left (clockwise)

    def __repr__(self):
        return ("(Name : " + str(self.name) + " , " +
                " left : " + self.adj[3] + " , " + " Right : " + self.adj[1] + " , " +
                " Up : " + self.adj[0] + " , " + " Down : " + self.adj[2] + " , " + ")")

# character state


class Player:
    def __init__(self, node, dir):
        self.current_node = node
        self.current_direction = dir
        self.gold = 0
        self.wumpus_killed = 0
        self.iLeaving = False

    def move(self, nodes):
        if nodes[self.current_node.adj[self.current_direction]] != "W":  # Direction node is not wall
            self.current_node = nodes[self.current_node.adj[self.current_direction]]

    def turn(self, dir):
        self.current_direction = (self.current_direction+dir) % 4

    def __repr__(self):
        return ("Current Node : " + str(self.current_node.name) + " , " +
                "Current Direction : " + str(self.current_direction))


class Game_State:
    def __init__(self):
        self.nodes = dict()
        self.visited_node = []
        self.unvisited_safe_node = []
        self.max_row = -1
        self.max_col = -1

    def add_node(self, node):
        # update adjacent nodes
        if self.max_col != -1 and node.col == self.max_col:
            node.adj[1] = "W"  # Meet wall on the right
        else:
            node.adj[1] = str(node.row)+","+str(node.col+1)
        if node.col == 1:
            node.adj[3] = "W"  # Meet left wall
        else:
            node.adj[3] = str(node.row)+","+str(node.col-1)
        if self.max_row != -1 and node.row == self.max_row:
            node.adj[0] = "W"  # Meet upper wall
        else:
            node.adj[0] = str(node.row+1)+","+str(node.col)
        if node.row == 1:
            node.adj[2] = "W"  # Meet bottom wall
        else:
            node.adj[2] = str(node.row-1)+","+str(node.col)
        self.nodes[node.name] = node
        if node.name not in self.visited_node:
            self.visited_node.append(node.name)

    def __repr__(self):
        return ("Nodes : " + str(self.nodes.keys()) + " , " +
                " Visited Nodes : " + str(self.visited_node))


class KB:
    def __init__(self, sentence=None):
        self.KB = []
    # add sentence to KB

    def tell(self, sentence):
        if sentence not in self.KB:
            self.KB.append(sentence)
            self.KB = sorted(self.KB, key=lambda x: len(x))
    # check for resolution compatibility

    def compare(self, query1, query2):
        if len(query1) == 1:
            for item in query2:
                if query1[0][0] == "~" and item[0:] == query1[0][1:]:
                    query2.remove(item)
                elif item[0] == "~" and query1[0][0:] == item[1:]:
                    query2.remove(item)
    # check for substitution that make a query true

    def check(self, query):
        KB_temp = [[item2 for item2 in item] for item in self.KB]
        KB_temp.append(query)
        KB_temp = sorted(KB_temp, key=lambda x: len(x))
        for item1 in KB_temp:
            if len(item1) > 0:
                for item2 in KB_temp:
                    self.compare(item1, item2)
            else:
                return True
        return False

    # discard sentence from KB

    def retract(self, sentence):
        for item1 in self.KB:
            for item2 in item1:
                if item2 == sentence or item2 == ("~"+sentence):
                    item1.remove(item2)
            if len(item1) == 0:
                self.KB.remove(item1)


class AIPlayer:
    def __init__(self):
        self.states = 'W'


def finding_path(initial_state):
    from Game import GameState
    KB = []
    print(GameState.get_possible_actions(initial_state))
    return ['North', 'North', 'North', 'North', 'East', 'North', 'West']