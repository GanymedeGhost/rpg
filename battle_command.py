import math
import random
import my_globals as g
import database as db
import event
import inventory
import utility

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
            Attack.get_targets(user)
        else:
            Attack.get_targets_auto(user)
    
    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = True
        SAME = False
        ALIVE = True    
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = Attack.queue

    def get_targets_auto(user, mostAggro=True):
        if mostAggro:
            bestAggro = -1
        else:
            bestAggro = 101
        bestTarget = None
        for target in user.BC.battlers:
            if (user.isHero != target.isHero and target.HP > 0):
                if mostAggro:
                    if target.aggro > bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                else:
                    if target.aggro < bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target

        Attack.queue(user, bestTarget)

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
        utility.log(self.user.NAME + " attacks " + self.target.NAME)
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
        utility.log(self.user.NAME + " is defending.", g.LogLevel.FEEDBACK)
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
            Potion.get_targets(user)
        else:
            Potion.get_targets_auto(user)
    
    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = False
        SAME = True
        ALIVE = True    
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = Potion.queue

    def get_targets_auto(user, mostAggro=True):
        Potion.queue(user, user)

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
        inventory.remove_item("Potion")
        utility.log(self.user.NAME + " Potions " + self.target.NAME)
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
            Revive.get_targets(user)
        else:
            Revive.get_targets_auto(user)
    
    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = False
        SAME = True
        ALIVE = False    
        DEAD = True

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = Revive.queue

    def get_targets_auto(user, mostAggro=True):
        Revive.queue(user, user)

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
        inventory.remove_item("Revive")
        utility.log(self.user.NAME + " Revives " + self.target.NAME)
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
            Antidote.get_targets(user)
        else:
            Antidote.get_targets_auto(user)
    
    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = False
        SAME = True
        ALIVE = True    
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = Antidote.queue

    def get_targets_auto(user, mostAggro=True):
        Antidote.queue(user, user)

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
        inventory.remove_item("Antidote")
        utility.log(self.user.NAME + " Antidotes " + self.target.NAME)
        self.target.mods[g.BattlerStatus.POISON] = 0
        if self.target.spr.animated:
            if self.target.spr.curAnim == "poison":
                self.target.spr.set_anim("idle")
        self.user.after_turn()
        return -1



##################
##SKILL COMMANDS##
##################

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
        utility.log(self.user.NAME + " uses Sacrifice.", g.LogLevel.FEEDBACK)
        if g.METER[g.SkillType.BLOOD] < g.METER_MAX:
            g.METER[g.SkillType.BLOOD] += 1
            self.user.BC.UI.create_popup("MAX HP DOWN", self.user.spr.pos, g.RED)
            self.user.sacrifice()

            for hero in self.user.BC.battlers:
                if hero.isHero:
                    hero.SP = hero.MAXSP
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
                if target.HP > 0:
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
        utility.log(self.user.NAME + " uses Finale.", g.LogLevel.FEEDBACK)
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
            for target in self.targets:
                dmg = 20 + self.user.MATK * 2 - target.MDEF
                target.take_damage(dmg, g.DamageType.ELEC)
        else:
            self.user.BC.UI.create_message("Dissonance")
            for target in self.targets:
                dmg = 10 + self.user.MATK * 2 - target.MDEF
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
        utility.log(self.user.NAME + " uses Transform.", g.LogLevel.FEEDBACK)
        self.user.transform()
        self.user.reset_anim()
        self.user.after_turn()
        return -1

