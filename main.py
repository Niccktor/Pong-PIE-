import time
import pygame
import random
import serial
import threading
import sys

# pyfirmata pour faire le lien entre Arduino et python
# https://pyfirmata.readthedocs.io/en/latest/
# https://arduinofactory.fr/pyfirmata/

def num_len(str):
    i = 0
    while str[i] >= '0' and str[i] <= '9':
        i +=1
    return i
def EXIT():
    global kill_thread
    pygame.quit()
    kill_thread = True
    x.join(timeout=5)
    sys.exit()

# Besoin de thread pour ne pas influencer sur le jeu

def Arduino_thread():
    global moyenne
    global moyenne2
    moyenne2 = 0
    moyenne = 0
    value1 = 0
    i1 = 0

    value2 = 0
    i2 = 0
    while True :
        if kill_thread:
            break
        payload = arduino.readline().decode('UTF-8')
        if payload.startswith('a'):
            payload = payload[1:]
            payload = payload[0:num_len(payload)]
            value1 += int(payload)
            #print(payload)
            i1 += 1
            if (value1 > 400):
                value1 = moyenne
            if i1 > 4:
                value1 = value1 / 4
                moyenne = value1
                value1 = 0
                i1 = 0
                #print(moyenne)
        elif payload.startswith('b'):
            payload = payload[1:]
            payload = payload[0:num_len(payload)]
            value2 += int(payload)
            i2 += 1
            if (value2 > 400):
                value2 = moyenne2
            if i2 > 4:
                value2 = value2 / 4
                moyenne2 = value2
                value2 = 0
                i2 = 0
                #print(moyenne2)






def event_handler():
    global player_1_speed
    global player_2_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            arduino.close()
            x.join()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                EXIT()
            if event.key == pygame.K_UP:
                player_1_speed = -7
            if event.key == pygame.K_DOWN:
                player_1_speed = 7
            if event.key == pygame.K_z:
                player_2_speed = -7
            if event.key == pygame.K_s:
                player_2_speed = 7
        if event.type == pygame.KEYUP:
#            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
#               player_1_speed = 0
            if event.key == pygame.K_w or event.key == pygame.K_s:
                player_2_speed = 0

def ball_movement():
    global ball_speed_x
    global ball_speed_y
    global score_1
    global score_2

    ball.x += ball_speed_x
    ball.y += ball_speed_y
    if ball.top <= 0 or ball.bottom >= height_screen:
        ball_speed_y *= -1
        wall_sound.play(0)
    if ball.left <= 0 or ball.right >= width_screen:
        if random.randint(1,100) != 100:
            la_chatte.play(0)
        else:
            score_sound.play(0)
        if ball.left <= 0:
            score_1 += 1
        else:
            score_2 += 1
        ball_restart()

    if ball.colliderect(player_2) or ball.colliderect(player_1):
        ball_speed_x *= -1.05
        paddle_sound.play(0)
        print("Ball speed x : ", ball_speed_x, "ball speed y : ", ball_speed_y)

def player_movement():
    #player_2.y += player_2_speed
    #player_1.y += player_1_speed

    if moyenne > 10 and moyenne < 100:
        player_1.y = (height_screen / 60) * (moyenne - 30)
    if moyenne2 > 10 and moyenne2 < 100:
        player_2.y = (height_screen / 60) * (moyenne2 - 30)

    if player_1.top <= 0:
        player_1.top = 0
    if player_1.bottom >= height_screen:
        player_1.bottom = height_screen

    if player_2.top <= 0:
        player_2.top = 0
    if player_2.bottom >= height_screen:
        player_2.bottom = height_screen

def ball_restart():
    global ball_speed_x
    global ball_speed_y

    ball.center = (width_screen / 2, height_screen / 2)
    ball_speed_x = 7 * random.choice((1, -1))
    ball_speed_y = 7 * random.choice((1, -1))
    while pygame.mixer.get_busy():
        event_handler()
        player_movement()
        render()
        clock.tick(60)

def render():
    # Fill background
    screen.fill(background_color)

    # Affichage Score
    score_2_img = font.render(str(score_2), True, pygame.Color('green'))
    score_1_img = font.render(str(score_1), True, pygame.Color('red'))
    screen.blit(score_1_img, ((width_screen / 4 * 3) - score_1_img.get_width() / 2, 20))
    screen.blit(score_2_img, (width_screen / 4 - score_2_img.get_width() / 2, 20))

    # Affichage Joueurs 1 et 2
    pygame.draw.rect(screen, player_1_color, player_1)
    pygame.draw.rect(screen, player_2_color, player_2)

    # Affichage milieu terrain
    pygame.draw.aaline(screen, line_color, [width_screen/2, 0], [width_screen/2, height_screen])
    pygame.draw.ellipse(screen, ball_color, ball)

    # Update screen
    pygame.display.flip()


kill_thread = False
arduino = serial.Serial('COM7', 9600)
x = threading.Thread(target=Arduino_thread)
x.start()



"""
arduino = PyMata("COM9")
arduino.sonar_config(8, 7)
data = arduino.get_sonar_data()
"""
"""
port = 'COM9'
HIGH = True
LOW = False
kill_thread = False
arduino = pyfirmata.Arduino(port)
ECHO_pin = arduino.get_pin('d:7:i')
TRIG_pin = arduino.get_pin('d:8:o')
# LED_pin = arduino.get_pin('d:8:o')
x = threading.Thread(target=Arduino_thread)
x.start()
"""
"""
#https://github.com/tino/pyFirmata/pull/45/files/c476236847cd8bb655c0fb645a1ce69b28d0e2d2
ECHO_pin = arduino.get_pin('d:7:o')
TRIG_pin = arduino.get_pin('d:8:i')

TRIG_pin.write(HIGH)
time.sleep(20/1000)
TRIG_pin.write(LOW)
dist = ECHO_pin.ping()
"""

# Générer la fenêtre
pygame.init()
clock = pygame.time.Clock()
width_screen = 1245
height_screen = 934
screen = pygame.display.set_mode((width_screen, height_screen))
pygame.display.set_caption("PIE 2022 Pong")
background_color = pygame.Color('grey43')

# Style du text
font = pygame.font.SysFont(None, 400)

# Sound Effect load
paddle_sound = pygame.mixer.Sound(r'Sound\paddle.wav')
wall_sound = pygame.mixer.Sound(r'sound\wall.wav')
score_sound = pygame.mixer.Sound(r'sound\score.wav')
la_chatte = pygame.mixer.Sound(r'sound\chatte.wav')

# Ball
ball_size = 40
ball = pygame.Rect(width_screen / 2 - ball_size / 2, height_screen / 2 - ball_size / 2, ball_size, ball_size)
ball_color = pygame.Color('blue')
ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))


# Player 1
player_1 = pygame.Rect((width_screen - 20), (height_screen / 2 - 70), 10, 140)
player_1_color = pygame.Color('red')
player_1_speed = 0
score_1 = 0


# Player 2
player_2 = pygame.Rect(10, (height_screen / 2 - 70), 10, 140)
player_2_color = pygame.Color('green')
player_2_speed = 0
score_2 = 0


# line
line_color = pygame.Color('grey12')
time.sleep(2)
while True:

    # Keyboard event
    event_handler()

    # Animation
    if True :
        ball_movement()
    player_movement()

    # Visuals
    render()
    clock.tick(60)
