import pygame as pg

WIDTH = 64
playerImgs = ['North.png', 'South.png', 'East.png', 'West.png']


def get_img(im, size=(WIDTH, WIDTH)):
    return pg.transform.scale(pg.image.load(im), size)


class GameGUI:
    def __init__(self, rows, cols):
        pg.init()
        self.delayTime = 000
        self.rows = rows
        self.cols = cols
        self.graphic_width = self.rows * WIDTH
        self.graphic_height = self.cols * WIDTH + 25
        self.score_font = pg.font.SysFont('comicsans', 30)  # Font object

        self.imgs = dict({})
        self.imgs['A'] = {
            im[:-4]: get_img('Image\\' + im) for im in playerImgs}
        self.imgs['#'] = get_img('Image\\cell.png')
        self.imgs['-'] = get_img('Image\\empty.png')
        self.imgs['B'] = get_img('Image\\breeze.png')
        self.imgs['S'] = get_img('Image\\stench.png')
        self.imgs['BS'] = get_img('Image\\BS.png')
        self.imgs['W'] = get_img('Image\\wumpus.png')
        self.imgs['P'] = get_img('Image\\pit.png')
        self.imgs['G'] = get_img('Image\\gold.png')

        self.screen = pg.display.set_mode(
            (self.graphic_width, self.graphic_height))

    def checkEvent(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
        return True

    def draw(self, explored_set, agent, score=0):
        pg.time.delay(self.delayTime)
        self.screen.fill((0, 0, 0))
        for i in range(self.rows):
            for j in range(self.cols):
                self.draw_room((i, j), explored_set)
        self.draw_agent(agent)

        text = self.score_font.render(
            'Score: ' + str(score), True, (255, 255, 255))
        self.screen.blit(text, (0, self.cols * WIDTH))

        pg.display.update()

    def draw_room(self, pos: tuple, explored_set):
        i, j = pos
        world_pos = (j*WIDTH, (self.cols - 1 - i)*WIDTH)
        try:
            self.screen.blit(self.imgs[explored_set[pos]], world_pos)
        except:
            raise Exception(explored_set)

    def draw_agent(self, agent):
        i, j = agent.pos
        self.screen.blit(self.imgs['A'][agent.dir],
                         (j*WIDTH, (self.cols - 1 - i)*WIDTH))
