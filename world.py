import configparser
import pygame
import pygame.locals
import my_globals as g
import database as db
import battle
import utility

DIR_DOWN = (0, 1)
DIR_RIGHT = (1, 0)
DIR_LEFT = (-1, 0)
DIR_UP = (0, -1)

class Level(object):

    def __init__(self, viewport, control):
        self.rect = pygame.Rect(0,0, 1,1)
        self.image = None
        self.viewport = viewport
        #self.player = player
        self.CONTROLLER = control
        self.TEXT_MANAGER = self.CONTROLLER.TEXT_MANAGER
        self.entities = {}
    
    def load_file(self, filename="lvl/level.map"):
        self.map = []
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.tileset = parser.get("level", "tileset")
        self.map = parser.get("level", "map").split("\n")
        for section in parser.sections():
            if (len(section)) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.MAP_CACHE = utility.TileCache(g.TILE_SIZE)
        self.sprites = {}
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if not self.is_wall(x, y) and 'sprite' in self.key[c]:
                    self.sprites[(x, y)] = self.key[c]
                if 'entity' in self.key[c]:
                    self.add_entity(ENTITY_DIC[self.key[c]['entity']](self.key[c]['name'], self, (x,y), self.MAP_CACHE['spr/red.png'], False))
        #render the static BG once
        self.render()

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
        #run update() for all entites, then center the viewport
        for ent in self.entities:
            self.entities[ent].update(dt, keys)
        self.update_viewport()

    def add_entity(self, entity):
        try:
            if (self.entities[entity.handle] != entity):
                utility.log("ERROR: An entity with handle '" + handle + "' already exists in this level", g.LogLevel.ERROR)
            else:
                utility.log("ERROR: This entity already exists in this level", g.LogLevel.ERROR)
        except KeyError:
            self.entities[entity.handle] = entity

    def render(self):
        wall = self.is_wall
        tiles = self.MAP_CACHE[self.tileset]
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
        for ent in self.entities:
            self.entities[ent].draw(new_image)
        surface.blit(new_image, (0,0), self.viewport)

class Entity(pygame.sprite.Sprite):
    def __init__(self, handle, level, pos, tileset, animated = False, animTime = 200):
        pygame.sprite.Sprite.__init__(self)
        
        self.handle = handle
        self.tileset = tileset
        self.animations = {}
        self.create_animation('default', [(0,0)])

        self.facing = DIR_DOWN
        
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
                utility.log("ERROR: tried to set a non-existant animation. Reverting to the previous animation", g.LogLevel.ERROR)

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
        surface.blit(self.image, self.rect)

    def interact(self):
        utility.log("test")

class Actor(Entity):
    def __init__(self, handle, level, pos, tileset, animated, animTime = 200):
        Entity.__init__(self, handle, level, pos, tileset, animated, animTime)
        
        self.create_animation('down', [(1,0), (0,0), (1,0), (2,0)])
        self.create_animation('up', [(1,1), (0,1), (1,1), (2,1)])
        self.create_animation('left', [(1,2), (0,2), (1,2), (2,2)])
        self.create_animation('right', [(1,3), (0,3), (1,3), (2,3)])

        self.curAnim = 'down'
        self.set_anim(self.curAnim, True)
        self.rect = self.image.get_rect()

        self.warp(pos[0], pos[1])
        self.tPos = (0,0)
        self.set_move_target(pos[0], pos[1])
        self.moveSpeed = 2
        self.moving = False

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
                self.set_move_target_rel(0,-1)
        elif (direction == 'left'):
            if not (self.level.is_blocking(self.pos[0]-1, self.pos[1])):
                self.set_move_target_rel(-1,0)
        elif (direction == 'down'):
            if not (self.level.is_blocking(self.pos[0], self.pos[1]+1)):
                self.set_move_target_rel(0,1)
        elif (direction == 'right'):
            if not (self.level.is_blocking(self.pos[0]+1, self.pos[1])):
                self.set_move_target_rel(1,0)

    def face_player(self):
        playerPos = self.level.entities["player"].pos
        dX = playerPos[0] - self.pos[0]
        dY = playerPos[1] - self.pos[1]
        if ((dX,dY) == DIR_LEFT):
            self.set_anim("left", True)
        elif ((dX,dY) == DIR_RIGHT):
            self.set_anim("right", True)
        elif ((dX,dY) == DIR_UP):
            self.set_anim("up", True)
        elif ((dX,dY) == DIR_DOWN):
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
        else:
            self.moving = False

    def update(self, dt, keys):
        Entity.update(self, dt, keys)
        self.process_movement()
        
class Player(Actor):
    def __init__(self, handle, level, pos, tileset, animated, animTime = 200):
        Actor.__init__(self, handle, level, pos, tileset, animated, animTime)
        g.INPUT_TIMER = -1
        self.resetConfirm = False
    
    def process_input(self, keys):
        if (g.INPUT_TIMER > 0):
            g.INPUT_TIMER -= self.level.CONTROLLER.CLOCK.get_time()
        mDir = ""
        if not self.moving:
            if keys[g.KEY_DOWN]:
                mDir = "down"
                self.facing = DIR_DOWN
            elif keys[g.KEY_UP]:
                mDir = "up"
                self.facing = DIR_UP
            elif keys[g.KEY_LEFT]:
                mDir = "left"
                self.facing = DIR_LEFT
            elif keys[g.KEY_RIGHT]:
                mDir = "right"
                self.facing = DIR_RIGHT
            if keys[g.KEY_CONFIRM]:
                if (g.INPUT_TIMER <= 0 and not self.resetConfirm):
                    self.try_interact()
                    g.INPUT_TIMER = g.INPUT_DELAY
                    self.resetConfirm = True
            elif (g.INPUT_TIMER <= 0):
                    self.resetConfirm = False
            if (mDir != ""):
                self.set_anim(mDir, False)
                self.try_move(mDir)

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
            string = "Don't mind me. I'm just chilling here."
        elif (self.talk02 == False):
            self.talk02 = True
            string = "Oh, it's you again."
        else:
            string = "This is the beginning of some really long diaglogue. Great dialogue! But, like, really long dialogue. You know? Isn't dialogue great? Isn't this dialogue great? I think this dialogue is excellent. Really exccellent. 1 2 3 4 5 6 7 8 9 0 20 300 4000 50000 600000 7000000 80000000 900000000 10000000000"
            
        self.level.TEXT_MANAGER.create_text_box(string)

class Actor002 (Actor):
    
    def interact(self):
        self.face_player()
        self.level.CONTROLLER.start_battle(["Slime", "Mold", "Slime"])

ENTITY_DIC = {}
ENTITY_DIC["actor001"] = Actor001
ENTITY_DIC["actor002"] = Actor002
