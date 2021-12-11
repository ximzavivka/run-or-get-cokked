from sys import exit
import time

import pygame
from pygame.locals import * # For keypress variables

from SFX import SFX

from Manage_highscores import *
from Button import Button
from Map import Map
from Player import Player

# Importing Timer to schedule things
# Example use:
# secondsToWait = 1.5
# list_of = player_sprite
# parameters = "new-image.jpg"
# def changeImage(player, filename) {
#     player.image = filename
# }
# changeImageTimer = Timer(secondsToWait, changeImage, [list_of, parameters])
# a la http://stackoverflow.com/questions/16578652/threading-timer
from threading import Timer

# Debug
DEBUG = False

# Init pygame & create a screen
pygame.init()
screen = pygame.display.set_mode((608,448),0,24)

# Create a clock to use to hold the framerate constant
clock = pygame.time.Clock()

# Initialize the audio
sfx = SFX()
sfx.play_music()

# Initialize fonts for printing to screen
debugfont = pygame.font.SysFont("monospace", 15)
gamefont = pygame.font.SysFont("comicsansms",30)
titlefont = pygame.font.SysFont("comicsansms", 60)
game_label = gamefont.render("", 1, (0,0,0))

# Create a white background
bg = pygame.Surface(screen.get_size())
bg = bg.convert()
bg.fill(pygame.Color(255,255,255))

# Set the window title and game font
pygame.display.set_caption("Run or Get Cooked👨🏻‍🍳")
pygame.display.set_icon(pygame.image.load("images/lobster_standing.png").convert_alpha())

# Make a button group
menubuttonGroup = pygame.sprite.Group()
highbuttonGroup = pygame.sprite.Group()
gamebuttonGroup = pygame.sprite.Group()
button_leftalign = screen.get_size()[0]/15
button_spacing = 65
button_base_y = screen.get_size()[1] - button_spacing*3

# Make a heart
heart = pygame.image.load("images/heart.png").convert_alpha()

start_button = Button(["images/start_0.png","images/start_1.png", "images/start_2.png"], 
                      button_leftalign, button_base_y + button_spacing*0, 
                      1, 0)
highscores_button = Button(["images/high_0.png","images/high_1.png", "images/high_2.png"], 
                           button_leftalign, button_base_y + button_spacing*1, 
                           2, 0)
exit_button = Button(["images/exit_0.png","images/exit_1.png", "images/exit_2.png"], 
                     button_leftalign, button_base_y + button_spacing*2, 
                     3, 0)
back_from_highscores_button = Button(["images/back_0.png", "images/back_1.png", "images/back_2.png"], 
                        500, 400,
                        0, 2)
start_button.add(menubuttonGroup)
highscores_button.add(menubuttonGroup)
exit_button.add(menubuttonGroup)
back_from_highscores_button.add(highbuttonGroup)
gametype = 0

# Make a menu splash background
menu_bg = pygame.image.load("images/menu_bg.png").convert()


