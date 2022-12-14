import pygame
import random
from pygame import draw

# to compile a new version for use without python (although compilation does require python) use these commands:
# cd <project path>
# auto-py-to-exe

# this should bring up a ui for compiling to exe
# cd <project path> isn't needed or valid if you are already in the project's path or using the console in pycharm
# compiling a new version does obviously require python, if you don't have python use the existing main.exe


pygame.init()
sc = pygame.display.set_mode((1080, 720))
c = pygame.time.Clock()
dt = 1
keys = None


def approach(x, y, a):
    if x < y:
        return min(x + a, y)
    if x > y:
        return max(x - a, y)
    return y


def darken(c, value=50):
    # return ((c & 0x7E7E7E) >> 1) | (c & 0x808080)
    return c - pygame.Color(value, value, value)


class Weapon:
    def __init__(self, stats, displayName):
        self.stats = {  # default stats
            "projectile": {
                "speed": 0.5,  # speed of projectile
                "tpd": 75,  # ticks per drop on the ground
                "damage": 30,  # how much damage it will do
                "size": 5,  # The size of the bullet
                "range": 300,  # how far the bullet will go
                "paintRange": (7, 15),  # how big the droplets on the ground will be
                "landPaint": 20,  # how much it will put on the ground upon landing
                "accuracyDebuff": 15  # how inaccurate the weapon is
            },
            "fireRate": 66,  # ticks until weapon fires again
            "consumption": 2,  # how much ink each shot takes
            "rechargeDelay": 500  # how many ticks until the weapon can recharge ink
        }
        self.stats = self.stats | stats
        self.name = displayName

    def shoot(self, pos, color, dest):
        inkBullet(pos.copy(), dest, color, self.stats["projectile"])


weapons = {
    "defaultTest": Weapon({
        "consumption": 0.9,
        "fireRate": 6,
        "projectile": {
            "range": 500,
            "speed": 0.3,
            "tpd": 10
        },
        "rechargeDelay": 20
    }, "splattershot")
}


class Player:
    def __init__(self, x=0, y=0):
        self.ink = 100  # how much ink the player has
        self.pos = pygame.Vector2(x, y)  # position
        self.vel = pygame.Vector2(0, 0)  # velocity
        self.color = pygame.Color(0xffa500FF)  # color
        self.accel = 0.01  # acceleration
        self.maxsp = 0.1  # max speed
        self.weapon = weapons["defaultTest"]  # weapon
        self.fireWait = 0  # time until I can fire again (weapon determined)
        self.squid = False  # am I in squid form
        self.hidden = False  # am I submerged in ink
        self.rechargeDelay = 0  # the delay before I can recharge ink (weapon determined)
        self.outFrames = 0  # how many frames I have been unsubmerged

    def rect(self):
        return pygame.Rect(self.pos.x - 8, self.pos.y - 8, 16, 16)

    def update(self):
        moveh = keys[pygame.K_d] - keys[pygame.K_a]
        movev = keys[pygame.K_s] - keys[pygame.K_w]

        self.squid = keys[pygame.K_SPACE]

        floorColor = inkSurf.get_at((int(self.pos.x), int(self.pos.y)))
        floorColor.a = 0
        self.outFrames -= self.squid and floorColor == darken(self.color)
        self.hidden = self.squid and floorColor == darken(self.color) and self.outFrames <= 0
        if (self.hidden): outFrames = 10

        speedmult = (1 + self.hidden * 1.5)

        self.vel.x = approach(self.vel.x / dt, moveh * self.maxsp * speedmult, self.accel * speedmult) * dt
        self.vel.y = approach(self.vel.y / dt, movev * self.maxsp * speedmult, self.accel * speedmult) * dt

        self.pos += self.vel
        if pygame.mouse.get_pressed()[0] and self.fireWait <= 0 and not self.squid:
            if self.ink >= self.weapon.stats["consumption"]:
                self.weapon.shoot(self.pos, self.color, pygame.mouse.get_pos())
                self.ink -= self.weapon.stats["consumption"]
            self.rechargeDelay = self.weapon.stats["rechargeDelay"]
            self.fireWait = self.weapon.stats["fireRate"]

        self.fireWait -= 1
        self.ink = min(100, self.ink + ((0.1 + (0.555 * self.hidden)) * int(self.rechargeDelay <= 0)))

        self.pos.x = min(1070, max(0, self.pos.x))
        self.pos.y = min(710, max(0, self.pos.y))

        if self.fireWait <= 0: self.rechargeDelay -= 1

    def __repr__(self):
        return "{player object: weapon: " + self.weapon.name + ", weapon stats: " + str(
            self.weapon.stats) + ", squid: " + str(self.squid) + ", submerged in ink: " + str(self.hidden) + "}"

    def draw(self):
        if not self.squid:
            draw.rect(sc, self.color, self.rect())
        else:
            draw.circle(sc, darken(self.color, int(self.hidden) * 25), self.pos, 8)

        draw.rect(sc, 0, (3, 3, 18, 34))
        draw.rect(sc, self.color, (4, 4, 16, self.ink * 0.32))


projectiles = []


class inkBullet:
    def __init__(self, pos, dest, color, stats={}):
        self.pos = pos
        self.vel = (dest - pos).normalize()
        self.color = color
        self.stats = {
            "speed": 1,
            "tpd": 75,
            "damage": 30,
            "size": 5,
            "range": 300,
            "paintRange": (7, 15),
            "landPaint": 20,
            "accuracyDebuff": 3
        }
        self.paintTime = 0
        self.stats = self.stats | stats
        projectiles.append(self)
        self.paintColor = darken(self.color)
        self.vel = self.vel.rotate(random.randrange(-self.stats["accuracyDebuff"], self.stats["accuracyDebuff"], 1))

    def update(self):
        self.paintTime += dt * (random.random() * 2)
        self.pos += self.vel * self.stats["speed"] * dt
        self.stats["range"] -= dt * (random.random() * 2)

        if self.paintTime >= self.stats["tpd"]:
            self.paintTime = 0
            draw.circle(inkSurf, self.paintColor, self.pos,
                        random.randint(self.stats["paintRange"][0], self.stats["paintRange"][1]))

        if self.stats["range"] <= 0:
            draw.circle(inkSurf, self.paintColor, self.pos, self.stats["landPaint"])
            del projectiles[projectiles.index(self)]

    def draw(self):
        draw.circle(sc, self.color, self.pos, self.stats["size"])


inkSurf = pygame.Surface((1080, 720))
inkSurf.set_colorkey(0)

player = Player()

print(player)

quitLoop = False

while not quitLoop:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitLoop = True

    sc.fill(0xeeeeee)
    sc.blit(inkSurf, (0, 0))

    player.update()
    player.draw()

    for i in projectiles:
        i.update()
        i.draw()

    pygame.display.flip()
    dt = c.tick(60)
