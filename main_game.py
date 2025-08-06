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

# Location coordinates
LOCATIONS = {
    "B1": (448, 518),
    "C2": (417, 507),
    "C3": (271, 610),
    "C4": (479, 401),
    "R1": (237, 578),
    "A1": (327, 666),
    "C1": (472, 241),
    "H1": (342, 128),
    "T1": (638, 417),
    "T2": (641, 193)
}

# Building center coordinates
BUILDINGS = {
    "BT1": {"center": (685, 377), "arrival": "T1", "name": "Temple1"},
    "BT2": {"center": (730, 129), "arrival": "T2", "name": "Temple2"},
    "BH1": {"center": (382, 74), "arrival": "H1", "name": "Hotel1"},
    "BA1": {"center": (364, 737), "arrival": "A1", "name": "Apt1"},
    "BR1": {"center": (177, 532), "arrival": "R1", "name": "Restaurant1"}
}

# Path connections (bidirectional)
CONNECTIONS = {
    "B1": ["C2"],
    "C2": ["B1", "C3", "C4"],
    "C3": ["C2", "C4", "R1", "A1"],
    "C4": ["C3", "C2", "C1", "T1"],
    "C1": ["C4", "H1", "T2"],
    "R1": ["C3"],
    "A1": ["C3"],
    "H1": ["C1"],
    "T1": ["C4"],
    "T2": ["C1"]
}

# Building info
BUILDING_INFO = {
    "BT1": {
        "text": "Puto Temples, composed of three temple in this location, is one the most visited place.",
        "script": "temple1.py"
    },
    "BT2": {
        "text": "Buddha's garden, a sacred garden blessed by the ancient Buddha.",
        "script": "temple2.py"
    },
    "BR1": {
        "text": "Welcome to our food court, we have 5 restaurants at this location, please come in!",
        "script": "restaurant1.py"
    },
    "BA1": {
        "text": "Apartment is a quiet area for all the employees to rest, it features an apartment complex, a coffee, a gym and a cafeteria!",
        "script": "apt1.py"
    },
    "BH1": {
        "text": "Hotel area is on the west side of the island, consist of 5 hotels from a 3 star to 5 star!",
        "script": "hotel1.py"
    }
}

class Map:
    def __init__(self):
        self.background = pygame.image.load("./assets/mainmap/mainmap.png")
        self.bg_rect = self.background.get_rect()
        self.bg_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.drag_start = None
        self.dragging = False
        self.animating = False
        self.anim_start_pos = None
        self.anim_target_pos = None
        self.anim_start_time = None
        self.anim_duration = 0.5  # 0.5 seconds for smooth animation
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drag_start = event.pos
            self.dragging = True
            self.animating = False  # Cancel animation if dragging
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
    def __init__(self, key, data):
        self.key = key
        self.center = data["center"]
        self.arrival = data["arrival"]
        self.name = data["name"]
        self.level = 0
        self.save_name = self._get_save_name()
        self.icon = pygame.image.load("./assets/emptyland.png")
        self.icon = pygame.transform.scale(self.icon, 
                                         (int(self.icon.get_width() * 0.5), 
                                          int(self.icon.get_height() * 0.5)))
        self.rect = self.icon.get_rect(center=self.center)
        self.button_rect = pygame.Rect(0, 0, 150, 150)
        self.button_rect.center = self.center
        self.showing_upgrade = False
        self.upgrade_button = None
        
    def _get_save_name(self):
        # Convert building name to save file format
        name_map = {
            "Temple1": "temple1",
            "Temple2": "temple2",
            "Hotel1": "hotel1",
            "Apt1": "apt1",
            "Restaurant1": "restaurant1"
        }
        return name_map.get(self.name, self.name.lower())
        
    def upgrade(self):
        self.level = 1
        
    def update_icon(self):
        """Update building icon based on completion status"""
        building_data = game_manager.get_building_data(self.save_name)
        completion_count = building_data.get('completion_count', 0)
        
        if completion_count > 0:
            # Building has been completed - show upgraded icon from mainmap folder
            if self.name == "Temple1":
                icon_path = "./assets/mainmap/t1.png"
            elif self.name == "Temple2":
                icon_path = "./assets/mainmap/t2.png"
            elif self.name == "Hotel1":
                icon_path = "./assets/mainmap/h1.png"
            elif self.name == "Restaurant1":
                icon_path = "./assets/mainmap/r1.png"
            elif self.name == "Apt1":
                icon_path = "./assets/mainmap/a1.png"
            else:
                icon_path = "./assets/emptyland.png"
        else:
            # Building not completed - show empty land
            icon_path = "./assets/emptyland.png"
            
        try:
            self.icon = pygame.image.load(icon_path)
            # Only scale empty land - keep completed buildings at original size
            if completion_count == 0:
                self.icon = pygame.transform.scale(self.icon, 
                                                 (int(self.icon.get_width() * 0.5), 
                                                  int(self.icon.get_height() * 0.5)))
        except:
            # Fallback to empty land if icon doesn't exist
            self.icon = pygame.image.load("./assets/emptyland.png")
            self.icon = pygame.transform.scale(self.icon, 
                                             (int(self.icon.get_width() * 0.5), 
                                              int(self.icon.get_height() * 0.5)))
        
    def handle_click(self, screen_pos, map_obj):
        world_pos = (screen_pos[0] - map_obj.bg_rect.x, 
                    screen_pos[1] - map_obj.bg_rect.y)
        if self.button_rect.collidepoint(world_pos):
            map_obj.center_on_building(self.center)
            return True
        return False
        
    def draw(self, screen, map_obj):
        screen_rect = self.icon.get_rect(center=map_obj.world_to_screen(self.center))
        screen.blit(self.icon, screen_rect)

