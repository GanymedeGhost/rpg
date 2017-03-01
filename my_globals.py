import pygame
import pygame.locals

pygame.init()

###START CONSTANTS
CAPTION = "RPG Engine"

TILE_SIZE = 16

CURSOR_DELAY = 200
CONFIRM_DELAY = 200
INPUT_DELAY = 100
AI_DELAY = 700

BATTLE_POPUP_LIFE = 500

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
GREEN_BLUE = (0, 180, 120)

HERO_MAX_HP = 999
HERO_MAX_SP = 999
HERO_MAX_LVL = 99
HERO_MAX_EXP = 999999999
HERO_MAX_ATTR = 255
HERO_MAX_STAT = 999
HERO_MAX_RATE = 100
HERO_MAX_DAMAGE = 999

FONT_SML = pygame.font.Font('font/percy.ttf', 8)
FONT_MED = pygame.font.Font('font/pixel8.ttf', 8)
FONT_MED_BOLD = pygame.font.Font('font/pixel8b.ttf', 8)
FONT_LRG = pygame.font.Font('font/pixel.ttf', 16)
FONT_LRG_BOLD = pygame.font.Font('font/pixelb.ttf', 16)


class GameState():
    INIT = 0
    MAP = 1
    MENU = 2
    BATTLE = 3

###END CONSTANTS

CURSOR_TIMER = 0
CONFIRM_TIMER = 0
INPUT_TIMER = 0
AI_TIMER = 0

KEY_CONFIRM = pygame.K_z
KEY_CANCEL = pygame.K_x
KEY_MENU = pygame.K_c
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT

PARTY_LIST = []
MONSTER_LIST = []
