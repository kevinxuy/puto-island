#!/usr/bin/env python3
"""
Main entry point for Puto Island Game
This file is required by Buildozer for Android builds
"""

# Import and run the main game
if __name__ == "__main__":
    from main_game import Game
    game = Game()
    game.run()