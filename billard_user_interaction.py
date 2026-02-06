import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import matplotlib.patches as patches
import math

# --- Initialisation ---
fig, ax = plt.subplots(figsize=(15,6))
ax.set_xlim(-5,10)
ax.set_ylim(-3,3)

R = 0.2
C, D, E, F = (-2,-2), (8,-2), (8,2), (-2,2)
plt.plot([C[0],D[0],E[0],F[0],C[0]], [C[1],D[1],E[1],F[1],C[1]], color="blue")

score = [0,0]
player = 0
score_text = ax.text(-4,2.5,f"Joueur 1: {score[0]}  Joueur 2: {score[1]}", fontsize=14)

# Positions fixes
positions = [
    np.array([[0.0,0.0]]),     # bille blanche
    np.array([[2.0,0.5]]),     # bille rouge
    np.array([[4.0,-0.5]])     # bille jaune
]

velocities = [
    np.array([0.0,0.0]),
    np.array([0.0,0.0]),
    np.array([0.0,0.0])
]

patches_list = [
    patches.Circle((pos[0,0], pos[0,1]), R, fc=color, ec='black')
    for pos, color in zip(positions, ['white','red','yellow'])
]
for p in patches_list:
    ax.add_patch(p)

aim_arrow = patches.FancyArrowPatch((0,0),(0,0), color='black', arrowstyle='-|>', mutation_scale=20)
aim_arrow.set_visible(False)
ax.add_patch(aim_arrow)

friction = 0.99
max_power = 15.0
power_multiplier = 5.0

# --- États du jeu ---
choosing_direction = True  # toujours prêt à tirer
white_selected = False     # True si on clique sur la blanche
counted_collisions = set()

# --- Clic ---
def on_click(event):
    global white_selected
    if event.xdata is None or event.ydata is None:
        return
    x, y = event.xdata, event.ydata

    # Tir possible uniquement si clic sur la blanche
    if np.linalg.norm(np.array([x,y]) - positions[0][0]) <= R:
        white_selected = True
    else:
        white_selected = False  # cliquer ailleurs ne fait rien

# --- Mouvement de la souris ---
def on_move(event):
    if choosing_direction and white_selected and event.xdata is not None and event.ydata is not None:
        start = positions[0][0]
        end = np.array([event.xdata, event.ydata])
        direction = end - start
        norm = np.linalg.norm(direction)
        if norm > max_power:
            end = start + direction / norm * max_power
        aim_arrow.set_positions(start, end)
        aim_arrow.set_visible(True)

# --- Relâchement pour tirer ---
def on_release(event):
    global velocities, white_selected
    if white_selected and event.xdata is not None and event.ydata is not None:
        start = positions[0][0]
        end = np.array([event.xdata, event.ydata])
        direction = end - start
        norm = np.linalg.norm(direction)
        if norm > max_power:
            direction = direction / norm * max_power
        velocities[0] = direction * power_multiplier
        white_selected = False
        aim_arrow.set_visible(False)

fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('motion_notify_event', on_move)
fig.canvas.mpl_connect('button_release_event', on_release)

# --- Collisions ---
def handle_collision(i1,i2):
    dx = positions[i2][0,0]-positions[i1][0,0]
    dy = positions[i2][0,1]-positions[i1][0,1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        dist = 0.0001
    if dist < 2*R:
        nx = dx/dist
        ny = dy/dist

        # Vitesses normales/tangentes
        v1n = velocities[i1][0]*nx + velocities[i1][1]*ny
        v1t = -velocities[i1][0]*ny + velocities[i1][1]*nx
        v2n = velocities[i2][0]*nx + velocities[i2][1]*ny
        v2t = -velocities[i2][0]*ny + velocities[i2][1]*nx

        # Échange normales
        v1n, v2n = v2n, v1n

        velocities[i1][0] = v1n*nx - v1t*ny
        velocities[i1][1] = v1n*ny + v1t*nx
        velocities[i2][0] = v2n*nx - v2t*ny
        velocities[i2][1] = v2n*ny + v2t*nx

        # Corriger chevauchement
        overlap = 2*R - dist
        positions[i1][0,0] -= nx*overlap/2
        positions[i1][0,1] -= ny*overlap/2
        positions[i2][0,0] += nx*overlap/2
        positions[i2][0,1] += ny*overlap/2

        pair = tuple(sorted([i1,i2]))
        if pair not in counted_collisions:
            counted_collisions.add(pair)
            if 0 in pair:
                if 1 in pair: return 1
                if 2 in pair: return 2
    else:
        pair = tuple(sorted([i1,i2]))
        if pair in counted_collisions:
            counted_collisions.remove(pair)
    return 0

# --- Animation ---
def animate(frame):
    global positions, velocities, score, player

    for idx,pos in enumerate(positions):
        pos[:,0] += velocities[idx][0]*0.02
        pos[:,1] += velocities[idx][1]*0.02

        # Rebond murs
        if pos[0,0]-R <= -2 or pos[0,0]+R >= 8:
            velocities[idx][0] = -velocities[idx][0]
        if pos[0,1]-R <= -2 or pos[0,1]+R >= 2:
            velocities[idx][1] = -velocities[idx][1]

    # Collisions
    n = len(positions)
    for i1 in range(n):
        for i2 in range(i1+1,n):
            point = handle_collision(i1,i2)
            if point == 1 or point == 2:
                score[player] += 1

    # Friction
    for idx in range(len(velocities)):
        velocities[idx] *= friction

    # Mise à jour patches
    for idx, patch in enumerate(patches_list):
        patch.center = (positions[idx][0,0], positions[idx][0,1])

    # Fin du tour
    if np.linalg.norm(velocities[0])<0.05:
        velocities[0] = np.array([0.0,0.0])
        player = (player+1)%2

    score_text.set_text(f"Joueur 1: {score[0]}  Joueur 2: {score[1]}")
    return patches_list + [score_text, aim_arrow]

ani = animation.FuncAnimation(fig, animate, init_func=lambda: patches_list+[score_text, aim_arrow], interval=20, blit=True)
plt.show()