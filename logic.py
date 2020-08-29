import itertools
import re
from Agent import Agent, Directions, Actions
from Game import GameState
from util import PriorityQueue
#from utils import *

# a game node


# class Node:
#     def __init__(self, row, col):
#         self.row = row
#         self.col = col
#         self.name = str(row)+","+str(col)
#         self.adj = ["", "", "", ""]  # up, right, down, left (clockwise)

#     def __repr__(self):
#         return ("(Name : " + str(self.name) + " , " +
#                 " left : " + self.adj[3] + " , " + " Right : " + self.adj[1] + " , " +
#                 " Up : " + self.adj[0] + " , " + " Down : " + self.adj[2] + " , " + ")")

# character state


# class Player:
#     def __init__(self, node, dir):
#         self.current_node = node
#         self.current_direction = dir
#         self.gold = 0
#         self.wumpus_killed = 0
#         self.iLeaving = False

#     def move(self, nodes):
#         if nodes[self.current_node.adj[self.current_direction]] != "W":  # Direction node is not wall
#             self.current_node = nodes[self.current_node.adj[self.current_direction]]

#     def turn(self, dir):
#         self.current_direction = (self.current_direction+dir) % 4

#     def __repr__(self):
#         return ("Current Node : " + str(self.current_node.name) + " , " +
#                 "Current Direction : " + str(self.current_direction))


# class Game_State:
#     def __init__(self):
#         self.nodes = dict()
#         self.visited_node = []
#         self.unvisited_safe_node = []
#         self.max_row = -1
#         self.max_col = -1

#     def add_node(self, node):
#         # update adjacent nodes
#         if self.max_col != -1 and node.col == self.max_col:
#             node.adj[1] = "W"  # Meet wall on the right
#         else:
#             node.adj[1] = str(node.row)+","+str(node.col+1)
#         if node.col == 1:
#             node.adj[3] = "W"  # Meet left wall
#         else:
#             node.adj[3] = str(node.row)+","+str(node.col-1)
#         if self.max_row != -1 and node.row == self.max_row:
#             node.adj[0] = "W"  # Meet upper wall
#         else:
#             node.adj[0] = str(node.row+1)+","+str(node.col)
#         if node.row == 1:
#             node.adj[2] = "W"  # Meet bottom wall
#         else:
#             node.adj[2] = str(node.row-1)+","+str(node.col)
#         self.nodes[node.name] = node
#         if node.name not in self.visited_node:
#             self.visited_node.append(node.name)

#     def __repr__(self):
#         return ("Nodes : " + str(self.nodes.keys()) + " , " +
#                 " Visited Nodes : " + str(self.visited_node))


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
        KB_temp = self.KB.copy()
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


def name(pos: tuple):
    return str(int(pos[0])) + ',' + str(int(pos[1]))


class AIPlayer(Agent):
    def __init__(self, pos):
        super().__init__(pos)
        # self.states = Game_State()
        # self.states.add_node((0, 0))
        self.visited_node = []
        self.visited_node.append((0, 0))
        self.unvisited_safe_node = []
        #self.player = Player("1,1", 1)

        self.KB = KB()
        self.KB.tell(["~P" + name(pos)])
        self.KB.tell(["~W" + name(pos)])

        self.actions = []
        #self.killing_wumpus = False

    def clear_base(self):
        remove_list = []
        for item in self.KB.KB:
            if item[0][0] == "W" or item[0][1] == "W":  # remove clause with W or ~W
                remove_list.append(item)
        for item in remove_list:
            self.KB.KB.remove(item)

    def wumpus_check(self, pos, adjs):
        row = int(pos[0])
        col = int(pos[1])

        if ((row, col + 1), Directions.EAST) in adjs:
            if self.KB.check(["W" + str(row - 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col + 1)]) or self.KB.check(
                    ["W" + str(row + 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col + 1)]):
                self.kill_wumpus(Directions.EAST)

        if ((row + 1, col), Directions.NORTH) in adjs:
            if self.KB.check(["W" + str(row) + "," + str(col - 1)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col - 1)]) or self.KB.check(
                    ["W" + str(row) + "," + str(col + 1)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col + 1)]):
                self.kill_wumpus(Directions.NORTH)

        if ((row, col - 1), Directions.WEST) in adjs:
            if self.KB.check(["W" + str(row - 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col - 1)]) or self.KB.check(
                    ["W" + str(row + 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col - 1)]):
                self.kill_wumpus(Directions.WEST)

        if ((row - 1, col), Directions.SOUTH) in adjs:
            if self.KB.check(["W" + str(row) + "," + str(col - 1)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col - 1)]) or self.KB.check(
                    ["W" + str(row) + "," + str(col + 1)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col + 1)]):
                self.kill_wumpus(Directions.SOUTH)

    def kill_wumpus(self, dir):
        self.actions = []
        self.actions.insert(0, Actions.shoot(dir))

    def safe_check(self, pos, adjs):
        for adj, _ in adjs:
            if adj not in self.visited_node and adj not in self.unvisited_safe_node:
                if self.KB.check(["P" + name(adj)]) and self.KB.check(["W" + name(adj)]):
                    self.unvisited_safe_node.append(name(adj))

    def handle_bump(self):
        pass

    def handle_stench(self, cur_pos, adjs):
        sentence = []
        for adj, _ in adjs:
            if adj not in self.visited_node:
                sentence.append("W"+name(adj))

        self.KB.tell(sentence)
        self.KB.tell(["S"+name(cur_pos)])

    def handle_breeze(self, pos, adjs):
        sentence = []
        for adj, _ in adjs:
            if adj not in self.visited_node:
                sentence.append("P"+name(adj))
        self.KB.tell(sentence)
        self.KB.tell(["B"+name(pos)])

    def handle_not_breeze(self, pos, adjs):
        for adj, _ in adjs:
            if adj not in self.visited_node:
                self.KB.tell(["~P"+name(adj)])

    def handle_not_stench(self, pos, adjs):
        for adj, _ in adjs:
            if adj not in self.visited_node:
                self.KB.tell(["~W"+name(adj)])


