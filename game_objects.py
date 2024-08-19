import random
import pygame
from constants import BOARD_OFFSET_X, BOARD_OFFSET_Y, SCALE_FACTOR, BLOCK_WIDTH, BLOCK_HEIGHT


class GameObject:
    def __init__(self,screen:"pygame.Surface"):
        self.screen = screen
    def render(self):
        pass
    def logic(self):
        pass
    def collide(self,rect):
        pass

class Background(GameObject):
    def __init__(self, screen, image, posx = 0, posy = 0):
        super().__init__(screen)
        self.BACKGROUND_SCROLL_SPEED = 5 * SCALE_FACTOR
        self.BACKGROUND_LOOPING_POINT = 413 * SCALE_FACTOR
        self.scrolling = True
        self.background_x = posx
        self.background_y = posy
        self.image = image
    def render(self):
        image = pygame.transform.scale_by(self.image, SCALE_FACTOR)
        self.screen.blit(image,(-self.background_x,self.background_y))
    def logic(self):
        if self.scrolling:
            self.background_x = (self.background_x + self.BACKGROUND_SCROLL_SPEED) % self.BACKGROUND_LOOPING_POINT


class Block(GameObject):
    def __init__(self, screen, grid_x, grid_y, object):
        super().__init__(screen)
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.object = object
        self.image  = self.object["image"]
        self.rect = self.image.get_rect()
        self.color = self.object["color"]
        self.pattern = self.object["pattern"]
    def __str__(self):
        return f"<Block ({self.grid_y},{self.grid_x}) />"
    def __repr__(self):
        return f"<Block ({self.grid_y},{self.grid_x}) />"
    


class Board(GameObject):
    def __init__(self,screen, grid_x, grid_y, block_images, state, offset_x = BOARD_OFFSET_X, offset_y = BOARD_OFFSET_Y):
        super().__init__(screen)
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.block_images = block_images
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.state = state
        self.board = self.generate_board()
        while self.check_color_matches():
            self.board = self.generate_board()
        self.match_sound  = pygame.mixer.Sound("sounds/match.wav")
        self.match_sound.set_volume(0.5)
    def generate_board(self):
        board = []
        for y in range(self.grid_y):
            new_y  = []
            for x in range(self.grid_x):
                new_sprite = random.choice(self.block_images)
                new_y.append(
                    Block(
                        self.screen,
                        x,
                        y,
                        new_sprite
                    )
                )
            board.append(new_y)
        return board
    def check_color_matches(self):
        ## Horizontal Matches
        matches = []
        for y in range(self.grid_y):
            match_number = 1
            color_to_match = self.board[y][0].color
            for x in range(1, self.grid_x):
                if color_to_match == self.board[y][x].color:
                    match_number += 1
                else:
                    color_to_match = self.board[y][x].color
                    if match_number >= 3:
                        match = []
                        for idx in range(x - 1, x - (match_number + 1) ,-1):
                            match.append(self.board[y][idx])
                        matches.append(match.copy())
                    
                    match_number = 1
                    if x >= self.grid_x - 2:
                        break
            if match_number >= 3:
                match = []
                for idx in range( x - 1, x - (match_number + 1) ,-1):
                    match.append(self.board[y][idx])
                matches.append(match.copy())
        ## Vertical Matches
        for x in range(self.grid_x):
            match_number = 1
            color_to_match = self.board[0][x].color
            for y in range(1, self.grid_y):
                if color_to_match == self.board[y][x].color:
                    match_number += 1
                else:
                    color_to_match = self.board[y][x].color
                    if match_number >= 3:
                        match = []
                        for idx in range(y - 1 , y - (match_number + 1) ,-1):
                            match.append(self.board[idx][x])
                        matches.append(match.copy())
                    match_number = 1
                    if y >= self.grid_y - 2:
                        break
            if match_number >= 3:
                match = []
                for idx in range(y - 1 , y - (match_number + 1) ,-1):
                    match.append(self.board[idx][x])
                matches.append(match.copy())
        return matches
    def remove_matches(self, matches):
        for match in matches:
            for block in match:
                self.board[block.grid_y][block.grid_x] = None
                
    def fall_blocks(self):
        for x in range(self.grid_x):
            y = self.grid_y - 1
            last_space = 0
            while y >= 0:
                if self.board[y][x] == None:
                    if not last_space:
                        last_space  = y
                else:
                    if last_space:
                        
                        self.board[last_space][x] = self.board[y][x]
                        self.board[last_space][x].grid_x = x
                        self.board[last_space][x].grid_y = last_space
                        self.board[y][x] = None
                        y = last_space - 1
                        last_space = 0
                
                y -= 1
        for y in range(self.grid_y):
            for x in range(self.grid_x):
                if self.board[y][x] == None:
                    self.board[y][x] = Block(self.screen, x, y, random.choice(self.block_images))
    def render(self):
        for y in range(self.grid_y):
            for x in range(self.grid_x):
                self.screen.blit(self.board[y][x].image,((x * BLOCK_WIDTH) + self.offset_x, (y * BLOCK_HEIGHT) + self.offset_y))
    def logic(self):
        color_match = self.check_color_matches()
        if color_match:
            self.remove_matches(color_match)
            self.fall_blocks()
            for match in color_match:
                self.state.score += len(match) * 50
            self.match_sound.play()

    
class Pointer(GameObject):
    def __init__(self, screen: pygame.Surface, grid_x, grid_y, offset_x = BOARD_OFFSET_X, offset_y = BOARD_OFFSET_Y):
        super().__init__(screen)
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.offset_x = offset_x
        self.offset_y = offset_y
        colors = [(255,0,255), (5, 82, 61), (17, 41, 91)]
        self.color = [random.choice(colors), random.choice(colors)]
        self.current_color = self.color[0]
        self.timer = 0
    def render(self):
        pointer_rect_x = (self.grid_x * BLOCK_WIDTH) + self.offset_x
        pointer_rect_y = (self.grid_y * BLOCK_HEIGHT) + self.offset_y
        pygame.draw.rect(self.screen, self.current_color,(pointer_rect_x, pointer_rect_y, BLOCK_WIDTH, BLOCK_HEIGHT), 10, 
                         round(5 * SCALE_FACTOR))
    def logic(self):
        self.timer += 0.1
        if self.timer >= 1:
            if self.current_color == self.color[0]:
                self.current_color = self.color[1]
            else:
                self.current_color = self.color[0]
            self.timer = 0