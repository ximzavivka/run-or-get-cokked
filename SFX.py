from pygame import mixer
from pygame.mixer import music

class SFX:
    """
    Does sound effects.
    """


    def __init__(self):
        """
        Initializes the sfx object with the mixer.init() call.
        """
        self.mixer = mixer.init()
    
    def play_music(self):
        music.load('audio/game_music.mp3')
        music.play(-1) # loop indefinitely
    
    