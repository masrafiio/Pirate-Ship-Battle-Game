from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

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


def draw_ship():
    glPushMatrix()
    glTranslatef(ship_x, ship_y, ship_z)
    glRotatef(ship_rotation, 0, 0, 1)
    
    #draw hull
    glColor3f(0.4, 0.2, 0.1)
    glPushMatrix()
    glScalef(4.2, 1.8, 1.0)
    glutSolidCube(70)
    glPopMatrix()

    #draw bow
    glColor3f(0.35, 0.18, 0.09)
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
    
    # Draw first mast - front
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(70, 0, 35)
    gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
    glPopMatrix()
    
    # Draw second mast - rear
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(-70, 0, 35)
    gluCylinder(gluNewQuadric(), 6, 6, 150, 10, 10)
    glPopMatrix()
    
    # Draw sails
    if sail_state > 0:
        glColor3f(0.9, 0.9, 0.9)
        sail_width = 42 if sail_state == 1 else 60
        sail_height = 48 if sail_state == 1 else 75
        
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


def update_ship_movement():
    global ship_x, ship_y, ship_speed
    
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
