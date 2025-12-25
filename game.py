from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

camera_pos = (0, 500, 500)
camera_distance = 500
camera_angle = 0

fovY = 120  # Field of view
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
rain_initialized = False

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
enemies = []  # List of enemy ships
enemy_health = 30  # Health for each enemy ship
enemy_speed = 2.0  # Movement speed
enemy_attack_range = 400  # Range to start firing
enemy_optimal_distance = 300  # Distance to maintain from player
enemy_fire_cooldown = 2.0  # Enemy firing cooldown

bow_back_x = 147
bow_tip_x = 210
bow_width = 63
bow_height = 35

cannon_positions = [80, 30, -20, -70]
cannon_length = 25
cannon_offset = 80

SPEED_NO_SAIL = 0
SPEED_HALF_SAIL = 4
SPEED_FULL_SAIL = 6
TURN_SPEED = 2

def initialize_rain():
    """Initialize rain drops at random positions around the ship"""
    global rain_drops, rain_initialized
    rain_drops = []
    
    # Create rain drops in a large area around the ship
    for i in range(300):
        # Distribute rain in a large area
        x = random.uniform(-1000, 1000)
        y = random.uniform(-1000, 1000)
        z = random.uniform(100, 400)  # Height above water
        rain_drops.append([x, y, z])
    
    rain_initialized = True


def draw_rain():
    """Draw rain as vertical lines falling straight down"""
    if not rain_initialized:
        return
    
    glColor3f(0.7, 0.7, 0.9)  # Light gray/blue color for rain
    glBegin(GL_LINES)
    
    for drop in rain_drops:
        # Draw each rain drop as a vertical line
        glVertex3f(drop[0], drop[1], drop[2])
        glVertex3f(drop[0], drop[1], drop[2] - 20)  # Line length of 20 units
    
    glEnd()


def update_rain():
    """Update rain drop positions to create falling effect"""
    global rain_drops
    
    if not rain_initialized:
        return
    
    for drop in rain_drops:
        # Move rain straight down
        drop[2] -= 8  # Fall speed
        
        # Reset rain drops that fall below water
        if drop[2] < 0:
            drop[2] = random.uniform(300, 400)
            # Keep rain drops relative to ship position
            drop[0] = ship_x + random.uniform(-1000, 1000)
            drop[1] = ship_y + random.uniform(-1000, 1000)


def draw_cannonball(ball):
    """Draw a single cannonball"""
    glPushMatrix()
    glTranslatef(ball['pos'][0], ball['pos'][1], ball['pos'][2])
    glColor3f(0.2, 0.2, 0.2)  # Dark gray/black
    glutSolidSphere(cannonball_size, 10, 10)
    glPopMatrix()


def draw_enemy_ship(enemy):
    """Draw an enemy ship using draw_ship function with red colors and 1 mast"""
    draw_ship(
        x=enemy['x'],
        y=enemy['y'],
        z=enemy['z'],
        rotation=enemy['rotation'],
        hull_color=(0.6, 0.15, 0.15),
        bow_color=(0.5, 0.1, 0.1),
        sail_color=(0.9, 0.7, 0.7),
        num_masts=1,
        sail_state_override=2  # Always full sail for enemy
    )


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
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


