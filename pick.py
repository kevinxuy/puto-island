#!/usr/bin/env python3
import pygame
import cv2
import random
import os
import sys
import subprocess
from font_helper import get_chinese_font, get_default_font

pygame.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 1000
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pick Game")

clock = pygame.time.Clock()

class VideoPlayer:
    def __init__(self, video_path, loop=False):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        self.playing = False
        self.loop = loop
        
    def play(self):
        self.playing = True
        
    def stop(self):
        self.playing = False
        self.cap.release()
        
    def get_frame(self):
        if not self.playing:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            if self.loop:
                self.cap.release()
                self.cap = cv2.VideoCapture(self.video_path)
                ret, frame = self.cap.read()
                if not ret:
                    self.playing = False
                    return None
            else:
                self.playing = False
                return None
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        return frame
        
    def is_playing(self):
        return self.playing

class Button:
    def __init__(self, image_path, position):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(center=position)
        self.visible = True
        
    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect)
            
    def is_clicked(self, pos):
        return self.visible and self.rect.collidepoint(pos)
        
    def hide(self):
        self.visible = False
        
    def show(self):
        self.visible = True

class TextButton:
    def __init__(self, text, position, font_size=40):
        self.font = get_chinese_font(font_size)
        self.text = text
        self.position = position
        self.visible = False
        self.text_surface = self.font.render(text, True, (255, 255, 255))
        self.rect = self.text_surface.get_rect(center=position)
        self.bg_rect = self.rect.inflate(20, 10)
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, (50, 50, 50), self.bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.bg_rect, 2)
            screen.blit(self.text_surface, self.rect)
            
    def is_clicked(self, pos):
        return self.visible and self.bg_rect.collidepoint(pos)
        
    def hide(self):
        self.visible = False
        
    def show(self):
        self.visible = True

