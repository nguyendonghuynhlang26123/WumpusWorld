from Agent import Agent, Actions
import os
import copy
from logic import finding_path
from GUI import GameGUI


def try_to_load(fname):
    if not os.path.exists(fname):
        return None
    f = open(fname)
    try:
        lines = [line.strip('\n') for line in f]
        n = int(lines[0])
        return n, proccess_input(lines[1:])
    finally:
        f.close()


def proccess_input(lines):
    maze = dict({})
    lines.reverse()
    # print('\n'.join(lines))
    lines = [line.split('.') for line in lines]

    for i in range(len(lines)):
        for j in range(len(lines[i])):
            maze[(i, j)] = lines[i][j]
    return maze


def process_maze(maze, n):
    wumpus = []
    pits = []
    golds = []
    exitPos = ()
    for i in range(n):
        for j in range(n):
            if (maze[(i, j)] == 'W'):
                wumpus.append(maze(i, j))
            elif (maze[(i, j)] == 'P'):
                pits.append(maze(i, j))
            elif (maze[(i, j)] == 'G'):
                golds.append(maze(i, j))
            elif (maze[(i, j)] == 'A'):
                exitPos = maze[(i, j)]

    return wumpus, pits, golds, exitPos


class GameState:
    def initial_state(maze, n):
        explored_set = dict({})
        for i in range(n):
            for j in range(n):
                explored_set[(i, j)] = '#'

        for pos in maze.keys():
            if maze[pos] == 'A':
                explored_set[pos] = '-'  # Mark start place is visited
                agent = Agent(pos)

        return GameState(explored_set, maze, n, agent, pos)
    initial_state = staticmethod(initial_state)

    def __init__(self, explored_set, maze, n, agent, exitPos, score=0):
        self.n = n
        self.explored = explored_set.copy()
        self.maze = maze.copy()

        self.exit = exitPos
        self.agent = agent
        self.score = score
        self.climbout = False

        self.number_of_wumpus = 0
        self.number_of_golds = 0

    def copy(self):
        return copy.deepcopy(self)

    def get_start_pos(self):
        for pos in self.maze.keys():
            if self.maze[pos] == 'A':
                return pos

    def isOver(self):
        if (self.maze[self.agent.pos] == 'W' or self.maze[self.agent.pos] == 'P'):
            return "Lose"
        elif (self.climbout):
            return "Win"
        return None

    def get_successor(curState, agent_action):
        new_state = curState.copy()
        if (agent_action == Actions.PICK_GOLD):
            new_state.score += 100
            new_state.explored[new_state.agent.pos] = '-'
        elif agent_action in Actions.SHOOT:
            new_state.score -= 100
        elif agent_action == Actions.EXIT:
            if curState.pos != curState.exit:
                raise Exception('There is no exit here')
            else:
                new_state.climbout = True
        else:
            next_agent_pos = Actions.getSuccessor(
                curState.agent.pos, agent_action)
            new_state.explored[next_agent_pos] = curState.maze[next_agent_pos]

            new_state.agent.move(agent_action)
            new_state.score -= 10
        return new_state

    get_successor = staticmethod(get_successor)

    def get_possible_actions(curState):
        return Actions.getPossibleActions(curState.agent.pos, curState.n)

    get_possible_actions = staticmethod(get_possible_actions)


def run():
    n, maze = try_to_load('input.txt')

    curState = GameState.initial_state(maze, n)
    ui = GameGUI(n, n)

    actions = finding_path(curState)
    print('2')

    isRunning = True
    while isRunning:
        isRunning = ui.checkEvent()

        if (curState.isOver() != None):
            isRunning = False
        else:
            print('1')
            for a in actions:
                curState = GameState.get_successor(curState, a)
                ui.draw(curState.explored, curState.agent, curState.score)


run()
