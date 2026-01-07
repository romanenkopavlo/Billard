import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import matplotlib.patches as patches
import math

fig, ax = plt.subplots(figsize=(16,9))
ax.set_xlim(-640,640)
ax.set_ylim(-360,360)
ax.set_aspect('equal')

ax.plot([-400,400,400,-400,-400], [200,200,-200,-200,200], 'k-', linewidth=2)

ball_radius = 10

white_ball_x, white_ball_y = -200, 0
white_ball = patches.Circle((white_ball_x, white_ball_y), ball_radius, 
                           fc='white', ec='black', linewidth=2, zorder=10)
ax.add_patch(white_ball)
white_vx, white_vy = 0, 0

red_ball_x, red_ball_y = 200, 0
red_ball = patches.Circle((red_ball_x, red_ball_y), ball_radius, 
                         fc='red', ec='black', linewidth=2, zorder=10)
ax.add_patch(red_ball)
red_vx, red_vy = 0, 0

dragging = False
start_x, start_y = 0, 0

info_text = ax.text(-630, 330, "Cliquez-glissez sur la bille BLANCHE", 
                   fontsize=12, bbox=dict(facecolor='lightblue', alpha=0.8))
speed_text_white = ax.text(-630, 300, "Blanche: arrêtée", 
                          fontsize=12, bbox=dict(facecolor='lightgray', alpha=0.8))
speed_text_red = ax.text(-630, 270, "Rouge: arrêtée", 
                        fontsize=12, bbox=dict(facecolor='pink', alpha=0.8))

def update_speed_text():
    white_speed = math.sqrt(white_vx**2 + white_vy**2)
    red_speed = math.sqrt(red_vx**2 + red_vy**2)
    
    if white_speed < 0.1:
        speed_text_white.set_text("Blanche: arrêtée")
    else:
        speed_text_white.set_text(f"Blanche: {white_speed:.1f}")
    
    if red_speed < 0.1:
        speed_text_red.set_text("Rouge: arrêtée")
    else:
        speed_text_red.set_text(f"Rouge: {red_speed:.1f}")

update_speed_text()

def check_ball_collision(x1, y1, x2, y2, vx1, vy1, vx2, vy2):
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance < 2 * ball_radius:
        if distance > 0:
            nx = dx / distance
            ny = dy / distance
        else:
            nx, ny = 1, 0
        
        dvx = vx2 - vx1
        dvy = vy2 - vy1
        dvn = dvx * nx + dvy * ny
        
        if dvn < 0:
            impulse = dvn
            
            new_vx1 = vx1 + impulse * nx
            new_vy1 = vy1 + impulse * ny
            new_vx2 = vx2 - impulse * nx
            new_vy2 = vy2 - impulse * ny
            
            overlap = 2 * ball_radius - distance
            if overlap > 0 and distance > 0:
                sep_x = nx * overlap * 0.5
                sep_y = ny * overlap * 0.5
                return (new_vx1, new_vy1, new_vx2, new_vy2, 
                        x1 - sep_x, y1 - sep_y, x2 + sep_x, y2 + sep_y)
            
            return new_vx1, new_vy1, new_vx2, new_vy2, x1, y1, x2, y2
    
    return vx1, vy1, vx2, vy2, x1, y1, x2, y2

def on_click(event):
    global dragging, start_x, start_y
    
    if event.xdata is None:
        return
    
    dist_to_white = math.sqrt((event.xdata - white_ball_x)**2 + 
                             (event.ydata - white_ball_y)**2)
    
    if dist_to_white <= ball_radius * 1.5:
        dragging = True
        start_x, start_y = white_ball_x, white_ball_y
        info_text.set_text("Glissez pour frapper...")
        
        for artist in ax.get_children():
            if isinstance(artist, patches.FancyArrow):
                artist.remove()
        
        plt.draw()
        return True
    else:
        info_text.set_text("Cliquez sur la bille BLANCHE !")
        plt.draw()
        return False

