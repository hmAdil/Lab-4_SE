import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60
RAMP_MS = 15000
RAMP_STEP = 2
MIN_INTERVAL = 5
FREEZE_FRAMES = 300
PELLET_CELL = (ROWS//2, COLS//2 - 2)
PELLET_R = 7

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.small_font = pygame.font.SysFont("monospace", 16)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)
        self.enemies = [
            Enemy(0, COLS-1),
            Enemy(ROWS-1, 0),
            Enemy(ROWS-1, COLS-1),
        ]
        self.exit_rect = pygame.Rect((COLS//2)*CELL+5, (ROWS//2)*CELL+5, CELL-10, CELL-10)
        pr, pc = PELLET_CELL
        pcx, pcy = pc*CELL+CELL//2, pr*CELL+CELL//2
        self.pellet = pygame.Rect(pcx-PELLET_R, pcy-PELLET_R, PELLET_R*2, PELLET_R*2)
        self.caught = False
        self.won = False
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed = 0
        self.tier = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
        return True

    def _apply_ramp(self):
        target = self.elapsed // RAMP_MS
        while self.tier < target:
            self.tier += 1
            for enemy in self.enemies:
                enemy.move_interval = max(MIN_INTERVAL, enemy.move_interval - RAMP_STEP)

    def _at_speed_floor(self):
        return all(e.move_interval <= MIN_INTERVAL for e in self.enemies)

    def update(self):
        if self.caught or self.won: return
        self.elapsed = pygame.time.get_ticks() - self.start_ticks
        self._apply_ramp()
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)
        if self.pellet is not None and self.player.rect.colliderect(self.pellet):
            self.pellet = None
            for enemy in self.enemies:
                enemy.freeze(FREEZE_FRAMES)
        for enemy in self.enemies:
            enemy.update(self.walls, self.player, ROWS, COLS)
            if self.player.rect.colliderect(enemy.rect):
                self.caught = True
        if self.player.rect.colliderect(self.exit_rect):
            self.won = not self.caught

    def draw(self):
        self.screen.fill((230, 220, 210))
        wc=(50,40,60)
        for r in range(ROWS):
            for c in range(COLS):
                x,y=c*CELL,r*CELL
                w=self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen,wc,(x,y),(x+CELL,y),3)
                if w[1]: pygame.draw.line(self.screen,wc,(x,y+CELL),(x+CELL,y+CELL),3)
                if w[2]: pygame.draw.line(self.screen,wc,(x+CELL,y),(x+CELL,y+CELL),3)
                if w[3]: pygame.draw.line(self.screen,wc,(x,y),(x,y+CELL),3)
        pygame.draw.rect(self.screen,(80,200,80),self.exit_rect,border_radius=4)
        lbl=self.font.render("EXIT",True,(20,80,20))
        self.screen.blit(lbl,(self.exit_rect.x+2,self.exit_rect.y+6))
        if self.pellet is not None:
            pygame.draw.circle(self.screen,(250,220,40),self.pellet.center,PELLET_R)
            pygame.draw.circle(self.screen,(180,140,10),self.pellet.center,PELLET_R,2)
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        hud=pygame.Rect(0,ROWS*CELL,WIDTH,50)
        pygame.draw.rect(self.screen,(30,30,50),hud)
        info=self.small_font.render("Reach EXIT before the enemies catch you!  R=Restart",True,(200,200,200))
        self.screen.blit(info,(8,ROWS*CELL+8))
        tier_label = "MAX" if self._at_speed_floor() else str(self.tier + 1)
        secs = self.elapsed // 1000
        text = f"Enemy speed tier: {tier_label}   Time: {secs}s"
        frozen_left = max(e.freeze_timer for e in self.enemies)
        if frozen_left > 0:
            text += f"   FROZEN: {frozen_left / FPS:.1f}s"
        speed=self.small_font.render(text,True,(240,190,90))
        self.screen.blit(speed,(8,ROWS*CELL+28))
        if self.caught:
            self._overlay("CAUGHT!", (220,60,60))
        if self.won:
            self._overlay("ESCAPED!", (80,220,80))
        pygame.display.flip()

    def _overlay(self, text, color):
        surf=pygame.Surface((WIDTH,ROWS*CELL),pygame.SRCALPHA)
        surf.fill((0,0,0,140))
        self.screen.blit(surf,(0,0))
        msg=self.big_font.render(text,True,color)
        sub=self.font.render("Press R to Restart",True,(200,200,200))
        self.screen.blit(msg,(WIDTH//2-msg.get_width()//2,ROWS*CELL//2-30))
        self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,ROWS*CELL//2+20))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()