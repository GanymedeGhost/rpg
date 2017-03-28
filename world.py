import configparser
import random
import pygame
import pygame.locals
import my_globals as g
import utility

class Level(object):

    def __init__(self, viewport, controller):
        self.rect = pygame.Rect(0,0, 1,1)
        self.image = None
        self.overlayImage = None
        self.viewport = viewport
        self.controller = controller
        self.TM = self.controller.TM
        self.entities = {}
        self.scenery = []
        self.overlays = []
        self.tileset = {}

        self.battleStepCounter = 100
        self.battleRate = (0,0)

    def load_file(self, filename="lvl/level.map"):
        self.map = []
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read(filename)

        self.tileset = parser.get("level", "tileset")
        self.map = parser.get("level", "map").split("\n")
        rate = parser.get("battle", "rate").split(",")
        self.battleRate = (int(rate[0]), int(rate[1]))
        if self.battleRate != (0,0):
            self.load_battle_data(parser)

        self.load_map_tiles(parser)

        #render the static BG once
        self.render()

    def load_battle_data(self, parser):
        self.battleList = []
        enemyMap = parser.get("battle", "enemies").split("\n")
        if enemyMap:
            for line in enemyMap:
                self.battleList.append(line.split(","))
        self.reset_battle_step_counter()

    def load_map_tiles(self, parser):
        for section in parser.sections():
            if (len(section)) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.mapTileCache = utility.TileCache(g.TILE_SIZE)
        self.sprites = {}
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if not self.is_wall(x, y) and 'sprite' in self.key[c]:
                    self.sprites[(x, y)] = self.key[c]
                elif 'entity' in self.key[c]:
                    self.add_entity(ENTITY_DIC[self.key[c]['entity']](self.key[c]['name'], self, (x, y), self.mapTileCache['spr/red.png'], False))
                if 'scenery' in self.key[c]:
                    tile = self.key[c]['scenery'].split(",")
                    image = self.mapTileCache[self.tileset][int(tile[0])][int(tile[1])]
                    self.scenery.append(Tile(image, (x,y)))
                if 'overlay' in self.key[c]:
                    tile = self.key[c]['overlay'].split(",")
                    image = self.mapTileCache[self.tileset][int(tile[0])][int(tile[1])]
                    self.overlays.append(Tile(image, (x,y)))

    def get_tile(self, x, y):
        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
                return {}

    def get_bool(self, x, y, name):
        value = self.get_tile(x,y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_wall(self, x, y):
        return self.get_bool(x, y, 'wall')

    def is_blocking(self, x, y):
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        return self.get_bool(x, y, 'block')

    def update_viewport(self):
        self.viewport.center = self.entities["player"].rect.center
        self.viewport.clamp_ip(self.rect)

    def update(self, dt, keys):
        #run update() for all entities, then center the viewport
        for ent in self.entities:
            self.entities[ent].update(dt, keys)
        self.update_viewport()

    def check_random_battle(self):
        self.battleStepCounter -= 1
        if self.battleStepCounter <= 0:
            self.reset_battle_step_counter()
            index = random.randint(0, len(self.battleList)-1)
            self.controller.start_battle(self.battleList[index])

    def reset_battle_step_counter(self):
        self.battleStepCounter = random.randint(self.battleRate[0], self.battleRate[1])

    def add_entity(self, entity):
        try:
            if (self.entities[entity.handle] != entity):
                utility.log("ERROR: An entity with handle '" + entity.handle + "' already exists in this level", g.LogLevel.ERROR)
            else:
                utility.log("ERROR: This entity already exists in this level", g.LogLevel.ERROR)
        except KeyError:
            self.entities[entity.handle] = entity

    def render(self):
        wall = self.is_wall
        tiles = self.mapTileCache[self.tileset]
        self.image = pygame.Surface((self.width*g.TILE_SIZE, self.height*g.TILE_SIZE))

        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                if wall(map_x, map_y):
                    tile = 6, 0
                else:
                    try:
                        tile = self.key[c]['tile'].split(',')
                        tile = int(tile[0]), int(tile[1])
                    except (ValueError, KeyError):
                        #default to ground tile
                        tile = 0, 0
                tile_image = tiles[tile[0]][tile[1]]
                self.image.blit(tile_image, (map_x*g.TILE_SIZE, map_y*g.TILE_SIZE))

        self.rect = self.image.get_rect()

    def draw (self, surface):
        new_image = self.image.copy()

        for scenery in self.scenery:
            if (scenery.rect.topleft[0] >= self.viewport.topleft[0] - 16 and
                scenery.rect.topright[0] <= self.viewport.topright[0] + 16 and
                scenery.rect.topleft[1] >= self.viewport.topleft[1] - 16 and
                scenery.rect.bottomright[1] <= self.viewport.bottomright[1] + 16):

                scenery.draw(new_image)

        for ent in self.entities:
            self.entities[ent].draw(new_image)

        for over in self.overlays:
            if (over.rect.topleft[0] >= self.viewport.topleft[0] - 16 and
                over.rect.topright[0] <= self.viewport.topright[0] + 16 and
                over.rect.topleft[1] >= self.viewport.topleft[1] - 16 and
                over.rect.bottomright[1] <= self.viewport.bottomright[1] + 16):

                over.draw(new_image)

        surface.blit(new_image, (0,0), self.viewport)


class Tile(pygame.sprite.Sprite):

    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()

        self.pos = pos

    def _get_pos(self):
        return (self.rect.topleft[0])//g.TILE_SIZE, (self.rect.topleft[1])//g.TILE_SIZE

    def _set_pos(self, value):
        self.rect.topleft = value[0]*g.TILE_SIZE, value[1]*g.TILE_SIZE
        self.depth = self.rect.center[1]

    pos = property(_get_pos, _set_pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Entity(pygame.sprite.Sprite):
    def __init__(self, handle, level, pos, tileset, animated = False, animTime = 200):
        pygame.sprite.Sprite.__init__(self)

        self.handle = handle
        self.tileset = tileset
        self.animations = {}
        self.create_animation('default', [(0,0)])

        self.facing = g.Dir.DOWN
        
        self.animated = animated
        self.animTime = animTime
        self.curTime = 0
        self.curFrame = 0
        self.curAnim = 'default'

        self.image = None
        self.set_anim(self.curAnim, True)
        self.rect = self.image.get_rect()

        self.pos = pos

        self.level = level
        self.controller = self.level.controller

    def _get_pos(self):
        return (self.rect.topleft[0])//g.TILE_SIZE, (self.rect.topleft[1])//g.TILE_SIZE

    def _set_pos(self, value):
        self.rect.topleft = value[0]*g.TILE_SIZE, value[1]*g.TILE_SIZE
        self.depth = self.rect.center[1]

    pos = property(_get_pos, _set_pos)

    def pos_to_xy(self):
        x = self.pos[0] * g.TILE_SIZE
        y = self.pos[1] * g.TILE_SIZE
        return (x,y)

    def create_animation(self, key, framelist):
        framecount = len(framelist)
        frames = []
        for i in range(0, framecount):
            row = framelist[i][0]
            col = framelist[i][1]
            frames.append(self.tileset[row][col])
        self.animations[key] = frames

    def set_anim(self, key, reset = False):
        lastAnim = self.curAnim
        if (self.curAnim != key or reset):
            self.curAnim = key
            self.curFrame = 0
            self.curTime = 0
            try:
                self.image = self.animations[self.curAnim][self.curFrame]
            except KeyError:
                self.curAnim = lastAnim
                self.image = self.animations[self.curAnim][self.curFrame]
                utility.log("ERROR: tried to set a non-existent animation. Reverting to the previous animation", g.LogLevel.ERROR)

    def animate(self, dt):
        if (self.animated):
            self.curTime += dt;
            if (self.curTime > self.animTime):
                self.curFrame += 1
                if (self.curFrame >= len(self.animations[self.curAnim])):
                    self.curFrame = 0
                self.image = self.animations[self.curAnim][self.curFrame]
                self.curTime = 0

    def update(self, dt, keys):
        self.animate(dt)

    def draw(self, surface):
        if (self.rect.topleft[0] >= self.level.viewport.topleft[0] - 16 and
            self.rect.topright[0] <= self.level.viewport.topright[0] + 16 and
            self.rect.topleft[1] >= self.level.viewport.topleft[1] - 16 and
            self.rect.bottomright[1] <= self.level.viewport.bottomright[1] + 16):

            surface.blit(self.image, utility.add_tuple(self.rect.topleft, (-4, -20)))

    def interact(self):
        utility.log("test")

class Actor(Entity):
    def __init__(self, handle, level, pos, tileset, animated, animTime = 200):
        Entity.__init__(self, handle, level, pos, tileset, animated, animTime)

        self.create_animation('up', [(1,0), (0,0), (1,0), (2,0)])
        self.create_animation('right', [(1,1), (0,1), (1,1), (2,1)])
        self.create_animation('down', [(1,2), (0,2), (1,2), (2,2)])
        self.create_animation('left', [(1,3), (0,3), (1,3), (2,3)])

        self.curAnim = 'down'
        self.set_anim(self.curAnim, True)
        self.rect = self.image.get_rect()

        self.warp(pos[0], pos[1])
        self.tPos = (0,0)
        self.set_move_target(pos[0], pos[1])
        self.moveSpeed = 2
        self.moving = False
        self.moveSuccess = False

    def set_move_target(self, tx, ty):
        tx *= g.TILE_SIZE
        ty *= g.TILE_SIZE
        self.tPos = (tx, ty)

    def set_move_target_rel(self, tx, ty):
        tx = self.pos[0] * g.TILE_SIZE + tx * g.TILE_SIZE
        ty = self.pos[1] * g.TILE_SIZE + ty * g.TILE_SIZE
        self.tPos = (tx, ty)

    def get_pos_rel(self, dx, dy):
        tx = dx - self.pos[0]
        ty = dy - self.pos[1]
        return (tx, ty)

    def warp(self, dx, dy):
        self.rect.move_ip(dx*g.TILE_SIZE, dy*g.TILE_SIZE)
        self.depth = self.rect.midbottom[1]

    def try_move(self, direction):
        self.set_anim(direction)
        self.moving = True
        if (direction == 'up'):
            if not (self.level.is_blocking(self.pos[0], self.pos[1]-1)):
                self.moveSuccess = True
                self.set_move_target_rel(0,-1)
        elif (direction == 'left'):
            if not (self.level.is_blocking(self.pos[0]-1, self.pos[1])):
                self.moveSuccess = True
                self.set_move_target_rel(-1,0)
        elif (direction == 'down'):
            if not (self.level.is_blocking(self.pos[0], self.pos[1]+1)):
                self.moveSuccess = True
                self.set_move_target_rel(0,1)
        elif (direction == 'right'):
            if not (self.level.is_blocking(self.pos[0]+1, self.pos[1])):
                self.moveSuccess = True
                self.set_move_target_rel(1,0)

    def face_player(self):
        playerPos = self.level.entities["player"].pos
        dX = playerPos[0] - self.pos[0]
        dY = playerPos[1] - self.pos[1]
        if ((dX,dY) == g.Dir.LEFT):
            self.set_anim("left", True)
        elif ((dX,dY) == g.Dir.RIGHT):
            self.set_anim("right", True)
        elif ((dX,dY) == g.Dir.UP):
            self.set_anim("up", True)
        elif ((dX,dY) == g.Dir.DOWN):
            self.set_anim("down", True)

    def process_movement(self):
        x, y = self.rect.topleft
        tx, ty = self.tPos
        if (x < tx):
            self.rect.move_ip(self.moveSpeed, 0)
        elif (x > tx):
            self.rect.move_ip(-self.moveSpeed, 0)
        elif (y < ty):
            self.rect.move_ip(0, self.moveSpeed)
        elif (y > ty):
            self.rect.move_ip(0, -self.moveSpeed)
        elif self.moving:
            self.moving = False
            if self.moveSuccess:
                self.on_step()
                self.moveSuccess = False

    def on_step(self):
        utility.log("Actor move complete")

    def update(self, dt, keys):
        Entity.update(self, dt, keys)
        self.process_movement()
        
class Player(Actor):
    def __init__(self, handle, level, pos, tileset, animated, animTime = 200):
        Actor.__init__(self, handle, level, pos, tileset, animated, animTime)
        g.inputTimer = -1
        self.resetConfirm = False
    
    def process_input(self, keys):
        if (g.inputTimer > 0):
            g.inputTimer -= self.controller.clock.get_time()
        mDir = ""
        if not self.moving and not self.controller.BC:
            if keys[g.keyDown]:
                mDir = "down"
                self.facing = g.Dir.DOWN
            elif keys[g.keyUp]:
                mDir = "up"
                self.facing = g.Dir.UP
            elif keys[g.keyLeft]:
                mDir = "left"
                self.facing = g.Dir.LEFT
            elif keys[g.keyRight]:
                mDir = "right"
                self.facing = g.Dir.RIGHT
            if keys[g.keyMenu]:
                if (g.inputTimer <= 0 and not self.resetConfirm):
                    self.controller.open_menu()
            if keys[g.keyConfirm]:
                if (g.inputTimer <= 0 and not self.resetConfirm):
                    self.try_interact()
                    g.inputTimer = g.INPUT_DELAY
                    self.resetConfirm = True
            elif (g.inputTimer <= 0):
                    self.resetConfirm = False
            if (mDir != ""):
                self.set_anim(mDir, False)
                self.try_move(mDir)

    def on_step(self):
        g.stepCounter += 1
        g.moonStepCounter -= 1
        if g.moonStepCounter < 0:
            g.moonStepCounter = g.MOON_COUNTER_MAX
            g.meter[g.SkillType.MOON] += 1
            if g.meter[g.SkillType.MOON] > g.METER_MAX:
                g.meter[g.SkillType.MOON] = 0
        self.level.check_random_battle()

    def try_interact(self):
        tX = self.pos[0] + self.facing[0]
        tY = self.pos[1] + self.facing[1]
        for ent in self.level.entities:
            if (self.level.entities[ent].pos == (tX, tY)):
                self.level.entities[ent].interact()
        
    def update(self, dt, keys):
        Actor.update(self, dt, keys)
        self.process_input(keys)

###Define specific entities
class Actor001 (Actor):

    def __init__(self, handle, level, pos, tileset, animated, animTime = 200):
        Actor.__init__(self, handle, level, pos, tileset, animated, animTime)
        self.talk01 = False
        self.talk02 = False
    
    
    def interact(self):
        self.face_player()
        
        if (self.talk01 == False):
            self.talk01 = True
            string = "Don't mind &iPotion me. I'm just chilling here."
        elif (self.talk02 == False):
            self.talk02 = True
            string = "Oh, it's you again."
        else:
            string = "This is the &iSalts beginning of some &iSword2 really long &iSword dialogue. Great dialogue! But, like, &iAntidote really long dialogue. You know? Isn't dialogue great? Isn't this dialogue great? I think this dialogue is excellent. Really excellent. 1 2 3 4 5 6 7 8 9 0 20 300 4000 50000 600000 7000000 80000000 900000000 10000000000"
            
        self.controller.TM.create_text_box(string)

class Actor002 (Actor):
    
    def interact(self):
        self.face_player()
        self.controller.start_battle(["Slime"], -1, False)

ENTITY_DIC = {}
ENTITY_DIC["actor001"] = Actor001
ENTITY_DIC["actor002"] = Actor002
