from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Camera-related variables
camera_pos = (0, 500, 500)
camera_distance = 500
camera_angle = 0  # Angle around the ship

fovY = 120  # Field of view
GRID_LENGTH = 600  # Length of grid lines

# Ship state variables
ship_x = 0
ship_y = 0
ship_z = 50  # Ship height above water
ship_rotation = 0  # Ship facing direction (0-360 degrees)
ship_speed = 0
sail_state = 0  # 0 = no sail, 1 = half sail, 2 = full sail

# Speed constants
SPEED_NO_SAIL = 0
SPEED_HALF_SAIL = 2
SPEED_FULL_SAIL = 4
TURN_SPEED = 2  # Degrees per frame
MOMENTUM_DECAY = 0.95  # Speed decay when lowering sails


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_ship():
    glPushMatrix()
    
    # Position ship at current location
    glTranslatef(ship_x, ship_y, ship_z)
    glRotatef(ship_rotation, 0, 0, 1)  # Rotate ship to face direction
    
    # Draw hull (brown cuboid)
    glColor3f(0.4, 0.2, 0.1)  # Brown color
    glPushMatrix()
    glScalef(2.5, 1.2, 0.8)  # Make hull elongated and larger
    glutSolidCube(60)
    glPopMatrix()
    
    # Draw mast (gray cylinder)
    glColor3f(0.3, 0.3, 0.3)  # Gray color
    glPushMatrix()
    glTranslatef(0, 0, 30)  # Position above hull
    gluCylinder(gluNewQuadric(), 5, 5, 100, 10, 10)
    glPopMatrix()
    
    # Draw sail based on sail_state (white quad)
    if sail_state > 0:
        glColor3f(0.9, 0.9, 0.9)  # White/light gray
        glPushMatrix()
        glTranslatef(0, 0, 60)  # Position on mast
        
        # Sail size depends on sail state
        sail_width = 35 if sail_state == 1 else 50
        sail_height = 40 if sail_state == 1 else 65
        
        glBegin(GL_QUADS)
        glVertex3f(-sail_width, 0, sail_height)
        glVertex3f(sail_width, 0, sail_height)
        glVertex3f(sail_width, 0, 0)
        glVertex3f(-sail_width, 0, 0)
        glEnd()
        glPopMatrix()
    
    # Draw cannons (small cylinders on sides)
    glColor3f(0.2, 0.2, 0.2)  # Dark gray
    glPushMatrix()
    glTranslatef(0, 40, 15)  # Left side
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 15, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, -40, 15)  # Right side
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 15, 8, 8)
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
            if (i + j) % 2 == 0:
                glColor3f(0.0, 0.3, 0.5)  # Darker blue
            else:
                glColor3f(0.0, 0.4, 0.6)  # Lighter blue
            
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


def update_ship_movement():
    global ship_x, ship_y, ship_speed
    
    # Target speed based on sail state
    if sail_state == 0:
        target_speed = SPEED_NO_SAIL
    elif sail_state == 1:
        target_speed = SPEED_HALF_SAIL
    else:
        target_speed = SPEED_FULL_SAIL
    
    # Apply momentum - gradually adjust to target speed
    if ship_speed > target_speed:
        ship_speed *= MOMENTUM_DECAY
        if ship_speed < 0.1:
            ship_speed = 0
    else:
        ship_speed = target_speed
    
    # Move ship forward in the direction it's facing
    if ship_speed > 0:
        rad = math.radians(ship_rotation)
        ship_x += ship_speed * math.cos(rad)
        ship_y += ship_speed * math.sin(rad)


def keyboardListener(key, x, y):
    global sail_state
    
    # Raise sails (W key)
    if key == b'w':
        if sail_state < 2:
            sail_state += 1
            print(f"Sail state: {['No Sail', 'Half Sail', 'Full Sail'][sail_state]}")
    
    # Lower sails (S key)
    if key == b's':
        if sail_state > 0:
            sail_state -= 1
            print(f"Sail state: {['No Sail', 'Half Sail', 'Full Sail'][sail_state]}")
    
    # Turn ship left (A key)
    if key == b'a':
        pass  # Handled in specialKeyListener for continuous turning
    
    # Turn ship right (D key)
    if key == b'd':
        pass  # Handled in specialKeyListener for continuous turning
    
    # Reset the game (R key)
    if key == b'r':
        reset_game()


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
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        print("Fire cannons!")


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


def reset_game():
    global ship_x, ship_y, ship_z, ship_rotation, ship_speed, sail_state
    ship_x = 0
    ship_y = 0
    ship_z = 50
    ship_rotation = 0
    ship_speed = 0
    sail_state = 0
    print("Game reset!")


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
    draw_text(10, 770, f"Sail State: {['No Sail', 'Half Sail', 'Full Sail'][sail_state]}")
    draw_text(10, 740, f"Speed: {ship_speed:.1f}")
    draw_text(10, 710, f"Position: ({ship_x:.0f}, {ship_y:.0f})")
    draw_text(10, 680, f"Rotation: {ship_rotation:.0f}°")
    draw_text(10, 620, "Controls: W/S - Sails | A/D - Turn | Arrows - Camera | R - Reset")
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
    update_continuous_keys()
    update_ship_movement()
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
