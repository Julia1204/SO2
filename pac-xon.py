import copy
import time
import pygame
from board import board
import threading
import random

pygame.init()

WIDTH = 900
HEIGHT = 700
x_tiles = 44
y_tiles = 29
height = ((HEIGHT - 100) // y_tiles)
width = (WIDTH // x_tiles)
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 15
font = pygame.font.Font('freesansbold.ttf', 20)
color = (0, 0, 255)
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (width, height)))
player_x = 0.5 * width
player_y = 100
direction = 0
counter = 0
pink_ghost_amount = 2
pink_ghost_x = []
pink_ghost_y = []
pink_ghost_direction = []
for _ in range(pink_ghost_amount):
    pink_ghost_direction.append(0)
board = copy.deepcopy(board)
pink_ghost = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (width, height))
lives = 5


def draw_board():
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 1:
                pygame.draw.rect(screen, color, pygame.Rect(i * width + 0.5 * width, j * height + 100, width - 1, height - 1))
            if board[i][j] == 2:
                pygame.draw.rect(screen, color, pygame.Rect(i * width + 0.5 * width, j * height + 100, width - 1, height - 1))
            if board[i][j] == -1:
                screen.blit(pink_ghost, (i * width + 0.5 * width, j * height + 100))


def draw_player():
    if direction == 0:
        screen.blit(player_images[counter // 1], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 1], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 1], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 1], -90), (player_x, player_y))


def move_player(playerx, playery):
    if direction == 0:
        playerx += width
        if playerx > WIDTH - width:
            playerx -= width
    if direction == 1:
        playerx -= width
        if playerx < 0:
            playerx += width
    if direction == 2:
        playery -= height
        if playery < 100:
            playery += height
    if direction == 3:
        playery += height
        if playery > HEIGHT - 2*height:
            playery -= height

    return playerx, playery


def fill_path():
    if board[int(player_x / width)][int((player_y - 5*height) / height)] == 0:
        board[int(player_x / width)][int((player_y - 5*height) / height)] = 2

    if board[int(player_x / width)][int((player_y - 5 * height) / height)] == 1:
        pass


def draw_pink(amount):
    for x in range(amount):
        i = 0
        j = 0
        while board[i][j] != 0:
            i = random.randint(0, 43)
            j = random.randint(0, 28)

        board[i][j] = -1
        pink_ghost_x.append(i)
        pink_ghost_y.append(j)


def lose_life():
    for i in range(x_tiles):
        for j in range(y_tiles):
            if board[i][j] == 2:
                board[i][j] = 0

    global lives
    lives = lives - 1

    global player_y
    global player_x
    player_y = 100
    player_x = 0.5 * width


def move_pink():
    for i in range(pink_ghost_amount):
        if pink_ghost_direction[i] == 0 and board[pink_ghost_x[i]+1][pink_ghost_y[i]-1] == 2:
            lose_life()
        elif pink_ghost_direction[i] == 0 and board[pink_ghost_x[i]+1][pink_ghost_y[i]-1] != 1:
            board[pink_ghost_x[i]][pink_ghost_y[i]] = 0
            board[pink_ghost_x[i]+1][pink_ghost_y[i]-1] = -1
            pink_ghost_x[i] += 1
            pink_ghost_y[i] -= 1
        elif pink_ghost_direction[i] == 0 and board[pink_ghost_x[i]+1][pink_ghost_y[i]-1] == 1:
            if board[pink_ghost_x[i]][pink_ghost_y[i]-1] == 1: pink_ghost_direction[i] = 1
            elif board[pink_ghost_x[i] + 1][pink_ghost_y[i]] == 1: pink_ghost_direction[i] = 3

        if pink_ghost_direction[i] == 1 and board[pink_ghost_x[i]+1][pink_ghost_y[i]+1] == 2:
            lose_life()
        elif pink_ghost_direction[i] == 1 and board[pink_ghost_x[i]+1][pink_ghost_y[i]+1] != 1:
            board[pink_ghost_x[i]][pink_ghost_y[i]] = 0
            board[pink_ghost_x[i]+1][pink_ghost_y[i]+1] = -1
            pink_ghost_x[i] += 1
            pink_ghost_y[i] += 1
        elif pink_ghost_direction[i] == 1 and board[pink_ghost_x[i]+1][pink_ghost_y[i]+1] == 1:
            if board[pink_ghost_x[i]][pink_ghost_y[i]+1] == 1: pink_ghost_direction[i] = 0
            elif board[pink_ghost_x[i] + 1][pink_ghost_y[i]] == 1: pink_ghost_direction[i] = 2

        if pink_ghost_direction[i] == 2 and board[pink_ghost_x[i]-1][pink_ghost_y[i]+1] == 2:
            lose_life()
        elif pink_ghost_direction[i] == 2 and board[pink_ghost_x[i]-1][pink_ghost_y[i]+1] != 1:
            board[pink_ghost_x[i]][pink_ghost_y[i]] = 0
            board[pink_ghost_x[i]-1][pink_ghost_y[i]+1] = -1
            pink_ghost_x[i] -= 1
            pink_ghost_y[i] += 1
        elif pink_ghost_direction[i] == 2 and board[pink_ghost_x[i]-1][pink_ghost_y[i]+1] == 1:
            if board[pink_ghost_x[i]][pink_ghost_y[i]+1] == 1: pink_ghost_direction[i] = 3
            elif board[pink_ghost_x[i] - 1][pink_ghost_y[i]] == 1: pink_ghost_direction[i] = 1

        if pink_ghost_direction[i] == 3 and board[pink_ghost_x[i]-1][pink_ghost_y[i]-1] == 2:
            lose_life()
        elif pink_ghost_direction[i] == 3 and board[pink_ghost_x[i]-1][pink_ghost_y[i]-1] != 1:
            board[pink_ghost_x[i]][pink_ghost_y[i]] = 0
            board[pink_ghost_x[i]-1][pink_ghost_y[i]-1] = -1
            pink_ghost_x[i] -= 1
            pink_ghost_y[i] -= 1
        elif pink_ghost_direction[i] == 3 and board[pink_ghost_x[i]-1][pink_ghost_y[i]-1] == 1:
            if board[pink_ghost_x[i]][pink_ghost_y[i]-1] == 1: pink_ghost_direction[i] = 2
            elif board[pink_ghost_x[i]-1][pink_ghost_y[i]] == 1: pink_ghost_direction[i] = 0


run = True
draw_pink(pink_ghost_amount)
while run:
    timer.tick(fps)
    if counter < 3:
        counter += 1
    else:
        counter = 0
        
    screen.fill('black')
    draw_board()
    draw_player()
    move_pink()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                direction = 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                direction = 2
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                direction = 3

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
        player_x, player_y = move_player(player_x, player_y)

    fill_path()
    pygame.display.flip()

pygame.quit()