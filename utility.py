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

def play_time():
    g.playTimeSec += 1
    if g.playTimeSec > 60:
        g.playTimeSec -= 60
        g.playTimeMin += 1
    if g.playTimeMin > 60:
        g.playTimeMin -= 60
        g.playTimeHour += 1

    if g.playTimeSec < 10:
        g.playTimeSecText = "0" + str(g.playTimeSec)
    else:
        g.playTimeSecText = str(g.playTimeSec)
    if g.playTimeMin < 10:
        g.playTimeMinText = "0" + str(g.playTimeMin)
    else:
        g.playTimeMinText = str(g.playTimeMin)
    g.playTimeHourText = str(g.playTimeHour)

def colorize(image, newColor):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param newColor: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy().convert_alpha()
    image.fill((0,0,0,255), None, pygame.BLEND_RGBA_MULT)
    # zero out RGB values
    image.fill(newColor[:] + (0,), None, pygame.BLEND_RGBA_ADD)

    return image

def log(string = "", level = g.LogLevel.DEBUG):
    if g.logFilter[level]:
        print (string)
               
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

        image = pygame.image.load(filename).convert_alpha()
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
    
    def __init__(self, uiSurf):
        self.isTyping = False
        self.lines = None
        self.boxImage = pygame.image.load("spr/text-box.png")

        self.textObj = None
        self.texRect = None

        self.frameDelay = g.textDelay
        self.frameSkip = g.textSkip
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
        self.uiSurf = uiSurf

    def parse_string(self, string, maxX = 150):
        words = string.split(" ")
        wordIndex = 0
        curLine = ""
        curWidth = 0
        lines = []
        glyphList = []
        glyphX = []
        glyphLine = []
        glyphIndex = []

        while (wordIndex < len(words)):
            if words[wordIndex].find("&i") >= 0:
                glyphIndex.append(len(curLine))

                curLine += "   "
                curWidth += self.curFont.size("   ")[0]

                glyphX.append(curWidth)
                glyphList.append(g.iconCache.icon(words[wordIndex]))
                glyphLine.append(len(lines))

                wordIndex += 1

            elif words[wordIndex] == "&n":
                wordIndex += 1
                lines.append(curLine)
                curLine = ""
                curWidth = 0
            elif curWidth + self.curFont.size(words[wordIndex])[0] < maxX:
                curLine += words[wordIndex] + " "
                wordIndex += 1
                curWidth = self.curFont.size(curLine)[0]
            else:
                lines.append(curLine[0:-1])
                curLine = ""
                curWidth = 0

        lines.append(curLine)
        return lines, glyphList, glyphX, glyphLine, glyphIndex

    def create_text_box(self, string, font = g.FONT_LRG):
        self.uiSurf.blit(self.boxImage, (0, 111))
        self.curFont = font
        self.curHeight = 0
        self.lines, self.glyphList, self.glyphX, self.glyphLine, self.glyphIndex = self.parse_string(string)
        self.isTyping = True
        self.boxIndex = 0
        self.lineIndex = 0
        self.charIndex = 0
        self.confirmReleased = False
        self.boxDrawn = False
        self.nextX = self.startX
        self.nextY = self.startY

    def type_text(self, keys, maxY = 140):
        if not self.boxDrawn:
            self.uiSurf.blit(self.boxImage, (0, 111))
            self.boxDrawn = True
        if (keys[g.keyConfirm]):
            self.frameCounter += self.frameSkip
        if (self.frameCounter > self.frameDelay):
            self.frameCounter = 0
            if (self.lineIndex >= 0 and (self.nextY + self.curFont.size("X")[1]) < maxY and self.lineIndex < len(self.lines)):
                if (self.charIndex < len(self.lines[self.lineIndex])):

                    if self.glyphIndex:
                        if self.charIndex == self.glyphIndex[0] and self.lineIndex == self.glyphLine[0]:
                            self.uiSurf.blit(self.glyphList[0], (self.nextX-4, self.nextY+1))
                            del self.glyphList[0]
                            del self.glyphX[0]
                            del self.glyphIndex[0]
                            del self.glyphLine[0]

                    textObj = self.curFont.render(self.lines[self.lineIndex][self.charIndex], False, g.BLACK)
                    textRect = textObj.get_rect()
                    textRect.topleft = (self.nextX, self.nextY)
                    self.nextX += self.curFont.size(self.lines[self.lineIndex][self.charIndex])[0]
                    self.uiSurf.blit(textObj, textRect)
                    self.charIndex += 1
                else:
                    self.nextX = self.startX
                    self.nextY += self.curFont.size("X")[1]
                    self.charIndex = 0
                    self.lineIndex += 1
            elif (keys[g.keyConfirm]):
                if (self.confirmReleased):
                    if (self.lineIndex == len(self.lines)):
                        self.destroy_text_box()
                    else:
                        self.uiSurf.blit(self.boxImage, (0, 111))
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

    def draw_text (self, string, pos=(0,0), color = g.BLACK, font = g.FONT_LRG):
        textObj = font.render(string, False, color)
        textRect = textObj.get_rect()
        textRect.topleft = pos
        self.uiSurf.blit(textObj, textRect)

    def draw_text_f(self, string, pos=(0,0), color = g.BLACK, maxWidth = g.VIEW_WIDTH, wrap = False, font = g.FONT_LRG):
        parsedStr, glyphList, glyphX, glyphLine, glyphIndex = self.parse_string(string, maxWidth)
        offset = pos
        heightInc = (0, font.size("X")[1]-4)

        for line in parsedStr:
            self.draw_text(line, offset, color)
            offset = add_tuple(offset, heightInc)

        index = 0
        for glyph in glyphList:
            self.uiSurf.blit(glyph, (pos[0] + glyphX[index] - 14, pos[1] + glyphLine[index] * font.size('X')[1] + 1))
            index += 1

    def draw_text_fr(self, string, pos=(0,0), color = g.BLACK, maxWidth = g.VIEW_WIDTH, wrap = False, font = g.FONT_LRG):
        parsedStr, glyphList, glyphX, glyphLine, glyphIndex = self.parse_string(string, maxWidth)
        offset = add_tuple(pos, (4, 0))
        heightInc = (0, font.size("X")[1]-4)

        for line in parsedStr:
            self.draw_text_ralign(line, offset, color)
            offset = add_tuple(offset, heightInc)

        index = 0
        for glyph in glyphList:
            self.uiSurf.blit(glyph, (pos[0] - glyphX[index], pos[1] - glyphLine[index] * font.size('X')[1]))
            index += 1

    def draw_text_centered(self, string, pos=(0,0), color = g.BLACK, font = g.FONT_LRG):
        textObj = font.render(string, False, color)
        textRect = textObj.get_rect()
        textRect.center = pos
        self.uiSurf.blit(textObj, textRect)

    def draw_text_ralign (self, string, pos=(0,0), color = g.BLACK, font = g.FONT_LRG):
        textObj = font.render(string, False, color)
        textRect = textObj.get_rect()
        textRect.topright = pos
        self.uiSurf.blit(textObj, textRect)

    def draw_text_shaded(self, string, pos, color1 = g.WHITE, color2 = g.BLACK, font = g.FONT_LRG):
        textObj4 = font.render(string, False, color2)
        textRect4 = textObj4.get_rect()
        textRect4.topleft = add_tuple(pos, (1,0))
        self.uiSurf.blit(textObj4, textRect4)
        textObj3 = font.render(string, False, color2)
        textRect3 = textObj3.get_rect()
        textRect3.topleft = add_tuple(pos, (1,1))
        self.uiSurf.blit(textObj3, textRect3)
        textObj2 = font.render(string, False, color2)
        textRect2 = textObj2.get_rect()
        textRect2.topleft = add_tuple(pos, (0,1))
        self.uiSurf.blit(textObj2, textRect2)
        textObj1 = font.render(string, False, color1)
        textRect1 = textObj1.get_rect()
        textRect1.topleft = pos
        self.uiSurf.blit(textObj1, textRect1)

    def draw_text_shaded_centered(self, string, pos, color1 = g.WHITE, color2 = g.BLACK, font = g.FONT_LRG):
        textObj4 = font.render(string, False, color2)
        textRect4 = textObj4.get_rect()
        textRect4.center = add_tuple(pos, (1,0))
        self.uiSurf.blit(textObj4, textRect4)
        textObj3 = font.render(string, False, color2)
        textRect3 = textObj3.get_rect()
        textRect3.center = add_tuple(pos, (1,1))
        self.uiSurf.blit(textObj3, textRect3)
        textObj2 = font.render(string, False, color2)
        textRect2 = textObj2.get_rect()
        textRect2.center = add_tuple(pos, (0,1))
        self.uiSurf.blit(textObj2, textRect2)
        textObj1 = font.render(string, False, color1)
        textRect1 = textObj1.get_rect()
        textRect1.center = pos
        self.uiSurf.blit(textObj1, textRect1)

    def draw_text_shaded_ralign(self, string, pos, color1 = g.WHITE, color2 = g.BLACK, font = g.FONT_LRG):
        textObj4 = font.render(string, False, color2)
        textRect4 = textObj4.get_rect()
        textRect4.topright = add_tuple(pos, (1,0))
        self.uiSurf.blit(textObj4, textRect4)
        textObj3 = font.render(string, False, color2)
        textRect3 = textObj3.get_rect()
        textRect3.topright = add_tuple(pos, (1,1))
        self.uiSurf.blit(textObj3, textRect3)
        textObj2 = font.render(string, False, color2)
        textRect2 = textObj2.get_rect()
        textRect2.topright = add_tuple(pos, (0,1))
        self.uiSurf.blit(textObj2, textRect2)
        textObj1 = font.render(string, False, color1)
        textRect1 = textObj1.get_rect()
        textRect1.topright = pos
        self.uiSurf.blit(textObj1, textRect1)
