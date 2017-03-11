import math
import random
import my_globals as g
import database as db
import event
import inventory
import utility

def get_target(user, cmdClass, opposite = True, same = False, alive = True, dead = False):

    validTargets = []
    selectedTargets = []
    index = 0
    for target in user.BC.battlers:
        if (opposite and user.isHero != target.isHero) or (same and user.isHero == target.isHero):
            if alive and not target.isDead or dead and target.isDead:
                validTargets.append(target)
        index += 1

    user.BC.UI.get_target(user, validTargets)
    user.BC.queuedAction = cmdClass.queue

def get_target_auto(user, cmdClass, mostAggro = True, opposite = True, same = False, alive = True, dead = False):
    if mostAggro:
        bestAggro = -1
    else:
        bestAggro = 101
    bestTarget = None
    for target in user.BC.battlers:
        if (opposite and user.isHero != target.isHero) or (same and user.isHero == target.isHero):
            if alive and not target.isDead or dead and target.isDead:
                if mostAggro:
                    if target.aggro > bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                else:
                    if target.aggro < bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
    if bestTarget == None:
        bestTarget = user

    cmdClass.queue(user, bestTarget)

##################
##BASIC COMMANDS##
##################

class UseItem():

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def name():
        return "Items"

    def start(user):
        UseItem.get_item(user)

    def get_item(user):
        user.BC.UI.get_item(user)
        user.BC.queuedAction = UseItem.queue

    def queue(user, action):
        user.BC.eventQueue.queue(action)

class UseSkill():
    def __init__(self, user, action):
        self.user = user
        self.action = action

    def name():
        return "Skills"

    def start(user):
        UseSkill.get_skill(user)

    def get_skill(user):
        user.BC.UI.get_skill(user)
        user.BC.queuedAction = UseSkill.queue

    def queue(user, action):
        user.BC.eventQueue.queue(action)

class Attack():

    def __init__(self, user, target):
        self.user = user
        self.target = target
    
    def name():
        return "Attack"

    def start(user):
        if (user.isHero):
            get_target(user, Attack)
        else:
            get_target_auto(user, Attack)

    def queue(user, target):
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Attack(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))
    
    def run(self):
        utility.log(self.user.attr['name'] + " attacks " + self.target.attr['name'])
        if self.user.BC.hit_calc(self.user, self.target):
            if not self.user.BC.dodge_calc(self.user, self.target):
                dmg = self.user.BC.phys_dmg_calc(self.user, self.target)
                if self.user.BC.crit_calc(self.user, self.target):
                    dmg*=2
                    self.target.stun()
                dmg -= self.user.BC.phys_def_calc(self.user, self.target)
                if (dmg < 0):
                    dmg = 0
                self.user.aggro_up()
                self.target.take_damage(dmg, g.DamageType.PHYS)

        self.user.after_turn()
        return -1

class Defend():

    def __init__(self, user):
        self.user = user

    def name():
        return "Defend"

    def start(user):
        Defend.queue(user)

    def queue(user):
        user.BC.UI.create_message(Defend.name())
        user.BC.eventQueue.queue(Defend(user))

    def run(self):
        utility.log(self.user.attr['name'] + " is defending.", g.LogLevel.FEEDBACK)
        self.user.mods[g.BattlerStatus.DEFEND] += 1
        self.user.reset_anim()
        self.user.after_turn()
        return -1

#################
##ITEM COMMANDS##
#################

class Potion():

    def __init__(self, user, target):
        self.user = user
        self.target = target
    
    def name():
        return "Potion"

    def start(user):
        if (user.isHero):
            get_target(user, Potion, False, True)
        else:
            get_target_auto(user, Potion, True, False, True)

    def queue(user, target):
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Potion(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))
    
    def run(self):
        if self.user.isHero:
            inventory.remove_item("Potion")
        utility.log(self.user.attr['name'] + " Potions " + self.target.attr['name'])
        self.target.heal_hp(50)
        self.user.after_turn()
        return -1

