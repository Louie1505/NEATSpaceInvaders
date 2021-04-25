from game import Game
from argparse import ArgumentParser
import pygame

parser = ArgumentParser()
parser.add_argument("-a", "--ai", help="Run in AI mode, defaults to false.", action='store_true')
parser.add_argument("-p", "--players", default=10, help="Player count per generation in AI mode, defaults to 10.")

args = parser.parse_args()

pygame.init()

# Doesn't work in Gnome :'(
icon = pygame.image.load("player.png")
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((1000, 800))
clock = pygame.time.Clock()
font = pygame.font.SysFont(pygame.font.get_default_font(), 30)
pygame.display.set_caption("Space Invaders")
# Enemies firing and player reload
pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
# Bonus ship
pygame.time.set_timer(pygame.USEREVENT + 2, 10000)

enemyImg = pygame.image.load("enemy.png")
enemyImg2 = pygame.image.load("enemy2.png")
enemyBonusImg = pygame.image.load("bonus.png")
greenBoltImg = pygame.transform.scale(pygame.image.load("boltgreen.png"), (12, 48))
redBoltImg =  pygame.transform.scale(pygame.image.load("boltred.png"), (12, 48))
playerImg = pygame.transform.scale(pygame.image.load("player.png"), (50, 50))

FPS = 60
QUIT = False
DEBUG = False
DIFF = 0.0
GAMES = list()
GENOMES = list()
GEN = 0

# Setup to train players
if args.ai:
    for i in range(int(args.players) + 1):
        GAMES.append(Game(FPS, font, screen, clock, enemyImg, enemyImg2, enemyBonusImg, greenBoltImg, redBoltImg, playerImg))
# Setup to play
else:
    game = Game(FPS, font, screen, clock, enemyImg, enemyImg2, enemyBonusImg, greenBoltImg, redBoltImg, playerImg)
    game.registerControls()
    GAMES.append(game)

while not QUIT:
    screen.fill((0, 0, 0))
    events = pygame.event.get()

    if DEBUG:
        # Do it this mong way so I can guarantee just one frame runs, not x frames per repeat rate of key
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    DEBUG = not DEBUG
                    continue
                if event.key == pygame.K_n:
                    STEP = True
        if not STEP:
            DIFF = clock.tick(FPS)
            continue

    for event in events:
        QUIT = (event.type == pygame.QUIT)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            DEBUG = not DEBUG
    for g in GAMES:
        g.gameLoop(events, DIFF)
        if g.DEAD:
            genome = g.produceGenome()
            if not genome in GENOMES:
                GENOMES.append(g.produceGenome())
            if len(GENOMES) == len(GAMES):
                # Go Evaluate
                GEN += 1
                break

    pygame.display.update()
    DIFF = clock.tick(FPS)
    STEP = False
