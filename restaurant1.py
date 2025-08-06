#!/usr/bin/env python3
import pygame
import random
import time
import subprocess
from collections import deque
import os
from game_manager import game_manager
from font_helper import get_chinese_font, get_default_font

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 1000
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
BEIGE = (245, 245, 220)

# Location coordinates (restaurant positions)
LOCATIONS = {
    "r1_1": (273, 606),
    "r1_2": (288, 507),
    "r1_3": (444, 439),
    "r1_4": (553, 493),
    "r1_5": (577, 643),
    "r1_6": (446, 686)
}

# Path connections (bidirectional)
CONNECTIONS = {
    "r1_1": ["r1_2", "r1_5", "r1_6"],
    "r1_2": ["r1_1", "r1_3", "r1_4"],
    "r1_3": ["r1_2", "r1_4"],
    "r1_4": ["r1_2", "r1_3", "r1_5"],
    "r1_5": ["r1_1", "r1_4", "r1_6"],
    "r1_6": ["r1_1", "r1_5"]
}

# Building centers for upgrade system
BUILDING_CENTERS = [
    (173, 623),
    (249, 355),
    (436, 289),
    (593, 363),
    (760, 515)
]

# Restaurant emoji mapping
RESTAURANT_EMOJIS = {
    "r1_1": "./assets/restaurant/emoji1.png",
    "r1_2": "./assets/restaurant/emoji2.png",
    "r1_3": "./assets/restaurant/emoji3.png",
    "r1_4": "./assets/restaurant/emoji4.png",
    "r1_5": "./assets/restaurant/emoji5.png",
    "r1_6": "./assets/restaurant/emoji6.png"
}

class Map:
    def __init__(self):
        self.background = pygame.image.load("./assets/restaurant/r1map.png")
        self.bg_rect = self.background.get_rect()
        self.bg_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.drag_start = None
        self.dragging = False
        self.animating = False
        self.anim_start_pos = None
        self.anim_target_pos = None
        self.anim_start_time = None
        self.anim_duration = 0.5
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drag_start = event.pos
            self.dragging = True
            self.animating = False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.drag_start[0]
            dy = event.pos[1] - self.drag_start[1]
            self.scroll(dx, dy)
            self.drag_start = event.pos
            
    def scroll(self, dx, dy):
        new_x = self.bg_rect.x + dx
        new_y = self.bg_rect.y + dy
        
        # Boundary checking
        if new_x > 0:
            new_x = 0
        elif new_x < WINDOW_WIDTH - self.bg_rect.width:
            new_x = WINDOW_WIDTH - self.bg_rect.width
            
        if new_y > 0:
            new_y = 0
        elif new_y < WINDOW_HEIGHT - self.bg_rect.height:
            new_y = WINDOW_HEIGHT - self.bg_rect.height
            
        self.bg_rect.x = new_x
        self.bg_rect.y = new_y
        
    def center_on_building(self, building_center):
        # Calculate desired position to center the building
        desired_x = WINDOW_WIDTH // 2 - building_center[0]
        desired_y = WINDOW_HEIGHT // 2 - building_center[1]
        
        # Apply boundary constraints
        if desired_x > 0:
            desired_x = 0
        elif desired_x < WINDOW_WIDTH - self.bg_rect.width:
            desired_x = WINDOW_WIDTH - self.bg_rect.width
            
        if desired_y > 0:
            desired_y = 0
        elif desired_y < WINDOW_HEIGHT - self.bg_rect.height:
            desired_y = WINDOW_HEIGHT - self.bg_rect.height
            
        # Start animation
        self.animating = True
        self.anim_start_pos = (self.bg_rect.x, self.bg_rect.y)
        self.anim_target_pos = (desired_x, desired_y)
        self.anim_start_time = time.time()
        
    def update(self):
        if self.animating:
            current_time = time.time()
            elapsed = current_time - self.anim_start_time
            progress = min(elapsed / self.anim_duration, 1.0)
            
            # Use easing function for smooth animation
            eased_progress = self.ease_in_out_cubic(progress)
            
            # Interpolate position
            self.bg_rect.x = self.anim_start_pos[0] + (self.anim_target_pos[0] - self.anim_start_pos[0]) * eased_progress
            self.bg_rect.y = self.anim_start_pos[1] + (self.anim_target_pos[1] - self.anim_start_pos[1]) * eased_progress
            
            if progress >= 1.0:
                self.animating = False
                
    def ease_in_out_cubic(self, t):
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
        
    def draw(self, screen):
        screen.blit(self.background, self.bg_rect)
        
    def world_to_screen(self, world_pos):
        return (world_pos[0] + self.bg_rect.x, world_pos[1] + self.bg_rect.y)

