import pygame
import Physics
from threading import Timer

class Player(pygame.sprite.Sprite):    
    """
    Player character. Subclasses Character->Sprite.
    
    Can move, jump, attack.
    Has an image, health, rect-bounds. 
        
    Has:
    image, rect, mask
    
    Can:
    move itself
    
    Movement is done by "try"ing to move. This does not update the actual
    positions: just the "new" positions. The "move" method must be called every
    frame to update the actual position to the "new" calculated position.
    """
    
    PLAYER_ANIMS = {"standing" : {"filenames" : ["images/lobster_standing.png"],
                              "frames_between" : 100,
                              },
                "walking"  : {"filenames" : ["images/lobster_walking_0.png",
                                             "images/lobster_walking_1.png"],
                              "frames_between" : 10
                              },
                "jumping"  : {"filenames" : ["images/lobster_jumping_0.png",
                                             "images/lobster_jumping_1.png"],
                              "frames_between" : 15
                              },
                "punching_left" : {"filenames" : ["images/lobster_punching_left_0.png",
                                                  "images/lobster_punching_left_1.png"],
                                   "frames_between" : 30
                                   },
                "punching_right" : {"filenames" : ["images/lobster_punching_right_0.png",
                                                  "images/lobster_punching_right_1.png"],
                                   "frames_between" : 30
                                   }
                }
    
    def __init__(self, bottomleft):
        """
        Pass in the filename of the image to represent
        this player.
        
        images_dict should have:
            keys: 'standing', 'walking', 'jumping'
            values: a list of image filenames
        """        
        # Call the parent class (Sprite) constructor)
        pygame.sprite.Sprite.__init__(self)
        
        # Create all animations, and set the default animation
        self.cur_anim = ''
        self.anims = dict()
        for name, data in self.PLAYER_ANIMS.items():
            self.create_animation(name, data['filenames'], data['frames_between'])
        self.set_animation("standing")
        self.image = self.anims[self.cur_anim]['images'][0]
        
        # Set the collision mask based on the image
        self.mask = pygame.mask.from_surface(self.image)
        
        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect()
        self.startloc = bottomleft
        
        # Set the last recorded direction
        # Used for punching/kicking
        self.facing_left = True
        self.punching = False
        self.punching_left = self.facing_left
        self.punching_time = .8
        self.can_punch = True
        self.punch_cooldown = 1.6
        
        self.reset()
        
    """
    Reset variables. Used when the player dies or the game restarts
    """
    def reset(self):
        # Current speeds
        self.vel_x = 0
        self.vel_y = 0
        
        # Jumping and base+max speeds
        self.on_ground = False
        self.jump_speed = 8
        self.move_speed = 1
        self.max_move_speed = 3
        
        # Points (how many enemies you have destroyed)
        self.points = 0
        
        # Set Base Health
        self.health = 3
    
        # used to ensure that we don't restart the game
        # over and over
        self.currently_dying = False
        
        # Used when we take damage from an enemy
        self.temp_invulnerable = False
        self.blink_counter = 0
        self.blink_threshold = 15
        self.blink_visible = True
        
        # Set starting location (which comes from 
        self.rect.bottomleft = self.startloc
    
    def create_animation(self, name, filenames, frames_between):
        self.anims[name] = dict()
        
        # Images
        self.anims[name]['images'] = []
        for cur_image_filename in filenames:
            self.anims[name]['images'].append(pygame.image.load(cur_image_filename).convert_alpha())
        
        # Timing
        self.anims[name]['frames_between'] = frames_between
        self.anims[name]['counter'] = 0
        self.anims[name]['cur_image_index'] = 0
    
    def set_animation(self, name):
        self.cur_anim = name
        
    def animate(self):
        # To be called every frame
        this_anim = self.anims[self.cur_anim]
        
        # Increment the counter for our current animation
        this_anim['counter'] += 1
        
        # If we've hit the threshold ('frames_between'), then move to the
        # next image in the sequence for this animation (which could mean looping
        # back to the front)
        if this_anim['counter'] >= this_anim['frames_between']:
            this_anim['counter'] = 0
            
            # If we're at the end of the list,
            if this_anim['cur_image_index'] >= len(this_anim['images'])-1:
                # Then loop back to the front
                this_anim['cur_image_index'] = 0
            else:
                # Otherwise, go to the next one
                this_anim['cur_image_index'] += 1
        
        # Set the image
        self.image = this_anim['images'][this_anim['cur_image_index']]
        
    def set_vulnerable(self):
        self.temp_invulnerable = False
        
    def stop_punching(self):
        self.punching = False
    
    def reset_can_punch(self):
        self.can_punch = True

    """
    Block Collision
    """
    def collide(self, xvel, yvel, blockGroup):
        for block in pygame.sprite.spritecollide(self, blockGroup, False):
            # Check for collision on the sides
            if xvel > 0:
                # going -->
                if block.can_jump_through:
                    if self.rect.right - xvel < block.rect.left:
                        self.rect.right = block.rect.left
                else:
                    self.rect.right = block.rect.left
            if xvel < 0:
                # going <--
                if block.can_jump_through:
                    if self.rect.left - xvel > block.rect.right:
                        self.rect.left = block.rect.right
                else:
                    self.rect.left = block.rect.right
            
            # Check for falling collision
            if yvel > 0:
                if self.rect.bottom - yvel < block.rect.top:
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                    self.vel_y = 0
            
            # Check for jumping collision
            if yvel < 0:
                # Check for jump-through-able block
                if block.can_jump_through:
                    pass
                else:
                    if self.rect.top - yvel > block.rect.bottom:
                        self.rect.top = block.rect.bottom
                        self.vel_y = 0
                        if not self.punching:
                            self.set_animation("standing")
    
    """
    Update player based on key input, gravity and collisions
    """
    def update(self, keys, blockGroup, enemyGroup, screen):
        # Jumping
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y -= self.jump_speed
            self.on_ground = False
            if not self.punching:
                self.set_animation("jumping")
        
        # Left-wards movement
        if keys[pygame.K_LEFT]:
            # Update direction we're moving
            self.facing_left = True
            
            # Go faster
            self.vel_x -= self.move_speed
            # But not too fast
            if self.vel_x < -1 * self.max_move_speed:
                self.vel_x = -1 * self.max_move_speed
        
        # Right-wards movement
        if keys[pygame.K_RIGHT]:
            # Update direction we're moving
            self.facing_left = False
            
            # Go faster
            self.vel_x += self.move_speed
            # But not too fast
            if self.vel_x > self.max_move_speed:
                self.vel_x = self.max_move_speed
        
        # Punching
        if keys[pygame.K_SPACE] and self.can_punch:
            
            self.punching = True
            self.punching_left = self.facing_left
            
            self.set_animation("punching_" + ("left" if self.punching_left else "right"))
            
            self.can_punch = False
            can_punch_again_timer = Timer(self.punch_cooldown, self.reset_can_punch)
            punch_ended_timer = Timer(self.punching_time, self.stop_punching)
            can_punch_again_timer.start()
            punch_ended_timer.start()
        
        # Set walking or standing animations
        if self.on_ground and not self.punching:
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.set_animation("walking")
            else:
                self.set_animation("standing")
        
        # Gravity
        if not self.on_ground:
            self.vel_y += Physics.gravity
            if self.vel_y > Physics.terminal_gravity:
                self.vel_y = Physics.terminal_gravity
            
        # Loop between top and bottom of map
        if self.rect.top >= screen.get_size()[1]+16:
            self.rect.bottom = 0
        if self.rect.bottom <= 0-8:
            self.rect.top = screen.get_size()[1]-8
                
        # If not moving left or right, stop.
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.vel_x = 0
            
        # Animate
        self.animate()
            
        # Move horizontally, then handle horizontal collisions
        self.rect.left += self.vel_x
        self.collide(self.vel_x, 0, blockGroup)
        
        # Move vertically, then handle vertical collisions
        self.rect.top += self.vel_y
        self.on_ground = False
        self.collide(0, self.vel_y, blockGroup)
        
        # Blinking after taking damage
        if self.temp_invulnerable:
            self.blink_counter += 1
            # If it's time to toggle visibility,
            if self.blink_counter >= self.blink_threshold:
                # Then toggle visibility
                self.blink_counter = 0
                self.blink_visible = not self.blink_visible # Toggle visibility
        
                
