import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 900
ARENA_SIZE = 800
REQUIRED_KEYS = 5
EXIT_WIDTH = 200

game_state = "PLAYING"
keys_state = {}
key_rotation_angle = 0.0
pulse_timer = 0.0

player = {}
cam_angle = 90
top_down_view = False

enemies_patrol = []
enemies_turret = []
enemies_ghost = []
pickups = []
breakables = []
projectiles = []
particles = []

maze_walls = [[0, ARENA_SIZE, ARENA_SIZE * 2, 20, 80],
              [0, -ARENA_SIZE, ARENA_SIZE * 2, 20, 80],
              [-ARENA_SIZE, 0, 20, ARENA_SIZE * 2, 80],
              [ARENA_SIZE, 0, 20, ARENA_SIZE * 2, 80],
              [-300, 200, 20, 300, 60],
              [350, 300, 400, 20, 60],
              [400, -200, 20, 400, 60],
              [-450, 60, 320, 20, 60],
              [-200, -450, 20, 300, 60],
              [-200, -300, 300, 20, 60],
              [300, 400, 20, 200, 60],
              [-125, 550, 20, 500, 60]]

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    if game_state == "PLAYING":
        glColor3f(1.0, 1.0, 1.0)
    elif game_state == "WON":
        glColor3f(0.0, 0.75, 0.0)
    else:
        glColor3f(0.5, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_environment():
    glBegin(GL_QUADS)
    cell_size = 100
    steps = int(ARENA_SIZE / cell_size)
    for i in range(-steps, steps):
        for j in range(-steps, steps):
            if (i + j) % 2 == 0:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(0.5, 0.5, 0.5)
            x1, y1 = i * cell_size, j * cell_size
            x2, y2 = (i + 1) * cell_size, (j + 1) * cell_size
            glNormal3f(0, 0, 1)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()

    glColor3f(0.35, 0.35, 0.45)
    for wx, wy, ww, wl, wh in maze_walls:
        glPushMatrix()
        glTranslatef(wx, wy, wh / 2)
        glScalef(ww, wl, wh)
        glutSolidCube(1.0)
        glPopMatrix()

    if player["keys_collected"] < REQUIRED_KEYS:
        glColor3f(0.9, 0.1, 0.1)
    else:
        glColor3f(0.1, 0.9, 0.1)

    glPushMatrix()
    glTranslatef(50, ARENA_SIZE - 2, 30)
    glScalef(1.0, 0.175, 0.51)
    glutSolidCube(EXIT_WIDTH)
    glPopMatrix()

def draw_player():
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(player["x"], player["y"], player["z"])
    glRotatef(math.degrees(player["angle"]), 0, 0, 1)
    if player["cheat_invulnerable"]:
        glColor3f(0.3, 1.0, 0.3)
    elif game_state == "GAME_OVER":
        glColor3f(1.0, 0.0, 0.0)
    else:
        glColor3f(0.35, 0.45, 1.0)
    # Main Body
    glPushMatrix()
    glScalef(1.2, 0.7, 0.5)
    glutSolidCube(30)
    glPopMatrix()

    for wy in [-12, 12]:
        glPushMatrix()
        glTranslatef(0, wy, -5)
        glRotatef(0, 0, 1, 0)
        glColor3f(0.2, 0.2, 0.2)
        gluSphere(quad, 6, 12, 12)
        glPopMatrix()
    if player["turret_mode"]:
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(18, 0, 5)
        glScalef(1.8, 0.3, 0.3)
        glutSolidCube(10)
        glPopMatrix()
    for wy in [-8, 8]:
        glPushMatrix()
        glTranslatef(20, wy, 1.0)
        glColor3f(1.0, 1.0, 1.0)
        gluSphere(quad, 6, 12, 12)
        glTranslatef(3.0, 0.0, 0.0)
        glColor3f(0.1, 0.1, 0.1)
        gluSphere(quad, 4, 12, 12)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(-20, 0, 5)
    glRotatef(-60, 0, 1, 0)
    glRotatef(player["wind_up_angle"], 0, 0, 1)
    if player["cheat_no_windup"]:
        glColor3f(0.0, 1.0, 0.25)
    else:
        glColor3f(0.75, 0.6, 0.0)

    glPushMatrix()
    glTranslatef(0, 0, 2)
    glScalef(1.0, 1.0, 3.0)
    glutSolidCube(4)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 14)
    glRotatef(90, 1, 0, 0)
    glScalef(0.3, 1.0, 2.0)
    glutSolidCube(18)
    glPopMatrix()

    glPopMatrix()

    if player["has_shield"]:
        if player["cheat_invulnerable"]:
            glColor3f(0.2, 1.0, 0.2)
        else:
            glColor3f(0.2, 0.5, 1.0)
        gluSphere(quad, 28, 20, 20)
    glPopMatrix()

