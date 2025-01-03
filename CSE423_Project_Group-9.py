from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

game_over = False

def display_game_over_message():
    print("Game Completed! You reached the goal.")
    global game_over
    game_over = True


maze_grid = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


spawn_x, spawn_y = 30, 30
spawn_radius = 20
player_x, player_y = spawn_x, spawn_y
player_radius = 5


goal_x, goal_y = 270, 250
goal_radius = 8


step_size = 20


difficulty_settings = {
    "EASY": {"num_enemies": 2, "enemy_speed": 1},
    "NORMAL": {"num_enemies": 3, "enemy_speed": 2},
    "HARD": {"num_enemies": 5, "enemy_speed": 3},
}


print("Select Difficulty: EASY, NORMAL, HARD")
while True:
    difficulty = input("Enter difficulty: ").upper()
    if difficulty in difficulty_settings:
        break
    print("Invalid choice. Please select EASY, NORMAL, or HARD.")


NUM_ENEMIES = difficulty_settings[difficulty]["num_enemies"]
ENEMY_SPEED = difficulty_settings[difficulty]["enemy_speed"]

print(f"You selected {difficulty}. Number of Enemies: {NUM_ENEMIES}, Enemy Speed: {ENEMY_SPEED}")


player_health = 3
max_health = 3


health_pickups = []


freeze_pickups = []


player_accessible_cells = [
    (col * 20 + 10, row * 20 + 10)
    for row in range(len(maze_grid))
    for col in range(len(maze_grid[row]))
    if maze_grid[row][col] == 0
]


for _ in range(2):
    if player_accessible_cells:
        x, y = random.choice(player_accessible_cells)
        player_accessible_cells.remove((x, y))
        health_pickups.append({"x": x, "y": y, "radius": 5, "active": True})

for _ in range(1):
    if player_accessible_cells:
        x, y = random.choice(player_accessible_cells)
        player_accessible_cells.remove((x, y))
        freeze_pickups.append({"x": x, "y": y, "radius": 5, "active": True})


enemies = []
for _ in range(NUM_ENEMIES):
    while True:
        rand_x = random.randint(1, 14) * 20
        rand_y = random.randint(1, 14) * 20
        col, row = rand_x // 20, rand_y // 20
        if maze_grid[row][col] == 0:
            enemy = {
                "x": rand_x,
                "y": rand_y,
                "radius": 6,
                "dx": random.choice([-1, 1]) * ENEMY_SPEED,
                "dy": random.choice([-1, 1]) * ENEMY_SPEED,
                "frozen": False,
                "freeze_time": 0,
            }
            enemies.append(enemy)
            break


def midpoint_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points


def midpoint_circle(cx, cy, radius):
    points = []
    x = 0
    y = radius
    d = 1 - radius

    points.extend(circle_symmetric_points(cx, cy, x, y))

    while x < y:
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
        points.extend(circle_symmetric_points(cx, cy, x, y))

    return points

