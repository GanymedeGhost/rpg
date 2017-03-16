import random
import my_globals as g
import database as db
import event
import inventory
import utility

def get_target(MC, cmdClass, alive = True, dead = False, user = None):

    validTargets = []
    index = 0
    for target in g.PARTY_LIST:
        if alive and not target.isDead or dead and target.isDead:
            validTargets.append(target)
        index += 1

    MC.UI.get_target(validTargets, user)
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
            utility.log("Used Potion on " + str(self.target.attr['hp']))
            self.target.heal_hp(50)
            if inventory.find_item("Potion"):
                self.MC.prev_state()
                self.MC.UI.restore_cursor()
        else:
            utility.log("No effect")
        return -1