def draw_entities():
    hover = math.sin(math.radians(key_rotation_angle * 2.0)) * 4.0
    quad = gluNewQuadric()

    for p in pickups:
        glPushMatrix()
        glTranslatef(p["x"], p["y"], p["z"] + hover)

        if p["type"] == "key":
            glColor3f(1.0, 0.84, 0.0)
            glRotatef(90, 1, 0, 0)
            glRotatef(key_rotation_angle, 0, 1, 0)

            glPushMatrix()
            glTranslatef(0, 0, 10)
            gluSphere(quad, 6, 10, 10)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(0, 0, 0)
            glScalef(1.5, 1.5, 12.0)
            glutSolidCube(1.5)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(3, 0, -4)
            glScalef(4.0, 1.2, 3.0)
            glutSolidCube(1.0)
            glPopMatrix()

        elif p["type"] == "health":
            glColor3f(0.9, 0.1, 0.1)
            gluSphere(quad, 10, 16, 16)
        elif p["type"] == "power":
            glColor3f(0.9, 0.9, 0.0)
            gluSphere(quad, 10, 16, 16)
        elif p["type"] == "shield":
            glColor3f(0.1, 0.5, 0.9)
            gluSphere(quad, 10, 16, 16)
        glPopMatrix()

    for e in enemies_patrol:
        glPushMatrix()
        glColor3f(0.4, 0.2, 0.4)
        glTranslatef(e["x"], e["y"], e["z"])
        glRotatef(math.degrees(e["spin"]), 0, 0, 1)
        gluSphere(quad, 25, 25, 25)
        glColor3f(0.8, 0.2, 0.4)
        for angle in range(0, 360, 90):
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)
            glTranslatef(25, 0, 0)
            glutSolidCube(10)
            glPopMatrix()
        glPopMatrix()

    for e in enemies_turret:
        glPushMatrix()
        glColor3f(0.1, 0.6, 0.3)
        glTranslatef(e["x"], e["y"], e["z"])
        glRotatef(math.degrees(e["angle"]), 0, 0, 1)
        glRotatef(math.degrees(e["spin"]), 1, 0, 0)
        glutSolidCube(25)
        glColor3f(0.6, 0.1, 0.2)
        glTranslatef(15, 0, 0)
        glutSolidCube(12)
        glPopMatrix()

    glColor3f(0.05, 0.05, 0.05)
    for g in enemies_ghost:
        glPushMatrix()
        glTranslatef(g["x"], g["y"], g["z"])
        glScalef(g["scale"], g["scale"], g["scale"])
        gluSphere(quad, 16, 16, 16)
        glPopMatrix()

    glColor3f(0.8, 0.4, 0.1)
    for b in breakables:
        glPushMatrix()
        glTranslatef(b["x"], b["y"], b["z"])
        glutSolidCube(45)
        glPopMatrix()

    for p in projectiles:
        glPushMatrix()
        glTranslatef(p["x"], p["y"], p["z"])
        if p["is_player"]:
            glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(1.0, 0.0, 1.0)
        gluSphere(quad, p["radius"], 10, 10)
        glPopMatrix()

    glDepthMask(GL_FALSE)
    for pt in particles:
        glPushMatrix()
        glTranslatef(pt["x"], pt["y"], pt["z"])
        alpha = max(0.0, pt["life"] / pt["max_life"])
        glColor4f(pt["color"][0], pt["color"][1], pt["color"][2], alpha)
        gluSphere(quad, pt["size"], 8, 8)
        glPopMatrix()
    glDepthMask(GL_TRUE)

