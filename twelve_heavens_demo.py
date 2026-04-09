"""
TWELVE HEAVENS — Demo
=====================
Controls:
  Arrow Keys  — Move player
  E           — Interact (with NPC or temple)
  SPACE       — Use Tiger Wisdom attack (if acquired)
  ESC         — Quit

Requirements:  pip install pygame
Run:           python twelve_heavens_demo.py
"""

import pygame
import sys
import textwrap

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TILE        = 64          # pixels per grid tile
COLS        = 10
ROWS        = 10
HUD_HEIGHT  = 160
WIN_W       = TILE * COLS
WIN_H       = TILE * ROWS + HUD_HEIGHT
FPS         = 60

# Tile type IDs
GRASS       = 0
WALL        = 1
VILLAGE     = 2
TEMPLE      = 3
PATH        = 4

# Colours  (R, G, B)
C_BG            = (18,  16,  24)
C_GRASS         = (52,  78,  45)
C_GRASS2        = (44,  68,  38)
C_WALL          = (60,  52,  44)
C_WALL_TOP      = (80,  70,  58)
C_PATH          = (110, 95,  72)
C_VILLAGE       = (160, 120,  70)
C_VILLAGE_ROOF  = (200,  80,  50)
C_TEMPLE        = (80,   90, 140)
C_TEMPLE_ROOF   = (110, 130, 200)
C_PLAYER        = (220, 200,  80)
C_PLAYER_DARK   = (160, 140,  40)
C_NPC           = (80,  180, 120)
C_NPC_DARK      = (40,  120,  80)
C_ENEMY         = (200,  60,  60)
C_HUD_BG        = (12,  10,  18)
C_HUD_BORDER    = (60,  52,  80)
C_GOLD          = (210, 170,  60)
C_JADE          = (60,  180, 120)
C_WHITE         = (240, 235, 225)
C_MUTED         = (140, 130, 120)
C_TIGER         = (220, 100,  40)
C_TIGER_DARK    = (160,  60,  20)
C_DAMAGE        = (255,  60,  60)
C_HEAL          = (60,  220, 120)
C_DIALOG_BG     = (20,  16,  28)
C_DIALOG_BORDER = (100,  80, 160)
C_HP_GREEN      = (60,  200,  80)
C_HP_RED        = (200,  60,  60)

# ---------------------------------------------------------------------------
# Map layout  (0=grass, 1=wall, 2=village, 3=temple, 4=path)
# ---------------------------------------------------------------------------

MAP_DATA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 4, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 4, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 4, 4, 4, 4, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 4, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 3, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

WALKABLE = {GRASS, VILLAGE, PATH, TEMPLE}

# ---------------------------------------------------------------------------
# Floating text
# ---------------------------------------------------------------------------

