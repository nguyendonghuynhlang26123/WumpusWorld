from Agent import Agent, Directions, Actions
from Game import GameState
from util import PriorityQueue


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


class AIAgent(Agent):
    def __init__(self, pos):
        super(AIAgent, self).__init__(pos)
        self.visited = []
        self.safe_places = []
        self.KB = KB()
        self.KB.tell(["~P" + name(pos)])
        self.KB.tell(["~W" + name(pos)])
        self.visited.append(pos)
        self.actions = []
        self.checked_places = []
        self.description = ''

    def clear_base(self):
        remove_list = []
        for item in self.KB.KB:
            if item[0][0] == "W" or item[0][1] == "W":  # remove clause with W or ~W
                remove_list.append(item)
        for item in remove_list:
            self.KB.KB.remove(item)

    def handle_stench(self, cur_pos, adjs):
        sentence = []
        for adj, _ in adjs:
            if adj not in self.visited:
                sentence.append("W"+name(adj))

        self.KB.tell(sentence)
        self.KB.tell(["S"+name(cur_pos)])

    def handle_breeze(self, pos, adjs):
        sentence = []
        for adj, _ in adjs:
            if adj not in self.visited:
                sentence.append("P"+name(adj))
        self.KB.tell(sentence)
        self.KB.tell(["B"+name(pos)])

    def handle_not_breeze(self, pos, adjs):
        for adj, _ in adjs:
            if adj not in self.visited:
                self.KB.tell(["~P"+name(adj)])

    def handle_not_stench(self, pos, adjs):
        for adj, _ in adjs:
            if adj not in self.visited:
                self.KB.tell(["~W"+name(adj)])

    def is_safe(self, pos):
        return self.KB.check(["P" + name(pos)]) and self.KB.check(["W" + name(pos)])

    def wumpus_check(self, pos, adjs):
        row = int(pos[0])
        col = int(pos[1])
        if ((row, col + 1), Directions.EAST) in adjs:
            if (self.KB.check(["W" + str(row - 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col + 1)])) or (self.KB.check(
                    ["W" + str(row + 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col + 1)])):
                return Directions.EAST, (row, col + 1)

        if ((row + 1, col), Directions.NORTH) in adjs:
            if self.KB.check(["W" + str(row) + "," + str(col - 1)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col - 1)]) or self.KB.check(
                    ["W" + str(row) + "," + str(col + 1)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col + 1)]):
                return Directions.NORTH, (row + 1, col)

        if ((row, col - 1), Directions.WEST) in adjs:
            if self.KB.check(["W" + str(row - 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col - 1)]) or self.KB.check(
                    ["W" + str(row + 1) + "," + str(col)]) and self.KB.check(
                    ["~S" + str(row + 1) + "," + str(col - 1)]):
                return Directions.WEST, (row, col - 1)

        if ((row - 1, col), Directions.SOUTH) in adjs:
            if self.KB.check(["W" + str(row) + "," + str(col - 1)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col - 1)]) or self.KB.check(
                    ["W" + str(row) + "," + str(col + 1)]) and self.KB.check(
                    ["~S" + str(row - 1) + "," + str(col + 1)]):
                return Directions.SOUTH, (row - 1, col)

        return None, None

    def recheck_stenches(self, state):
        possible_safe = []
        for pos in self.stenches:
            if 'S' in state.explored[pos]:
                adjs = GameState.get_adjs(state, pos)
                _, target_pos = self.wumpus_check(pos, adjs)
                if (target_pos != None and target_pos not in self.checked_places):
                    possible_safe.append(pos)

        return possible_safe

    def get_action(self, state):
        pos = state.agent.pos
        adjs = GameState.get_adjs(state, pos)
        self.description = '\n--------------------\nPos: ' + name(pos) + '\n'
        self.description += "KB:\t" + str(self.KB.KB) + '\n'

        "Moving following by the temporary goals"
        if (self.actions != []):
            self.description += 'Goal: Move to the next safe place: '
            if (self.iLeaving):
                self.description += name(state.exit) + ' (Exit)'
            else:
                self.description += name(self.safe_places[0])
            return self.actions.pop(0)

        "Gold picking - Prioritize picking gold"
        if ('G' in state.explored[pos]):
            self.description += 'Goal: Pick gold'
            return Actions.PICK_GOLD

        "Add KB"
        if 'S' in state.explored[pos]:
            self.handle_stench(pos, adjs)
            "If there is enough condition to conclude the wumpus position"
            target_dir, target_pos = self.wumpus_check(pos, adjs)
            if (target_dir != None and target_pos not in self.checked_places):
                self.checked_places.append(target_pos)
                # self.safe_places.append(target_pos)
                self.description += 'Goal: Attempting to shoot at ' + \
                    name(target_pos)
                return Actions.shoot(target_dir)
        else:
            self.handle_not_stench(pos, adjs)
        if 'B' in state.explored[pos]:
            self.handle_breeze(pos, adjs)
        else:
            self.handle_not_breeze(pos, adjs)

        "Update safe places"
        temp = []
        for adj, _ in adjs:
            if (self.is_safe(adj)) and adj not in self.visited and adj not in self.safe_places:
                temp.append(adj)
                self.safe_places.insert(0, adj)
        if (temp != []):
            self.description += 'Percept: ' + \
                str(temp) + ' is safe and not yet visited\n'

        "Update visited lists"
        self.visited.append(pos)
        if (pos in self.safe_places):
            self.safe_places.remove(pos)

        "Find the next place to move"
        if (self.safe_places != []):
            self.actions = ucs(state, self.safe_places[0])
            self.description += 'Goal: Move to the next unvisited safe place: ' + \
                name(self.safe_places[0])
            return self.actions.pop(0)

        "If there is no safe place => Exit"
        if pos == state.exit and self.iLeaving:
            self.description += 'Goal: Climb out of the cave'
            return Actions.EXIT
        else:
            self.iLeaving = True
            self.description += 'Goal: Find the exit to leave'
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
    # print(startpos, goal_pos)

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
