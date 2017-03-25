import pygame
import pygame.locals

pygame.init()

#######################
### START CONSTANTS ###
#######################
CAPTION = "RPG Engine"

TILE_SIZE = 16

CURSOR_DELAY = 200
CONFIRM_DELAY = 200
INPUT_DELAY = 100
AI_DELAY = 500

BATTLE_POPUP_LIFE = 350
BATTLE_MESSAGE_LIFE = 1000

VIEW_WIDTH = TILE_SIZE * 10 #160px
VIEW_HEIGHT = TILE_SIZE * 9 #144px
VIEW_SCALE = 4
WIN_WIDTH = VIEW_WIDTH * VIEW_SCALE
WIN_HEIGHT = VIEW_HEIGHT * VIEW_SCALE

BLACK = (0,0,0)
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREEN_BLUE = (0, 180, 120)

HERO_MAX_HP = 9999
HERO_MAX_SP = 999
HERO_MAX_LVL = 99
HERO_MAX_EXP = 999999999
HERO_MAX_ATTR = 255
HERO_MAX_STAT = 999
HERO_MAX_RATE = 100
HERO_MAX_DAMAGE = 999

INVENTORY_MAX_SLOTS = 99
METER_MAX = 5

MOON_COUNTER_MAX = 50

ANIMAGI_MAX_SLOTS = 50
ANIMAGUS_MAX_LEVEL = 4

FONT_SML = pygame.font.Font('font/percy.ttf', 8)
FONT_MED = pygame.font.Font('font/pixel8.ttf', 8)
FONT_MED_BOLD = pygame.font.Font('font/pixel8b.ttf', 8)
FONT_MED_MONO = pygame.font.Font('font/pixelm8.ttf', 8)
FONT_LRG = pygame.font.Font('font/pixel.ttf', 16)
FONT_LRG_BOLD = pygame.font.Font('font/pixelb.ttf', 16)

INVENTORY_SORT_KEYS = []
INVENTORY_SORT_KEYS.append("field")
INVENTORY_SORT_KEYS.append("battle")
INVENTORY_SORT_KEYS.append("recovery")
INVENTORY_SORT_KEYS.append("damage")


### ENUMS
ATTR_NAME = {}
ATTR_NAME["maxHP"] = "M.HP"
ATTR_NAME["maxSP"] = "M.SP"
ATTR_NAME["str"] = "Str"
ATTR_NAME["end"] = "End"
ATTR_NAME["wis"] = "Wis"
ATTR_NAME["spr"] = "Spr"
ATTR_NAME["agi"] = "Agi"
ATTR_NAME["lck"] = "Lck"
ATTR_NAME["atk"] = "Atk"
ATTR_NAME["def"] = "Def"
ATTR_NAME["matk"] = "MAtk"
ATTR_NAME["mdef"] = "MDef"
ATTR_NAME["hit"] = "Hit%"
ATTR_NAME["eva"] = "Eva%"

class LogLevel():
    SYSTEM = 0
    DEBUG = 1
    ERROR = 2
    FEEDBACK = 3

    SIZE = 4


class GameState():
    INIT = 0
    MAP = 1
    MENU = 2
    BATTLE = 3

    SIZE = 4


class BattlerStatus():
    DEFEND = 0
    POISON = 1
    SLEEP = 2
    SILENCE = 3
    STUN = 4
    PARALYZE = 5
    DEATH = 6
    WOLF = 7

    SIZE = 8

    NAME = {}
    NAME[DEFEND] = "DEF"
    NAME[POISON] = "PSN"
    NAME[SLEEP] = "SLP"
    NAME[SILENCE] = "SIL"
    NAME[STUN] = "STN"
    NAME[PARALYZE] = "PLZ"
    NAME[DEATH] = "DTH"
    NAME[WOLF] = "WLF"


class ItemType():
    NONE = 0
    CONSUMABLE = 1
    ACC = 2
    SWORD = 3
    BELL = 4
    GLOVE = 5

    SIZE = 6


