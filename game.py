from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

camera_pos = (0, 500, 500)
camera_distance = 500
camera_angle = 0

fovY = 110  # Field of view
GRID_LENGTH = 600  # Length of grid lines

ship_x = 0
ship_y = 0
ship_z = 50  #above water
ship_rotation = 0  # Ship facing direction
ship_speed = 0
sail_state = 0

# Storm system variables
storm_active = False
storm_start_time = 0
storm_duration = 10
game_start_time = time.time()
last_storm_end_time = 0
time_until_first_storm = 10

# Rain animation variables
rain_drops = []
rain_init = False

# Health system
ship_health = 100
max_health = 100
last_damage_time = 0
ship_sinking = False
sinking_speed = 0.5
target_sink_depth = -35

# Cannon system
cannonballs = []
last_fire_time = 0
fire_cooldown = 1.5
cannonball_speed = 12.0
cannonball_size = 8.0
cannonball_max_distance = 800

# Enemy ship system
enemy_list = []
enemy_health = 30
enemy_speed = 2.0
enemy_attack_range = 400
enemy_optimal_distance = 300
enemy_fire_cooldown = 2.0
enemy_turn_speed = 3.0

# Aiming range indicator
aiming_left = False
aiming_right = False

# Large Wave System
wave_active = False
wave_x = 0
wave_y = 0
wave_z = 0
wave_direction_x = 0
wave_direction_y = 1
wave_speed = 8.0
wave_spawn_distance = 4000
wave_width = 6000
wave_depth = 400
wave_height = 150
wave_damage = 15
last_wave_damage_time = 0
wave_damage_cooldown = 1.0
wave_has_damaged = False

#Bow
bow_back_x = 147
bow_tip_x = 210
bow_width = 63
bow_height = 35

#Cannon
cannon_positions = [80, 30, -20, -70]
cannon_length = 40
cannon_offset = 100

NO_SAIL_SPEED = 0
HALF_SAIL_SPEED = 7.5
FULL_SAIL_SPEED = 15
TURN_SPEED = 2

def initRain():
    global rain_drops, rain_init
    rain_drops = []
    for i in range(300):
        x = random.uniform(-1000, 1000)
        y = random.uniform(-1000, 1000)
        z = random.uniform(100, 400)
        rain_drops.append([x, y, z])
    rain_init = True


def drawRain():
    if not rain_init:
        return
    glColor3f(0.7, 0.7, 0.9)
    glBegin(GL_LINES)
    for drop in rain_drops: #vertical line rain
        glVertex3f(drop[0], drop[1], drop[2])
        glVertex3f(drop[0], drop[1], drop[2] - 20)
    glEnd()


def updateRain():
    global rain_drops
    if not rain_init:
        return
    for drop in rain_drops:
        drop[2] -= 8
        if drop[2] < 0:
            drop[2] = random.uniform(300, 400)
            drop[0] = ship_x + random.uniform(-1000, 1000)
            drop[1] = ship_y + random.uniform(-1000, 1000)


def drawCannonball(ball):
    glPushMatrix()
    glTranslatef(ball['pos'][0], ball['pos'][1], ball['pos'][2])
    glColor3f(0.2, 0.2, 0.2)
    glutSolidSphere(cannonball_size, 10, 10)
    glPopMatrix()


def drawEnemyShip(enemy):
    drawShip(x=enemy['x'], y=enemy['y'], z=enemy['z'], rotation=enemy['rotation'], hull_color=(0.6, 0.15, 0.15), bow_color=(0.5, 0.1, 0.1), sail_color=(0.9, 0.7, 0.7), mast_count=1, sail_state_override=2)


