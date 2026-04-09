"""
TWELVE HEAVENS — Demo v2
========================
Controls:
  Arrow Keys  — Move / bump-attack
  E           — Interact (NPC, items, temple)
  SPACE       — Tiger Wisdom strike (after acquiring)
  H           — Use Healing Herb (if in inventory)
  ESC         — Quit   |   R — Restart

Requirements:  pip install pygame
Run:           python twelve_heavens_demo.py
"""

import pygame, sys, textwrap, math, random

# ── Constants ────────────────────────────────────────────────────────────────
TILE  = 64
COLS  = 10
ROWS  = 10
HUD_H = 170
WIN_W = TILE * COLS
WIN_H = TILE * ROWS + HUD_H
FPS   = 60

GRASS=0; WALL=1; VILLAGE=2; TEMPLE=3; PATH=4; WATER=5; TREE=6
WALKABLE = {GRASS, VILLAGE, PATH, TEMPLE}

# ── Palette ──────────────────────────────────────────────────────────────────
C = dict(
    bg=(14,12,20), grass=(46,72,38), grass2=(38,62,30), grass_hi=(60,88,48),
    wall=(55,48,40), wall_top=(75,66,54), wall_shadow=(35,30,25),
    path=(105,90,68), path2=(118,102,78),
    water=(30,80,130), water2=(40,95,150), water_foam=(80,160,200),
    tree_trunk=(70,50,30), tree_top=(30,90,40), tree_top2=(45,110,50),
    village=(155,115,65), village_hi=(175,135,85),
    v_roof=(190,70,45), v_roof2=(210,90,60),
    temple=(70,85,135), temple_hi=(90,110,165),
    t_roof=(100,125,195), t_roof2=(120,148,220), t_glow=(140,170,255),
    player=(215,195,75), player_dk=(155,135,38),
    tiger=(215,95,35), tiger_dk=(150,55,18),
    npc=(75,175,115), npc_dk=(38,115,72),
    enemy=(195,55,55), enemy2=(230,80,80), enemy_dk=(120,25,25),
    boss=(160,40,160), boss2=(200,70,200),
    gold=(210,168,58), gold2=(240,200,90),
    jade=(55,175,115), white=(238,232,220), muted=(135,125,115),
    hud_bg=(10,8,16), hud_border=(55,48,75),
    dialog_bg=(18,14,26), dialog_bd=(95,75,155),
    hp_green=(55,195,75), hp_red=(195,55,55), hp_yellow=(210,180,40),
    dmg=(255,55,55), heal_col=(55,215,115),
    item_herb=(80,200,80), item_scroll=(220,190,80), item_bone=(210,200,180),
    xp_col=(180,140,240),
)

# ── Map ───────────────────────────────────────────────────────────────────────
MAP_DATA = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,4,0,0,6,0,0,1],
    [1,0,2,4,0,0,0,0,0,1],
    [1,0,0,4,4,4,4,5,5,1],
    [1,6,0,0,0,0,4,5,5,1],
    [1,0,0,0,0,0,4,0,0,1],
    [1,0,0,0,6,0,4,4,0,1],
    [1,0,0,0,0,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
]

# ── Particles ────────────────────────────────────────────────────────────────
class Particle:
    __slots__ = ('x','y','vx','vy','life','max_life','r','col','gravity')
    def __init__(self,x,y,col,vx=0,vy=0,r=3,life=40,gravity=0.0):
        self.x=float(x); self.y=float(y)
        self.vx=vx+random.uniform(-0.8,0.8)
        self.vy=vy+random.uniform(-0.8,0.8)
        self.r=r; self.col=col; self.life=life
        self.max_life=life; self.gravity=gravity
    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy+=self.gravity; self.life-=1
        self.vx*=0.91; self.vy*=0.91
    def alive(self): return self.life>0
    def draw(self,surf):
        a=int(255*self.life/self.max_life)
        r=max(1,int(self.r*self.life/self.max_life))
        s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        pygame.draw.circle(s,(*self.col,a),(r,r),r)
        surf.blit(s,(int(self.x)-r,int(self.y)-r))

def burst(particles,x,y,col,n=10,speed=3,r=4,life=35,gravity=0.05):
    for _ in range(n):
        a=random.uniform(0,math.tau)
        sp=random.uniform(0.5,speed)
        particles.append(Particle(x,y,col,math.cos(a)*sp,math.sin(a)*sp,r,life,gravity))

