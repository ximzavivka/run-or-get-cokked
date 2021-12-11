import pygame
import random
import Physics
from threading import Timer

class Enemy(pygame.sprite.Sprite):
    """
    Enemy character.
    
    Can move and kill the player.
    Has an image, rect-bounds.
    """
    def __init__(self, images_dict, pos_x, pos_y, enemytype):
        """
        Pass in the filename of the image to represent
        this enemy.
        """
        # ------------------------------------------------
        # Call super constructor, set image and rect
        # ------------------------------------------------
        
        # Call the parent class (Sprite) constructor)
        pygame.sprite.Sprite.__init__(self)
        
        # Create all animations, and set the default animation
        self.cur_anim = ''
        self.anims = dict()
        for name, data in images_dict.items():
            self.create_animation(name, data['filenames'], data['frames_between'])
        self.set_animation("walking")
        self.image = self.anims[self.cur_anim]['images'][0]
        
        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect(center=(pos_x,pos_y))
        
        self.move = random.randint(0,1)
        self.vel_x = 0
        self.vel_y = 0
        
        self.on_ground = False
        self.move_speed = 1
        self.movecounter = 140
        
        self.currently_dying = False
        
        self.enemy_type = enemytype

        if self.enemy_type == "spiky":
            self.max_move_speed = 1
        if self.enemy_type == "basic":
            self.max_move_speed = random.randint(1,2)
    
    #===========================================================================
    # Animations
    #===========================================================================
    
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
    
    
    #===========================================================================
    # Collisions and updating
    #===========================================================================
    
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
                    self.move = 0
            if xvel < 0:
                # going <--
                if block.can_jump_through:
                    if self.rect.left - xvel > block.rect.right:
                        self.rect.left = block.rect.right
                else:
                    self.rect.left = block.rect.right
                    self.move = 1
            
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
                        
    """
    Collision with Player and basic enemy
    """
    def player_collide(self, player,hasSquishedSomeoneAlready):
        squished, punched = False, False
        if pygame.sprite.collide_rect(self, player):
            if player.vel_y > 0 and player.rect.bottom - player.vel_y < self.rect.top:
                # Player squishes this enemy
                if not player.currently_dying:
                    player.points += 1
                
                # Bounce off the enemy
                player.vel_y = player.jump_speed/-1.5
                
                # Animate the death of said enemy
                self.set_animation("squished")
                squished = True # Squished
                
            elif player.punching:
                # Player got us, arggghh
                player.punching = False # Can only punch one enemy
                
                # Player gets a point
                if not player.currently_dying:
                    player.points += 1
                
                # Animate our death
                self.set_animation("punched")
                punched = True
                
            elif not player.temp_invulnerable:
                
                # We've been hit! Get the lifeboats! Ready the guns!
                if not hasSquishedSomeoneAlready and not player.currently_dying:
                    # Lose some health
                    player.health -= 1
                    
                    # Set player to be temporarily invulnerable
                    player.temp_invulnerable = True
                    setVulnerableTimer = Timer(2.0, player.set_vulnerable)
                    setVulnerableTimer.start()
                
                # bounce the enemy back
                self.vel_x *= -6

        return (squished, punched)

    """
    Collision with Player and spiky enemy
    """
    def player_collide_spiky(self, player):
        squished, punched = False, False
        if pygame.sprite.collide_rect(self, player):
            if (player.vel_y > 0 and player.rect.bottom - player.vel_y < self.rect.top
                and not player.temp_invulnerable):
                # Bounce off the enemy (spiky can't be killed by a jump)
                player.vel_y = player.jump_speed/-1.5
                
                # We've been hit!
                if not player.currently_dying:
                    player.health -= 1
                
            elif player.punching:
                # Player got us, arggghh
                player.punching = False # Can only punch one enemy
                
                # Player gets a point
                if not player.currently_dying:
                    player.points += 2
                
                # Animate our death
                self.set_animation("punched")
                punched = True
                    
            elif not player.temp_invulnerable:
                # We've been hit! Get the lifeboats! Ready the guns!
                if not player.currently_dying:
                    player.health -= 1
                
                # bounce the enemy back
                self.vel_x *= -6
                
                # Set player to be temporarily invulnerable
                if not player.temp_invulnerable:
                    player.temp_invulnerable = True
                    set_vulnerable_timer = Timer(2.0, player.set_vulnerable)
                    set_vulnerable_timer.start()
        
        return (squished, punched)
                

    """
    Update enemy based on key input, gravity and collisions
    """
    def update(self, blockGroup, screen, waypoint, player, hasSquishedSomeoneAlready):
        #Update movement
        if self.enemy_type == "basic":
            if self.movecounter == 0:
                self.random_movement()
                self.movecounter = 140
        
        if self.enemy_type == "spiky":
            self.basic_movement(waypoint, player)
 
        # Left/right movement
        #Left
        if self.move == 0:
            # Go faster
            self.vel_x -= self.move_speed
            # But not too fast
            if self.vel_x < -1 * self.max_move_speed:
                self.vel_x = -1 * self.max_move_speed
        #Right
        if self.move == 1:
            # Go faster
            self.vel_x += self.move_speed
            # But not too fast
            if self.vel_x > self.max_move_speed:
                self.vel_x = self.max_move_speed
        
        # Gravity
        if not self.on_ground:
            self.vel_y += Physics.gravity
            if self.vel_y > Physics.terminal_gravity:
                self.vel_y = Physics.terminal_gravity

        # Looping Across screen
        if self.rect.top >= screen.get_size()[1]+16:
            self.rect.bottom = 0
        if self.rect.bottom <= 0-8:
            self.rect.top = screen.get_size()[1]-8
            
        # Move horizontally, then handle horizontal collisions
        self.rect.left += self.vel_x
        self.collide(self.vel_x, 0, blockGroup)
        
        # Move vertically, then handle vertical collisions
        self.rect.top += self.vel_y
        self.on_ground = False
        self.collide(0, self.vel_y, blockGroup)
        
        # Animate
        self.animate()
        
        # Check collision with player
        if self.enemy_type == "basic":
            squished, punched = self.player_collide(player, hasSquishedSomeoneAlready)
        if self.enemy_type == "spiky":
            squished, punched = self.player_collide_spiky(player)
        self.movecounter -= 1
        
        return (squished, punched)

    def send_to_heaven(self, dyingEnemyGroup):
        # NOOOOOOOOOOOOOOOOOOOOOOOOOO
        dyingEnemyGroup.remove(self)

    def basic_movement(self, waypoint, player):
        """
        The basic movement for an enemy. If the player is on the 
        same platform region as the player, move toward the player.
        Otherwise move towards the nearest edge, using waypoints.
        """
        wlist = []
        closestval = 100000
        closewaypoint = (0,0)
        #Check if the player is on the same floor
        if abs(player.rect.bottom - self.rect.top) < 70:
            if player.rect.right > self.rect.right:
                self.move = 1
                return 
            else:
                self.move = 0
                return
        
        #Find waypoints on same floor
        for w in waypoint:
            if abs(w[1] - self.rect.bottom) < 20:
                wlist.append(w)
        #Find closest waypoint
        for c in wlist:
            if abs(c[0]-self.rect.center[0]) < closestval:
                closestval = abs(c[0]-self.rect.center[0])
                closewaypoint = c
        if self.rect.left < closewaypoint[0]:
            self.move = 1
            return
        if self.rect.right > closewaypoint[0]:
            self.move = 0
            return         
     
    def  random_movement(self):
        """
        Move in a random direction
        """
        self.move = random.randint(0,1)
        
    