def draw_ship(x=None, y=None, z=None, rotation=None, hull_color=(0.4, 0.2, 0.1), bow_color=(0.35, 0.18, 0.09), sail_color=(0.9, 0.9, 0.9), num_masts=2, sail_state_override=None):
    # Use player ship values if not provided
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
    glVertex3f(bow_tip_x, 0, -bow_height)      # Tip bottom
    glVertex3f(bow_back_x, -bow_width, -bow_height)  # Back left bottom
    glVertex3f(bow_back_x, bow_width, -bow_height)   # Back right bottom
    
    # Top face - triangle
    glVertex3f(bow_tip_x, 0, bow_height)       # Tip top
    glVertex3f(bow_back_x, bow_width, bow_height)    # Back right top
    glVertex3f(bow_back_x, -bow_width, bow_height)   # Back left top
    
    # Left side face
    glVertex3f(bow_tip_x, 0, -bow_height)      # Tip bottom
    glVertex3f(bow_tip_x, 0, bow_height)       # Tip top
    glVertex3f(bow_back_x, -bow_width, bow_height)   # Back left top
    
    glVertex3f(bow_tip_x, 0, -bow_height)      # Tip bottom
    glVertex3f(bow_back_x, -bow_width, bow_height)   # Back left top
    glVertex3f(bow_back_x, -bow_width, -bow_height)  # Back left bottom
    
    # Right side face
    glVertex3f(bow_tip_x, 0, -bow_height)      # Tip bottom
    glVertex3f(bow_back_x, bow_width, -bow_height)   # Back right bottom
    glVertex3f(bow_back_x, bow_width, bow_height)    # Back right top
    
    glVertex3f(bow_tip_x, 0, -bow_height)      # Tip bottom
    glVertex3f(bow_back_x, bow_width, bow_height)    # Back right top
    glVertex3f(bow_tip_x, 0, bow_height)       # Tip top
    glEnd()
    
    # Back face to connect with hull
    glBegin(GL_QUADS)
    glVertex3f(bow_back_x, -bow_width, -bow_height)  # Back left bottom
    glVertex3f(bow_back_x, -bow_width, bow_height)   # Back left top
    glVertex3f(bow_back_x, bow_width, bow_height)    # Back right top
    glVertex3f(bow_back_x, bow_width, -bow_height)   # Back right bottom
    glEnd()
    
    # Draw masts based on num_masts
    glColor3f(0.3, 0.3, 0.3)
    if num_masts == 1:
        # Single mast in center
        glPushMatrix()
        glTranslatef(0, 0, 35)
        gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
        glPopMatrix()
    elif num_masts == 2:
        # Draw first mast - front
        glPushMatrix()
        glTranslatef(70, 0, 35)
        gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
        glPopMatrix()
        
        # Draw second mast - rear
        glPushMatrix()
        glTranslatef(-70, 0, 35)
        gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
        glPopMatrix()
    
    # Draw sails
    if current_sail_state > 0 or sail_state_override is not None:
        glColor3f(*sail_color)
        sail_width = 42 if current_sail_state == 1 else 60
        sail_height = 48 if current_sail_state == 1 else 75
        
        if num_masts == 1:
            # Single sail in center
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
        elif num_masts == 2:
            # Front mast sail
            glPushMatrix()
            glTranslatef(70, 0, 90)
            glRotatef(90, 0, 0, 1)
            glBegin(GL_QUADS)
            glVertex3f(-sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, 0)
            glVertex3f(-sail_width, 0, 0)
            glEnd()
            glPopMatrix()
            
            # Rear mast sail
            glPushMatrix()
            glTranslatef(-70, 0, 90)
            glRotatef(90, 0, 0, 1)
            glBegin(GL_QUADS)
            glVertex3f(-sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, sail_height)
            glVertex3f(sail_width, 0, 0)
            glVertex3f(-sail_width, 0, 0)
            glEnd()
            glPopMatrix()
    
    # Draw cannons
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


def draw_ocean():
    glPushMatrix()
    # Draw ocean as multiple quads in a grid pattern
    tile_size = 100
    tiles = 30  # Number of tiles in each direction
    
    # Calculate which tile the ship is on
    ship_tile_x = int(ship_x / tile_size)
    ship_tile_y = int(ship_y / tile_size)
    
    # Draw tiles centered around the ship's position
    for i in range(ship_tile_x - tiles, ship_tile_x + tiles):
        for j in range(ship_tile_y - tiles, ship_tile_y + tiles):
            # Alternate colors for checkerboard pattern
            # Darken ocean during storm
            if storm_active:
                if (i + j) % 2 == 0:
                    glColor3f(0.15, 0.3, 0.35)  # Dark gray-blue
                else:
                    glColor3f(0.2, 0.35, 0.4)  # Slightly lighter dark gray-blue
            else:
                if (i + j) % 2 == 0:
                    glColor3f(0.2, 0.6, 0.8)  # Brighter blue
                else:
                    glColor3f(0.3, 0.7, 0.9)  # Even brighter blue
            
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


