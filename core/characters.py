import pygame

from agents import Agent

class Player(Agent):
    def init(self):
        self.hotspot = [16,32]
        self.facing = [-1,0]
        self.next_frame = 10
        self.animdelay = 5
        self.frame = 0
        self.anim = None
        self.animating = False
        self.walk_speed = 2
        self.vector = [0,0]
        
        self.radius = 14   #collision radius around hotspot
    def load(self,spritesheet):
        super(Player,self).load(spritesheet)
        self.anims = {}
        order = ["down","left","right","up"]
        for y in range(4):
            frames = []
            for x in range(4):
                frames.append(self.graphics.subsurface([[x*32,y*48],[32,48]]))
            self.anims[order[y]] = frames
    def draw(self,engine,offset=[0,0]):
        pygame.draw.circle(engine.surface,[0,0,0,50],[self.pos[0]-offset[0],self.pos[1]-offset[1]+16],6)
        super(Player,self).draw(engine,offset)
        x,y = (self.pos[0])//32*32-offset[0],(self.pos[1])//32*32-offset[1]
        w,h = 32,32
        #pygame.draw.rect(engine.surface,[255,0,255],pygame.Rect([[x,y],[w,h]]))
    def idle(self):
        self.animating = False
        self.vector = [0,0]
    def walk(self):
        moved = False
        col1=col2=None
        if self.vector[0]:
            self.pos[0]+=self.vector[0]*self.walk_speed
            col1 = self.world.collide(self)
            if col1:
                self.pos[0]-=self.vector[0]*self.walk_speed
            else:
                self.facing = [self.vector[0],0]
                moved = True
        if self.vector[1]:
            self.pos[1]+=self.vector[1]*self.walk_speed
            col2 = self.world.collide(self)
            if col2:
                self.pos[1]-=self.vector[1]*self.walk_speed
            else:
                self.facing = [0,self.vector[1]]
                moved = True
        for col in col1,col2:
            if col:
                if isinstance(col,dict):
                    if "warptarget" in col:
                        self.world.change_map(self,col["map"],col["warptarget"])
        if moved:
            self.animating = True
    def left(self):
        self.facing = [-1,0]
        self.vector[0] = -1
    def right(self):
        self.facing = [1,0]
        self.vector[0] = 1
    def up(self):
        self.facing = [0,-1]
        self.vector[1] = -1
    def down(self):
        self.facing = [0,1]
        self.vector[1] = 1
    def set_anim(self,anim):
        self.anim = anim
        self.frame = 0
        self.next_frame = self.animdelay
        self.set_animation_frame()
    def set_animation_frame(self):
        anim = self.anims[self.anim]
        if self.frame>=len(anim):
            self.frame = 0
        self.surface = anim[self.frame]
    def update(self,dt):
        if self.vector[0] or self.vector[1]:
            self.walk()
            
        if self.facing[0]<0:
            anim = "left"
        elif self.facing[0]>0:
            anim = "right"
        elif self.facing[1]<0:
            anim = "up"
        elif self.facing[1]>0:
            anim = "down"
        else:
            anim = self.anim
        if anim!=self.anim:
            self.set_anim(anim)
        if self.animating:
            self.next_frame -= 1
        if self.next_frame<=0:
            self.next_frame = self.animdelay
            self.frame += 1
            self.set_animation_frame()
    def collide(self,agent):
        radius = self.radius
        left,top,right,bottom = self.pos[0]-radius+1,self.pos[1]-radius+1,self.pos[0]+radius-1,self.pos[1]+radius-1
        if agent.pos[0]>=left and agent.pos[0]<=right and agent.pos[1]>=top and agent.pos[1]<=bottom:
            return 1
    def rect(self):
        radius = self.radius
        left,top,right,bottom = self.pos[0]-radius+1,self.pos[1]-radius+1,self.pos[0]+radius-1,self.pos[1]+radius-1
        return pygame.Rect([[left,top],[right-left,bottom-top]])