class Game:
    def __init__(self):
        self.state = "INITIAL"
        self.current_video = None
        self.pick_button = Button("./assets/pick/pick_button.png", (300, 850))
        self.continue_button = TextButton("CONTINUE", (300, 850))
        self.back_button = TextButton("BACK", (300, 850))
        self.main_back_button = Button("./assets/back.png", (550, 30))
        self.current_doc_text = None
        self.popup_active = False
        self.background = None
        self.doc_scroll_offset = 0
        self.doc_line_height = 35
        
    def load_video(self, video_path, loop=False):
        if self.current_video:
            self.current_video.stop()
        self.current_video = VideoPlayer(video_path, loop)
        self.current_video.play()
        
    def load_document(self, doc_number):
        doc_path = f"./assets/pick/docs/{doc_number}.txt"
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                self.current_doc_text = f.read()
        except:
            self.current_doc_text = f"Document {doc_number} not found"
            
    def draw_document(self, screen):
        if not self.current_doc_text:
            return
            
        screen.fill((20, 20, 20))
        font = get_chinese_font(24)
        
        lines = self.current_doc_text.split('\n')
        y = 50 - self.doc_scroll_offset
        
        # Create a clipping rectangle to ensure text doesn't overlap with button
        clip_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT - 200)
        screen.set_clip(clip_rect)
        
        for line in lines:
            if y > -self.doc_line_height and y < WINDOW_HEIGHT - 200:  # Only draw visible lines
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (50, y))
            y += self.doc_line_height
            
        # Reset clipping
        screen.set_clip(None)
        
        # Calculate max scroll
        total_height = len(lines) * self.doc_line_height
        self.max_scroll = max(0, total_height - (WINDOW_HEIGHT - 250))
                
    def draw_popup(self, screen):
        popup_width = 400
        popup_height = 200
        popup_x = (WINDOW_WIDTH - popup_width) // 2
        popup_y = (WINDOW_HEIGHT - popup_height) // 2
        
        pygame.draw.rect(screen, (50, 50, 50), (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 3)
        
        font = get_chinese_font(40)
        text = font.render("Pick Again?", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, popup_y + 60))
        screen.blit(text, text_rect)
        
        return (popup_x + 100, popup_y + 130), (popup_x + 300, popup_y + 130)
        
    def reset_to_initial(self):
        self.state = "INITIAL"
        self.load_video("./assets/pick/sit.mp4", loop=True)
        self.pick_button.show()
        self.continue_button.hide()
        self.back_button.hide()
        self.current_doc_text = None
        self.popup_active = False
        self.background = None
        self.doc_scroll_offset = 0
        
    def run(self):
        running = True
        self.reset_to_initial()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    if self.state == "SHOW_DOCUMENT":
                        # Scroll up/down with mouse wheel
                        self.doc_scroll_offset -= event.y * 30
                        self.doc_scroll_offset = max(0, min(self.doc_scroll_offset, self.max_scroll))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.main_back_button.is_clicked(event.pos):
                        pygame.quit()
                        subprocess.Popen([sys.executable, "main_game.py"])
                        sys.exit()
                    elif self.popup_active:
                        yes_pos, no_pos = self.draw_popup(screen)
                        yes_rect = pygame.Rect(yes_pos[0] - 40, yes_pos[1] - 20, 80, 40)
                        no_rect = pygame.Rect(no_pos[0] - 40, no_pos[1] - 20, 80, 40)
                        
                        if yes_rect.collidepoint(event.pos):
                            self.reset_to_initial()
                        elif no_rect.collidepoint(event.pos):
                            pygame.quit()
                            subprocess.Popen([sys.executable, "main_game.py"])
                            sys.exit()
                    elif self.state == "INITIAL" and self.pick_button.is_clicked(event.pos):
                        self.pick_button.hide()
                        self.load_video("./assets/pick/pick.mp4")
                        self.state = "PICKING"
                    elif self.state == "SHOW_CONTINUE" and self.continue_button.is_clicked(event.pos):
                        doc_number = random.randint(1, 4)
                        self.load_document(doc_number)
                        self.state = "SHOW_DOCUMENT"
                        self.continue_button.hide()
                        self.back_button.show()
                        self.doc_scroll_offset = 0
                        self.max_scroll = 0
                    elif self.state == "SHOW_DOCUMENT" and self.back_button.is_clicked(event.pos):
                        self.reset_to_initial()
                        
            if self.current_video and self.current_video.is_playing():
                frame = self.current_video.get_frame()
                if frame:
                    screen.blit(frame, (0, 0))
                else:
                    if self.state == "PICKING":
                        choice = random.choice(["YES", "NO"])
                        if choice == "YES":
                            self.load_video("./assets/pick/monk_yes.MP4")
                            self.state = "SHOWING_MONK_YES"
                        else:
                            self.load_video("./assets/pick/monk_no.MP4")
                            self.state = "SHOWING_MONK_NO"
                    elif self.state == "SHOWING_MONK_YES":
                        self.state = "SHOW_CONTINUE"
                        self.continue_button.show()
                        self.current_video = None
                        self.background = pygame.image.load("./assets/pick/bg2.png")
                    elif self.state == "SHOWING_MONK_NO":
                        self.state = "SHOW_POPUP"
                        self.popup_active = True
                        self.current_video = None
                        self.background = pygame.image.load("./assets/pick/bg1.png")
            elif self.state == "SHOW_DOCUMENT":
                self.draw_document(screen)
            elif self.state == "SHOW_POPUP":
                if self.background:
                    screen.blit(self.background, (0, 0))
                else:
                    screen.fill((0, 0, 0))
                yes_pos, no_pos = self.draw_popup(screen)
                font = get_chinese_font(30)
                yes_text = font.render("Yes", True, (255, 255, 255))
                no_text = font.render("No", True, (255, 255, 255))
                pygame.draw.rect(screen, (100, 100, 100), (yes_pos[0] - 40, yes_pos[1] - 20, 80, 40))
                pygame.draw.rect(screen, (100, 100, 100), (no_pos[0] - 40, no_pos[1] - 20, 80, 40))
                screen.blit(yes_text, (yes_pos[0] - 15, yes_pos[1] - 10))
                screen.blit(no_text, (no_pos[0] - 15, no_pos[1] - 10))
            elif self.state == "SHOW_CONTINUE":
                if self.background:
                    screen.blit(self.background, (0, 0))
                else:
                    screen.fill((0, 0, 0))
            else:
                screen.fill((0, 0, 0))
                
            self.pick_button.draw(screen)
            self.continue_button.draw(screen)
            self.back_button.draw(screen)
            self.main_back_button.draw(screen)
            
            pygame.display.flip()
            clock.tick(30)
            
        if self.current_video:
            self.current_video.stop()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()