def spawn_enemy():
    """Spawn a new enemy ship at a random position around the player"""
    # Spawn at distance 1500-2000 from player (further away)
    angle = random.uniform(0, 360)
    distance = random.uniform(1500, 2000)
    
    rad = math.radians(angle)
    x = ship_x + distance * math.cos(rad)
    y = ship_y + distance * math.sin(rad)
    
    enemy = {
        'x': x,
        'y': y,
        'z': 50,
        'rotation': 0,
        'health': enemy_health,
        'last_fire_time': 0,
        'sinking': False,
        'sink_depth': 50
    }
    enemies.append(enemy)
    print(f"Enemy ship spawned! Total enemies: {len(enemies)}")


def update_enemy_ai():
    """Update enemy ship AI - movement, positioning, and firing"""
    enemies_to_remove = []
    
    for enemy in enemies:
        if enemy['sinking']:
            # Sink the enemy ship
            if enemy['sink_depth'] > -35:
                enemy['sink_depth'] -= 0.5
                enemy['z'] = enemy['sink_depth']
            else:
                enemies_to_remove.append(enemy)
            continue
        
        # Calculate distance and direction to player
        dx = ship_x - enemy['x']
        dy = ship_y - enemy['y']
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 1:
            continue
        
        # Normalize direction
        dir_x = dx / distance
        dir_y = dy / distance
        
        # Calculate angle to player
        angle_to_player = math.degrees(math.atan2(dy, dx))
        
        # Behavior: Position broadside to player at optimal distance
        if distance > enemy_optimal_distance + 50:
            # Move closer to player
            enemy['x'] += dir_x * enemy_speed
            enemy['y'] += dir_y * enemy_speed
            # Face the player while approaching
            enemy['rotation'] = angle_to_player
        elif distance < enemy_optimal_distance - 50:
            # Move away from player
            enemy['x'] -= dir_x * enemy_speed
            enemy['y'] -= dir_y * enemy_speed
            # Face away while retreating
            enemy['rotation'] = angle_to_player + 180
        else:
            # At optimal distance - position broadside (perpendicular)
            # Rotate to be perpendicular to player (90 degrees offset)
            enemy['rotation'] = angle_to_player + 90
            
            # Strafe to maintain broadside position
            # Move perpendicular to the line between ships
            perp_x = -dir_y
            perp_y = dir_x
            enemy['x'] += perp_x * enemy_speed * 0.3
            enemy['y'] += perp_y * enemy_speed * 0.3
        
        # Fire cannons if in range
        if distance <= enemy_attack_range:
            fire_enemy_cannons(enemy)
    
    # Remove fully sunken enemies
    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)


def fire_enemy_cannons(enemy):
    """Fire cannons from enemy ship toward player"""
    current_time = time.time()
    if current_time - enemy['last_fire_time'] < enemy_fire_cooldown:
        return
    
    enemy['last_fire_time'] = current_time
    
    # Calculate direction from enemy to player
    dx = ship_x - enemy['x']
    dy = ship_y - enemy['y']
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance < 1:
        return
    
    # Normalize direction
    dir_x = dx / distance
    dir_y = dy / distance
    
    # Enemy rotation
    rad = math.radians(enemy['rotation'])
    forward_x = math.cos(rad)
    forward_y = math.sin(rad)
    right_x = math.sin(rad)
    right_y = -math.cos(rad)
    
    # Fire from both sides (2 cannons per side for enemies)
    for x_pos in [60, -60]:
        # Right side
        cannon_world_x = enemy['x'] + x_pos * forward_x + 70 * right_x
        cannon_world_y = enemy['y'] + x_pos * forward_y + 70 * right_y
        cannon_world_z = enemy['z'] + 10
        
        cannonballs.append({
            'pos': [cannon_world_x, cannon_world_y, cannon_world_z],
            'dir': [dir_x, dir_y, 0.0],
            'travelled': 0.0,
            'enemy_shot': True  # Mark as enemy shot
        })
        
        # Left side
        cannon_world_x = enemy['x'] + x_pos * forward_x - 70 * right_x
        cannon_world_y = enemy['y'] + x_pos * forward_y - 70 * right_y
        
        cannonballs.append({
            'pos': [cannon_world_x, cannon_world_y, cannon_world_z],
            'dir': [dir_x, dir_y, 0.0],
            'travelled': 0.0,
            'enemy_shot': True
        })