def drawRangeIndicator(direction):
    rad = math.radians(ship_rotation)
    forward_x = math.cos(rad)
    forward_y = math.sin(rad)

    right_x = math.sin(rad)
    right_y = -math.cos(rad)

    if direction == 'right':
        x_dir = right_x
        y_dir = right_y
    else:
        x_dir = -right_x
        y_dir = -right_y

    start_x = ship_x
    start_y = ship_y
    start_z = ship_z + 30
    end_x = start_x + x_dir * cannonball_max_distance
    end_y = start_y + y_dir * cannonball_max_distance
    end_z = start_z
    
    # Draw the line in red
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex3f(start_x, start_y, start_z)
    glVertex3f(end_x, end_y, end_z)
    glEnd()
    glLineWidth(1.0)
    arrow_size = 50
    
    glBegin(GL_TRIANGLES)
    # Tip pointing in firing direction
    glVertex3f(end_x, 
               end_y, 
               end_z)
    # Bottom back
    glVertex3f(end_x - x_dir * arrow_size * 0.6, 
               end_y - y_dir * arrow_size * 0.6, 
               end_z - arrow_size/2)
    # Top back
    glVertex3f(end_x - x_dir * arrow_size * 0.6, 
               end_y - y_dir * arrow_size * 0.6, 
               end_z + arrow_size/2)
    glEnd()


def drawWave():
    if not wave_active:
        return

    glColor4f(0.0, 0.4, 1.0, 0.9) 
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Perpendicular to wave direction (for width)
    perp_x = -wave_direction_y
    perp_y = wave_direction_x
    half_width = wave_width / 2
    half_depth = wave_depth / 2
    
    # Front face (leading edge)
    x1_front = wave_x - perp_x * half_width + wave_direction_x * half_depth
    y1_front = wave_y - perp_y * half_width + wave_direction_y * half_depth
    x2_front = wave_x + perp_x * half_width + wave_direction_x * half_depth
    y2_front = wave_y + perp_y * half_width + wave_direction_y * half_depth
    
    # Back face (trailing edge)
    x1_back = wave_x - perp_x * half_width - wave_direction_x * half_depth
    y1_back = wave_y - perp_y * half_width - wave_direction_y * half_depth
    x2_back = wave_x + perp_x * half_width - wave_direction_x * half_depth
    y2_back = wave_y + perp_y * half_width - wave_direction_y * half_depth
    
    # Draw front face
    glBegin(GL_QUADS)
    glVertex3f(x1_front, y1_front, 0)
    glVertex3f(x2_front, y2_front, 0)
    glVertex3f(x2_front, y2_front, wave_height)
    glVertex3f(x1_front, y1_front, wave_height)
    glEnd()
    
    # Draw back face
    glBegin(GL_QUADS)
    glVertex3f(x2_back, y2_back, 0)
    glVertex3f(x1_back, y1_back, 0)
    glVertex3f(x1_back, y1_back, wave_height)
    glVertex3f(x2_back, y2_back, wave_height)
    glEnd()
    
    # Draw top face
    glColor4f(0.0, 0.5, 1.0, 0.7)
    glBegin(GL_QUADS)
    glVertex3f(x1_back, y1_back, wave_height)
    glVertex3f(x1_front, y1_front, wave_height)
    glVertex3f(x2_front, y2_front, wave_height)
    glVertex3f(x2_back, y2_back, wave_height)
    glEnd()
    
    glDisable(GL_BLEND)


