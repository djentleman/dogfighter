import sys
import time
import curses
import random
from sprite_loader import Sprite


belts = [
    '...',
    '.,.',
    '.,,',
    '.,\'',
    ',,"',
    '\'\'\'',
    '\'""',
    '"""',
    '"|"',
    '"||',
    '|||',
    '||^',
    '^|^',
    '^^^'
]


def get_bullet_damage(bullet):
    return {
        ' ': 0,
        '.': 2,
        ',': 3,
        '\'': 4,
        '"': 5,
        '|': 8,
        '^': 10,
        'v': 10,
        'U': 30,
    }.get(bullet, 1)


class Bullet():
    def __init__(self, char, vel, col, x, y):
        self.char = char
        self.vel = vel
        self.col = col
        self.x = x
        self.y = y

    def update(self):
        self.y += self.vel

    def render(self, stdscr):
        try:
            stdscr.attron(curses.color_pair(self.col))
            stdscr.addstr(int(self.y), int(self.x), self.char)
            stdscr.attroff(curses.color_pair(self.col))
        except:
            pass


class Drop(Bullet):
    def __init__(self, x, y, sprite, col=1):
        super().__init__(' ', 0.3, col, x, y)
        self.name = sprite
        self.sprite = Sprite(sprite, 1)

    def render(self, stdscr):
        self.sprite.render(stdscr, int(self.x), int(self.y), col=1)

class Aircraft():

    def __init__(self, sprite, x, y, vx, vy, hp, ai=1, ammo=300, col=0, belt='.', guns=[-5, 5], gun_vel=1):
        self.name = sprite
        self.sprite = Sprite(sprite, 2)
        self.dead = False
        self.explode = False
        self.init_hp = hp
        self.hp = hp
        self.ai = ai
        self.ammo = ammo
        self.x = x
        self.y = y
        self.init_x = x
        self.init_y = y
        self.vx = vx
        self.vy = vy
        self.col = col
        self.tick = 0
        self.guns = guns
        self.belt = belt
        self.gun_vel = gun_vel

    def render(self, stdscr):
        stdscr.attron(curses.color_pair(self.col))
        #stdscr.addstr(int(self.y-5), int(self.x-3), f'{self.hp}/{self.init_hp}')
        self.sprite.render(stdscr, int(self.x), int(self.y))
        stdscr.attroff(curses.color_pair(self.col))


    def damage(self, d=2):
        self.hp -= d
        if self.hp <= 0:
            if not self.explode:
                self.explode = True
                self.sprite = Sprite(f'{self.name}_death', 3)

    def shoot(self):
        bullets = []
        char = self.belt[self.tick % len(self.belt)]
        if self.ammo > len(self.guns):
            for g in self.guns:
                if random.random() < 1: # jan chance
                    bullets.append(Bullet(char, self.gun_vel, self.col, self.x+g, self.y))
                    self.ammo -= 1
        self.tick += 1
        return bullets