class Building:
    def __init__(self, index, center):
        self.index = index
        self.center = center
        self.level = 0
        self.animating = False
        self.animation_start = None
        self.animation_type = None
        self.animation_frame = 0
        self.animation_cycle = 0
        self.showing_final = False
        
        # Load construction images
        self.construction_imgs = []
        for i in range(1, 6):
            img = pygame.image.load(f"./assets/mainmap/construction{i}.png")
            img = pygame.transform.scale(img, (200, 200))
            self.construction_imgs.append(img)
            
        self.construction_static = pygame.image.load("./assets/mainmap/construction.png")
        self.construction_static = pygame.transform.scale(self.construction_static, (200, 200))
        
        # Load fireworks
        self.fireworks = []
        for i in range(1, 7):
            img = pygame.image.load(f"./assets/fireworks/fireworks{i}.png")
            img = pygame.transform.scale(img, (400, 500))
            self.fireworks.append(img)
            
        # Load final building image
        self.final_img = pygame.image.load(f"./assets/restaurant/r{index+1}.png")
        
    def upgrade(self):
        if self.level < 5:
            self.level += 1
            self.start_animation()
            
    def start_animation(self):
        self.animating = True
        self.animation_start = time.time()
        self.animation_frame = 0
        self.animation_cycle = 0
        if self.level < 5:
            self.animation_type = "construction"
        else:
            self.animation_type = "fireworks"
            
    def update(self):
        if not self.animating:
            return
            
        current_time = time.time()
        
        if self.animation_type == "construction":
            # Construction animation: 3 cycles of 5 frames, 0.2s each
            elapsed = current_time - self.animation_start
            total_frames = int(elapsed / 0.2)
            
            if total_frames >= 15:  # 3 cycles * 5 frames
                self.animating = False
            else:
                self.animation_frame = total_frames % 5
                self.animation_cycle = total_frames // 5
                
        elif self.animation_type == "fireworks":
            # Fireworks animation: 6 frames, 0.1s each
            elapsed = current_time - self.animation_start
            frame = int(elapsed / 0.1)
            
            if frame >= 6:
                self.animating = False
                self.showing_final = True
            else:
                self.animation_frame = frame
                
    def draw(self, screen, map_obj, restaurant1_level=0):
        screen_pos = map_obj.world_to_screen(self.center)
        
        if self.animating:
            if self.animation_type == "construction":
                # Draw construction animation
                img = self.construction_imgs[self.animation_frame]
                rect = img.get_rect(center=screen_pos)
                screen.blit(img, rect)
            elif self.animation_type == "fireworks":
                # Draw fireworks
                img = self.fireworks[self.animation_frame]
                rect = img.get_rect(center=screen_pos)
                screen.blit(img, rect)
        elif self.showing_final or self.level == 5 or restaurant1_level > 0:
            # Draw final building image when showing_final is True, level is 5, or Restaurant1 level > 0
            rect = self.final_img.get_rect(center=screen_pos)
            screen.blit(self.final_img, rect)
        elif self.level > 0 and self.level < 5:
            # Draw static construction image
            rect = self.construction_static.get_rect(center=screen_pos)
            screen.blit(self.construction_static, rect)