def drawText(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
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


def drawShip(x=None, y=None, z=None, rotation=None, hull_color=(0.4, 0.2, 0.1), bow_color=(0.35, 0.18, 0.09), sail_color=(0.9, 0.9, 0.9), mast_count=2, sail_state_override=None):
    if x is None:
        x = ship_x
    if y is None:
        y = ship_y
    if z is None:
        z = ship_z
    if rotation is None:
        rotation = ship_rotation
    if sail_state_override is None:
        current_sail_state = sail_state
    else:
        current_sail_state = sail_state_override
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 0, 1)
    
    #draw hull
    glColor3f(*hull_color)
    glPushMatrix()
    glScalef(4.2, 1.8, 1.0)
    glutSolidCube(70)
    glPopMatrix()

    #draw bow
    glColor3f(*bow_color)
    glBegin(GL_TRIANGLES)
    # Bottom face - left triangle
    glVertex3f(bow_tip_x, 0, -bow_height)
    glVertex3f(bow_back_x, -bow_width, -bow_height)
    glVertex3f(bow_back_x, bow_width, -bow_height)
    
    # Top face - triangle
    glVertex3f(bow_tip_x, 0, bow_height)
    glVertex3f(bow_back_x, bow_width, bow_height)
    glVertex3f(bow_back_x, -bow_width, bow_height)
    
    # Left side face
    glVertex3f(bow_tip_x, 0, -bow_height)
    glVertex3f(bow_tip_x, 0, bow_height)
    glVertex3f(bow_back_x, -bow_width, bow_height)
    
    glVertex3f(bow_tip_x, 0, -bow_height)
    glVertex3f(bow_back_x, -bow_width, bow_height)
    glVertex3f(bow_back_x, -bow_width, -bow_height)
    
    # Right side face
    glVertex3f(bow_tip_x, 0, -bow_height)
    glVertex3f(bow_back_x, bow_width, -bow_height)
    glVertex3f(bow_back_x, bow_width, bow_height)
    
    glVertex3f(bow_tip_x, 0, -bow_height)
    glVertex3f(bow_back_x, bow_width, bow_height)
    glVertex3f(bow_tip_x, 0, bow_height)
    glEnd()
    
    # Back face to connect with hull
    glBegin(GL_QUADS)
    glVertex3f(bow_back_x, -bow_width, -bow_height)
    glVertex3f(bow_back_x, -bow_width, bow_height)
    glVertex3f(bow_back_x, bow_width, bow_height)
    glVertex3f(bow_back_x, bow_width, -bow_height)
    glEnd()
    
    #draw masts
    glColor3f(0.3, 0.3, 0.3)
    if mast_count == 1: #for enemy ship
        glPushMatrix()
        glTranslatef(0, 0, 35)
        gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
        glPopMatrix()
    elif mast_count == 2:
        glPushMatrix()#first mast
        glTranslatef(70, 0, 35)
        gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
        glPopMatrix()
        glPushMatrix()#second mast
        glTranslatef(-70, 0, 35)
        gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
        glPopMatrix()
    
    #draw sails
    if current_sail_state > 0 or sail_state_override is not None:
        glColor3f(*sail_color)
        sail_width = 42 if current_sail_state == 1 else 60
        sail_height = 48 if current_sail_state == 1 else 75
        
        if mast_count == 1: #for enemy ship
            glPushMatrix()
            glTranslatef(0, 0, 90)
            glRotatef(90, 0, 0, 1)
            glBegin(GL_QUADS)
            glVertex3f(-sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, 0)
            glVertex3f(-sail_width, 0, 0)
            glEnd()
            glPopMatrix()
        elif mast_count == 2:
            glPushMatrix()#front mast sail
            glTranslatef(70, 0, 90)
            glRotatef(90, 0, 0, 1)
            glBegin(GL_QUADS)
            glVertex3f(-sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, 0)
            glVertex3f(-sail_width, 0, 0)
            glEnd()
            glPopMatrix()
            glPushMatrix()#fear mast sail
            glTranslatef(-70, 0, 90)
            glRotatef(90, 0, 0, 1)
            glBegin(GL_QUADS)
            glVertex3f(-sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, 0)
            glVertex3f(-sail_width, 0, 0)
            glEnd()
            glPopMatrix()
    
    #draw cannons
    glColor3f(0.2, 0.2, 0.2)
    for x_pos in cannon_positions:
        glPushMatrix()
        glTranslatef(x_pos, cannon_offset, 10)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 4, cannon_length, 8, 8)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(x_pos, -cannon_offset, 10)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 4, cannon_length, 8, 8)
        glPopMatrix()
    
    glPopMatrix()


def drawOcean():
    glPushMatrix()
    tile_size = 100
    tiles = 30  # tiles in each direction

    # Calculating which tile the ship is on
    ship_tile_x = int(ship_x / tile_size)
    ship_tile_y = int(ship_y / tile_size)
    
    # Draw tiles centered around the ship's position
    for i in range(ship_tile_x - tiles, ship_tile_x + tiles):
        for j in range(ship_tile_y - tiles, ship_tile_y + tiles):
            # Alternate color 
            if storm_active:
                if (i + j) % 2 == 0:
                    glColor3f(0.15, 0.3, 0.35)  
                else:
                    glColor3f(0.2, 0.35, 0.4) 
            else:
                if (i + j) % 2 == 0:
                    glColor3f(0.2, 0.6, 0.8) 
                else:
                    glColor3f(0.3, 0.7, 0.9)
            
            x1 = i * tile_size
            y1 = j * tile_size
            x2 = x1 + tile_size
            y2 = y1 + tile_size
            
            glBegin(GL_QUADS)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
            glEnd()
    
    glPopMatrix()


