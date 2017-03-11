import random
import battle_command as cmd
import database as db

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
            if (battler.attr['hp'] == battler.attr['maxHP'] and battler.attr['sp'] >= db.Skill.dic['Toxic'].spCost):
                db.Skill.dic['Toxic'].battleAction.start(battler)
            else:
                cmd.Attack.start(battler)
        else:
            battler.after_turn()

dic = {}
dic["Slime"] = Slime
dic["Mold"] = Mold
