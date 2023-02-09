import pygame
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import numpy
from handTracking import HandGesture
import cv2
import mediapipe as mp
import pandas as pd
from tensorflow.keras.models import load_model
from pykalman import KalmanFilter
import numpy as np

def read_texture(filename):
    """
    Reads an image file and converts to a OpenGL-readable textID format
    """
    img = Image.open(filename)
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return textID




def main():
    pygame.init()

    cap = cv2.VideoCapture(0)
    handtrckingdetector = HandGesture(maxNumHand=2)
    success, frame = cap.read()
    framex, framey, c = frame.shape


    display = (500, 500)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('PyOpenGLobe')
    pygame.key.set_repeat(1, 10)    # allows press and hold of buttons
    gluPerspective(40, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)    # sets initial zoom so we can see globe
    lastPosX = 0
    lastPosY = 0
    texture = read_texture('world.jpg')
    
    class Rectangle:
        def __init__(self, pos, color, size):
            self.pos = pos
            self.color = color
            self.size = size
        def draw(self):
            pygame.draw.rect(screen, self.color, pygame.Rect(self.pos, self.size))


    model = load_model('mp_hand_gesture')
    kf = KalmanFilter(initial_state_mean=0, n_dim_obs=2)

    # Load class names
    with open('gesture.names', 'r') as f:
        classNames = f.read().split('\n')
    
    className = None
    last_gesture = None
    old_movements = []
    max_old_movements = 15
    while True:


        for event in pygame.event.get():    # user avtivities are called events

            # Exit cleanly if user quits window
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Rotation with arrow keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    glRotatef(1, 0, 1, 0)
                if event.key == pygame.K_RIGHT:
                    glRotatef(1, 0, -1, 0)
                if event.key == pygame.K_UP:
                    glRotatef(1, -1, 0, 0)
                if event.key == pygame.K_DOWN:
                    glRotatef(1, 1, 0, 0)
                

            # Zoom in and out with mouse wheel
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # wheel rolled up
                    glScaled(1.05, 1.05, 1.05)
                if event.button == 5:  # wheel rolled down
                    glScaled(0.95, 0.95, 0.95)

            # Rotate with mouse click and drag
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                dx = x - lastPosX
                dy = y - lastPosY
                mouseState = pygame.mouse.get_pressed()
                if mouseState[0]:

                    modelView = (GLfloat * 16)()
                    mvm = glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

                    # To combine x-axis and y-axis rotation
                    temp = (GLfloat * 3)()
                    temp[0] = modelView[0]*dy + modelView[1]*dx
                    temp[1] = modelView[4]*dy + modelView[5]*dx
                    temp[2] = modelView[8]*dy + modelView[9]*dx
                    norm_xy = math.sqrt(temp[0]*temp[0] + temp[1]
                                        * temp[1] + temp[2]*temp[2])
                    glRotatef(math.sqrt(dx*dx+dy*dy),
                              temp[0]/norm_xy, temp[1]/norm_xy, temp[2]/norm_xy)

                lastPosX = x
                lastPosY = y




        success, frame = cap.read()
        img = handtrckingdetector.drawHand(frame)
        img = cv2.flip(img, 1)
        landmarkList = handtrckingdetector.handPosition(img)

        screen.fill((0, 0, 0))
        
        
        # Creates Sphere and wraps texture
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        gluSphere(qobj, 1, 50, 50)
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)

        if len(landmarkList) > 0:
            try:
                prediction = model.predict([ [[l[1],l[2]] for l in landmarkList] ],verbose=0)
                classID = np.argmax(prediction)
                className = classNames[classID]
            except Exception as e:
                print(f'Model Uncaught Exception: {e}')
                
            # for i, landmark in enumerate(landmarkList):
            #     pass
                # if len(measurements) > 0:
                #     out = kf.em(measurements).smooth([measurements[-1],[x,y]])[0]
            
            xi = landmarkList[0][1]#(landmark[1]/framex)*50
            yi = landmarkList[0][2]#(landmark[2]/framey)*50
            
            # if len(old_movements) == max_old_movements:
            #     kfp = kf.em(old_movements[:(len(old_movements) - 3)]).smooth(old_movements[-3:])[0]
            #     xi = -kfp[0][0]
            #     yi = kfp[1][0]
            
            dx = -(xi - lastPosX)/2
            dy = (yi - lastPosY)/2
            
            dx = dx if abs(dx) > 1 else 0
            dy = dy if abs(dy) > 1 else 0

            #print(f'x:{xi}, y:{yi}, dx:{dx} dy:{dy}')
            if className == last_gesture and className == 'fist' and abs(dx) > 0.001 and abs(dy) > 0.001:

                modelView = (GLfloat * 16)()
                mvm = glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

                # To combine x-axis and y-axis rotation
                temp = (GLfloat * 3)()
                temp[0] = modelView[0]*dy + modelView[1]*dx
                temp[1] = modelView[4]*dy + modelView[5]*dx
                temp[2] = modelView[8]*dy + modelView[9]*dx
                norm_xy = math.sqrt(temp[0]*temp[0] + temp[1]
                                    * temp[1] + temp[2]*temp[2])
                glRotatef(math.sqrt(dx*dx+dy*dy),
                            temp[0]/norm_xy, temp[1]/norm_xy, temp[2]/norm_xy)

            old_movements.append([lastPosX,lastPosY])
            lastPosX = xi
            lastPosY = yi
            

            last_gesture = className

            old_movements = old_movements[-max_old_movements:] if len(old_movements) > max_old_movements else old_movements
                
                

        else:
            pass

        
        # Displays pygame window
        pygame.display.flip()
        clock.tick(60)


main()
