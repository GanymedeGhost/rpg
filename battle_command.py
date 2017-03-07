import my_globals as g
import event
import inventory
import utility

class UseItem():

    def __init__(self, user, action):
        self.user = user
        self.action = action

    def name():
        return "Items"

    def start(user):
        UseItem.get_item(user)

    def get_item(user):
        user.BC.change_state(g.BattleState.ITEM)
        user.BC.UI.get_item(user)
        user.BC.queuedAction = UseItem.queue

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

        user.BC.change_state(g.BattleState.TARGET)
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
        if (user.isHero):
            f = -1
        else:
            f = 1
        pos = utility.add_tuple(user.spr.pos, (6*f, 0))
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

class DoubleAttack():

    def __init__(self, user, target):
        self.user = user
        self.target = target
    
    def name():
        return "2x Attack"

    def start(user):
        if (user.isHero):
            DoubleAttack.get_targets(user)
        else:
            DoubleAttack.get_targets_auto(user)
    
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

        user.BC.change_state(g.BattleState.TARGET)
        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = DoubleAttack.queue

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

        DoubleAttack.queue(user, bestTarget)

    def queue(user, target):
        user.BC.UI.create_message(DoubleAttack.name())
        if (user.isHero):
            f = -1
        else:
            f = 1
        pos = utility.add_tuple(user.spr.pos, (6*f, 0))
        lastAnim = user.spr.curAnim
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

        user.BC.change_state(g.BattleState.TARGET)
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
        
        pos = utility.add_tuple(user.spr.pos, (0, -4))
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

        user.BC.change_state(g.BattleState.TARGET)
        user.BC.UI.get_target(user, validTargets)
        user.BC.queuedAction = Potion.queue

    def get_targets_auto(user, mostAggro=True):
        Potion.queue(user, user)

    def queue(user, target):
        if (user.isHero):
            f = -1
        else:
            f = 1
        pos = utility.add_tuple(user.spr.pos, (6*f, 0))
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
        utility.log(self.user.NAME + " potions " + self.target.NAME)
        self.target.heal_hp(50)
        self.user.after_turn()
        return -1