class SkillType():
    NONE = 0
    BLOOD = 1
    MUSIC = 2
    MOON = 3
    ENEMY = 4

    SIZE = 5

    NAME = {}
    NAME[NONE] = "Null"
    NAME[BLOOD] = "Blood"
    NAME[MUSIC] = "Music"
    NAME[MOON] = "Moon"
    NAME[ENEMY] = "Enemy"

class DamageType():
    NONE = 0
    PHYS = 1
    FIRE = 2
    COLD = 3
    ELEC = 4
    WIND = 5
    LIGHT = 6
    DARK = 7
    CURSE = 8
    POISON = 9
    EARTH = 10

    SIZE = 11

    NAME = {}
    NAME[NONE] = "NULL"
    NAME[PHYS] = "PHYS"
    NAME[FIRE] = "FIRE"
    NAME[COLD] = "COLD"
    NAME[ELEC] = "ELEC"
    NAME[WIND] = "WIND"
    NAME[EARTH] = "EARTH"
    NAME[LIGHT] = "LIGHT"
    NAME[DARK] = "DARK"
    NAME[POISON] = "POISON"
    NAME[CURSE] = "CURSE"

class BattleState():
    FIGHT = 0
    WIN = 1
    LOSE = 2
    TARGET = 3
    COMMAND = 4
    AI = 5
    ITEM = 6
    SKILL = 7
    ESCAPE = 8
    EXIT = 9

    SIZE = 10


class MenuState():
    MENU = 0
    ITEM = 1
    SKILL = 2
    STATUS = 3
    CONFIG = 4
    EXIT = 5
    TARGET_ITEM = 6
    TARGET_SKILL = 7
    ITEM_OPTIONS = 8
    ITEM_ORGANIZE = 9
    SKILL_HERO = 10
    EQUIP_HERO = 11
    EQUIP = 12
    EQUIP_WEAPON = 13
    EQUIP_ACC = 14
    ANIMAGI = 16
    ANIMAGI_CONFIRM = 17
    ANIMAGI_HERO = 18
    STATUS_HERO = 19

    SIZE = 20


class Initiative():
    NONE = 0
    PARTY = 1
    ENEMY = 2

    SIZE = 3


class Dir():
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    UP = (0, -1)

#####################
### END CONSTANTS ###
#####################


class IconCache():

    def __init__(self):
        self.dic = {}

    def icon(self, icon):
        icon = icon.replace("&i","").lower()
        try:
            return self.dic[icon]
        except KeyError:
            self.dic[icon] = pygame.image.load("spr/icons/" + icon + ".png")
            return self.dic[icon]

iconCache = IconCache()

cursorTimer = 0
confirmTimer = 0
inputTimer = 0
aiTimer = 0

textDelay = 1
textSkip = 1

playTimeSec = 0
playTimeMin = 0
playTimeHour = 0
playTimeSecText = "00"
playTimeMinText = "00"
playTimeHourText = "0"

keyConfirm = pygame.K_z
keyCancel = pygame.K_x
keyMenu = pygame.K_c
keyUp = pygame.K_UP
keyDown = pygame.K_DOWN
keyLeft = pygame.K_LEFT
keyRight = pygame.K_RIGHT

logFilter = {}
logFilter[LogLevel.SYSTEM] = True
logFilter[LogLevel.DEBUG] = False
logFilter[LogLevel.ERROR] = True
logFilter[LogLevel.FEEDBACK] = False

stepCounter = 0
moonStepCounter = MOON_COUNTER_MAX

INVENTORY = [] #stores tuples (item, quantity)
INVENTORY_SORT_KEY = 0
ANIMAGI = []
ANIMAGI_SORT_KEY = 0
GP = 100

partyList = []
monsterList = []

meter = {}
meter[SkillType.BLOOD] = 0
meter[SkillType.MUSIC] = [] #fills with damage types
meter[SkillType.MOON] = 0

def music_meter_add(damageType):
    meter[SkillType.MUSIC].insert(0, damageType)
    if len(meter[SkillType.MUSIC]) > METER_MAX:
        del meter[SkillType.MUSIC][METER_MAX]


