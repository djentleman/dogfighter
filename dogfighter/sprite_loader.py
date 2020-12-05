import curses
import os
from pathlib import Path

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = ROOT_DIR / 'sprites'


class Sprite():
    def __init__(self, path, length):
        self.l = length
        self.sprite_data = [
            [list(l.replace('\n', '')) for l in open(str(SPRITES_DIR / f'{path}_{j}.txt')).readlines()]
            for j in range(self.l)]
        self.height = len(self.sprite_data[0])
        self.width = max([len(l) for l in self.sprite_data[0]])
        self.render_count = 0

    def render(self, stdscr, x, y, col=0):
        stdscr.attron(curses.color_pair(col))
        rid = self.render_count % self.l
        sprite_frame = self.sprite_data[rid]
        sx = x - self.width // 2
        sy = y - self.height // 2
        cx, cy = sx, sy
        for i in range(self.height):
            string = sprite_frame[i]
            stdscr.addstr(cy+i, cx, ''.join(string))
        self.render_count += 1
        stdscr.attroff(curses.color_pair(col))



