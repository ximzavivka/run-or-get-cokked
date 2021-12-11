import pygame.sprite
from pygame import Rect

class HealthBar(pygame.sprite.Sprite):
    """
    A health bar.
    
    Is a rect filled with red.
    Has:
    - maximum health
    - current health
    - rectangle
    Can:
    - decrease health
    - query health
    """


    def __init__(self, maximum_health, rect):
        """
        Takes:
        maximum_health (int),
        rect (Rect with x,y,width,height)
        """
        # Call the parent class (Sprite) constructor)
        pygame.sprite.Sprite.__init__(self)
        
        # Set defaults
        self.maximum_health = maximum_health
        self.current_health = maximum_health
        self.rect = rect
        
        self.image = pygame.Surface([self.rect.width, self.rect.height])
        self.refill()
    
    def refill(self):
        # Reset the fill
        self.image.fill((255, 0, 0))
        self.image.fill((60, 60, 60), self.get_fill_rect())
    
    def decrease(self):
        self.current_health -= 1
        self.refill()
    
    def set_current_health(self, current_health):
        self.current_health = current_health
        self.refill()
    
    def get_health(self):
        return self.current_health
    
    def get_percentage_health(self):
        return self.current_health / self.maximum_health
    
    def get_fill_rect(self):
        fill_rect = Rect(self.rect)
        fill_rect.topleft = (0,0) # Topleft of the image
        fill_rect.top -= self.rect.height * self.get_percentage_health()
        return fill_rect