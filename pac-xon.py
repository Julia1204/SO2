import copy
import threading
import pygame
from board import board
import random
import numpy as np
from scipy.ndimage import label

pygame.init()

# Board
WIDTH = 900
HEIGHT = 700
x_tiles = 44
y_tiles = 29
height = (HEIGHT - 100) // y_tiles
width = WIDTH // x_tiles
color = (0, 0, 255)
board = copy.deepcopy(board)

# Gameplay
lives = 3
point_count = 0
fill_percent = 0
level = 0
game_over = False
winner = False

# Display
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Pac-xon")
font = pygame.font.Font("freesansbold.ttf", 30)
timer = pygame.time.Clock()
fps = 15

# Pac-man
player_images = []
for i in range(1, 5):
    player_images.append(
        pygame.transform.scale(
            pygame.image.load(f"assets/player_images/{i}.png"), (width, height)
        )
    )
player_x = 0.5 * width
player_y = 100
direction = 0
counter = 0

# Pink ghost
pink_ghost_amount = 3
pink_ghost_x = []
pink_ghost_y = []
pink_ghost_direction = []
for _ in range(pink_ghost_amount):
    pink_ghost_direction.append(0)
pink_ghost = pygame.transform.scale(
    pygame.image.load(f"assets/ghost_images/pink.png"), (width, height)
)
eaten_pink_ghosts = 0

# Orange ghost
orange_ghost_amount = 1
orange_ghost_x = []
orange_ghost_y = []
orange_ghost_direction = []
orange_ghost = pygame.transform.scale(
    pygame.image.load(f"assets/ghost_images/orange.png"), (width, height)
)

# Red ghost
red_ghost_amount = 1
red_ghost_x = []
red_ghost_y = []
red_ghost_direction = []
for _ in range(red_ghost_amount):
    red_ghost_direction.append(0)
red_ghost = pygame.transform.scale(
    pygame.image.load(f"assets/ghost_images/red.png"), (width, height)
)


def draw_board(lock):
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == 1:
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(
                        row * width + 0.5 * width,
                        col * height + 100,
                        width - 1,
                        height - 1,
                    ),
                )
            if board[row][col] == 2:
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(
                        row * width + 0.5 * width,
                        col * height + 100,
                        width - 1,
                        height - 1,
                    ),
                )
            if board[row][col] == -1:
                screen.blit(pink_ghost, (row * width + 0.5 * width, col * height + 100))
            if board[row][col] == -2:
                screen.blit(
                    orange_ghost, (row * width + 0.5 * width, col * height + 100)
                )
            if board[row][col] == -3:
                screen.blit(red_ghost, (row * width + 0.5 * width, col * height + 100))

    with lock:
        eat_ghost()


