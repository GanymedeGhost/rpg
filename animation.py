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
    def __init__(self, spr, targetPos):
        self.spr = spr
        self.targetPos = targetPos
    
    def run(self):
        if (self.spr.pos != self.targetPos):
            if (self.spr.pos[0] > self.targetPos[0]):
                self.spr.move_ip((-1,0))
            elif (self.spr.pos[0] < self.targetPos[0]):
                self.spr.move_ip((1,0))
            if (self.spr.pos[1] > self.targetPos[1]):
                self.spr.move_ip((0,-1))
            elif (self.spr.pos[1] < self.targetPos[1]):
                self.spr.move_ip((0,1))
            return True
        return -1

    
