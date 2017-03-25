import random
import my_globals as g
import database as db
import event
import inventory
import utility

def get_target(MC, cmdClass, alive = True, dead = False):

    validTargets = []
    index = 0
    for target in g.partyList:
        if alive and not target.isDead or dead and target.isDead:
            validTargets.append(target)
        index += 1

    MC.UI.get_target(validTargets)
    MC.queuedAction = cmdClass.queue

#################
##ITEM COMMANDS##
#################

class Potion():

    def __init__(self, MC, target):
        self.MC = MC
        self.target = target

    def start(MC):
        get_target(MC, Potion)

    def queue(MC, target, user = None):
        MC.eventQueue.queue(Potion(MC, target))

    def run(self):
        if self.target.attr['hp'] < self.target.baseMaxHP:
            inventory.remove_item("Potion")
            utility.log("Used Potion on " + str(self.target.attr['name']))
            self.target.heal_hp(50, g.DamageType.NONE)
            if inventory.find_item("Potion"):
                self.MC.prev_state()
                self.MC.UI.restore_cursor()
        else:
            utility.log("No effect")
        return -1

class Revive():

    def __init__(self, MC, target):
        self.MC = MC
        self.target = target

    def start(MC):
        get_target(MC, Revive, False, True)

    def queue(MC, target, user = None):
        MC.eventQueue.queue(Revive(MC, target))

    def run(self):
        if self.target.attr['hp'] <= 0:
            inventory.remove_item("Revive")
            utility.log("Used Revive on " + str(self.target.attr['name']))
            self.target.revive(33)
            if inventory.find_item("Revive"):
                self.MC.prev_state()
                self.MC.UI.restore_cursor()
        else:
            utility.log("No effect")
        return -1


##################
##SKILL COMMANDS##
##################

class Adagio():

    def __init__(self, MC, target):
        self.MC = MC
        self.target = target
        self.user = MC.UI.currentHero

    def start(MC, user):
        get_target(MC, Adagio, True, False)

    def queue(MC, target):
        MC.eventQueue.queue(Adagio(MC, target))

    def run(self):
        if self.target.attr['hp'] < self.target.baseMaxHP:
            self.user.attr['sp'] -= db.Skill.dic["Adagio"].spCost
            utility.log("Used Adagio on " + str(self.target.attr['name']))

            baseDmg = 30 + self.user.baseMAtk
            dmg = random.randint(baseDmg, baseDmg + self.user.baseMAtk)
            self.target.heal_hp(dmg, g.DamageType.LIGHT)

            if not db.Skill.check_cost(self.user, db.Skill.dic["Adagio"]):
                self.MC.prev_state()
                self.MC.UI.restore_cursor()
        else:
            utility.log("No effect")
        return -1