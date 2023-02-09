import pygame, sys
import cv2
import mediapipe as mp
import pandas as pd
from handTracking import HandGesture
from pykalman import KalmanFilter
from tensorflow.keras.models import load_model

pygame.init()

# Set up the window

# Set up the game clock
clock = pygame.time.Clock()
# Set up the player character


#player = pygame.Rect(100, 200, 10, 10)
# Set up the obstacle
#obstacle = pygame.Circ(200, 200, 50, 50)

    
class Rectangle:
    def __init__(self, pos, color, size):
        self.pos = pos
        self.color = color
        self.size = size
    def draw(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos, self.size))


cap = cv2.VideoCapture(0)
handtrckingdetector = HandGesture(maxNumHand=2)
success, frame = cap.read()
x, y, c = frame.shape

screen = pygame.display.set_mode((x, y))

rects = pygame.sprite.Group()
    

# Set up the game loop
kf = KalmanFilter(initial_state_mean=0, n_dim_obs=2)

measurements = []

while True:
# Handle events

    success, frame = cap.read()
    img = handtrckingdetector.drawHand(frame)
    img = cv2.flip(img, 1)
    landmarkList = handtrckingdetector.handPosition(img)

    screen.fill((0, 0, 0))
    if len(landmarkList) > 0:
        for i, landmark in enumerate(landmarkList):

            print(len(landmarkList))
            if len(measurements) > 0:
                out = kf.em(measurements).smooth([measurements[-1],[x,y]])[0]
            
            xi = landmark[1]
            yi = landmark[2]

            #pygame.font.SysFont('Arial', 25).render(str(i), True, (255,0,0)), (200, 100)
            Rectangle((xi,yi), (255,0,0), (10,10)).draw()


    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_LEFT:
        #         player.x -= 10
        #     elif event.key == pygame.K_RIGHT:
        #         player.x += 10
 
    # Update the game state

    # Draw the game
    #screen.fill((0, 0, 0))
    #pygame.draw.rect(screen, (255, 0, 0), player)
    #pygame.draw.rect(screen, (0, 255, 0), obstacle)
    
    # Update the display
    pygame.display.flip()
    
    # Limit the frame rate
    clock.tick(100)