class Character:
    def __init__(self, char_type, spawn_pos):
        self.type = char_type
        self.pos = list(spawn_pos)
        self.destination = random.choice(["R1", "H1", "T2", "T1", "A1"])
        self.path = []
        self.speed = 0.5
        self.spawn_time = time.time()
        self.lifetime = 120  # 2 minutes
        self.state = "MOVING"  # MOVING, AT_DESTINATION, DISAPPOINTED, SATISFIED_LEAVING
        self.visible = True
        self.arrival_time = None
        self.stay_duration = 20  # 20 seconds
        self.original_destination = self.destination  # Store original destination for icon logic
        
        # Animation
        self.direction = 3  # 1=left, 2=right, 3=down, 4=up
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
                                           (int(img.get_width() * 0.5), 
                                            int(img.get_height() * 0.5)))
                self.sprites[direction].append(img)
                
        # Load icon sprites
        self.icons = {
            "sleepy": pygame.image.load("./assets/sleepy.png"),
            "burger": pygame.image.load("./assets/burger.png"),
            "budda": pygame.image.load("./assets/budda.png"),
            "bye": pygame.image.load("./assets/bye.png"),
            "thumbsup": pygame.image.load("./assets/coin.png")
        }
        
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
        
        # Check lifetime
        if current_time - self.spawn_time > self.lifetime and self.destination != "B1":
            self.destination = "B1"
            self.calculate_path()
            
        # Update animation frame
        if current_time - self.last_frame_change > self.frame_duration:
            self.frame = (self.frame + 1) % 4
            self.last_frame_change = current_time
            
        # Handle different states
        if self.state == "AT_DESTINATION":
            if self.arrival_time and current_time - self.arrival_time > self.stay_duration:
                self.visible = True
                self.state = "SATISFIED_LEAVING"
                # Choose new destination or return
                if current_time - self.spawn_time > self.lifetime:
                    self.destination = "B1"
                else:
                    self.destination = random.choice(["R1", "H1", "T2", "T1", "A1"])
                    self.original_destination = self.destination
                self.calculate_path()
                
        elif self.state == "MOVING" or self.state == "DISAPPOINTED" or self.state == "SATISFIED_LEAVING":
            # Move along path
            if self.path:
                next_loc = LOCATIONS[self.path[0]]
                dx = next_loc[0] - self.pos[0]
                dy = next_loc[1] - self.pos[1]
                dist = (dx**2 + dy**2)**0.5
                
                if dist < 10:  # Reached waypoint
                    self.pos = list(next_loc)
                    arrived_at = self.path.pop(0)
                    
                    # Check if reached main road and was satisfied leaving
                    if self.state == "SATISFIED_LEAVING" and arrived_at in ["C1", "C2", "C3", "C4"]:
                        self.state = "MOVING"  # Change back to normal state
                    
                    # Check if reached destination
                    if arrived_at == self.destination:
                        if self.destination == "B1":
                            return False  # Remove character
                        else:
                            # Check structure completion count - if > 0, always satisfied
                            structure_completion = 0
                            if self.destination == "T1":
                                structure_completion = game_manager.get_building_data('temple1').get('completion_count', 0)
                            elif self.destination == "T2":
                                structure_completion = game_manager.get_building_data('temple2').get('completion_count', 0)
                            elif self.destination == "R1":
                                structure_completion = game_manager.get_building_data('restaurant1').get('completion_count', 0)
                            elif self.destination == "H1":
                                structure_completion = game_manager.get_building_data('hotel1').get('completion_count', 0)
                            elif self.destination == "A1":
                                structure_completion = game_manager.get_building_data('apt1').get('completion_count', 0)
                            
                            if structure_completion > 0:
                                # Structure has been completed at least once - always satisfied
                                self.state = "AT_DESTINATION"
                                self.visible = False
                                self.arrival_time = current_time
                                # Reward player with 10 coins for successful arrival
                                game_manager.update_player_resources(coins_delta=10)
                            else:
                                # Structure never completed - check building level
                                building_level = self.get_building_level(self.destination, buildings)
                                if building_level >= 1:
                                    self.state = "AT_DESTINATION"
                                    self.visible = False
                                    self.arrival_time = current_time
                                    # Reward player with 10 coins for successful arrival
                                    game_manager.update_player_resources(coins_delta=10)
                                else:
                                    self.state = "DISAPPOINTED"
                                    self.destination = "B1"
                                    self.calculate_path()
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
        
    def get_building_level(self, arrival_point, buildings):
        for building in buildings:
            if building.arrival == arrival_point:
                return building.level
        return 0
        
    def get_icon(self):
        # If satisfied and leaving, show thumbs up until reaching main road
        if self.state == "SATISFIED_LEAVING":
            return self.icons["thumbsup"]
        
        # If disappointed, keep original icon (don't change to bye)
        if self.state == "DISAPPOINTED":
            if self.original_destination in ["H1", "A1"]:
                return self.icons["sleepy"]
            elif self.original_destination == "R1":
                return self.icons["burger"]
            elif self.original_destination in ["T1", "T2"]:
                return self.icons["budda"]
        
        # Normal icon logic
        if self.destination in ["H1", "A1"]:
            return self.icons["sleepy"]
        elif self.destination == "R1":
            return self.icons["burger"]
        elif self.destination in ["T1", "T2"]:
            return self.icons["budda"]
        elif self.destination == "B1" and self.state != "DISAPPOINTED":
            return self.icons["bye"]
        return None
        
    def get_disappointment_text(self):
        if self.original_destination in ["H1", "A1"]:
            return "No Hotel!"
        elif self.original_destination == "R1":
            return "No Food!"
        elif self.original_destination in ["T1", "T2"]:
            return "No Buddha!"
        return ""
        
    def draw(self, screen, map_obj, font):
        if not self.visible:
            return
            
        screen_pos = map_obj.world_to_screen(self.pos)
        
        # Draw character sprite
        sprite = self.sprites[self.direction][self.frame]
        char_rect = sprite.get_rect(center=screen_pos)
        screen.blit(sprite, char_rect)
        
        # Draw disappointment text
        if self.state == "DISAPPOINTED":
            text = font.render(self.get_disappointment_text(), True, RED)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 40))
            screen.blit(text, text_rect)
        else:
            # Only draw icon if not disappointed
            icon = self.get_icon()
            if icon:
                icon_rect = icon.get_rect(midbottom=char_rect.midtop)
                screen.blit(icon, icon_rect)