def circle_symmetric_points(cx, cy, x, y):
    return [
        (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
        (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x),
    ]

def draw_pixels(points, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for x, y in points:
        glVertex2f(x, y)
    glEnd()

def draw_maze():
    for row in range(len(maze_grid)):
        for col in range(len(maze_grid[row])):
            if maze_grid[row][col] == 1:
                x0, y0 = col * 20, row * 20
                x1, y1 = x0 + 20, y0
                x2, y2 = x0, y0 + 20
                x3, y3 = x1, y2
                draw_pixels(midpoint_line(x0, y0, x1, y1), (1.0, 1.0, 1.0))
                draw_pixels(midpoint_line(x1, y1, x3, y3), (1.0, 1.0, 1.0))
                draw_pixels(midpoint_line(x3, y3, x2, y2), (1.0, 1.0, 1.0))
                draw_pixels(midpoint_line(x2, y2, x0, y0), (1.0, 1.0, 1.0))

def draw_circle(cx, cy, radius, color):
    points = midpoint_circle(cx, cy, radius)
    draw_pixels(points, color)

def can_move(x, y):
    col, row = x // 20, y // 20
    if row < 0 or col < 0 or row >= len(maze_grid) or col >= len(maze_grid[0]):
        return False
    return maze_grid[row][col] == 0


def move_enemies():
    for enemy in enemies:
        if enemy["frozen"]:
            continue
        next_x = enemy["x"] + enemy["dx"]
        next_y = enemy["y"] + enemy["dy"]
        if not can_move(next_x, enemy["y"]):
            enemy["dx"] = -enemy["dx"]
        else:
            enemy["x"] += enemy["dx"]
        if not can_move(enemy["x"], next_y):
            enemy["dy"] = -enemy["dy"]
        else:
            enemy["y"] += enemy["dy"]

def check_collision():
    global player_x, player_y, game_over, player_health


    in_spawn_area = (player_x - spawn_x)**2 + (player_y - spawn_y)**2 <= spawn_radius**2
    if in_spawn_area:
        return


    for enemy in enemies:
        dist_sq = (player_x - enemy["x"])**2 + (player_y - enemy["y"])**2
        if dist_sq <= (player_radius + enemy["radius"])**2:
            player_health -= 1
            print(f"Health: {player_health}")
            if player_health <= 0:
                print("Game Over! You lost all your health.")
                game_over = True
            player_x, player_y = spawn_x, spawn_y
            return


    for pickup in health_pickups:
        if pickup["active"]:
            dist_sq = (player_x - pickup["x"])**2 + (player_y - pickup["y"])**2
            if dist_sq <= (player_radius + pickup["radius"])**2:
                player_health = min(player_health + 1, max_health)
                pickup["active"] = False
                print(f"Health: {player_health}")


    for pickup in freeze_pickups:
        if pickup["active"]:
            dist_sq = (player_x - pickup["x"])**2 + (player_y - pickup["y"])**2
            if dist_sq <= (player_radius + pickup["radius"])**2:
                pickup["active"] = False
                freeze_enemies_for_time(3)
                print("Enemies frozen for 3 seconds!")


    dist_to_goal_sq = (player_x - goal_x)**2 + (player_y - goal_y)**2
    if dist_to_goal_sq <= (player_radius + goal_radius)**2:
        display_game_over_message()


def draw_health_pickups():
    for pickup in health_pickups:
        if pickup["active"]:
            draw_circle(pickup["x"], pickup["y"], pickup["radius"], (0.0, 1.0, 1.0))

def draw_freeze_pickups():
    for pickup in freeze_pickups:
        if pickup["active"]:
            draw_circle(pickup["x"], pickup["y"], pickup["radius"], (0.0, 0.0, 1.0))

def draw_health_bar(health, max_health):
    bar_start_x, bar_start_y = 20, 280
    bar_segment_length = 20
    bar_height = 5

    for i in range(max_health):
        segment_start_x = bar_start_x + i * bar_segment_length
        segment_end_x = segment_start_x + bar_segment_length
        color = (0.0, 1.0, 0.0) if i < health else (1.0, 0.0, 0.0)

        top_line = midpoint_line(segment_start_x, bar_start_y, segment_end_x, bar_start_y)
        bottom_line = midpoint_line(segment_start_x, bar_start_y - bar_height, segment_end_x, bar_start_y - bar_height)

        left_line = midpoint_line(segment_start_x, bar_start_y, segment_start_x, bar_start_y - bar_height)
        right_line = midpoint_line(segment_end_x, bar_start_y, segment_end_x, bar_start_y - bar_height)

        draw_pixels(top_line + bottom_line + left_line + right_line, color)

def freeze_enemies_for_time(seconds):
    freeze_end_time = time.time() + seconds
    for enemy in enemies:
        enemy["frozen"] = True
        enemy["freeze_time"] = freeze_end_time

def update_enemy_freeze_status():
    current_time = time.time()
    for enemy in enemies:
        if enemy["frozen"] and current_time > enemy["freeze_time"]:
            enemy["frozen"] = False

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_maze()
    draw_circle(player_x, player_y, player_radius, (0.0, 1.0, 0.0))
    draw_circle(goal_x, goal_y, goal_radius, (1.0, 0.0, 0.0))
    for enemy in enemies:
        draw_circle(enemy["x"], enemy["y"], enemy["radius"], (1.0, 1.0, 0.0))
    draw_health_pickups()
    draw_freeze_pickups()
    draw_health_bar(player_health, max_health)
    glutSwapBuffers()

def keyboard(key, x, y):
    global player_x, player_y
    if not game_over:
        next_x, next_y = player_x, player_y
        if key == b"w":
            next_y += step_size
        elif key == b"s":
            next_y -= step_size
        elif key == b"a":
            next_x -= step_size
        elif key == b"d":
            next_x += step_size

        if can_move(next_x, next_y):
            player_x, player_y = next_x, next_y


def update(value):
    if not game_over:
        move_enemies()
        check_collision()
        update_enemy_freeze_status()
        glutPostRedisplay()
        glutTimerFunc(1000 // 60, update, 0)



glutInit()
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Maze Game")
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutTimerFunc(1000 // 60, update, 0)
glClearColor(0.0, 0.0, 0.0, 1.0)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, 300, 0, 300, -1, 1)

glutMainLoop()

