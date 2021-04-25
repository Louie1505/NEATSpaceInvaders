from random import randrange
import math
from enemy import Enemy
import pygame, keyengine, neat, collisionhelper

class Game:

    def __init__(self, fps, font, screen, clock, enemyImg, enemyImg2, enemyBonusImg, greenBoltImg, redBoltImg, player):
        self.FPS = fps
        self.font = font
        self.screen = screen
        self.clock = clock
        self.enemyImg  = enemyImg
        self.enemyImg2 = enemyImg2
        self.enemyBonusImg = enemyBonusImg
        self.greenBoltImg = greenBoltImg
        self.redBoltImg = redBoltImg
        self.player = player
        # keyEngine is KeyEngine, an engine for keys
        self.keyEngine = keyengine.KeyEngine()
        self.DEBUG = False
        self.DEAD = False
        self.player_rect = player.get_rect(center=(500, 750))
        self.PLAYER_SPEED = 15
        self.playerShots = list()
        self.enemyShots = list()
        self.CAN_FIRE = True
        self.START_TICKS=0
        self.SCORE = 0
        self.CANVAS_XY = (100, 20)
        self.canvas = (pygame.Surface((800, 270), pygame.SRCALPHA, 32)).convert_alpha()
        self.enemies = list()
        self.FIRE_EVENT = pygame.USEREVENT + 1
        self.BONUS_EVENT = pygame.USEREVENT + 2
        self.spawnEnemies()

    def registerControls(self):
        self.keyEngine.register(pygame.K_LEFT, lambda: self.movePlayer(self.player_rect.x - self.PLAYER_SPEED))
        self.keyEngine.register(pygame.K_a, lambda: self.movePlayer(self.player_rect.x - self.PLAYER_SPEED))

        self.keyEngine.register(pygame.K_RIGHT, lambda: self.movePlayer(self.player_rect.x + self.PLAYER_SPEED))
        self.keyEngine.register(pygame.K_d, lambda: self.movePlayer(self.player_rect.x + self.PLAYER_SPEED))

        self.keyEngine.register(pygame.K_w, lambda: self.fire())
        self.keyEngine.register(pygame.K_UP, lambda: self.fire())
        self.keyEngine.register(pygame.K_SPACE, lambda: self.fire())
        self.keyEngine.register(pygame.K_b, lambda: self.toggleDebug())

    def drawText(self):
        blit_list = []
        blit_list.append((self.font.render(f"Score: {self.SCORE}", True, (255, 255, 255)), (5,5)))
        if self.DEAD:
            blit_list.append((self.font.render("GAME OVER", True, (255, 255, 255)), (430,400)))
        if len(self.enemies) < 1:
            blit_list.append((self.font.render("YOU WIN", True, (255, 255, 255)), (440,400)))
        self.screen.blits(blit_list)

    def movePlayer(self, x):
        if self.DEAD:
            return
        if 0 <= x <= self.screen.get_width() - self.player_rect.width:
            self.player_rect.x = x

    def moveShots(self, seconds):
        if self.DEAD:
            return
        for i, s in enumerate(self.playerShots):
            sXY1 = (int(s[0] - 4), int(s[1] - 22))
            sXY2 = (int(s[0] + 4), int(s[1] + 20))
            self.playerShots[i] = (s[0], s[1] - (500.0 * seconds))
            # If we're not even on the canvas then don't waste time checking if we're hitting anything
            if collisionhelper.intersecting((sXY1, sXY2), ((self.CANVAS_XY[0], self.CANVAS_XY[1]),(self.CANVAS_XY[0] + 800, self.CANVAS_XY[1] + 270))):
                # 73n + 3 + Cx is the polynomial for the left of each image
                # Plug in our shot and solve for n thats: n = ((Sx - Cx - 3) / 73)
                # 64 is 87.67% of 73 so if fractional of n > .8767 then we're between the enemies, don't need to check
                n = (s[0] - self.CANVAS_XY[0] - 3.0) / 73.0
                if (n - math.floor(n)) <= 0.8767:
                    for e in self.enemies:
                        if collisionhelper.intersecting((sXY1, sXY2), ((e.coords[0] + self.CANVAS_XY[0], e.coords[1] + self.CANVAS_XY[1]), (e.coords[0] + self.CANVAS_XY[0] + 64, e.coords[1] + self.CANVAS_XY[1] + 55))):
                            self.enemies.remove(e)
                            self.SCORE += 100 if s[1] <= self.CANVAS_XY[1] + 75 else 50
                            # Get rid of the shot if it's hit something (In the hackiest way possible 😊)
                            self.playerShots[i] = (s[0], s[1] - 2000)
                            break

        for i, s in enumerate(self.enemyShots):
            self.enemyShots[i] = (s[0], s[1] + (500.0 * seconds))
            sXY1 = (int(s[0] - 5), int(s[1] - 25))
            sXY2 = (int(s[0] + 6), int(s[1] + 20))
            if collisionhelper.intersecting((sXY1, sXY2), ((self.player_rect.x, self.player_rect.y),(self.player_rect.x + 50, self.player_rect.y + 50))):
                self.die()

    def drawShots(self):
        blit_list = []
        for s in self.playerShots:
            if s[1] < 0:
                self.playerShots.remove(s)
                continue
            blit_list.append((self.redBoltImg, self.redBoltImg.get_rect(center=(s[0], s[1]))))
        for s in self.enemyShots:
            if s[1] > 1000:
                self.enemyShots.remove(s)
                continue
            blit_list.append((self.greenBoltImg, self.greenBoltImg.get_rect(center=(s[0], s[1]))))
        self.screen.blits(blit_list)

    def fire(self):
        if self.DEAD:
            return
        if not self.CAN_FIRE:
            return
        self.CAN_FIRE = False
        self.playerShots.append((self.player_rect.x + 25, 703))

    def die(self):
        self.DEAD = True

    def moveCanvas(self):
        if self.DEAD:
            return
        if self.CANVAS_XY[1] % 2 == 0:
            if self.CANVAS_XY[0] >= 200:
                self.CANVAS_XY = (self.CANVAS_XY[0] + 1, self.CANVAS_XY[1] + 15)
            else:
                self.CANVAS_XY = (self.CANVAS_XY[0] + 1, self.CANVAS_XY[1])
        else:
            if self.CANVAS_XY[0] <= 0:
                self.CANVAS_XY = (self.CANVAS_XY[0] - 1, self.CANVAS_XY[1] + 15)
            else:
                self.CANVAS_XY = (self.CANVAS_XY[0] - 1, self.CANVAS_XY[1])

    def spawnEnemies(self):
        x = 3
        y = 0
        for e in range(44):
            self.enemies.append(Enemy(self.enemyImg2 if e < 11 else self.enemyImg, (x, y)))
            x += 73
            if x >= 800:
                y += 70
                x = 3

    def drawEnemies(self):
        self.canvas = (pygame.Surface((800, 270), pygame.SRCALPHA, 32)).convert_alpha()
        for e in self.enemies:
            self.canvas.blit(e.img, e.coords)

    def enemyRandomShoot(self):
        if len(self.enemies) > 0:
            for _ in range (randrange(5)):
                x = randrange(len(self.enemies))
                self.enemyShots.append(((self.CANVAS_XY[0] + self.enemies[x].coords[0] + 32),(self.CANVAS_XY[1] + self.enemies[x].coords[1] + 64)))

    def bonusEnemy(self):
        return

    def toggleDebug(self):
        self.DEBUG = not self.DEBUG
        if self.DEBUG:
            self.keyEngine.currEvents = list()

    def gameLoop(self, events, diff):
        for event in events:
            self.keyEngine.handleEvents(event)
            if event.type == self.FIRE_EVENT and not self.DEAD:
                self.enemyRandomShoot()
                self.CAN_FIRE = True
            if event.type == self.BONUS_EVENT and not self.DEAD:
                self.bonusEnemy()
        self.keyEngine.run()
        self.screen.blit(self.player, self.player_rect)
        self.moveCanvas()
        self.drawEnemies()
        self.screen.blit(self.canvas, self.CANVAS_XY)
        self.drawText()
        self.moveShots(diff / 1000.0)
        self.drawShots()

    def produceGenome(self):
        return None