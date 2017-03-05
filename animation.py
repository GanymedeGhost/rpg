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

class MoveToPos:
    """Moves a Sprite to target position at a given speed"""
    def __init__(self, spr, targetPos, speed = 1):
        self.spr = spr
        self.targetPos = targetPos
        self.speed = speed
    
    def run(self):
        if (self.spr.pos != self.targetPos):
            dX = self.targetPos[0] - self.spr.pos[0]
            dY = self.targetPos[1] - self.spr.pos[1]
            
            if abs(dX) < self.speed:
                self.spr.pos = (self.targetPos[0], self.spr.pos[1])
                dX = 0
            if abs(dY) < self.speed:
                self.spr.pos = (self.spr.pos[0], self.targetPos[1])
                dY = 0

            if (dY < 0):
                self.spr.move_ip((0, -self.speed))
            elif (dY > 0):
                self.spr.move_ip((0, self.speed))
                
            if (dX < 0):
                self.spr.move_ip((-self.speed, 0))
            elif (dX > 0):
                self.spr.move_ip((self.speed, 0))
                
            
                
            return True
        return -1

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
        self.plays = -1

    def run(self):
        if self.spr.animated:
            if self.plays < 0:
                self.spr.set_anim(self.animation, True)
                self.plays += 1
            if self.spr.curFrame == self.length:
                self.plays += 1
                utility.log(str(self.plays))
            if self.plays > self.repeats:
                return -1
            else:
                return True
        return -1



    
