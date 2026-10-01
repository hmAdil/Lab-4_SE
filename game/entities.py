import pygame
from game.maze import CELL

SPEED = 2
WALL_T = 4

class Player:
    def __init__(self, r, c):
        self.r, self.c = r, c
        cx, cy = c*CELL+CELL//2, r*CELL+CELL//2
        self.rect = pygame.Rect(cx-10, cy-10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = SPEED
        nr = self.rect.move(dx, 0)
        if self._valid(nr, walls, rows, cols): self.rect = nr
        nr = self.rect.move(0, dy)
        if self._valid(nr, walls, rows, cols): self.rect = nr

    def _valid(self, rect, walls, rows, cols):
        if rect.left < 0 or rect.top < 0 or rect.right > cols*CELL or rect.bottom > rows*CELL:
            return False
        r0 = max(0, (rect.top - WALL_T)//CELL)
        r1 = min(rows-1, (rect.bottom + WALL_T)//CELL)
        c0 = max(0, (rect.left - WALL_T)//CELL)
        c1 = min(cols-1, (rect.right + WALL_T)//CELL)
        for r in range(r0, r1+1):
            for c in range(c0, c1+1):
                for wall in self._wall_rects(r, c, walls[r][c]):
                    if rect.colliderect(wall):
                        return False
        return True

    def _wall_rects(self, r, c, cell_walls):
        x, y = c*CELL, r*CELL
        h = WALL_T//2
        top, bottom, right, left = cell_walls
        out = []
        if top: out.append(pygame.Rect(x-h, y-h, CELL+WALL_T, WALL_T))
        if bottom: out.append(pygame.Rect(x-h, y+CELL-h, CELL+WALL_T, WALL_T))
        if right: out.append(pygame.Rect(x+CELL-h, y-h, WALL_T, CELL+WALL_T))
        if left: out.append(pygame.Rect(x-h, y-h, WALL_T, CELL+WALL_T))
        return out

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

class Enemy:
    def __init__(self, r, c):
        self.r, self.c = r, c
        cx, cy = c*CELL+CELL//2, r*CELL+CELL//2
        self.rect = pygame.Rect(cx-12, cy-12, 24, 24)
        self.color = (220, 60, 60)
        self.frozen_color = (90, 160, 240)
        self.ice_color = (210, 235, 255)
        self.timer = 0
        self.move_interval = 20
        self.frozen = False
        self.freeze_timer = 0

    def freeze(self, frames):
        self.frozen = True
        self.freeze_timer = frames

    def update(self, walls, player, rows, cols):
        from game.maze import bfs
        if self.frozen:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.frozen = False
                self.freeze_timer = 0
            return
        self.timer += 1
        if self.timer >= self.move_interval:
            self.timer = 0
            pr, pc = player.rect.centery//CELL, player.rect.centerx//CELL
            step = bfs(walls, (self.r, self.c), (pr, pc), rows, cols)
            if step:
                dr, dc = step
                self.r += dr; self.c += dc
                cx, cy = self.c*CELL+CELL//2, self.r*CELL+CELL//2
                self.rect.center = (cx, cy)

    def draw(self, screen):
        body = self.frozen_color if self.frozen else self.color
        pygame.draw.rect(screen, body, self.rect, border_radius=5)
        if self.frozen:
            pygame.draw.rect(screen, self.ice_color, self.rect, width=2, border_radius=5)
            pygame.draw.line(screen, self.ice_color, (self.rect.x+3, self.rect.bottom-6), (self.rect.right-3, self.rect.bottom-6), 2)
        for ex in [self.rect.x+4, self.rect.x+14]:
            pygame.draw.circle(screen, (255,255,255), (ex, self.rect.y+8), 4)
            pygame.draw.circle(screen, (0,0,0), (ex+1, self.rect.y+8), 2)