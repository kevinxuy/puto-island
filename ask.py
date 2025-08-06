#!/usr/bin/env python3
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((600, 800))
pygame.display.set_caption("Ask")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((180, 180, 100))
    font = pygame.font.Font(None, 36)
    text = font.render("Ask - Under Construction", True, (255, 255, 255))
    text_rect = text.get_rect(center=(300, 400))
    screen.blit(text, text_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()