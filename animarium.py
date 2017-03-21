import copy
import random
import my_globals as g
import database as db


def clear_all():
    for i in range (0, g.ANIMAGI_MAX_SLOTS):
        clear_slot(i)

def clear_slot(slot):
    del g.ANIMAGI[slot]

def add_animagus(key):
    if len(g.ANIMAGI) < g.ANIMARIUM_MAX_SLOTS:
        g.ANIMAGI.append(copy.deepcopy(db.Animagus.dic[key]))
        return True
    else:
        return False

def can_level(animagus, hero):
    if animagus.level < 5:
        if hero.exp >= animagus.levelUpAt:
            return True
        else:
            return False
    return False

def level_up(animagus, hero):
    if can_level(animagus, hero):
        hero.exp -= animagus.levelUpAt
        hero.attr['lvl'] += 1

        if "str" in animagus.growth:
            min = animagus.growth['str']
            max = min + 1
        else:
            min = 0
            max = 1
        hero.attr['str'] += random.randint(min, max+1)

        if "end" in animagus.growth:
            min = animagus.growth['end']
            max = min + 1
        else:
            min = 0
            max = 1
        hero.attr['end'] += random.randint(min, max+1)

        if "wis" in animagus.growth:
            min = animagus.growth['wis']
            max = min + 1
        else:
            min = 0
            max = 1
        hero.attr['wis'] += random.randint(min, max+1)

        if "spr" in animagus.growth:
            min = animagus.growth['spr']
            max = min + 1
        else:
            min = 0
            max = 1
        hero.attr['spr'] += random.randint(min, max+1)

        if "agi" in animagus.growth:
            min = animagus.growth['agi']
            max = min + 1
        else:
            min = 0
            max = 1
        hero.attr['agi'] += random.randint(min, max+1)

        if "lck" in animagus.growth:
            min = animagus.growth['lck']
            max = min + 1
        else:
            min = 0
            max = 1
        hero.attr['lck'] += random.randint(min, max+1)

        animagus.exp += animagus.levelUpAt
        animagus.level += 1
        animagus.levelUpAt += animagus.expToNext
        learn_skill(animagus, hero)

        return True
    else:
        return False


def learn_skill(animagus, hero):
    for skill in animagus.skills:
        if not skill in animagus.skillsTaught and not skill in hero.skills:
            if skill.skillType == g.SkillType.NONE or skill.skillType == hero.skillType:
                hero.skills.append(skill)
                animagus.skillsTaught.append(skill)
                return True
            else:
                return False
    else:
        return False