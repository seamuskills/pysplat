import pygame
import random
from pygame import draw

pygame.init()
sc = pygame.display.set_mode((1080, 720))
c = pygame.time.Clock()
dt = 1
keys = None

def approach(x, y, a):
    if x < y:
        return min(x+a, y)
    if x > y:
        return max(x-a, y)
    return y

def darken(c, value=50):
    #return ((c & 0x7E7E7E) >> 1) | (c & 0x808080)
    return c - pygame.Color(value, value, value)

class Weapon:
    def __init__(self, stats, displayName):
        self.stats = {
            "projectile": {
                "speed": 0.5,
                "tpd": 75,
                "damage": 30,
                "size": 5,
                "range": 300,
                "paintRange": (7,15),
                "landPaint": 20,
                "accuracyDebuff": 15
            },
            "fireRate": 66,
            "consumption": 2,
            "rechargeDelay": 500
        }
        self.stats = self.stats | stats
        self.name = displayName

    def shoot(self, pos, color, dest):
        inkBullet(pos.copy(), dest, color, self.stats["projectile"])

weapons = {
    "defaultTest": Weapon({}, "missingno")
}


class Player:
    def __init__(self, x=0, y=0):
        self.ink = 100
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.color = pygame.Color(0xffa500FF)
        self.accel = 0.01
        self.maxsp = 0.1
        self.weapon = weapons["defaultTest"]
        self.fireWait = 0
        self.squid = False
        self.hidden = False
        self.rechargeDelay = 0

    def rect(self):
        return pygame.Rect(self.pos.x-8, self.pos.y-8, 16, 16)

    def update(self):
        moveh = keys[pygame.K_d] - keys[pygame.K_a]
        movev = keys[pygame.K_s] - keys[pygame.K_w]

        self.squid = keys[pygame.K_SPACE]

        floorColor = inkSurf.get_at((int(self.pos.x), int(self.pos.y)))
        floorColor.a = 0
        self.hidden = self.squid and floorColor == darken(self.color)

        speedmult = (1+self.hidden*1.5)

        self.vel.x = approach(self.vel.x/dt, moveh*self.maxsp*speedmult, self.accel*speedmult)*dt
        self.vel.y = approach(self.vel.y/dt, movev*self.maxsp*speedmult, self.accel*speedmult)*dt

        self.pos += self.vel
        if pygame.mouse.get_pressed()[0] and self.fireWait <= 0 and not self.squid:
            if self.ink > self.weapon.stats["consumption"]:
                self.weapon.shoot(self.pos, self.color, pygame.mouse.get_pos())
                self.fireWait = self.weapon.stats["fireRate"]
                self.ink -= self.weapon.stats["consumption"]
            self.rechargeDelay = self.weapon.stats["rechargeDelay"]

        self.fireWait -= dt
        self.ink = min(100, self.ink + (0.1 * (1 + self.hidden * 10) * int(self.rechargeDelay <= 0)))

        self.pos.x = min(1070, max(0, self.pos.x))
        self.pos.y = min(710, max(0, self.pos.y))

        self.rechargeDelay -= dt

    def __repr__(self):
        return "{player object: weapon: " + self.weapon.name + ", weapon stats: " + str(self.weapon.stats) + ", squid: " + str(self.squid) + ", submerged in ink: " + str(self.hidden) + "}"

    def draw(self):
        if not self.squid:
            draw.rect(sc, self.color, self.rect())
        else:
            draw.circle(sc, darken(self.color, int(self.hidden)*25), self.pos, 8)

        draw.rect(sc, 0, (3, 3, 18, 34))
        draw.rect(sc, darken(self.color,50 * (self.rechargeDelay >= 0)), (4, 4, 16, self.ink*0.32))


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
            "paintRange": (7,15),
            "landPaint": 20,
            "accuracyDebuff": 3
        }
        self.paintTime = 0
        self.stats = self.stats | stats
        projectiles.append(self)
        self.paintColor = darken(self.color)
        self.vel = self.vel.rotate(random.randrange(-self.stats["accuracyDebuff"], self.stats["accuracyDebuff"], 1))

    def update(self):
        self.paintTime += dt * (random.random()*2)
        self.pos += self.vel*self.stats["speed"]*dt
        self.stats["range"] -= dt * (random.random()*2)

        if self.paintTime >= self.stats["tpd"]:
            self.paintTime = 0
            draw.circle(inkSurf, self.paintColor, self.pos, random.randint(self.stats["paintRange"][0], self.stats["paintRange"][1]))

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
