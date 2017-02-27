import pygame
from pygame import *
import my_globals as g

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
        
        self.FONT = pygame.font.Font('font/pixelm8b.ttf', 8)
        self.SURF = UI_SURF
        

    def parse_string(self, string):
        words = string.split(" ")
        wordIndex = 0
        curLine = ""
        lines = []
        while (wordIndex < len(words)):
            if (words[wordIndex] == "&n"):
                wordIndex += 1
                lines.append(curLine)
                curLine = ""
            if (len (curLine) + len(words[wordIndex]) < 19):
                curLine += words[wordIndex] + " "
                wordIndex += 1
            else:
                lines.append(curLine)
                curLine = ""
        lines.append(curLine)
        return lines

    def create_text_box(self, string):
        self.SURF.blit(self.boxImage, (0, 111))
        self.lines = self.parse_string(string)
        self.isTyping = True
        self.boxIndex = 0
        self.lineIndex = 0
        self.charIndex = 0
        self.confirmReleased = False
        self.boxDrawn = False

    def type_text(self, keys):
        if not self.boxDrawn:
            self.SURF.blit(self.boxImage, (0, 111))
            self.boxDrawn = True
        if (keys[g.KEY_CONFIRM]):
            self.frameCounter += self.frameSkip
        if (self.frameCounter > self.frameDelay):
            self.frameCounter = 0
            if (self.lineIndex >= 0 and self.lineIndex < (self.boxIndex+1)*2 and self.lineIndex < len(self.lines)):
                if (self.charIndex < len(self.lines[self.lineIndex])):
                    textObj = self.FONT.render(self.lines[self.lineIndex][self.charIndex], False, g.BLACK)
                    textRect = textObj.get_rect()
                    textRect.topleft = (7 + 8 * self.charIndex, 118 + 10 * self.lineIndex - self.boxIndex * 20)
                    self.SURF.blit(textObj, textRect)
                    self.charIndex += 1
                else:
                    self.charIndex = 0
                    self.lineIndex += 1
            elif (keys[g.KEY_CONFIRM]):
                if (self.confirmReleased):
                    if (self.lineIndex == len(self.lines)):
                        self.destroy_text_box()
                    else:
                        self.SURF.blit(self.boxImage, (0, 111))
                        self.boxIndex += 1
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
        
    
    def draw_text (self, string, pos=(0,0)):
        textObj = self.FONT.render(string, False, g.BLACK)
        textRect = textObj.get_rect()
        textRect.topleft = pos
        self.SURF.blit(textObj, textRect)