def check_cannonball_hits():
    """Check if cannonballs hit ships"""
    global ship_health, ship_sinking
    
    balls_to_remove = []
    
    for ball in cannonballs:
        # Check if player shot hit an enemy
        if not ball.get('enemy_shot', False):
            for enemy in enemies:
                if enemy['sinking']:
                    continue
                
                dx = ball['pos'][0] - enemy['x']
                dy = ball['pos'][1] - enemy['y']
                dz = ball['pos'][2] - enemy['z']
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < 80:  # Hit detection radius
                    enemy['health'] -= 10
                    balls_to_remove.append(ball)
                    print(f"Enemy hit! Enemy health: {enemy['health']}")
                    
                    if enemy['health'] <= 0:
                        enemy['sinking'] = True
                        print("Enemy ship destroyed!")
                    break
        
        # Check if enemy shot hit player
        else:
            if not ship_sinking:
                dx = ball['pos'][0] - ship_x
                dy = ball['pos'][1] - ship_y
                dz = ball['pos'][2] - ship_z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < 100:  # Hit detection radius for player
                    ship_health -= 10
                    balls_to_remove.append(ball)
                    print(f"Player hit! Health: {ship_health}")
                    
                    if ship_health <= 0:
                        ship_health = 0
                        ship_sinking = True
                        print("Your ship is sinking!")
                    break
    
    # Remove hit cannonballs
    for ball in balls_to_remove:
        if ball in cannonballs:
            cannonballs.remove(ball)


def fire_cannons():
    """Fire cannons from both sides of the ship"""
    global last_fire_time
    
    # Check cooldown
    current_time = time.time()
    if current_time - last_fire_time < fire_cooldown:
        return
    
    # Can't fire when sinking
    if ship_sinking:
        return
    
    last_fire_time = current_time
    
    # Calculate direction the ship is facing
    rad = math.radians(ship_rotation)
    forward_x = math.cos(rad)
    forward_y = math.sin(rad)
    
    # Calculate perpendicular direction (for left and right sides)
    # Right side is 90 degrees clockwise from forward
    right_x = math.sin(rad)
    right_y = -math.cos(rad)
    
    # Fire from right side (all 4 cannons)
    for x_pos in cannon_positions:
        # Calculate cannon world position
        # First rotate the cannon position, then add to ship position
        cannon_local_x = x_pos
        cannon_local_y = cannon_offset
        
        cannon_world_x = ship_x + cannon_local_x * forward_x + cannon_local_y * right_x
        cannon_world_y = ship_y + cannon_local_x * forward_y + cannon_local_y * right_y
        cannon_world_z = ship_z + 10
        
        # Cannonball fires perpendicular to ship (right side)
        cannonballs.append({
            'pos': [cannon_world_x, cannon_world_y, cannon_world_z],
            'dir': [right_x, right_y, 0.0],
            'travelled': 0.0,
            'enemy_shot': False  # Mark as player shot
        })
    
    # Fire from left side (all 4 cannons)
    for x_pos in cannon_positions:
        # Calculate cannon world position
        cannon_local_x = x_pos
        cannon_local_y = -cannon_offset
        
        cannon_world_x = ship_x + cannon_local_x * forward_x + cannon_local_y * right_x
        cannon_world_y = ship_y + cannon_local_x * forward_y + cannon_local_y * right_y
        cannon_world_z = ship_z + 10
        
        # Cannonball fires perpendicular to ship (left side)
        cannonballs.append({
            'pos': [cannon_world_x, cannon_world_y, cannon_world_z],
            'dir': [-right_x, -right_y, 0.0],
            'travelled': 0.0,
            'enemy_shot': False  # Mark as player shot
        })


