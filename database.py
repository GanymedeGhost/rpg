import pygame

import math

import utility
import my_globals as g
import battle as b
import battle_ai as bai
import battle_command as cmd
import field_command as fcmd

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
		return min(50 + self.attr["end"] * math.ceil(self.attr["lvl"] // 2), g.HERO_MAX_HP)
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
	@property
	def isDead(self):
		return self.attr['hp'] < 1


	def heal_hp(self, value):
		self.attr['hp'] +=  value
		self.check_hp()


	def check_hp(self):
		if self.attr['hp'] > self.baseMaxHP:
			self.attr['hp'] = self.baseMaxHP


	def revive(self, hpPercent):
		self.attr['hp'] = max(1, math.floor(self.baseMaxHP * hpPercent / 100))

class Monster (object):
	dic = {}

	def __init__(self, index, attr = {}, resD = {}, resS = {}, drops = [], steals = [], spr = None, size = 16, icon = None):
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
			self.attr['exp'] = 1
			self.attr['gold'] = 1

		self.resD = resD
		if not self.resD:
			for dmgType in range(0, g.DamageType.SIZE):
				self.resD[dmgType] = 0
		self.resS = resS
		if not self.resS:
			for status in range(0, g.BattlerStatus.SIZE):
				self.resS[status] = 0

		self.drops = drops
		self.steals = steals

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

	def __init__(self, index, desc, limit = 99, useAction = None, battleAction = None, sortPriority = {}):
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

		self.sortPriority = sortPriority
		if not self.sortPriority:
			self.sortPriority["field"] = 99
			self.sortPriority["battle"] = 99
			self.sortPriority["recovery"] = 99
			self.sortPriority["damage"] = 99
			
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
		if battler.attr['sp'] >= skill.spCost:
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
	sortPriority = {}
	sortPriority["field"] = 0
	sortPriority["battle"] = 0
	sortPriority["recovery"] = 0
	sortPriority["damage"] = 0

	InvItem(name, desc, limit, useAction, battleAction, sortPriority)
	
	name = "Potion"
	desc = "Restores 50 HP"
	limit = 99
	useAction = fcmd.Potion
	battleAction = cmd.Potion
	sortPriority = {}
	sortPriority["field"] = 0
	sortPriority["battle"] = 0
	sortPriority["recovery"] = 0
	sortPriority["damage"] = 99
	
	InvItem(name, desc, limit, useAction, battleAction, sortPriority)

	name = "Revive"
	desc = "Restores life to a fallen ally"
	limit = 99
	useAction = fcmd.Revive
	battleAction = cmd.Revive
	sortPriority = {}
	sortPriority["field"] = 10
	sortPriority["battle"] = 10
	sortPriority["recovery"] = 10
	sortPriority["damage"] = 99
	
	InvItem(name, desc, limit, useAction, battleAction, sortPriority)

	name = "Antidote"
	desc = "Cures poison"
	limit = 99
	useAction = None
	battleAction = cmd.Antidote
	sortPriority = {}
	sortPriority["field"] = 11
	sortPriority["battle"] = 11
	sortPriority["recovery"] = 11
	sortPriority["damage"] = 99
	
	InvItem(name, desc, limit, useAction, battleAction, sortPriority)

	################
	##BLOOD SKILLS##
	################
	name = "Sacrifice"
	desc = "Lowers Max HP to restore the party's SP"
	skillType = g.SkillType.BLOOD
	spCost = 0
	meterReq = 0
	useAction = None
	battleAction = cmd.Sacrifice

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	name = "Blood Slash"
	desc = "Deals neutral damage to an enemy"
	skillType = g.SkillType.BLOOD
	spCost = 15
	meterReq = 0
	useAction = None
	battleAction = cmd.BloodSlash

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	################
	##MUSIC SKILLS##
	################

	name = "Finale"
	desc = "Resolve the melody"
	skillType = g.SkillType.MUSIC
	spCost = 0
	meterReq = 1
	useAction = None
	battleAction = cmd.Finale

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	name = "Stacatto"
	desc = "Deals ELEC damage to an enemy"
	skillType = g.SkillType.MUSIC
	spCost = 10
	meterReq = 0
	useAction = None
	battleAction = cmd.Stacatto

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	################
	##MOON SKILLS##
	################

	name = "Transform"
	desc = "Change physical form"
	skillType = g.SkillType.MOON
	spCost = 0
	meterReq = 1
	useAction = None
	battleAction = cmd.Transform

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	name = "Double Cut"
	desc = "Attack twice"
	skillType = g.SkillType.MOON
	spCost = 12
	meterReq = 1
	useAction = None
	battleAction = cmd.DoubleCut

	Skill(name, desc, skillType, spCost, meterReq, useAction, battleAction)

	################
	##ENEMY SKILLS##
	################
	name = "Toxic"
	desc = "Small chance to inflict Poison"
	skillType = g.SkillType.ENEMY
	spCost = 10
	meterReq = 0
	useAction = None
	battleAction = cmd.Toxic

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
	attr["lvl"] = 5
	attr["exp"] = 0
	attr["str"] = 12
	attr["end"] = 13
	attr["wis"] = 9
	attr["spr"] = 7
	attr["agi"] = 13
	attr["lck"] = 9

	resD = {}
	resS = {}
	skillType = g.SkillType.BLOOD
	commands = []
	commands.append(cmd.Attack)
	commands.append(cmd.UseSkill)
	commands.append(cmd.UseItem)
	commands.append(cmd.Defend)
	commands.append(cmd.Escape)
	skills = [Skill.dic["Sacrifice"]]
	skills.append(Skill.dic["Blood Slash"])

	spr = "spr/battle/hero-luxe.png"
	size = 16
	icon = pygame.image.load("spr/battle/icon-luxe.png")

	Hero(attr["name"], attr, resD, resS, skillType, commands, skills, equip, spr, size, icon)

	attr = {}
	attr["name"] = "Elle"
	attr["lvl"] = 5
	attr["exp"] = 0
	attr["str"] = 7
	attr["end"] = 9
	attr["wis"] = 16
	attr["spr"] = 14
	attr["agi"] = 10
	attr["lck"] = 10

	resD = {}
	resS = {}
	skillType = g.SkillType.MUSIC
	commands = []
	commands.append(cmd.Attack)
	commands.append(cmd.UseSkill)
	commands.append(cmd.UseItem)
	commands.append(cmd.Defend)
	commands.append(cmd.Escape)
	skills = [Skill.dic["Finale"]]
	skills.append(Skill.dic["Stacatto"])
	

	spr = "spr/battle/hero-elle.png"
	size = 16
	icon = pygame.image.load("spr/battle/icon-elle.png")

	Hero(attr["name"], attr, resD, resS, skillType, commands, skills, equip, spr, size, icon)

	attr = {}
	attr["name"] = "Asa"
	attr["lvl"] = 5
	attr["exp"] = 0
	attr["str"] = 15
	attr["end"] = 14
	attr["wis"] = 7
	attr["spr"] = 6
	attr["agi"] = 9
	attr["lck"] = 7

	resD = {}
	resS = {}
	skillType = g.SkillType.MOON
	commands = []
	commands.append(cmd.Attack)
	commands.append(cmd.UseSkill)
	commands.append(cmd.UseItem)
	commands.append(cmd.Defend)
	commands.append(cmd.Escape)
	skills = [Skill.dic["Transform"]]
	skills.append(Skill.dic["Double Cut"])

	spr = "spr/battle/hero-asa.png"
	size = 16
	icon = pygame.image.load("spr/battle/icon-asa.png")

	Hero(attr["name"], attr, resD, resS, skillType, commands, skills, equip, spr, size, icon)

	############
	##MONSTERS##
	############
	attr = {}
	attr["name"] = "Slime"
	attr["lvl"] = 3
	attr["hp"] = 20
	attr["sp"] = 10
	attr["atk"] = 15
	attr["def"] = 12
	attr["matk"] = 15
	attr["mdef"] = 15
	attr["hit"] = 95
	attr["eva"] = 5
	attr["agi"] = 10
	attr["lck"] = 5
	attr['exp'] = 5
	attr['gold'] = 5

	drops = []
	drops.append(("Potion", 50))

	steals = []

	resD = {}
	resS = {}

	spr = "spr/battle/mon-slime.png"
	size = 16
	icon = pygame.image.load("spr/battle/mon-slime.png")

	Monster(attr["name"], attr, resD, resS, drops, steals, spr, size, icon)

	attr = {}
	attr["name"] = "Mold"
	attr["lvl"] = 5
	attr["hp"] = 35
	attr["sp"] = 20
	attr["atk"] = 20
	attr["def"] = 15
	attr["matk"] = 5
	attr["mdef"] = 5
	attr["hit"] = 95
	attr["eva"] = 5
	attr["agi"] = 13
	attr["lck"] = 5
	attr['exp'] = 7
	attr['gold'] = 6

	drops = []
	drops.append(("Antidote", 50))
	drops.append(("Revive", 10))

	steals = []

	resD = {}
	resS = {}

	spr = "spr/battle/mon-mold.png"
	size = 16
	icon = pygame.image.load("spr/battle/mon-mold.png")

	Monster(attr["name"], attr, resD, resS, drops, steals, spr, size, icon)
	
create_data()
