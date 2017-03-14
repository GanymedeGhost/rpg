import random
import my_globals as g
import database as db
import event
import inventory
import utility

def get_target(user, cmdClass, alive = True, dead = False):

    validTargets = []
    index = 0
    for target in user.BC.battlers:
        if alive and not target.isDead or dead and target.isDead:
            validTargets.append(target)
        index += 1

    user.MC.UI.get_target(user, validTargets)
    user.MC.queuedAction = cmdClass.queue