class UpgradeButton:
    def __init__(self, building_key):
        self.building_key = building_key
        self.info = BUILDING_INFO[building_key]
        self.button_img = pygame.image.load("./assets/upgrade_button.png")
        self.rect = self.button_img.get_rect()
        self.visible = False
        self.building_center = BUILDINGS[building_key]["center"]
        
    def show(self):
        self.visible = True
        self.rect.center = (self.building_center[0], self.building_center[1] + 60)
        
    def hide(self):
        self.visible = False
        
    def handle_click(self, screen_pos, map_obj):
        if not self.visible:
            return False
            
        world_pos = (screen_pos[0] - map_obj.bg_rect.x, 
                    screen_pos[1] - map_obj.bg_rect.y)
                    
        # Check if click is on right half of button
        button_rect = pygame.Rect(self.rect.x + 100, self.rect.y, 100, self.rect.height)
        if button_rect.collidepoint(world_pos):
            # Open the script
            script_path = os.path.join(os.path.dirname(__file__), self.info["script"])
            subprocess.Popen(["python3", script_path])
            return True
        return False
        
    def draw(self, screen, map_obj, font):
        if not self.visible:
            return
            
        screen_rect = self.rect.copy()
        screen_rect.center = map_obj.world_to_screen(self.rect.center)
        screen.blit(self.button_img, screen_rect)
        
        # Draw text on left side
        text_lines = []
        words = self.info["text"].split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < 90:
                current_line = test_line
            else:
                if current_line:
                    text_lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            text_lines.append(current_line.strip())
            
        y_offset = screen_rect.y + 10
        for line in text_lines:
            text_surf = font.render(line, True, BLACK)
            screen.blit(text_surf, (screen_rect.x + 5, y_offset))
            y_offset += 15

