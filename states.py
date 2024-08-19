import pygame
import random
from constants import SCALE_FACTOR
from game_objects import *
from utils import *
class BaseState:
    """
    Abstract state class for all state
    """
    def __init__(self, state_machine,screen:"pygame.Surface"):
        self.state_machine = state_machine
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
    
    def enter(self):
        pass
    def exit(self):
        pass
    def key_up_event(self,key):
        pass
    def key_event(self,key):
        raise NotImplementedError("Key Event method must be implement")
    def render(self):
        raise NotImplementedError("Render method must be implement")
    def logic(self):
        raise NotImplementedError("Logic method must be implemented")

class TitleState(BaseState):
    def enter(self):
        self.block_spritesheet = SpriteSheet("assets/match3.png", (0,0), (384,288),32,32)
        self.blocks_objects = self.block_spritesheet.get_sprites().copy()
        random.shuffle(self.blocks_objects)
        board_offset_x =  (self.screen_width/2) - (BLOCK_WIDTH * 4)
        self.board = Board(self.screen, 8,8, self.blocks_objects, self,board_offset_x, 10 * SCALE_FACTOR)
        self.titleFont = pygame.font.Font("fonts/font.ttf",30 * round(SCALE_FACTOR))
        self.optionFont = pygame.font.Font("fonts/font.ttf",25 * round(SCALE_FACTOR))
        self.currentCursor = 1
        self.activeColor = (11, 101, 147)
        self.text_color = (5, 82, 61)
        self.option_color = (4, 39, 91)
        self.selectSound = pygame.mixer.Sound("sounds/select.wav")
        self.startSound = pygame.mixer.Sound("sounds/start.wav")
        self.selectSound.set_volume(0.5)
        self.startSound.set_volume(0.5)
        self.timer = 0
    def key_event(self, key):
        if key == pygame.K_RETURN:
            self.startSound.play()
            if self.currentCursor == 1:
                self.state_machine.change("play")
            elif self.currentCursor == 2:
                pygame.quit()
                quit()
        elif key == pygame.K_UP:
            self.currentCursor -= 1
            if self.currentCursor < 1:
                self.currentCursor = 2
            self.selectSound.play()
               
        elif key == pygame.K_DOWN:
            self.currentCursor += 1
            if self.currentCursor > 2:
                self.currentCursor = 1
            self.selectSound.play()
    def render(self):
        self.board.render()
        transparent_surface = pygame.Surface((self.screen_width,self.screen_height), pygame.SRCALPHA)
        box_width = 170 * SCALE_FACTOR
        box_height = 170 * SCALE_FACTOR
        box_posx = self.screen_width / 2 - box_width /2
        box_posy = self.screen_height /2 - box_height /2
        pygame.draw.rect(transparent_surface,(0,0,0,128),(0,0,self.screen_width,self.screen_height))
        pygame.draw.rect(transparent_surface,(243, 244, 232, 128), 
                         (box_posx, box_posy, box_width, box_height),
                           border_radius= round(15 * SCALE_FACTOR))
        self.screen.blit(transparent_surface,(0,0))
        
        # Title Text Print
        title = self.titleFont.render("BLOCK CRUSH", 1, self.text_color)
        title_rect = title.get_rect()
        title_rect.centerx = (box_posx + (box_posx + box_width))/2
        title_rect.centery = (box_posy) + 20 * SCALE_FACTOR
        self.screen.blit(title, title_rect)

        # Options Text Print
        start_option = self.optionFont.render("Start",1,self.activeColor if self.currentCursor == 1 else self.option_color)
        quit_option = self.optionFont.render("Quit",1,self.activeColor if self.currentCursor == 2 else self.option_color)
        start_option_rect = start_option.get_rect()
        quit_option_rect = quit_option.get_rect()
        
        start_option_rect.center = ((box_posx + (box_posx + box_width))/2, box_posy + (box_height - 40 * SCALE_FACTOR))
        quit_option_rect.center = ((box_posx + (box_posx + box_width))/2, box_posy + (box_height - 20 * SCALE_FACTOR ))
        self.screen.blit(start_option,start_option_rect)
        self.screen.blit(quit_option,quit_option_rect)


    def logic(self):
        self.timer += 0.1
        if self.timer >= 1:
            self.text_color = (random.randint(0,255), random.randrange(255), random.randrange(255))
            self.timer = 0
        

