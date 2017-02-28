import my_globals as g
import battle as b

class Hero (object):
	dic = {}
	
	def __init__(self, index, attr = {}, equip = {}):
		self.index = ""
		
		if not attr:
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
		else:
			self.attr = attr
		self.attr["hp"] = self.baseMaxHP
		self.attr["sp"] = self.baseMaxSP
			
		self.attrMods = {}
		
		if not equip:
			self.equip = {}
			self.equip["wpn"] = None
			self.equip["arm"] = None
			self.equip["acc"] = None
		else:
			self.equip = equip
		
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

        def __init__(self, index, attr = {}):
                if not attr:
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
                else:
                        self.attr = attr

                Monster.dic[index] = self
	
##########
##HEROES##
##########
attr = {}
attr["name"] = "Asa"
attr["lvl"] = 1
attr["exp"] = 0
attr["str"] = 6
attr["end"] = 5
attr["wis"] = 6
attr["spr"] = 4
attr["agi"] = 6
attr["lck"] = 4
Hero(attr["name"], attr)

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
Hero(attr["name"], attr)

attr = {}
attr["name"] = "Lux"
attr["lvl"] = 1
attr["exp"] = 0
attr["str"] = 7
attr["end"] = 6
attr["wis"] = 4
attr["spr"] = 5
attr["agi"] = 3
attr["lck"] = 5
Hero(attr["name"], attr)

############
##MONSTERS##
############
attr = {}
attr["name"] = "Slime"
attr["lvl"] = 1
attr["hp"] = 10
attr["sp"] = 10
attr["atk"] = 6
attr["def"] = 6
attr["matk"] = 6
attr["mdef"] = 6
attr["hit"] = 95
attr["eva"] = 3
attr["agi"] = 5
attr["lck"] = 3
Monster(attr["name"], attr)

attr = {}
attr["name"] = "Bear"
attr["lvl"] = 2
attr["hp"] = 15
attr["sp"] = 2
attr["atk"] = 10
attr["def"] = 7
attr["matk"] = 2
attr["mdef"] = 2
attr["hit"] = 70
attr["eva"] = 1
attr["agi"] = 2
attr["lck"] = 1
Monster(attr["name"], attr)