class Revive():

    def __init__(self, user, target):
        self.user = user
        self.target = target
    
    def name():
        return "Revive"

    def start(user):
        if (user.isHero):
            get_target(user, Revive, False, True, False, True)
        else:
            get_target_auto(user, Revive, True, False, True, False, True)

    def queue(user, target):
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Revive(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))
    
    def run(self):
        if self.user.isHero:
            inventory.remove_item("Revive")

        utility.log(self.user.attr['name'] + " Revives " + self.target.attr['name'])
        self.target.revive(33)
        self.user.after_turn()
        return -1

class Antidote():

    def __init__(self, user, target):
        self.user = user
        self.target = target
    
    def name():
        return "Antidote"

    def start(user):
        if (user.isHero):
            get_target(user, Antidote, False, True)
        else:
            get_target_auto(user, Antidote, True, False, True)

    def queue(user, target):
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Antidote(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))
    
    def run(self):
        if self.user.isHero:
            inventory.remove_item("Antidote")
        utility.log(self.user.attr['name'] + " Antidotes " + self.target.attr['name'])
        self.target.mods[g.BattlerStatus.POISON] = 0
        if self.target.spr.animated:
            if self.target.spr.curAnim == "poison":
                self.target.spr.set_anim("idle")
        self.user.after_turn()
        return -1



####################
##SPECIAL COMMANDS##
####################

class Sacrifice():

    def __init__(self, user):
        self.user = user

    def name():
        return "Sacrifice"

    def start(user):
        Sacrifice.queue(user)

    def queue(user):
        user.BC.UI.create_message(Sacrifice.name())
        user.BC.eventQueue.queue(Sacrifice(user))

    def run(self):
        utility.log(self.user.attr['name'] + " uses Sacrifice.", g.LogLevel.FEEDBACK)
        if g.METER[g.SkillType.BLOOD] < g.METER_MAX:
            g.METER[g.SkillType.BLOOD] += 1
            self.user.BC.UI.create_popup("MAX HP DOWN", self.user.spr.pos, g.RED)
            self.user.sacrifice()

            for hero in self.user.BC.battlers:
                if hero.isHero and not hero.isDead:
                    hero.attr['sp'] = hero.attr['maxSP']
                    self.user.BC.UI.create_popup("FULL SP", hero.spr.pos, g.BLUE)
        else:
            self.user.BC.UI.create_popup("NO EFFECT", self.user.spr.pos, g.RED)
        self.user.reset_anim()
        self.user.after_turn()
        return -1

class Finale():

    def __init__(self, user, targets):
        self.user = user
        self.targets = targets

    def name():
        return "Finale"

    def start(user):
        targets = []
        index = 0
        for target in user.BC.battlers:
            if not target.isHero:
                if not target.isDead:
                    targets.append(target)
            index += 1

        Finale.queue(user, targets)

    def queue(user, targets):
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Finale(user, targets))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))

    def run(self):
        utility.log(self.user.attr['name'] + " uses Finale.", g.LogLevel.FEEDBACK)
        red = 0
        ylw = 0
        blu = 0
        grn = 0
        wht = 0
        blk = 0

        hash = ""

        for note in g.METER[g.SkillType.MUSIC]:
            hash += str(note)
        g.METER[g.SkillType.MUSIC] = []

        if hash == "44":
            self.user.BC.UI.create_message("Thunderclap")
            baseDmg = 15 + self.user.attr['matk']
            for target in self.targets:
                dmg = random.randint(baseDmg, baseDmg + self.user.attr['matk']) - target.attr['mdef']
                target.take_damage(dmg, g.DamageType.ELEC)
        else:
            self.user.BC.UI.create_message("Dissonance")
            baseDmg = 10 + self.user.attr['matk']
            for target in self.targets:
                dmg = random.randint(baseDmg, baseDmg + self.user.attr['matk']) - target.attr['mdef']
                target.take_damage(dmg, g.DamageType.NONE)

        self.user.reset_anim()
        self.user.after_turn()
        return -1

class Transform():

    def __init__(self, user):
        self.user = user

    def name():
        return "Transform"

    def start(user):
        Transform.queue(user)

    def queue(user):
        user.BC.UI.create_message(Transform.name())
        user.BC.eventQueue.queue(Transform(user))

    def run(self):
        utility.log(self.user.attr['name'] + " uses Transform.", g.LogLevel.FEEDBACK)
        self.user.transform()
        self.user.reset_anim()
        self.user.after_turn()
        return -1

