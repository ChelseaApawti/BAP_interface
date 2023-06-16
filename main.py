import threading
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import sleep

import ctypes
import random
import sys
from time import sleep

import matplotlib
import mne
import pygame
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.pyplot import subplots


# Check type of collision between the ball and a brick
def check_which_collision(ball, brick):
    if ball.speedX > 0:
        delta_x = ball.rect.right - brick.left
    else:
        delta_x = brick.right - ball.rect.left
    if ball.speedY > 0:
        delta_y = ball.rect.bottom - brick.top
    else:
        delta_y = brick.bottom - ball.rect.top
    if abs(delta_x - delta_y) < 10:
        ball.speedX *= -1
        ball.speedY *= -1
    if delta_x > delta_y:
        ball.speedY *= -1
    elif delta_x < delta_y:
        ball.speedX *= -1


# Class for paddles
class Rectangle(pygame.sprite.Sprite):
    def __init__(self, color, width, height, speed, posX, posY):
        super().__init__()
        self.color = color
        self.width = width
        self.height = height
        self.speed = speed
        self.posX = posX
        self.posY = posY
        self.rect = pygame.Rect(posX, posY, width, height)

        self.image = pygame.Surface([width, height])
        self.image.fill(black)
        self.image.set_colorkey(black)

        pygame.draw.rect(self.image, color, [0, 0, width, height])

    # Move the paddle to the left but no further than the left field boundary
    def move_player_left(self):
        if self.rect.left > 0:
            self.rect.x -= self.speed
        return

    # Move the paddle to the right but no further than the right field boundary
    def move_player_right(self):
        if self.rect.right < screen_width:
            self.rect.x += self.speed
        return

    # Move the paddle up but no further than the upper field boundary
    def move_player_up(self):
        if self.rect.top > 0:
            self.rect.y -= self.speed
        return

    # Move the paddle down but no further than the lower field boundary
    def move_player_down(self):
        if self.rect.bottom < screen_height:
            self.rect.y += self.speed
        return


# Class for the ball
class Ball(pygame.sprite.Sprite):
    def __init__(self, color, size, speedX, speedY, posX, posY, width, height):
        super().__init__()
        self.color = color
        self.size = size
        self.speedX = speedX
        self.speedY = speedY
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.rect = pygame.Rect(posX, posY, size, size)
        self.invisibleRect = pygame.Rect(posX, posY, size, size)
        self.speedX = speedX
        self.playerCollisions = 0

        self.image = pygame.Surface([width, height])
        self.image.fill(black)
        self.image.set_colorkey(black)

        pygame.draw.ellipse(self.image, white, [0, 0, width, height])

    # Update the ball for pong based on events
    def updateBall_pong(self, player, AI):
        global AIScore
        global playerScore
        # Update ball speed based on which collision:
        # - Collision with upper boundary or lower boundary
        if self.rect.top < 0 or self.rect.bottom > screen_height:
            self.speedY *= -1

        # - Collision with left or right boundary --> player or AI gets a point, ball resets to starting position
        elif self.rect.left < 0:
            AIScore += 1
            self.reset()
        elif self.rect.right > screen_width:
            playerScore += 1
            self.reset()

        # - Collision with player's or AI's paddle
        elif self.rect.colliderect(AI) or self.rect.colliderect(player):
            self.speedX *= -1

        # Update ball position based on speed
        self.rect.x += self.speedX
        self.rect.y += self.speedY
        return

    # Update the ball for breakout based on events
    def updateBall_breakout(self, player):
        global playerLives
        # Update ball speed based on which collision:
        # - Collision with upper boundary
        if self.rect.top < 0:
            self.speedY *= -1

        # - Collision with lower boundary --> player loses a life, ball resets to starting position
        elif self.rect.bottom > screen_height:
            playerLives -= 1
            self.reset()

        # - Collision with left or right boundary
        elif self.rect.left < 0 or self.rect.right > screen_width:
            self.speedX *= -1

        # - Collision with player's paddle
        elif self.rect.colliderect(player):
            if self.speedX > 0:
                delta_x = self.rect.right - player.rect.left
            else:
                delta_x = player.rect.right - self.rect.left
            if self.speedY > 0:
                delta_y = self.rect.bottom - player.rect.top
            else:
                delta_y = player.rect.bottom - self.rect.top
            if abs(delta_x - delta_y) < 10:
                self.speedX *= -1
                self.speedY *= -1
            elif delta_x > delta_y:
                self.speedY *= -1
            elif delta_x < delta_y:
                self.speedX *= -1

        # Update ball position based on speed
        self.rect.x += self.speedX
        self.rect.y += self.speedY
        return

    # Reset ball to starting position, launch ball into random direction
    def reset(self):
        sleep(2)
        self.rect = pygame.Rect(self.posX, self.posY, self.size, self.size)
        self.speedX *= random.choice([-1, 1])
        self.speedY *= random.choice([-1, 1])