def spawnEnemy():
    angle = random.uniform(0, 360)
    distance = random.uniform(1500, 2000)
    rad = math.radians(angle)
    x = ship_x + distance * math.cos(rad)
    y = ship_y + distance * math.sin(rad)
    enemy = {'x': x, 'y': y, 'z': 50, 'rotation': 0, 'health': enemy_health, 'last_fire_time': 0, 'sinking': False, 'sink_depth': 50}
    enemy_list.append(enemy)


def updateEnemyAi():
    remove_enemy = []
    for enemy in enemy_list:
        if enemy['sinking']:
            if enemy['sink_depth'] > -35:
                enemy['sink_depth'] -= 0.5
                enemy['z'] = enemy['sink_depth']
            else:
                remove_enemy.append(enemy)
            continue
        
        dx = ship_x - enemy['x'] #calc dist and dir
        dy = ship_y - enemy['y']
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 1: continue
        x_dir = dx / distance
        y_dir = dy / distance
        
        angle_to_player = math.degrees(math.atan2(dy, dx))#calc angle
        
        # Determine target rotation based on distance
        if distance > enemy_optimal_distance + 50:
            target_rotation = angle_to_player
            enemy['x'] += x_dir * enemy_speed
            enemy['y'] += y_dir * enemy_speed
        elif distance < enemy_optimal_distance - 50:
            target_rotation = angle_to_player + 180
            enemy['x'] -= x_dir * enemy_speed
            enemy['y'] -= y_dir * enemy_speed
        else:
            target_rotation = angle_to_player + 90
            perp_x = -y_dir
            perp_y = x_dir
            enemy['x'] += perp_x * enemy_speed * 0.3
            enemy['y'] += perp_y * enemy_speed * 0.3
        
        angle_diff = target_rotation - enemy['rotation']
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360
        
        # Rotate gradually
        if abs(angle_diff) > enemy_turn_speed:
            if angle_diff > 0:
                enemy['rotation'] += enemy_turn_speed
            else:
                enemy['rotation'] -= enemy_turn_speed
        else:
            enemy['rotation'] = target_rotation
        
        enemy['rotation'] = enemy['rotation'] % 360
        
        if distance <= enemy_attack_range and abs(distance - enemy_optimal_distance) < 100:
            broadside_angle = angle_to_player + 90
            broadside_angle = broadside_angle % 360
            
            rotation_diff = broadside_angle - enemy['rotation']
            while rotation_diff > 180:
                rotation_diff -= 360
            while rotation_diff < -180:
                rotation_diff += 360
            
            if abs(rotation_diff) < 15:
                fireEnemyCannons(enemy)
    
    for enemy in remove_enemy:
        if enemy in enemy_list:
            enemy_list.remove(enemy)


def fireEnemyCannons(enemy):
    current_time = time.time()
    if current_time - enemy['last_fire_time'] < enemy_fire_cooldown:
        return
    
    enemy['last_fire_time'] = current_time
    
    dx = ship_x - enemy['x']
    dy = ship_y - enemy['y']
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance < 1:
        return
    
    x_dir = dx / distance
    y_dir = dy / distance
    
    # Enemy rotation
    rad = math.radians(enemy['rotation'])
    forward_x = math.cos(rad)
    forward_y = math.sin(rad)
    right_x = math.sin(rad)
    right_y = -math.cos(rad)
    
    for x_pos in [60, -60]:
        # Right side
        final_cannon_x = enemy['x'] + x_pos * forward_x + 70 * right_x
        final_cannon_y = enemy['y'] + x_pos * forward_y + 70 * right_y
        final_cannon_z = enemy['z'] + 10
        
        cannonballs.append({
            'pos': [final_cannon_x, final_cannon_y, final_cannon_z],
            'dir': [x_dir, y_dir, 0.0],
            'travelled': 0.0,
            'enemy_shot': True  # Mark as enemy shot
        })
        
        # Left side
        final_cannon_x = enemy['x'] + x_pos * forward_x - 70 * right_x
        final_cannon_y = enemy['y'] + x_pos * forward_y - 70 * right_y
        
        cannonballs.append({
            'pos': [final_cannon_x, final_cannon_y, final_cannon_z],
            'dir': [x_dir, y_dir, 0.0],
            'travelled': 0.0,
            'enemy_shot': True
        })


