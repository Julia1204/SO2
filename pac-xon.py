import copy

import pygame
from board import board

pygame.init()

WIDTH = 900
HEIGHT = 700
x_tiles = 44
y_tiles = 29
height = ((HEIGHT - 100) // y_tiles)
width = (WIDTH // x_tiles)
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
color = (0, 0, 255)
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (width, height)))
player_x = 0.5 * width
player_y = 100
direction = 0
counter = 0
board = copy.deepcopy(board)


def draw_board():
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 1:
                pygame.draw.rect(screen, color, pygame.Rect(i * width + 0.5 * width, j * height + 100, width - 1, height - 1))


def draw_player():
    if direction == 0:
        screen.blit(player_images[counter //5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter //5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter //5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter //5], -90), (player_x, player_y))


run = True
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
    else:
        counter = 0
        
    screen.fill('black')
    draw_board()
    draw_player()

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

    pygame.display.flip()

pygame.quit()