def spawn_particles(x, y, z, color_rgb, count=15):
    for _ in range(count):
        angle = random.random() * 2 * math.pi
        spd = random.uniform(0.2, 2.0)
        particles.append({"x": x, "y": y, "z": z, "dx": math.cos(angle) * spd, "dy": math.sin(angle) * spd,
                          "dz": random.uniform(1.0, 4.0), "life": 50, "max_life": 50, "color": color_rgb,
                          "size": random.uniform(3.0, 6.0)})

def update_particles():
    global particles
    surviving_particles = []
    for p in particles:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["z"] += p["dz"]
        p["dz"] -= 0.05
        p["life"] -= 0.5
        if p["life"] > 0:
            surviving_particles.append(p)
    particles = surviving_particles

def init_player():
    global player
    player = {"x": 0.0, "y": 100.0, "z": 15.0, "vz": 0.0, "angle": math.pi / 2, "power": 0.0, "max_power": 100.0,
              "lives": 5, "max_health": 5, "radius": 18.0, "turret_mode": False, "has_shield": False, "keys_collected": 0,
              "wind_up_angle": 0.0, "cheat_invulnerable": False, "cheat_no_windup": False}

def spawn_entities():
    global enemies_patrol, enemies_turret, enemies_ghost, pickups, breakables, projectiles, particles
    particles = []

    enemies_patrol = [
        {"x": -300, "y": 450, "z": 15.0, "start_x": -300, "start_y": 450, "travel_dist": 450, "axis": "x", "speed": 0.5,
            "spin": 0.0, "direction": 1, "radius": 15.0},
        {"x": 550, "y": -50, "z": 15.0, "start_x": 550, "start_y": -50, "travel_dist": 300, "axis": "y", "speed": 0.5,
            "spin": 0.0, "direction": 1, "radius": 15.0},
        {"x": -550, "y": -350, "z": 15.0, "start_x": -550,"start_y": -350, "travel_dist": 250, "axis": "x", "speed": 0.5,
            "spin": 0.0, "direction": 1,"radius": 15.0},
        {"x": 250, "y": -300, "z": 15.0, "start_x": 250, "start_y": -300, "travel_dist": 500, "axis": "y", "speed": 0.5,
            "spin": 0.0, "direction": 1, "radius": 15.0}
    ]

    enemies_turret = [
        {"x": -400, "y": 150, "z": 15.0, "angle": 0.0, "spin": 0.0, "cooldown": 250, "radius": 15.0},
        {"x": 750, "y": -650, "z": 15.0, "angle": 0.0, "spin": 0.0, "cooldown": 250,"radius": 15.0},
        {"x": -300, "y": -450, "z": 15.0, "angle": 0.0, "spin": 0.0, "cooldown": 250,"radius": 15.0}
    ]

    enemies_ghost = [{"x": 800, "y": 800, "z": 40.0, "speed": 0.075, "radius": 15.0, "scale": 1.0}]

    pickups = [
        {"x": -654, "y": 600, "z": 15.0, "type": "key", "radius": 12.0},
        {"x": 600, "y": 675, "z": 15.0, "type": "key", "radius": 12.0},
        {"x": -720, "y": -600, "z": 15.0, "type": "key", "radius": 12.0},
        {"x": 720, "y": -540, "z": 15.0, "type": "key", "radius": 12.0},
        {"x": -125, "y": -425, "z": 15.0, "type": "key", "radius": 12.0},
        {"x": 500, "y": 300, "z": 15.0, "type": "health", "radius": 10.0},
        {"x": 240, "y": -600, "z": 15.0, "type": "health", "radius": 10.0},
        {"x": -180, "y": 700, "z": 15.0, "type": "health", "radius": 10.0},
        {"x": -480, "y": -450, "z": 15.0, "type": "health", "radius": 10.0},
        {"x": 220, "y": -225, "z": 15.0, "type": "power", "radius": 10.0},
        {"x": 120, "y": 525, "z": 15.0, "type": "power", "radius": 10.0},
        {"x": 500, "y": 500, "z": 15.0, "type": "shield", "radius": 10.0},
        {"x": -680, "y": -180, "z": 15.0, "type": "shield", "radius": 10.0}
    ]

    breakables = [{"x": 130, "y": 300, "z": 1.0, "radius": 30.0},
                  {"x": 70, "y": 300, "z": 1.0, "radius": 30.0},
                  {"x": 10, "y": 300, "z": 1.0, "radius": 30.0},
                  {"x": -40, "y": 300, "z": 1.0, "radius": 30.0},
                  {"x": -100, "y": 300, "z": 1.0, "radius": 30.0},
                  {"x": -200, "y": -625, "z": 1.0, "radius": 30.0},
                  {"x": -180, "y": -670, "z": 1.0, "radius": 30.0},
                  {"x": -160, "y": -715, "z": 1.0, "radius": 30.0},
                  {"x": -140, "y": -760, "z": 1.0, "radius": 30.0},
                  {"x": 600, "y": 675, "z": 1.0, "radius": 30.0}
                  ]

    projectiles = []