class UIButton:
    def __init__(self, center, size, image_path, script):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=center)
        self.script = script
        
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            script_path = os.path.join(os.path.dirname(__file__), self.script)
            subprocess.Popen(["python3", script_path])
            return True
        return False
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Puto Island Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = get_chinese_font(12)
        self.ui_font = get_chinese_font(30)
        
        # Load game data
        game_manager.load_game_data()
        
        # Initialize game objects
        self.map = Map()
        self.buildings = []
        self.upgrade_buttons = {}
        
        # Create buildings
        for key, data in BUILDINGS.items():
            building = Building(key, data)
            building.update_icon()  # Set initial icon based on completion status
            self.buildings.append(building)
            self.upgrade_buttons[key] = UpgradeButton(key)
            
        # Characters
        self.characters = []
        self.last_spawn = time.time()
        self.spawn_interval = random.uniform(1, 10)
        
        # UI Buttons
        self.ui_buttons = [
            UIButton((300, 900), (130, 135), "./assets/mainmap/turn.png", "zjt.py"),
            UIButton((450, 900), (110, 120), "./assets/mainmap/ask.png", "ask.py"),
            UIButton((150, 900), (110, 133), "./assets/mainmap/pick.png", "pick.py")
        ]
        
        # Initialize building levels from save data
        self._load_building_levels()
        
        # Timer for real-time income
        self.last_income_update = time.time()
        
    def spawn_character(self):
        current_time = time.time()
        # Apply spawn speed multiplier from island level
        spawn_multiplier = game_manager.get_spawn_speed_multiplier()
        adjusted_interval = self.spawn_interval / spawn_multiplier
        
        if current_time - self.last_spawn > adjusted_interval:
            char_type = random.randint(1, 9)
            character = Character(char_type, LOCATIONS["B1"])
            # Apply movement speed multiplier
            character.speed *= game_manager.get_movement_speed_multiplier()
            self.characters.append(character)
            self.last_spawn = current_time
            self.spawn_interval = random.uniform(1, 10)
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            self.map.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check UI buttons first
                ui_clicked = False
                for button in self.ui_buttons:
                    if button.handle_click(event.pos):
                        ui_clicked = True
                        self.running = False  # Exit main game when sub-game opens
                        break
                        
                if not ui_clicked:
                    # Check upgrade buttons
                    upgrade_clicked = False
                    for key, upgrade_btn in self.upgrade_buttons.items():
                        if upgrade_btn.handle_click(event.pos, self.map):
                            # Find the building and upgrade it
                            for building in self.buildings:
                                if building.key == key:
                                    building.upgrade()
                                    upgrade_btn.hide()
                                    # Update save file to mark building as upgraded
                                    building_data = game_manager.get_building_data(building.save_name)
                                    if building_data:
                                        building_data['is_upgraded'] = True
                                        game_manager.save_game_data()
                                    break
                            upgrade_clicked = True
                            self.running = False  # Exit main game when sub-game opens
                            break
                            
                    if not upgrade_clicked:
                        # Check building clicks
                        building_clicked = False
                        for building in self.buildings:
                            if building.handle_click(event.pos, self.map):
                                # Hide all upgrade buttons
                                for btn in self.upgrade_buttons.values():
                                    btn.hide()
                                # Show this building's upgrade button
                                self.upgrade_buttons[building.key].show()
                                building_clicked = True
                                break
                                
                        if not building_clicked:
                            # Click on empty space - hide all upgrade buttons
                            for btn in self.upgrade_buttons.values():
                                btn.hide()
                                
    def update(self):
        # Update passive income every minute
        game_manager.update_passive_income()
        
        self.spawn_character()
        
        # Update map animation
        self.map.update()
        
        # Update characters
        self.characters = [char for char in self.characters if char.update(self.buildings)]
        
        # Update building icons based on completion status
        for building in self.buildings:
            building.update_icon()
        
        # Update real-time income
        self._update_income()
        
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw map
        self.map.draw(self.screen)
        
        # Draw buildings
        for building in self.buildings:
            building.draw(self.screen, self.map)
            
        # Draw characters
        for character in self.characters:
            character.draw(self.screen, self.map, self.font)
            
        # Draw upgrade buttons
        for upgrade_btn in self.upgrade_buttons.values():
            upgrade_btn.draw(self.screen, self.map, self.font)
            
        # Draw UI buttons
        for button in self.ui_buttons:
            button.draw(self.screen)
            
        # Draw MP and Coins display
        self._draw_resources()
        
        # Draw Island Level
        self._draw_island_level()
            
        pygame.display.flip()
        
    def _load_building_levels(self):
        """Load building levels from save data"""
        for building in self.buildings:
            building_data = game_manager.get_building_data(building.save_name)
            if building_data and building_data.get('is_upgraded'):
                building.level = 1
                
    def _draw_resources(self):
        """Draw MP and Coins at top of screen"""
        mp, coins = game_manager.get_player_resources()
        
        # Draw background for resources
        resource_bg = pygame.Surface((200, 40))
        resource_bg.fill((200, 200, 200))
        resource_bg.set_alpha(200)
        self.screen.blit(resource_bg, (WINDOW_WIDTH - 210, 10))
        
        # Draw MP
        mp_text = self.ui_font.render(f"MP: {int(mp)}", True, (0, 0, 255))
        self.screen.blit(mp_text, (WINDOW_WIDTH - 200, 15))
        
        # Draw Coins
        coins_text = self.ui_font.render(f"Coins: {int(coins)}", True, (255, 215, 0))
        self.screen.blit(coins_text, (WINDOW_WIDTH - 200, 35))
        
    def _draw_island_level(self):
        """Draw island level at top left"""
        island_level = game_manager.get_island_level()
        level_text = self.ui_font.render(f"Island Level: {island_level}", True, RED)
        self.screen.blit(level_text, (10, 10))
        
    def _update_income(self):
        """Update real-time income collection"""
        current_time = time.time()
        if current_time - self.last_income_update > 1:  # Update every second
            # Collect income from all buildings
            for building in self.buildings:
                if building.level >= 1:
                    game_manager.collect_income(building.save_name)
                    
            # Consume MP for Workers House
            game_manager.consume_mp('apt1')
            
            self.last_income_update = current_time
        
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