def checkCannonballHits():
    global ship_health, ship_sinking
    balls_to_remove = []
    for ball in cannonballs:
        # Checking if player shot hit an enemy
        if not ball.get('enemy_shot', False):
            for enemy in enemy_list:
                if enemy['sinking']:
                    continue
                
                dx = ball['pos'][0] - enemy['x']
                dy = ball['pos'][1] - enemy['y'] 
                dz = ball['pos'][2] - enemy['z']
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < 80:  # Hit detection radius
                    enemy['health'] -= 10
                    balls_to_remove.append(ball)
                    
                    if enemy['health'] <= 0:
                        enemy['sinking'] = True
                    break
        
        # Check if enemy shot hit player
        else:
            if not ship_sinking:
                dx = ball['pos'][0] - ship_x
                dy = ball['pos'][1] - ship_y
                dz = ball['pos'][2] - ship_z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < 100:  # Hit detection radius for player
                    ship_health -= 2.5
                    balls_to_remove.append(ball)
                    
                    if ship_health <= 0:
                        ship_health = 0
                        ship_sinking = True
                    break
    
 
    for ball in balls_to_remove:
        if ball in cannonballs:
            cannonballs.remove(ball)


def fireCannons():
    global last_fire_time
    if not aiming_left and not aiming_right:
        return
    # Check cooldown
    current_time = time.time()
    if current_time - last_fire_time < fire_cooldown:
        return
    
    # Can't fire when sinking
    if ship_sinking:
        return
    
    last_fire_time = current_time

    # Direction of ship facing
    rad = math.radians(ship_rotation)
    forward_x = math.cos(rad)
    forward_y = math.sin(rad)

    #Perpendicular direction
    right_x = math.sin(rad)
    right_y = -math.cos(rad)
    

    if aiming_right:
        for x_pos in cannon_positions:
            
            cannon_local_x = x_pos
            cannon_local_y = cannon_offset
            #Cannon final position 
            final_cannon_x = ship_x + cannon_local_x * forward_x + cannon_local_y * right_x
            final_cannon_y = ship_y + cannon_local_x * forward_y + cannon_local_y * right_y
            final_cannon_z = ship_z + 10
            
            # Cannonball fires perpendicular to ship (right side)
            cannonballs.append({
                'pos': [final_cannon_x, final_cannon_y, final_cannon_z],
                'dir': [right_x, right_y, 0.0],
                'travelled': 0.0,
                'enemy_shot': False  # Mark as player shot
            })
    
    # Fire from left side
    if aiming_left:
        for x_pos in cannon_positions:
            # Calculate cannon world position
            cannon_local_x = x_pos
            cannon_local_y = -cannon_offset
            
            final_cannon_x = ship_x + cannon_local_x * forward_x + cannon_local_y * right_x
            final_cannon_y = ship_y + cannon_local_x * forward_y + cannon_local_y * right_y
            final_cannon_z = ship_z + 10
            
            # Cannonball fires perpendicular to ship
            cannonballs.append({
                'pos': [final_cannon_x, final_cannon_y, final_cannon_z],
                'dir': [-right_x, -right_y, 0.0],
                'travelled': 0.0,
                'enemy_shot': False  # Mark as player shot
            })


