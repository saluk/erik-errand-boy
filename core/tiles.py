import random

import pygame
from tiledtmxloader import tmxreader
from agents import Agent
from items import Item

class Tile(Agent):
    def init(self):
        self.col = None    #full,top,bottom,left,right
    def is_empty(self):
        return self.index==-1
    def draw(self,engine,offset):
        super(Tile,self).draw(engine,offset)
        if hasattr(self,"chest"):
            s = pygame.Surface([32,32])
            s.fill([255,255,255])
            s.set_alpha(50)
            engine.surface.blit(s,[self.pos[0]-offset[0],self.pos[1]-offset[1]])
    def collide_point(self,point,flags=None):
        if not self.col:
            return
        top = self.pos[1]
        left = self.pos[0]
        right = self.pos[0]+31
        bottom = self.pos[1]+31
        if self.col == "top":
            bottom-=16
        if self.col == "left":
            right-=16
        if self.col == "right":
            left+=16
        if self.col == "bottom":
            top+=16
        if point[0]>=left and point[0]<=right and point[1]>=top and point[1]<=bottom:
            return self
            
class Frober(Agent):
    def init_properties(self):
        if hasattr(self,"chest"):
            self.items = []
            if not self.chest:
                names = Item.names[:]
                random.sort(names)
                names = names[:4]
            else:
                names = self.chest.split(",")
            for name in names:
                item = Item()
                item.name = name
                self.items.append(item)
    def frobme(self,actor):
        if hasattr(self,"chest"):
            self.frob_chest(actor)
        if hasattr(self,"sign"):
            self.frob_sign(actor)
    def frob_chest(self,actor):
        if actor.menu:
            options = []
            for i in self.items:
                options.append( (i.name,self.action_pickitem,(actor,i)) )
            actor.menu.setup(options)
    def frob_sign(self,actor):
        actor.say(self.sign)
    def action_pickitem(self,actor,item):
        actor.items.append(item)
        self.items.remove(item)
    def collide_point(self,point,flags=None):
        if point[0]>=self.pos[0] and point[0]<=self.right and point[1]>=self.pos[1] and point[1]<=self.bottom:
            return self
        
class TileLayer(Agent):
    def init(self):
        self.tiles = []
    def draw(self,engine,offset):
        for row in self.tiles:
            for tile in row:
                tile.draw(engine,offset)

class TileMap(Agent):
    def load(self,map):
        self.mapfile = map
        self.raw_map = tmxreader.TileMapParser().parse_decode(self.mapfile)

        self.tileset_list = [None]
        self.tile_properties = {}
        self.regions = {}
        self.warps = []
        self.frobers = []
        self.destinations = {}
        for tileset_raw in self.raw_map.tile_sets:
            props = {}
            for tile in tileset_raw.tiles:
                props[tile.id] = tile.properties
            tileset = pygame.image.load(tileset_raw.images[0].source).convert_alpha()
            x = 0
            y = 0
            i = 0
            while y*32<tileset.get_height():
                self.tileset_list.append(tileset.subsurface([[x*32,y*32],[32,32]]))
                if str(i) in props:
                    self.tile_properties[len(self.tileset_list)-1] = props[str(i)]
                i += 1
                x+=1
                if x*32>=tileset.get_width():
                    x=0
                    y+=1

        self.map = []
        for layer in self.raw_map.layers:
            if hasattr(layer,"decoded_content"):
                self.read_tile_layer(layer)
            else:
                self.read_object_layer(layer)
        self.collisions = self.map[-1].tiles
        del self.map[-1]
        self.map_width = len(self.map[0].tiles[0])
        self.map_height = len(self.map[0].tiles)
    def read_tile_layer(self,layer):
        maplayer = TileLayer()
        maplayer.layer = len(self.map)
        x=y=0
        row = []
        for ti in layer.decoded_content:
            tile = Tile()
            tile.index = ti
            tile.surface = self.tileset_list[tile.index]
            tile.pos = [x*32,y*32]
            for k,v in self.tile_properties.get(ti,{}).items():
                setattr(tile,k,v)
            row.append(tile)
            x+=1
            if x>=layer.width:
                x=0
                y+=1
                maplayer.tiles.append(row)
                row = []
        self.map.append(maplayer)
    def read_object_layer(self,layer):
        for o in layer.objects:
            r = pygame.Rect([[int(o.x),int(o.y)],[int(o.width),int(o.height)]])
            if o.name=="spawn":
                self.regions["spawn"] = r
            elif o.name=="playerspawn":
                self.regions["playerspawn"] = r
            elif "warp" in o.properties:
                map,target = o.properties["warp"].split("_")
                self.warps.append({"rect":r,"map":map,"warptarget":target})
            elif "destination" in o.properties:
                self.destinations[o.properties["destination"]] = r
            elif "chest" in o.properties or "sign" in o.properties:
                f = Frober()
                f.pos = [r.left,r.top]
                f.right,f.bottom = r.right,r.bottom
                for p in o.properties:
                    setattr(f,p,o.properties[p])
                f.init_properties()
                self.frobers.append(f)
    def collide(self,agent,flags=None):
        r = agent.rect()
        for point in ([r.left,r.top],[r.right,r.top],[r.left,r.bottom],[r.right,r.bottom]):
            col = self.collide_point(point,flags)
            if col:
                return col
    def collide_point(self,point,flags=None):
            x,y = [i//32 for i in point]
            if x<0 or y<0 or x>=self.map_width or y>=self.map_height:
                return Tile()
            col = 0
            if flags=="move":
                tile = self.collisions[y][x].collide_point(point,flags)
                if tile:
                    return tile
                for warp in self.warps:
                    r = warp["rect"]
                    if point[0]>=r.left and point[0]<=r.right and point[1]>=r.top and point[1]<=r.bottom:
                        return warp
            if flags=="frobme":
                for frober in self.frobers:
                    if frober.collide_point(point,flags):
                        return frober
    def get_sprites(self):
        return [layer for layer in self.map]