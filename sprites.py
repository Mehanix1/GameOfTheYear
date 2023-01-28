from __future__ import annotations
import pygame

from load_image import load_image


class AntiFloor(pygame.sprite.Sprite):
    def __init__(self, anti_floor_group, all_sprites, name_of_map, map):
        super().__init__(anti_floor_group, all_sprites)
        self.image = pygame.Surface((0, 0))
        anti_floor_image = load_image(name_of_map)

        anti_floor_image = pygame.transform.scale(anti_floor_image, (
            map.get_size()))

        self.mask = pygame.mask.from_surface(anti_floor_image)  # Берётся маска пола
        self.mask.invert()  # маска пола превращается в маску НЕ ПОЛА, т.е. в маску стен

        self.rect = anti_floor_image.get_rect().move(0, 0)


class FireAnimation(pygame.sprite.Sprite):
    def __init__(self, fire_group, object_group, all_sprites, sheet, columns, rows, x, y, coefficient):
        super().__init__(fire_group, object_group, all_sprites)
        self.frames = []
        sheet = pygame.transform.scale(sheet,
                                       (int(sheet.get_width() // coefficient), int(sheet.get_height() // coefficient)))
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, tick_animation=False):
        if not tick_animation:
            return
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Fog(pygame.sprite.Sprite):
    def __init__(self, fog_group, object_group, all_sprites, map):
        super().__init__(fog_group, object_group, all_sprites)

        self.image = load_image("туман_дом.png")
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_width(), map.get_size()[1]))

        self.rect = self.image.get_rect()

    def update(self, tick_animation=False):
        if not tick_animation:
            return
        self.rect.left -= 1  # движение тумана
        if self.rect.right < 0:  # телепортация
            self.rect = self.rect.move((pygame.display.get_surface().get_size()[0] * 2.5, 0))