##################
##SKILL COMMANDS##
##################

class BloodSlash():

    def __init__(self, user, target):
        self.user = user
        self.target = target

    def name():
        return "Blood Slash"

    def start(user):
        if (user.isHero):
            get_target(user, BloodSlash)
        else:
            get_target_auto(user, BloodSlash)

    def queue(user, target):
        user.BC.UI.create_message(BloodSlash.name())
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(BloodSlash(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))

    def run(self):
        self.user.attr['sp'] -= db.Skill.dic[BloodSlash.name()].spCost
        utility.log(self.user.attr['name'] + " uses Blood Slash on " + self.target.attr['name'])
        if self.user.BC.hit_calc(self.user, self.target):
            if not self.user.BC.dodge_calc(self.user, self.target):
                dmg = (self.user.attr['atk'] // 2) + self.user.BC.phys_dmg_calc(self.user, self.target)
                if self.user.BC.crit_calc(self.user, self.target):
                    dmg*=2
                    self.target.stun()
                dmg += dmg*g.METER[g.SkillType.BLOOD]
                dmg -= self.user.BC.phys_def_calc(self.user, self.target)
                if (dmg < 0):
                    dmg = 0
                self.user.aggro_up()
                self.target.take_damage(dmg, g.DamageType.NONE)

        self.user.after_turn()
        return -1

class Stacatto():

    def __init__(self, user, target):
        self.user = user
        self.target = target

    def name():
        return "Stacatto"

    def start(user):
        if (user.isHero):
            get_target(user, Stacatto)
        else:
            get_target_auto(user, Stacatto)

    def queue(user, target):
        user.BC.UI.create_message(Stacatto.name())
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Stacatto(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))

    def run(self):
        self.user.attr['sp'] -= db.Skill.dic[Stacatto.name()].spCost
        g.music_meter_add(g.DamageType.ELEC)
        utility.log(self.user.attr['name'] + " uses Stacatto on " + self.target.attr['name'])
        baseDmg = 15 + self.user.attr['matk']
        if self.user.BC.hit_calc(self.user, self.target, 5):
            if not self.user.BC.dodge_calc(self.user, self.target):
                dmg = random.randint(baseDmg, baseDmg + self.user.attr['matk']) - self.target.attr['mdef']
                if self.user.BC.crit_calc(self.user, self.target):
                    dmg *= 2
                    self.target.stun()
                if (dmg < 0):
                    dmg = 0
                self.user.aggro_up()
                self.target.take_damage(dmg, g.DamageType.ELEC)

        self.user.after_turn()
        return -1

class DoubleCut():

    def __init__(self, user, target):
        self.user = user
        self.target = target

    def name():
        return "Double Cut"

    def start(user):
        if (user.isHero):
            get_target(user, DoubleCut)
        else:
            get_target_auto(user, DoubleCut)

    def queue(user, target):
        lastAnim = user.spr.curAnim
        user.attr['sp'] -= db.Skill.dic["Double Cut"].spCost
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerStepForward(user, 2))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Attack(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))
        user.BC.eventQueue.queue(event.PlayAnimation(user.spr, "sleep"))
        user.BC.eventQueue.queue(Attack(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.BattlerReturn(user))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))

##################
##ENEMY COMMANDS##
##################

class Toxic():

    def __init__(self, user, target):
        self.user = user
        self.target = target
    
    def name():
        return "Toxic"

    def start(user):
        if (user.isHero):
            get_target(user, Toxic)
        else:
            get_target_auto(user, Toxic)

    def queue(user, target):
        user.BC.UI.create_message(Toxic.name())
        user.attr['sp'] -= db.Skill.dic[Toxic.name()].spCost
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.JumpInPlace(user.BC.eventQueue, user.spr))
        user.BC.eventQueue.queue(event.JumpInPlace(user.BC.eventQueue, user.spr))
        user.BC.eventQueue.queue(Toxic(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))

    def run(self):
        utility.log(self.user.attr['name'] + " uses Poison on " + self.target.attr['name'])
        self.target.poison(33)
        self.user.after_turn()
        return -1