class FloatingText:
    def __init__(self, text, x, y, colour, size=18, lifetime=90):
        self.text     = text
        self.x        = float(x)
        self.y        = float(y)
        self.colour   = colour
        self.size     = size
        self.lifetime = lifetime
        self.age      = 0

    def update(self):
        self.age += 1
        self.y   -= 0.7

    def alive(self):
        return self.age < self.lifetime

    def draw(self, surf, font):
        alpha = max(0, 255 - int(255 * self.age / self.lifetime))
        s = font.render(self.text, True, self.colour)
        s.set_alpha(alpha)
        surf.blit(s, (int(self.x) - s.get_width() // 2, int(self.y)))

# ---------------------------------------------------------------------------
# Enemy
# ---------------------------------------------------------------------------

class Enemy:
    def __init__(self, gx, gy):
        self.gx     = gx
        self.gy     = gy
        self.hp     = 3
        self.max_hp = 3
        self.alive  = True
        self._shake = 0

    def take_damage(self, dmg):
        self.hp    -= dmg
        self._shake = 10
        if self.hp <= 0:
            self.alive = False

    def update(self):
        if self._shake > 0:
            self._shake -= 1

    def draw(self, surf):
        ox = 4 if self._shake % 4 < 2 else -4
        px = self.gx * TILE + TILE // 2 + ox
        py = self.gy * TILE + TILE // 2

        # Body
        pygame.draw.circle(surf, C_ENEMY, (px, py), 18)
        pygame.draw.circle(surf, (140, 30, 30), (px, py), 18, 2)

        # Eyes
        pygame.draw.circle(surf, C_WHITE, (px - 6, py - 5), 4)
        pygame.draw.circle(surf, C_WHITE, (px + 6, py - 5), 4)
        pygame.draw.circle(surf, (20, 20, 20), (px - 6, py - 5), 2)
        pygame.draw.circle(surf, (20, 20, 20), (px + 6, py - 5), 2)

        # HP bar
        bar_w = 36
        bar_x = px - bar_w // 2
        bar_y = py - 28
        pygame.draw.rect(surf, (60, 20, 20), (bar_x, bar_y, bar_w, 5))
        fill = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(surf, C_HP_RED, (bar_x, bar_y, fill, 5))

# ---------------------------------------------------------------------------
# NPC
# ---------------------------------------------------------------------------

class NPC:
    QUEST_STAGES = [
        # (speaker, lines)
        ("Village Elder",
         ["Wanderer, dark spirits stir near the Tiger Temple to the east.",
          "Defeat the corrupted beast that guards the path.",
          "Return to me and I shall share the Temple's wisdom with you."]),
        ("Village Elder",
         ["You've done it! The path is clear.",
          "Take this — the essence of Tiger Wisdom.",
          "With it, your attacks will strike twice as hard. Use it wisely."]),
        ("Village Elder",
         ["The village is safe, thanks to you.",
          "May your two wisdoms serve you well on the road ahead."]),
    ]

    def __init__(self, gx, gy):
        self.gx          = gx
        self.gy          = gy
        self.quest_stage = 0   # 0=not started, 1=in progress, 2=complete, 3=done
        self._bob        = 0.0

    def advance_quest(self):
        self.quest_stage = min(self.quest_stage + 1, 2)

    def current_dialog(self):
        s = min(self.quest_stage, len(self.QUEST_STAGES) - 1)
        return self.QUEST_STAGES[s]

    def update(self):
        self._bob += 0.08

    def draw(self, surf):
        bob = int(3 * __import__('math').sin(self._bob))
        px  = self.gx * TILE + TILE // 2
        py  = self.gy * TILE + TILE // 2 + bob

        # Robe
        points = [(px, py - 20), (px - 12, py + 18), (px + 12, py + 18)]
        pygame.draw.polygon(surf, C_NPC_DARK, points)
        pygame.draw.polygon(surf, C_NPC, points, 2)

        # Head
        pygame.draw.circle(surf, C_NPC, (px, py - 26), 10)
        pygame.draw.circle(surf, C_NPC_DARK, (px, py - 26), 10, 2)

        # Hat
        pygame.draw.polygon(surf, C_GOLD,
                            [(px, py - 42), (px - 9, py - 36), (px + 9, py - 36)])
        pygame.draw.rect(surf, C_GOLD, (px - 10, py - 37, 20, 5))

        # Quest indicator
        if self.quest_stage < 2:
            pygame.draw.circle(surf, C_GOLD, (px, py - 52), 7)
            pygame.draw.circle(surf, C_GOLD, (px, py - 52), 7, 2)

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    def __init__(self, gx, gy):
        self.gx           = gx
        self.gy           = gy
        self.px           = float(gx * TILE)   # pixel x (smooth)
        self.py           = float(gy * TILE)   # pixel y (smooth)
        self.hp           = 10
        self.max_hp       = 10
        self.attack       = 1
        self.has_tiger    = False
        self.facing       = (1, 0)
        self._move_cd     = 0
        self._attack_cd   = 0
        self._shake       = 0
        self._bob         = 0.0
        self.tiger_active = False   # visual flash when activating
        self._tiger_flash = 0

    def take_damage(self, dmg):
        self.hp    -= dmg
        self._shake = 12

    def grant_tiger(self):
        self.has_tiger  = True
        self.attack     = 2
        self._tiger_flash = 40

    def update(self):
        # Smooth pixel follow
        tx = float(self.gx * TILE)
        ty = float(self.gy * TILE)
        self.px += (tx - self.px) * 0.25
        self.py += (ty - self.py) * 0.25

        if self._move_cd   > 0: self._move_cd   -= 1
        if self._attack_cd > 0: self._attack_cd -= 1
        if self._shake     > 0: self._shake     -= 1
        if self._tiger_flash > 0: self._tiger_flash -= 1
        self._bob += 0.07

    def draw(self, surf):
        import math
        ox = 4 if self._shake % 4 < 2 and self._shake > 0 else 0
        px = int(self.px) + TILE // 2 + ox
        py = int(self.py) + TILE // 2

        bob = int(2 * math.sin(self._bob))

        # Tiger aura
        if self.has_tiger:
            aura_alpha = 60 + int(40 * math.sin(self._bob * 1.5))
            aura_surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*C_TIGER, aura_alpha),
                               (TILE // 2, TILE // 2), 26)
            surf.blit(aura_surf, (int(self.px) + ox, int(self.py)))

        # Tiger flash burst
        if self._tiger_flash > 0:
            r = int(30 + 20 * (self._tiger_flash / 40))
            alpha = int(200 * self._tiger_flash / 40)
            flash_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (*C_TIGER, alpha), (r, r), r)
            surf.blit(flash_surf, (px - r, py - r))

        # Cloak / body
        cloak_col = C_TIGER_DARK if self.has_tiger else C_PLAYER_DARK
        body_col  = C_TIGER      if self.has_tiger else C_PLAYER
        points = [(px, py - 22 + bob),
                  (px - 13, py + 18 + bob),
                  (px + 13, py + 18 + bob)]
        pygame.draw.polygon(surf, cloak_col, points)
        pygame.draw.polygon(surf, body_col, points, 2)

        # Head
        pygame.draw.circle(surf, body_col, (px, py - 28 + bob), 11)
        pygame.draw.circle(surf, cloak_col, (px, py - 28 + bob), 11, 2)

        # Conical hat
        pygame.draw.polygon(surf, cloak_col,
                            [(px, py - 44 + bob),
                             (px - 12, py - 33 + bob),
                             (px + 12, py - 33 + bob)])
        pygame.draw.rect(surf, cloak_col,
                         (px - 13, py - 34 + bob, 26, 5))

# ---------------------------------------------------------------------------
# Map renderer
# ---------------------------------------------------------------------------

def draw_tile(surf, tile_type, col, row):
    x = col * TILE
    y = row * TILE
    r = pygame.Rect(x, y, TILE, TILE)

    if tile_type == GRASS:
        shade = C_GRASS if (col + row) % 2 == 0 else C_GRASS2
        surf.fill(shade, r)
        # Subtle grass tufts
        for dx, dy in [(12, 20), (38, 42), (52, 14), (24, 50)]:
            pygame.draw.line(surf, (40, 60, 32),
                             (x + dx, y + dy), (x + dx - 2, y + dy - 5), 1)
            pygame.draw.line(surf, (40, 60, 32),
                             (x + dx, y + dy), (x + dx + 2, y + dy - 5), 1)

    elif tile_type == WALL:
        surf.fill(C_WALL, r)
        # Stone brick lines
        pygame.draw.rect(surf, C_WALL_TOP, (x, y, TILE, 8))
        for bx in range(x, x + TILE, 20):
            pygame.draw.line(surf, C_WALL_TOP, (bx, y + 8), (bx, y + TILE), 1)
        for by in range(y + 8, y + TILE, 18):
            pygame.draw.line(surf, C_WALL_TOP, (x, by), (x + TILE, by), 1)

    elif tile_type == PATH:
        surf.fill(C_PATH, r)
        # Cobblestone dots
        for dx, dy in [(10, 10), (38, 20), (20, 44), (50, 50), (54, 12)]:
            pygame.draw.circle(surf, (90, 76, 55), (x + dx, y + dy), 4)

    elif tile_type == VILLAGE:
        surf.fill(C_GRASS, r)
        # House body
        pygame.draw.rect(surf, C_VILLAGE, (x + 10, y + 22, 44, 34))
        # Roof
        pygame.draw.polygon(surf, C_VILLAGE_ROOF,
                            [(x + 6, y + 24), (x + 32, y + 6), (x + 58, y + 24)])
        # Door
        pygame.draw.rect(surf, C_WALL, (x + 24, y + 38, 16, 18))
        # Window
        pygame.draw.rect(surf, (200, 220, 255), (x + 13, y + 28, 10, 10))

    elif tile_type == TEMPLE:
        surf.fill(C_GRASS, r)
        # Base
        pygame.draw.rect(surf, C_TEMPLE, (x + 8, y + 28, 48, 28))
        # Curved roof (approximated with polygon)
        pygame.draw.polygon(surf, C_TEMPLE_ROOF,
                            [(x + 4,  y + 30),
                             (x + 16, y + 10),
                             (x + 32, y + 4),
                             (x + 48, y + 10),
                             (x + 60, y + 30)])
        # Roof ridge
        pygame.draw.line(surf, C_WHITE, (x + 16, y + 10), (x + 48, y + 10), 2)
        # Pillars
        for px2 in (x + 12, x + 44):
            pygame.draw.rect(surf, C_WHITE, (px2, y + 28, 6, 28))
        # Door arch
        cx2 = x + 29
        pygame.draw.rect(surf, C_WALL, (cx2 - 7, y + 40, 14, 16))
        pygame.draw.circle(surf, C_WALL, (cx2, y + 40), 7)

# ---------------------------------------------------------------------------
# Dialog box renderer
# ---------------------------------------------------------------------------

def draw_dialog(surf, font_title, font_body, speaker, lines, page, total_pages):
    box_w = WIN_W - 40
    box_h = 130
    box_x = 20
    box_y = TILE * ROWS + 15

    pygame.draw.rect(surf, C_DIALOG_BG,    (box_x, box_y, box_w, box_h),
                     border_radius=8)
    pygame.draw.rect(surf, C_DIALOG_BORDER, (box_x, box_y, box_w, box_h),
                     2, border_radius=8)

    # Speaker name
    name_surf = font_title.render(speaker, True, C_GOLD)
    surf.blit(name_surf, (box_x + 14, box_y + 10))

    # Body text (word-wrapped)
    full_text = " ".join(lines)
    wrapped   = textwrap.wrap(full_text, width=68)
    for i, line in enumerate(wrapped[:3]):
        ts = font_body.render(line, True, C_WHITE)
        surf.blit(ts, (box_x + 14, box_y + 34 + i * 22))

    # Prompt
    prompt = f"[E] Continue  ({page}/{total_pages})" if page < total_pages else "[E] Close"
    ps = font_body.render(prompt, True, C_MUTED)
    surf.blit(ps, (box_x + 14, box_y + box_h - 22))

# ---------------------------------------------------------------------------
# HUD renderer
# ---------------------------------------------------------------------------

def draw_hud(surf, font_title, font_body, player, message, msg_timer):
    hud_y = TILE * ROWS
    pygame.draw.rect(surf, C_HUD_BG, (0, hud_y, WIN_W, HUD_HEIGHT))
    pygame.draw.line(surf, C_HUD_BORDER, (0, hud_y), (WIN_W, hud_y), 1)

    # HP bar
    bar_w = 160
    label = font_body.render("HP", True, C_MUTED)
    surf.blit(label, (16, hud_y + 14))
    pygame.draw.rect(surf, (40, 20, 20), (50, hud_y + 14, bar_w, 14), border_radius=4)
    fill = int(bar_w * max(0, player.hp) / player.max_hp)
    col = C_HP_GREEN if player.hp > 4 else C_HP_RED
    pygame.draw.rect(surf, col, (50, hud_y + 14, fill, 14), border_radius=4)
    hp_txt = font_body.render(f"{max(0,player.hp)}/{player.max_hp}", True, C_WHITE)
    surf.blit(hp_txt, (220, hud_y + 14))

    # Attack stat
    atk_txt = font_body.render(f"ATK  {player.attack}", True, C_WHITE)
    surf.blit(atk_txt, (16, hud_y + 38))

    # Wisdom slot
    wis_label = font_body.render("WISDOM", True, C_MUTED)
    surf.blit(wis_label, (16, hud_y + 62))

    slot_rect = pygame.Rect(80, hud_y + 58, 120, 24)
    if player.has_tiger:
        pygame.draw.rect(surf, C_TIGER_DARK, slot_rect, border_radius=4)
        pygame.draw.rect(surf, C_TIGER,      slot_rect, 1, border_radius=4)
        wis_txt = font_body.render("Tiger  [SPACE]", True, C_TIGER)
    else:
        pygame.draw.rect(surf, (30, 26, 36), slot_rect, border_radius=4)
        pygame.draw.rect(surf, C_HUD_BORDER, slot_rect, 1, border_radius=4)
        wis_txt = font_body.render("— empty —", True, C_MUTED)
    surf.blit(wis_txt, (slot_rect.x + 6, slot_rect.y + 4))

    # Controls hint
    hints = font_body.render("Arrows: Move    E: Interact    SPACE: Tiger Wisdom", True, C_MUTED)
    surf.blit(hints, (16, hud_y + 94))

    # Flash message
    if msg_timer > 0:
        alpha = min(255, msg_timer * 8)
        ms = font_title.render(message, True, C_JADE)
        ms.set_alpha(alpha)
        surf.blit(ms, (WIN_W // 2 - ms.get_width() // 2, hud_y + 120))

# ---------------------------------------------------------------------------
# Game state machine
# ---------------------------------------------------------------------------

STATE_EXPLORE = "explore"
STATE_DIALOG  = "dialog"
STATE_DEAD    = "dead"
STATE_WIN     = "win"

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Twelve Heavens — Demo")
        self.screen    = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock     = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Georgia",        16, bold=True)
        self.font_body  = pygame.font.SysFont("Georgia",        14)
        self.font_big   = pygame.font.SysFont("Georgia",        32, bold=True)
        self.font_small = pygame.font.SysFont("Arial",          13)

        self.map        = MAP_DATA
        self.player     = Player(1, 1)
        self.npc        = NPC(2, 2)
        self.enemies    = [Enemy(5, 5), Enemy(6, 7)]
        self.floats     = []      # FloatingText list

        self.state      = STATE_EXPLORE
        self.dialog_data = None   # (speaker, lines, page_index, total_pages_fn)
        self.dialog_page = 0

        self.message       = ""
        self.message_timer = 0

        self.enemy_killed  = 0    # track kills for quest
        self.quest_complete= False

    # -----------------------------------------------------------------------
    def flash(self, msg, duration=120):
        self.message       = msg
        self.message_timer = duration

    def spawn_float(self, text, gx, gy, colour=C_DAMAGE):
        self.floats.append(FloatingText(
            text,
            gx * TILE + TILE // 2,
            gy * TILE,
            colour
        ))

    # -----------------------------------------------------------------------
    def tile_at(self, gx, gy):
        if 0 <= gy < ROWS and 0 <= gx < COLS:
            return self.map[gy][gx]
        return WALL

    def can_walk(self, gx, gy):
        if self.tile_at(gx, gy) not in WALKABLE:
            return False
        for e in self.enemies:
            if e.alive and e.gx == gx and e.gy == gy:
                return False
        if self.npc.gx == gx and self.npc.gy == gy:
            return False
        return True

    # -----------------------------------------------------------------------
    def try_move(self, dx, dy):
        if self.player._move_cd > 0:
            return
        nx = self.player.gx + dx
        ny = self.player.gy + dy
        self.player.facing = (dx, dy)

        if self.can_walk(nx, ny):
            self.player.gx = nx
            self.player.gy = ny
            self.player._move_cd = 8
        else:
            # Bump-attack adjacent enemies
            for e in self.enemies:
                if e.alive and e.gx == nx and e.gy == ny:
                    dmg = self.player.attack
                    e.take_damage(dmg)
                    self.spawn_float(f"-{dmg}", nx, ny, C_DAMAGE)
                    self.player._attack_cd = 20
                    if not e.alive:
                        self.enemy_killed += 1
                        self.spawn_float("Defeated!", nx, ny, C_JADE)
                        self.check_quest_progress()
                    break

    # -----------------------------------------------------------------------
    def tiger_attack(self):
        if not self.player.has_tiger:
            return
        if self.player._attack_cd > 0:
            return

        fx, fy = self.player.facing
        tx = self.player.gx + fx
        ty = self.player.gy + fy
        self.player._tiger_flash = 20

        hit = False
        for e in self.enemies:
            if e.alive and e.gx == tx and e.gy == ty:
                dmg = self.player.attack * 2
                e.take_damage(dmg)
                self.spawn_float(f"TIGER -{dmg}!", tx, ty, C_TIGER)
                self.player._attack_cd = 25
                hit = True
                if not e.alive:
                    self.enemy_killed += 1
                    self.spawn_float("Defeated!", tx, ty, C_JADE)
                    self.check_quest_progress()
                break

        if not hit:
            self.spawn_float("No target!", self.player.gx, self.player.gy, C_MUTED)

    # -----------------------------------------------------------------------
    def check_quest_progress(self):
        if self.npc.quest_stage == 1 and self.enemy_killed >= len(self.enemies):
            self.quest_complete = True
            self.flash("Quest complete! Return to the Elder.")

    # -----------------------------------------------------------------------
    def try_interact(self):
        px, py = self.player.gx, self.player.gy

        # Adjacent NPC?
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
            if self.npc.gx == px + dx and self.npc.gy == py + dy:
                self.open_npc_dialog()
                return

        # On temple?
        if self.tile_at(px, py) == TEMPLE:
            if self.player.has_tiger:
                self.flash("You already hold the Tiger Wisdom.")
            else:
                self.flash("A temple… but first, heed the village elder's quest.")
            return

    # -----------------------------------------------------------------------
    def open_npc_dialog(self):
        # Advance quest stage if applicable
        if self.npc.quest_stage == 0:
            self.npc.advance_quest()   # 0 → 1  (quest given)
        elif self.npc.quest_stage == 1 and self.quest_complete:
            self.npc.advance_quest()   # 1 → 2  (quest complete: give wisdom)
            self.player.grant_tiger()
            self.flash("Tiger Wisdom acquired!  ATK doubled.")

        speaker, lines = self.npc.current_dialog()
        self.dialog_data  = (speaker, lines)
        self.dialog_page  = 0
        self.state        = STATE_DIALOG

    # -----------------------------------------------------------------------
    def advance_dialog(self):
        if self.dialog_data is None:
            self.state = STATE_EXPLORE
            return
        speaker, lines = self.dialog_data
        total = len(lines)
        if self.dialog_page < total - 1:
            self.dialog_page += 1
        else:
            self.state       = STATE_EXPLORE
            self.dialog_data = None

    # -----------------------------------------------------------------------
    def update(self):
        self.player.update()
        self.npc.update()
        for e in self.enemies:
            e.update()
        self.floats = [f for f in self.floats if f.alive()]
        for f in self.floats:
            f.update()
        if self.message_timer > 0:
            self.message_timer -= 1

        if self.player.hp <= 0:
            self.state = STATE_DEAD

    # -----------------------------------------------------------------------
    def draw_map(self):
        for row in range(ROWS):
            for col in range(COLS):
                draw_tile(self.screen, self.map[row][col], col, row)

    # -----------------------------------------------------------------------
    def draw_world(self):
        self.draw_map()
        self.npc.draw(self.screen)
        for e in self.enemies:
            if e.alive:
                e.draw(self.screen)
        self.player.draw(self.screen)
        for f in self.floats:
            f.draw(self.screen, self.font_small)

    # -----------------------------------------------------------------------
    def draw_overlay(self):
        if self.state == STATE_DIALOG and self.dialog_data:
            speaker, lines = self.dialog_data
            page_lines = [lines[self.dialog_page]]
            draw_dialog(self.screen, self.font_title, self.font_body,
                        speaker, page_lines,
                        self.dialog_page + 1, len(lines))

        elif self.state == STATE_DEAD:
            s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 160))
            self.screen.blit(s, (0, 0))
            t1 = self.font_big.render("You have fallen.", True, C_DAMAGE)
            t2 = self.font_body.render("Press R to restart", True, C_MUTED)
            self.screen.blit(t1, (WIN_W//2 - t1.get_width()//2, WIN_H//2 - 30))
            self.screen.blit(t2, (WIN_W//2 - t2.get_width()//2, WIN_H//2 + 20))

        elif self.state == STATE_WIN:
            s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 160))
            self.screen.blit(s, (0, 0))
            t1 = self.font_big.render("Tiger Wisdom mastered.", True, C_TIGER)
            t2 = self.font_body.render("The road to the Twelve Heavens begins here.", True, C_WHITE)
            t3 = self.font_body.render("Press R to play again", True, C_MUTED)
            self.screen.blit(t1, (WIN_W//2 - t1.get_width()//2, WIN_H//2 - 50))
            self.screen.blit(t2, (WIN_W//2 - t2.get_width()//2, WIN_H//2))
            self.screen.blit(t3, (WIN_W//2 - t3.get_width()//2, WIN_H//2 + 40))

    # -----------------------------------------------------------------------
    def reset(self):
        self.__init__()

    # -----------------------------------------------------------------------
    def run(self):
        while True:
            dt = self.clock.tick(FPS)

            # --- Events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_r:
                        self.reset()
                        continue

                    if self.state == STATE_DIALOG:
                        if event.key == pygame.K_e:
                            self.advance_dialog()

                    elif self.state == STATE_EXPLORE:
                        if event.key == pygame.K_UP:
                            self.try_move(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.try_move(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.try_move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.try_move(1, 0)
                        elif event.key == pygame.K_e:
                            self.try_interact()
                        elif event.key == pygame.K_SPACE:
                            self.tiger_attack()

            # Held keys for smooth movement (secondary)
            if self.state == STATE_EXPLORE and self.player._move_cd == 0:
                keys = pygame.key.get_pressed()
                if   keys[pygame.K_UP]:    self.try_move(0, -1)
                elif keys[pygame.K_DOWN]:  self.try_move(0, 1)
                elif keys[pygame.K_LEFT]:  self.try_move(-1, 0)
                elif keys[pygame.K_RIGHT]: self.try_move(1, 0)

            # --- Update ---
            self.update()

            # Check win condition
            if (self.state == STATE_EXPLORE
                    and self.player.has_tiger
                    and self.npc.quest_stage >= 2
                    and self.enemy_killed >= len(self.enemies)):
                # Only trigger win if player revisits temple
                if self.tile_at(self.player.gx, self.player.gy) == TEMPLE:
                    self.state = STATE_WIN

            # --- Draw ---
            self.screen.fill(C_BG)
            self.draw_world()
            draw_hud(self.screen, self.font_title, self.font_body,
                     self.player, self.message, self.message_timer)
            self.draw_overlay()
            pygame.display.flip()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    Game().run()
