import pygame

class Button(pygame.sprite.Sprite):
    """
    A button that can be clicked, when hovered over with mouse
    changes from one image to another.
    """
    def __init__(self, images_list, pos_x, pos_y, mode_change, current_mode):
        """
        Pass in the filename of the images to represent
        this button on certain actions.
        """
        # ------------------------------------------------
        # Call super constructor, set image and rect
        # ------------------------------------------------
        
        # Call the parent class (Sprite) constructor)
        pygame.sprite.Sprite.__init__(self)  
  
        self.images = []

        # Create images
        for cur_image_filename in images_list:
            self.images.append(pygame.image.load(cur_image_filename).convert_alpha())

        # Sets the base image state for the button
        self.button_state = 0

        self.image = self.images[self.button_state]

        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

        # If a button is clicked, what game mode to change it to
        self.mode_change = mode_change

        # The gamemode the button is in
        self.current_mode = current_mode

    def button_update(self, mouse_position, left_mouse):
        """
        update the state of a button
        """
        self.mouse_collision(mouse_position)
        mode = self.button_pressed(left_mouse)
        self.button_click_down(left_mouse)
        return mode

    def mouse_collision(self, mouse_position):
        """
        Checks to see if the mouse is hovering over the button
        """
        if (mouse_position[0] >= self.rect.left) and (mouse_position[0] <= self.rect.right) and (mouse_position[1] >= self.rect.top) and (mouse_position[1] <= self.rect.bottom) and self.button_state != 2:
            self.button_state = 1
        elif (mouse_position[0] >= self.rect.left) and (mouse_position[0] <= self.rect.right) and (mouse_position[1] >= self.rect.top) and (mouse_position[1] <= self.rect.bottom) and self.button_state == 2:
            self.button_state = 2
        else:
            self.button_state = 0

        self.image = self.images[self.button_state]
            
            
    def button_click_down(self, left_mouse):
        """
        Check if the user pressed down on the button
        """
        if self.button_state == 1:
            if left_mouse == True:
                self.button_state = 2

        self.image = self.images[self.button_state]
        
    def button_pressed(self, left_mouse):
        """
        Check if the user finished the
        mouse click over the button
        """
        if self.button_state == 2:
            if left_mouse == False:
                self.button_state = 0
                return self.mode_change

        return self.current_mode