def on_drag(event):
    global dragging
    
    if not dragging or event.xdata is None or event.ydata is None:
        return
    
    for artist in ax.get_children():
        if isinstance(artist, patches.FancyArrow):
            artist.remove()
    
    for line in ax.get_lines():
        line.remove()
    
    ax.plot([-400,400,400,-400,-400], [200,200,-200,-200,200], 'k-', linewidth=2)
    
    dx = event.xdata - start_x
    dy = event.ydata - start_y
    
    current_length = math.sqrt(dx**2 + dy**2)
    
    arrow_scale = 1.0
    ax.arrow(start_x, start_y, dx * arrow_scale, dy * arrow_scale, 
             head_width=20, head_length=25, fc='blue', ec='blue', 
             alpha=0.8, zorder=5, width=3)
    
    ax.plot([start_x, start_x + dx * arrow_scale], 
            [start_y, start_y + dy * arrow_scale], 'b-', alpha=0.5, zorder=4, linewidth=2)
    
    speed_factor = 10.5
    preview_vx = dx * speed_factor
    preview_vy = dy * speed_factor
    preview_speed = math.sqrt(preview_vx**2 + preview_vy**2)
    preview_angle = math.degrees(math.atan2(preview_vy, preview_vx))
    
    info_text.set_text(f"Puissance: {preview_speed:.1f}, Angle: {preview_angle:.1f}°")
    
    plt.draw()

def on_release(event):
    global dragging, white_vx, white_vy
    
    if not dragging:
        return
    
    dragging = False
    
    if event.xdata is None or event.ydata is None:
        info_text.set_text("Annulé.")
        plt.draw()
        return
    
    dx = event.xdata - start_x
    dy = event.ydata - start_y
    
    speed_factor = 10.5
    
    white_vx = dx * speed_factor
    white_vy = dy * speed_factor
    
    info_text.set_text("Bille frappée !")
    
    update_speed_text()
    
    ax.clear()
    ax.set_xlim(-640,640)
    ax.set_ylim(-360,360)
    ax.set_aspect('equal')
    ax.plot([-400,400,400,-400,-400], [200,200,-200,-200,200], 'k-', linewidth=2)
    
    ax.add_patch(white_ball)
    ax.add_patch(red_ball)
    ax.add_artist(info_text)
    ax.add_artist(speed_text_white)
    ax.add_artist(speed_text_red)
    
    plt.draw()

fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('motion_notify_event', on_drag)
fig.canvas.mpl_connect('button_release_event', on_release)

def update(frame):
    global white_ball_x, white_ball_y, white_vx, white_vy
    global red_ball_x, red_ball_y, red_vx, red_vy
    
    dt = 1/60.0
    
    white_ball_x += white_vx * dt
    white_ball_y += white_vy * dt
    white_ball.center = (white_ball_x, white_ball_y)
    
    red_ball_x += red_vx * dt
    red_ball_y += red_vy * dt
    red_ball.center = (red_ball_x, red_ball_y)
    
    white_vx, white_vy, red_vx, red_vy, white_ball_x, white_ball_y, red_ball_x, red_ball_y = \
        check_ball_collision(white_ball_x, white_ball_y, red_ball_x, red_ball_y,
                           white_vx, white_vy, red_vx, red_vy)
    
    if white_ball_x + ball_radius > 400:
        white_ball_x = 400 - ball_radius
        white_vx = -abs(white_vx) * 0.9
    elif white_ball_x - ball_radius < -400:
        white_ball_x = -400 + ball_radius
        white_vx = abs(white_vx) * 0.9
    
    if white_ball_y + ball_radius > 200:
        white_ball_y = 200 - ball_radius
        white_vy = -abs(white_vy) * 0.9
    elif white_ball_y - ball_radius < -200:
        white_ball_y = -200 + ball_radius
        white_vy = abs(white_vy) * 0.9
    
    if red_ball_x + ball_radius > 400:
        red_ball_x = 400 - ball_radius
        red_vx = -abs(red_vx) * 0.9
    elif red_ball_x - ball_radius < -400:
        red_ball_x = -400 + ball_radius
        red_vx = abs(red_vx) * 0.9
    
    if red_ball_y + ball_radius > 200:
        red_ball_y = 200 - ball_radius
        red_vy = -abs(red_vy) * 0.9
    elif red_ball_y - ball_radius < -200:
        red_ball_y = -200 + ball_radius
        red_vy = abs(red_vy) * 0.9
    
    friction = 0.99
    white_vx *= friction
    white_vy *= friction
    red_vx *= friction
    red_vy *= friction
    
    if abs(white_vx) < 0.1 and abs(white_vy) < 0.1:
        white_vx, white_vy = 0, 0
    if abs(red_vx) < 0.1 and abs(red_vy) < 0.1:
        red_vx, red_vy = 0, 0
    
    if frame % 10 == 0:
        update_speed_text()
    
    return white_ball, red_ball, info_text, speed_text_white, speed_text_red

ani = animation.FuncAnimation(fig, update, interval=16, blit=False)
plt.title("Billard - Frappez la bille blanche")
plt.show()