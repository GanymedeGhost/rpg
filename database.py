import pygame

import utility
import my_globals as g
import battle as b
import battle_ai as bai
import battle_command as cmd

class Hero (object):
	dic = {}
	
	def __init__(self, index, attr = {}, resD = {}, resS = {}, skillType = None, commands = [], skills = [], equip = {}, spr = None, size = 32, icon = None):
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

		self.skillType = skillType
		self.commands = commands
		self.skills = skills
		
		self.attrMods = {}
		
		if not equip:
			self.equip = {}
			self.equip["wpn"] = None
			self.equip["arm"] = None
			self.equip["acc"] = None
		else:
			self.equip = equip

		self.size = size
		self.spr = spr
		if not self.spr:
			self.spr = "spr/battle/hero-asa.png"

		self.icon = icon
		if not self.icon:
			self.icon = pygame.image.load("spr/battle/hero-asa.png")

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

class Monster (object):
	dic = {}

	def __init__(self, index, attr = {}, resD = {}, resS = {}, spr = None, size = 16, icon = None):
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

		self.size = size
		self.spr = spr
		if not self.spr:
			self.spr = "spr/battle/mon-slime.png"

		self.icon = icon
		if not self.icon:
			self.icon = pygame.image.load("spr/battle/mon-slime.png")

		Monster.dic[index] = self

class InvItem (object):
	dic = {}

	def __init__(self, index, desc, limit = 99, useAction = None, battleAction = None):
		self.name = index
		self.desc = desc
		self.limit = limit
		
		self.useAction = useAction
		if useAction != None:
			self.usableField = True
		else:
			self.usableField = False
			
		self.battleAction = battleAction
		if battleAction != None:
			self.usableBattle = True
		else:
			self.usableBattle = False
			
		InvItem.dic[index] = self

class Skill (object):
	dic = {}

	def __init__(self, index, desc, skillType, spCost, meterReq, useAction, battleAction):
		self.name = index
		self.desc = desc
		self.skillType = skillType
		self.spCost = spCost
		self.meterReq = meterReq
		self.useAction = useAction
		if (useAction != None):
			self.usableField = True
		else:
			self.usableField = False
		self.battleAction = battleAction
		if (battleAction != None):
			self.usableBattle = True
		else:
			self.usableBattle = False

		Skill.dic[index] = self

	def check_cost(battler, skill):
		if battler.SP >= skill.spCost:
			if skill.skillType != g.SkillType.MUSIC:
				if g.METER[skill.skillType] >= skill.meterReq:
					return True
			else:
				if len(g.METER[skill.skillType]) >= skill.meterReq:
					return True
		return False

def create_data():
	#########
	##ITEMS##
	#########
	name = ""
	desc = ""
	limit = 1
	useAction = None
	battleAction = None

	InvItem(name, desc, limit, useAction, battleAction)
	
	name = "Potion"
	desc = "Restores 50 HP"
	limit = 99
	useAction = None
	battleAction = cmd.Potion
	
	InvItem(name, desc, limit, useAction, battleAction)

	name = "Revive"
	desc = "Restores life"
	limit = 99
	useAction = None
	battleAction = cmd.Revive
	
	InvItem(name, desc, limit, useAction, battleAction)

	name = "Antidote"
	desc = "Cures poison"
	limit = 99
	useAction = None
	battleAction = cmd.Antidote
	
	InvItem(name, desc, limit, useAction, battleAction)

	##########
	##SKILLS##
	##########
	name = "Sacrifice"
	desc = "Lowers Max HP to restore the party's SP"
	skillType = g.SkillType.BLOOD
	spCost = 0
	meterReq = 0
	useAction = None
	battleAction = cmd.Sacrifice

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	name = "Blood Slash"
	desc = "Deals heavy neutral damage to an enemy"
	skillType = g.SkillType.BLOOD
	spCost = 5
	meterReq = 1
	useAction = None
	battleAction = cmd.BloodSlash

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)
	name = "Blood Slash2"
	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)
	name = "Blood Slash3"
	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)
	name = "Blood Slash4"
	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)
	name = "Blood Slash5"
	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	
	##########
	##HEROES##
	##########
	equip = {}
	equip["wpn"] = None
	equip["arm"] = None
	equip["acc"] = None

	attr = {}
	attr["name"] = "Luxe"
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
	skillType = g.SkillType.BLOOD
	commands = []
	commands.append(cmd.Attack)
	commands.append(cmd.UseSkill)
	commands.append(cmd.UseItem)
	commands.append(cmd.Defend)
	skills = [Skill.dic["Sacrifice"]]
	skills.append(Skill.dic["Blood Slash"])
	skills.append(Skill.dic["Blood Slash2"])
	skills.append(Skill.dic["Blood Slash3"])
	skills.append(Skill.dic["Blood Slash4"])
	skills.append(Skill.dic["Blood Slash5"])

	spr = "spr/battle/hero-Luxe.png"
	size = 16
	icon = pygame.image.load("spr/battle/icon-Luxe.png")

	Hero(attr["name"], attr, resD, resS, skillType, commands, skills, equip, spr, size, icon)

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
	skillType = g.SkillType.MUSIC
	commands = []
	commands.append(cmd.Attack)
	commands.append(cmd.UseSkill)
	commands.append(cmd.UseItem)
	commands.append(cmd.Defend)
	skills = [Skill.dic["Blood Slash"]]
	

	spr = "spr/battle/hero-elle.png"
	size = 16
	icon = pygame.image.load("spr/battle/icon-elle.png")

	Hero(attr["name"], attr, resD, resS, skillType, commands, skills, equip, spr, size, icon)

	attr = {}
	attr["name"] = "Asa"
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
	skillType = g.SkillType.MOON
	commands = []
	commands.append(cmd.Attack)
	commands.append(cmd.UseSkill)
	commands.append(cmd.UseItem)
	commands.append(cmd.Defend)
	skills = [Skill.dic["Blood Slash"]]

	spr = "spr/battle/hero-asa.png"
	size = 16
	icon = pygame.image.load("spr/battle/icon-asa.png")

	Hero(attr["name"], attr, resD, resS, skillType, commands, skills, equip, spr, size, icon)

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

	spr = "spr/battle/mon-slime.png"
	size = 16
	icon = pygame.image.load("spr/battle/mon-slime.png")

	Monster(attr["name"], attr, resD, resS, spr, size, icon)

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

	spr = "spr/battle/mon-mold.png"
	size = 16
	icon = pygame.image.load("spr/battle/mon-mold.png")
	
	Monster(attr["name"], attr, resD, resS, spr, size, icon)
	
create_data()
