import pygame
import random
import math
import time
import sys
import os

pygame.init()

# ================== HIGH SCORE FILE ==================
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "w") as f:
            f.write("0")
        return 0
    with open(HIGHSCORE_FILE, "r") as f:
        return int(f.read())

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

high_score = load_highscore()

# ================== SCREEN ==================
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Exam Hall Survival")
clock = pygame.time.Clock()
FPS = 60

# ================== COLORS ==================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (60, 120, 255)
RED = (255, 70, 70)
DARK_RED = (180, 30, 30)
LIGHT_GRAY = (210, 210, 210)

# ================== STAR TYPES ==================
STAR_TYPES = {
    "yellow": ((255, 220, 60), 10),
    "blue":   ((60, 200, 255), 15),
    "green":  ((100, 255, 100), 20),
    "pink":   ((255, 120, 180), 25),
    "orange": ((255, 160, 60), 30)
}

# ================== FONTS ==================
font = pygame.font.SysFont("Arial", 22, bold=True)
big_font = pygame.font.SysFont("Arial", 46, bold=True)

# ================== PLAYER ==================
player_size = 40
player_x, player_y = WIDTH//2, HEIGHT-80
player_speed = 6
lives = 3

# ================== OBJECTS ==================
teachers = []
obstacles = []
powerups = []

teacher_size = 50
obstacle_w, obstacle_h = 30, 15

# ================== BOSS ==================
boss = None
boss_size = 80

# ================== GAME ==================
score = 0
level = 1
LEVEL_TIME = 30
level_start_time = None
game_state = "start"
game_over_time = None

teacher_speech = [
    "No cheating!",
    "Eyes on paper!",
    "Caught you!",
    "Hey!"
]

boss_speech = [
    "YOU DARE CHEAT?",
    "DETENTION!",
    "I SEE EVERYTHING!"
]