def reset_game():
    global game_state, key_rotation_angle, cam_angle
    init_player()
    player["cheat_invulnerable"] = False
    player["cheat_no_windup"] = False
    key_rotation_angle = 0.0
    cam_angle = 90
    game_state = "PLAYING"
    spawn_entities()

def check_collision_3d(x1, y1, z1, r1, x2, y2, z2, r2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) < (r1 + r2)

def check_wall_collision(x, y, radius):
    for wx, wy, ww, wl, wh in maze_walls:
        min_x, max_x = wx - ww / 2 - radius, wx + ww / 2 + radius
        min_y, max_y = wy - wl / 2 - radius, wy + wl / 2 + radius
        if min_x <= x <= max_x and min_y <= y <= max_y:
            return True
    return False

def check_box_collision(x, y, radius):
    for b in breakables:
        dist = math.sqrt((x - b["x"]) ** 2 + (y - b["y"]) ** 2)
        if dist < (radius + b["radius"]):
            return True
    return False

def fire_projectile(x, y, z, angle, is_player):
    start_x = x + math.cos(angle) * 25
    start_y = y + math.sin(angle) * 25
    start_z = z + 5

    speed = 4.0 if is_player else 1.0
    projectiles.append({"x": start_x, "y": start_y, "z": start_z, "dx": math.cos(angle) * speed,
                        "dy": math.sin(angle) * speed, "is_player": is_player, "radius": 6.0,})