def draw_player():
    if direction == 0:
        screen.blit(player_images[counter // 1], (player_x, player_y))
    elif direction == 1:
        screen.blit(
            pygame.transform.flip(player_images[counter // 1], True, False),
            (player_x, player_y),
        )
    elif direction == 2:
        screen.blit(
            pygame.transform.rotate(player_images[counter // 1], 90),
            (player_x, player_y),
        )
    elif direction == 3:
        screen.blit(
            pygame.transform.rotate(player_images[counter // 1], -90),
            (player_x, player_y),
        )


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
        if playery > HEIGHT - 2 * height:
            playery -= height

    return playerx, playery


def fill_path():
    global fill_percent
    if board[int(player_x / width)][int((player_y - 5 * height) / height)] == 0:
        board[int(player_x / width)][int((player_y - 5 * height) / height)] = 2
    np_array = np.array(board)
    np_structure = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    labeled_array, num_features = label(np_array <= 0, structure=np_structure)
    for el in range(1, num_features + 1):
        w = np.where(labeled_array == el)
        a = list(zip(*w))
        for x, y in a:
            if board[x][y] == -1 or board[x][y] == -2 or board[x][y] == -3:
                break
        else:
            for x, y in a:
                board[x][y] = 1
            two_to_one()
            fill_percent = fill_counter()
            is_win(fill_percent)

    if board[int(player_x / width)][int((player_y - 5 * height) / height)] == 1:
        pass


def two_to_one():
    for row in range(x_tiles):
        for col in range(y_tiles):
            if board[row][col] == 2:
                board[row][col] = 1


def fill_counter():
    count = 0
    for row in range(x_tiles):
        for col in range(y_tiles):
            if board[row][col] == 1:
                count += 1
    return count * 100 // (x_tiles * y_tiles)


def is_win(filling):
    global game_over
    global winner
    if filling >= 80:
        game_over = True
        winner = True


def restart_board():
    global eaten_pink_ghosts
    global pink_ghost_amount
    for row in range(x_tiles - 1):
        for col in range(y_tiles - 1):
            if row != 0 and col != 0 and row != x_tiles - 1 and col != y_tiles - 1:
                board[row][col] = 0

    for _ in range(eaten_pink_ghosts):
        pink_ghost_direction.append(0)
    draw_pink(eaten_pink_ghosts)
    pink_ghost_amount = pink_ghost_amount + eaten_pink_ghosts
    eaten_pink_ghosts = 0


def draw_pink(amount):
    for x in range(amount):
        row = 0
        col = 0
        while board[row][col] != 0:
            row = random.randint(0, 43)
            col = random.randint(0, 28)

        board[row][col] = -1
        pink_ghost_x.append(row)
        pink_ghost_y.append(col)


def draw_orange(amount):
    global orange_ghost_direction
    for x in range(amount):
        row = 0
        col = 0
        while board[row][col] != 0 or (
            board[row + 1][col] != 1
            and board[row + 1][col + 1] != 1
            and board[row][col + 1] != 1
            and board[row - 1][col] != 1
            and board[row - 1][col - 1] != 1
            and board[row][col - 1] != 1
            and board[row + 1][col - 1] != 1
            and board[row - 1][col + 1] != 1
        ):
            row = random.randint(0, 43)
            col = random.randint(0, 28)

        board[row][col] = -2
        orange_ghost_x.append(row)
        orange_ghost_y.append(col)

        if board[row - 1][col] == 1:
            orange_ghost_direction.append(1)
        elif board[row][col - 1] == 1:
            orange_ghost_direction.append(2)
        elif board[row + 1][col] == 1:
            orange_ghost_direction.append(3)
        else:
            orange_ghost_direction.append(0)


def draw_red(amount):
    for x in range(amount):
        row = 0
        col = 0
        while board[row][col] != 0:
            row = random.randint(0, 43)
            col = random.randint(0, 28)

        board[row][col] = -3
        red_ghost_x.append(row)
        red_ghost_y.append(col)


def lose_life():
    global lives
    global game_over
    global player_y
    global player_x

    for row in range(x_tiles):
        for col in range(y_tiles):
            if board[row][col] == 2:
                board[row][col] = 0
    lives = lives - 1
    player_y = 100
    player_x = 0.5 * width
    if lives < 1:
        game_over = True


def move_pink(stop):
    if not stop:
        for el in range(pink_ghost_amount):
            if (
                board[pink_ghost_x[el] + 1][pink_ghost_y[el]] == 1
                and board[pink_ghost_x[el] - 1][pink_ghost_y[el]] == 1
            ):
                if (
                    board[pink_ghost_x[el] + 1][pink_ghost_y[el] + 1] == 0
                    or board[pink_ghost_x[el] - 1][pink_ghost_y[el] + 1] == 0
                ):
                    board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                    board[pink_ghost_x[el]][pink_ghost_y[el] + 1] = -1
                    pink_ghost_y[el] += 1
                    pink_ghost_direction[el] = 1
                else:
                    board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                    board[pink_ghost_x[el]][pink_ghost_y[el] - 1] = -1
                    pink_ghost_y[el] -= 1
                    pink_ghost_direction[el] = 0

            if (
                board[pink_ghost_x[el]][pink_ghost_y[el] + 1] == 1
                and board[pink_ghost_x[el]][pink_ghost_y[el] - 1] == 1
            ):
                if (
                    board[pink_ghost_x[el] + 1][pink_ghost_y[el] + 1] == 0
                    or board[pink_ghost_x[el] + 1][pink_ghost_y[el] - 1] == 0
                ):
                    board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                    board[pink_ghost_x[el] + 1][pink_ghost_y[el]] = -1
                    pink_ghost_x[el] += 1
                    pink_ghost_direction[el] = 0
                else:
                    board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                    board[pink_ghost_x[el] - 1][pink_ghost_y[el]] = -1
                    pink_ghost_x[el] -= 1
                    pink_ghost_direction[el] = 3

            if (
                pink_ghost_direction[el] == 0
                and board[pink_ghost_x[el] + 1][pink_ghost_y[el] - 1] == 2
            ):
                lose_life()
            elif (
                pink_ghost_direction[el] == 0
                and board[pink_ghost_x[el] + 1][pink_ghost_y[el] - 1] != 1
            ):
                board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                board[pink_ghost_x[el] + 1][pink_ghost_y[el] - 1] = -1
                pink_ghost_x[el] += 1
                pink_ghost_y[el] -= 1
            elif (
                pink_ghost_direction[el] == 0
                and board[pink_ghost_x[el] + 1][pink_ghost_y[el] - 1] == 1
            ):
                if board[pink_ghost_x[el]][pink_ghost_y[el] - 1] == 1:
                    pink_ghost_direction[el] = 1
                elif board[pink_ghost_x[el] + 1][pink_ghost_y[el]] == 1:
                    pink_ghost_direction[el] = 3
                else:
                    pink_ghost_direction[el] = 2

            if (
                pink_ghost_direction[el] == 1
                and board[pink_ghost_x[el] + 1][pink_ghost_y[el] + 1] == 2
            ):
                lose_life()
            elif (
                pink_ghost_direction[el] == 1
                and board[pink_ghost_x[el] + 1][pink_ghost_y[el] + 1] != 1
            ):
                board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                board[pink_ghost_x[el] + 1][pink_ghost_y[el] + 1] = -1
                pink_ghost_x[el] += 1
                pink_ghost_y[el] += 1
            elif (
                pink_ghost_direction[el] == 1
                and board[pink_ghost_x[el] + 1][pink_ghost_y[el] + 1] == 1
            ):
                if board[pink_ghost_x[el]][pink_ghost_y[el] + 1] == 1:
                    pink_ghost_direction[el] = 0
                elif board[pink_ghost_x[el] + 1][pink_ghost_y[el]] == 1:
                    pink_ghost_direction[el] = 2
                else:
                    pink_ghost_direction[el] = 3

            if (
                pink_ghost_direction[el] == 2
                and board[pink_ghost_x[el] - 1][pink_ghost_y[el] + 1] == 2
            ):
                lose_life()
            elif (
                pink_ghost_direction[el] == 2
                and board[pink_ghost_x[el] - 1][pink_ghost_y[el] + 1] != 1
            ):
                board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                board[pink_ghost_x[el] - 1][pink_ghost_y[el] + 1] = -1
                pink_ghost_x[el] -= 1
                pink_ghost_y[el] += 1
            elif (
                pink_ghost_direction[el] == 2
                and board[pink_ghost_x[el] - 1][pink_ghost_y[el] + 1] == 1
            ):
                if board[pink_ghost_x[el]][pink_ghost_y[el] + 1] == 1:
                    pink_ghost_direction[el] = 3
                elif board[pink_ghost_x[el] - 1][pink_ghost_y[el]] == 1:
                    pink_ghost_direction[el] = 1
                else:
                    pink_ghost_direction[el] = 0

            if (
                pink_ghost_direction[el] == 3
                and board[pink_ghost_x[el] - 1][pink_ghost_y[el] - 1] == 2
            ):
                lose_life()
            elif (
                pink_ghost_direction[el] == 3
                and board[pink_ghost_x[el] - 1][pink_ghost_y[el] - 1] != 1
            ):
                board[pink_ghost_x[el]][pink_ghost_y[el]] = 0
                board[pink_ghost_x[el] - 1][pink_ghost_y[el] - 1] = -1
                pink_ghost_x[el] -= 1
                pink_ghost_y[el] -= 1
            elif (
                pink_ghost_direction[el] == 3
                and board[pink_ghost_x[el] - 1][pink_ghost_y[el] - 1] == 1
            ):
                if board[pink_ghost_x[el]][pink_ghost_y[el] - 1] == 1:
                    pink_ghost_direction[el] = 2
                elif board[pink_ghost_x[el] - 1][pink_ghost_y[el]] == 1:
                    pink_ghost_direction[el] = 0
                else:
                    pink_ghost_direction[el] = 1


def move_orange(stop):
    if not stop:
        for el in range(orange_ghost_amount):
            if (
                orange_ghost_direction[el] == 0
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el]] == 2
            ):
                lose_life()
            elif (
                orange_ghost_direction[el] == 0
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el]] == 1
            ):
                orange_ghost_direction[el] = 3
            elif (
                orange_ghost_direction[el] == 0
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el] + 1] == 1
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el] + 1] == 1
            ):
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el] + 1][orange_ghost_y[el]] = -2
                orange_ghost_x[el] += 1
            elif (
                orange_ghost_direction[el] == 0
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el] + 1] == 1
                and board[orange_ghost_x[el]][orange_ghost_y[el] + 1] == 0
            ):
                orange_ghost_direction[el] = 1
            elif orange_ghost_direction[el] == 0:
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el] + 1][orange_ghost_y[el]] = -2
                orange_ghost_x[el] += 1

            if (
                orange_ghost_direction[el] == 1
                and board[orange_ghost_x[el]][orange_ghost_y[el] + 1] == 2
            ):
                lose_life()
            elif (
                orange_ghost_direction[el] == 1
                and board[orange_ghost_x[el]][orange_ghost_y[el] + 1] == 1
            ):
                orange_ghost_direction[el] = 0
            elif (
                orange_ghost_direction[el] == 1
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el] - 1] == 1
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el] + 1] == 1
            ):
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el]][orange_ghost_y[el] + 1] = -2
                orange_ghost_y[el] += 1
            elif (
                orange_ghost_direction[el] == 1
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el] - 1] == 1
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el]] == 0
            ):
                orange_ghost_direction[el] = 2
            elif orange_ghost_direction[el] == 1:
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el]][orange_ghost_y[el] + 1] = -2
                orange_ghost_y[el] += 1

            if (
                orange_ghost_direction[el] == 2
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el]] == 2
            ):
                lose_life()
            elif (
                orange_ghost_direction[el] == 2
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el]] == 1
            ):
                orange_ghost_direction[el] = 1
            elif (
                orange_ghost_direction[el] == 2
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el] - 1] == 1
                and board[orange_ghost_x[el] - 1][orange_ghost_y[el] - 1] == 1
            ):
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el] - 1][orange_ghost_y[el]] = -2
                orange_ghost_x[el] -= 1
            elif (
                orange_ghost_direction[el] == 2
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el] - 1] == 1
                and board[orange_ghost_x[el]][orange_ghost_y[el] - 1] == 0
            ):
                orange_ghost_direction[el] = 3
            elif orange_ghost_direction[el] == 2:
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el] - 1][orange_ghost_y[el]] = -2
                orange_ghost_x[el] -= 1

            if (
                orange_ghost_direction[el] == 3
                and board[orange_ghost_x[el]][orange_ghost_y[el] - 1] == 2
            ):
                lose_life()
            elif (
                orange_ghost_direction[el] == 3
                and board[orange_ghost_x[el]][orange_ghost_y[el] - 1] == 1
            ):
                orange_ghost_direction[el] = 2
            elif (
                orange_ghost_direction[el] == 2
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el] - 1] == 1
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el] + 1] == 1
            ):
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el]][orange_ghost_y[el] - 1] = -2
                orange_ghost_y[el] -= 1
            elif (
                orange_ghost_direction[el] == 3
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el] + 1] == 1
                and board[orange_ghost_x[el] + 1][orange_ghost_y[el]] == 0
            ):
                orange_ghost_direction[el] = 0
            elif orange_ghost_direction[el] == 3:
                board[orange_ghost_x[el]][orange_ghost_y[el]] = 0
                board[orange_ghost_x[el]][orange_ghost_y[el] - 1] = -2
                orange_ghost_y[el] -= 1


