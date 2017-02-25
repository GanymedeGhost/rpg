import pygame
import pygame.locals
import utility
import random

class BattleMod():
    DEFEND = 0
    POISON = 1
    SLEEP = 2
    SILENCE = 3
    STUN = 4 

class Battle (object):
    def __init__(self):
        random.seed()
        self.enemies = []
        self.heroes = []

        self.enemies.append( BattleActor(self, "Slime") )
        self.heroes.append( BattleActor(self, "Vinny") )

    def battle_loop(self):
        while (self.enemies_alive() and self.heroes_alive()):
            print ("*NEW TURN*")
            self.list_heroes()
            self.list_enemies()
            #ACTOR ACTIONS
            for enemy in self.enemies:
                if (enemy.HP > 0):
                    enemy.preturn()
                    AIRoll = random.randint(0, 1)
                    if AIRoll == 0:
                        enemy.attack(self.heroes[0])
                    elif AIRoll == 1:
                        enemy.defend()
            for hero in self.heroes:
                if (hero.HP > 0):
                    hero.preturn()
                    command = input("What will you do? ")
                    if (command == "attack"):
                        hero.attack(self.enemies[0])
                    elif (command == "defend"):
                        hero.defend()
                    else:
                        print("Invalid command!")
            

    def list_enemies(self):
        print("*ENEMIES*")
        for actor in self.enemies:
            print (actor.NAME)
            print ("HP: " + str(actor.HP))

    def list_heroes(self):
        print("*HEROES*")
        for actor in self.heroes:
            print (actor.NAME)
            print ("HP: " + str(actor.HP))

    def enemies_alive(self):
        for actor in self.enemies:
            if actor.HP > 0:
                return True
        return False

    def heroes_alive(self):
        for actor in self.heroes:
            if actor.HP > 0:
                return True
        return False
            

class BattleActor (object):
    
    def __init__(self, BC, NAME, LVL = 1, HP=10, SP = 10, ATK = 5, DEF = 5, MATK = 5, MDEF = 5, AGI = 5, HIT = 95, EVA = 5):
        self.BC = BC
        self.NAME = NAME
        self.HP = HP
        self.SP = SP
        self.ATK = ATK
        self.DEF = DEF
        self.MATK = MATK
        self.MDEF = MDEF
        self.AGI = AGI
        self.HIT = HIT
        self.EVA = EVA
        
        self.mods = {}
        self.mods[BattleMod.DEFEND] = 0

    def attack(self, target):
        if (random.randint(0, 100) < self.HIT):
            if (random.randint(0, 100) > target.EVA):
                if (target.mods[BattleMod.DEFEND] > 0):
                    defMod = target.DEF
                else:
                    defMod = 0
                print ("defMod: " + str(defMod))
                defTotal = target.DEF + defMod // 2
                damageMin = self.ATK + (self.ATK // 2) - defTotal
                damageMax = self.ATK * 2 - defTotal
                damage = random.randint(damageMin, damageMax)
                if (damage < 0):
                    damage = 0
                print (self.NAME + " does " + str(damage) + " damage to " + target.NAME)
                target.take_damage(damage)
            else:
                print (target.NAME + " avoided " + self.NAME + "'s attack!")
        else:
            print (self.NAME + "'s attack missed " + target.NAME)

    def defend(self):
        print (self.NAME + " is defending.")
        self.mods[BattleMod.DEFEND] += 1

    def preturn(self):
        for mod in self.mods:
            if (self.mods[mod] > 0):
                self.mods[mod] -= 1

    def take_damage(self, damage):
        self.HP -= damage
        
        if (self.HP < 0):
            self.HP = 0
        if (self.HP == 0):
            print (self.NAME + " died!")
            

if __name__=='__main__':
    BC = Battle()

    BC.battle_loop()
    print ("***")
    print ("Battle over")
        

    
