import random
import battle_command as cmd
import database as db

def target_weakest_enemy(battler):
    target = None
    lowestHP = 9999999999

    for mon in battler.BC.battlers:
        if not mon.isHero:
            if mon.attr['hp'] < lowestHP and mon.attr['hp'] != mon.totalMaxHP and not mon.isDead:
                lowestHP = mon.attr['hp']
                target = mon
    return target

def target_strongest_hero(battler):
    target = None
    highestHP = 0

    for hero in battler.BC.battlers:
        if hero.isHero:
            if hero.attr['hp'] > highestHP:
                highestHP = hero.attr['hp']
                target = hero

    return target

class Slime ():

    def run(battler):
        battler.before_turn()

        if battler.can_act():
            roll = random.randint(0, 100)
            if (roll < 50):
                cmd.Attack.start(battler)
            else:
                cmd.Defend.start(battler)

class Mold ():

    def run(battler):
        battler.before_turn()
        
        if battler.can_act():
            if (battler.attr['hp'] == battler.attr['maxHP'] and battler.attr['sp'] >= db.Skill.dic['Toxic'].spCost):
                db.Skill.dic['Toxic'].battleAction.start(battler)
            else:
                cmd.Attack.start(battler)

class Beetle ():

    def run(battler):
        battler.before_turn()

        if battler.can_act():
            target = target_strongest_hero(battler)
            cmd.Attack.queue(battler, target)

class Sapling ():

    def run(battler):
        battler.before_turn()

        if battler.can_act():
            roll = random.randint(0, 100)
            if (roll < 50 and  battler.attr['sp'] >= db.Skill.dic['Symbioism'].spCost):
                target = target_weakest_enemy(battler)
                if target != None:
                    cmd.Symbioism.queue(battler, target)
                else:
                    cmd.Defend.start(battler)
            else:
                cmd.Attack.start(battler)



dic = {}
dic["Slime"] = Slime
dic["Mold"] = Mold
dic["Beetle"] = Beetle
dic["Sapling"] = Sapling