# Class for button (menu options)
class ButtonRect:
    def __init__(self, width, height, posX, posY):
        self.width = width
        self.height = height
        self.posX = posX
        self.posY = posY
        self.invisibleRect = pygame.Rect(posX, posY, width, height)


# Class for text on buttons (menu options)
class ButtonText:
    def __init__(self, color1, color2, posX, posY):
        self.color1 = color1
        self.color2 = color2
        self.color = color1
        self.posX = posX
        self.posY = posY

    # Text is a certain color if cursor hovers over the button
    def Button_hover(self, words):
        self.color = self.color2
        self.Button_render(words)
        return

    # Text is a certain color is cursor does not hover over the button
    def Button_unhover(self, words):
        self.color = self.color1
        self.Button_render(words)
        return

    # Render and blit the text of the button on the screen
    def Button_render(self, words):

        text = font.render(words, True, self.color)
        screen.blit(text, (self.posX, self.posY))
        return


def interface():
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    pygame.init()
    pygame.font.init()
    info = pygame.display.Info()
    global screen_width
    global screen_height
    screen_width, screen_height = info.current_w, info.current_h
    global screen
    screen = pygame.display.set_mode((screen_width, screen_height))

    # Global variables
    global playerScore
    global AIScore
    global playerLives
    playerScore = 0
    AIScore = 0
    playerLives = 3
    gameState = 'start_menu'
    sensor_change = 1

    # Color definitions
    global black, white, red, blue, orange, yellow, green
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    orange = (255, 119, 34)
    yellow = (255, 225, 0)
    green = (102, 204, 0)

    # Create background to overwrite each frame
    background = pygame.Surface((screen.get_width(), screen.get_height()))
    background.fill(black)

    # Frame rate
    gameClock = pygame.time.Clock()
    FPS = 120

    # Speeds
    ballSpeed = 3
    rectangleSpeed = 6
    cursorSpeed = 2

    # Object dimensions
    ballWidth = 15
    ballHeight = 15
    paddleWidth = 10
    paddleHeight = 100

    BrickWidth = 120
    BrickHeight = 50

    # Lists that contain all the sprites intended for use in the games
    all_sprites_list_pong = pygame.sprite.Group()
    all_sprites_list_breakout = pygame.sprite.Group()

    # Font sizes
    global font
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 60)

    # PONG:
    # Render scores for the player and AI
    scorePlayer = font.render(str(playerScore), True, red)
    scoreAI = font.render(str(AIScore), True, red)

    # Create button (menu option) for pong
    pongRect = ButtonRect(80, 20, screen_width / 2 - 50, screen_height / 2)
    pongText = ButtonText(white, blue, screen_width / 2 - 50, screen_height / 2)
    pongText.Button_render('PONG')

    # Create objects
    player_pong = Rectangle(white, paddleWidth, paddleHeight, rectangleSpeed, 40, screen_height / 2)
    AI = Rectangle(white, paddleWidth, paddleHeight, rectangleSpeed, screen_width - 50, screen_height / 2)
    ball = Ball(white, 15, ballSpeed, -ballSpeed, screen_width / 2, screen_height / 2, ballWidth, ballHeight)
    pygame.mouse.set_pos(random.randint(0, screen_width - 20), random.randint(0, screen_height - 20))
    pygame.display.flip()

    # Add objects to list
    all_sprites_list_pong.add(player_pong)
    all_sprites_list_pong.add(AI)
    all_sprites_list_pong.add(ball)

    # BREAKOUT:
    # Render lives of the player
    livesPlayer = font.render(str(playerLives), True, red)

    # Create button (menu option) for breakout
    breakoutRect = ButtonRect(80, 20, screen_width / 2 - 82, screen_height / 2 + 50)
    breakoutText = ButtonText(white, blue, screen_width / 2 - 82, screen_height / 2 + 50)
    breakoutText.Button_render('BREAKOUT')

    # Create objects
    player_breakout = Rectangle(white, paddleHeight, paddleWidth, rectangleSpeed, screen_width / 2, screen_height - 40)
    pygame.mouse.set_pos(random.randint(0, screen_width - 20), random.randint(0, screen_height - 20))
    pygame.display.flip()

    brick_colors = [red, orange, yellow, green, blue]

    # Add objects to list
    brick_list = [pygame.Rect(40 + i * (BrickWidth + 10), 40 + j * (BrickHeight + 10), BrickWidth, BrickHeight) for i in
                  range(14) for j in range(4)]
    all_sprites_list_breakout.add(player_breakout)
    all_sprites_list_breakout.add(ball)

    # CALIBRATION:
    # Create button (menu option) for calibration screen
    calRect = ButtonRect(80, 20, screen_width / 2 - 100, screen_height / 2 + 100)
    calibrationText = ButtonText(white, blue, screen_width / 2 - 100, screen_height / 2 + 100)
    calibrationText.Button_render('CALIBRATION')

    # Create montage and info
    standard_montage = mne.channels.make_standard_montage('biosemi16')
    n_channels = len(standard_montage.ch_names)
    info = mne.create_info(standard_montage.ch_names, 250, 'eeg')
    info.set_montage(standard_montage)
    # channel_names = ['Fp1', 'Fp2', 'F4', 'Fz', 'F3', 'T7', 'C3', 'Cz', 'C4', 'T8', 'P4', 'Pz', 'P3', 'O1', 'Oz', 'O2']
    channel_groups = [[0, 1, 2], [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]

    # Create legend
    legend_elements = [Line2D([0], [0], marker='o', label='Connected sensor',
                              markerfacecolor="#000080", markersize=22),
                       Line2D([0], [0],
                              lw=0),
                       Line2D([0], [0], marker='o', label='Unconnected sensor',
                              markerfacecolor="#800000", markersize=22)
                       ]

    # Create display of electrode impedances
    impRect = ButtonRect(80, 20, 1200, 150)
    impText = ButtonText(white, white, 1200, 150)
    impText.Button_render('Electrode impedances')

    fp1Rect = ButtonRect(80, 20, 1150, 200)
    fp1Text = ButtonText(white, white, 1150, 200)
    fp1Text.Button_render('Fp1:')

    fp2Rect = ButtonRect(80, 20, 1150, 250)
    fp2Text = ButtonText(white, white, 1150, 250)
    fp2Text.Button_render('Fp2:')

    f4Rect = ButtonRect(80, 20, 1150, 300)
    f4Text = ButtonText(white, white, 1150, 300)
    f4Text.Button_render('F4:')

    # Game loop
    while True:
        gameClock.tick(FPS)

        # Exit interface if escape is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # START MENU:
        if gameState == 'start_menu':

            # Exit interface if escape is pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            # If mouse hovers over an option, let its text change color
            # Go to the respective game state if the option gets selected
            mousePOS = pygame.mouse.get_pos()
            if pongRect.invisibleRect.collidepoint(mousePOS[0], mousePOS[1]):
                pongText.Button_hover('PONG')
                breakoutText.Button_unhover('BREAKOUT')
                calibrationText.Button_unhover('CALIBRATION')
                mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]
                if mouse_pressed:
                    gameState = 'pong_game'
            elif breakoutRect.invisibleRect.collidepoint(mousePOS[0], mousePOS[1]):
                breakoutText.Button_hover('BREAKOUT')
                pongText.Button_unhover('PONG')
                calibrationText.Button_unhover('CALIBRATION')
                mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]
                if mouse_pressed:
                    gameState = 'breakout_game'
            elif calRect.invisibleRect.collidepoint(mousePOS[0], mousePOS[1]):
                breakoutText.Button_unhover('BREAKOUT')
                pongText.Button_unhover('PONG')
                calibrationText.Button_hover('CALIBRATION')
                mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]
                if mouse_pressed:
                    gameState = 'calibration'
            else:
                pongText.Button_unhover('PONG')
                breakoutText.Button_unhover('BREAKOUT')
                calibrationText.Button_unhover('CALIBRATION')

            # Display the buttons (menu options)
            screen.blit(background, (0, 0))
            breakoutText.Button_render('BREAKOUT')
            pongText.Button_render('PONG')
            calibrationText.Button_render('CALIBRATION')
            pygame.display.flip()


        # CALIBRATION SCREEN:
        elif gameState == 'calibration':

            # Exit interface if escape is pressed, go back to start menu if backspace is pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            if keys[pygame.K_BACKSPACE]:
                gameState == 'start_menu'

            # Plot the electrode layout
            if sensor_change:
                fig, ax = subplots(1, 1)
                mne.viz.plot_sensors(info, show_names=True, ch_groups=channel_groups, linewidth=0.5, show=False,
                                     axes=ax)
                plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.2, 1.1), frameon=False)
                plt.savefig("sensors.png", dpi=150)
                sensor_change = 0
                sensors = pygame.image.load("sensors.png")

            # Display the electrode impedances
            screen.blit(background, (0, 0))
            screen.blit(sensors, (20, 200))
            impText.Button_render('Electrode impedances')
            fp1Text.Button_render('Fp1:')
            fp2Text.Button_render('Fp2:')
            f4Text.Button_render('F4:')
            pygame.display.flip()


        # PONG:
        elif gameState == 'pong_game':

            keys = pygame.key.get_pressed()
            # Exit interface if escape is pressed, go back to start menu if backspace is pressed
            # Move player's paddle up if up key is pressed and down if down key is pressed
            if keys[pygame.K_DOWN]:
                player_pong.move_player_down()
            if keys[pygame.K_UP]:
                player_pong.move_player_up()
            if keys[pygame.K_BACKSPACE]:
                gameState = 'start_menu'
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            # Introduce imperfections in the AI
            # - AI predicts the ball position if the ball is going towards the AI's paddle
            #   and passed the first quarter of the screen
            # - AI executes a movement 70% of the time
            if ball.speedX > 0 and ball.rect.x > 0.25 * screen_width:
                if ball.rect.y < AI.rect.top and AI.rect.top > 0:
                    bias = random.randint(1, 10)
                    if bias <= 7:
                        AI.move_player_up()
                if ball.rect.y > AI.rect.bottom and AI.rect.bottom < screen_height:
                    bias = random.randint(1, 10)
                    if bias <= 7:
                        AI.move_player_down()

            # Print all updated objects on the screen
            screen.blit(background, (0, 0))
            scorePlayer = font.render(str(playerScore), True, red)
            scoreAI = font.render(str(AIScore), True, red)
            screen.blit(scorePlayer, (0.25 * screen_width, 0.1 * screen_height))
            screen.blit(scoreAI, (0.75 * screen_width, 0.1 * screen_height))
            all_sprites_list_pong.update()
            all_sprites_list_pong.draw(screen)
            ball.updateBall_pong(player_pong, AI)

            # Go to the end screen if either the player or AI reaches a score of 3
            if AIScore == 3 or playerScore == 3:
                gameState = 'end_screen'

            pygame.display.flip()


        # BREAKOUT:
        elif gameState == 'breakout_game':

            # Exit interface if escape is pressed, go back to start menu if backspace is pressed
            # Move player's paddle left if left key is pressed and right if right key is pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_breakout.move_player_left()
            if keys[pygame.K_RIGHT]:
                player_breakout.move_player_right()
            if keys[pygame.K_BACKSPACE]:
                gameState = 'start_menu'
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            # Remove a brick if it has been hit with the ball
            hit_index = ball.rect.collidelist(brick_list)
            if 0 <= hit_index <= 14 * 4:
                check_which_collision(ball, brick_list[hit_index])
                brick_list.pop(hit_index)

            # Print all updated objects on the screen
            screen.blit(background, (0, 0))
            livesPlayer = font.render(str(playerLives), True, red)
            screen.blit(livesPlayer, (screen_width - 40, screen_height - 40))
            all_sprites_list_breakout.update()
            ball.updateBall_breakout(player_breakout)
            all_sprites_list_breakout.draw(screen)
            [pygame.draw.rect(screen, brick_colors[0], brick_list[i]) for i in range(len(brick_list))]

            # Go to the end screen if either the player has no lives left or all the brick have been eliminated
            if playerLives == 0 or len(brick_list) == 0:
                gameState = 'end_screen'

            pygame.display.flip()


        # END SCREEN:
        elif gameState == 'end_screen':

            # Create a message with the result of the game
            if playerLives == 0:
                message1 = "You lost"
                message2 = "Score:"
                message3 = "  {}".format(str(11 * 4 - len(brick_list)))
            elif len(brick_list) == 0:
                message1 = "You won!"
                message2 = ""
                message3 = ""
            elif AIScore == 3:
                message1 = "You lost"
                message2 = "Score"
                message3 = "{} - {}".format(playerScore, AIScore)
            elif playerScore == 3:
                message1 = "You won!"
                message2 = "Score"
                message3 = "{} - {}".format(playerScore, AIScore)

            # Render messages
            text1 = large_font.render(message1, True, red)
            text2 = font.render(message2, True, red)
            text3 = font.render(message3, True, red)

            # Display messages
            screen.blit(background, (0, 0))
            screen.blit(text1, (screen_width / 2 - 100, screen_height / 2 - 100))
            screen.blit(text2, (screen_width / 2 - 50, screen_height / 2))
            screen.blit(text3, (screen_width / 2 - 40, screen_height / 2 + 50))

            pygame.display.flip()


def init():
    line.set_data([], [])
    return line,


def animate(i):
    x = np.linspace(0, 4, 1000)
    y = np.sin(2 * np.pi * (x - 0.01 * i))
    line.set_data(x, y)
    return line,


if __name__ == '__main__':
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 4), ylim=(-2, 2))
    line, = ax.plot([], [], lw=3)

    anim = FuncAnimation(fig, animate, init_func=init,
                         frames=200, interval=20, blit=False)

    # Create and start the print thread
    # interface_thread = threading.Thread(target=interface)
    # interface_thread.start()

    interface_process = multiprocessing.Process(target=interface)
    interface_process.start()
    # Start the animation
    plt.show()

    # Wait for the print thread to finish
    # interface_thread.join()
    interface_process.join()