def updateCannonballs():
    global cannonballs
    
    balls_to_remove = []
    
    for ball in cannonballs:
        # Update position
        ball['pos'][0] += ball['dir'][0] * cannonball_speed
        ball['pos'][1] += ball['dir'][1] * cannonball_speed
        ball['pos'][2] += ball['dir'][2] * cannonball_speed
        
        # distance travelled
        ball['travelled'] += cannonball_speed
        
        # Remove if traveled too far
        if ball['travelled'] >= cannonball_max_distance:
            balls_to_remove.append(ball)
    

    for ball in balls_to_remove:
        if ball in cannonballs:
            cannonballs.remove(ball)


def updateShipMovement():
    global ship_x, ship_y, ship_speed
    if ship_sinking:
        ship_speed = 0
        return
    if sail_state == 0:
        ship_speed = NO_SAIL_SPEED
    elif sail_state == 1:
        ship_speed = HALF_SAIL_SPEED
    else:
        ship_speed = FULL_SAIL_SPEED
    if ship_speed > 0:
        rad = math.radians(ship_rotation)
        ship_x += ship_speed * math.cos(rad)
        ship_y += ship_speed * math.sin(rad)
        
        # Check for ramming collisions
        checkRammingCollision()


def checkRammingCollision():
    global ship_speed, sail_state
    
    if ship_sinking:
        return
    
    # Calculate bow position in world coordinates
    rad = math.radians(ship_rotation)
    forward_x = math.cos(rad)
    forward_y = math.sin(rad)
    
    # Bow tip position (front of the ship)
    bow_tip_world_x = ship_x + bow_tip_x * forward_x
    bow_tip_world_y = ship_y + bow_tip_x * forward_y
    
    # Check collision with each enemy
    for enemy in enemy_list:
        if enemy['sinking']:
            continue
        
        # Calculate distance from bow tip to enemy center
        dx = bow_tip_world_x - enemy['x']
        dy = bow_tip_world_y - enemy['y']
        dist = math.sqrt(dx * dx + dy * dy)
        enemy_collision_radius = 120
        
        if dist < enemy_collision_radius:
            to_enemy_x = enemy['x'] - ship_x
            to_enemy_y = enemy['y'] - ship_y
            to_enemy_dist = math.sqrt(to_enemy_x * to_enemy_x + to_enemy_y * to_enemy_y)
            
            if to_enemy_dist > 0:
                to_enemy_x /= to_enemy_dist
                to_enemy_y /= to_enemy_dist
                dot = forward_x * to_enemy_x + forward_y * to_enemy_y
                
                if dot > 0.7:
                    enemy['health'] = 0
                    enemy['sinking'] = True
                    ship_speed = 0
                    sail_state = 0
                    
                    print(f"RAMMING ATTACK! Enemy ship destroyed!")
                    return


def keyboardListener(key, x, y):
    global sail_state, ship_rotation
    if ship_sinking:
        if key == b'r':
            resetGame()
        return
    
    if key == b'w':#raise sails
        if sail_state < 2:
            sail_state += 1
    
    if key == b's':#lower sails
        if sail_state > 0:
            sail_state -= 1
    
    if key == b'a':#turn left
        if ship_speed > 0:
            ship_rotation += TURN_SPEED
            if ship_rotation >= 360:
                ship_rotation -= 360
    
    if key == b'd':#turn right
        if ship_speed > 0:
            ship_rotation -= TURN_SPEED
            if ship_rotation < 0:
                ship_rotation += 360
    
    if key == b'r':#reset
        resetGame()
    
    if key == b'\x1b':  #ESC
        glutLeaveMainLoop()


def specialKeyListener(key, x, y):
    global camera_distance, camera_angle, ship_rotation
    
    #move camera up
    if key == GLUT_KEY_UP:
        camera_distance -= 20
        if camera_distance < 200:
            camera_distance = 200
    
    #move camera down
    if key == GLUT_KEY_DOWN:
        camera_distance += 20
        if camera_distance > 1000:
            camera_distance = 1000
    
    #rotate camera left
    if key == GLUT_KEY_LEFT:
        camera_angle += 5
    
    #rotate camera right
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5


