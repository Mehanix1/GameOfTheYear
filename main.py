import os
import sys
import pygame
from pygame.locals import *  # это добавляет обработку клавиш

pygame.init()

all_sprites = pygame.sprite.Group()
anti_floor_group = pygame.sprite.Group()
fire_group = pygame.sprite.Group()
fog_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()


FPS = 60

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = load_image("player.png")
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class AntiFloor(pygame.sprite.Sprite):
    def __init__(self, name_of_map, map):
        super().__init__(anti_floor_group, all_sprites)
        self.image = load_image(name_of_map)

        self.image = pygame.transform.scale(self.image, (
            map.get_size()))

        self.mask = pygame.mask.from_surface(self.image)  # Берётся маска пола
        self.mask.invert()  # маска пола превращается в маску НЕ ПОЛА, т.е. в маску стен

        self.rect = self.image.get_rect().move(0, 0)


class FireAnimation(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, coefficient):
        super().__init__(fire_group, all_sprites)
        self.frames = []
        sheet = pygame.transform.scale(sheet, (sheet.get_width() // coefficient, sheet.get_height() // coefficient))
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

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Fog(pygame.sprite.Sprite):
    def __init__(self, map):
        super().__init__(fog_group, all_sprites)

        self.image = load_image("туман_дом.png")
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_width(), map.get_size())[1])

        self.rect = self.image.get_rect()

    def update(self):
        self.rect.left -= 1  # движение тумана
        if self.rect.right < 0:  # телепортация
            self.rect = self.rect.move((pygame.display.get_surface().get_size()[0] * 2.5, 0))


def maps_loader(name_of_map):
    map = pygame.transform.scale(load_image(name_of_map), (
        pygame.display.get_surface().get_size()))  # Загрузать и изменить карту под размер окна

    if name_of_map == "карта_дом.png":
        pygame.time.set_timer(pygame.USEREVENT + 1, 240)  # таймер для огня
        pygame.time.set_timer(pygame.USEREVENT + 2, 140)  # таймер для тумана

        anti_floor = AntiFloor("пол_дом.png", map)

        firentlmt = load_image("огонь.png")  # Fire not to load many times Огонь чтобы не загружать много раз
        FireAnimation(firentlmt, 6, 1, map.get_size()[0] // 4.8, map.get_size()[1] // 1.6, coefficient=2)
        FireAnimation(firentlmt, 6, 1, map.get_size()[0] // 1.5, map.get_size()[1] // 3.1, coefficient=3.5)

        Fog(map)

        return map, anti_floor
    return map


# -----------------------------------------------------------------------------------------------------------


def start():
    map, anti_floor = maps_loader('карта_дом.png')

    screen.blit(map, (0, 0))

    running = True
    player = Player(500, 500)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]:
                running = False
            elif event.type == pygame.USEREVENT + 1:
                fire_group.update()
            elif event.type == pygame.USEREVENT + 2:

                fog_group.update()

        # ------------------------------------------------------------------------------------------------
        if (pygame.key.get_pressed()[K_RIGHT] or pygame.key.get_pressed()[K_d]):

            player.rect.left += 10
            if pygame.sprite.collide_mask(player, anti_floor):  # Если после того как
                # персонаж прошёл, он соприкасается со стеной
                player.rect.left -= 10  # то его отбросит назад

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_LEFT] or pygame.key.get_pressed()[K_a]:
            player.rect.left -= 10
            if pygame.sprite.collide_mask(player, anti_floor):
                player.rect.left += 10

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_UP] or pygame.key.get_pressed()[K_w]:
            player.rect.top -= 10

            if pygame.sprite.collide_mask(player, anti_floor):
                player.rect.top += 10

        # ------------------------------------------------------------------------------------------------

        if pygame.key.get_pressed()[K_DOWN] or pygame.key.get_pressed()[K_s]:
            player.rect.top += 10
            if pygame.sprite.collide_mask(player, anti_floor):
                player.rect.top -= 10

        screen.blit(map, (0, 0))
        player_group.draw(screen)
        fire_group.draw(screen)
        fog_group.draw(screen)

        pygame.display.flip()

        clock.tick(FPS)


# -------------------------------------------------------------------------------------------------------------------


start()

pygame.quit()
sys.exit()
