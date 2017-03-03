import pygame
import utility
import my_globals as g
import battle as b
import battle_ai as bai

class Hero (object):
	dic = {}
	
	def __init__(self, index, attr = {}, resD = {}, resS = {}, equip = {}, spr = {}):
		self.index = ""

		self.attr = attr
		if not self.attr:
			self.attr = {}
			self.attr["name"] = "???"
			self.attr["lvl"] = 1
			self.attr["exp"] = 0
			self.attr["str"] = 5
			self.attr["end"] = 5
			self.attr["wis"] = 5
			self.attr["spr"] = 5
			self.attr["agi"] = 5
			self.attr["lck"] = 5
			
		self.attr["hp"] = self.baseMaxHP
		self.attr["sp"] = self.baseMaxSP

		self.resD = resD
		if not self.resD:
			for dmgType in range(0, g.DamageType.SIZE):
				self.resD[dmgType] = 0
		self.resS = resS
		if not self.resS:
			for status in range(0, g.BattlerStatus.SIZE):
				self.resS[status] = 0
			
		self.attrMods = {}
		
		if not equip:
			self.equip = {}
			self.equip["wpn"] = None
			self.equip["arm"] = None
			self.equip["acc"] = None
		else:
			self.equip = equip

		self.spr = spr
		if not self.spr:
			self.spr['battle'] = pygame.image.load("spr/battle/hero-asa.png")
			self.spr['icon'] = pygame.image.load("spr/battle/hero-asa.png")

		Hero.dic[index] = self

	@property
	def baseMaxHP (self):
		return min(self.attr["end"] * 2 + self.attr["lvl"], g.HERO_MAX_HP)
	@property	
	def baseMaxSP (self):
		return min(self.attr["wis"] + self.attr["spr"] + self.attr["lvl"], g.HERO_MAX_SP)
	@property
	def baseHit(self):
		return min(90 + self.attr["agi"] - self.attr["str"], g.HERO_MAX_RATE)
	@property
	def baseEva(self):
		return min(1 + self.attr["agi"] - self.attr["end"], g.HERO_MAX_RATE)
	@property
	def baseAtk(self):
		return min(self.attr["str"] + self.attr["lvl"], g.HERO_MAX_STAT)
	@property
	def baseDef(self):
		return min(self.attr["end"] + self.attr["lvl"], g.HERO_MAX_STAT)
	@property
	def baseMAtk(self):
		return min(self.attr["wis"] + self.attr["lvl"], g.HERO_MAX_STAT)
	@property
	def baseMDef(self):
		return min(self.attr["spr"] + self.attr["lvl"], g.HERO_MAX_STAT)
	
def InvItem (object):
	dic = {}

class Monster (object):
	dic = {}

	def __init__(self, index, attr = {}, resD = {}, resS = {}, spr = {}):
		self.ai = bai.dic[index]

		self.attr = attr
		if not self.attr:
			self.attr = {}
			self.attr["name"] = "???"
			self.attr["lvl"] = 1
			self.attr["hp"] = 10
			self.attr["sp"] = 10
			self.attr["atk"] = 6
			self.attr["def"] = 6
			self.attr["matk"] = 6
			self.attr["mdef"] = 6
			self.attr["hit"] = 95
			self.attr["eva"] = 3
			self.attr["agi"] = 5
			self.attr["lck"] = 3

		self.resD = resD
		if not self.resD:
			for dmgType in range(0, g.DamageType.SIZE):
				self.resD[dmgType] = 0
		self.resS = resS
		if not self.resS:
			for status in range(0, g.BattlerStatus.SIZE):
				self.resS[status] = 0
		
		self.spr = spr
		if not self.spr:
			self.spr = {}
			self.spr['battle'] = pygame.image.load("spr/battle/mon-slime.png")
			self.spr['icon'] = pygame.image.load("spr/battle/mon-slime.png") 

		Monster.dic[index] = self

def create_data():
	##########
	##HEROES##
	##########
	equip = {}
	equip["wpn"] = None
	equip["arm"] = None
	equip["acc"] = None

	attr = {}
	attr["name"] = "Asa"
	attr["lvl"] = 1
	attr["exp"] = 0
	attr["str"] = 6
	attr["end"] = 5
	attr["wis"] = 6
	attr["spr"] = 4
	attr["agi"] = 7
	attr["lck"] = 4

	resD = {}
	resS = {}

	spr = {}
	spr['battle'] = pygame.image.load("spr/battle/hero-asa.png")
	spr['icon'] = pygame.image.load("spr/battle/hero-asa.png")

	Hero(attr["name"], attr, resD, resS, equip, spr)

	attr = {}
	attr["name"] = "Elle"
	attr["lvl"] = 1
	attr["exp"] = 0
	attr["str"] = 3
	attr["end"] = 3
	attr["wis"] = 7
	attr["spr"] = 7
	attr["agi"] = 6
	attr["lck"] = 4

	resD = {}
	resS = {}

	spr = {}
	spr['battle'] = pygame.image.load("spr/battle/hero-elle.png")
	spr['icon'] = pygame.image.load("spr/battle/hero-elle.png")

	Hero(attr["name"], attr, resD, resS, equip, spr)

	attr = {}
	attr["name"] = "Lux"
	attr["lvl"] = 1
	attr["exp"] = 0
	attr["str"] = 7
	attr["end"] = 6
	attr["wis"] = 4
	attr["spr"] = 5
	attr["agi"] = 3
	attr["lck"] = 6

	resD = {}
	resS = {}

	spr = {}
	spr['battle'] = pygame.image.load("spr/battle/hero-lux.png")
	spr['icon'] = pygame.image.load("spr/battle/hero-lux.png")

	Hero(attr["name"], attr, resD, resS, equip, spr)

	############
	##MONSTERS##
	############
	attr = {}
	attr["name"] = "Slime"
	attr["lvl"] = 1
	attr["hp"] = 6
	attr["sp"] = 3
	attr["atk"] = 5
	attr["def"] = 5
	attr["matk"] = 5
	attr["mdef"] = 5
	attr["hit"] = 95
	attr["eva"] = 3
	attr["agi"] = 5
	attr["lck"] = 3

	resD = {}
	resS = {}

	spr = {}
	spr['battle'] = pygame.image.load("spr/battle/mon-slime.png")
	spr['icon'] = pygame.image.load("spr/battle/mon-slime.png")

	Monster(attr["name"], attr, resD, resS, spr)

	attr = {}
	attr["name"] = "Mold"
	attr["lvl"] = 2
	attr["hp"] = 12
	attr["sp"] = 5
	attr["atk"] = 6
	attr["def"] = 6
	attr["matk"] = 2
	attr["mdef"] = 2
	attr["hit"] = 95
	attr["eva"] = 5
	attr["agi"] = 7
	attr["lck"] = 5

	resD = {}
	resS = {}

	spr = {}
	spr['battle'] = pygame.image.load("spr/battle/mon-mold.png")
	spr['icon'] = pygame.image.load("spr/battle/mon-mold.png")
	Monster(attr["name"], attr, resD, resS, spr)

create_data()
