import pygame
import random
from constants import SCALE_FACTOR, BOARD_OFFSET_X, BOARD_OFFSET_Y, BLOCK_WIDTH, BLOCK_HEIGHT



class SpriteSheet:
    def __init__(self,filename,start_coordinates,end_coordinates,width,height,skip_x = False, skip_y = False):
        self.start_coordinates = start_coordinates
        self.end_coordinates = end_coordinates
        self.width = width
        self.height = height
        self.image = pygame.image.load(filename).convert_alpha()
        self.sprites = []
        self.skip_y = skip_y
        self.skip_x = skip_x

        self.generate_sprites()
        

    def generate_sprites(self):
        self.grid_start_x = (self.start_coordinates[0]) // self.width
        self.grid_start_y = (self.start_coordinates[1]) // self.height
        self.grid_end_x = (self.end_coordinates[0]) // self.width
        self.grid_end_y = (self.end_coordinates[1]) // self.height
        skipper_y = False
        skipper_x = False
        counter = 0
        for y in range(self.grid_start_y,self.grid_end_y):
            if self.skip_y and skipper_y:
                skipper_y = not skipper_y
                continue
            else: 
                skipper_y = not skipper_y

            for x in range(self.grid_start_x,self.grid_end_x):
                if self.skip_y and skipper_x:
                    skipper_x = not skipper_x
                    continue
                else: 
                    skipper_x = not skipper_x
                data = {

                }
                data['image'] = self.get_sprite(x,y)
                data["color"] = counter // 6
                data["pattern"] = counter % 6
                
                self.sprites.append(data.copy())
                counter += 1
        
    def get_sprite(self,x,y): # using grid number
        sprite_rect = pygame.Rect(x * self.width,y * self.height, self.width,self.height)
        sprite_image  = pygame.Surface((self.width,self.height))
        sprite_image.blit(self.image,(0,0),sprite_rect)
        sprite_image.set_colorkey((0,0,0))
        sprite_image = pygame.transform.scale_by(sprite_image, SCALE_FACTOR)
        return sprite_image
    
    def get_sprites(self):
        return self.sprites
    # def get_sprite_grid(self,sprite_number): # A helper
    #     """
    #     For getting the index of the 2d array of where the number is located
    #     e.g 6 is located in (1,0) , 13 is located in (2,1)
    #     """
    #     y = sprite_number // self.grid_end_x
    #     x = sprite_number % self.grid_end_x
    #     return (y,x)

    

# sprites = SpriteSheet("assets/blocks.png",(0,0),(192,48),32,16)

class AlternativeSpriteSheet(SpriteSheet):
    
    def generate_sprites(self):
        no_of_grid_x = (self.end_coordinates[0] - self.start_coordinates[0])// self.width #(96 - 32) / 64 = 1
        no_of_grid_y = (self.end_coordinates[1] - self.start_coordinates[1]) // self.height #(176 - 64) /16 = 7
        skipper_y = False
        skipper_x = False
        counter = 0
        for y in range(no_of_grid_y): #[0,1,2,3,4,5,6]
            if self.skip_y and skipper_y:
                skipper_y = not skipper_y
                continue #[1,3,5]
            else: 
                skipper_y = not skipper_y
            skipper_x = False
            for x in range(no_of_grid_x): # [0]
                if self.skip_x and skipper_x:
                    skipper_x = not skipper_x
                    continue 
                else: 
                    skipper_x = not skipper_x
                data = {}
                data['image'] = self.get_sprite(x,y)
                data ['color'] = counter  // 6
                data["pattern"] = counter % 6
                self.sprites.append(data.copy())
                counter += 1
    def get_sprite(self,x,y): # using grid number
        sprite_rect = pygame.Rect((x * self.width) + self.start_coordinates[0],(y * self.height) + self.start_coordinates[1],
                                   self.width,self.height)
        sprite_image  = pygame.Surface((self.width,self.height))
        sprite_image.blit(self.image,(0,0),sprite_rect)
        sprite_image.set_colorkey((0,0,0))
        sprite_image = pygame.transform.scale_by(sprite_image, SCALE_FACTOR)
        return sprite_image
    


class Timer:
    def __init__(self):
        self.counting_down = False
        self.timing = False
        self.in_use = False
        self.coundown_timer = 0
    def countdown(self, seconds, callback = None):
        if self.in_use:
            return 
        self.in_use = True
        self.counting_down = True
        self.coundown_timer = seconds
        self.callback = callback
        self.start_time = pygame.time.get_ticks()
    def timer(self):
        if self.in_use:
            return
        self.in_use = True
        self.timing = True
        self.start_time = pygame.time.get_ticks()
    def end_timer(self):
        self.in_use = False
        self.timing = False
    def logic(self):
        if self.in_use:
            
            if self.counting_down:
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.start_time
                remaining_time = max(0, self.coundown_timer - elapsed_time // 1000)
                if remaining_time <= 0:
                    self.in_use = False
                    self.counting_down = False
                    if self.callback:
                        self.callback()
                return remaining_time
            elif self.timing:
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.start_time
                return elapsed_time // 1000
        return 0

