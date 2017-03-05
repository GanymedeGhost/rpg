import random
import battle_command as cmd

class Slime ():

    def run(battler):
        battler.before_turn()

        if battler.can_act():
            roll = random.randint(0, 100)
            if (roll < 50):
                cmd.Attack.start(battler)
            else:
                cmd.Defend.start(battler)
        else:
            battler.after_turn()

class Mold ():

    def run(battler):
        battler.before_turn()
        
        if battler.can_act():
            roll = random.randint(0, 100)
            if (battler.HP == battler.MAXHP):
                cmd.Poison.start(battler)
            else:
                cmd.Attack.start(battler)
        else:
            battler.after_turn()

dic = {}
dic["Slime"] = Slime
dic["Mold"] = Mold