class PlayState(BaseState):
    def __init__(self, state_machine, screen, **kwargs):
        super().__init__(state_machine, screen)
    def enter(self):
        self.score = 0
        self.level = 1
        self.goal = 1450
        self.countdown_timer = 60

        self.block_spritesheet = SpriteSheet("assets/match3.png", (0,0), (384,288),32,32)
        self.blocks_objects = self.block_spritesheet.get_sprites().copy()
        random.shuffle(self.blocks_objects)
        self.grid_x = 8
        self.grid_y = 8
        self.board = Board(self.screen, self.grid_x,self.grid_y, self.blocks_objects, state = self)

        # sounds
        self.move_sound = pygame.mixer.Sound("sounds/select.wav")
        self.select_sound = pygame.mixer.Sound("sounds/start.wav")
        self.error_sound = pygame.mixer.Sound("sounds/error.wav")
        self.clock_sound = pygame.mixer.Sound("sounds/clock.wav")
        self.gameover_sound = pygame.mixer.Sound("sounds/game-over.wav")
        self.move_sound.set_volume(0.5)
        self.select_sound.set_volume(0.5)
        self.error_sound.set_volume(0.5)
        self.clock_sound.set_volume(0.5)
        self.gameover_sound.set_volume(0.5)
        
        # Fonts
        self.bigFont = pygame.font.Font("fonts/font.ttf",30 * round(SCALE_FACTOR))
        self.smallFont = pygame.font.Font("fonts/font.ttf",25 * round(SCALE_FACTOR))

        # for the pointer
        self.pointer = Pointer(self.screen,0,0)

        # For COuntdown Timer
        self.counter = Timer()
        self.counter.countdown(self.countdown_timer)

        # Game play
        self.current_selected_grid = None
    def key_event(self, key):
        if key == pygame.K_RETURN:
            if self.current_selected_grid:
                self.swap_block()
            else:
                self.current_selected_grid = (self.pointer.grid_x, self.pointer.grid_y)
            
        if key == pygame.K_RIGHT:
            if self.pointer.grid_x < self.grid_x - 1:
                self.pointer.grid_x += 1
                self.move_sound.play()
            else:
                self.error_sound.play()
        elif key == pygame.K_LEFT:
            if self.pointer.grid_x > 0:
                self.pointer.grid_x -= 1
                self.move_sound.play()
            else:
                self.error_sound.play()
        elif key == pygame.K_UP:
            if self.pointer.grid_y > 0:
                self.pointer.grid_y -= 1
                self.move_sound.play()
            else:
                self.error_sound.play()
        elif key == pygame.K_DOWN:
            if self.pointer.grid_y < self.grid_y - 1:
                self.pointer.grid_y += 1
                self.move_sound.play()
            else:
                self.error_sound.play()

    def key_up_event(self, key):
        pass
    def swap_block(self):
        if self.current_selected_grid:
            new_grid = self.pointer.grid_x, self.pointer.grid_y
            # To check whether the new grid is adjacent to the current selected grid - checker_point
            checker_point = (self.current_selected_grid[0] - new_grid[0]) - (self.current_selected_grid[1] - new_grid[1])
            if checker_point == 1 or checker_point == 0 or checker_point == -1: # Adjacent Check
                currentBlock = self.board.board[self.current_selected_grid[1]][self.current_selected_grid[0]]
                currentGridX = currentBlock.grid_x
                currentGridY = currentBlock.grid_y
                self.board.board[self.current_selected_grid[1]][self.current_selected_grid[0]] = self.board.board[new_grid[1]][new_grid[0]]
                self.board.board[self.current_selected_grid[1]][self.current_selected_grid[0]].grid_x = currentGridX
                self.board.board[self.current_selected_grid[1]][self.current_selected_grid[0]].grid_y = currentGridY
                self.board.board[new_grid[1]][new_grid[0]] = currentBlock
                self.board.board[new_grid[1]][new_grid[0]].grid_x = new_grid[0]
                self.board.board[new_grid[1]][new_grid[0]].grid_y = new_grid[1]
                self.select_sound.play()
                self.current_selected_grid = None
            else:
                self.error_sound.play()
    def display_highlighted_block(self):
        if self.current_selected_grid and type(self.current_selected_grid) == tuple and len(self.current_selected_grid) == 2:
            transparent_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            block_rect_x = (self.current_selected_grid[0] * BLOCK_WIDTH) + BOARD_OFFSET_X
            block_rect_y = (self.current_selected_grid[1] * BLOCK_HEIGHT) + BOARD_OFFSET_Y
            pygame.draw.rect(transparent_surface, (255,255,255,128),(block_rect_x, block_rect_y, BLOCK_WIDTH, BLOCK_HEIGHT), 
                            border_radius=round(5 * SCALE_FACTOR))
            self.screen.blit(transparent_surface, (0, 0))

    def display_side_info(self):
        """
        What will the displayed
        - Container *
        - Score
        - Goal
        - Countdown
        - Level
        """
        # For Container
        box_x = 20 * SCALE_FACTOR
        box_y = BOARD_OFFSET_Y
        box_width = 200 * SCALE_FACTOR
        box_height = 150 * SCALE_FACTOR
        text_color = (255,255,255)
        transparent_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(transparent_surface,
                            (25, 138, 213, 150),
                              (box_x, box_y, box_width, box_height ), border_radius= round(10 * SCALE_FACTOR))
        # For Score
        score_text = self.smallFont.render(f"Score: {self.score}", 1, text_color)
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (box_x + 10 * SCALE_FACTOR, box_y + 10 * SCALE_FACTOR)
        transparent_surface.blit(score_text, score_text_rect)
        # For Level
        level_text = self.smallFont.render(f"Level: {self.level}", 1, text_color)
        level_text_rect = level_text.get_rect()
        level_text_rect.topleft = (box_x + 10 * SCALE_FACTOR, box_y + 30 * SCALE_FACTOR)
        transparent_surface.blit(level_text, level_text_rect)

        # For Goal
        goal_text = self.smallFont.render(f"Level: {self.goal}", 1, text_color)
        goal_text_rect = goal_text.get_rect()
        goal_text_rect.topleft = (box_x + 10 * SCALE_FACTOR, box_y + 50 * SCALE_FACTOR)
        transparent_surface.blit(goal_text, goal_text_rect)

        # For Countdown
        countdown_text = self.smallFont.render(f"Countdown: {self.countdown_timer}", 1, text_color)
        countdown_text_rect = countdown_text.get_rect()
        countdown_text_rect.topleft = (box_x + 10 * SCALE_FACTOR, box_y + 70 * SCALE_FACTOR)
        transparent_surface.blit(countdown_text, countdown_text_rect)
    
        self.screen.blit(transparent_surface,(0,0))
    def render(self):
        self.board.render()
        self.display_highlighted_block()
        self.pointer.render()
        self.display_side_info()
        
    def logic(self):
        self.pointer.logic()
        self.board.logic()
        self.countdown_timer = self.counter.logic()
        if not self.countdown_timer:
            if self.countdown_timer == 0:
                self.gameover_sound.play()
                self.state_machine.change("gameover",{'score': self.score})
            else:
                self.countdown_timer = 0
            

