#
# controller.py
# not well implemented for expansion
# but, provides a lot of nice base behavior:
# * alt-enter to toggle fullscreen
# * minimise pauses the engine (although the world still needs to check if the engine is paused)
# * un minimise unpauses the engine
# * can resize the window to change the display resolution
# * can quit the game

import pygame

class Controller:
    def __init__(self,engine):
        self.engine = engine
        self.mbdown = 0
        self.mpos = [0,0]
        self.left = 0
        self.right = 0
        self.up = 0
        self.down = 0
    def input(self):
        self.mbdown = 0
        self.action = 0
        self.menu = 0
        engine = self.engine
        pygame.event.pump()
        for e in pygame.event.get():
            if e.type==pygame.ACTIVEEVENT:
                if e.gain==0 and (e.state==6 or e.state==2 or e.state==4):
                    self.engine.pause()
                    continue
                if e.gain==1 and (e.state==6 or e.state==2 or e.state==4):
                    self.engine.unpause()
                    continue
            if e.type==pygame.VIDEORESIZE:
                w,h = e.w,e.h
                engine.swidth = w
                engine.sheight = h
                engine.make_screen()
                continue
            if e.type == pygame.QUIT:
                self.engine.stop()
                continue
            if e.type==pygame.KEYDOWN and\
                e.key==pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
                engine.fullscreen = 1-engine.fullscreen
                engine.make_screen()
                continue
            if e.type==pygame.KEYDOWN and\
                e.key==pygame.K_F12:
                pygame.image.save(engine.window,"screen.jpg")
                continue
            self.handle_pygame_event(e)
        if engine.world:
            engine.world.input(self)
    def handle_pygame_event(self,e):
        """Ideally, build this out with state so that the world
        can make a query like controller.enter_was_pressed or key_held_for(3)"""
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.mbdown = 1
            self.mpos = e.pos
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT:
                self.left = 1
            elif e.key == pygame.K_RIGHT:
                self.right = 1
            if e.key == pygame.K_UP:
                self.up = 1
            elif e.key == pygame.K_DOWN:
                self.down = 1
            if e.key == pygame.K_z:
                self.action = 1
            if e.key == pygame.K_x:
                self.menu = 1
        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_LEFT:
                self.left = 0
            elif e.key == pygame.K_RIGHT:
                self.right = 0
            if e.key == pygame.K_UP:
                self.up = 0
            elif e.key == pygame.K_DOWN:
                self.down = 0
            elif e.key == pygame.K_x:
                self.menu = 0