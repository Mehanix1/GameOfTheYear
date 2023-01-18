import os
import sys
import time as tm

import pygame
from pygame.locals import *  # это добавляет обработку клавиш
from datetime import *

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


def start_screen():
    global start_time
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

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


def final_screen():
    end_time = datetime.now()
    playing_time = end_time - start_time
    outro_text = ['ИГРА ОКОНЧЕНА', '',
                  f'Потрачено {playing_time.seconds} сек.']
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
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


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


class ExampleMap:
    def get_anti_floor(self):
        return self.anti_floor

    def get_map(self):
        return self.load_map

    def blink(self):
        transporant = pygame.Surface((screen.get_size()))

        for i in range(7):
            transporant.set_alpha(100)
            screen.blit(transporant, (0, 0))
            pygame.display.flip()
            pygame.time.wait(30)

    def update(self):
        pass

    def mtal(self, player: Player, load_map):  # Moving to another location / Переход на другую локацию
        if player.rect.bottom > load_map.get_size()[1]:  # переход вниз
            self.blink()
            player.rect.top = 0
            return "вниз"

        elif player.rect.top < 0:  # вверх
            self.blink()
            player.rect.bottom = load_map.get_size()[1]
            return "вверх"

        elif player.rect.left < 0:  # влево
            self.blink()
            player.rect.right = load_map.get_size()[0]
            return "влево"

        elif player.rect.right > load_map.get_size()[0]:  # вправо
            self.blink()
            player.rect.left = 0
            return "вправо"

        else:
            return False


class Map1(ExampleMap):
    def __init__(self):
        self.load_map = pygame.transform.scale(load_image("карта_дом.png"), (
            pygame.display.get_surface().get_size()))
        self.anti_floor = AntiFloor("пол_дом.png", self.load_map)

        firentlmt = load_image("огонь.png")  # Fire not to load many times Огонь чтобы не загружать много раз
        self.f1 = FireAnimation(firentlmt, 6, 1, self.load_map.get_size()[0] // 4.8, self.load_map.get_size()[1] // 1.6,
                                coefficient=2)
        self.f2 = FireAnimation(firentlmt, 6, 1, self.load_map.get_size()[0] // 1.5, self.load_map.get_size()[1] // 3.1,
                                coefficient=3.5)

        Fog(self.load_map)

        pygame.time.set_timer(pygame.USEREVENT + 1, 240)  # таймер для огня
        pygame.time.set_timer(pygame.USEREVENT + 2, 140)  # таймер для тумана

    def update(self):
        fire_group.draw(screen)
        fog_group.draw(screen)

    def player_check(self, player):
        global map
        kuda = self.mtal(player, self.load_map)  # <--- получает напрвление движения и двигает пользователя
        if kuda == "вниз":

            fog_group.empty()

            map = Map2()

            fire_group.empty()

            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.left = map.get_map().get_size()[0] // 2


class Map2(ExampleMap):
    def __init__(self):
        self.load_map = pygame.transform.scale(load_image("карта_2.png"), (
            pygame.display.get_surface().get_size()))
        self.anti_floor = AntiFloor("пол_карта_2.png", self.load_map)

        Fog(self.load_map)

    def update(self):
        fog_group.draw(screen)

    def player_check(self, player):
        global map

        kuda = self.mtal(player, self.load_map)
        if kuda == "вверх":  # карта 2 переход вверх на карту 1
            fog_group.empty()
            map = Map1()

            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.left = map.get_map().get_size()[0] // 2

        elif kuda == "вниз":  # карта 2 переход вниз на карту 3

            fog_group.empty()

            map = Map3()


        elif kuda == "влево":  # карта 2 переход влево на карту 4

            fog_group.empty()

            map = Map4()
            player.rect.right = map.get_map().get_size()[0]

            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.top = map.get_map().get_size()[1] // 4

        elif kuda == "вправо":  # карта 2 переход влево на карту 4

            fog_group.empty()

            map = Map6()

            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.top = map.get_map().get_size()[1] // 4


