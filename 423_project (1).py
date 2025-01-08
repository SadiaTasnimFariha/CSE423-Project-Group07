from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
#Window
W_Width,W_Height= 500,500
snake_size=10
#snake_speed
speed=0.1
score1= 0
score2= 0
direction1= "RIGHT"
direction2= "LEFT"  
player1_snake= [[250, 250]]
player2_snake= [[200, 200]]
food= [random.randint(0, 49) * 10, random.randint(0, 49) * 10]
special_food= None
special_food_timer= 0
obstacles= []

#mode
game_mode= None  

#Directions and movement mapping
directions= {
    "UP":(0, snake_size),
    "DOWN":(0, -snake_size),
    "LEFT":(-snake_size, 0),
    "RIGHT":(snake_size, 0),
}
# Midpoint line drawing algorithm
def draw_midpoint_line(x0, y0, x1, y1):
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        glVertex2f(x0, y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def draw_rect(x, y, size, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    draw_midpoint_line(x, y, x + size, y)
    draw_midpoint_line(x, y + size, x + size, y + size)
    draw_midpoint_line(x, y, x, y + size)
    draw_midpoint_line(x + size, y, x + size, y + size)
    glEnd()

def draw_midpoint_circle(x_center, y_center, radius):
    x = radius
    y = 0
    p = 1 - radius

    while x >= y:

        glVertex2f(x_center + x, y_center + y)
        glVertex2f(x_center - x, y_center + y)
        glVertex2f(x_center + x, y_center - y)
        glVertex2f(x_center - x, y_center - y)
        glVertex2f(x_center + y, y_center + x)
        glVertex2f(x_center - y, y_center + x)
        glVertex2f(x_center + y, y_center - x)
        glVertex2f(x_center - y, y_center - x)
        y += 1
        if p <= 0:
            p += 2 * y + 1
        else:
            x -= 1
            p += 2 * (y - x) + 1


#snake
def draw_snake(snake, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for part in snake:
        x,y= part
        for i in range(x,x+snake_size):
            for j in range(y,y+snake_size):
                glVertex2f(i,j)
    glEnd()
#food
def draw_food():
    x, y = food
    radius = snake_size // 2  # Adjust size to match the grid
    glColor3f(1.0, 0.0, 0.0)  # Food color (Red)
    glBegin(GL_POINTS)
    draw_midpoint_circle(x + radius, y + radius, radius)
    glEnd()

#special_food
def draw_special_food():
    if special_food:
        x, y = special_food
        glColor3f(0.0, 1.0, 1.0)  # Cyan color for special food
        glBegin(GL_POINTS)
        draw_midpoint_line(x, y, x + snake_size, y)  # Top border
        draw_midpoint_line(x, y + snake_size, x + snake_size, y + snake_size)  # Bottom border
        draw_midpoint_line(x, y, x, y + snake_size)  # Left border
        draw_midpoint_line(x + snake_size, y, x + snake_size, y + snake_size)  # Right border
        glEnd()
#obstacles
def draw_obstacles():
    for obstacle in obstacles:
        x, y = obstacle
        glColor3f(0.5, 0.5, 0.5)  # Gray color for obstacles
        glBegin(GL_POINTS)
        draw_midpoint_line(x, y, x + snake_size, y)  # Top border
        draw_midpoint_line(x, y + snake_size, x + snake_size, y + snake_size)  # Bottom border
        draw_midpoint_line(x, y, x, y + snake_size)  # Left border
        draw_midpoint_line(x + snake_size, y, x + snake_size, y + snake_size)  # Right border
        glEnd()
#snake movements based on direction
def move_snake(snake, direction):
    if not snake:
        return
    x_change, y_change = directions[direction]
    new_head = [snake[0][0]+ x_change, snake[0][1]+ y_change]
    snake.insert(0, new_head)
#collison with own body or screen limit
def check_collision(snake, boundaries=True):
    if not snake:  
        return True
    head= snake[0]
    if head in snake[1:]: 
        return True
    if boundaries and (head[0]< 0 or head[0]>= W_Width or head[1]<0 or head[1]>= W_Height):
        return True
    return False
#position of special food
def generate_special_food():
    global special_food, special_food_timer
    while True:
        special_food = [random.randint(0, 49) * 10, random.randint(0, 49) * 10]
        if special_food not in player1_snake and special_food not in player2_snake and special_food not in obstacles and special_food != food:
            break
    special_food_timer = time.time()
def add_obstacle():
    while True:
        obstacle = [random.randint(0, 49) * 10, random.randint(0, 49) * 10]
        if obstacle not in player1_snake and obstacle not in player2_snake and obstacle not in obstacles and obstacle != food and obstacle != special_food:
            obstacles.append(obstacle)
            break

#updating the score when body collisioning with food
def check_food_collision(snake, score):
    global food, special_food, obstacles
    if snake[0]== food:
        score+= 1
        food= [random.randint(0, 49) * 10, random.randint(0, 49) * 10]
        if score % 4== 0:
            generate_special_food()
        return True, score

    if special_food and snake[0]== special_food:
        score+= 3
        special_food= None
        obstacles.append([random.randint(0, 49)* 10,random.randint(0, 49)* 10])
        return True, score

    return False, score
#based on mod snake placement and color 
def render_scene():
    glClear(GL_COLOR_BUFFER_BIT)

    if game_mode == 'single' or game_mode == 'duo':
        draw_snake(player1_snake, (0.0, 1.0, 0.0))  
        if game_mode == 'duo':
            draw_snake(player2_snake, (0.0, 0.0, 1.0))  
        draw_food()
        draw_special_food()
        draw_obstacles()

#scorecard
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(10, W_Height - 20)
        for character in f"Player 1: {score1}":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

        if game_mode == 'duo':
            glRasterPos2f(10, W_Height - 40)
            for character in f"Player 2: {score2}":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
#front page
    else:
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(W_Width/2-50, W_Height/ 2+20)
        for character in "Press 1 for Single Player":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

        glRasterPos2f(W_Width/2 -50, W_Height/ 2-20)
        for character in "Press 2 for Two Player":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    glutSwapBuffers()

def update_scene(value):
    global score1, score2, special_food, special_food_timer
    if game_mode == 'single':
        move_snake(player1_snake, direction1)
        collision1, score1= check_food_collision(player1_snake, score1)
        if not collision1:
            if len(player1_snake) > 1: 
                player1_snake.pop()
        if check_collision(player1_snake) or player1_snake[0] in obstacles:
            print(f"Game Over! Final Score: Player 1 - {score1}")
            glutLeaveMainLoop()

    if game_mode== 'duo':
        move_snake(player1_snake, direction1)
        move_snake(player2_snake, direction2)

        collision1, score1= check_food_collision(player1_snake, score1)
        collision2, score2= check_food_collision(player2_snake, score2)

        if not collision1:
            if len(player1_snake)> 1:  
                player1_snake.pop()
        if not collision2:
            if len(player2_snake)> 1:  
                player2_snake.pop()
        if check_collision(player1_snake) or player1_snake[0] in obstacles:
            print(f"Player 1 lost! Player 2 wins!")
            print(f"Final Scores - Player 1: {score1}, Player 2: {score2}")
            glutLeaveMainLoop()

        if check_collision(player2_snake) or player2_snake[0] in obstacles:
            print(f"Player 2 lost! Player 1 wins!")
            print(f"Final Scores - Player 1: {score1}, Player 2: {score2}")
            glutLeaveMainLoop()
    if special_food and time.time()-special_food_timer> 5:
        special_food= None

    glutPostRedisplay()
    glutTimerFunc(int(1000 * speed), update_scene, 0)

#controlling the snake and selecting the mode
def keyboard_listener(key, x, y):
    global direction1, direction2, game_mode
    if game_mode is None: 
        if key== b'1':  
            game_mode= 'single'
            print("Single Player Mode Selected")
        elif key== b'2':  
            game_mode= 'duo'
            print("Two Player Mode Selected")
        return

    if game_mode== 'single':
        if key== b'\x1b':  
            glutLeaveMainLoop()

        if key==b'w' and direction1!= "DOWN": direction1= "UP"
        if key==b's' and direction1!= "UP": direction1= "DOWN"
        if key==b'a' and direction1!= "RIGHT": direction1= "LEFT"
        if key==b'd' and direction1!= "LEFT": direction1= "RIGHT"

    if game_mode== 'duo':
        if key== b'i' and direction2!= "DOWN": direction2= "UP"
        if key== b'k' and direction2!= "UP": direction2= "DOWN"
        if key== b'j' and direction2!= "RIGHT": direction2= "LEFT"
        if key== b'l' and direction2!= "LEFT": direction2= "RIGHT"


def special_keyboard_listener(key, x, y):
    global direction1, direction2

    if key== GLUT_KEY_UP and direction1!= "DOWN":
        direction1= "UP"
    elif key== GLUT_KEY_DOWN and direction1 != "UP":
        direction1= "DOWN"
    elif key== GLUT_KEY_LEFT and direction1 != "RIGHT":
        direction1= "LEFT"
    elif key== GLUT_KEY_RIGHT and direction1!= "LEFT":
        direction1= "RIGHT"

    #for player 2
    if key== GLUT_KEY_F1 and direction2 != "DOWN":
        direction2 = "UP"
    if key== GLUT_KEY_F2 and direction2!= "UP":
        direction2 = "DOWN"
    if key== GLUT_KEY_F3 and direction2!= "RIGHT":
        direction2 = "LEFT"
    if key== GLUT_KEY_F4 and direction2 != "LEFT":
        direction2 = "RIGHT"
#opengl
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glOrtho(0, W_Width, 0, W_Height, -1, 1)

# Main program
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
glutInitWindowSize(W_Width, W_Height)
glutCreateWindow(b"Snake Game")  
glutDisplayFunc(render_scene)
glutKeyboardFunc(keyboard_listener)   
glutSpecialFunc(special_keyboard_listener)  
init()
glutTimerFunc(0, update_scene, 0)
glutMainLoop()
