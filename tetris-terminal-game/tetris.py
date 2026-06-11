#!/usr/bin/env python3
"""
TETRIS - Terminal Edition
Run with: python3 tetris.py
Controls: A/D or LEFT/RIGHT to move, W/UP to rotate, S/DOWN to soft drop, SPACE to hard drop, Q to quit
"""

import curses
import random
import time

BOARD_W, BOARD_H = 10, 20
TICK = 0.5

PIECES = {
    'I': [[(0,1),(1,1),(2,1),(3,1)], [(2,0),(2,1),(2,2),(2,3)]],
    'O': [[(0,0),(1,0),(0,1),(1,1)]],
    'T': [[(1,0),(0,1),(1,1),(2,1)], [(1,0),(1,1),(2,1),(1,2)], [(0,1),(1,1),(2,1),(1,2)], [(1,0),(0,1),(1,1),(1,2)]],
    'S': [[(1,0),(2,0),(0,1),(1,1)], [(1,0),(1,1),(2,1),(2,2)]],
    'Z': [[(0,0),(1,0),(1,1),(2,1)], [(2,0),(1,1),(2,1),(1,2)]],
    'J': [[(0,0),(0,1),(1,1),(2,1)], [(1,0),(2,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(2,2)], [(1,0),(1,1),(0,2),(1,2)]],
    'L': [[(2,0),(0,1),(1,1),(2,1)], [(1,0),(1,1),(1,2),(2,2)], [(0,1),(1,1),(2,1),(0,2)], [(0,0),(1,0),(1,1),(1,2)]],
}

COLORS = {'I':1,'O':2,'T':3,'S':4,'Z':5,'J':6,'L':7}

SCORES = {0:0, 1:100, 2:300, 3:500, 4:800}

class Tetris:
    def __init__(self):
        self.board = [[0]*BOARD_W for _ in range(BOARD_H)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.piece = None
        self.piece_type = None
        self.piece_rot = 0
        self.piece_x = 0
        self.piece_y = 0
        self.next_type = random.choice(list(PIECES.keys()))
        self.spawn()

    def spawn(self):
        self.piece_type = self.next_type
        self.next_type = random.choice(list(PIECES.keys()))
        self.piece_rot = 0
        self.piece = PIECES[self.piece_type][0]
        self.piece_x = BOARD_W // 2 - 2
        self.piece_y = 0
        if not self.valid(self.piece, self.piece_x, self.piece_y):
            self.game_over = True

    def valid(self, shape, ox, oy):
        for (x, y) in shape:
            nx, ny = ox + x, oy + y
            if nx < 0 or nx >= BOARD_W or ny >= BOARD_H:
                return False
            if ny >= 0 and self.board[ny][nx]:
                return False
        return True

    def rotate(self):
        rots = PIECES[self.piece_type]
        new_rot = (self.piece_rot + 1) % len(rots)
        new_shape = rots[new_rot]
        if self.valid(new_shape, self.piece_x, self.piece_y):
            self.piece_rot = new_rot
            self.piece = new_shape
        elif self.valid(new_shape, self.piece_x - 1, self.piece_y):
            self.piece_rot = new_rot
            self.piece = new_shape
            self.piece_x -= 1
        elif self.valid(new_shape, self.piece_x + 1, self.piece_y):
            self.piece_rot = new_rot
            self.piece = new_shape
            self.piece_x += 1

    def move(self, dx):
        if self.valid(self.piece, self.piece_x + dx, self.piece_y):
            self.piece_x += dx

    def drop(self):
        if self.valid(self.piece, self.piece_x, self.piece_y + 1):
            self.piece_y += 1
            return True
        else:
            self.lock()
            return False

    def hard_drop(self):
        while self.valid(self.piece, self.piece_x, self.piece_y + 1):
            self.piece_y += 1
            self.score += 2
        self.lock()

    def ghost_y(self):
        gy = self.piece_y
        while self.valid(self.piece, self.piece_x, gy + 1):
            gy += 1
        return gy

    def lock(self):
        color = COLORS[self.piece_type]
        for (x, y) in self.piece:
            nx, ny = self.piece_x + x, self.piece_y + y
            if 0 <= ny < BOARD_H:
                self.board[ny][nx] = color
        cleared = 0
        new_board = [row for row in self.board if any(c == 0 for c in row)]
        cleared = BOARD_H - len(new_board)
        self.board = [[0]*BOARD_W for _ in range(cleared)] + new_board
        self.lines += cleared
        self.score += SCORES.get(cleared, 0) * self.level
        self.level = self.lines // 10 + 1
        self.spawn()

    def tick(self):
        self.drop()


def draw(stdscr, game, ox, oy):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Ghost piece
    gy = game.ghost_y()
    for (x, y) in game.piece:
        nx, ny = game.piece_x + x, gy + y
        if 0 <= ny < BOARD_H and 0 <= nx < BOARD_W:
            try:
                stdscr.addstr(oy + ny, ox + nx*2, '::',
                    curses.color_pair(COLORS[game.piece_type]) | curses.A_DIM)
            except: pass

    # Board
    for y in range(BOARD_H):
        for x in range(BOARD_W):
            c = game.board[y][x]
            try:
                if c:
                    stdscr.addstr(oy+y, ox+x*2, '[]', curses.color_pair(c) | curses.A_BOLD)
                else:
                    stdscr.addstr(oy+y, ox+x*2, ' .', curses.color_pair(8))
            except: pass

    # Active piece
    for (x, y) in game.piece:
        nx, ny = game.piece_x + x, game.piece_y + y
        if 0 <= ny < BOARD_H:
            try:
                stdscr.addstr(oy+ny, ox+nx*2, '[]',
                    curses.color_pair(COLORS[game.piece_type]) | curses.A_BOLD)
            except: pass

    # Border
    for y in range(BOARD_H):
        try:
            stdscr.addstr(oy+y, ox-2, '|', curses.color_pair(8))
            stdscr.addstr(oy+y, ox+BOARD_W*2, '|', curses.color_pair(8))
        except: pass
    try:
        stdscr.addstr(oy-1,   ox-2, '+' + '-'*BOARD_W*2 + '+', curses.color_pair(8))
        stdscr.addstr(oy+BOARD_H, ox-2, '+' + '-'*BOARD_W*2 + '+', curses.color_pair(8))
    except: pass

    # Sidebar
    sx = ox + BOARD_W*2 + 4
    def sline(row, txt, attr=0):
        try: stdscr.addstr(oy+row, sx, txt, attr)
        except: pass

    sline(0,  '╔══════════╗', curses.color_pair(8))
    sline(1,  '║  TETRIS  ║', curses.color_pair(3) | curses.A_BOLD)
    sline(2,  '╚══════════╝', curses.color_pair(8))
    sline(4,  f'SCORE', curses.A_BOLD)
    sline(5,  f'{game.score:08d}', curses.color_pair(2) | curses.A_BOLD)
    sline(7,  f'LINES', curses.A_BOLD)
    sline(8,  f'{game.lines:05d}', curses.color_pair(1) | curses.A_BOLD)
    sline(10, f'LEVEL', curses.A_BOLD)
    sline(11, f'{game.level:03d}', curses.color_pair(4) | curses.A_BOLD)
    sline(13, 'NEXT', curses.A_BOLD)

    # Next piece preview
    next_shape = PIECES[game.next_type][0]
    nc = COLORS[game.next_type]
    preview = [[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' '],[' ',' ',' ',' ']]
    for (x, y) in next_shape:
        if 0<=y<4 and 0<=x<4:
            try:
                stdscr.addstr(oy+14+y, sx+x*2, '[]', curses.color_pair(nc) | curses.A_BOLD)
            except: pass

    sline(19, 'CONTROLS', curses.A_BOLD)
    sline(20, 'A/D  : Move')
    sline(21, 'W    : Rotate')
    sline(22, 'S    : Soft drop')
    sline(23, 'SPC  : Hard drop')
    sline(24, 'Q    : Quit')

    if game.game_over:
        msg = ' GAME OVER '
        try:
            stdscr.addstr(oy + BOARD_H//2,     ox + BOARD_W - len(msg)//2, msg,
                curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            stdscr.addstr(oy + BOARD_H//2 + 1, ox + BOARD_W - 5, ' PRESS R ',
                curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
        except: pass

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    # Init colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,    -1)  # I
    curses.init_pair(2, curses.COLOR_YELLOW,  -1)  # O
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)  # T
    curses.init_pair(4, curses.COLOR_GREEN,   -1)  # S
    curses.init_pair(5, curses.COLOR_RED,     -1)  # Z
    curses.init_pair(6, curses.COLOR_BLUE,    -1)  # J
    curses.init_pair(7, curses.COLOR_WHITE,   -1)  # L
    curses.init_pair(8, curses.COLOR_WHITE,   -1)  # UI

    game = Tetris()
    h, w = stdscr.getmaxyx()
    ox = max(2, w//2 - BOARD_W)
    oy = max(1, h//2 - BOARD_H//2)

    last_tick = time.time()
    speed = TICK

    while True:
        speed = max(0.05, TICK - (game.level - 1) * 0.04)

        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break
        elif key in (ord('r'), ord('R')) and game.game_over:
            game = Tetris()
        elif not game.game_over:
            if key in (curses.KEY_LEFT,  ord('a'), ord('A')): game.move(-1)
            elif key in (curses.KEY_RIGHT, ord('d'), ord('D')): game.move(1)
            elif key in (curses.KEY_UP,   ord('w'), ord('W')): game.rotate()
            elif key in (curses.KEY_DOWN,  ord('s'), ord('S')):
                game.drop()
                game.score += 1
            elif key == ord(' '): game.hard_drop()

        now = time.time()
        if now - last_tick >= speed and not game.game_over:
            game.tick()
            last_tick = now

        h, w = stdscr.getmaxyx()
        ox = max(2, w//2 - BOARD_W)
        oy = max(1, h//2 - BOARD_H//2)
        draw(stdscr, game, ox, oy)
        time.sleep(0.016)

if __name__ == '__main__':
    curses.wrapper(main)
