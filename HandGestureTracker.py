# TechVidvan hand Gesture Recognizer

# import necessary packages

import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

import threading
import time

class HandGestureTracker():
    def __init__(self, path_url="data/hand_data.txt"):
        self.line_count = 0
        self.updated_since_last_calc_x = True
        self.updated_since_last_calc_y = True
        self.updated_since_last_calc_gesture = True
        self.data_file_read = open(path_url, "r")
        self.lines = []
    def main(self):

        open("data/hand_data.txt", "w").close()
        data_file = open("data/hand_data.txt", "w")
        data_file.flush()

        # initialize mediapipe
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.6)
        mpDraw = mp.solutions.drawing_utils

        # Load the gesture recognizer model
        model = load_model('mp_hand_gesture')

        # Load class names
        f = open('gesture.names', 'r')
        classNames = f.read().split('\n')
        f.close()

        # Initialize the webcam
        cap = cv2.VideoCapture(0)

        # data_file.close() # this will erease contents of last time this was run
        # data_file = open("data/hand_data.txt", "w")

        while True:
            # Read each frame from the webcam
            _, frame = cap.read()

            x, y, c = frame.shape

            # Flip the frame vertically
            frame = cv2.flip(frame, 1)
            framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Get hand landmark prediction
            result = hands.process(framergb)

            # print(result)

            className = ''
            x_0 = 0
            y_0 = 0
            gesture_0 = ''
            # post process the result
            landmarks_0 = []
            if result.multi_hand_landmarks:
                landmarks = []
                for handslms in result.multi_hand_landmarks:
                    for lm in handslms.landmark:
                        # print(id, lm)
                        lmx = int(lm.x * x)
                        lmy = int(lm.y * y)
                        # print("x " + str(lmx) + " y " + str(lmy))
                        landmarks.append([lmx, lmy])
                        x_0 = lmx
                        y_0 = lmy
                        # for a in range(len(landmarks)):
                        # print(str(a) + " " + str(landmarks[a]))
                        # print("---------------")
                        landmarks_0 = landmarks
                    # Drawing landmarks on frames
                    mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

                    # Predict gesture
                    prediction = model.predict([landmarks],verbose=0)
                    # print(prediction)
                    classID = np.argmax(prediction)
                    className = classNames[classID]

                    gesture_0 = className
                    data_file.write(str(x_0) + ", " + str(y_0) + ", " + str(gesture_0) + "\n")
                    data_file.flush()

                    # start

                    # end

            # show the prediction on the frame
            cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)

            # rect_frame = cv2.rectangle(frame, (x_0,y_0), (x_0+ 5, y_0 + 5), (0,255,0), 2)
            rect_frame = frame
            for i in range(len(landmarks_0)):
                x1 = landmarks_0[i][0]
                y1 = landmarks_0[i][1]
                rect_frame = cv2.rectangle(rect_frame, (x1, y1), (x1 + 5, y1 + 5), (0, 0, (255 * i) / 20), 2)

            # Show the final output
            #cv2.imshow("Output", rect_frame)

            if cv2.waitKey(1) == ord('q'):
                break

        # release the webcam and destroy all active windows
        cap.release()

        cv2.destroyAllWindows()

        data_file.close()
        # in the format x,y,gesture

    def get_last_delta_x(self):
        self.update_lines_file()
        if self.line_count < 2 or not self.updated_since_last_calc_x:
            return 0
        self.updated_since_last_calc_x = False;
        last_line = self.lines[self.line_count - 1]
        second_last_line = self.lines[self.line_count - 2]
        last_x = last_line[:last_line.index(",")]
        second_last_x = second_last_line[:second_last_line.index(",")]
        return int(last_x) - int(second_last_x)

    def get_last_delta_y(self):
        self.update_lines_file()
        if self.line_count < 2 or not self.updated_since_last_calc_y:
            return 0
        self.updated_since_last_calc_y = False;
        last_line = self.lines[self.line_count - 1]
        second_last_line = self.lines[self.line_count - 2]
        #last_y = last_line[last_line.index(",") + 1: last_line.rfind(",") - 1]
        #second_last_y = last_line[second_last_line.index(",") + 1 : second_last_line.rfind(",") - 1]
        last_split = last_line.split(",")
        second_last_split = second_last_line.split(",")

        return int(second_last_split[1]) - int(last_split[1])

    def get_last_gesture(self):
        self.update_lines_file()
        if self.line_count < 2 or not self.updated_since_last_calc_gesture:
            return 0
        self.updated_since_last_calc_gesture = False;
        last_line = self.lines[self.line_count - 1]
        second_last_line = self.lines[self.line_count - 2]
        #last_y = last_line[last_line.index(",") + 1: last_line.rfind(",") - 1]
        #second_last_y = last_line[second_last_line.index(",") + 1 : second_last_line.rfind(",") - 1]
        last_split = last_line.split(",")
        second_last_split = second_last_line.split(",")
        
        return (second_last_split[-1], last_split[-1])


    def update_lines_file(self):
        line = self.data_file_read.readline()
        while not line == "":
            self.updated_since_last_calc_y = True
            self.updated_since_last_calc_x = True
            self.updated_since_last_calc_gesture = True
            self.lines.append(line)
            line = self.data_file_read.readline()
        self.line_count = len(self.lines)
        line = self.data_file_read.readline()

'''
    def app_runner():
        data_file = open("data/hand_data.txt", "r")
        data_file.flush()
        lines = []while True:
            line = data_file.readline()
            if not line == "":
                lines.append(line)
                time.sleep(0.1)
            if len(lines) > 0:
                print("L: " + lines[len(lines)-1])
        

'''
# print("test1")
# tracker = HandGestureTracker()
# def app_runner():
#     '''
#     data_file = open("data/hand_data.txt", "r")
#     data_file.flush()
#     lines = []
#     while True:
#         line = data_file.readline()
#         if not line == "":
#             lines.append(line)
#             time.sleep(0.1)
#         if len(lines) > 0:
#             print("L: " + lines[len(lines) - 1])
#     '''
#     while True:
#         print(f'dX:{tracker.get_last_delta_x()}, dY:{tracker.get_last_delta_y()}, commands:{tracker.get_last_gesture()}')
#         #print(str(tracker.get_last_delta_x()) + " " + str(tracker.get_last_delta_y()))
#         time.sleep(0.4)



# print("test2")
# #print(tracker.get_last_delta_x())


# thread_1 = threading.Thread(target=tracker.main, daemon=True)
# thread_2 = threading.Thread(target=app_runner, daemon=False)

# thread_1.start()
# thread_2.start()

# thread_1.join()
# thread_2.join()