def move_red(stop):
    if not stop:
        for el in range(red_ghost_amount):
            if (
                board[red_ghost_x[el] + 1][red_ghost_y[el]] == 1
                and board[red_ghost_x[el] - 1][red_ghost_y[el]] == 1
            ):
                if (
                    board[red_ghost_x[el] + 1][red_ghost_y[el] + 1] == 0
                    or board[red_ghost_x[el] - 1][red_ghost_y[el] + 1] == 0
                ):
                    board[red_ghost_x[el]][red_ghost_y[el]] = 0
                    board[red_ghost_x[el]][red_ghost_y[el] + 1] = -1
                    red_ghost_y[el] += 1
                    red_ghost_direction[el] = 1
                else:
                    board[red_ghost_x[el]][red_ghost_y[el]] = 0
                    board[red_ghost_x[el]][red_ghost_y[el] - 1] = -1
                    red_ghost_y[el] -= 1
                    red_ghost_direction[el] = 0

            if (
                board[red_ghost_x[el]][red_ghost_y[el] + 1] == 1
                and board[red_ghost_x[el]][red_ghost_y[el] - 1] == 1
            ):
                if (
                    board[red_ghost_x[el] + 1][red_ghost_y[el] + 1] == 0
                    or board[red_ghost_x[el] + 1][red_ghost_y[el] - 1] == 0
                ):
                    board[red_ghost_x[el]][red_ghost_y[el]] = 0
                    board[red_ghost_x[el] + 1][red_ghost_y[el]] = -1
                    red_ghost_x[el] += 1
                    red_ghost_direction[el] = 0
                else:
                    board[red_ghost_x[el]][red_ghost_y[el]] = 0
                    board[red_ghost_x[el] - 1][red_ghost_y[el]] = -1
                    red_ghost_x[el] -= 1
                    red_ghost_direction[el] = 3

            if (
                red_ghost_direction[el] == 0
                and board[red_ghost_x[el] + 1][red_ghost_y[el] - 1] == 2
            ):
                lose_life()
            elif (
                red_ghost_direction[el] == 0
                and board[red_ghost_x[el] + 1][red_ghost_y[el] - 1] != 1
            ):
                board[red_ghost_x[el]][red_ghost_y[el]] = 0
                board[red_ghost_x[el] + 1][red_ghost_y[el] - 1] = -3
                red_ghost_x[el] += 1
                red_ghost_y[el] -= 1
            elif (
                red_ghost_direction[el] == 0
                and board[red_ghost_x[el] + 1][red_ghost_y[el] - 1] == 1
            ):
                if board[red_ghost_x[el]][red_ghost_y[el] - 1] == 1:
                    red_ghost_direction[el] = 1
                    if red_ghost_y[el] - 1 != 0:
                        board[red_ghost_x[el]][red_ghost_y[el] - 1] = 0
                elif board[red_ghost_x[el] + 1][red_ghost_y[el]] == 1:
                    red_ghost_direction[el] = 3
                    if red_ghost_x[el] + 1 != x_tiles - 1:
                        board[red_ghost_x[el] + 1][red_ghost_y[el]] = 0
                else:
                    red_ghost_direction[el] = 2
                    if red_ghost_y[el] - 1 != 0 and red_ghost_x[el] + 1 != x_tiles - 1:
                        board[red_ghost_x[el] + 1][red_ghost_y[el] - 1] = 0

            if (
                red_ghost_direction[el] == 1
                and board[red_ghost_x[el] + 1][red_ghost_y[el] + 1] == 2
            ):
                lose_life()
            elif (
                red_ghost_direction[el] == 1
                and board[red_ghost_x[el] + 1][red_ghost_y[el] + 1] != 1
            ):
                board[red_ghost_x[el]][red_ghost_y[el]] = 0
                board[red_ghost_x[el] + 1][red_ghost_y[el] + 1] = -3
                red_ghost_x[el] += 1
                red_ghost_y[el] += 1
            elif (
                red_ghost_direction[el] == 1
                and board[red_ghost_x[el] + 1][red_ghost_y[el] + 1] == 1
            ):
                if board[red_ghost_x[el]][red_ghost_y[el] + 1] == 1:
                    red_ghost_direction[el] = 0
                    if red_ghost_y[el] + 1 != y_tiles - 1:
                        board[red_ghost_x[el]][red_ghost_y[el] + 1] = 0
                elif board[red_ghost_x[el] + 1][red_ghost_y[el]] == 1:
                    red_ghost_direction[el] = 2
                    if red_ghost_x[el] + 1 != x_tiles - 1:
                        board[red_ghost_x[el] + 1][red_ghost_y[el]] = 0
                else:
                    red_ghost_direction[el] = 3
                    if (
                        red_ghost_y[el] + 1 != y_tiles - 1
                        and red_ghost_x[el] + 1 != x_tiles - 1
                    ):
                        board[red_ghost_x[el] + 1][red_ghost_y[el] + 1] = 0

            if (
                red_ghost_direction[el] == 2
                and board[red_ghost_x[el] - 1][red_ghost_y[el] + 1] == 2
            ):
                lose_life()
            elif (
                red_ghost_direction[el] == 2
                and board[red_ghost_x[el] - 1][red_ghost_y[el] + 1] != 1
            ):
                board[red_ghost_x[el]][red_ghost_y[el]] = 0
                board[red_ghost_x[el] - 1][red_ghost_y[el] + 1] = -3
                red_ghost_x[el] -= 1
                red_ghost_y[el] += 1
            elif (
                red_ghost_direction[el] == 2
                and board[red_ghost_x[el] - 1][red_ghost_y[el] + 1] == 1
            ):
                if board[red_ghost_x[el]][red_ghost_y[el] + 1] == 1:
                    red_ghost_direction[el] = 3
                    if red_ghost_y[el] + 1 != y_tiles - 1:
                        board[red_ghost_x[el]][red_ghost_y[el] + 1] = 0
                elif board[red_ghost_x[el] - 1][red_ghost_y[el]] == 1:
                    red_ghost_direction[el] = 1
                    if red_ghost_x[el] - 1 != 0:
                        board[red_ghost_x[el] - 1][red_ghost_y[el]] = 0
                else:
                    red_ghost_direction[el] = 0
                    if red_ghost_y[el] + 1 != y_tiles - 1 and red_ghost_x[el] - 1 != 0:
                        board[red_ghost_x[el] - 1][red_ghost_y[el] + 1] = 0

            if (
                red_ghost_direction[el] == 3
                and board[red_ghost_x[el] - 1][red_ghost_y[el] - 1] == 2
            ):
                lose_life()
            elif (
                red_ghost_direction[el] == 3
                and board[red_ghost_x[el] - 1][red_ghost_y[el] - 1] != 1
            ):
                board[red_ghost_x[el]][red_ghost_y[el]] = 0
                board[red_ghost_x[el] - 1][red_ghost_y[el] - 1] = -3
                red_ghost_x[el] -= 1
                red_ghost_y[el] -= 1
            elif (
                red_ghost_direction[el] == 3
                and board[red_ghost_x[el] - 1][red_ghost_y[el] - 1] == 1
            ):
                if board[red_ghost_x[el]][red_ghost_y[el] - 1] == 1:
                    red_ghost_direction[el] = 2
                    if red_ghost_y[el] - 1 != 0:
                        board[red_ghost_x[el]][red_ghost_y[el] - 1] = 0
                elif board[red_ghost_x[el] - 1][red_ghost_y[el]] == 1:
                    red_ghost_direction[el] = 0
                    if red_ghost_x[el] - 1 != 0:
                        board[red_ghost_x[el] - 1][red_ghost_y[el]] = 0
                else:
                    red_ghost_direction[el] = 1
                    if red_ghost_y[el] - 1 != 0 and red_ghost_x[el] - 1 != 0:
                        board[red_ghost_x[el] - 1][red_ghost_y[el] - 1] = 0


