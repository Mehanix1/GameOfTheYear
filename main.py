from __future__ import annotations
import os
import sys
import time as tm

import pygame
from pygame.locals import *  # это добавляет обработку клавиш
from datetime import *

pygame.init()

all_sprites = pygame.sprite.Group()
map_group = pygame.sprite.Group()
object_group = pygame.sprite.Group()
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
        super().__init__(player_group, object_group, all_sprites)
        self.image = load_image("idle.png")
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class AntiFloor(pygame.sprite.Sprite):
    def __init__(self, name_of_map, map):
        super().__init__(anti_floor_group, all_sprites)
        self.image = pygame.Surface((0, 0))
        anti_floor_image = load_image(name_of_map)

        anti_floor_image = pygame.transform.scale(anti_floor_image, (
            map.get_size()))

        self.mask = pygame.mask.from_surface(anti_floor_image)  # Берётся маска пола
        self.mask.invert()  # маска пола превращается в маску НЕ ПОЛА, т.е. в маску стен

        self.rect = anti_floor_image.get_rect().move(0, 0)


class FireAnimation(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, coefficient):
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
    def __init__(self, map):
        super().__init__(fog_group, object_group, all_sprites)

        self.image = load_image("туман_дом.png")
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_width(), map.get_size())[1])

        self.rect = self.image.get_rect()

    def update(self, tick_animation=False):
        if not tick_animation:
            return
        self.rect.left -= 1  # движение тумана
        if self.rect.right < 0:  # телепортация
            self.rect = self.rect.move((pygame.display.get_surface().get_size()[0] * 2.5, 0))


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


class MapBase(pygame.sprite.Sprite):
    def __init__(self, map_image: pygame.Surface, map_name=None) -> None:
        super().__init__(map_group, all_sprites)
        self.image = pygame.transform.scale(map_image, pygame.display.get_surface().get_size())
        self.rect = self.image.get_rect()
        self.map_name = map_name

    def get_map_name(self):
        return self.map_name

    def get_anti_floor(self):
        return self.anti_floor

    def get_if_map_is_big(self):
        return self.is_map_is_big

    def blink(self):
        transporant = pygame.Surface((screen.get_size()))

        for i in range(7):
            transporant.set_alpha(100)
            screen.blit(transporant, (0, 0))
            pygame.display.flip()
            pygame.time.wait(30)

    def collide_map_border(self, player: Player):  # Moving to another location / Переход на другую локацию
        if player.rect.bottom > self.rect.bottom:  # переход вниз
            return "вниз"
        if player.rect.top < self.rect.y:  # вверх
            return "вверх"
        if player.rect.left < self.rect.x:  # влево
            return "влево"
        if player.rect.right > self.rect.right:  # вправо
            return "вправо"
        return None

    def change_location(self, where: str | None, new_map: MapBase, player: Player):
        global map
        if not where:
            return

        self.blink()
        self.move_player_to_another_map(player, where)
        self.logging(new_map)

    def move_player_to_another_map(self, player: Player, where: str) -> None:

        if where == "вниз":
            player.rect.top = map.rect.top
        elif where == "вверх":
            player.rect.bottom = map.rect.bottom
        elif where == "влево":
            player.rect.right = map.rect.right
        elif where == "вправо":
            player.rect.left = map.rect.left

    def logging(self, new_map):
        with open('logs.txt', 'a', encoding='utf-8') as file:
            file.write(f'{datetime.now()} перешёл на "{new_map.get_map_name()}" \n')


class Map1(MapBase):
    def __init__(self):

        map_image = load_image("карта_дом.png")
        super().__init__(map_image,"карта 1")
        self.is_map_is_big = False
        self.anti_floor = AntiFloor("пол_дом.png", self.image)

        firentlmt = load_image("огонь.png")  # Fire not to load many times Огонь чтобы не загружать много раз
        self.f1 = FireAnimation(firentlmt, 6, 1, self.image.get_size()[0] // 4.8, self.image.get_size()[1] // 1.6,
                                coefficient=2)
        self.f2 = FireAnimation(firentlmt, 6, 1, self.image.get_size()[0] // 1.5, self.image.get_size()[1] // 3.1,
                                coefficient=3.5)

        Fog(self.image)

        pygame.time.set_timer(FIRE_ANIMATE_EVENT, 240)  # таймер для огня
        pygame.time.set_timer(FOG_ANIMATE_EVENT, 140)  # таймер для тумана

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя
        if where == "вниз":
            object_group.remove(*fog_group)
            fog_group.empty()

            object_group.remove(*fire_group)
            fire_group.empty()

            map_group.remove(map)

            map = Map2()
        else:
            return
        self.change_location(where, map, player)


