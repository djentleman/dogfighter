import sys
import time
import curses
import random
from sprite_loader import Sprite


belts = [
    '...',
    '.,.',
    '.\'\'',
    '\'""',
    '"""',
    '"|"',
    '|||',
    '||^',
    '^|^',
    '^^^'
]


def get_bullet_damage(bullet):
    return {
        '.': 2,
        ',': 3,
        '\'': 4,
        '"': 5,
        '|': 8,
        '^': 10,
        'v': 10,
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
        stdscr.attron(curses.color_pair(self.col))
        stdscr.addstr(int(self.y), int(self.x), self.char)
        stdscr.attroff(curses.color_pair(self.col))

class Aircraft():

    def __init__(self):
        pass

    def render(self, stdscr):
        self.sprite.render(stdscr, int(self.x), int(self.y))

class Ammo(Bullet):
    def __init__(self, x, y, col=1):
        self.sprite = Sprite('ammo', 1)
        self.x = x
        self.y = y
        self.col = col
        self.vel = 0.3

    def render(self, stdscr):
        self.sprite.render(stdscr, int(self.x), int(self.y), col=1)



class Enemy(Aircraft):
    def __init__(self, sprite, x, y, vx, vy, hp, ai=1):
        self.name = sprite
        self.sprite = Sprite(sprite, 2)
        self.dead = False
        self.explode = False
        self.init_hp = hp
        self.ai = ai
        self.hp = hp
        self.ammo = 300
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.tick = 0
        if sprite in ['enemy0', 'enemy1']:
            self.belt = '...'
        if sprite in ['enemy2']:
            self.belt = '..\''
        if sprite in ['enemy3']:
            self.belt = ',\'"'

    def shoot(self):
        bullets = []
        char = self.belt[self.tick % len(self.belt)]
        if self.ai == 1:
            if random.random() > 0.95:
                if self.ammo > 6:
                    bullets.append(Bullet(char, 0.6, 0, self.x-5, self.y))
                    bullets.append(Bullet(char, 0.6, 0, self.x+5, self.y))
                    self.tick += 1
                    char = self.belt[self.tick % len(self.belt)]
                    bullets.append(Bullet(char, 0.6, 0, self.x-5, self.y-1))
                    bullets.append(Bullet(char, 0.6, 0, self.x+5, self.y-1))
                    self.tick += 1
                    char = self.belt[self.tick % len(self.belt)]
                    bullets.append(Bullet(char, 0.6, 0, self.x-5, self.y+1))
                    bullets.append(Bullet(char, 0.6, 0, self.x+5, self.y+1))
                    self.ammo -= 6
        elif self.ai in [2, 3]:
            if random.random() > 0.92:
                if self.ammo > 4:
                    bullets.append(Bullet(char, 0.8, 0, self.x-4, self.y))
                    bullets.append(Bullet(char, 0.8, 0, self.x+4, self.y))
                    self.tick += 1
                    char = self.belt[self.tick % len(self.belt)]
                    bullets.append(Bullet(char, 0.8, 0, self.x-4, self.y+1))
                    bullets.append(Bullet(char, 0.8, 0, self.x+4, self.y+1))
                    self.ammo -= 4
        elif self.ai in [4]:
            if random.random() > 0.85:
                if self.ammo > 2:
                    bullets.append(Bullet(char, 1.2, 0, self.x-4, self.y))
                    bullets.append(Bullet(char, 1.2, 0, self.x+4, self.y))
                    self.ammo -= 2
        elif self.ai in [5]:
            if random.random() > 0.85:
                if self.ammo > 4:
                    bullets.append(Bullet(char, 1.2, 0, self.x-4, self.y))
                    bullets.append(Bullet(char, 1.2, 0, self.x+4, self.y))
                    bullets.append(Bullet(char, 1.2, 0, self.x-3, self.y))
                    bullets.append(Bullet(char, 1.2, 0, self.x+3, self.y))
                    self.ammo -= 4

        self.tick += 1
        return bullets

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
        if self.hp <= 0:
            if self.sprite.render_count > self.sprite.l+1:
                self.dead = True


    def damage(self, d=2):
        self.hp -= d
        if self.hp <= 0:
            if not self.explode:
                self.sprite = Sprite('enemy0_death', 3)
                self.explode = True

class Player(Aircraft):
    def __init__(self, x, y, col=0):
        self.sprite = Sprite('player', 2)
        self.col = col
        self.hp = 100
        self.ammo = 1000
        self.explode = False
        self.belt = '...'
        self.tick = 0
        self.x = x
        self.y = y
        self.points = 0
        self.kills = 0
        self.lives = 2

    def move(self, x, y):
        self.x = x
        self.y = y
        if self.hp <= 0:
            if self.sprite.render_count > self.sprite.l+1:
                self.sprite = Sprite('player', 2)
                self.lives -= 1
                self.hp = 100
                self.ammo = 1000

    def shoot(self):
        bullets = []
        char = self.belt[self.tick % len(self.belt)]
        if self.ammo <= 4:
            return []
        bullets.append(Bullet(char, -1, 1, self.x-3, self.y))
        bullets.append(Bullet(char, -1, 1, self.x+3, self.y))
        bullets.append(Bullet(char, -1, 1, self.x-4, self.y))
        bullets.append(Bullet(char, -1, 1, self.x+4, self.y))
        self.ammo -= 4
        self.tick += 1
        return bullets

    def damage(self, d=2):
        self.hp -= d
        if self.hp <= 0:
            if not self.explode:
                self.sprite = Sprite('player_death', 3)
                self.explode = True


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
        self.ammo = None
        self.close = False

    def init_screen(self, stdscr):
        curses.halfdelay(1) # 10/10 = 1[s] inteval
        self.stdscr = stdscr
        curses.curs_set(0)
        self.height, self.width = self.stdscr.getmaxyx()

        self.k = 0
        self.cursor_x = self.width // 2
        self.cursor_y = int(self.height * 0.8)
        self.player = Player(self.cursor_x, self.cursor_y, col=1)

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
        self.stdscr.addstr(12, 10, f'Points: {self.player.points}')
        self.stdscr.addstr(13, 10, f'Kills: {self.player.kills}')
        self.stdscr.addstr(14, 10, f'Lives: {self.player.lives}')

    def process_input(self):
        if self.k in [curses.KEY_DOWN, ord('j')]:
            self.cursor_y = self.cursor_y + 1
        elif self.k in [curses.KEY_UP, ord('k')]:
            self.cursor_y = self.cursor_y - 1
        elif self.k in [curses.KEY_RIGHT, ord('l')]:
            self.cursor_x = self.cursor_x + 1
        elif self.k in [curses.KEY_LEFT, ord('h')]:
            self.cursor_x = self.cursor_x - 1
        elif self.k == ord(' '):
            self.bullets += self.player.shoot()
        elif self.k == ord('q'):
            self.close = True
        self.cursor_x = max(7, self.cursor_x)
        self.cursor_x = min(self.width - 8, self.cursor_x)
        self.cursor_y = max(5, self.cursor_y)
        self.cursor_y = min(self.height - 6, self.cursor_y)

    def event_loop(self):
        self.stdscr.clear()
        self.stdscr.move(self.cursor_y, self.cursor_x)
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
                    if len(self.enimies) == 0:
                        self.enimies.append(Enemy('enemy1', 60, 10, 0.8, 0, 25))
                        self.enimies.append(Enemy('enemy1', 80, 18, -0.8, 0, 25))
                if e.x > self.width - 5 or e.x < 5:
                    del self.enimies[i]
                elif e.y > self.height - 5:
                    del self.enimies[i]

                if collision_check(e, self.player):
                    self.player.damage(e.init_hp)
                    self.player.points -= e.init_hp*2
                    e.damage(100)

            for i, b in enumerate(self.bullets):
                self.bullets[i].update()
                if b.y <= 1:
                    del self.bullets[i]
                if b.y >= self.height-2:
                    del self.bullets[i]
                b.render(self.stdscr)
                # collision check
                if b.vel > 0:
                    if collision_check(b, self.player):
                        self.player.damage(get_bullet_damage(b.char))
                        del self.bullets[i]
                else:
                    for e in self.enimies:
                        if collision_check(b, e):
                            e.damage(get_bullet_damage(b.char))
                            self.player.points += 2
                            del self.bullets[i]

            if self.ammo is not None:
                self.ammo.render(self.stdscr)
                self.ammo.update()
                if self.ammo.y > self.height - 10:
                    self.ammo = None
                elif collision_check(self.ammo, self.player):
                    self.player.ammo += 500
                    self.ammo = None

            #self.stdscr.move(self.cursor_y, self.cursor_x)
            self.player.move(self.cursor_x, self.cursor_y)
            self.player.render(self.stdscr)
            self.k = self.stdscr.getch()
            if self.k != -1:
                self.process_input()

            if len(self.enimies) < 6:
                if self.player.kills > 1:
                    if random.random() > 0.995:
                        enemy = Enemy('enemy0', 20, 20, 1, 0, 10, ai=2)
                        self.enimies.append(enemy)
                    if random.random() > 0.995:
                        enemy = Enemy('enemy0', self.width-20, 20, 1, 0, 10, ai=3)
                        self.enimies.append(enemy)

                if self.player.kills > 5:
                    if random.random() > 0.999:
                        enemy = Enemy('enemy2', self.width // 2, 10, 0.5, 0.1, 40, ai=4)
                        self.enimies.append(enemy)
                    if random.random() > 0.999:
                        enemy = Enemy('enemy2', self.width // 2, 10, -0.5, 0.1, 40, ai=4)
                        self.enimies.append(enemy)

                if self.player.kills > 10:
                    if random.random() > 0.999:
                        enemy = Enemy('enemy3', self.width // 2, 10, 1.2, 0.1, 80, ai=5)
                        self.enimies.append(enemy)
                    if random.random() > 0.999:
                        enemy = Enemy('enemy3', self.width // 2, 10, -1.2, 0.1, 80, ai=5)
                        self.enimies.append(enemy)

            if self.player.ammo < 200:
                if self.ammo is None:
                    if random.random() > 0.95:
                        self.ammo = Ammo(random.randint(20, 100), 20)

            self.stdscr.refresh()


        curses.endwin()


def main():
    atig = Game()
    curses.wrapper(atig.init_screen)


if __name__ == "__main__":
    main()