# ── Floating text ─────────────────────────────────────────────────────────────
class FloatText:
    def __init__(self,text,x,y,col,life=80):
        self.text=text; self.x=float(x); self.y=float(y)
        self.col=col; self.life=life; self.max_life=life
    def update(self): self.y-=0.65; self.life-=1
    def alive(self): return self.life>0
    def draw(self,surf,font):
        a=max(0,int(255*self.life/self.max_life))
        s=font.render(self.text,True,self.col); s.set_alpha(a)
        surf.blit(s,(int(self.x)-s.get_width()//2,int(self.y)))

# ── Item kinds ────────────────────────────────────────────────────────────────
ITEM_HERB="herb"; ITEM_SCROLL="scroll"; ITEM_BONE="bone"
ITEM_META={
    ITEM_HERB:  dict(label="Healing Herb",   col_key="item_herb",   short="Herb"),
    ITEM_SCROLL:dict(label="Ancient Scroll", col_key="item_scroll", short="Scroll"),
    ITEM_BONE:  dict(label="Spirit Bone",    col_key="item_bone",   short="Bone"),
}

class Item:
    def __init__(self,gx,gy,kind):
        self.gx=gx; self.gy=gy; self.kind=kind; self.collected=False
        self._bob=random.uniform(0,math.tau)
        self._pulse=random.uniform(0,math.tau)
    def update(self): self._bob+=0.07; self._pulse+=0.05
    def draw(self,surf):
        if self.collected: return
        col=C[ITEM_META[self.kind]["col_key"]]
        px=self.gx*TILE+TILE//2
        py=self.gy*TILE+TILE//2+int(3*math.sin(self._bob))
        # glow
        gr=15+int(3*math.sin(self._pulse))
        gs=pygame.Surface((gr*2,gr*2),pygame.SRCALPHA)
        pygame.draw.circle(gs,(*col,55),(gr,gr),gr)
        surf.blit(gs,(px-gr,py-gr))
        # shadow
        pygame.draw.ellipse(surf,(0,0,0),(px-10,py+9,20,5))
        if self.kind==ITEM_HERB:
            pygame.draw.circle(surf,col,(px,py),9)
            pygame.draw.circle(surf,(30,100,30),(px,py),9,1)
            pygame.draw.line(surf,(40,140,40),(px,py+2),(px,py-10),2)
            pygame.draw.line(surf,(40,140,40),(px,py-4),(px-6,py-10),1)
        elif self.kind==ITEM_SCROLL:
            pygame.draw.rect(surf,col,(px-8,py-7,16,14),border_radius=3)
            pygame.draw.circle(surf,C["gold2"],(px-8,py),5)
            pygame.draw.circle(surf,C["gold2"],(px+8,py),5)
            for ly in range(py-3,py+5,3):
                pygame.draw.line(surf,(180,150,50),(px-5,ly),(px+5,ly),1)
        elif self.kind==ITEM_BONE:
            pygame.draw.line(surf,col,(px-7,py-7),(px+7,py+7),3)
            pygame.draw.line(surf,col,(px+7,py-7),(px-7,py+7),3)
            for cx2,cy2 in [(px-7,py-7),(px+7,py-7),(px-7,py+7),(px+7,py+7)]:
                pygame.draw.circle(surf,col,(cx2,cy2),4)

# ── Enemy ─────────────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self,gx,gy,hp=4,atk=1,boss=False):
        self.gx=gx; self.gy=gy; self.hp=hp; self.max_hp=hp
        self.atk=atk; self.boss=boss; self.alive=True
        self._shake=0; self._bob=random.uniform(0,math.tau)
        self._move_cd=0; self._atk_flash=0
        self.intent="attack"
        self._intent_cd=random.randint(30,90)

    def take_damage(self,dmg):
        self.hp-=dmg; self._shake=10; self._atk_flash=8
        if self.hp<=0: self.alive=False

    def update(self,pgx,pgy,can_walk_fn):
        self._bob+=0.06
        if self._shake>0: self._shake-=1
        if self._atk_flash>0: self._atk_flash-=1
        if self._move_cd>0: self._move_cd-=1; return
        self._intent_cd-=1
        if self._intent_cd<=0:
            self.intent=random.choice(["attack","attack","wait"])
            self._intent_cd=random.randint(40,100)
        if self.intent=="wait": return
        dx=pgx-self.gx; dy=pgy-self.gy
        steps=[]
        if dx!=0: steps.append((dx//abs(dx),0))
        if dy!=0: steps.append((0,dy//abs(dy)))
        random.shuffle(steps)
        for sx,sy in steps:
            nx,ny=self.gx+sx,self.gy+sy
            if abs(nx-pgx)+abs(ny-pgy)>1 and can_walk_fn(nx,ny):
                self.gx=nx; self.gy=ny
                self._move_cd=50 if not self.boss else 38
                break

    def draw(self,surf):
        ox=(4 if self._shake%4<2 else -4) if self._shake>0 else 0
        bob=int(2*math.sin(self._bob))
        px=self.gx*TILE+TILE//2+ox; py=self.gy*TILE+TILE//2+bob
        col=C["boss"] if self.boss else C["enemy"]
        col2=C["boss2"] if self.boss else C["enemy2"]
        sz=22 if self.boss else 17
        # shadow
        pygame.draw.ellipse(surf,(0,0,0),(px-sz,py+sz-4,sz*2,8))
        # flash white on hit
        if self._atk_flash>0: pygame.draw.circle(surf,C["white"],(px,py),sz+4)
        pygame.draw.circle(surf,col,(px,py),sz)
        pygame.draw.circle(surf,col2,(px,py),sz,2)
        if self.boss:
            pygame.draw.polygon(surf,C["enemy_dk"],[(px-10,py-sz),(px-17,py-sz-15),(px-4,py-sz-2)])
            pygame.draw.polygon(surf,C["enemy_dk"],[(px+10,py-sz),(px+17,py-sz-15),(px+4,py-sz-2)])
        ew=5 if self.boss else 4
        for ex2,sign in [(px-ew-1,-1),(px+ew+1,1)]:
            pygame.draw.circle(surf,C["white"],(ex2,py-5),ew)
            pygame.draw.circle(surf,(15,15,15),(ex2,py-5),ew-2)
            pygame.draw.circle(surf,C["dmg"],(ex2,py-5),2)
        # intent icon
        iy=py-sz-18
        if self.intent=="attack":
            pygame.draw.line(surf,C["dmg"],(px-4,iy-6),(px+4,iy+6),2)
            pygame.draw.line(surf,C["dmg"],(px-4,iy+2),(px-1,iy-1),2)
        else:
            for lx,ly in [((px-4,iy-5),(px+4,iy-5)),((px+4,iy-5),(px-4,iy+5)),
                          ((px-4,iy+5),(px+4,iy+5))]:
                pygame.draw.line(surf,C["water_foam"],lx,ly,2)
        # HP bar
        bw=int(sz*2.2); bx2=px-bw//2; by2=py-sz-10
        pygame.draw.rect(surf,(40,15,15),(bx2,by2,bw,5))
        fill=max(0,int(bw*self.hp/self.max_hp))
        ratio=self.hp/self.max_hp
        hcol=C["hp_green"] if ratio>0.5 else C["hp_yellow"] if ratio>0.25 else C["hp_red"]
        pygame.draw.rect(surf,hcol,(bx2,by2,fill,5))

# ── NPC ───────────────────────────────────────────────────────────────────────
class NPC:
    DIALOGS=[
        ("Village Elder",[
            "Wanderer — dark spirits stir near the Tiger Temple to the east.",
            "Find the Ancient Scroll hidden somewhere on the map.",
            "Slay the two beasts, then collect a Spirit Bone as proof.",
            "Return when you hold both. I will share the Temple's wisdom."
        ]),
        ("Village Elder",[
            "The beasts still roam. Find the Scroll and bring a Spirit Bone.",
            "Glowing items on the ground can be picked up with E.",
            "Use H to eat a Healing Herb if you're hurt."
        ]),
        ("Village Elder",[
            "You found the Scroll and the Bone — the spirits are at rest!",
            "Take this: the essence of Tiger Wisdom. Your attack triples.",
            "The temple to the east now awaits. Go with courage."
        ]),
        ("Village Elder",[
            "The village is safe. May your wisdoms guide you to the Twelve Heavens.",
        ]),
    ]
    def __init__(self,gx,gy):
        self.gx=gx; self.gy=gy; self.stage=0; self._bob=0.0
    def dialog(self): return self.DIALOGS[min(self.stage,3)]
    def update(self): self._bob+=0.07
    def draw(self,surf):
        bob=int(3*math.sin(self._bob))
        px=self.gx*TILE+TILE//2; py=self.gy*TILE+TILE//2+bob
        pygame.draw.ellipse(surf,(0,0,0),(px-14,py+16,28,8))
        pts=[(px,py-22),(px-13,py+18),(px+13,py+18)]
        pygame.draw.polygon(surf,C["npc_dk"],pts)
        pygame.draw.polygon(surf,C["npc"],pts,2)
        pygame.draw.rect(surf,C["gold"],(px-8,py+4,16,4))
        pygame.draw.circle(surf,C["npc"],(px,py-28),11)
        pygame.draw.circle(surf,C["npc_dk"],(px,py-28),11,2)
        pygame.draw.polygon(surf,C["gold"],[(px,py-46),(px-10,py-37),(px+10,py-37)])
        pygame.draw.rect(surf,C["gold"],(px-11,py-38,22,5))
        if self.stage<3:
            bx,by=px+8,py-48
            pygame.draw.circle(surf,C["gold2"],(bx,by),8)
            pygame.draw.circle(surf,C["gold"],(bx,by),8,2)
            pygame.draw.circle(surf,C["gold2"],(bx,by+14),3)

# ── Player ────────────────────────────────────────────────────────────────────
class Player:
    def __init__(self,gx,gy):
        self.gx=gx; self.gy=gy
        self.px=float(gx*TILE); self.py=float(gy*TILE)
        self.hp=10; self.max_hp=10; self.atk=1
        self.has_tiger=False; self.facing=(1,0)
        self.inventory={}
        self._move_cd=0; self._atk_cd=0; self._shake=0
        self._bob=0.0; self._tiger_flash=0
    def add_item(self,kind): self.inventory[kind]=self.inventory.get(kind,0)+1
    def use_herb(self):
        if self.inventory.get(ITEM_HERB,0)>0:
            self.inventory[ITEM_HERB]-=1; heal=3
            self.hp=min(self.max_hp,self.hp+heal); return heal
        return 0
    def take_damage(self,dmg): self.hp-=dmg; self._shake=14
    def grant_tiger(self): self.has_tiger=True; self.atk=3; self._tiger_flash=55
    def update(self):
        tx=float(self.gx*TILE); ty=float(self.gy*TILE)
        self.px+=(tx-self.px)*0.22; self.py+=(ty-self.py)*0.22
        for attr in ('_move_cd','_atk_cd','_shake','_tiger_flash'):
            v=getattr(self,attr)
            if v>0: setattr(self,attr,v-1)
        self._bob+=0.07
    def draw(self,surf):
        ox=(5 if self._shake%4<2 else -5) if self._shake>0 else 0
        bob=int(2*math.sin(self._bob))
        px=int(self.px)+TILE//2+ox; py=int(self.py)+TILE//2
        if self.has_tiger:
            aa=55+int(35*math.sin(self._bob*1.4)); asz=28
            aus=pygame.Surface((asz*2,asz*2),pygame.SRCALPHA)
            pygame.draw.circle(aus,(*C["tiger"],aa),(asz,asz),asz)
            surf.blit(aus,(px-asz,py-asz))
        if self._tiger_flash>0:
            r=int(28+22*(self._tiger_flash/55)); a=int(180*self._tiger_flash/55)
            fs=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(fs,(*C["tiger"],a),(r,r),r)
            surf.blit(fs,(px-r,py-r))
        pygame.draw.ellipse(surf,(0,0,0),(px-14+ox,py+17,28,8))
        ck=C["tiger_dk"] if self.has_tiger else C["player_dk"]
        bk=C["tiger"]    if self.has_tiger else C["player"]
        pts=[(px,py-23+bob),(px-14,py+19+bob),(px+14,py+19+bob)]
        pygame.draw.polygon(surf,ck,pts)
        pygame.draw.polygon(surf,bk,pts,2)
        pygame.draw.line(surf,bk,(px-8,py+bob),(px+8,py+bob),3)
        pygame.draw.circle(surf,bk,(px,py-29+bob),12)
        pygame.draw.circle(surf,ck,(px,py-29+bob),12,2)
        pygame.draw.polygon(surf,ck,[(px,py-47+bob),(px-13,py-35+bob),(px+13,py-35+bob)])
        pygame.draw.rect(surf,ck,(px-14,py-36+bob,28,5))
        ex=px+(self.facing[0]*4)
        pygame.draw.circle(surf,(20,20,20),(ex-3,py-28+bob),2)
        pygame.draw.circle(surf,(20,20,20),(ex+3,py-28+bob),2)

# ── Tile cache + renderer ─────────────────────────────────────────────────────
_tcache={}
def build_tile(t,col,row):
    key=(t,col,row)
    if key in _tcache: return _tcache[key]
    s=pygame.Surface((TILE,TILE)); x=y=0
    if t==GRASS:
        base=C["grass"] if (col+row)%2==0 else C["grass2"]; s.fill(base)
        for dx,dy in [(8,16),(30,38),(50,12),(18,50),(44,26),(6,44)]:
            pygame.draw.line(s,C["grass_hi"],(dx,dy),(dx-2,dy-6),1)
            pygame.draw.line(s,C["grass_hi"],(dx,dy),(dx+2,dy-6),1)
    elif t==WALL:
        s.fill(C["wall"])
        pygame.draw.rect(s,C["wall_top"],(0,0,TILE,9))
        for bx in range(0,TILE,22): pygame.draw.line(s,C["wall_shadow"],(bx,9),(bx,TILE),1)
        for by in range(9,TILE,16): pygame.draw.line(s,C["wall_top"],(0,by),(TILE,by),1)
        pygame.draw.rect(s,C["wall_shadow"],(0,TILE-2,TILE,2))
    elif t==PATH:
        shade=C["path"] if (col+row)%2==0 else C["path2"]; s.fill(shade)
        for dx,dy in [(10,10),(36,18),(18,42),(52,48),(54,12),(28,30)]:
            pygame.draw.circle(s,(88,72,50),(dx,dy),4)
            pygame.draw.circle(s,(75,60,40),(dx+1,dy+1),2)
    elif t==WATER:
        s.fill(C["water"])
        for wy in range(8,TILE,14):
            pygame.draw.arc(s,C["water2"],pygame.Rect(4,wy,24,8),0,math.pi,2)
            pygame.draw.arc(s,C["water2"],pygame.Rect(32,wy+4,24,8),0,math.pi,2)
    elif t==TREE:
        s.fill(C["grass"])
        pygame.draw.rect(s,C["tree_trunk"],(26,36,12,22))
        pygame.draw.circle(s,C["tree_top"],(32,28),18)
        pygame.draw.circle(s,C["tree_top2"],(26,22),12)
        pygame.draw.circle(s,C["tree_top2"],(40,20),10)
    elif t==VILLAGE:
        s.fill(C["grass"])
        pygame.draw.rect(s,C["village"],(10,24,44,34))
        pygame.draw.rect(s,C["village_hi"],(10,24,44,8))
        pygame.draw.polygon(s,C["v_roof"],[(5,26),(32,5),(59,26)])
        pygame.draw.polygon(s,C["v_roof2"],[(5,26),(32,5),(32,26)])
        pygame.draw.rect(s,C["wall"],(24,40,16,18))
        pygame.draw.circle(s,C["wall"],(32,40),8)
        pygame.draw.rect(s,C["wall_top"],(26,42,12,8))
        pygame.draw.rect(s,(170,200,240),(12,30,12,10))
        pygame.draw.rect(s,C["wall_top"],(12,30,12,10),1)
        pygame.draw.rect(s,C["wall"],(46,8,8,18))
    elif t==TEMPLE:
        s.fill(C["grass"])
        pygame.draw.rect(s,C["temple"],(6,30,52,28))
        pygame.draw.rect(s,C["temple_hi"],(6,30,52,6))
        pygame.draw.polygon(s,C["t_roof"],[(2,32),(18,8),(32,2),(46,8),(62,32)])
        pygame.draw.polygon(s,C["t_roof2"],[(2,32),(18,8),(32,2),(32,32)])
        pygame.draw.line(s,C["white"],(18,8),(46,8),2)
        for px2 in (11,47):
            pygame.draw.rect(s,C["white"],(px2,30,7,28))
            pygame.draw.rect(s,C["t_roof"],(px2,28,7,4))
        pygame.draw.rect(s,C["wall"],(24,42,16,16))
        pygame.draw.circle(s,C["t_glow"],(32,42),8)
        pygame.draw.circle(s,C["white"],(32,42),5)
        pygame.draw.circle(s,C["gold2"],(32,2),4)
    _tcache[key]=s; return s

def draw_map(surf,tick):
    for row in range(ROWS):
        for col in range(COLS):
            t=MAP_DATA[row][col]
            surf.blit(build_tile(t,col,row),(col*TILE,row*TILE))
            if t==WATER:
                phase=tick*0.04+col*0.8+row*0.5
                for wy in range(8,TILE,14):
                    ox=int(4*math.sin(phase+wy*0.2))
                    pygame.draw.arc(surf,C["water_foam"],
                        pygame.Rect(col*TILE+4+ox,row*TILE+wy,22,6),0,math.pi,2)

# ── HUD ───────────────────────────────────────────────────────────────────────
def draw_hud(surf,fonts,player,npc,message,msg_timer,items):
    hy=TILE*ROWS
    pygame.draw.rect(surf,C["hud_bg"],(0,hy,WIN_W,HUD_H))
    pygame.draw.line(surf,C["hud_border"],(0,hy),(WIN_W,hy),1)
    fb,ft,fs=fonts["body"],fonts["title"],fonts["small"]

    # HP
    surf.blit(ft.render("HP",True,C["muted"]),(14,hy+12))
    bw=150
    pygame.draw.rect(surf,(40,18,18),(46,hy+12,bw,15),border_radius=5)
    fill=int(bw*max(0,player.hp)/player.max_hp)
    ratio=player.hp/player.max_hp
    hcol=C["hp_green"] if ratio>0.5 else C["hp_yellow"] if ratio>0.25 else C["hp_red"]
    pygame.draw.rect(surf,hcol,(46,hy+12,fill,15),border_radius=5)
    surf.blit(fb.render(f"{max(0,player.hp)}/{player.max_hp}",True,C["white"]),(204,hy+13))

    # ATK
    surf.blit(fb.render(f"ATK  {player.atk}",True,C["white"]),(14,hy+36))

    # Wisdom
    surf.blit(ft.render("WISDOM",True,C["muted"]),(14,hy+60))
    sr=pygame.Rect(84,hy+56,148,24)
    if player.has_tiger:
        pygame.draw.rect(surf,C["tiger_dk"],sr,border_radius=4)
        pygame.draw.rect(surf,C["tiger"],sr,1,border_radius=4)
        surf.blit(fb.render("Tiger  [SPACE]",True,C["tiger"]),(sr.x+6,sr.y+4))
    else:
        pygame.draw.rect(surf,(28,24,34),sr,border_radius=4)
        pygame.draw.rect(surf,C["hud_border"],sr,1,border_radius=4)
        surf.blit(fb.render("— empty —",True,C["muted"]),(sr.x+6,sr.y+4))

    # Inventory
    surf.blit(ft.render("BAG",True,C["muted"]),(14,hy+90))
    ix=60
    for kind,meta in ITEM_META.items():
        cnt=player.inventory.get(kind,0)
        col2=C[meta["col_key"]]
        bg=(20,30,20) if cnt>0 else (30,26,36)
        ir=pygame.Rect(ix,hy+86,82,24)
        pygame.draw.rect(surf,bg,ir,border_radius=4)
        pygame.draw.rect(surf,col2 if cnt>0 else C["hud_border"],ir,1,border_radius=4)
        surf.blit(fs.render(f"{meta['short']} x{cnt}",True,col2 if cnt>0 else C["muted"]),(ix+5,hy+90))
        ix+=90

    # Quest tracker
    scroll_done=any(i.kind==ITEM_SCROLL and i.collected for i in items)
    bone_done  =any(i.kind==ITEM_BONE   and i.collected for i in items)
    enemies_done=npc.stage>=2
    surf.blit(ft.render("QUEST",True,C["muted"]),(WIN_W-185,hy+12))
    for i,(done,txt) in enumerate([
        (scroll_done,"Find Ancient Scroll"),
        (bone_done,  "Collect Spirit Bone"),
        (enemies_done,"Defeat the beasts"),
    ]):
        col2=C["jade"] if done else C["muted"]
        surf.blit(fs.render(("✓ " if done else "○ ")+txt,True,col2),(WIN_W-180,hy+30+i*18))

    # Controls
    surf.blit(fs.render("Arrows:Move  E:Interact/Pickup  SPACE:Tiger  H:Heal",True,C["muted"]),(14,hy+120))

    # Flash
    if msg_timer>0:
        a=min(255,msg_timer*7)
        ms=ft.render(message,True,C["jade"]); ms.set_alpha(a)
        surf.blit(ms,(WIN_W//2-ms.get_width()//2,hy+146))

# ── Dialog ────────────────────────────────────────────────────────────────────
def draw_dialog(surf,fonts,speaker,line,page,total):
    bw=WIN_W-32; bh=128; bx=16; by=TILE*ROWS+14
    pygame.draw.rect(surf,C["dialog_bg"],(bx,by,bw,bh),border_radius=8)
    pygame.draw.rect(surf,C["dialog_bd"],(bx,by,bw,bh),2,border_radius=8)
    pygame.draw.circle(surf,C["npc"],(bx+26,by+28),18)
    pygame.draw.circle(surf,C["gold"],(bx+26,by+28),18,2)
    surf.blit(fonts["title"].render(speaker,True,C["gold"]),(bx+50,by+10))
    for i,l in enumerate(textwrap.wrap(line,width=64)[:3]):
        surf.blit(fonts["body"].render(l,True,C["white"]),(bx+50,by+32+i*22))
    prompt=f"[E] Next  ({page}/{total})" if page<total else "[E] Close"
    surf.blit(fonts["small"].render(prompt,True,C["muted"]),(bx+50,by+bh-22))

# ── Game ──────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Twelve Heavens — Demo v2")
        self.screen=pygame.display.set_mode((WIN_W,WIN_H))
        self.clock=pygame.time.Clock()
        self.tick=0
        self.fonts=dict(
            title=pygame.font.SysFont("Georgia",15,bold=True),
            body =pygame.font.SysFont("Georgia",14),
            big  =pygame.font.SysFont("Georgia",34,bold=True),
            small=pygame.font.SysFont("Arial",  12),
        )
        self.player=Player(1,1)
        self.npc=NPC(2,2)
        self.enemies=[Enemy(5,5,hp=4,atk=1),Enemy(6,7,hp=6,atk=1,boss=True)]
        self.items=[Item(4,8,ITEM_HERB),Item(7,1,ITEM_SCROLL),
                    Item(8,5,ITEM_BONE),Item(1,7,ITEM_HERB)]
        self.particles=[]; self.floats=[]
        self.state="explore"
        self.dialog_data=None; self.dialog_page=0
        self.message=""; self.msg_timer=0
        self._enemy_cd=0

    def flash(self,msg,dur=130): self.message=msg; self.msg_timer=dur

    def sfloat(self,text,gx,gy,col=None):
        self.floats.append(FloatText(text,gx*TILE+TILE//2,gy*TILE,col or C["dmg"]))

    def sburst(self,gx,gy,col,n=12):
        burst(self.particles,gx*TILE+TILE//2,gy*TILE+TILE//2,col,n,speed=3)

    def tile_at(self,gx,gy):
        if 0<=gy<ROWS and 0<=gx<COLS: return MAP_DATA[gy][gx]
        return WALL

    def can_walk(self,gx,gy):
        if self.tile_at(gx,gy) not in WALKABLE: return False
        if self.npc.gx==gx and self.npc.gy==gy: return False
        for e in self.enemies:
            if e.alive and e.gx==gx and e.gy==gy: return False
        return True

    def enemy_walk(self,gx,gy):
        if self.tile_at(gx,gy) not in WALKABLE: return False
        if self.npc.gx==gx and self.npc.gy==gy: return False
        if self.player.gx==gx and self.player.gy==gy: return False
        for e in self.enemies:
            if e.alive and e.gx==gx and e.gy==gy: return False
        return True

    def do_attack(self,e,tx,ty,bonus_mult=1):
        if self.player._atk_cd>0: return
        dmg=self.player.atk*bonus_mult
        e.take_damage(dmg)
        self.sfloat(f"-{dmg}",tx,ty,C["dmg"])
        self.sburst(tx,ty,C["dmg"],8)
        self.player._atk_cd=18
        if not e.alive:
            self.sfloat("Defeated!",tx,ty,C["jade"])
            self.sburst(tx,ty,C["xp_col"],18)
            self.flash("Enemy defeated!")

    def try_move(self,dx,dy):
        if self.player._move_cd>0: return
        nx=self.player.gx+dx; ny=self.player.gy+dy
        if dx!=0: self.player.facing=(dx,0)
        elif dy!=0: self.player.facing=(0,dy)
        if self.can_walk(nx,ny):
            self.player.gx=nx; self.player.gy=ny; self.player._move_cd=7
            for item in self.items:
                if not item.collected and item.gx==nx and item.gy==ny:
                    self.collect_item(item)
        else:
            for e in self.enemies:
                if e.alive and e.gx==nx and e.gy==ny:
                    self.do_attack(e,nx,ny); break

    def tiger_strike(self):
        if not self.player.has_tiger or self.player._atk_cd>0: return
        fx,fy=self.player.facing
        tx=self.player.gx+fx; ty=self.player.gy+fy
        self.player._tiger_flash=25
        self.sburst(self.player.gx,self.player.gy,C["tiger"],8)
        hit=False
        for e in self.enemies:
            if e.alive and e.gx==tx and e.gy==ty:
                dmg=self.player.atk*3
                e.take_damage(dmg)
                self.sfloat(f"TIGER -{dmg}!",tx,ty,C["tiger"])
                self.sburst(tx,ty,C["tiger"],16)
                self.player._atk_cd=28; hit=True
                if not e.alive:
                    self.sfloat("Defeated!",tx,ty,C["jade"])
                    self.sburst(tx,ty,C["xp_col"],18)
                    self.flash("Enemy defeated!")
                break
        if not hit:
            self.sfloat("No target!",self.player.gx,self.player.gy,C["muted"])

    def collect_item(self,item):
        item.collected=True
        meta=ITEM_META[item.kind]
        self.player.add_item(item.kind)
        self.sburst(item.gx,item.gy,C[meta["col_key"]],14)
        self.sfloat(f"+{meta['label']}",item.gx,item.gy,C[meta["col_key"]])
        self.flash(f"Picked up: {meta['label']}  [desc: {ITEM_META[item.kind]['label']}]")

    def use_herb(self):
        heal=self.player.use_herb()
        if heal>0:
            self.sfloat(f"+{heal} HP",self.player.gx,self.player.gy,C["heal_col"])
            self.sburst(self.player.gx,self.player.gy,C["heal_col"],12)
            self.flash(f"Healed {heal} HP!")
        else:
            self.flash("No Healing Herbs in bag!")

    def try_interact(self):
        px,py=self.player.gx,self.player.gy
        for item in self.items:
            if not item.collected and abs(item.gx-px)<=1 and abs(item.gy-py)<=1:
                if item.gx!=px or item.gy!=py:
                    self.collect_item(item); return
        for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
            if self.npc.gx==px+dx and self.npc.gy==py+dy:
                self.open_dialog(); return
        if self.tile_at(px,py)==TEMPLE:
            self.flash("Tiger Wisdom pulses here…" if self.player.has_tiger else "Complete the elder's quest first.")

    def open_dialog(self):
        quest_ready=(any(i.kind==ITEM_SCROLL and i.collected for i in self.items) and
                     any(i.kind==ITEM_BONE   and i.collected for i in self.items) and
                     all(not e.alive for e in self.enemies))
        if self.npc.stage==0:
            self.npc.stage=1
        elif self.npc.stage==1 and quest_ready:
            self.npc.stage=2
            self.player.grant_tiger()
            self.sburst(self.player.gx,self.player.gy,C["tiger"],22)
            self.flash("Tiger Wisdom acquired!  ATK x3!")
        elif self.npc.stage==2:
            self.npc.stage=3
        speaker,lines=self.npc.dialog()
        self.dialog_data=(speaker,lines); self.dialog_page=0; self.state="dialog"

    def advance_dialog(self):
        if not self.dialog_data: self.state="explore"; return
        _,lines=self.dialog_data
        if self.dialog_page<len(lines)-1: self.dialog_page+=1
        else: self.state="explore"; self.dialog_data=None

    def check_enemy_contact(self):
        if self._enemy_cd>0: return
        px,py=self.player.gx,self.player.gy
        for e in self.enemies:
            if e.alive and e.intent=="attack":
                if abs(e.gx-px)<=1 and abs(e.gy-py)<=1 and (e.gx!=px or e.gy!=py):
                    self.player.take_damage(e.atk)
                    self.sfloat(f"-{e.atk} HP",px,py,C["dmg"])
                    self._enemy_cd=90; break

    def update(self):
        self.tick+=1
        self.player.update(); self.npc.update()
        for e in self.enemies: e.update(self.player.gx,self.player.gy,self.enemy_walk)
        for item in self.items: item.update()
        self.particles=[p for p in self.particles if p.alive()]
        for p in self.particles: p.update()
        self.floats=[f for f in self.floats if f.alive()]
        for f in self.floats: f.update()
        if self.msg_timer>0: self.msg_timer-=1
        if self._enemy_cd>0: self._enemy_cd-=1
        self.check_enemy_contact()
        if self.player.hp<=0: self.state="dead"

    def draw(self):
        self.screen.fill(C["bg"])
        draw_map(self.screen,self.tick)
        px,py=self.player.gx,self.player.gy
        for item in self.items:
            item.draw(self.screen)
            if not item.collected and abs(item.gx-px)<=1 and abs(item.gy-py)<=1:
                es=self.fonts["small"].render("[E]",True,C["gold"])
                self.screen.blit(es,(item.gx*TILE+TILE//2-es.get_width()//2,item.gy*TILE-4))
        self.npc.draw(self.screen)
        for e in self.enemies:
            if e.alive: e.draw(self.screen)
        for p in self.particles: p.draw(self.screen)
        self.player.draw(self.screen)
        for f in self.floats: f.draw(self.screen,self.fonts["small"])
        draw_hud(self.screen,self.fonts,self.player,self.npc,
                 self.message,self.msg_timer,self.items)
        if self.state=="dialog" and self.dialog_data:
            speaker,lines=self.dialog_data
            draw_dialog(self.screen,self.fonts,speaker,lines[self.dialog_page],
                        self.dialog_page+1,len(lines))
        elif self.state=="dead":
            ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,170))
            self.screen.blit(ov,(0,0))
            t1=self.fonts["big"].render("You have fallen.",True,C["hp_red"])
            t2=self.fonts["body"].render("Press R to restart",True,C["muted"])
            self.screen.blit(t1,(WIN_W//2-t1.get_width()//2,WIN_H//2-30))
            self.screen.blit(t2,(WIN_W//2-t2.get_width()//2,WIN_H//2+20))
        elif self.state=="win":
            ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,170))
            self.screen.blit(ov,(0,0))
            t1=self.fonts["big"].render("Tiger Wisdom mastered.",True,C["tiger"])
            t2=self.fonts["body"].render("The road to the Twelve Heavens begins here.",True,C["white"])
            t3=self.fonts["body"].render("Press R to play again",True,C["muted"])
            self.screen.blit(t1,(WIN_W//2-t1.get_width()//2,WIN_H//2-50))
            self.screen.blit(t2,(WIN_W//2-t2.get_width()//2,WIN_H//2))
            self.screen.blit(t3,(WIN_W//2-t3.get_width()//2,WIN_H//2+40))
        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type==pygame.QUIT: pygame.quit(); sys.exit()
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    if event.key==pygame.K_r: self.__init__(); continue
                    if self.state=="dialog":
                        if event.key==pygame.K_e: self.advance_dialog()
                    elif self.state=="explore":
                        if event.key==pygame.K_UP:    self.try_move(0,-1)
                        elif event.key==pygame.K_DOWN: self.try_move(0,1)
                        elif event.key==pygame.K_LEFT: self.try_move(-1,0)
                        elif event.key==pygame.K_RIGHT:self.try_move(1,0)
                        elif event.key==pygame.K_e:    self.try_interact()
                        elif event.key==pygame.K_SPACE:self.tiger_strike()
                        elif event.key==pygame.K_h:    self.use_herb()
            if self.state=="explore":
                keys=pygame.key.get_pressed()
                if self.player._move_cd==0:
                    if   keys[pygame.K_UP]:    self.try_move(0,-1)
                    elif keys[pygame.K_DOWN]:  self.try_move(0,1)
                    elif keys[pygame.K_LEFT]:  self.try_move(-1,0)
                    elif keys[pygame.K_RIGHT]: self.try_move(1,0)
                self.update()
                if (self.player.has_tiger and self.npc.stage>=2 and
                        self.tile_at(self.player.gx,self.player.gy)==TEMPLE):
                    self.state="win"
            self.draw()

if __name__=="__main__":
    Game().run()