class Character:
    def __init__(self, char_type, spawn_pos):
        self.type = char_type
        self.pos = list(spawn_pos)
        # Choose a different destination than spawn position
        spawn_location = self.find_nearest_location(spawn_pos)
        possible_destinations = [loc for loc in LOCATIONS.keys() if loc != spawn_location]
        self.destination = random.choice(possible_destinations)
        self.path = []
        self.speed = 0.5
        self.spawn_time = time.time()
        self.state = "MOVING"
        self.visible = True
        self.arrival_time = None
        self.stay_duration = 3
        
        # Animation
        self.direction = 3
        self.frame = 0
        self.last_frame_change = time.time()
        self.frame_duration = 0.25
        
        # Load character sprites
        self.sprites = {}
        for direction in range(1, 5):
            self.sprites[direction] = []
            for frame in range(1, 5):
                img_path = f"./assets/characters/c{char_type}_{direction}-{frame}.png"
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, 
                                           (int(img.get_width() * 0.4), 
                                            int(img.get_height() * 0.4)))
                self.sprites[direction].append(img)
                
        # Load icon sprites
        self.icons = {
            "thumbsup": pygame.image.load("./assets/coin.png")
        }
        
        # Load restaurant emojis
        for emoji_key, emoji_path in RESTAURANT_EMOJIS.items():
            self.icons[emoji_key] = pygame.image.load(emoji_path)
        
        # Scale icons
        for key in self.icons:
            self.icons[key] = pygame.transform.scale(self.icons[key],
                                                    (int(self.icons[key].get_width() * 0.5),
                                                     int(self.icons[key].get_height() * 0.5)))
        
        # Calculate initial path
        self.calculate_path()
        
    def calculate_path(self):
        start = self.find_nearest_location(self.pos)
        end = self.destination
        self.path = self.bfs_pathfind(start, end)
        
    def find_nearest_location(self, pos):
        min_dist = float('inf')
        nearest = None
        for loc, loc_pos in LOCATIONS.items():
            dist = ((pos[0] - loc_pos[0])**2 + (pos[1] - loc_pos[1])**2)**0.5
            if dist < min_dist:
                min_dist = dist
                nearest = loc
        return nearest
        
    def bfs_pathfind(self, start, end):
        if start == end:
            return [end]
            
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in CONNECTIONS.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    if neighbor == end:
                        return new_path
                    queue.append((neighbor, new_path))
                    
        return []
        
    def update(self, buildings):
        current_time = time.time()
        
        # Update animation frame
        if current_time - self.last_frame_change > self.frame_duration:
            self.frame = (self.frame + 1) % 4
            self.last_frame_change = current_time
            
        # Handle different states
        if self.state == "AT_DESTINATION":
            if self.arrival_time and current_time - self.arrival_time > self.stay_duration:
                return False  # Remove character after celebration
                
        elif self.state == "MOVING":
            # Move along path
            if self.path:
                next_loc = LOCATIONS[self.path[0]]
                dx = next_loc[0] - self.pos[0]
                dy = next_loc[1] - self.pos[1]
                dist = (dx**2 + dy**2)**0.5
                
                if dist < 10:  # Reached waypoint
                    self.pos = list(next_loc)
                    arrived_at = self.path.pop(0)
                    
                    # Check if reached destination
                    if arrived_at == self.destination:
                        self.state = "AT_DESTINATION"
                        self.arrival_time = current_time
                        # Reward player with 20 coins for successful arrival
                        game_manager.update_player_resources(coins_delta=20)
                else:
                    # Move towards next waypoint
                    move_x = (dx / dist) * self.speed
                    move_y = (dy / dist) * self.speed
                    self.pos[0] += move_x
                    self.pos[1] += move_y
                    
                    # Update direction
                    if abs(dx) > abs(dy):
                        self.direction = 1 if dx < 0 else 2
                    else:
                        self.direction = 4 if dy < 0 else 3
                        
        return True
        
    def get_icon(self):
        if self.state == "AT_DESTINATION":
            return self.icons["thumbsup"]
        else:
            # Show destination emoji while moving
            return self.icons[self.destination]
        
    def draw(self, screen, map_obj, font):
        if not self.visible:
            return
            
        screen_pos = map_obj.world_to_screen(self.pos)
        
        # Draw character sprite
        sprite = self.sprites[self.direction][self.frame]
        char_rect = sprite.get_rect(center=screen_pos)
        screen.blit(sprite, char_rect)
        
        # Draw icon
        icon = self.get_icon()
        if icon:
            icon_rect = icon.get_rect(midbottom=char_rect.midtop)
            screen.blit(icon, icon_rect)

