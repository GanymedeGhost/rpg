import my_globals as g
import animation
import utility

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
        user.BC.animationStack.queue(animation.ChangeAnimation(user.spr, "idle"))
        user.BC.animationStack.queue(animation.BattlerStepForward(user, 2))
        user.BC.animationStack.queue(animation.PlayAnimation(user.spr, "sleep"))
        user.BC.animationStack.queue(Attack(user, target))
        user.BC.animationStack.queue(animation.ChangeAnimation(user.spr, "idle"))
        user.BC.animationStack.queue(animation.BattlerReturn(user))
        user.BC.animationStack.queue(animation.ChangeAnimation(user.spr, lastAnim))
    
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

class Defend():

    def __init__(self, user):
        self.user = user

    def name():
        return "Defend"

    def start(user):
        Defend.queue(user)

    def queue(user):
        user.BC.UI.create_message(Defend.name())
        user.BC.animationStack.queue(Defend(user))

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
        user.BC.animationStack.queue(animation.ChangeAnimation(user.spr, "idle"))
        user.BC.animationStack.queue(animation.MoveToPos(user.spr, pos, 2))
        user.BC.animationStack.queue(animation.MoveToPos(user.spr, user.spr.anchor))
        user.BC.animationStack.queue(animation.MoveToPos(user.spr, pos, 2))
        user.BC.animationStack.queue(animation.MoveToPos(user.spr, user.spr.anchor))
        user.BC.animationStack.queue(Poison(user, target))
        user.BC.animationStack.queue(animation.ChangeAnimation(user.spr, lastAnim))

    def run(self):
        utility.log(self.user.NAME + " uses Poison on " + self.target.NAME)
        self.target.poison(50)

        self.user.after_turn()
        return -1
