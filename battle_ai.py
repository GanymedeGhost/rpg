import math
import random
import battle

class Slime ():

    def run(battler):
        battler.before_turn()

        if battler.can_act():
            roll = random.randint(0, 100)
            if (roll < 50):
                battle.CmdAttack.start(battler)
            else:
                battle.CmdDefend.start(battler)
        else:
            battler.after_turn()

class Mold ():

    def run(battler):
        battler.before_turn()
        
        if battler.can_act():
            roll = random.randint(0, 100)
            if (battler.HP == battler.MAXHP):
                battle.CmdPoison.start(battler)
            else:
                battle.CmdAttack.start(battler)
        else:
            battler.after_turn()

dic = {}
dic["Slime"] = Slime
dic["Mold"] = Mold