class UpgradeButton:
    def __init__(self, index):
        self.index = index
        self.pos = (50 + index * 100, 800)
        self.size = (90, 90)
        self.rect = pygame.Rect(self.pos, self.size)
        
        # Load icon
        self.icon = pygame.image.load(f"./assets/restaurant/r{index+1}_icon.png")
        self.icon = pygame.transform.scale(self.icon, (64, 64))
        
        # Progress bar
        self.progress_rect = pygame.Rect(self.pos[0], self.pos[1] - 24, 90, 18)
        
    def draw(self, screen, level):
        # Draw button background
        pygame.draw.rect(screen, BEIGE, self.rect)
        pygame.draw.rect(screen, GOLD, self.rect, 2)
        
        # Draw icon
        icon_rect = self.icon.get_rect(center=self.rect.center)
        screen.blit(self.icon, icon_rect)
        
        # Draw progress bar
        pygame.draw.rect(screen, GOLD, self.progress_rect, 2)
        
        # Draw progress cells
        cell_width = 18
        for i in range(5):
            cell_rect = pygame.Rect(self.progress_rect.x + i * cell_width,
                                   self.progress_rect.y,
                                   cell_width,
                                   self.progress_rect.height)
            if i < level:
                pygame.draw.rect(screen, GREEN, cell_rect)
            else:
                pygame.draw.rect(screen, RED, cell_rect)
            pygame.draw.rect(screen, GOLD, cell_rect, 1)
            
    def handle_click(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Restaurant1")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = get_chinese_font(20)
        self.level_font = get_chinese_font(30)
        self.ui_font = get_chinese_font(30)
        
        # Load game data
        game_manager.load_game_data()
        
        # Level system - load from save (completion count, not building level)
        self.R1 = game_manager.get_building_data('restaurant1').get('completion_count', 0)
        self.showing_congratulations = False
        self.congrats_rect = pygame.Rect(150, 400, 300, 200)
        self.ok_button_rect = pygame.Rect(250, 520, 100, 40)
        
        # Initialize game objects
        self.map = Map()
        
        # Create buildings and load their levels
        self.buildings = []
        for i, center in enumerate(BUILDING_CENTERS):
            building = Building(i, center)
            # Load level from save
            structure_id = f'r{i+1}'
            saved_level = game_manager.get_structure_level('restaurant1', structure_id)
            building.level = saved_level
            # If level is 5, set showing_final to True
            if saved_level == 5:
                building.showing_final = True
            self.buildings.append(building)
            
        # Create upgrade buttons
        self.upgrade_buttons = []
        for i in range(5):
            self.upgrade_buttons.append(UpgradeButton(i))
            
        # Back button
        self.back_button = pygame.image.load("./assets/back.png")
        self.back_button = pygame.transform.scale(self.back_button, (30, 30))
        self.back_rect = self.back_button.get_rect(topleft=(550, 50))
        
        # Characters
        self.characters = []
        self.last_spawn = time.time()
        self.spawn_interval = 1.0  # 1 second
        
    def spawn_character(self):
        current_time = time.time()
        # Apply spawn speed multiplier from island level
        spawn_multiplier = game_manager.get_spawn_speed_multiplier()
        adjusted_interval = self.spawn_interval / spawn_multiplier
        
        if current_time - self.last_spawn > adjusted_interval:
            char_type = random.randint(1, 9)
            spawn_location = random.choice(list(LOCATIONS.keys()))
            spawn_pos = LOCATIONS[spawn_location]
            character = Character(char_type, spawn_pos)
            # Apply movement speed multiplier
            character.speed *= game_manager.get_movement_speed_multiplier()
            self.characters.append(character)
            self.last_spawn = current_time
            
    def check_all_level_5(self):
        for building in self.buildings:
            if building.level < 5:
                return False
        return True
    
    def reset_building_levels(self):
        for i, building in enumerate(self.buildings):
            building.level = 0
            # Reset in save file
            structure_id = f'r{i+1}'
            structure = game_manager.get_building_data('restaurant1')['structures'][structure_id]
            structure['level'] = 0
            structure['is_built'] = False
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if not self.showing_congratulations:
                self.map.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check congratulations OK button
                if self.showing_congratulations:
                    if self.ok_button_rect.collidepoint(event.pos):
                        self.showing_congratulations = False
                        self.R1 += 1
                        # Update in save file (save to completion_count, not building_level)
                        game_manager.game_data['buildings']['restaurant1']['completion_count'] = self.R1
                        game_manager._update_island_level()
                        game_manager.save_game_data()
                        self.reset_building_levels()
                    return
                
                # Check back button
                if self.back_rect.collidepoint(event.pos):
                    subprocess.Popen(["python3", "main_game.py"])
                    self.running = False
                    return
                        
                # Check upgrade buttons
                for i, btn in enumerate(self.upgrade_buttons):
                    if btn.handle_click(event.pos):
                        # Try to upgrade through game manager
                        structure_id = f'r{i+1}'
                        if game_manager.upgrade_structure('restaurant1', structure_id):
                            self.buildings[i].upgrade()
                            self.map.center_on_building(BUILDING_CENTERS[i])
                            
                            # Check if all buildings are now level 5
                            if self.check_all_level_5():
                                self.showing_congratulations = True
                        else:
                            # Not enough coins
                            print("Not enough coins to upgrade!")
                        break
                        
    def update(self):
        # Update passive income every minute
        game_manager.update_passive_income()
        
        self.spawn_character()
        self.map.update()
        
        # Update buildings
        for building in self.buildings:
            building.update()
            
        # Update characters
        self.characters = [char for char in self.characters if char.update(self.buildings)]
        
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw map
        self.map.draw(self.screen)
        
        # Draw buildings - first pass: draw final buildings and static construction
        for building in self.buildings:
            if building.showing_final or building.level == 5 or self.R1 > 0 or (building.level > 0 and building.level < 5 and not building.animating):
                building.draw(self.screen, self.map, self.R1)
        
        # Draw characters
        for character in self.characters:
            character.draw(self.screen, self.map, self.font)
            
        # Draw buildings - second pass: draw animations on top
        for building in self.buildings:
            if building.animating:
                building.draw(self.screen, self.map, self.R1)
            
        # Draw UI
        # Draw level indicator in top-left
        level_text = self.level_font.render(f"Level = {self.R1}", True, RED)
        self.screen.blit(level_text, (10, 10))
        
        # Draw MP and Coins display
        self._draw_resources()
        
        # Back button
        self.screen.blit(self.back_button, self.back_rect)
        
        # Upgrade buttons
        for i, btn in enumerate(self.upgrade_buttons):
            btn.draw(self.screen, self.buildings[i].level)
            
        # Draw congratulations popup if needed
        if self.showing_congratulations:
            # Draw popup background
            pygame.draw.rect(self.screen, WHITE, self.congrats_rect)
            pygame.draw.rect(self.screen, BLACK, self.congrats_rect, 3)
            
            # Draw congratulations text
            congrats_text = self.font.render("Congratulations,", True, BLACK)
            text_rect = congrats_text.get_rect(center=(self.congrats_rect.centerx, self.congrats_rect.y + 50))
            self.screen.blit(congrats_text, text_rect)
            
            upgrade_text = self.font.render("You've Upgraded!", True, BLACK)
            text_rect = upgrade_text.get_rect(center=(self.congrats_rect.centerx, self.congrats_rect.y + 80))
            self.screen.blit(upgrade_text, text_rect)
            
            # Draw OK button
            pygame.draw.rect(self.screen, GOLD, self.ok_button_rect)
            pygame.draw.rect(self.screen, BLACK, self.ok_button_rect, 2)
            ok_text = self.font.render("OK", True, BLACK)
            ok_rect = ok_text.get_rect(center=self.ok_button_rect.center)
            self.screen.blit(ok_text, ok_rect)
            
        pygame.display.flip()
        
    def _draw_resources(self):
        """Draw MP and Coins at top of screen"""
        mp, coins = game_manager.get_player_resources()
        
        # Draw background for resources
        resource_bg = pygame.Surface((200, 60))
        resource_bg.fill((200, 200, 200))
        resource_bg.set_alpha(200)
        self.screen.blit(resource_bg, (WINDOW_WIDTH - 210, 10))
        
        # Draw MP
        mp_text = self.ui_font.render(f"MP: {int(mp)}", True, (0, 0, 255))
        self.screen.blit(mp_text, (WINDOW_WIDTH - 200, 15))
        
        # Draw Coins
        coins_text = self.ui_font.render(f"Coins: {int(coins)}", True, GOLD)
        self.screen.blit(coins_text, (WINDOW_WIDTH - 200, 40))
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()