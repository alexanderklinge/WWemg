import pygame
import sys
import random
import time
import numpy as np
import serial

random_max_value = 0.6 # 0.6

level = 1

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
FPS = 60
TIME_INTERVAL = 50  # Time interval in milliseconds

# Game variables
config_val = 0
countdown_time = 3  # countdown in secons
game_running = False
threshold = 200  # threshold in pixels

wwemg_img = pygame.image.load('WWEMG-Pic.png')
pygame.display.set_icon(wwemg_img)
wwemg_img_resized = pygame.transform.scale(wwemg_img, (200, 200))

# Initialize Pygame screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EMG Arm-Wrestling")
clock = pygame.time.Clock()

font_large = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 36)

cpu_avg = [] # for computer opponent strength fade in

ser = serial.Serial("COM5", 115200)  # Establish Serial object with COM port and BAUD rate to match Arduino Port/rate
time.sleep(2)  # Time delay for Arduino Serial initialization


# Function to display countdown
def display_countdown(count):
    screen.fill(WHITE)
    relax_text = font_small.render("Relax your arms until start in...", True, BLACK)
    relax_rect = relax_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(relax_text, relax_rect)

    count_text = font_large.render(str(count), True, BLACK)
    count_rect = count_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(count_text, count_rect)

    pygame.display.flip()