def move_when_keys(stop):
    global player_x
    global player_y
    if not stop:
        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_RIGHT]
            or keys[pygame.K_LEFT]
            or keys[pygame.K_UP]
            or keys[pygame.K_DOWN]
        ):
            player_x, player_y = move_player(player_x, player_y)


def display_text():
    global lives
    global point_count
    global fill_percent
    text_lives = font.render("Lives: " + str(lives), True, (255, 255, 0))
    text_lives_rect = text_lives.get_rect()
    text_lives_rect.center = (100, 50)

    text_fill = font.render("Filled: " + str(fill_percent) + "%", True, (255, 255, 0))
    text_fill_rect = text_lives.get_rect()
    text_fill_rect.center = (750, 50)

    screen.blit(text_lives, text_lives_rect)
    screen.blit(text_fill, text_fill_rect)


def eat_ghost():
    global pink_ghost_amount
    global pink_ghost_direction
    global pink_ghost_y
    global pink_ghost_x
    global eaten_pink_ghosts
    for i in range(pink_ghost_amount):
        for j in range(orange_ghost_amount):
            if (
                pink_ghost_y[i] == orange_ghost_y[j]
                and pink_ghost_x[i] == orange_ghost_x[j]
            ):
                pink_ghost_x.pop(i)
                pink_ghost_y.pop(i)
                pink_ghost_direction.pop(i)
                pink_ghost_amount = pink_ghost_amount - 1
                eaten_pink_ghosts = eaten_pink_ghosts + 1
                return

        for j in range(red_ghost_amount):
            if pink_ghost_y[i] == red_ghost_y[j] and pink_ghost_x[i] == red_ghost_x[j]:
                pink_ghost_x.pop(i)
                pink_ghost_y.pop(i)
                pink_ghost_direction.pop(i)
                pink_ghost_amount = pink_ghost_amount - 1
                eaten_pink_ghosts = eaten_pink_ghosts + 1
                return