def update_cannonballs():
    """Update cannonball positions and remove those that have traveled too far"""
    global cannonballs
    
    balls_to_remove = []
    
    for ball in cannonballs:
        # Update position
        ball['pos'][0] += ball['dir'][0] * cannonball_speed
        ball['pos'][1] += ball['dir'][1] * cannonball_speed
        ball['pos'][2] += ball['dir'][2] * cannonball_speed
        
        # Track distance travelled
        ball['travelled'] += cannonball_speed
        
        # Remove if traveled too far (max distance)
        if ball['travelled'] >= cannonball_max_distance:
            balls_to_remove.append(ball)
    
    # Remove marked cannonballs
    for ball in balls_to_remove:
        if ball in cannonballs:
            cannonballs.remove(ball)


def update_ship_movement():
    global ship_x, ship_y, ship_speed
    
    # Stop movement if ship is sinking
    if ship_sinking:
        ship_speed = 0
        return
    
    if sail_state == 0:
        ship_speed = SPEED_NO_SAIL
    elif sail_state == 1:
        ship_speed = SPEED_HALF_SAIL
    else:
        ship_speed = SPEED_FULL_SAIL
    
    if ship_speed > 0:
        rad = math.radians(ship_rotation)
        ship_x += ship_speed * math.cos(rad)
        ship_y += ship_speed * math.sin(rad)


def keyboardListener(key, x, y):
    global sail_state
    
    # Prevent controls when sinking
    if ship_sinking:
        if key == b'r':
            reset_game()
        return
    
    # Raise sails (W key)
    if key == b'w':
        if sail_state < 2:
            sail_state += 1
    
    # Lower sails (S key)
    if key == b's':
        if sail_state > 0:
            sail_state -= 1
    
    # Turn ship left (A key)
    if key == b'a':
        pass  # Handled in specialKeyListener for continuous turning
    
    # Turn ship right (D key)
    if key == b'd':
        pass  # Handled in specialKeyListener for continuous turning
    
    # Reset the game (R key)
    if key == b'r':
        reset_game()
    
    if key == b'\x1b':  #ESC
        glutLeaveMainLoop()


def specialKeyListener(key, x, y):
    global camera_distance, camera_angle, ship_rotation
    
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_distance -= 20
        if camera_distance < 200:
            camera_distance = 200
    
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_distance += 20
        if camera_distance > 1000:
            camera_distance = 1000
    
    # Rotate camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_angle += 5
    
    # Rotate camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5


def mouseListener(button, state, x, y):
    # Disable firing when ship is sinking
    if ship_sinking:
        return
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_cannons()


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    cam_angle_rad = math.radians(ship_rotation + camera_angle)
    cam_x = ship_x - camera_distance * math.cos(cam_angle_rad)
    cam_y = ship_y - camera_distance * math.sin(cam_angle_rad)
    cam_z = camera_distance * 0.4  # Camera height
    gluLookAt(cam_x, cam_y, cam_z, ship_x, ship_y, ship_z, 0, 0, 1)


def update_storm_system():
    """Manage storm timing and state transitions"""
    global storm_active, storm_start_time, last_storm_end_time, rain_initialized
    global game_start_time
    
    current_time = time.time()
    elapsed_game_time = current_time - game_start_time
    
    # Check if storm should start (30 seconds after game start or after enemy destroyed)
    if not storm_active:
        # First storm after 30 seconds
        if elapsed_game_time >= time_until_first_storm and last_storm_end_time == 0:
            start_storm()
        # Subsequent storms happen after enemy destroyed (not implemented yet)
        # For now, just cycle storms every 40 seconds (30 wait + 10 storm)
        elif last_storm_end_time > 0 and (current_time - last_storm_end_time) >= 30:
            start_storm()
    else:
        # Check if storm should end (after 10 seconds)
        if (current_time - storm_start_time) >= storm_duration:
            end_storm()


def start_storm():
    """Start a storm event"""
    global storm_active, storm_start_time, rain_initialized
    storm_active = True
    storm_start_time = time.time()
    rain_initialized = False  # Force rain re-initialization
    initialize_rain()