class Map3(ExampleMap):
    def __init__(self):
        self.load_map = pygame.transform.scale(load_image("карта_3.png"), (
            pygame.display.get_surface().get_size()))
        self.anti_floor = AntiFloor("пол_карта_3.png", self.load_map)

        Fog(self.load_map)

    def update(self):
        fog_group.draw(screen)

    def player_check(self, player):
        global map
        kuda = self.mtal(player, self.load_map)

        if kuda == "вверх":
            fog_group.empty()

            map = Map2()

            fire_group.empty()
            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.left = map.get_map().get_size()[0] // 2


class Map4(ExampleMap):
    def __init__(self):
        self.load_map = pygame.transform.scale(load_image("карта_4.png"), (
            pygame.display.get_surface().get_size()))
        self.anti_floor = AntiFloor("пол_карта_4.png", self.load_map)

        Fog(self.load_map)

    def update(self):
        fog_group.draw(screen)

    def player_check(self, player):
        global map
        kuda = self.mtal(player, self.load_map)

        if kuda == "вправо":
            fog_group.empty()

            map = Map2()

            fire_group.empty()

            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.top = map.get_map().get_size()[1] // 3


class Map6(ExampleMap):
    def __init__(self):
        self.load_map = pygame.transform.scale(load_image("карта_6.png"), (
            pygame.display.get_surface().get_size()))
        self.anti_floor = AntiFloor("пол_карта_6.png", self.load_map)

        Fog(self.load_map)

    def update(self):
        fog_group.draw(screen)

    def player_check(self, player):
        global map
        kuda = self.mtal(player, self.load_map)

        if kuda == "влево":
            fog_group.empty()

            map = Map2()

            fire_group.empty()

        try:
            if kuda == "вправо":
                fog_group.empty()

                map = Map7()

                fire_group.empty()

                player.rect.left = 0
                if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                    player.rect.top = map.get_map().get_size()[1] // 3
        except:
            print("УРОВЕНЬ НЕ ДОСТРОЕН")


# УРОВЕНЬ ГДЕ КАРТА ДОЛЖНА СЛЕДОВАТЬ ЗА ПЕРСОНАЖЕМ


# -----------------------------------------------------------------------------------------------------------

map = None


def start():
    start_screen()

    pygame.mixer.music.load("data/music.mp3")
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)

    global map
    map = Map1()

    running = True

    size = pygame.display.get_surface().get_size()
    player = Player(size[0] // 2, size[1] // 2)

    velocity = 901
    frame_delay = 0

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]:
                running = False
            elif event.type == pygame.USEREVENT + 1:
                fire_group.update()
            elif event.type == pygame.USEREVENT + 2:

                fog_group.update()

        # ------------------------------------------------------------------------------------------------
        distance = int(velocity * frame_delay)
        if pygame.key.get_pressed()[K_RIGHT] or pygame.key.get_pressed()[K_d]:

            player.rect.left += distance
            if pygame.sprite.collide_mask(player, map.get_anti_floor()):  # Если после того как
                # персонаж прошёл, он соприкасается со стеной
                player.rect.left -= distance  # то его отбросит назад

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_LEFT] or pygame.key.get_pressed()[K_a]:
            player.rect.left -= distance
            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.left += distance

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_UP] or pygame.key.get_pressed()[K_w]:
            player.rect.top -= distance

            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.top += distance

        # ------------------------------------------------------------------------------------------------

        if pygame.key.get_pressed()[K_DOWN] or pygame.key.get_pressed()[K_s]:
            player.rect.top += distance
            if pygame.sprite.collide_mask(player, map.get_anti_floor()):
                player.rect.top -= distance

        # ============================================================================================

        if pygame.key.get_pressed()[K_f]:
            final_screen()

        # ============================================================================================

        screen.blit(map.get_map(), (0, 0))
        player_group.draw(screen)
        map.update()

        pygame.display.flip()

        map.player_check(player)

        clock.tick(FPS)
        frame_delay = clock.tick(FPS) / 1000


# -------------------------------------------------------------------------------------------------------------------


start()

pygame.quit()
sys.exit()