def main():
    global lives
    global game_over
    global winner
    global fill_percent
    global player_x
    global player_y
    global counter
    global direction
    refreshed = False
    stop = False
    run = True
    draw_orange(orange_ghost_amount)
    draw_red(red_ghost_amount)
    draw_pink(pink_ghost_amount)
    lock = threading.Lock()
    while run:
        timer.tick(fps)
        if counter < 3:
            counter += 1
        else:
            counter = 0
        screen.fill("black")
        t_board = threading.Thread(target=draw_board, args=(lock,)).start()
        display_text()
        draw_player()
        t_pink = threading.Thread(target=move_pink(stop)).start()
        t_orange = threading.Thread(target=move_orange(stop)).start()
        t_red = threading.Thread(target=move_red(stop)).start()
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    stop = False
                    game_over = False
                    player_y = 100
                    player_x = 0.5 * width
                    winner = False
                    refreshed = True
                    restart_board()
                    fill_percent = 0

        t2 = threading.Thread(target=move_when_keys(stop)).start()

        if not refreshed:
            fill_path()
        elif refreshed:
            lives = 3
            refreshed = False

        if game_over:
            if winner:
                game_over_text = font.render(
                    "You won! Press space to restart", True, "white"
                )
                screen.blit(game_over_text, (200, 300))
                stop = True
            else:
                game_over_text = font.render(
                    "Game over! Press space to restart", True, "white"
                )
                screen.blit(game_over_text, (200, 300))
                stop = True

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
