import numpy as np


def random_idxs(N, num_sets):
    idxs = np.random.permutation(np.arange(N*N))[:num_sets]
    return [(idx//N, idx % N) for idx in idxs]


def get_adjs(pos, N):
    i, j = pos
    adjs = []
    if i + 1 < N:
        adjs.append((i + 1, j))
    if i - 1 >= 0:
        adjs.append((i - 1, j))
    if j + 1 < N:
        adjs.append((i, j + 1))
    if j - 1 >= 0:
        adjs.append((i, j - 1))
    return adjs


def check_adjs(pos, N, target):
    "Check if target is an adj of pos"
    adjs = get_adjs(target, N)
    if pos in adjs:
        return False
    return True


def map_generator(N, Wumpus_num, Pit_num, Gold_num=None):
    if Gold_num == None:
        Gold_num = np.random.randint(10, 50)
    num_sets = Wumpus_num + Pit_num + Gold_num + 1

    idxs = random_idxs(N, num_sets)
    agent_pos = idxs.pop(0)
    wumpuses = idxs[:Wumpus_num]
    pits = idxs[Wumpus_num: Wumpus_num + Pit_num + 1]
    golds = idxs[-Gold_num:]

    maze = dict({})

    for i in range(N):
        for j in range(N):
            maze[(i, j)] = ''

    for w in wumpuses:
        adjs = get_adjs(w, N)
        if (agent_pos in adjs):
            return map_generator(N, Wumpus_num, Pit_num, Gold_num)

        for adj in adjs:
            maze[adj] += 'S' if ('S' not in maze[adj]) else ''
        maze[w] = 'W'

    for p in pits:
        adjs = get_adjs(p, N)
        if agent_pos in adjs:
            return map_generator(N, Wumpus_num, Pit_num, Gold_num)
        for adj in adjs:
            maze[adj] += 'B'if ('B' not in maze[adj]) else ''
        maze[p] = 'P'

    for g in golds:
        maze[g] += 'G'

    maze[agent_pos] = 'A'
    for i in range(N):
        for j in range(N):
            if (maze[(i, j)] == ''):
                maze[(i, j)] = '-'

    return N, maze


def print_maze(maze, N):
    s = ''
    for i in range(N):
        for j in range(N):
            s += maze[(i, j)] + '.'
        s = s[:-1] + '\n'
    print(s)


# n, maze = map_generator(10, 3, 3, 3)
# print_maze(maze, n)