def finding_path(initial_state):
    KB = []
    print(GameState.get_possible_actions(initial_state))
    return ['North', 'North', Actions.PICK_GOLD, 'North', 'North', 'East', 'North', 'West']


class AIAgentII(AIPlayer):
    def __init__(self, pos):
        super(AIAgentII, self).__init__(pos)
        self.visited = []
        self.safe_places = []
        self.KB = KB()
        self.KB.tell(["~P" + name(pos)])
        self.KB.tell(["~W" + name(pos)])
        self.visited.append(pos)
        self.actions = []

    def is_safe(self, pos):
        #print("check", pos)
        return self.KB.check(["P" + name(pos)]) and self.KB.check(["W" + name(pos)])

    def nearest_safe_place(self):
        dist = []
        for room in self.safe_places:
            dist.append(abs(self.pos[0] - room[0]) +
                        abs(self.pos[1] - room[1]))
        return self.safe_places[dist.index(min(dist))]

    def get_action(self, state):
        if (self.actions != []):
            return self.actions.pop(0)

        pos = state.agent.pos
        adjs = GameState.get_adjs(state, pos)

        "Add KB"
        if 'S' in state.explored[pos]:
            self.handle_stench(pos, adjs)
            self.wumpus_check(pos, adjs)
        else:
            self.handle_not_stench(pos, adjs)

        if 'B' in state.explored[pos]:
            self.handle_breeze(pos, adjs)
        else:
            self.handle_not_breeze(pos, adjs)

        "Update safe places"
        print(pos, '-----')
        for adj, _ in adjs:
            if (self.is_safe(adj)) and adj not in self.visited and adj not in self.safe_places:
                print("Check ", adj, "=> Safe")
                self.safe_places.append(adj)
            else:
                print("Check ", adj, "=> UnSafe")

        "Update visited lists"
        self.visited.append(pos)
        if (pos in self.safe_places):
            self.safe_places.remove(pos)

        # print(self.KB.KB)
        if ('G' in state.explored[pos]):
            return Actions.PICK_GOLD

        if (self.safe_places != []):
            self.actions = ucs(state, self.nearest_safe_place())
            return self.actions.pop(0)

        "If there is no safe place => Exit"
        if pos == state.exit and self.iLeaving:
            return Actions.EXIT
        else:
            self.iLeaving = True
            print("EXIT", state.exit)
            self.actions = ucs(state, state.exit)
            return self.actions.pop(0)


def getCostOfActions(state, pos, actions):
    score = 0
    for a in actions:
        pos = Actions.getSuccessor(pos, a)
        if (state.explored[pos] != '#'):
            score += 1
        else:
            score += 1000
    return score


def ucs(current_state, goal_pos, chooseVisited=False):
    startpos = current_state.agent.pos
    factor = -1 if chooseVisited else 1
    #print(startpos, goal_pos)

    explored = []
    frontier = PriorityQueue()
    frontier.push((startpos, []), 0)
    while not frontier.isEmpty():
        pos, moves = frontier.pop()
        if pos == goal_pos:
            return moves
        explored.append(pos)

        for adj, action in GameState.get_adjs(current_state, pos):
            if adj not in explored:
                newMoves = moves + [action]
                frontier.update(
                    (adj, newMoves), factor * getCostOfActions(
                        current_state, startpos, newMoves)
                )
