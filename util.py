import heapq
import sys


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def has(self, item):
        return len([i for (p, c, i) in self.heap if item != i]) > 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i[0] == item[0]:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

    def __repr__(self):
        return str(self.heap)


def readCommand(argv):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser

    usageStr = """
    USAGE:      python Game.py <options>
                STEPS BY STEPS mode (-a 0): program run steps by steps description will 
                                            be displayed in the game screen.
                AUTOMATIC mode (-a 1): program run automatically. In this mode, description
                                        won't be displayed

    EXAMPLES:   (1) python Game.py
                    - starts a game with default setting
                (2) python Game.py --generator n=10,w=5,p=5,g=20 --automatic 1 --fps 5
                OR  python Game.py -g n=10,w=5,p=5,g=20 -a 1 -f 5
                    - starts the game with random map and the game run automatically with fps = 5. 
                (3) python Game.py --map input --automatic 0
                OR  python Game.py -m input -a 0
                    - starts the game with custom map, the game run steps by steps and display descriptions.
    """
    parser = OptionParser(usageStr)

    parser.add_option(
        "-g",
        "--generator",
        dest="generator",
        help=(
            "Generate a map size = a, number of wumpus = b, numper of pits = c, golds = d"),
        metavar="<n=a,w=b,p=c,g=d>",
        default="n=10,w=5,p=5",
    )
    parser.add_option(
        "-m",
        "--map",
        dest="map",
        help=("the MAP_FILE from which to load the map layout"),
        metavar="FILE",
        default="",
    )
    parser.add_option(
        "-f",
        "--fps",
        dest="fps",
        type="int",
        help=("frame per second when displaying UI"),
        metavar="INT",
        default=3,
    )
    parser.add_option(
        "-a",
        "--automatic",
        dest="auto",
        type="int",
        help=("automatically run the game"),
        metavar="BOOL",
        default=1,
    )

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception("Command line input not understood: " + str(otherjunk))

    args = dict()
    if options.generator:
        generateInfo = {a.split('=')[0].upper(): int(
            a.split('=')[1]) for a in options.generator.split(',')}

        for o in generateInfo.keys():
            args[o] = generateInfo[o]

    if options.map:
        if '.txt' in options.map:
            args['filename'] = options.map
        else:
            args['filename'] = options.map + '.txt'

    args['fps'] = options.fps
    args['auto'] = options.auto

    return args
