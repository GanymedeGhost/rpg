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

ANIMARIUM_MAX_SLOTS = 50
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

    SIZE = 19


class Initiative():
    NONE = 0
    PARTY = 1
    ENEMY = 2

    SIZE = 3

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
            self.dic[icon] = pygame.image.load("spr/icon/" + icon + ".png")
            return self.dic[icon]

ICON_CACHE = IconCache()

CURSOR_TIMER = 0
CONFIRM_TIMER = 0
INPUT_TIMER = 0
AI_TIMER = 0

PLAY_SEC = 0
PLAY_MIN = 0
PLAY_HR = 0
PLAY_SEC_STR = "00"
PLAY_MIN_STR = "00"
PLAY_HR_STR = "0"

KEY_CONFIRM = pygame.K_z
KEY_CANCEL = pygame.K_x
KEY_MENU = pygame.K_c
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT

LOG_FILTER = {}
LOG_FILTER[LogLevel.SYSTEM] = True
LOG_FILTER[LogLevel.DEBUG] = False
LOG_FILTER[LogLevel.ERROR] = True
LOG_FILTER[LogLevel.FEEDBACK] = False

STEP_COUNTER = 0

MOON_COUNTER = MOON_COUNTER_MAX

PARTY_LIST = []
MONSTER_LIST = []
INVENTORY = [] #stores tuples (item, quantity)
INVENTORY_SORT_KEY = 0
ANIMAGI = []
ANIMAGI_SORT_KEY = 0
GP = 100

METER = {}
METER[SkillType.BLOOD] = 0
METER[SkillType.MUSIC] = [] #fills with damage types
METER[SkillType.MOON] = 0

def music_meter_add(damageType):
    METER[SkillType.MUSIC].insert(0, damageType)
    if len(METER[SkillType.MUSIC]) > METER_MAX:
        del METER[SkillType.MUSIC][METER_MAX]