def end_storm():
    """End the current storm"""
    global storm_active, last_storm_end_time, rain_initialized
    storm_active = False
    last_storm_end_time = time.time()
    rain_initialized = False
    
    # Spawn enemy ship after storm ends
    spawn_enemy()
    print("Storm has ended!")


def apply_storm_damage():
    """Apply damage to ship based on sail state during storm"""
    global ship_health, last_damage_time, ship_sinking
    
    if not storm_active or ship_sinking:
        return
    
    current_time = time.time()
    # Apply damage once per second
    if current_time - last_damage_time >= 1.0:
        if sail_state == 2:  # Full sail
            ship_health -= 5
        elif sail_state == 1:  # Half sail
            ship_health -= 2
        # No sail takes no damage
        
        last_damage_time = current_time
        
        # Check if ship is destroyed
        if ship_health <= 0:
            ship_health = 0
            ship_sinking = True


def update_sinking():
    """Gradually sink the ship into the ocean"""
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


def reset_game():
    global ship_x, ship_y, ship_z, ship_rotation, ship_speed, sail_state
    global storm_active, storm_start_time, last_storm_end_time, game_start_time
    global ship_health, last_damage_time, rain_initialized, ship_sinking
    global cannonballs, last_fire_time, enemies
    
    ship_x = 0
    ship_y = 0
    ship_z = 50
    ship_rotation = 0
    ship_speed = 0
    sail_state = 0
    
    # Reset storm system
    storm_active = False
    storm_start_time = 0
    last_storm_end_time = 0
    game_start_time = time.time()
    rain_initialized = False
    
    # Reset health and sinking
    ship_health = 100
    last_damage_time = 0
    ship_sinking = False
    
    # Reset cannon system
    cannonballs.clear()
    last_fire_time = 0
    
    # Reset enemies
    enemies.clear()
def idle():
    update_ship_movement()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_ocean()
    draw_ship()
    
    # Draw enemy ships
    for enemy in enemies:
        draw_enemy_ship(enemy)
    
    # Draw cannonballs
    for ball in cannonballs:
        draw_cannonball(ball)
    
    # Draw rain if storm is active
    if storm_active:
        draw_rain()
    
    # Display UI text
    draw_text(10, 770, f"Sail State: {['No Sail', 'Half Sail', 'Full Sail'][sail_state]}")
    draw_text(10, 740, f"Health: {ship_health}/{max_health}")
    
    if ship_sinking:
        draw_text(300, 400, "GAME OVER - SHIP SINKING!")
        draw_text(350, 370, "Press R to Restart")
    elif storm_active:
        draw_text(10, 710, "STORM ACTIVE!")
        if sail_state == 2:
            draw_text(10, 680, "Full Sail: -5 HP/sec")
        elif sail_state == 1:
            draw_text(10, 680, "Half Sail: -2 HP/sec")
    
    glutSwapBuffers()

keys_pressed = set()

def keyboard_down(key, x, y):
    keys_pressed.add(key)
    keyboardListener(key, x, y)

def keyboard_up(key, x, y):
    if key in keys_pressed:
        keys_pressed.remove(key)

def update_continuous_keys():
    global ship_rotation
    
    # Can't turn when sinking
    if ship_sinking:
        return
    
    # Can only turn when ship is moving
    if ship_speed > 0:
        # Turn left (A key)
        if b'a' in keys_pressed:
            ship_rotation += TURN_SPEED
            if ship_rotation >= 360:
                ship_rotation -= 360
        
        # Turn right (D key)
        if b'd' in keys_pressed:
            ship_rotation -= TURN_SPEED
            if ship_rotation < 0:
                ship_rotation += 360

def idle_with_keys():
    # When ship is sinking, pause gameplay but continue sinking animation
    if ship_sinking:
        update_sinking()
        glutPostRedisplay()
        return
    
    update_continuous_keys()
    update_ship_movement()
    update_storm_system()
    apply_storm_damage()
    update_sinking()
    update_cannonballs()
    update_enemy_ai()
    check_cannonball_hits()
    if storm_active:
        update_rain()
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Pirate Ship Battle Game")
    
    glEnable(GL_DEPTH_TEST)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle_with_keys)
    
    glutMainLoop()

if __name__ == "__main__":
    main()