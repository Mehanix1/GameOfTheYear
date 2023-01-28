from __future__ import annotations
import pygame
from datetime import *

from config import FIRE_ANIMATE_EVENT, FOG_ANIMATE_EVENT
from load_image import load_image
from start_screen import final_screen
from sprites import AntiFloor, FireAnimation, Fog
from player_and_camera import Player

map = None


def get_map():
    return map


def set_map(new_map) -> None:
    global map
    map = new_map
    return map


class MapBase(pygame.sprite.Sprite):
    def __init__(self, all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group,
                 player_group, map_image: pygame.Surface, map_name=None) -> None:
        super().__init__(map_group, all_sprites)
        self._all_sprites = all_sprites
        self._map_group = map_group
        self._object_group = object_group
        self._anti_floor_group = anti_floor_group
        self._fire_group = fire_group
        self._fog_group = fog_group
        self._player_group = player_group
        self.image = pygame.transform.scale(map_image, pygame.display.get_surface().get_size())
        self.rect = self.image.get_rect()
        self.map_name = map_name

        self.width = self.rect.width
        self.height = self.rect.height

    def get_map_name(self):
        return self.map_name

    def get_anti_floor(self):
        return self.anti_floor

    def get_if_map_is_big(self):
        return self.is_map_is_big

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

    def change_location(self, where: str | None, new_map: MapBase, player: Player, screen):
        global map
        if not where:
            return

        blink(screen)
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
    def __init__(self, all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group,
                 player_group):
        map_image = load_image("карта_дом.png")
        super().__init__(all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group,
                         player_group, map_image, "карта №1")
        self.is_map_is_big = False
        self.anti_floor = AntiFloor(self._anti_floor_group, self._all_sprites, "пол_дом.png", self.image)

        firentlmt = load_image("огонь.png")  # Fire not to load many times Огонь чтобы не загружать много раз
        self.f1 = FireAnimation(self._fire_group, self._object_group, self._all_sprites, firentlmt, 6, 1,
                                self.image.get_size()[0] // 4.8, self.image.get_size()[1] // 1.6,
                                coefficient=2)
        self.f2 = FireAnimation(self._fire_group, self._object_group, self._all_sprites, firentlmt, 6, 1,
                                self.image.get_size()[0] // 1.5, self.image.get_size()[1] // 3.1,
                                coefficient=3.5)

        Fog(self._fog_group, self._object_group, self._all_sprites, self.image)

        pygame.time.set_timer(FIRE_ANIMATE_EVENT, 240)  # таймер для огня
        pygame.time.set_timer(FOG_ANIMATE_EVENT, 140)  # таймер для тумана

    def player_check(self, player, screen):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя
        if where == "вниз":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()
            self._object_group.remove(*self._fire_group)
            self._fire_group.empty()

            self._map_group.remove(map)

            map = set_map(Map2(self._all_sprites, self._map_group, self._object_group, self._anti_floor_group, self._fire_group, self._fog_group, self._player_group))


        else:
            return

        self.change_location(where, map, player, screen)
        if pygame.sprite.collide_mask(player, map.get_anti_floor()):
            if where == 'вниз':
                player.rect.x = map.rect.width / 2


class Map2(MapBase):
    def __init__(self, all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group, player_group, ):
        map_image = load_image("карта_2.png")
        super().__init__(all_sprites, map_group, object_group, anti_floor_group, fire_group, fog_group,
                         player_group, map_image, "карта №2")
        self.anti_floor = AntiFloor(anti_floor_group, all_sprites, "пол_карта_2.png", self.image)
        self.is_map_is_big = False

        Fog(fog_group, object_group, all_sprites, self.image)

    def player_check(self, player):
        global map

        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя
        if where == "вниз":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()

            self._object_group.remove(*self._fire_group)

            self._map_group.remove(map)

            map = Map3()

        elif where == "вверх":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()

            self._map_group.remove(map)

            map = Map1()

        elif where == "влево":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()

            self._map_group.remove(map)

            map = Map4()


        elif where == "вправо":

            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()
            self._map_group.remove(map)

            map = Map6()
        else:
            return
        self.change_location(where, map, player)

        if pygame.sprite.collide_mask(player, map.get_anti_floor()):
            if where == 'вниз':
                player.rect.x = map.width / 2
            elif where == 'вверх':
                player.rect.x = map.width / 2
            elif where == 'влево':
                player.rect.y = map.height / 4
            elif where == 'вправо':
                player.rect.y = map.height / 4


