class Directions:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"

    LEFT = {NORTH: WEST, SOUTH: EAST, EAST: NORTH, WEST: SOUTH}

    RIGHT = dict([(y, x) for x, y in LEFT.items()])

    REVERSE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}


class Actions:
    """
    A collection of static methods for manipulating move actions.
    """

    # Directions for moving
    _directions = {
        Directions.NORTH: (1, 0),
        Directions.SOUTH: (-1, 0),
        Directions.EAST: (0, 1),
        Directions.WEST: (0, -1)
    }

    SHOOT = {
        "Shoot North": (1, 0),
        "Shoot South": (-1, 0),
        "Shoot East": (0, 1),
        "Shoot West": (0, -1)
    }

    PICK_GOLD = 2
    EXIT = 3

    _directionsAsList = _directions.items()

    TOLERANCE = 0.001

    def shoot(Direction):
        return "Shoot " + Direction
    shoot = staticmethod(shoot)

    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action

    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST

    vectorToDirection = staticmethod(vectorToDirection)

    def getPossibleActions(pos, n):
        possible = []
        x, y = pos

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y + dy
            next_x = x + dx
            if next_x >= 0 and next_x < n and next_x >= 0 and next_y < n:
                possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def directionToVector(direction, speed=1.0):
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)
    directionToVector = staticmethod(directionToVector)

    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)

    getSuccessor = staticmethod(getSuccessor)


class Agent:
    def __init__(self, pos):
        self.pos = pos
        self.actions = ['North', 'North', Actions.PICK_GOLD,
                        'North', 'North', 'East', 'North', 'West']
        #self.actions = []
        self.dir = Directions.EAST
        self.gold = 0
        self.wumpus_killed = 0
        self.iLeaving = False

    def get_action(self, gamestate):
        return self.actions.pop(0)

    def move(self, direction):
        self.dir = direction
        self.actions.append(direction)
        self.pos = Actions.getSuccessor(self.pos, direction)

    def __repr__(self):
        return ("Current Pos : " + str(self.pos) + " , " +
                "Current Direction : " + str(self.dir))