class Map2(MapBase):
    def __init__(self):
        map_image = load_image("карта_2.png")
        super().__init__(map_image,"карта2")
        self.anti_floor = AntiFloor("пол_карта_2.png", self.image)
        self.is_map_is_big = False

        Fog(self.image)

    def player_check(self, player):
        global map

        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя
        if where == "вниз":
            object_group.remove(*fog_group)
            fog_group.empty()

            object_group.remove(*fire_group)

            map_group.remove(map)

            map = Map3()

        elif where == "вверх":
            object_group.remove(*fog_group)
            fog_group.empty()

            map_group.remove(map)

            map = Map1()
        elif where == "влево":
            object_group.remove(*fog_group)
            fog_group.empty()

            map_group.remove(map)

            map = Map4()


        elif where == "вправо":

            object_group.remove(*fog_group)
            fog_group.empty()
            map_group.remove(map)

            map = Map6()
        else:
            return
        self.change_location(where, map, player)


class Map3(MapBase):
    def __init__(self):
        map_image = load_image("карта_3.png")
        super().__init__(map_image)
        self.anti_floor = AntiFloor("пол_карта_3.png", self.image)
        self.is_map_is_big = False

        Fog(self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "вверх":
            object_group.remove(*fog_group)

            map_group.remove(map)

            map = Map2()
        else:
            return
        self.change_location(where, map, player)


class Map4(MapBase):
    def __init__(self):
        map_image = load_image("карта_4.png")
        super().__init__(map_image)
        self.anti_floor = AntiFloor("пол_карта_4.png", self.image)
        self.is_map_is_big = False

        Fog(self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "вправо":
            object_group.remove(*fog_group)
            fog_group.empty()

            map_group.remove(map)

            map = Map2()
        else:
            return
        self.change_location(where, map, player)


class Map6(MapBase):
    def __init__(self):
        map_image = load_image("карта_6.png")
        super().__init__(map_image)
        self.anti_floor = AntiFloor("пол_карта_6.png", self.image)
        self.is_map_is_big = False

        Fog(self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "влево":
            object_group.remove(*fog_group)
            fog_group.empty()

            map_group.remove(map)
            map = Map2()
        elif where == "вправо":
            object_group.remove(*fog_group)
            fog_group.empty()

            map_group.remove(map)
            map = Map7()
        else:
            return
        self.change_location(where, map, player)


class Map7(MapBase):
    def __init__(self):
        map_image = load_image("карта_7.png")
        super().__init__(map_image)
        self.image = map_image
        self.rect = self.image.get_rect()

        self.anti_floor = AntiFloor("пол_карта_7.png", self.image)
        self.is_map_is_big = True

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "влево":
            object_group.remove(*fog_group)
            fog_group.empty()

            map_group.remove(map)
            map = Map6()

        elif where == "вправо":
            object_group.remove(*fog_group)
            fog_group.empty()
            map_group.remove(map)
            map = Map8()
        else:
            return
        self.change_location(where, map, player)


class Map8(MapBase):
    def __init__(self):
        map_image = load_image("карта_8.png")
        self.is_map_is_big = True
        super().__init__(map_image)
        self.image = map_image
        self.rect = self.image.get_rect()

        self.anti_floor = AntiFloor("пол_карта_8.png", self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "влево":
            object_group.remove(*fog_group)
            fog_group.empty()
            map_group.remove(map)

            map = Map7()
        else:
            return
        self.change_location(where, map, player)


# -----------------------------------------------------------------------------------------------------------
with open('logs.txt', 'a', encoding='utf-8') as file:
    file.write(f'\nначата новая игра\n')
map = None

FIRE_ANIMATE_EVENT = pygame.USEREVENT + 1
FOG_ANIMATE_EVENT = pygame.USEREVENT + 2


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

    camera = Camera()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]:
                running = False
            elif event.type == FIRE_ANIMATE_EVENT:
                fire_group.update(tick_animation=True)
            elif event.type == FOG_ANIMATE_EVENT:
                fog_group.update(tick_animation=True)

        # ------------------------------------------------------------------------------------------------
        distance = int(velocity * frame_delay)
        if pygame.key.get_pressed()[K_RIGHT] or pygame.key.get_pressed()[K_d]:
            player.image = load_image("r_walk.png")
            player.rect.left += distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())
            if are_colliding_anti_floor:  # Если после того как
                # персонаж прошёл, он соприкасается со стеной
                player.rect.left -= distance  # то его отбросит назад

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_LEFT] or pygame.key.get_pressed()[K_a]:
            player.image = load_image("l_walk.png")
            player.rect.left -= distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())
            if are_colliding_anti_floor:
                player.rect.left += distance

        # ------------------------------------------------------------------------------------------------
        if pygame.key.get_pressed()[K_UP] or pygame.key.get_pressed()[K_w]:
            player.image = load_image('u_walk.png')
            player.rect.top -= distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())
            if are_colliding_anti_floor:
                player.rect.top += distance

        # ------------------------------------------------------------------------------------------------

        if pygame.key.get_pressed()[K_DOWN] or pygame.key.get_pressed()[K_s]:
            player.image = load_image('d_walk.png')
            player.rect.top += distance
            are_colliding_anti_floor = pygame.sprite.collide_mask(player, map.get_anti_floor())
            if are_colliding_anti_floor:
                player.rect.top -= distance

        # ============================================================================================

        if pygame.key.get_pressed()[K_f]:
            final_screen()

        # ============================================================================================

        all_sprites.update()

        map.player_check(player)

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


start()

pygame.quit()
sys.exit()