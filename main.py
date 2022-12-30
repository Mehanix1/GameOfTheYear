import os
import sys
import pygame
from pygame.locals import *  # это добавляет обработку клавиш

pygame.init()

all_sprites = pygame.sprite.Group()
anti_floor_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()

FPS = 50

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


class Anti_Floor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(anti_floor_group, all_sprites)
        self.image = load_image("пол_дом.png")

        self.mask = pygame.mask.from_surface(self.image)  # Берётся маска пола
        self.mask.invert()  # маска пола превращается в маску НЕ ПОЛА, т.е. в маску стен

        self.rect = self.image.get_rect().move(0, 0)


def start():
    anti_floor = Anti_Floor()

    map_house = pygame.transform.scale(load_image('карта_дом.png'), (
        pygame.display.get_surface().get_size()))  # Загрузать и изменить карту под размер окна

    screen.blit(map_house, (0, 0))

    running = True
    player = Player(500, 500)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]:
                running = False

        if (pygame.key.get_pressed()[K_RIGHT] or pygame.key.get_pressed()[K_d]):

            player.rect.left += 10
            if pygame.sprite.collide_mask(player,
                                          anti_floor):  # Если после того как персонаж прошёл, он соприкасается со стеной
                player.rect.left -= 10 # то его отбросит назад

        if pygame.key.get_pressed()[K_UP] or pygame.key.get_pressed()[K_w]:
            player.rect.top -= 10

            if pygame.sprite.collide_mask(player, anti_floor):
                player.rect.top += 10
        if pygame.key.get_pressed()[K_DOWN] or pygame.key.get_pressed()[K_s]:
            player.rect.top += 10
            if pygame.sprite.collide_mask(player, anti_floor):
                player.rect.top -= 10

        if pygame.key.get_pressed()[K_LEFT] or pygame.key.get_pressed()[K_a]:
            player.rect.left -= 10
            if pygame.sprite.collide_mask(player, anti_floor):
                player.rect.left += 10

        screen.blit(map_house, (0, 0))
        player_group.draw(screen)

        pygame.display.flip()

        clock.tick(FPS)


# -------------------------------------------------------------------------------------------------------------------


start()

pygame.quit()
sys.exit()