def player_take_damage(instant_kill=False):
    global game_state
    if player["cheat_invulnerable"]:
        return

    if instant_kill:
        player["lives"] = 0
        spawn_particles(player["x"], player["y"], player["z"], [1.0, 0.6, 0.5], count=50)
        game_state = "GAME_OVER"
        return

    if player["has_shield"]:
        player["has_shield"] = False
        spawn_particles(player["x"], player["y"], player["z"], [0.2, 0.5, 1.0], count=30)
        return

    player["lives"] -= 1
    spawn_particles(player["x"], player["y"], player["z"], [1.0, 0.1, 0.1], count=35)
    if player["lives"] <= 0:
        game_state = "GAME_OVER"

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_WIDTH / WINDOW_HEIGHT, 1, 3500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if top_down_view:
        gluLookAt(player["x"], player["y"], player["z"] + 1100,
                  player["x"], player["y"], player["z"],
                  0, 1, 0)
    else:
        cam_dist = 450
        rad = math.radians(cam_angle)
        cx = player["x"] - math.cos(rad) * cam_dist
        cy = player["y"] - math.sin(rad) * cam_dist
        cz = player["z"] + 450
        gluLookAt(cx, cy, cz,
                  player["x"], player["y"], player["z"],
                  0, 0, 1)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    setup_camera()
    draw_environment()
    draw_player()
    draw_entities()

    draw_text(20, WINDOW_HEIGHT - 40, f"Power: {int(player['power'])} / 100")
    draw_text(20, WINDOW_HEIGHT - 70, f"Lives: {player['lives']}")
    draw_text(20, WINDOW_HEIGHT - 100, f"Keys Collected: {player['keys_collected']} / {REQUIRED_KEYS}",)

    status = []
    if player["turret_mode"]:
        status.append("TURRET MODE ACTIVE (LEFT CLICK TO SHOOT)")
    if player["has_shield"]:
        status.append("SHIELD ACTIVE")
    if player["cheat_invulnerable"]:
        status.append("CHEAT: INVULNERABLE (C)")
    if player["cheat_no_windup"]:
        status.append("CHEAT: NO WIND-UP REQUIRED (V)")
    for i, msg in enumerate(status):
        draw_text(20, WINDOW_HEIGHT - 135 - (i * 25), msg)

    if game_state == "PLAYING":
        draw_text(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 30, "Hold W to Accelerate.",)
        draw_text(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 60, "Hold A/D to Turn.",)
        draw_text(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 90, "Press E to Toggle Turret Mode.",)
    elif game_state == "PAUSED":
        draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 50, "GAME PAUSED! Press P to Resume.",)
    elif game_state == "GAME_OVER":
        draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 50, "GAME OVER! Press R to Restart or Q to Quit.",)
    elif game_state == "WON":
        draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 50, "YOU ESCAPED! YOU WIN! Press Q to Quit.",)

    glutSwapBuffers()

def keyboardDown(key, x, y):
    global top_down_view, game_state, keys_state
    keys_state[key.lower()] = True
    k = key.lower()

    if k == b"r":
        reset_game()

    if k == b"p" and game_state != "GAME_OVER" and game_state != "WON":
        if game_state == "PAUSED":
            game_state = "PLAYING"

        else:
            game_state = "PAUSED"

    if k == b"q" or key == b"\x1b":
            glutLeaveMainLoop()

    if game_state != "PLAYING":
        return

    if k == b"b":
        top_down_view = not top_down_view

    elif k == b"e":
        player["turret_mode"] = not player["turret_mode"]

    elif k == b"c":
        player["cheat_invulnerable"] = not player["cheat_invulnerable"]

    elif k == b"v":
        player["cheat_no_windup"] = not player["cheat_no_windup"]


def keyboardUp(key, x, y):
    global keys_state
    keys_state[key.lower()] = False

def specialKeys(key, x, y):
    global cam_angle
    if top_down_view or game_state != "PLAYING":
        return
    if key == GLUT_KEY_LEFT:
        cam_angle = (cam_angle - 5.0) % 360
    elif key == GLUT_KEY_RIGHT:
        cam_angle = (cam_angle + 5.0) % 360

def mouseListener(button, state, x, y):
    if game_state != "PLAYING":
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if player["turret_mode"]:
            fire_projectile(player["x"], player["y"], player["z"], player["angle"], is_player=True)