class Map3(MapBase):
    def __init__(self):
        map_image = load_image("карта_3.png")
        super().__init__(map_image, "карта №3")
        self.anti_floor = AntiFloor("пол_карта_3.png", self.image)
        self.is_map_is_big = False

        Fog(self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "вверх":
            self._object_group.remove(*self._fog_group)

            self._map_group.remove(map)

            map = Map2()
        else:
            return
        self.change_location(where, map, player)

        if pygame.sprite.collide_mask(player, map.get_anti_floor()):

            if where == 'вверх':
                player.rect.x = map.width / 2


class Map4(MapBase):
    def __init__(self):
        map_image = load_image("карта_4.png")
        super().__init__(map_image, "карта №4")
        self.anti_floor = AntiFloor("пол_карта_4.png", self.image)
        self.is_map_is_big = False

        Fog(self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "вправо":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()

            self._map_group.remove(map)

            map = Map2()
        else:
            return
        self.change_location(where, map, player)
        if pygame.sprite.collide_mask(player, map.get_anti_floor()):
            if where == 'вправо':
                player.rect.y = map.height / 4


class Map6(MapBase):
    def __init__(self):
        map_image = load_image("карта_6.png")
        super().__init__(map_image, "карта №6")
        self.anti_floor = AntiFloor("пол_карта_6.png", self.image)
        self.is_map_is_big = False

        Fog(self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "влево":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()

            self._map_group.remove(map)
            map = Map2()
        elif where == "вправо":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()

            self._map_group.remove(map)
            map = Map7()
        else:
            return
        self.change_location(where, map, player)
        if pygame.sprite.collide_mask(player, map.get_anti_floor()):

            if where == 'влево':
                player.rect.y = map.height / 4
            elif where == 'вправо':
                player.rect.y = map.rect.height / 2.3


class Map7(MapBase):
    def __init__(self):
        map_image = load_image("карта_7.png")
        super().__init__(map_image, "карта №7")
        self.image = map_image
        self.rect = self.image.get_rect()

        self.anti_floor = AntiFloor("пол_карта_7.png", self.image)
        self.is_map_is_big = True

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "влево":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()

            self._map_group.remove(map)
            map = Map6()

        elif where == "вправо":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()
            self._map_group.remove(map)
            map = Map8()
        else:
            return
        self.change_location(where, map, player)
        if pygame.sprite.collide_mask(player, map.get_anti_floor()):
            if where == 'влево':
                player.rect.y = map.height / 4


class Map8(MapBase):
    def __init__(self):
        map_image = load_image("карта_8.png")
        self.is_map_is_big = True
        super().__init__(map_image, "карта №8")
        self.image = map_image
        self.rect = self.image.get_rect()

        self.anti_floor = AntiFloor("пол_карта_8.png", self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя

        if where == "влево":
            self._map_group.remove(map)

            map = Map7()
        elif where == "вверх":
            self._map_group.remove(map)
            map = Map9()
        else:
            return
        self.change_location(where, map, player)


class Map9(MapBase):
    def __init__(self):
        map_image = load_image("карта_9.png")
        self.is_map_is_big = True
        super().__init__(map_image, "карта №9")
        self.image = map_image
        self.rect = self.image.get_rect()

        self.anti_floor = AntiFloor("пол_карта_9.png", self.image)

    def player_check(self, player):
        global map
        where = self.collide_map_border(player)  # <--- получает напрвление движения и двигает пользователя
        if map.rect.top > - 324:
            pygame.time.wait(2000)
            final_screen(screen)

        if where == "вниз":
            self._object_group.remove(*self._fog_group)
            self._fog_group.empty()
            self._map_group.remove(map)

            map = Map8()

        else:
            return
        self.change_location(where, map, player)

        if pygame.sprite.collide_mask(player, map.get_anti_floor()) or not pygame.sprite.collide_mask(player, map):

            if where == 'вниз':
                player.rect.x = map.rect.width / 2

def blink(screen):
    transparent = pygame.Surface((screen.get_size()))

    for i in range(7):
        transparent.set_alpha(100)
        screen.blit(transparent, (0, 0))
        pygame.display.flip()
        pygame.time.wait(30)