def mouseListener(button, state, x, y):
    #no left click fire when sinking
    if ship_sinking:
        return
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fireCannons()


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 10000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cam_angle_rad = math.radians(ship_rotation + camera_angle)
    cam_x = ship_x - camera_distance * math.cos(cam_angle_rad)
    cam_y = ship_y - camera_distance * math.sin(cam_angle_rad)
    cam_z = camera_distance * 0.4
    gluLookAt(cam_x, cam_y, cam_z, ship_x, ship_y, ship_z, 0, 0, 1)


def updateStorm():
    global storm_active, storm_start_time, last_storm_end_time, rain_init
    global game_start_time
    current_time = time.time()
    elapsed_game_time = current_time - game_start_time
    
    if not storm_active:
        if elapsed_game_time >= time_until_first_storm and last_storm_end_time == 0: #start storm after gameplay
            startStorm()
        elif last_storm_end_time > 0 and (current_time - last_storm_end_time) >= 30: #again storm after 30s
            startStorm()
    elif (current_time - storm_start_time) >= storm_duration: #storm end after 10s
        endStorm()


def startStorm():
    global storm_active, storm_start_time, rain_init
    storm_active = True
    storm_start_time = time.time()
    rain_init = False
    initRain()


def endStorm():
    global storm_active, last_storm_end_time, rain_init
    global wave_active, wave_x, wave_y, wave_direction_x, wave_direction_y
    storm_active = False
    last_storm_end_time = time.time()
    rain_init = False
    spawn_wave()
    spawnEnemy()


def applyStormDamage():
    global ship_health, last_damage_time, ship_sinking
    if not storm_active or ship_sinking:
        return
    
    current_time = time.time()
    if current_time - last_damage_time >= 1.0:#damage every sec
        if sail_state == 2:  # Full sail
            ship_health -= 2
        elif sail_state == 1:  # Half sail
            ship_health -= 1
        last_damage_time = current_time
        
        if ship_health <= 0:#destroyed check
            ship_health = 0
            ship_sinking = True


def updateSinking():
    global ship_z, ship_speed
    
    if not ship_sinking:
        return
    
    # Stop the ship from moving
    ship_speed = 0
    
    # Gradually lower the ship
    if ship_z > target_sink_depth:
        ship_z -= sinking_speed
        if ship_z < target_sink_depth:
            ship_z = target_sink_depth


def spawn_wave():
    global wave_active, wave_x, wave_y, wave_direction_x, wave_direction_y, wave_has_damaged
    # Spawn wave in random direction around the ship
    random_angle = random.uniform(0, 360)
    angle_rad = math.radians(random_angle)
    
    # Wave spawns at random direction from ship
    spawn_x_dir = math.cos(angle_rad)
    spawn_y_dir = math.sin(angle_rad)
    
    wave_x = ship_x + spawn_x_dir * wave_spawn_distance
    wave_y = ship_y + spawn_y_dir * wave_spawn_distance
    
    # Wave moves toward the ship
    wave_direction_x = -spawn_x_dir
    wave_direction_y = -spawn_y_dir
    wave_active = True
    wave_has_damaged = False  # Reset damage flag for new wave


def updateWave():
    global wave_active, wave_x, wave_y, ship_health, last_wave_damage_time
    if not wave_active:
        return
    
    # Move wave toward ship
    wave_x += wave_direction_x * wave_speed
    wave_y += wave_direction_y * wave_speed
    
    checkWaveCollision()
    
    # Remove wave if it has passed far beyond the ship
    dist_to_ship = math.sqrt((wave_x - ship_x)**2 + (wave_y - ship_y)**2)
    if dist_to_ship < 100 or dist_to_ship > wave_spawn_distance + 1000:
        wave_active = False


