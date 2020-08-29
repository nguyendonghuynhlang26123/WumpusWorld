from Agent import Agent, Actions, Directions
from MapGenerator import map_generator
import os
import copy
import logic
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
    def initial_state(maze, n, agent_type="Agent"):
        explored_set = dict({})
        for i in range(n):
            for j in range(n):
                explored_set[(i, j)] = '#'  # Unexplored == #

        agent = None
        for pos in maze.keys():
            if maze[pos] == 'A':
                exitPos = pos
                explored_set[pos] = '-'  # Mark start place is visited
                if agent_type == "Agent":
                    agent = Agent(pos)
                else:
                    print("voov")
                    try:
                        from logic import AIAgentII
                        agent = AIAgentII(pos)
                    except:
                        raise Exception('Error')

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

        wumpus_list, pits_list, gold_list, _ = process_maze(maze, n)
        self.max_wumpus = len(wumpus_list)
        self.max_gold = len(gold_list)

    def copy(self):
        return copy.deepcopy(self)

    def get_start_pos(self):
        for pos in self.maze.keys():
            if self.maze[pos] == 'A':
                return pos

    def isOver(self):
        if ('W' in self.maze[self.agent.pos] or 'P' in self.maze[self.agent.pos]):
            return "Lose"
        elif (self.climbout or
              (self.agent.wumpus_killed == self.max_wumpus and self.agent.gold == self.max_gold)):
            return "Win"
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
            dx, dy = Actions.SHOOT[agent_action]
            target = (dx + curState.agent.pos[0], dy + curState.agent.pos[1])
            if (0 <= target[0] < curState.n and 0 <= target[1] < curState.n):
                new_state.score -= 100
                if ('W' in curState.maze[target]):
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


def run():
    #n, maze = try_to_load('input.txt')
    n, maze = map_generator(10, 5, 5)

    curState = GameState.initial_state(maze, n, "AIAgentII")
    ui = GameGUI(n, n)
    result = dict({
        'Result': '',
        'Score': 0,
        'Gold Picked': 0,
        'Wumpus Killed': 0
    })

    isRunning = True
    waitforButt = False
    while isRunning:
        isRunning = ui.checkEvent(waitforButt)

        if (curState.isOver() != None):
            isRunning = False
            result['Score'] = curState.score
            result['Result'] = curState.isOver()
            result['Wumpus Killed'] = curState.agent.wumpus_killed
            result['Gold Picked'] = curState.agent.gold
        else:
            next_act = curState.agent.get_action(curState)
            curState = GameState.get_successor(curState, next_act)
            ui.draw(curState, next_act)
    print('-------------------------')
    print("\n".join([str(e) + ": " + str(result[e]) for e in result]))
    print('-------------------------')


if __name__ == "__main__":
    run()
