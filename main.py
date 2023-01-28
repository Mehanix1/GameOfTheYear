from __future__ import annotations
import sys
import pygame
from pygame.locals import *  # это добавляет обработку клавиш

from maps import (
    set_map,
    Map1,
    Map2,
    Map3,
    Map4,
    Map6,
    Map7,
    Map8,
    Map9,
)
from start_screen import start_screen, final_screen

from player_and_camera import Player, Camera
from config import FPS, FIRE_ANIMATE_EVENT, FOG_ANIMATE_EVENT
from maps import get_map


def main():
    pygame.init()

    all_sprites = pygame.sprite.Group()
    map_group = pygame.sprite.Group()
    object_group = pygame.sprite.Group()
    anti_floor_group = pygame.sprite.Group()
    fire_group = pygame.sprite.Group()
    fog_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    start_screen(screen, clock)
    with open('logs.txt', 'a', encoding='utf-8') as file:
        file.write(f'\nначата новая игра\n')
    start_game(screen, clock, all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group,
               player_group)


# -----------------------------------------------------------------------------------------------------------


def start_game(screen, clock, all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group,
               player_group):
    pygame.mixer.music.load("data/music.mp3")
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)

    map = set_map(Map1(all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group, player_group))

    running = True

    size = pygame.display.get_surface().get_size()
    player = Player(player_group, object_group, all_sprites, size[0] // 2, size[1] // 2 - 100)

    velocity = 901
    frame_delay = 0

    camera = Camera()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]:
                running = False
            elif event.type == FIRE_ANIMATE_EVENT:
                fire_group.update(tick_animation=True)
            elif event.type == FOG_ANIMATE_EVENT:
                fog_group.update(tick_animation=True)
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_d, pygame.K_a,
                                 pygame.K_w, pygame.K_s]:
                    player.i_stop()

        # ------------------------------------------------------------------------------------------------
        distance = int(velocity * frame_delay)
        if pygame.key.get_pressed()[K_RIGHT] or pygame.key.get_pressed()[K_d]:
            player.right()
            player.rect.left += distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())

            if are_colliding_anti_floor:  # Если после того как
                # персонаж прошёл, он соприкасается со стеной
                player.rect.left -= distance  # то его отбросит назад

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_LEFT] or pygame.key.get_pressed()[K_a]:
            player.left()
            player.rect.left -= distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())
            if are_colliding_anti_floor:
                player.rect.left += distance

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_UP] or pygame.key.get_pressed()[K_w]:
            player.up()
            player.rect.top -= distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())
            if are_colliding_anti_floor:
                player.rect.top += distance

        # ------------------------------------------------------------------------------------------------

        if pygame.key.get_pressed()[K_DOWN] or pygame.key.get_pressed()[K_s]:
            player.down()
            player.rect.top += distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())
            if are_colliding_anti_floor:
                player.rect.top -= distance

        # ============================================================================================

        all_sprites.update()
        map.player_check(player, screen)

        if map.get_if_map_is_big():
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)

        screen.fill('black')
        map_group.draw(screen)
        object_group.draw(screen)

        pygame.display.flip()

        clock.tick(FPS)
        frame_delay = clock.tick(FPS) / 1000


# -------------------------------------------------------------------------------------------------------------------


main()

pygame.quit()
sys.exit()