def checkWaveCollision():
    global ship_health, last_wave_damage_time, wave_active, ship_sinking, wave_has_damaged
    
    if not wave_active or ship_sinking or wave_has_damaged:
        return
    
    # Calculate distance to wave center
    dist_to_wave = math.sqrt((wave_x - ship_x)**2 + (wave_y - ship_y)**2)
    
    # Check if ship is within collision range (considering wave depth)
    collision_range = wave_depth / 2 + 250  # Ship size consideration
    
    if dist_to_wave < collision_range:
        # Get ship's forward direction
        ship_rad = math.radians(ship_rotation)
        ship_forward_x = math.cos(ship_rad)
        ship_forward_y = math.sin(ship_rad)
        
        # Normalize wave direction
        wave_mag = math.sqrt(wave_direction_x**2 + wave_direction_y**2)
        if wave_mag > 0:
            norm_wave_x = wave_direction_x / wave_mag
            norm_wave_y = wave_direction_y / wave_mag
        else:
            return

        dot_product = ship_forward_x * norm_wave_x + ship_forward_y * norm_wave_y
        angle_rad = math.acos(max(-1, min(1, dot_product)))
        angle_deg = math.degrees(angle_rad)
        wave_has_damaged = True

        if angle_deg < 150:
            ship_health -= wave_damage
            print(f"Wave hit! Angle: {angle_deg:.1f}° - Damage: {wave_damage} HP")
            
            if ship_health <= 0:
                ship_health = 0
                ship_sinking = True
        else:
            print(f"Wave passed! Angle: {angle_deg:.1f}° - Head-on, no damage")


def resetGame():
    global ship_x, ship_y, ship_z, ship_rotation, ship_speed, sail_state
    global storm_active, storm_start_time, last_storm_end_time, game_start_time
    global ship_health, last_damage_time, rain_init, ship_sinking
    global cannonballs, last_fire_time, wave_active, last_wave_damage_time
    global cannonballs, last_fire_time, enemy_list
    
    ship_x = 0
    ship_y = 0
    ship_z = 50
    ship_rotation = 0
    ship_speed = 0
    sail_state = 0
    
    storm_active = False
    storm_start_time = 0
    last_storm_end_time = 0
    game_start_time = time.time()
    rain_init = False
    
    ship_health = 100
    last_damage_time = 0
    ship_sinking = False
    
    cannonballs.clear()
    last_fire_time = 0
    
    wave_active = False
    last_wave_damage_time = 0
    wave_has_damaged = False
    print("Game reset!")
    enemy_list.clear()


def idle():
    updateShipMovement()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    drawOcean()
    drawShip()
    
    # Draw wave if active
    if wave_active:
        drawWave()
    
    for enemy in enemy_list:
        drawEnemyShip(enemy)
    # Draw range indicator when aiming
    if aiming_left:
        drawRangeIndicator('left')
    if aiming_right:
        drawRangeIndicator('right')
    
    for ball in cannonballs:
        drawCannonball(ball)
    
    if storm_active:
        drawRain()
    
    drawText(10, 770, f"Sail State: {['No Sail', 'Half Sail', 'Full Sail'][sail_state]}")
    drawText(10, 740, f"Health: {ship_health}/{max_health}")
    
    if ship_sinking:
        drawText(300, 400, "GAME OVER - SHIP SINKING!")
        drawText(350, 370, "Press R to Restart")
    elif storm_active:
        drawText(10, 710, "STORM ACTIVE!")
        if sail_state == 2:
            drawText(10, 680, "Full Sail: -2 HP/sec")
        elif sail_state == 1:
            drawText(10, 680, "Half Sail: -1 HP/sec")
    glutSwapBuffers()
keys_pressed = set()


def keyboardDown(key, x, y):
    keys_pressed.add(key)
    
    # Handle aiming
    global aiming_left, aiming_right
    if key == b'q':
        aiming_left = True
    elif key == b'e':
        aiming_right = True
    
    keyboardListener(key, x, y)


def keyboardUp(key, x, y):
    if key in keys_pressed:
        keys_pressed.remove(key)
    
    # Handle aiming stop
    global aiming_left, aiming_right
    if key == b'q':
        aiming_left = False
    elif key == b'e':
        aiming_right = False


def idleWithKeys():
    if ship_sinking:
        updateSinking()
        glutPostRedisplay()
        return
    
    updateShipMovement()
    updateStorm()
    applyStormDamage()
    updateSinking()
    updateCannonballs()
    updateWave()
    updateEnemyAi()
    checkCannonballHits()
    if storm_active:
        updateRain()
    glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Pirate Ship Battle Game")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardDown)
    glutKeyboardUpFunc(keyboardUp)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idleWithKeys)
    glutMainLoop()


if __name__ == "__main__":
    main()