class Enemy(Aircraft):
    def __init__(self, sprite, x, y, vx, vy, hp, ai=1, col=0, ammo=300):
        if sprite in ['enemy0']:
            belt = '. .'
            guns = [-5, 5]
            gun_vel = 0.5
        elif sprite in ['enemy1']:
            belt = '...'
            guns = [-4, 4]
            gun_vel = 0.6
        elif sprite in ['enemy2']:
            belt = '..\''
            guns = [-4, 4]
            gun_vel = 0.8
        elif sprite in ['enemy3']:
            belt = ',\'"'
            guns = [-4, -3, 3, 4]
            gun_vel = 1.2
        elif sprite in ['bossD']:
            belt = '"""'
            gun_vel = 1.1
            guns = [-6, -2, 0, 2, 6]
            ammo = 5000
        else:
            belt = '.'
            guns = [0]
            gun_vel = 0.6
        super().__init__(sprite, x, y, vx, vy, hp, ai=ai, belt=belt, col=col, guns=guns, gun_vel=gun_vel, ammo=ammo)

    def shoot(self):
        char = self.belt[self.tick % len(self.belt)]
        if self.name == 'bossD':
            bullets = []
            if random.random() > 0.85:
                bullets += super().shoot()
            if random.random() > 0.8:
                bullets += [Bullet('U', 0.3, self.col, self.x, self.y)]
            return bullets
        if self.ai in [1, 6]:
            if random.random() > 0.92:
                return super().shoot()
        elif self.ai in [2, 3]:
            if random.random() > 0.95:
                return super().shoot()
        elif self.ai in [4, 5]:
            if random.random() > 0.85:
                return super().shoot()

        return []

    def move(self):
        if self.ai == 1:
            self.x += self.vx
            if self.x >= 150:
                self.vx = -self.vx
                self.y += 1
            if self.x <= 50:
                self.vx = -self.vx
                self.y += 1
        elif self.ai == 2:
            self.x += 1
            self.y += 0.3
        elif self.ai == 3:
            self.x += -1
            self.y += 0.3
        elif self.ai in [4, 5]:
            if self.x >= 150:
                self.vx = -self.vx
            if self.x <= 50:
                self.vx = -self.vx
            self.x += self.vx
            self.y += self.vy
        elif self.ai == 6:
            self.y += self.vy
        if self.hp <= 0:
            if self.sprite.render_count > self.sprite.l+1:
                self.dead = True


class Player(Aircraft):
    def __init__(self, x, y, col=1):
        super().__init__('player', x, y, 1, 0, 100, ammo=1000, ai=0, belt='...', col=col, guns=[-4, -3, 3, 4], gun_vel=-1)
        self.belt_id = 0
        self.belt = belts[self.belt_id]
        self.points = 0
        self.kills = 0
        self.lives = 3

    def move(self):
        if self.hp <= 0:
            if self.sprite.render_count > self.sprite.l+1:
                self.sprite = Sprite('player', 2)
                self.lives -= 1
                self.explode = False
                self.x = self.init_x
                self.y = self.init_y
                self.hp = 100
                self.ammo = 1000

    def shoot(self):
        self.belt = belts[min(self.belt_id, len(belts)-1)]
        return super().shoot()


def collision_check(projectile, target):
    if projectile.y > target.y - 3 and projectile.y < target.y + 3:
        if projectile.x > target.x - 4 and projectile.x < target.x + 4:
            return True
    return False



