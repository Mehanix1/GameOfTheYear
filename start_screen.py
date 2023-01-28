from __future__ import annotations
import sys
import pygame
from datetime import *
from pygame import K_ESCAPE

from load_image import load_image
from config import (
    FPS,
)


def start_screen(screen, clock):
    global start_time
    intro_text = ["Добро пожаловать", "",
                  "Для выхода нажмите Esc",
                  "...",
                  "тут надо чё-нить написать",
                  "Типо самая крутая игра. бла-бла-бла, ну вы поняли",
                  ]

    fon = pygame.transform.scale(load_image('fon.jpg'), (1920, 1080))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start_time = datetime.now()
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def final_screen(screen, clock):
    end_time = datetime.now()
    playing_time = end_time - start_time
    outro_text = ['ИГРА ОКОНЧЕНА',
                  f'Проведено с пользой {playing_time.seconds} сек.', 'Для выхода нажмите Esc', ]
    fon = pygame.transform.scale(load_image('fon.jpg'), (1920, 1080))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in outro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]:
                pygame.quit()
                sys.exit()
