import pygame
import pygame.locals
import my_globals as g
import utility

class AnimationStack:
    def __init__(self, stack=[]):
        self.stack = stack

    def queue(self, action):
        self.stack.append(action)

    def run (self):
        if (self.stack):
            currentAnimCallback = self.stack[0].run()
            if currentAnimCallback < 0:
                del self.stack[0]
            return True
        else:
            return -1

############################
##Sprite Animation Control##
############################

class ChangeAnimation:
    """Changes a Sprite's current animation"""
    def __init__(self, spr, animation, reset = False):
        self.spr = spr
        self.animation = animation
        self.reset = reset

    def run(self):
        if self.spr.animated:
            self.spr.set_anim(self.animation, self.reset)
        return -1

class PauseAnimation:
    """Pauses an animated Sprite's current animation"""
    def __init__(self, spr):
        self.spr = spr

    def run(self):
        if self.spr.animated:
            self.spr.paused = True
        return -1

class ResumeAnimation:
    """Resumes an animated Sprite's current animation"""
    def __init__(self, spr):
        self.spr = spr

    def run(self):
        if self.spr.animated:
            self.spr.paused = False
        return -1

class PlayAnimation:
    """Changes a Sprite's animation and plays it a set number of times"""
    def __init__(self, spr, animation, repeats = 0):
        self.spr = spr
        self.animation = animation
        try:
            self.length = len(self.spr.animations[self.animation])-1
        except KeyError:
            self.length = 0
        self.repeats = repeats * self.length
        self.frameCount = -1

    def run(self):
        if self.spr.animated:
            if self.frameCount < 0:
                self.spr.set_anim(self.animation, True)
                self.frameCount += 1
            if self.spr.curFrame == self.length:
                self.frameCount += 1
                utility.log(str(self.frameCount))
            if self.frameCount > self.repeats:
                return -1
            else:
                return True
        return -1

###########################
##Sprite Movement Control##
###########################

class MoveToPos:
    """Moves a Sprite to target position at a given speed"""
    def __init__(self, spr, targetPos, speed = 1):
        self.spr = spr
        self.targetPos = targetPos
        self.speed = speed
    
    def run(self):
        if (self.spr.pos != self.targetPos):
            distX = self.targetPos[0] - self.spr.pos[0]
            distY = self.targetPos[1] - self.spr.pos[1]
            
            if abs(distX) < self.speed:
                self.spr.pos = (self.targetPos[0], self.spr.pos[1])
                distX = 0
                
            if abs(distY) < self.speed:
                self.spr.pos = (self.spr.pos[0], self.targetPos[1])
                distY = 0

            if (distY < 0):
                deltaY = -self.speed
            elif (distY > 0):
                deltaY = self.speed
            else:
                deltaY = 0
                
            if (distX < 0):
                deltaX = -self.speed
            elif (distX > 0):
                deltaX = self.speed
            else:
                deltaX = 0

            if deltaX != 0 or deltaY != 0:
                self.spr.move_ip((deltaX, deltaY))

            return True
        return -1

class BattlerStepForward:
    
    def __init__(self, battler, speed = 1):
        self.spr = battler.spr
        self.speed = speed
        
        if battler.isHero:
            f = 1
        else:
            f = -1

        self.targetX = battler.spr.anchor[0] - 8*f

    def run(self):
        if (self.spr.pos[0] != self.targetX):
            distX = self.targetX - self.spr.pos[0]
            
            if abs(distX) < self.speed:
                self.spr.pos = (self.targetX, self.spr.pos[1])
                distX = 0
                
            if (distX < 0):
                deltaX = -self.speed
            elif (distX > 0):
                deltaX = self.speed
            else:
                deltaX = 0

            if deltaX != 0:
                self.spr.move_ip((deltaX, 0))

            return True
        return -1

class BattlerReturn:
    
    """Moves a Sprite to target position at a given speed"""
    def __init__(self, battler, speed = 1):
        self.spr = battler.spr
        self.targetPos = battler.spr.anchor
        self.speed = speed
    
    def run(self):
        if (self.spr.pos != self.targetPos):
            distX = self.targetPos[0] - self.spr.pos[0]
            distY = self.targetPos[1] - self.spr.pos[1]
            
            if abs(distX) < self.speed:
                self.spr.pos = (self.targetPos[0], self.spr.pos[1])
                distX = 0
                
            if abs(distY) < self.speed:
                self.spr.pos = (self.spr.pos[0], self.targetPos[1])
                distY = 0

            if (distY < 0):
                deltaY = -self.speed
            elif (distY > 0):
                deltaY = self.speed
            else:
                deltaY = 0
                
            if (distX < 0):
                deltaX = -self.speed
            elif (distX > 0):
                deltaX = self.speed
            else:
                deltaX = 0

            if deltaX != 0 or deltaY != 0:
                self.spr.move_ip((deltaX, deltaY))

            return True
        return -1
