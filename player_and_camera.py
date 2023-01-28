from __future__ import annotations
import pygame
from load_image import load_image


class Player(pygame.sprite.Sprite):
    def __init__(self, player_group, object_group, all_sprites, pos_x, pos_y):
        from maps import get_map

        super().__init__(player_group, object_group, all_sprites)

        map = get_map()
        self.kx, self.ky = int(map.width / 17), int(map.height / 15)

        self.i_walk = self.size_change(load_image("idle.png"))
        self.r_walk = self.size_change(load_image("r_walk.png"))

        self.l_walk = self.size_change(load_image("l_walk.png"))

        self.d_walk = self.size_change(load_image("d_walk.png"))
        self.u_walk = self.size_change(load_image("u_walk.png"))
        self.image = self.i_walk

        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def size_change(self, i):
        i = pygame.transform.scale(i, (self.kx, self.ky))
        return i

    def right(self):
        self.image = self.r_walk

    def left(self):
        self.image = self.l_walk

    def down(self):
        self.image = self.d_walk

    def up(self):
        self.image = self.u_walk

    def i_stop(self):
        self.image = self.i_walk


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = round(screen.get_size()[0] / 2 - target.rect.x - target.rect.w / 2)
        self.dy = round(screen.get_size()[1] / 2 - target.rect.y - target.rect.h / 2)