class GameOverState(BaseState):
    def __init__(self, state_machine, screen: pygame.Surface, **kwargs):
        super().__init__(state_machine, screen)
        self.score = kwargs.get("score")
    def enter(self):
        self.bigFont = pygame.font.Font("fonts/font.ttf",25 * round(SCALE_FACTOR))
        self.smallFont = pygame.font.Font("fonts/font.ttf",15 * round(SCALE_FACTOR))
    def key_event(self, key):
        if key == pygame.K_RETURN:
            self.state_machine.change("title")
    def key_up_event(self, key):
        pass

    def render(self):
        transparent_surface = pygame.Surface((self.screen_width,self.screen_height), pygame.SRCALPHA)
        box_width = 170 * SCALE_FACTOR
        box_height = 170 * SCALE_FACTOR
        box_posx = self.screen_width / 2 - box_width /2
        box_posy = self.screen_height /2 - box_height /2
        pygame.draw.rect(transparent_surface,(0,0,0,128),(0,0,self.screen_width,self.screen_height))
        pygame.draw.rect(transparent_surface,(243, 244, 232, 128), 
                         (box_posx, box_posy, box_width, box_height),
                           border_radius= round(15 * SCALE_FACTOR))
        self.screen.blit(transparent_surface,(0,0))
        
        title = self.bigFont.render("Game Over", 1, (25, 138, 213))
        title_rect = title.get_rect()
        title_rect.centerx = (box_posx + (box_posx + box_width))/2
        title_rect.centery = (box_posy) + 20 * SCALE_FACTOR
        self.screen.blit(title, title_rect)

        start_option = self.bigFont.render(f"Score : {self.score}",1, (25, 138, 213))
        quit_option = self.smallFont.render("Press Enter to Continue",1,(25, 138, 213))
        start_option_rect = start_option.get_rect()
        quit_option_rect = quit_option.get_rect()
        
        start_option_rect.center = ((box_posx + (box_posx + box_width))/2, box_posy + box_height /2 )
        quit_option_rect.center = ((box_posx + (box_posx + box_width))/2, box_posy + (box_height - 20 * SCALE_FACTOR ))
        self.screen.blit(start_option,start_option_rect)
        self.screen.blit(quit_option,quit_option_rect)
        
    def logic(self):
        pass
    