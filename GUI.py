import pygame as pg
from Agent import Actions

WIDTH = 64
SIDE_BAR = 30
playerImgs = ['North.png', 'South.png', 'East.png', 'West.png']
animationImgs = ['shoot_North.png', 'shoot_South.png',
                 'shoot_East.png', 'shoot_West.png']


def get_img(im, size=(WIDTH, WIDTH)):
    return pg.transform.scale(pg.image.load(im), size)


class GameGUI:
    def __init__(self, rows, cols):
        pg.init()
        self.fps = 3
        self.rows = rows
        self.cols = cols
        self.graphic_width = self.rows * WIDTH
        self.graphic_height = self.cols * WIDTH + SIDE_BAR
        self.score_font = pg.font.SysFont('comicsans', 30)  # Font object
        self.desc_font = pg.font.SysFont('comicsans', 30)

        self.imgs = dict({})
        self.imgs['A'] = {
            im[:-4]: get_img('Image\\' + im) for im in playerImgs}
        self.imgs['#'] = get_img('Image\\cell.png')
        self.imgs['-'] = get_img('Image\\empty.png')
        self.imgs['B'] = get_img('Image\\breeze.png')
        self.imgs['S'] = get_img('Image\\stench.png')
        #self.imgs['BS'] = get_img('Image\\BS.png')
        self.imgs['W'] = get_img('Image\\wumpus.png')
        self.imgs['P'] = get_img('Image\\pit.png')
        self.imgs['G'] = get_img('Image\\gold.png')
        self.imgs['E'] = get_img('Image\\exit.png')
        self.imgs['Killed'] = get_img('Image\\killed.png')

        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(
            (self.graphic_width, self.graphic_height))

        #pg.key.set_repeat(1, 50)

    def checkEvent(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
        return True

    def waitForTheButton(self):
        while True:
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN):
                    return True
                elif event.type == pg.QUIT:
                    return False
        return True

    def draw(self, curState):
        self.clock.tick(self.fps)
        self.screen.fill((0, 0, 0))

        "Draw rooms"
        for i in range(self.rows):
            for j in range(self.cols):
                self.draw_room((i, j), curState)

        "Draw scores"
        text = self.score_font.render(
            'Score: ' + str(curState.score), True, (255, 255, 255))
        self.screen.blit(text, (0, self.rows * WIDTH))

        "Draw exit"
        self.screen.blit(
            self.imgs['E'], (curState.exit[1]*WIDTH, (self.cols - 1 - curState.exit[0])*WIDTH))

        "Draw agent"
        self.draw_agent(curState.agent)
        pg.display.update()

    def draw_room(self, pos: tuple, state):
        explored_set = state.explored
        i, j = pos
        world_pos = (j*WIDTH, (self.cols - 1 - i)*WIDTH)

        try:
            self.screen.blit(self.imgs['-'], world_pos)
            if (pos in state.killed_wumpus):
                self.screen.blit(self.imgs['Killed'], world_pos)
            if (explored_set[pos] != '-'):
                for c in explored_set[pos]:
                    self.screen.blit(self.imgs[c], world_pos)
        except:
            raise Exception(explored_set)

    def draw_agent(self, agent):
        i, j = agent.pos
        self.screen.blit(self.imgs['A'][agent.dir],
                         (j*WIDTH, (self.cols - 1 - i)*WIDTH))

    def open_screen(self):
        self.screen.fill((0, 0, 0))
        font = pg.font.SysFont('comicsans', 40)
        text = font.render(
            "Press any key to continue the process...", True, (255, 255, 255))
        self.screen.blit(text, (WIDTH, self.graphic_width/2))
        pg.display.update()

    def draw_description(self, description):
        "Print the goal of the actions"
        goal = description[description.find('Goal') + 5:]

        if (goal == ''):
            print("No goal")
            return

        text = self.desc_font.render(
            goal, True, (162, 213, 242))
        self.screen.blit(text, (WIDTH * 2, self.rows * WIDTH))
        pg.display.update()
