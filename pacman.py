from board import boards
import pygame
import sys
import math
import random

from pygame.locals import (
        RLEACCEL, 
        K_UP,
        K_DOWN,
        K_LEFT,
        K_RIGHT,
        K_ESCAPE,
        K_SPACE,
        KEYDOWN,
        KEYUP,
        QUIT
        )    

clock = pygame.time.Clock()

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("playing.mp3")
pygame.mixer.music.play(loops=-1)

game_over_sound = pygame.mixer.Sound("game_over.wav")
game_won_sound = pygame.mixer.Sound("game_won.wav")
super_power_sound = pygame.mixer.Sound("super_power.wav")
collision_sound = pygame.mixer.Sound("collision.wav")

WIDTH = 757
HEIGHT = 800
FPS = 30

BLACK_BLUE = (0, 0, 28)
WHITE = (255, 255, 255)
TITLE = (59, 143, 140)
RED = (255, 0, 0)

PI = math.pi

screen = pygame.display.set_mode([WIDTH,HEIGHT])
title = pygame.image.load("tytul.png")
screen.blit(title, (0, 0))
icon = pygame.image.load("pac-man2.png")
screen.blit(icon, (230, 383))
icon2 = pygame.image.load("pac-man.png")
screen.blit(icon2, (510, 383))

pygame.display.flip()

player_icon = pygame.image.load("pac-man3.png")
player_icon = pygame.transform.scale(player_icon,(35,35))
player_lives_icon = pygame.transform.scale(player_icon,(20,20))

player_left = pygame.transform.rotate(player_icon, 180)
player_up = pygame.transform.rotate(player_icon, 90)
player_down = pygame.transform.rotate(player_icon, 270)

level = boards

direction = 0
player_x = 250
player_y = 550

allowed_turns = [False, False, False, False]

score = 0
points = 0

blinky_icon = pygame.image.load("blinky.png")
inky_icon = pygame.image.load("inky.png")
pinky_icon = pygame.image.load("pinky.png")
clyde_icon = pygame.image.load("clyde.png")

history_text = ['Pac-Man,originally called Puck Man in Japan, is a 1980 maze action video game developed and released','by Namco for arcades. In North America, the game was released by Midway Manufacturing as part of its','licensing agreement with Namco America. The player controls Pac-Man, who must eat all the dots inside an','enclosed maze while avoiding four colored ghosts. Eating large flashing dots called "Power Pellets" causes','the ghosts to temporarily turn blue, allowing Pac-Man to eat them for bonus points.',' ','Game development began in early 1979, directed by Toru Iwatani with a nine-man team. Iwatani wanted to ','create a game that could appeal to women as well as men, because most video games of the time had','themes of war or sports. Although the inspiration for the Pac-Man character was the image of a pizza','with a slice removed, Iwatani has said he also rounded out the Japanese character for mouth, kuchi.','The in-game characters were made to be cute and colorful to appeal to younger players.','The original Japanese title of Puck Man was derived from the Japanese phrase "Paku paku taberu" which refers','to gobbling something up; the title was changed for the North American release to mitigate vandalism.','Pac-Man was a widespread critical and commercial success, leading to several sequels, merchandise,','and two television series, as well as a hit single by Buckner & Garcia. The character of Pac-Man has become','the official mascot of Bandai Namco Entertainment. The game remains one of the highest-grossing and best-selling','games, generating more than $14 billion in revenue (as of 2016) and 43 million units in sales','combined, and has an enduring commercial and cultural legacy, commonly listed as one of the greatest video','games of all time.']

with open("best_scores.txt", "r") as file:        # podział pliku z najlepszymi wynikami na listę i sortowanie
    best_scores = file.read()
    best_scores = best_scores.split(' ')
    for i in range(len(best_scores)):
        best_scores[i] = int(best_scores[i])
    best_scores.sort(reverse=True)

font_name = pygame.font.match_font('arial', bold=True)


def add_score():
    '''Funkcja dodająca aktualny stan punktów do pliku z najlepszymi wynikami'''
    with open("best_scores.txt", "a") as file:
        file.write(' '+str(score))