# Function to display tacho
def display_tacho(position, contraction_player, contraction_com):
    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, (50, 350, 700, 100), 2)  # Tacho outline
    pygame.draw.line(screen, RED, (WIDTH // 2, 400), (WIDTH // 2 + position , 400), 20)  # Tacho needle
    pygame.draw.line(screen, BLUE, (WIDTH // 2 - threshold, 350), (WIDTH // 2 - threshold, 450),
                     2)  # Left threshold line
    pygame.draw.line(screen, BLUE, (WIDTH // 2 + threshold, 350), (WIDTH // 2 + threshold, 450),
                     2)  # Right threshold line

    screen.blit(wwemg_img_resized, ((WIDTH /2) - 100 , (HEIGHT / 2) -200))


    # Draw labels at thresholds
    left_label = font_small.render("Player", True, BLUE)
    right_label = font_small.render("Computer", True, BLUE)
    screen.blit(left_label, (WIDTH // 2 - threshold - 80, 460))
    screen.blit(right_label, (WIDTH // 2 + threshold + 10, 460))

    # Draw Strength Player
    headline = font_large.render(f"EMG Arm-Wrestling - Level {level}", True, BLACK)
    headline_rect = headline.get_rect(center=(WIDTH // 2, 50))
    screen.blit(headline, headline_rect)

    pygame.draw.rect(screen, RED, (100, 125, 100, 200), 2)  # Tacho outline
    pygame.draw.line(screen, RED, (150, 325), (150, 320 - contraction_player * 25), 30)  # Tacho needle

    # Draw Strength CPU
    headline = font_small.render("Strength", True, BLACK)
    headline_rect = headline.get_rect(center=(150, 100))
    screen.blit(headline, headline_rect)

    pygame.draw.rect(screen, RED, (600, 125, 100, 200), 2)  # Tacho outline
    pygame.draw.line(screen, RED, (650, 325), (650, 320 - contraction_com * 30), 30)  # Tacho needle

    # Draw headline
    headline = font_small.render("Strength", True, BLACK)
    headline_rect = headline.get_rect(center=(650, 100))
    screen.blit(headline, headline_rect)

    pygame.display.flip()


# Function to display start button
def display_start_button():
    screen.fill(WHITE)

    # Draw headline
    start_headline = font_large.render("EMG Arm-Wrestling", True, BLACK)
    start_headline_rect = start_headline.get_rect(center=(WIDTH // 2, 50))
    screen.blit(start_headline, start_headline_rect)

    start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100)
    pygame.draw.rect(screen, GRAY, start_button_rect)
    start_text = font_large.render("Start", True, BLACK)
    text_rect = start_text.get_rect(center=start_button_rect.center)
    screen.blit(start_text, text_rect)
    pygame.display.flip()
    return start_button_rect  # Return the Rect object


# Function to display start button
def display_restart_button():
    restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100)
    pygame.draw.rect(screen, GRAY, restart_button_rect)
    restart_text = font_large.render("Restart", True, BLACK)
    text_rect = restart_text.get_rect(center=restart_button_rect.center)
    screen.blit(restart_text, text_rect)
    pygame.display.flip()
    return restart_button_rect  # Return the Rect object


# Function to display "Game Over" message
def display_game_over_message(winner):
    screen.fill(WHITE)
    game_over_text = font_large.render(f"Game Over! {winner} wins!", True, RED)
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(game_over_text, text_rect)
    pygame.display.flip()


def moving_average(data, window_size):
    moving_avg = np.convolve(data, np.ones(window_size) / window_size, mode='valid')
    return moving_avg


# Display the start button and get its Rect object
start_button = display_start_button()

# Wait for the 'Start' button to be clicked
waiting_for_start = True
while waiting_for_start:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if start_button.collidepoint(event.pos):
                    waiting_for_start = False

# Countdown
for i in range(countdown_time, 0, -1):
    display_countdown(i)
    for j in range(100): # 100
        #ser.write(string_encode.encode('utf-8'))
        try:
            arduinoData_string = ser.readline().decode('ascii')  # Decode receive Arduino data as a formatted string
            arduinoData_float = float(arduinoData_string) / 10 # Convert to float
            print(arduinoData_float)

        except:  # Pass if data point is bad
            print("error")
            pass
        #print(moving_avg[0])
        # time.sleep(0.0025)


# Game loop
tick = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not game_running:
        # Read config_val here (you can replace this with actual input)
        # config_val = random.randint(0, 1)
        config_val = random.uniform(0, 1)
        game_running = True

    current_time = pygame.time.get_ticks()

    # Read two values every 10 milliseconds (replace these with your actual input)

   # ser.write(string_encode.encode('utf-8'))
    arduinoData_string = ser.readline().decode('ascii')  # Decode receive Arduino data as a formatted string

    try:
        arduinoData_float = float(arduinoData_string)  # Convert to float
        arduinoData_float = (arduinoData_float / 1023) / 10
    except:  # Pass if data point is bad
        print("error")
        pass

    # compute player and computer values for display
    value1 = arduinoData_float * 2
    cpu_avg.append(random.gauss(random_max_value, 0.2))
    value2 = moving_average(cpu_avg, 100)[-1:][0]

    # update cpu buffer for strength fade in, from zero to max strength
    cpu_avg = cpu_avg[-100:]
    # Update tacho position based on the values
    config_val += value1 - value2
    config_val = max(-threshold, min(threshold, config_val))

    # update screen
    display_tacho(config_val, value1, value2)
    tick += 1
    # Check if the game should stop
    if config_val <= -threshold or config_val >= threshold:
        game_running = False
        winner = "Computer" if config_val <= -threshold else "Player"
        print(f"The winner is {winner}!")
        if(winner == "Player"):
            random_max_value += 0.2
            level+=1
        else:
            if not (random_max_value <= 0.4):
                level-=1
                random_max_value -= 0.2
        for i in range(len(cpu_avg)):
            cpu_avg[i] = 0
        #print(cpu_avg)
        # Display "Game Over" message
        display_game_over_message(winner)
        restart_button = display_restart_button()

        # Keep the last screen until the user closes the window
        restart_val = False
        while True:
            # keep reading
            #ser.write(string_encode.encode('utf-8'))
            arduinoData_string = ser.readline().decode('ascii')  # Decode receive Arduino data as a formatted string

            try:
                arduinoData_float = float(arduinoData_string)  # Convert to float
                arduinoData_float = (arduinoData_float / 1023) / 10
            except:  # Pass if data point is bad
                #print("error")
                pass

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print("pressed")
                    if restart_button.collidepoint(event.pos):
                        print("event")
                        restart_val = True
                        break
            if restart_val == True:
                break
            pygame.display.flip()
            clock.tick(FPS)