while True:
    # --------------------------------------------
    # Menu Game Loop
    # --------------------------------------------
    while gametype == 0:
        # --------------------------------------------
        # Event Handling
        # --------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        # Get mouse buttons pressed
        mouse_pressed = pygame.mouse.get_pressed()

        # Update buttons based on mouse input
        for button in menubuttonGroup:
            if gametype == 0:
                gametype = button.button_update(pygame.mouse.get_pos(), mouse_pressed[0])

        # Redraw the Background
        screen.blit(menu_bg, (0,0))

        # Redraw buttons
        menubuttonGroup.draw(screen)

        # Update the display
        pygame.display.update()


    if gametype == 2:
        scores = ""
        highscore_list = open("highscores.txt", "r")
        for line in highscore_list:
            scores += line
        highscore_list.close()
        score_list = scores.splitlines()
        seperate_score_list = []
        for string in score_list:
            seperate_score_list.append(string.split())
    
    if gametype == 3:
        exit()
    
    #------------------------
    # HIGH SCORE SCREEN
    #------------------------
    while gametype == 2:

        # --------------------------------------------
        # Event Handling
        # --------------------------------------------
        font_size = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        # Get mouse buttons pressed
        mouse_pressed = pygame.mouse.get_pressed()

        # Update buttons based on mouse input
        for button in highbuttonGroup:
            if gametype == 2:
                gametype = button.button_update(pygame.mouse.get_pos(), mouse_pressed[0])
        
        # Redraw the Background
        screen.blit(bg, (0,0))

        # Draw Highscores
        screen.blit(titlefont.render("HIGHSCORES", 1, (20,80,200)),(screen.get_size()[0]/4, 5))
        screen.blit(gamefont.render("Points:", 1, (0,0,0)),(screen.get_size()[0]/8-40, 80+font_size))            
        screen.blit(gamefont.render("Name:", 1, (0,0,0)),(screen.get_size()[0]/2-40, 80+font_size))

        for score, name in seperate_score_list:
            screen.blit(gamefont.render(score, 1, (0,0,0)),(screen.get_size()[0]/8+40, 110+font_size))
            screen.blit(gamefont.render(name, 1, (0,0,0)),(screen.get_size()[0]/2+40, 110+font_size))
            font_size += 25

        # Redraw buttons
        highbuttonGroup.draw(screen)

        # Update the display
        pygame.display.update()
        

    # Initialize game
    if gametype == 1:

        # Create the map
        game_map = Map("getonmy.lvl")

        blockGroup = pygame.sprite.Group()
        blockGroup.add([block for block in game_map.get_blocks()])

        spawnerGroup = pygame.sprite.Group()
        spawnerGroup.add([spawner for spawner in game_map.get_spawner()])
        
        waypointList = game_map.get_waypoints()
    
        # Create the player
        playerGroup = pygame.sprite.GroupSingle() # Create the Group
        player = Player(game_map.get_player_pos()) # Create the player Sprite
        player.add(playerGroup) # Add the player Sprite to the Group

        # Create an enemy group
        enemyGroup = pygame.sprite.Group()
        # Create a group for dying (non-interactive) enemies
        dyingEnemyGroup = pygame.sprite.Group()

        # Monster spawn times
        last_called_basic = time.time()
        last_called_spiky = time.time()

        # To be used on game restart or on
        # player death/game over
    def resetGame():
        global game_label # using the GLOBAL game_label
        game_label = gamefont.render("", 1, (0,0,0))
        blockGroup.empty()
        spawnerGroup.empty()
        enemyGroup.empty()
        global gametype
        gametype = 4

    # --------------------------------------------
    # Main Game Loop
    # --------------------------------------------
    while gametype == 1:
        # --------------------------------------------
        # Event Handling
        # --------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        # --------------------------------------------
        # Player: Movement, Collisions and Death
        # --------------------------------------------

        # Update player based on keyboard input
        keys_down = pygame.key.get_pressed() # Get a list of all keys pressed right now

        player.update(keys_down, blockGroup, enemyGroup, screen)
        if player.health <= 0:
            # Player has died
            if not player.currently_dying:
                player.currently_dying = True
                resetGameTimer = Timer(3.0, resetGame)
                resetGameTimer.start()    
                game_label = gamefont.render("Game over! Points: {}".format(player.points),
                                             1, (0,0,0))

        if player.rect.x < 0 or player.rect.x > screen.get_size()[0]:
            player.rect.x = screen.get_size()[0]//2


        #--------------------------------------------
        # Enemy Movement    
        #--------------------------------------------
        hasSquishedSomeoneAlready = False
        to_remove = []
        for e in enemyGroup:
            squished, punched = e.update(blockGroup, screen, waypointList, player, hasSquishedSomeoneAlready)
            if squished or punched:
                to_remove.append(e)
                if squished:
                    hasSquishedSomeoneAlready = True
        for dead_enemy in to_remove:
            enemyGroup.remove(dead_enemy)

            dyingEnemyGroup.add(dead_enemy)
            oneAnimFrames = dead_enemy.anims[dead_enemy.cur_anim]['frames_between'] * len(dead_enemy.anims[dead_enemy.cur_anim]['images'])
            oneAnimTime = 6/7 * oneAnimFrames / clock.get_fps()
            removeEnemyTimer = Timer(oneAnimTime, dead_enemy.send_to_heaven, [dyingEnemyGroup])
            removeEnemyTimer.start()

        # Update the animations of dying enemies
        for e in dyingEnemyGroup:
            e.animate()

        #---------------------------------------------
        # Monster Spawning
        #---------------------------------------------
        for spawner in spawnerGroup:
            spawner.spawn(enemyGroup)
        # --------------------------------------------
        # Redraw everything on the screen
        # --------------------------------------------

        # Redraw the Background
        screen.blit(bg, (0,0))

        # Redraw all Groups
        blockGroup.draw(screen)
        spawnerGroup.draw(screen)
        enemyGroup.draw(screen)
        dyingEnemyGroup.draw(screen)
        if player.temp_invulnerable:
            # If we were just hit, we will be blinking
            if player.blink_visible:
                # If the blinking is currently in the visible state, then draw the player
                playerGroup.draw(screen)
        else:
            playerGroup.draw(screen)

        # Draw game text
        width, height = screen.get_size()
        screen.blit(game_label, (width/4, height/2))
        screen.blit(titlefont.render(str(player.points), 1, (255,140,0)),(screen.get_size()[0]*43/89, 5))

        # Draw health bar
        if player.health > 0:
            heart_width = 35
            for i in range (0, player.health):
                screen.blit(heart, (width*5/8 + heart_width*i, height/50))

        # Render text for debug
        if DEBUG:
            label = debugfont.render("fps:"+str(int(clock.get_fps()))
                                  +" monsters:"+str(len(enemyGroup))
                                  +" points: " + str(player.points)
                                  +" health: " + str(player.health)

                                  , 1, (0,0,0))
            screen.blit(label, (20, 10))


        # Update the display
        pygame.display.update()

        # --------------------------------------------
        # Clock Tick
        # --------------------------------------------
        clock.tick(60)



    if gametype == 4:
        name = ""

    #--------------------------------
    # Enter name for highscore
    #--------------------------------
    while gametype == 4:
        
        # --------------------------------------------
        # Event Handling
        # --------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if len(name) < 12:
                    if event.unicode.isalpha():
                        name += event.unicode
                if event.key == K_BACKSPACE:
                    name = name[:-1]
                if event.key == K_RETURN:
                    manage_highscore(player, name)
                    playerGroup.empty()
                    gametype = 0
                
            if event.type == pygame.QUIT:
                exit()
                
        label2 = gamefont.render("Please enter your name: " + name, 1, (0,0,0))



        # Redraw the Background
        screen.blit(bg, (0,0))

        screen.blit(label2, (screen.get_size()[0]/8, screen.get_size()[1]/3))

        pygame.display.update()
