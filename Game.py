from Agent import Agent, Actions, Directions
from MapGenerator import map_generator
from util import readCommand
from GUI import GameGUI
import os
import copy
import logic
import sys


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
            if ('W' in maze[(i, j)]):
                wumpus.append(maze[(i, j)])
            elif ('P' in maze[(i, j)]):
                pits.append(maze[(i, j)])
            elif ('G' in maze[(i, j)]):
                golds.append(maze[(i, j)])
            elif (maze[(i, j)] == 'A'):
                exitPos = maze[(i, j)]

    return wumpus, pits, golds, exitPos


class GameState:
    def initial_state(maze, n):
        explored_set = dict({})
        for i in range(n):
            for j in range(n):
                explored_set[(i, j)] = '#'  # Unexplored == #

        agent = None
        for pos in maze.keys():
            if maze[pos] == 'A':
                exitPos = pos
                explored_set[pos] = '-'  # Mark start place is visited
                try:
                    from logic import AIAgent
                    agent = AIAgent(pos)
                except:
                    raise Exception(
                        'Error! Cannot import AIAgent from logic.py')

        return GameState(explored_set, maze, n, agent, exitPos)
    initial_state = staticmethod(initial_state)

    def __init__(self, explored_set, maze, n, agent, exitPos, score=0):
        self.n = n
        self.explored = explored_set.copy()
        self.maze = maze.copy()

        self.exit = exitPos
        self.agent = agent
        self.score = score
        self.climbout = False

        wumpus_list, _, gold_list, _ = process_maze(maze, n)
        self.max_wumpus = len(wumpus_list)
        self.max_gold = len(gold_list)
        self.killed_wumpus = []

    def copy(self):
        return copy.deepcopy(self)

    def get_start_pos(self):
        for pos in self.maze.keys():
            if self.maze[pos] == 'A':
                return pos

    def isOver(self):
        if ('W' in self.maze[self.agent.pos]):
            return "Lose - Killed by Wumpus"
        if 'P' in self.maze[self.agent.pos]:
            return "Lose - Falled into a pit"
        if (self.climbout):
            return "Win - Agent climbed out of the cave"
        if self.agent.wumpus_killed == self.max_wumpus and self.agent.gold == self.max_gold:
            return "Win - Kill all of wumpuses and golds"
        return None

    def get_successor(curState, agent_action):
        new_state = curState.copy()
        "Agent performing grab a gold"
        if (agent_action == Actions.PICK_GOLD):
            new_state.score += 100
            if (new_state.explored[new_state.agent.pos] == 'G'):
                new_state.explored[new_state.agent.pos] = '-'
            else:
                new_state.explored[new_state.agent.pos] = new_state.explored[new_state.agent.pos].replace(
                    'G', '')
            new_state.agent.gold += 1
        elif agent_action in Actions.SHOOT:
            "Agent Shoots arrows"
            new_state.agent.dir = agent_action[6:]
            dx, dy = Actions.SHOOT[agent_action]
            target = (dx + curState.agent.pos[0], dy + curState.agent.pos[1])
            if (0 <= target[0] < curState.n and 0 <= target[1] < curState.n):
                new_state.score -= 100
                if ('W' in curState.maze[target]):  # Killed wumpus
                    new_state.killed_wumpus.append(target)
                    if curState.maze[target] == 'W':
                        new_state.explored[target] = '-'
                        new_state.maze[target] = '-'
                    else:
                        others = curState.maze[target].replace('W', '')
                        new_state.explored[target] = others
                        new_state.maze[target] = others

                    new_state.agent.wumpus_killed += 1
        elif agent_action == Actions.EXIT:
            "Agent exits the cave"
            if curState.agent.pos != curState.exit:
                raise Exception('There is no exit here')
            else:
                new_state.score += 10
                new_state.climbout = True
        else:
            "Agent moves in any valid direction"
            next_agent_pos = Actions.getSuccessor(
                curState.agent.pos, agent_action)
            if new_state.explored[next_agent_pos] == '#':  # This room is not visited
                new_state.explored[next_agent_pos] = curState.maze[next_agent_pos]

            new_state.agent.move(agent_action)
            new_state.score -= 10

            if new_state.isOver() == 'Lose':
                new_state.score -= 1000
        return new_state

    get_successor = staticmethod(get_successor)

    def get_possible_actions(curState):
        return Actions.getPossibleActions(curState.agent.pos, curState.n)

    get_possible_actions = staticmethod(get_possible_actions)

    def get_adjs(state, pos):
        "Return nodes surrounding pos"
        i, j = pos
        adjs = []
        if i + 1 < state.n:
            adjs.append(((i + 1, j), Directions.NORTH))
        if i - 1 >= 0:
            adjs.append(((i - 1, j), Directions.SOUTH))
        if j + 1 < state.n:
            adjs.append(((i, j + 1), Directions.EAST))
        if j - 1 >= 0:
            adjs.append(((i, j - 1), Directions.WEST))
        return adjs
    get_adjs = staticmethod(get_adjs)


def write_maze(n, maze, f):
    try:
        for i in range(n):
            for j in range(n):
                if j != 0:
                    f.write('.')
                f.write('%3s' % (maze[(i, j)]))
            f.write('\n')
    except:
        raise('Cannot write the map to file')


def run(
    filename=None,  # File used as layout
    N=10,  # Size of the map
    W=5,  # Number of Wumpuses
    P=5,  # Numper of Pits
    G=None,  # Numper of golds
    auto=1,  # The game run automatically
    fps=15
):
    if (filename != None):
        n, maze = try_to_load(filename)
    else:
        n, maze = map_generator(N, W, P, G)

    curState = GameState.initial_state(maze, n)
    ui = GameGUI(n, n)
    ui.fps = fps
    stepModes = not auto
    result = dict({
        'Result': 'Interupted',
        'Score': 0,
        'Gold Picked': 0,
        'Wumpus Killed': 0
    })

    log = open('log.txt', 'w')
    write_maze(n, maze, log)
    desc = ''

    isRunning = True
    ui.open_screen()
    while isRunning:
        "Handling events"
        if stepModes:
            isRunning = ui.waitForTheButton()
        else:
            isRunning = ui.checkEvent()

        if (curState.isOver() != None):
            ui.draw(curState)
            isRunning = False
            result['Score'] = curState.score
            result['Result'] = curState.isOver()
            result['Wumpus Killed'] = curState.agent.wumpus_killed
            result['Gold Picked'] = curState.agent.gold
        else:
            "Get next action"
            next_act = curState.agent.get_action(curState)
            desc = curState.agent.description + '\nAction: ' + str(next_act)

            "Draw current state"
            ui.draw(curState)

            "Render the description "
            if (stepModes):
                ui.draw_description(curState.agent.description)

            "Store the output of the agent"
            log.write(desc)

            "Generate next stage"
            curState = GameState.get_successor(curState, next_act)

    log.close()
    print('-------------------------')
    print("\n".join([str(e) + ": " + str(result[e]) for e in result]))
    print('-------------------------')


def main(argstring):
    argv = argstring.split()
    if argv[0] in ["python", "python3"]:
        argv = argv[1:]
    args = readCommand(argv[1:])
    run(**args)


if __name__ == "__main__":
    args = readCommand(sys.argv[1:])  # Get game components based on input
    run(**args)