def idle():
    global game_state, key_rotation_angle, projectiles, enemies_patrol, enemies_turret, enemies_ghost, pickups, pulse_timer

    update_particles()
    if game_state != "PLAYING":
        glutPostRedisplay()
        return

    key_rotation_angle = (key_rotation_angle + 0.5) % 360.0
    pulse_timer += 0.025

    if player["cheat_no_windup"]:
        player["power"] = player["max_power"]

    if keys_state.get(b"w", False) and not player["cheat_no_windup"]:
        player["power"] = min(player["max_power"], player["power"] + 0.1)
        player["wind_up_angle"] += player["power"] * 0.05

    if player["power"] > 0:
        if keys_state.get(b"a", False):
            player["angle"] += 0.005
        if keys_state.get(b"d", False):
            player["angle"] -= 0.005

        speed = 1.0 * (player["power"] / player["max_power"])

        if not player["turret_mode"]:
            next_x = player["x"] + math.cos(player["angle"]) * speed
            next_y = player["y"] + math.sin(player["angle"]) * speed

            if not check_wall_collision(next_x, player["y"], player["radius"]) and not check_box_collision(next_x, player["y"],
                                                                                                           player["radius"]):
                player["x"] = next_x
            if not check_wall_collision(player["x"], next_y, player["radius"]) and not check_box_collision(player["x"], next_y,
                                                                                                           player["radius"]):
                player["y"] = next_y
            if not player["cheat_no_windup"]:
                player["power"] = max(0.0, player["power"] - 0.05)
            player["wind_up_angle"] -= speed * 2.0
        else:
            if not player["cheat_no_windup"]:
                player["power"] = max(0.0, player["power"] - 0.01)
                player["wind_up_angle"] -= speed * 2.0

    if player["keys_collected"] >= REQUIRED_KEYS:
        if (-EXIT_WIDTH + 150) < player["x"] < (EXIT_WIDTH - 50) and ARENA_SIZE - 50 < player["y"] < ARENA_SIZE:
            game_state = "WON"

    for e in enemies_patrol:
        next_ex, next_ey = e["x"], e["y"]
        e["spin"] += 0.01

        if e["axis"] == "x":
            next_ex += e["speed"] * e["direction"]
            if abs(next_ex - e["start_x"]) > e["travel_dist"] or check_wall_collision(next_ex, e["y"], e["radius"]):
                e["direction"] *= -1
            else:
                e["x"] = next_ex
        else:
            next_ey += e["speed"] * e["direction"]
            if abs(next_ey - e["start_y"]) > e["travel_dist"] or check_wall_collision(e["x"], next_ey, e["radius"]):
                e["direction"] *= -1
            else:
                e["y"] = next_ey

        if check_collision_3d(player["x"], player["y"], player["z"], player["radius"],
                              e["x"], e["y"], e["z"], e["radius"]):
            player_take_damage()
            spawn_particles(e["x"], e["y"], e["z"], [0.3, 0.1, 0.1], count=20)
            enemies_patrol.remove(e)
            break

        for g in enemies_ghost:
            if check_collision_3d(g["x"], g["y"], g["z"], g["radius"], e["x"], e["y"], e["z"], e["radius"]):
                spawn_particles(e["x"], e["y"], e["z"], [0.3, 0.1, 0.1], count=20)
                enemies_patrol.remove(e)
                break

    for e in enemies_turret:
        e["angle"] = math.atan2(player["y"] - e["y"], player["x"] - e["x"])
        e["cooldown"] -= 1
        if e["cooldown"] <= 0:
            fire_projectile(e["x"], e["y"], e["z"], e["angle"], is_player=False)
            e["cooldown"] = 1000
        if e["cooldown"] <= 200:
            e["spin"] += math.radians(1.0)
        for g in enemies_ghost:
            if check_collision_3d(g["x"], g["y"], g["z"], g["radius"], e["x"], e["y"], e["z"], e["radius"]):
                spawn_particles(e["x"], e["y"], e["z"], [0.3, 0.7, 0.0], count=20)
                enemies_turret.remove(e)
                break

    for g in enemies_ghost:
        angle = math.atan2(player["y"] - g["y"], player["x"] - g["x"])
        g["x"] += math.cos(angle) * g["speed"]
        g["y"] += math.sin(angle) * g["speed"]
        g['z'] = 35.0 + math.sin(pulse_timer) * 15.0
        g["scale"] = 2.0 + 0.2 * math.sin(pulse_timer * 2.0)

        if check_collision_3d(player["x"], player["y"], player["z"], player["radius"],
                              g["x"], g["y"], g["z"], g["radius"] * g["scale"]):
            player_take_damage(instant_kill=True)

    hover = math.sin(math.radians(key_rotation_angle * 2.0)) * 4.0
    pickups_to_remove = []

    for p in pickups:
        visual_z = p["z"] + math.radians(hover)
        if check_collision_3d(player["x"], player["y"], player["z"], player["radius"],
                              p["x"], p["y"], visual_z, p["radius"]):
            if p["type"] == "key":
                player["keys_collected"] += 1
                g["speed"] += 0.035
                spawn_particles(p["x"], p["y"], visual_z, [1.0, 0.84, 0.0], count=25)
                enemies_ghost.append({"x": player["x"] + random.choice([-500, 500]) + random.uniform(-p["x"], p["x"]),
                                      "y": player["y"] + random.choice([-500, 500]) + random.uniform(-p["y"], p["y"]),
                                      "z": 40.0, "speed": g["speed"], "radius": 15.0, "scale": 1.0})

            elif p["type"] == "health":
                player["lives"] = min(player["max_health"], player["lives"] + 1)
                spawn_particles(p["x"], p["y"], visual_z, [1.0, 0.0, 0.0], count=20)

            elif p["type"] == "power":
                player["power"] = min(player["max_power"], player["power"] + 50)
                spawn_particles(p["x"], p["y"], visual_z, [1.0, 1.0, 0.0], count=20)

            elif p["type"] == "shield":
                player["has_shield"] = True
                spawn_particles(p["x"], p["y"], visual_z, [0.0, 0.5, 1.0], count=20)
            pickups_to_remove.append(p)

    for p in pickups_to_remove:
        if p in pickups:
            pickups.remove(p)

    projs_to_remove = []
    for p in projectiles:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        if check_wall_collision(p["x"], p["y"], p["radius"]):
            spawn_particles(p["x"], p["y"], p["z"], [0.8, 0.4, 0.0], count=10)
            projs_to_remove.append(p)
            continue

        for b in breakables:
            if check_collision_3d(p["x"], p["y"], p["z"], p["radius"], b["x"], b["y"],
                                b["z"], b["radius"]):
                spawn_particles(p["x"], p["y"], p["z"], [0.8, 0.4, 0.0], count=10)
                projs_to_remove.append(p)
                continue

        if p["is_player"]:
            for e in enemies_patrol + enemies_turret:
                if check_collision_3d(p["x"], p["y"], p["z"], p["radius"], e["x"], e["y"], e["z"], e["radius"]):
                    spawn_particles(e["x"], e["y"], e["z"], [0.8, 0.1, 0.1], count=20)
                    if e in enemies_patrol: enemies_patrol.remove(e)
                    else: enemies_turret.remove(e)
                    projs_to_remove.append(p)
                    break

            for b in breakables:
                if check_collision_3d(p["x"], p["y"], p["z"], p["radius"], b["x"], b["y"], b["z"], b["radius"]):
                    spawn_particles(b["x"], b["y"], b["z"], [0.8, 0.8, 0.1], count=20)
                    breakables.remove(b)
                    projs_to_remove.append(p)
                    break

        else:
            if check_collision_3d(p["x"], p["y"], p["z"], p["radius"], player["x"], player["y"], player["z"],
                                  player["radius"]):
                player_take_damage()
                projs_to_remove.append(p)

    for p in projs_to_remove:
        if p in projectiles:
            projectiles.remove(p)

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"The Lost Toy's Escapade")

    init_player()
    spawn_entities()

    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardDown)
    glutKeyboardUpFunc(keyboardUp)
    glutSpecialFunc(specialKeys)
    glutMouseFunc(mouseListener)

    glutMainLoop()

if __name__ == "__main__":
    main()