class BloodSlash():

    def __init__(self, user, target):
        self.user = user
        self.target = target

    def name():
        return "Blood Slash"

    def start(user):
        if (user.isHero):
            BloodSlash.get_targets(user)
        else:
            BloodSlash.get_targets_auto(user)

    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = True
        SAME = False
        ALIVE = True
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = BloodSlash.queue

    def get_targets_auto(user, mostAggro=True):
        if mostAggro:
            bestAggro = -1
        else:
            bestAggro = 101
        bestTarget = None
        for target in user.BC.battlers:
            if (user.isHero != target.isHero and target.HP > 0):
                if mostAggro:
                    if target.aggro > bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                else:
                    if target.aggro < bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target

        BloodSlash.queue(user, bestTarget)

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
        self.user.SP -= db.Skill.dic[BloodSlash.name()].spCost
        utility.log(self.user.NAME + " uses Blood Slash on " + self.target.NAME)
        if self.user.BC.hit_calc(self.user, self.target):
            if not self.user.BC.dodge_calc(self.user, self.target):
                dmg = self.user.BC.phys_dmg_calc(self.user, self.target)
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
            Stacatto.get_targets(user)
        else:
            Stacatto.get_targets_auto(user)

    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = True
        SAME = False
        ALIVE = True
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = Stacatto.queue

    def get_targets_auto(user, mostAggro=True):
        if mostAggro:
            bestAggro = -1
        else:
            bestAggro = 101
        bestTarget = None
        for target in user.BC.battlers:
            if (user.isHero != target.isHero and target.HP > 0):
                if mostAggro:
                    if target.aggro > bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                else:
                    if target.aggro < bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target

        BloodSlash.queue(user, bestTarget)

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
        self.user.SP -= db.Skill.dic[Stacatto.name()].spCost
        g.music_meter_add(g.DamageType.ELEC)
        utility.log(self.user.NAME + " uses Stacatto on " + self.target.NAME)
        if self.user.BC.hit_calc(self.user, self.target):
            if not self.user.BC.dodge_calc(self.user, self.target):
                dmg = random.randint(25, 50+self.user.MATK*2) - self.target.MDEF
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
            DoubleCut.get_targets(user)
        else:
            DoubleCut.get_targets_auto(user)

    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = True
        SAME = False
        ALIVE = True
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = DoubleCut.queue

    def get_targets_auto(user, mostAggro=True):
        if mostAggro:
            bestAggro = -1
        else:
            bestAggro = 101
        bestTarget = None
        for target in user.BC.battlers:
            if (user.isHero != target.isHero and target.HP > 0):
                if mostAggro:
                    if target.aggro > bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                else:
                    if target.aggro < bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target

        DoubleCut.queue(user, bestTarget)

    def queue(user, target):
        lastAnim = user.spr.curAnim
        user.SP -= db.Skill.dic["Double Cut"].spCost
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

class Poison():

    def __init__(self, user, target):
        self.user = user
        self.target = target
    
    def name():
        return "Poison"

    def start(user):
        if (user.isHero):
            Poison.get_targets(user)
        else:
            Poison.get_targets_auto(user)
    
    def get_targets(user):
        ALL = False
        USER = False
        OPPOSITE = True
        SAME = False
        ALIVE = True
        DEAD = False

        validTargets = []
        selectedTargets = []
        index = 0
        for target in user.BC.battlers:
            if ((OPPOSITE and (user.isHero != target.isHero)) or (SAME and (user.isHero == target.isHero))):
                if ((ALIVE and (target.HP > 0)) or (DEAD and (target.HP == 0))):
                    validTargets.append(target)
            index += 1

        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = Poison.queue

    def get_targets_auto(user, mostAggro=True):
        if mostAggro:
            bestAggro = -1
        else:
            bestAggro = 101
        bestTarget = None
        for target in user.BC.battlers:
            if (user.isHero != target.isHero and target.HP > 0):
                if mostAggro:
                    if target.aggro > bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target
                else:
                    if target.aggro < bestAggro:
                        bestAggro = target.aggro
                        bestTarget = target

        Poison.queue(user, bestTarget)

    def queue(user, target):
        user.BC.UI.create_message(Poison.name())
        lastAnim = user.spr.curAnim
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, "idle"))
        user.BC.eventQueue.queue(event.JumpInPlace(user.BC.eventQueue, user.spr))
        user.BC.eventQueue.queue(event.JumpInPlace(user.BC.eventQueue, user.spr))
        user.BC.eventQueue.queue(Poison(user, target))
        user.BC.eventQueue.queue(event.ChangeAnimation(user.spr, lastAnim))

    def run(self):
        utility.log(self.user.NAME + " uses Poison on " + self.target.NAME)
        self.target.poison(50)
        self.user.after_turn()
        return -1

