import pygame
from state_machine import StateMachine
from states import *
from constants import SCALE_FACTOR, SCREEN_VIRTUAL_WIDTH,SCREEN_VIRTUAL_HEIGHT
from game_objects import Background


pygame.init()
class Game: 
    def __init__(self):
        self.WINDOW_WIDTH = SCREEN_VIRTUAL_WIDTH * SCALE_FACTOR
        self.WINDOW_HEIGHT = SCREEN_VIRTUAL_HEIGHT * SCALE_FACTOR
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH,self.WINDOW_HEIGHT))
        pygame.display.set_caption("Block Crush")
        self.clock = pygame.time.Clock()
        self.FPS  = 20
        
        
        # game play
        self.state_machine = StateMachine(
            {
                'play': PlayState,
                'title': TitleState,
                'gameover': GameOverState
            },
            self.screen
        )
        self.state_machine.change("title")
        self.game_play = True

        # music
        self.game_music = pygame.mixer.music.load("sounds/music3.mp3")
        
        # needed image assets
        self.background_image = pygame.image.load("assets/background.png")
        self.background = Background(self.screen,self.background_image,0,0)
    
    def game(self):
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        while self.game_play:
            self.background.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_play = False
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                    self.state_machine.key_event(event.key)
                if event.type == pygame.KEYUP:
                    self.state_machine.key_up_event(event.key)

            self.background.logic()
            self.state_machine.render()
            self.state_machine.logic()

            pygame.display.flip()
            self.clock.tick(self.FPS)

game = Game()
game.game()