import pygame
from pygame import *
import my_globals as g

def add_tuple(a, b):
    s0 = a[0]+b[0]
    s1 = a[1]+b[1]
    return s0,s1

def scale_tuple(o, f):
    p0 = o[0] * f[0]
    p1 = o[1] * f[1]
    return p0, p1
               
class TileCache:
    """Load the tilesets lazily into global cache"""

    def __init__(self,  width=g.TILE_SIZE, height=g.TILE_SIZE):
        self.width = width
        self.height = height or width
        self.cache = {}

    def __getitem__(self, filename):
        """Return a table of tiles, load it from disk if needed."""

        key = (filename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table(filename, self.width,
                                               self.height)
            self.cache[key] = tile_table
            return tile_table

    def _load_tile_table(self, filename, width, height):
        """Load an image and split it into tiles."""

        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width//width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height//height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

class TextManager:
    
    def __init__(self, UI_SURF):
        self.isTyping = False
        self.lines = None
        self.boxImage = pygame.image.load("spr/text-box.png")

        self.textObj = None
        self.texRect = None

        self.frameDelay = 1
        self.frameSkip = 1
        self.frameCounter = 0

        self.boxIndex = 0
        self.lineIndex = 0
        self.charIndex = 0
        self.waitForConfirm = False
        self.confirmReleased = False
        self.boxDrawn = False

        self.startX = 5
        self.startY = 118
        self.maxX = 150
        self.maxY = 140
        
        self.curFont = g.FONT_MED
        self.SURF = UI_SURF
        

    def parse_string(self, string):
        words = string.split(" ")
        wordIndex = 0
        curLine = ""
        curWidth = 0
        lines = []
        while (wordIndex < len(words)):
            if (words[wordIndex] == "&n"):
                wordIndex += 1
                lines.append(curLine)
                curLine = ""
                curWidth = 0
            if curWidth + self.curFont.size(words[wordIndex])[0] < self.maxX:
                curWidth += self.curFont.size(words[wordIndex] + " ")[0]
                curLine += words[wordIndex] + " "
                wordIndex += 1
            else:
                lines.append(curLine)
                curLine = ""
                curWidth = 0
        lines.append(curLine)
        return lines

    def create_text_box(self, string, font = g.FONT_MED):
        self.SURF.blit(self.boxImage, (0, 111))
        self.curFont = font
        self.curHeight = 0
        self.lines = self.parse_string(string)
        self.isTyping = True
        self.boxIndex = 0
        self.lineIndex = 0
        self.charIndex = 0
        self.confirmReleased = False
        self.boxDrawn = False
        self.nextX = self.startX
        self.nextY = self.startY

    def type_text(self, keys, font = g.FONT_MED):
        if not self.boxDrawn:
            self.SURF.blit(self.boxImage, (0, 111))
            self.boxDrawn = True
        if (keys[g.KEY_CONFIRM]):
            self.frameCounter += self.frameSkip
        if (self.frameCounter > self.frameDelay):
            self.frameCounter = 0
            if (self.lineIndex >= 0 and (self.nextY + self.curFont.size("X")[1]) < self.maxY and self.lineIndex < len(self.lines)):
                if (self.charIndex < len(self.lines[self.lineIndex])):
                    textObj = self.curFont.render(self.lines[self.lineIndex][self.charIndex], False, g.BLACK)
                    textRect = textObj.get_rect()
                    textRect.topleft = (self.nextX, self.nextY)
                    self.nextX += self.curFont.size(self.lines[self.lineIndex][self.charIndex])[0]
                    self.SURF.blit(textObj, textRect)
                    self.charIndex += 1
                else:
                    self.nextX = self.startX
                    self.nextY += self.curFont.size("X")[1]
                    self.charIndex = 0
                    self.lineIndex += 1
            elif (keys[g.KEY_CONFIRM]):
                if (self.confirmReleased):
                    if (self.lineIndex == len(self.lines)):
                        self.destroy_text_box()
                    else:
                        self.SURF.blit(self.boxImage, (0, 111))
                        self.boxIndex += 1
                        self.nextY = self.startY
                    self.confirmReleased = False
            else:
                self.confirmReleased = True
        self.frameCounter += 1

    def destroy_text_box(self):
        self.lineIndex = -1
        self.boxIndex = 0
        del self.lines[:]
        self.isTyping = False
        self.confirmRelease = False
        self.boxDrawn = False
        
    
    def draw_text (self, string, pos=(0,0), color = g.BLACK, font = g.FONT_MED):
        textObj = font.render(string, False, color)
        textRect = textObj.get_rect()
        textRect.topleft = pos
        self.SURF.blit(textObj, textRect)

    def draw_text_shaded(self, string, pos, color1 = g.WHITE, color2 = g.BLACK, font = g.FONT_MED):
        textObj4 = font.render(string, False, color2)
        textRect4 = textObj4.get_rect()
        textRect4.topleft = add_tuple(pos, (1,0))
        self.SURF.blit(textObj4, textRect4)
        textObj3 = font.render(string, False, color2)
        textRect3 = textObj3.get_rect()
        textRect3.topleft = add_tuple(pos, (1,1))
        self.SURF.blit(textObj3, textRect3)
        textObj2 = font.render(string, False, color2)
        textRect2 = textObj2.get_rect()
        textRect2.topleft = add_tuple(pos, (0,1))
        self.SURF.blit(textObj2, textRect2)
        textObj1 = font.render(string, False, color1)
        textRect1 = textObj1.get_rect()
        textRect1.topleft = pos
        self.SURF.blit(textObj1, textRect1)
