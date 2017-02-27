import pygame
import pygame.locals

###START CONSTANTS
CAPTION = "RPG Engine"

TILE_SIZE = 16

CURSOR_DELAY = 20
CURSOR_TIMER = 0
CONFIRM_DELAY = 20
CONFIRM_TIMER = 0

VIEW_WIDTH = TILE_SIZE * 10 #160px
VIEW_HEIGHT = TILE_SIZE * 9 #144px
VIEW_SCALE = 4
WIN_WIDTH = VIEW_WIDTH * VIEW_SCALE
WIN_HEIGHT = VIEW_HEIGHT * VIEW_SCALE

BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class GameState():
    INIT = 0
    MAP = 1
    MENU = 2
    BATTLE = 3

###END CONSTANTS

KEY_CONFIRM = pygame.K_z
KEY_CANCEL = pygame.K_x
KEY_MENU = pygame.K_c
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
