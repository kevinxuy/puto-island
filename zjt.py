#!/usr/bin/env python3
import pygame
import time
import subprocess
import os
from game_manager import game_manager
from font_helper import get_chinese_font, get_default_font
try:
    import cv2
except ImportError:
    cv2 = None

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 1000
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Speed definitions (playback rates)
SPEED_RATES = {
    0: 0.0,    # V0: Paused
    1: 0.2,    # V1: 35 seconds (7/35 = 0.2)
    2: 0.28,   # V2: 25 seconds (7/25 = 0.28)
    3: 0.5,    # V3: 14 seconds (7/14 = 0.5)  
    4: 1.0     # V4: 7 seconds (7/7 = 1.0)
}

# Timeout rules for speed reduction (in seconds)
SPEED_TIMEOUTS = {
    4: [10, 5, 5],  # V4: 10s->V3, 5s->V2, 5s->V1
    3: [10, 5],     # V3: 10s->V2, 5s->V1
    2: [10],        # V2: 10s->V1
    1: [10]         # V1: 10s->V0
}

class VideoPlayer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.current_speed = 0
        self.is_playing = False
        self.video_length = 7.0  # 7 seconds
        self.current_time = 0.0
        self.last_frame_time = time.time()
        self.loops_completed = 0
        self.frames = []
        self.current_frame_index = 0
        
        # Setup video display to fit window first
        self.video_width = WINDOW_WIDTH  # Full width
        self.video_height = WINDOW_HEIGHT  # Full height
        self.video_rect = pygame.Rect(0, 0, self.video_width, self.video_height)
        
        # Create video surface
        self.video_surface = pygame.Surface((self.video_width, self.video_height))
        
        # Now load actual video
        self.load_video()
        
    def load_video(self):
        """Load video frames using OpenCV if available"""
        if cv2 is None or not os.path.exists(self.video_path):
            # Create placeholder frames if no video or OpenCV
            self.create_placeholder_frames()
            return
            
        try:
            cap = cv2.VideoCapture(self.video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_length = frame_count / fps if fps > 0 else 7.0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize to fit window
                frame = cv2.resize(frame, (self.video_width, self.video_height))
                # Convert to pygame surface
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.frames.append(frame_surface)
                
            cap.release()
            
            if not self.frames:
                self.create_placeholder_frames()
                
        except Exception as e:
            print(f"Error loading video: {e}")
            self.create_placeholder_frames()
            
    def create_placeholder_frames(self):
        """Create animated placeholder frames"""
        # Create 60 frames for smooth animation (assuming 60fps)
        for i in range(60):
            frame = pygame.Surface((self.video_width, self.video_height))
            # Create a spinning effect
            angle = (i * 6) % 360  # 6 degrees per frame
            color_intensity = int(128 + 127 * abs(pygame.math.Vector2(1, 0).rotate(angle).x))
            frame.fill((color_intensity // 2, color_intensity // 2, color_intensity))
            
            # Draw ZJT text
            font = get_chinese_font(72)
            text = font.render("转经筒", True, WHITE)
            text_rect = text.get_rect(center=(self.video_width//2, self.video_height//2))
            frame.blit(text, text_rect)
            
            # Draw rotation indicator
            center = (self.video_width//2, self.video_height//2 + 100)
            end_point = pygame.math.Vector2(50, 0).rotate(angle) + center
            pygame.draw.line(frame, WHITE, center, end_point, 5)
            pygame.draw.circle(frame, WHITE, center, 10)
            
            self.frames.append(frame)
            
        # Set video length for placeholder
        self.video_length = 7.0
        
    def update(self, dt):
        if self.is_playing and self.current_speed > 0 and self.frames:
            # Update video time based on speed
            self.current_time += dt * SPEED_RATES[self.current_speed]
            
            # Update frame index based on time
            if self.video_length > 0:
                frame_progress = (self.current_time / self.video_length) % 1.0
                self.current_frame_index = int(frame_progress * len(self.frames))
            
            # Check if video completed
            if self.current_time >= self.video_length:
                self.current_time = 0.0
                self.loops_completed += 1
                self.current_frame_index = 0
                return True  # Signal completion
        return False
        
    def set_speed(self, speed):
        self.current_speed = speed
        self.is_playing = speed > 0
        
    def draw(self, screen):
        # Draw current video frame
        if self.frames and 0 <= self.current_frame_index < len(self.frames):
            screen.blit(self.frames[self.current_frame_index], self.video_rect)
        else:
            # Fallback
            self.video_surface.fill(GRAY)
            font = pygame.font.Font(None, 36)
            text = font.render("ZJT Video", True, WHITE)
            text_rect = text.get_rect(center=(self.video_width//2, self.video_height//2))
            self.video_surface.blit(text, text_rect)
            screen.blit(self.video_surface, self.video_rect)
        
        # No border needed since video fills entire screen
        
        # Draw current time at bottom of screen (over video)
        time_font = pygame.font.Font(None, 24)
        time_text = time_font.render(f"{self.current_time:.1f}s / {self.video_length:.1f}s", True, WHITE)
        time_rect = time_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 200))
        # Add background for better visibility
        bg_rect = time_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        screen.blit(time_text, time_rect)

class MPBar:
    def __init__(self):
        self.mp = 0
        self.max_mp = 20
        self.bar_width = 400
        self.bar_height = 20
        self.cell_width = self.bar_width // self.max_mp
        self.pos = (WINDOW_WIDTH // 2 - self.bar_width // 2, WINDOW_HEIGHT - 150)
        
        # Track video completions for MP generation
        self.video_completions = 0
        
    def add_mp(self):
        """Add MP when video completes - using real economy system"""
        self.video_completions += 1
        # Generate 1 MP per video completion (affected by temple bonuses)
        mp_generated = game_manager.generate_mp(1.0)
        
        # Update visual MP bar (for display purposes)
        current_mp, _ = game_manager.get_player_resources()
        self.mp = min(int(current_mp), self.max_mp)
            
    def draw(self, screen):
        # Draw MP label
        font = pygame.font.Font(None, 24)
        font.set_bold(True)
        mp_text = font.render("MP", True, WHITE)
        screen.blit(mp_text, (self.pos[0] - 40, self.pos[1]))
        
        # Draw MP bar cells
        for i in range(self.max_mp):
            cell_rect = pygame.Rect(
                self.pos[0] + i * self.cell_width,
                self.pos[1],
                self.cell_width - 1,  # -1 for border
                self.bar_height
            )
            
            # Color based on MP
            if i < self.mp:
                color = RED
            else:
                color = LIGHT_BLUE
                
            pygame.draw.rect(screen, color, cell_rect)
            pygame.draw.rect(screen, BLACK, cell_rect, 1)

class SpeedDisplay:
    def __init__(self):
        self.pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        
    def draw(self, screen, current_speed):
        font = pygame.font.Font(None, 20)
        speed_text = font.render(f"Speed: V{current_speed}", True, WHITE)
        text_rect = speed_text.get_rect(center=self.pos)
        screen.blit(speed_text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("ZJT - 转经筒修行")
        self.clock = pygame.time.Clock()
        self.running = True
        self.ui_font = pygame.font.Font(None, 30)
        
        # Load game data
        game_manager.load_game_data()
        
        # Game components
        self.video_player = VideoPlayer("./assets/zjt.mp4")
        self.mp_bar = MPBar()
        self.speed_display = SpeedDisplay()
        
        # Input handling
        self.dragging = False
        self.drag_start = None
        self.last_input_time = time.time()
        self.drag_threshold = 30
        self.last_speed_increase_time = 0
        self.speed_increase_cooldown = 0.2  # 200ms between speed increases
        
        # Speed management
        self.current_speed = 0
        self.speed_reduction_timers = []
        
        # Load back button
        try:
            self.back_button = pygame.image.load("./assets/back.png")
            self.back_button = pygame.transform.scale(self.back_button, (50, 50))
        except:
            # Fallback if image doesn't exist
            self.back_button = pygame.Surface((50, 50))
            self.back_button.fill(GRAY)
            
        self.back_rect = self.back_button.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check back button
                    if self.back_rect.collidepoint(event.pos):
                        # Return to main map
                        subprocess.Popen(["python3", "main_game.py"])
                        self.running = False
                        return
                        
                    # Start drag
                    self.dragging = True
                    self.drag_start = event.pos
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.drag_start:
                    # Check horizontal drag distance
                    dx = abs(event.pos[0] - self.drag_start[0])
                    current_time = time.time()
                    
                    # Allow speed increase if we've dragged far enough and enough time has passed
                    if (dx > self.drag_threshold and 
                        current_time - self.last_speed_increase_time > self.speed_increase_cooldown):
                        self.increase_speed()
                        self.last_speed_increase_time = current_time
                        self.drag_start = event.pos  # Reset for next increment
                        
    def increase_speed(self):
        if self.current_speed < 4:
            self.current_speed += 1
            self.video_player.set_speed(self.current_speed)
            self.last_input_time = time.time()
            self.setup_speed_reduction_timers()
            
    def setup_speed_reduction_timers(self):
        """Setup timers for automatic speed reduction"""
        self.speed_reduction_timers = []
        current_time = time.time()
        
        if self.current_speed in SPEED_TIMEOUTS:
            cumulative_time = 0
            for timeout in SPEED_TIMEOUTS[self.current_speed]:
                cumulative_time += timeout
                self.speed_reduction_timers.append(current_time + cumulative_time + (time.time() - self.last_input_time))
                
    def update_speed_reduction(self):
        """Handle automatic speed reduction based on inactivity"""
        current_time = time.time()
        inactive_time = current_time - self.last_input_time
        
        # Check speed reduction rules
        if self.current_speed == 4:
            if inactive_time >= 20:  # 10 + 5 + 5
                self.reduce_speed_to(1)
            elif inactive_time >= 15:  # 10 + 5
                self.reduce_speed_to(2)
            elif inactive_time >= 10:
                self.reduce_speed_to(3)
                
        elif self.current_speed == 3:
            if inactive_time >= 15:  # 10 + 5
                self.reduce_speed_to(1)
            elif inactive_time >= 10:
                self.reduce_speed_to(2)
                
        elif self.current_speed == 2:
            if inactive_time >= 10:
                self.reduce_speed_to(1)
                
        elif self.current_speed == 1:
            if inactive_time >= 10:
                self.reduce_speed_to(0)
                
    def reduce_speed_to(self, new_speed):
        if self.current_speed != new_speed:
            self.current_speed = new_speed
            self.video_player.set_speed(self.current_speed)
            self.last_input_time = time.time()  # Reset timer
            
    def update(self):
        # Update passive income every minute
        game_manager.update_passive_income()
        
        dt = self.clock.get_time() / 1000.0  # Delta time in seconds
        
        # Update video player
        if self.video_player.update(dt):
            # Video completed, add MP
            self.mp_bar.add_mp()
            
        # Update speed reduction
        self.update_speed_reduction()
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw video
        self.video_player.draw(self.screen)
        
        # Draw MP bar
        self.mp_bar.draw(self.screen)
        
        # Draw speed display
        self.speed_display.draw(self.screen, self.current_speed)
        
        # Draw back button
        self.screen.blit(self.back_button, self.back_rect)
        
        # Draw instructions (for development)
        font = pygame.font.Font(None, 20)
        instruction = font.render("Drag horizontally to increase speed", True, WHITE)
        self.screen.blit(instruction, (10, WINDOW_HEIGHT - 50))
        
        # Draw loops completed
        loops_text = font.render(f"Loops completed: {self.video_player.loops_completed}", True, WHITE)
        self.screen.blit(loops_text, (10, WINDOW_HEIGHT - 30))
        
        # Draw MP and Coins display
        self._draw_resources()
        
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
        coins_text = self.ui_font.render(f"Coins: {int(coins)}", True, (255, 215, 0))
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