class Ghost:
    def __init__(self, image, x, y, player_x, player_y, speed, direction, current_score, dead=False):
        self.x = x
        self.y = y
        self.center_x = self.x + 19
        self.center_y = self.y + 18
        self.dead = dead
        self.score = current_score
        self.speed = speed
        self.direction = direction
        self.image = image
        self.player_x = player_x
        self.player_y = player_y

    def add_ghost(self):
        '''Dodawanie ducha na ekran'''
        screen.blit(self.image, (self.x, self.y))
    
    def detect_player(self, distance):
        '''Funkcja odpowiadająca za namierzanie gracza. Parametr distance to minimalna odległość w jakiej musi znaleźć się gracz, aby duch zaczął za nim podążać'''
        if math.sqrt(abs((self.player_x - self.center_x)^2)+abs((self.player_y - self.center_y)^2)) < distance:
            if self.center_x >= self.player_x + 20 and self.center_y >= self.player_y + 20:
                p = [1,2]
                i = random.choice(p)
                p.remove(i)
                if self.allowed_turns[i]:
                    self.direction = i
                else:
                    if self.allowed_turns[p[0]]:
                        self.direction = p[0]
                    else:
                        pass
        
            elif self.center_x >= self.player_x + 20 and self.center_y < self.player_y + 20:
                p = [1,3]
                i = random.choice(p)
                p.remove(i)
                if self.allowed_turns[i]:
                    self.direction = i
                else:
                    if self.allowed_turns[p[0]]:
                        self.direction = p[0]
                    else:
                        pass

            elif self.center_x < self.player_x + 20 and self.center_y < self.player_y + 20:
                p = [0,3]
                i = random.choice(p)
                p.remove(i)
                if self.allowed_turns[i]:
                    self.direction = i
                else:
                    if self.allowed_turns[p[0]]:
                        self.direction = p[0]
                    else:
                        pass

            elif self.center_x < self.player_x + 20 and self.center_y >= self.player_y + 20:
                p = [0,2]
                i = random.choice(p)
                p.remove(i)
                if self.allowed_turns[i]:
                    self.direction = i
                else:
                    if self.allowed_turns[p[0]]:
                        self.direction = p[0]
                    else:
                        pass
        else: 
            pass
        return self.direction

    def wall_collision(self):
        '''Dtetekcja ścian ducha'''
        tile_h = (HEIGHT-50)//32
        tile_w = WIDTH//30
        extra_space = 13
        self.allowed_turns = [False, False, False, False]

        if self.center_x //30 < 29:
            if level[(self.center_y - extra_space) // tile_h][self.center_x // tile_w] == 0:
                self.allowed_turns[2] = True
            if level[self.center_y // tile_h][(self.center_x - extra_space) // tile_w] < 3:
                self.allowed_turns[1] = True
            if level[self.center_y // tile_h][(self.center_x + extra_space) // tile_w] < 3:
                self.allowed_turns[0] = True
            if level[(self.center_y + extra_space) // tile_h][self.center_x // tile_w] < 3:
                self.allowed_turns[3] = True
            if level[(self.center_y -extra_space) // tile_h][self.center_x // tile_w] < 3:
                self.allowed_turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % tile_w <= 18:
                    if level[(self.center_y + extra_space) // tile_h][self.center_x // tile_w] < 3:
                        self.allowed_turns[3] = True
                    if level[(self.center_y - extra_space) // tile_h][self.center_x // tile_w] < 3:
                        self.allowed_turns[2] = True
                if 12 <= self.center_y % tile_w <= 18:
                    if level[self.center_y // tile_h][(self.center_x - tile_w) // tile_w] < 3:
                        self.allowed_turns[1] = True
                    if level[self.center_y // tile_h][(self.center_x + tile_w) // tile_w] < 3:
                        self.allowed_turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % tile_w <= 18:
                    if level[(self.center_y + extra_space) // tile_h][self.center_x // tile_w] < 3:
                        self.allowed_turns[3] = True
                    if level[(self.center_y - extra_space) // tile_h][self.center_x // tile_w] < 3:
                        self.allowed_turns[2] = True
                if 12 <= self.center_y % tile_h <= 18:
                    if level[self.center_y // tile_h][(self.center_x - extra_space) // tile_w] < 3:
                        self.allowed_turns[1] = True
                    if level[self.center_y // tile_h][(self.center_x + extra_space) // tile_w] < 3:
                        self.allowed_turns[0] = True
        return self.allowed_turns
    
    def move_ghost(self):
        '''Funkcja odpowiadająca za poruszanie się ducha oraz przyspieszanie'''
        if self.score >= 40:
            self.speed = 3
        elif self.score >= 80:
            self.speed = 4
        elif self.score >= 120:
            self.speed = 5

        self.allowed_turns = self.wall_collision()

        if self.direction == 0 and self.allowed_turns[0]:
            self.x += self.speed
        elif self.direction == 1 and self.allowed_turns[1]:
            self.x += -self.speed
        elif self.direction == 2 and self.allowed_turns[2]:
            self.y += -self.speed
        elif self.direction == 3 and self.allowed_turns[3]:
            self.y += self.speed
        else:
            possible = []
            for i in range(len(self.allowed_turns)):
                if self.allowed_turns[i]:
                    possible.append(i)
            k = random.choice(possible)
            self.direction = k
                
        return self.x, self.y, self.direction
    
    def detect_collision(self, distance):
        '''Funkcja sprawdzająca kolizję ducha z graczem'''
        player_center_x = self.player_x + 19
        player_center_y = self.player_y + 18
        if abs(player_center_x - self.center_x) < distance and abs(player_center_y - self.center_y) < distance:
            collision_sound.play()
            return True


def all_points(lvl):
    '''Funkcja zliczająca sumę punktów do zebrania na danym poziomie'''
    points = 0
    for i in range(len(lvl)):
        for j in range(len(lvl[i])):
            if lvl[i][j] == 1 or lvl[i][j] == 2:
                points +=1
    return points
    

def draw_boards(lvl):
    '''Funkcja rysująca planszę'''
    tile_h = (HEIGHT-50)//32
    tile_w = WIDTH//30
    for i in range(len(lvl)):
        for j in range(len(lvl[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'black', (j * tile_w + (0.5 * tile_w), i * tile_h + (0.5 * tile_h)), 4)
            if level[i][j] == 2:
                pygame.draw.circle(screen, 'black', (j * tile_w + (0.5 * tile_w), i * tile_h + (0.5 * tile_h)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, TITLE, (j * tile_w + (0.5 * tile_w), i * tile_h), (j * tile_w + (0.5 * tile_w), i * tile_h + tile_h), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, TITLE, (j * tile_w, i * tile_h + (0.5 * tile_h)), (j * tile_w + tile_w, i * tile_h + (0.5 * tile_h)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, TITLE, [(j * tile_w - (tile_w * 0.4)) - 2, (i * tile_h + (0.5 * tile_h)), tile_w, tile_h], 0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, TITLE, [(j * tile_w + (tile_w * 0.5)), (i * tile_h + (0.5 * tile_h)), tile_w, tile_h], PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, TITLE, [(j * tile_w + (tile_w * 0.5)), (i * tile_h - (0.4 * tile_h)), tile_w, tile_h], PI,3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, TITLE, [(j * tile_w - (tile_w * 0.4)) - 2, (i * tile_h - (0.4 * tile_h)), tile_w, tile_h], 3 * PI / 2,2 * PI, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'black', (j * tile_w, i * tile_h + (0.5 * tile_h)), (j * tile_w + tile_w, i * tile_h + (0.5 * tile_h)), 3)


def new_text(surf, text, color, size, x, y):
    '''Dodawanie tekstu na ekran'''
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surf.blit(text_surface,text_rect)


def lives(surf, x, y, lives, img):
    '''Funkcja dodająca ikonky dostępnych żyć na ekran'''
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img, img_rect)


def history_screen():
    '''Ekran zawierający historię gry'''
    screen = pygame.display.set_mode([WIDTH,HEIGHT])
    screen.fill(WHITE)
    new_text(screen, "History", TITLE, 30, WIDTH/2, 100)
    for i in range(len(history_text)):
        new_text(screen, history_text[i], BLACK_BLUE, 13, WIDTH/2, 200+(i*18))
    new_text(screen, "Source: https://en.wikipedia.org/wiki/Pac-Man", BLACK_BLUE, 12, 150, HEIGHT-35)
    new_text(screen, "~ LEFT ARROW to start page ~", TITLE, 17, WIDTH/2, 650)
    pygame.display.flip()
    status = True
    while status:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    start_screen()
                else:
                    status = False


def start_screen():
    '''Konfiguracja ekranu startowego'''
    screen = pygame.display.set_mode([WIDTH,HEIGHT])
    title = pygame.image.load("tytul.png")
    screen.blit(title, (0, 0))
    icon = pygame.image.load("pac-man2.png")
    screen.blit(icon, (WIDTH-(3/4)*WIDTH, 333))
    icon2 = pygame.image.load("pac-man.png")
    screen.blit(icon2, (515, 333))
    new_text(screen, "Press a key to start", TITLE, 20, WIDTH/2, 350)
    new_text(screen, "~ RIGHT ARROW to read about history ~", BLACK_BLUE, 13, 145, 30)
    new_text(screen, "~ ESC to quit ~", BLACK_BLUE, 13, 660, 30)
    new_text(screen, "Arrows to move", TITLE, 17, WIDTH/2, 450)
    new_text(screen, "Eat all of the dots", TITLE, 17, WIDTH/2, 480)
    new_text(screen, "Stay away from the ghosts", TITLE, 17, WIDTH/2, 510)
    new_text(screen, "Big dot = you can eat the ghosts for extra points", TITLE, 17, WIDTH/2, 540)
    new_text(screen, "Best scores", BLACK_BLUE, 20, WIDTH/2, 600)
    for i in range(4):
        new_text(screen, "~  "+str(best_scores[i])+"  ~", BLACK_BLUE, 15, WIDTH/2, 640+(i*30))
    pygame.display.flip()
    status = True
    while status:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    history_screen()
                else:
                    status = False


def add_player():
    '''Dodawanie gracza na ekran'''
    if direction == 0:
        screen.blit(player_left, (player_x, player_y))
    elif direction == 1:
        screen.blit(player_icon, (player_x, player_y))
    elif direction == 2:
        screen.blit(player_up, (player_x, player_y))
    elif direction == 3:
        screen.blit(player_down, (player_x, player_y))
    

def movement(surf_x, surf_y):
    '''Ruch gracza'''
    if direction == 0 and allowed_turns[0]:
        surf_x += -3
    elif direction == 1 and allowed_turns[1]:
        surf_x += 3
    elif direction == 2 and allowed_turns[2]:
        surf_y += -3
    elif direction == 3 and allowed_turns[3]:
        surf_y += 3
    return surf_x, surf_y

def wall_collision(surf_x, surf_y):
    '''Detekcja ścian dla gracza'''
    center_x = surf_x + 19
    center_y = surf_y + 17
    allowed_turns = [False, False, False, False]  #[left, right, up, down]
    tile_h = (HEIGHT-50)//32
    tile_w = WIDTH//30
    extra_space = 13
    
    if center_x //30 < 29:
        if direction == 0:
            if level[center_y // tile_h][(center_x - extra_space) // tile_w] < 3:
                allowed_turns[0] = True
        if direction == 1:
            if level[center_y // tile_h][(center_x + extra_space) // tile_w] < 3:
                allowed_turns[1] = True
        if direction == 2:
            if level[(center_y + extra_space) // tile_h][center_x // tile_w] < 3:
                allowed_turns[3] = True
        if direction == 3:
            if level[(center_y - extra_space) // tile_h][center_x // tile_w] < 3:
                allowed_turns[2] = True
        
        if direction == 2 or direction == 3:
            if 12 <= center_x % tile_w <= 18:
                if level[(center_y + extra_space) // tile_h][center_x // tile_w] < 3:
                        allowed_turns[3] = True
                if level[(center_y - extra_space) // tile_h][center_x // tile_w] < 3:
                        allowed_turns[2] = True
            if 12 <= center_y % tile_h <= 18:
                if level[center_y // tile_h][(center_x + tile_w) // tile_w] < 3:
                        allowed_turns[1] = True
                if level[center_y // tile_h][(center_x - tile_w) // tile_w] < 3:
                        allowed_turns[0] = True
        
        if direction == 0 or direction == 1:
            if 12 <= center_x % tile_w <= 18:
                if level[(center_y + tile_h) // tile_h][center_x // tile_w] < 3:
                    allowed_turns[3] = True
                if level[(center_y - tile_h) // tile_h][center_x // tile_w] < 3:
                    allowed_turns[2] = True
            if 12 <= center_y % tile_h <= 18:
                if level[center_y // tile_h][(center_x + extra_space) // tile_w] < 3:
                    allowed_turns[1] = True
                if level[center_y // tile_h][(center_x - extra_space) // tile_w] < 3:
                    allowed_turns[0] = True

    else:
        allowed_turns[0] = True
        allowed_turns[1] = True

    return allowed_turns


def eating(surf_x, surf_y, lvl):
    '''Zjadanie kulek i aktualizacja planszy'''
    center_x = surf_x + 19
    center_y = surf_y + 18
    tile_h = (HEIGHT-50)//32
    tile_w = WIDTH//30
    cords = lvl
    if cords[center_y//tile_h][center_x//tile_w] == 1:
        cords[center_y//tile_h][center_x//tile_w] = 0
        draw_boards(cords)
        return False
    if cords[center_y//tile_h][center_x//tile_w] == 2:
        cords[center_y//tile_h][center_x//tile_w] = 0
        draw_boards(cords)
        return True

def super_power(surf_x, surf_y, lvl):
    '''Aktywowanie super sił i możliwości jedzenia duchów'''
    center_x = surf_x + 19
    center_y = surf_y + 18
    tile_h = (HEIGHT-50)//32
    tile_w = WIDTH//30
    cords = lvl
    if cords[center_y//tile_h][center_x//tile_w] == 2:
        super_power_sound.play()
        return True
    


###########################################
#             Rozpoczęcie gry             #
###########################################

running = True
game_start = True
game_won = False
game_over = False
add = True

blinky = Ghost(blinky_icon, 300, 355, player_x, player_y, speed=2, direction=0, current_score=0)
inky = Ghost(inky_icon, 340, 355, player_x, player_y, speed=2, direction=0, current_score=0)
pinky = Ghost(pinky_icon, 380, 355, player_x, player_y, speed=2, direction=0, current_score=0)
clyde = Ghost(clyde_icon, 420, 355, player_x, player_y, speed=2, direction=0, current_score=0)

counter = 0
power_count = 600
power = False

left_lives = 3

while running:

    if game_start:
        start_screen()
        game_start = False

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_LEFT:
                direction = 0
            elif event.key == K_RIGHT:
                direction = 1
            elif event.key == K_UP:
                direction = 2
            elif event.key == K_DOWN:
                direction = 3    
            elif event.key == K_SPACE and game_over:
                    game_start = True
                    game_over = False
                    game_won = False
                    add = True

                    level = boards

                    direction = 0
                    player_x = 250
                    player_y = 550

                    allowed_turns = [False, False, False, False]

                    score = 0
                    points = 0

                    blinky = Ghost(blinky_icon, 300, 355, player_x, player_y, speed=2, direction=0, current_score=0)
                    inky = Ghost(inky_icon, 340, 355, player_x, player_y, speed=2, direction=0, current_score=0)
                    pinky = Ghost(pinky_icon, 380, 355, player_x, player_y, speed=2, direction=0, current_score=0)
                    clyde = Ghost(clyde_icon, 420, 355, player_x, player_y, speed=2, direction=0, current_score=0)

                    counter = 0
                    power_count = 600
                    power = False

                    left_lives = 3   
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                direction = 0
            elif event.key == K_RIGHT:
                direction = 1
            elif event.key == K_UP:
                direction = 2
            elif event.key == K_DOWN:
                direction = 3

    counter += 1
    screen.fill(WHITE)
    points_to_get = all_points(level)
    new_text(screen, 'Score: ' + str(score), TITLE, 20, WIDTH-700, HEIGHT-35)
    draw_boards(level)
    add_player()
    
    blinky = Ghost(blinky_icon, blinky.x, blinky.y, player_x, player_y, speed=blinky.speed, direction=blinky.direction, current_score=score)
    blinky.add_ghost()
    inky = Ghost(inky_icon, inky.x, inky.y, player_x, player_y, speed=inky.speed, direction=inky.direction, current_score=score)
    inky.add_ghost()
    pinky = Ghost(pinky_icon, pinky.x, pinky.y, player_x, player_y, speed=pinky.speed, direction=pinky.direction, current_score=score)
    pinky.add_ghost()
    clyde = Ghost(clyde_icon, clyde.x, clyde.y, player_x, player_y, speed=clyde.speed, direction=clyde.direction, current_score=score)
    clyde.add_ghost()

    player_x, player_y = movement(player_x, player_y)
    allowed_turns = wall_collision(player_x, player_y)

    blinky.x, blinky.y, blinky.direction = blinky.move_ghost()
    blinky.direction = blinky.detect_player(17)
    inky.x, inky.y, inky.direction = inky.move_ghost()
    pinky.x, pinky.y, pinky.direction = pinky.move_ghost()
    clyde.x, clyde.y, clyde.direction = clyde.move_ghost()

    if super_power(player_x, player_y, level) and power_count == 600:
        power_count = 599
    if  power_count < 600 and power_count > 0:
        new_text(screen, '~ Super power activated ~', RED, 20, WIDTH/2, HEIGHT-35)
        if blinky.detect_collision(15):
            blinky.x, blinky.y, blinky.direction = 300, 355, 0
            score += 10
        elif inky.detect_collision(15):
            inky.x, inky.y, inky.direction = 340, 355, 0
            score += 10
        elif pinky.detect_collision(15):
            pinky.x, pinky.y, pinky.direction = 380, 355, 0
            score += 10
        elif clyde.detect_collision(15):
            clyde.x, clyde.y, clyde.direction = 300, 355, 0
            score += 10
        power_count -= 1
    elif power_count == 0:
        power_count = 600
        
    if blinky.detect_collision(4) and left_lives > 0:
        left_lives -= 1
    elif inky.detect_collision(4) and left_lives > 0:
        left_lives -= 1
    elif pinky.detect_collision(4) and left_lives > 0:
        left_lives -= 1
    elif clyde.detect_collision(4) and left_lives > 0:
        left_lives -= 1

    eaten = eating(player_x, player_y, level)
    if eaten == False:
        score += 1
        points += 1

    lives(screen, WIDTH-100, HEIGHT-35, left_lives, player_lives_icon) 

    if left_lives == 0:
        new_text(screen, '~ GAME OVER ~', RED, 50, WIDTH/2, (HEIGHT/2)-100)
        new_text(screen, 'SPACE to play again', RED, 25, WIDTH/2, (HEIGHT/2)-50)
        game_over = True
        if add == True:
            game_over_sound.play()
            add_score()
            add = False

    if points == all_points(level)-4 and left_lives > 0:
        new_text(screen, '~ YOU WIN ~', RED, 50, WIDTH/2, (HEIGHT/2)-100)
        new_text(screen, 'SPACE to play again', RED, 25, WIDTH/2, (HEIGHT/2)-50)
        game_won = True
        if add == True:
            game_won_sound.play()
            add_score()
            add = False

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
