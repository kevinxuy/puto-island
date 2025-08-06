#!/usr/bin/env python3
import pygame
import platform
import os

def get_chinese_font(size=24):
    """
    Get a font that supports Chinese characters based on the operating system.
    Falls back to default font if Chinese font is not found.
    """
    system = platform.system()
    
    chinese_fonts = []
    
    if system == "Windows":
        chinese_fonts = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttf",
            "C:/Windows/Fonts/simsun.ttc"
        ]
    elif system == "Darwin":  # macOS
        chinese_fonts = [
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Songti.ttc",
            "/System/Library/Fonts/PingFang.ttc"
        ]
    elif system == "Linux":
        chinese_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
        ]
    
    # Try to load Chinese font
    for font_path in chinese_fonts:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    # Fallback to default font if no Chinese font found
    return pygame.font.Font(None, size)

def get_default_font(size=24):
    """
    Get default system font for UI elements that don't need Chinese support.
    """
    return pygame.font.Font(None, size)