class Game():
    def __init__(self):
        self.migrations = None
        self.migration_collection = None
        self.display_window_contents = []
        self.bullets = []
        self.enimies = []
        self.drops = []
        self.close = False

    def init_screen(self, stdscr):
        curses.halfdelay(1) # 10/10 = 1[s] inteval
        self.stdscr = stdscr
        curses.curs_set(0)
        self.height, self.width = self.stdscr.getmaxyx()

        self.k = 0
        px = self.width // 2
        py = int(self.height * 0.8)
        self.player = Player(px, py, col=1)

        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self.event_loop()

    def render_data(self):
        self.stdscr.addstr(10, 10, f'Health: {self.player.hp}')
        self.stdscr.addstr(11, 10, f'Ammo: {self.player.ammo}')
        self.stdscr.addstr(12, 10, f'Belt: {self.player.belt}')
        self.stdscr.addstr(13, 10, f'Points: {self.player.points}')
        self.stdscr.addstr(14, 10, f'Kills: {self.player.kills}')
        self.stdscr.addstr(15, 10, f'Lives: {self.player.lives}')

    def process_input(self):
        if self.k in [curses.KEY_DOWN, ord('j')]:
            self.player.y += self.player.vx
        elif self.k in [curses.KEY_UP, ord('k')]:
            self.player.y -= self.player.vx
        elif self.k in [curses.KEY_RIGHT, ord('l')]:
            self.player.x += self.player.vx
        elif self.k in [curses.KEY_LEFT, ord('h')]:
            self.player.x -= self.player.vx
        elif self.k == ord(' '):
            self.bullets += self.player.shoot()
        elif self.k == ord('q'):
            self.close = True
        self.player.x = max(7, self.player.x)
        self.player.x = min(self.width - 8, self.player.x)
        self.player.y = max(5, self.player.y)
        self.player.y = min(self.height - 6, self.player.y)

    def event_loop(self):
        self.stdscr.clear()
        ex = 75
        ey = 10
        enemy = Enemy('enemy1', ex, ey, 0.8, 0, 25)
        self.enimies.append(enemy)
        # Loop where k is the last character pressed

        while (not self.close):
            self.stdscr.clear()
            if self.player.lives <= 0:
                break

            self.render_data()
            # Wait for next input
            # Refresh the screen
            for i, e in enumerate(self.enimies):
                e.render(self.stdscr)
                self.bullets += e.shoot()
                e.move()
                if e.dead:
                    del self.enimies[i]
                    self.player.kills += 1
                    self.player.points += e.init_hp*2
                    if e.name == 'bossD':
                        self.drops.append(Drop(e.x, e.y, 'upgr'))
                        self.drops.append(Drop(e.x-10, e.y, 'upgr'))
                        self.drops.append(Drop(e.x+10, e.y, 'upgr'))
                        self.drops.append(Drop(e.x, e.y+10, 'ammo'))
                        self.player.lives += 3
                    if e.name == 'enemy3':
                        self.drops.append(Drop(e.x, e.y, 'upgr'))
                    if e.name == 'enemy2' and random.random() > 0.7:
                        self.drops.append(Drop(e.x, e.y, 'upgr'))
                    if e.name == 'enemy1' and random.random() > 0.85:
                        self.drops.append(Drop(e.x, e.y, 'upgr'))
                    if e.name == 'enemy0' and random.random() > 0.95:
                        self.drops.append(Drop(e.x, e.y, 'ammo'))

                if e.x > self.width - 5 or e.x < 5:
                    del self.enimies[i]
                elif e.y > self.height - 5:
                    del self.enimies[i]

                if collision_check(e, self.player):
                    self.player.damage(e.init_hp)
                    if self.player.explode:
                        self.enimies = []
                        self.bullets = []
                        break
                    self.player.points -= e.init_hp*2
                    e.damage(100)

            for i, b in enumerate(self.bullets):
                self.bullets[i].update()
                if b.y <= 1+b.vel:
                    del self.bullets[i]
                if b.y >= self.height-2+b.vel:
                    del self.bullets[i]
                b.render(self.stdscr)
                # collision check
                if b.vel > 0:
                    if collision_check(b, self.player):
                        self.player.damage(get_bullet_damage(b.char))
                        if self.player.explode:
                            self.enimies = []
                            self.bullets = []
                            break
                        del self.bullets[i]
                else:
                    for e in self.enimies:
                        if collision_check(b, e):
                            e.damage(get_bullet_damage(b.char))
                            self.player.points += 2
                            del self.bullets[i]

            for i, drop in enumerate(self.drops):
                drop.render(self.stdscr)
                drop.update()
                if drop.y > self.height - 10:
                    del self.drops[i]
                    continue
                if collision_check(drop, self.player):
                    if drop.name == 'upgr':
                        r = random.random()
                        if r < 0.3:
                            self.player.ammo += 200
                            self.player.belt_id += 1
                        elif r < 0.5:
                            self.player.init_hp += 10
                            self.player.hp += 10
                        elif r < 0.65:
                            self.player.gun_vel -= 0.1
                            self.player.ammo += 200
                        elif r < 0.8:
                            if len(self.player.guns) == 4:
                                self.player.guns.append(0)
                            else:
                                self.player.belt_id += 1
                        else:
                            self.player.vx += 0.1
                    elif drop.name == 'repr':
                        self.player.hp = self.player.init_hp
                    elif drop.name == 'ammo':
                        self.player.ammo += 500
                    del self.drops[i]
                    continue

            #self.stdscr.move(self.cursor_y, self.cursor_x)
            self.player.move()
            self.player.render(self.stdscr)
            self.k = self.stdscr.getch()
            if self.k != -1:
                self.process_input()

            if len(self.enimies) < 6:
                if self.player.kills <= 20:
                    if self.player.kills > 0:
                        if random.random() > 0.995:
                            enemy = Enemy('enemy0', 20, 20, 1, 0, 10, ai=2)
                            self.enimies.append(enemy)
                        if random.random() > 0.995:
                            enemy = Enemy('enemy0', self.width-20, 20, 1, 0, 10, ai=3)
                            self.enimies.append(enemy)

                    if self.player.kills > 5:
                        if random.random() > 0.995:
                            enemy = Enemy('enemy1', self.width // 2, 20, 0.8, 0, 25)
                            self.enimies.append(enemy)
                        if random.random() > 0.995:
                            enemy = Enemy('enemy1', self.width // 2, 20, -0.6, 0, 25, ai=1)
                            self.enimies.append(enemy)

                    if self.player.kills > 10:
                        if random.random() > 0.995:
                            enemy = Enemy('enemy0', 20 + (self.width-20)*random.random(), 20, 0, 0.3, 10, ai=6)
                            self.enimies.append(enemy)


                elif self.player.kills > 20 and self.player.kills <= 50:
                    if random.random() > 0.997:
                        enemy = Enemy('enemy2', self.width // 2, 10, 0.5, 0.1, 40, ai=4)
                        self.enimies.append(enemy)
                    if random.random() > 0.997:
                        enemy = Enemy('enemy2', self.width // 2, 10, -0.5, 0.1, 40, ai=4)
                        self.enimies.append(enemy)
                    if random.random() > 0.997:
                        enemy = Enemy('enemy1', self.width-20, 20, 1, 0, 25, ai=3)
                        self.enimies.append(enemy)
                    if random.random() > 0.997:
                        enemy = Enemy('enemy1', 20, 20, 1, 0, 25, ai=2)
                        self.enimies.append(enemy)

                    if self.player.kills > 30:
                        if random.random() > 0.998:
                            enemy = Enemy('enemy3', self.width // 2, 10, 0.7, 0.1, 60, ai=5)
                            self.enimies.append(enemy)
                        if random.random() > 0.998:
                            enemy = Enemy('enemy3', self.width // 2, 10, -0.7, 0.1, 60, ai=5)
                            self.enimies.append(enemy)
                        if random.random() > 0.999:
                            enemy = Enemy('enemy3', self.width // 2, 10, 0.7, 0.1, 80, ai=5, col=2)
                            self.enimies.append(enemy)
                        if random.random() > 0.999:
                            enemy = Enemy('enemy3', self.width // 2, 10, -0.7, 0.1, 80, ai=5, col=2)
                            self.enimies.append(enemy)
                        if random.random() > 0.997:
                            enemy = Enemy('enemy2', self.width-20, 20, 1, 0, 40, ai=3)
                            self.enimies.append(enemy)
                        if random.random() > 0.997:
                            enemy = Enemy('enemy2', 20, 20, 1, 0, 40, ai=2)
                            self.enimies.append(enemy)

                elif self.player.kills > 50:
                    if len(self.enimies) == 0:
                        enemy = Enemy('bossD', self.width // 2, 10, 0.6, 0.03, 600, ai=5, col=2)
                        self.enimies.append(enemy)
                        enemy = Enemy('enemy3', 70, 10, 0.7, 0.1, 60, ai=5, col=0)
                        self.enimies.append(enemy)
                        enemy = Enemy('enemy3', self.width - 70, 30, -0.7, 0.1, 60, ai=5, col=0)
                        self.enimies.append(enemy)

            if self.player.ammo < 200:
                if not any([d.name == 'ammo' for d in self.drops]):
                    if random.random() > 0.997:
                        self.drops.append(Drop(random.randint(20, 100), 20, 'ammo'))

            if self.player.hp < 30:
                if not any([d.name == 'repr' for d in self.drops]):
                    if random.random() > 0.999:
                        self.drops.append(Drop(random.randint(20, 100), 20, 'repr'))

            self.stdscr.refresh()


        curses.endwin()


def main():
    atig = Game()
    curses.wrapper(atig.init_screen)


if __name__ == "__main__":
    main()
