import pygame

class Block(pygame.sprite.Sprite):
    """
    Floors, walls, platforms, etc.
    
    Can be jumped up through if the property
    self.can_jump_through is set to True. (False by default)
    """

    def __init__(self, image_filename, x, y):
        """
        Pass in the filename of the image to represent
        this block.
        """
        # ------------------------------------------------
        # Call super constructor, set image and rect
        # ------------------------------------------------
        
        # Call the parent class (Sprite) constructor)
        pygame.sprite.Sprite.__init__(self)
        
        # Set the image of the player Sprite
        self.image = pygame.image.load(image_filename).convert_alpha()
        # Set the collision mask based on the image
        self.mask = pygame.mask.from_surface(self.image)
        
        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect()
        
        self.rect.x = x
        self.rect.y = y
        
        self.can_jump_through = False