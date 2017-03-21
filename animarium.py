import copy
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