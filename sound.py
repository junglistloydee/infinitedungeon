import pygame
import json
import os
import debug

# --- Sound Manager ---

class Sound:
    def __init__(self, game_data_file='game_data.json', sound_enabled=True):
        """
        Initializes the Sound Manager.
        Args:
            game_data_file (str): The path to the game data JSON file.
            sound_enabled (bool): Whether sound is enabled or not.
        """
        self.sound_enabled = sound_enabled
        if not self.sound_enabled:
            debug.debug_print("Sound is disabled.")
            return

        try:
            pygame.mixer.init()
            debug.debug_print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            self.sound_enabled = False
            debug.debug_print(f"Error initializing pygame mixer: {e}")
            return

        self.sounds = {}
        self.load_sounds(game_data_file)

    def load_sounds(self, game_data_file):
        """
        Loads sound data from the game data JSON file.
        Args:
            game_data_file (str): The path to the game data JSON file.
        """
        if not self.sound_enabled:
            return

        try:
            with open(game_data_file, 'r') as f:
                game_data = json.load(f)
                sound_data = game_data.get('sounds', {})
                for key, path in sound_data.items():
                    if os.path.exists(path):
                        if 'music' in key:
                            self.sounds[key] = path
                        else:
                            self.sounds[key] = pygame.mixer.Sound(path)
                        debug.debug_print(f"Loaded sound: {key} -> {path}")
                    else:
                        debug.debug_print(f"Sound file not found for {key}: {path}")
        except FileNotFoundError:
            debug.debug_print(f"Game data file not found: {game_data_file}")
        except json.JSONDecodeError:
            debug.debug_print(f"Error decoding JSON from {game_data_file}")
        except pygame.error as e:
            debug.debug_print(f"Error loading sound file: {e}")

    def play_music(self, key, loops=-1):
        """
        Plays background music.
        Args:
            key (str): The key of the music to play.
            loops (int): The number of times to loop the music (-1 for infinite).
        """
        if not self.sound_enabled:
            debug.debug_print(f"Sound disabled, not playing music: {key}")
            return

        if key in self.sounds:
            try:
                pygame.mixer.music.load(self.sounds[key])
                pygame.mixer.music.play(loops)
                debug.debug_print(f"Playing music: {key}")
            except pygame.error as e:
                debug.debug_print(f"Error playing music {key}: {e}")
        else:
            debug.debug_print(f"Music key not found: {key}")

    def stop_music(self):
        """
        Stops the currently playing music.
        """
        if not self.sound_enabled:
            return
        pygame.mixer.music.stop()
        debug.debug_print("Music stopped.")

    def play_sound(self, key):
        """
        Plays a sound effect.
        Args:
            key (str): The key of the sound effect to play.
        """
        if not self.sound_enabled:
            debug.debug_print(f"Sound disabled, not playing sound: {key}")
            return

        if key in self.sounds:
            try:
                self.sounds[key].play()
                debug.debug_print(f"Playing sound: {key}")
            except pygame.error as e:
                debug.debug_print(f"Error playing sound {key}: {e}")
        else:
            debug.debug_print(f"Sound key not found: {key}")