# ================== DRAW FUNCTIONS ==================
def draw_player(x, y):
    bounce = 3 * math.sin(pygame.time.get_ticks()*0.01)
    cx, cy = x+player_size//2, int(y+player_size//2+bounce)
    pygame.draw.circle(screen, BLUE, (cx, cy), player_size//2)
    pygame.draw.circle(screen, WHITE, (cx-8, cy-6), 5)
    pygame.draw.circle(screen, WHITE, (cx+8, cy-6), 5)
    pygame.draw.circle(screen, BLACK, (cx-8, cy-6), 2)
    pygame.draw.circle(screen, BLACK, (cx+8, cy-6), 2)
    pygame.draw.arc(screen, BLACK, (cx-10, cy, 20, 10),
                    math.pi/6, 5*math.pi/6, 2)

def draw_teacher(t):
    cx, cy = t["x"]+teacher_size//2, t["y"]+teacher_size//2
    pygame.draw.circle(screen, RED, (cx, cy), teacher_size//2)
    pygame.draw.circle(screen, WHITE, (cx-8, cy-6), 5)
    pygame.draw.circle(screen, WHITE, (cx+8, cy-6), 5)
    pygame.draw.circle(screen, BLACK, (cx-8, cy-6), 2)
    pygame.draw.circle(screen, BLACK, (cx+8, cy-6), 2)
    pygame.draw.arc(screen, BLACK, (cx-10, cy, 20, 10),
                    5*math.pi/6, math.pi/6, 2)
    if t["talk"] > 0:
        draw_bubble(cx, t["y"]-10, t["speech"])
        t["talk"] -= 1

def draw_boss(b):
    cx, cy = b["x"]+boss_size//2, b["y"]+boss_size//2
    pygame.draw.circle(screen, DARK_RED, (cx, cy), boss_size//2)
    pygame.draw.circle(screen, WHITE, (cx-15, cy-10), 7)
    pygame.draw.circle(screen, WHITE, (cx+15, cy-10), 7)
    pygame.draw.circle(screen, BLACK, (cx-15, cy-10), 3)
    pygame.draw.circle(screen, BLACK, (cx+15, cy-10), 3)
    pygame.draw.arc(screen, BLACK, (cx-20, cy+5, 40, 20),
                    5*math.pi/6, math.pi/6, 3)
    pygame.draw.rect(screen, RED, (b["x"], b["y"]-10, boss_size, 6))
    pygame.draw.rect(screen, (0,255,0),
                     (b["x"], b["y"]-10,
                      int(boss_size*(b["hp"]/2)), 6))
    if b["talk"] > 0:
        draw_bubble(cx, b["y"]-20, b["speech"])
        b["talk"] -= 1

def draw_bubble(x, y, text):
    txt = font.render(text, True, BLACK)
    rect = txt.get_rect(center=(x, y))
    pygame.draw.rect(screen, WHITE, rect.inflate(10,10), border_radius=8)
    pygame.draw.rect(screen, BLACK, rect.inflate(10,10), 2, border_radius=8)
    screen.blit(txt, rect)

def draw_obstacle(o):
    pygame.draw.rect(screen, LIGHT_GRAY,
                     (o["x"], o["y"], obstacle_w, obstacle_h))

def draw_powerup(p):
    if p["type"]=="star":
        pygame.draw.circle(screen, p["color"], (p["x"], p["y"]), 10)
    else:
        pygame.draw.polygon(screen, RED, [
            (p["x"], p["y"]+8),
            (p["x"]-10, p["y"]-6),
            (p["x"], p["y"]-14),
            (p["x"]+10, p["y"]-6)
        ])

def draw_ui():
    for i in range(lives):
        pygame.draw.circle(screen, RED, (30+i*30, 30), 8)
    screen.blit(font.render(f"Score: {score}", True, BLACK), (WIDTH-160, 20))
    screen.blit(font.render(f"High: {high_score}", True, BLACK), (WIDTH-160, 45))

def draw_timer():
    elapsed = time.time()-level_start_time
    remaining = max(0, LEVEL_TIME-elapsed)
    w = int((remaining/LEVEL_TIME)*(WIDTH-40))
    color = (0,200,0) if remaining>20 else (255,200,0) if remaining>10 else (200,0,0)
    pygame.draw.rect(screen, color, (20,60,w,15))

def start_level():
    global level_start_time, teachers, obstacles, powerups, boss
    level_start_time = time.time()
    teachers, obstacles, powerups = [], [], []
    boss = None
    if level == 3:
        boss = {
            "x": WIDTH//2-boss_size//2,
            "y": 80,
            "hp": 2,
            "talk": 120,
            "speech": random.choice(boss_speech)
        }

# ================== MAIN LOOP ==================
running = True
while running:
    screen.fill(WHITE)

    if game_state=="start":
        screen.blit(big_font.render("Exam Hall Survival",True,BLACK),
                    (WIDTH//2-220, HEIGHT//3))
        screen.blit(font.render("Press SPACE to Start",True,BLACK),
                    (WIDTH//2-110, HEIGHT//2))
        screen.blit(font.render(f"High Score: {high_score}",True,BLACK),
                    (WIDTH//2-90, HEIGHT//2+40))

    elif game_state=="playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x>0: player_x-=player_speed
        if keys[pygame.K_RIGHT] and player_x<WIDTH-player_size: player_x+=player_speed

        if random.randint(1,50)==1:
            obstacles.append({"x":random.randint(0,WIDTH-obstacle_w),"y":-20})
        for o in obstacles: o["y"]+=2+level

        if random.randint(1,120-level*20)==1:
            teachers.append({
                "x":random.randint(0,WIDTH-teacher_size),
                "y":-50,
                "speech":random.choice(teacher_speech),
                "talk":0
            })
        for t in teachers:
            t["y"]+=2+level
            if abs(t["x"]-player_x)<60 and abs(t["y"]-player_y)<60:
                t["talk"]=40

        if random.randint(1,60)==1:
            if random.choice([True,True,False]):
                _,(col,pts)=random.choice(list(STAR_TYPES.items()))
                powerups.append({"type":"star","x":random.randint(20,WIDTH-20),
                                 "y":-20,"color":col,"points":pts})
            else:
                powerups.append({"type":"heart","x":random.randint(20,WIDTH-20),"y":-20})

        for p in powerups: p["y"]+=3

        draw_player(player_x,player_y)
        for o in obstacles: draw_obstacle(o)
        for t in teachers: draw_teacher(t)
        if boss:
            boss["x"]+=(player_x-boss["x"])*0.02
            draw_boss(boss)
        for p in powerups: draw_powerup(p)
        draw_ui()
        draw_timer()

        pr = pygame.Rect(player_x,player_y,player_size,player_size)

        for o in obstacles[:]:
            if pr.colliderect((o["x"],o["y"],obstacle_w,obstacle_h)):
                lives-=1; obstacles.remove(o)

        for t in teachers[:]:
            if pr.colliderect((t["x"],t["y"],teacher_size,teacher_size)):
                lives-=1; teachers.remove(t)

        if boss and pr.colliderect((boss["x"],boss["y"],boss_size,boss_size)):
            lives-=2; boss["talk"]=60

        for p in powerups[:]:
            if pr.colliderect((p["x"],p["y"],20,20)):
                if p["type"]=="star": score+=p["points"]
                else: lives=min(3,lives+1)
                powerups.remove(p)

        if lives<=0:
            if score>high_score:
                high_score=score; save_highscore(high_score)
            game_state="gameover"; game_over_time=time.time()

        if time.time()-level_start_time>=LEVEL_TIME:
            level+=1
            if level>3:
                if score>high_score:
                    high_score=score; save_highscore(high_score)
                game_state="gameover"; game_over_time=time.time()
            else:
                start_level()

    elif game_state=="gameover":
        screen.blit(big_font.render("GAME OVER",True,RED),
                    (WIDTH//2-140,HEIGHT//3))
        if game_over_time and time.time()-game_over_time>3:
            game_state="start"
            lives,score,level=3,0,1

    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
            if game_state=="start":
                game_state="playing"
                lives,score,level=3,0,1
                player_x,player_y=WIDTH//2,HEIGHT-80
                start_level()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
