import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import cv2
import pyautogui
from time import time
from math import hypot
import mediapipe as mp
import matplotlib.pyplot as plt
gui = tk.Tk()
up = ""
down = ""
left = ""
right = ""
space=""
def start():
    global up
    global down
    global left
    global right
    global space
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    pose_image = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=1)
    pose_video = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.7,
                            min_tracking_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils 
    def detectPose(image, pose, draw=False, display=False):
        output_image = image.copy()
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(imageRGB)
        if results.pose_landmarks and draw:
            mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                    connections=mp_pose.POSE_CONNECTIONS,
                                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255,255,255),
                                                                                thickness=3, circle_radius=3),
                                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(49,125,237),
                                                                                thickness=2, circle_radius=2))
        if display:
            plt.figure(figsize=[22,22])
            plt.subplot(121);plt.imshow(image[:,:,::-1]);plt.title("Original Image");plt.axis('off');
            plt.subplot(122);plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        else:
            return output_image, results
    def checkHandsJoined(image, results, draw=False, display=False):
        height, width, _ = image.shape
        output_image = image.copy()
        left_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * width,
                            results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * height)
        right_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * width,
                            results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * height)
        euclidean_distance = int(hypot(left_wrist_landmark[0] - right_wrist_landmark[0],
                                    left_wrist_landmark[1] - right_wrist_landmark[1]))
        if euclidean_distance < 160:
            hand_status = 'Hands Joined'
            color = (0, 255, 0)
        else:
            hand_status = 'Hands Not Joined'
            color = (0, 0, 255)
        if draw:
            cv2.putText(output_image, hand_status, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 3)
            cv2.putText(output_image, f'Distance: {euclidean_distance}', (10, 70),
                        cv2.FONT_HERSHEY_PLAIN, 2, color, 3)
        if display:
            plt.figure(figsize=[10,10])
            plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        else:
            return output_image, hand_status
    def checkLeftRight(image, results, draw=False, display=False):
        horizontal_position = None
        height, width, _ = image.shape
        output_image = image.copy()
        left_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width)
        right_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * width)
        if (right_x <= width//2 and left_x <= width//2):
            horizontal_position = 'Left'
        elif (right_x >= width//2 and left_x >= width//2):
            horizontal_position = 'Right'
        elif (right_x >= width//2 and left_x <= width//2):
            horizontal_position = 'Center'
        if draw:
            cv2.putText(output_image, horizontal_position, (5, height - 10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
            cv2.line(output_image, (width//2, 0), (width//2, height), (255, 255, 255), 2)
        if display:
            plt.figure(figsize=[10,10])
            plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        else:
            return output_image, horizontal_position
    def checkJumpCrouch(image, results, MID_Y=250, draw=False, display=False):
        height, width, _ = image.shape
        output_image = image.copy()
        left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height)
        right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height)
        actual_mid_y = abs(right_y + left_y) // 2
        lower_bound = MID_Y-15
        upper_bound = MID_Y+100
        if (actual_mid_y < lower_bound):
            posture = 'Jumping'
        elif (actual_mid_y > upper_bound):
            posture = 'Crouching'
        else:
            posture = 'Standing'
        if draw:
            cv2.putText(output_image, posture, (5, height - 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
            cv2.line(output_image, (0, MID_Y),(width, MID_Y),(255, 255, 255), 2)
        if display:
            plt.figure(figsize=[10,10])
            plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        else:
            return output_image, posture
    camera_video = cv2.VideoCapture(0)
    cv2.namedWindow('PlayConnect', cv2.WINDOW_NORMAL)
    camera_video.set(3,1280)
    camera_video.set(4,960)
    time1 = 0
    game_started = False   
    x_pos_index = 1
    y_pos_index = 1
    MID_Y = None
    counter = 0
    num_of_frames = 10
    def nothing():
        pass
    while camera_video.isOpened():
        ok, frame = camera_video.read()
        if not ok:
            continue
        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        frame, results = detectPose(frame, pose_video, draw=game_started)
        if results.pose_landmarks:
            if game_started:
                switch = '1 : ON'
                value = 1
                cv2.createTrackbar(switch, 'PlayConnect',value,1,nothing)
                if cv2.getTrackbarPos(switch, 'PlayConnect') == 0:
                    camera_video.release()
                    cv2.destroyAllWindows()
                cv2.putText(frame, 'TO DELETE THIS WINDOW PRESS BAR AT TOP', (150, frame_height - 10), cv2.FONT_HERSHEY_PLAIN,
                                    2, (0, 255, 0), 3)
                frame, horizontal_position = checkLeftRight(frame, results, draw=True)
                if (horizontal_position=='Left' and x_pos_index!=0) or (horizontal_position=='Center' and x_pos_index==2):
                    pyautogui.press(left)
                    x_pos_index -= 1               
                elif (horizontal_position=='Right' and x_pos_index!=2) or (horizontal_position=='Center' and x_pos_index==0):
                    pyautogui.press(right)
                    x_pos_index += 1
            else:
                cv2.putText(frame, 'JOIN BOTH HANDS TO START THE GAME.', (5, frame_height - 10), cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 255, 0), 3)
                switch = '1 : ON'
                value = 1
                cv2.createTrackbar(switch, 'PlayConnect',value,1,nothing)
                if cv2.getTrackbarPos(switch, 'PlayConnect') == 0:
                    camera_video.release()
                    cv2.destroyAllWindows()
                cv2.putText(frame, 'TO DELETE THIS WINDOW PRESS BAR AT TOP', (150, frame_height - 10), cv2.FONT_HERSHEY_PLAIN,
                                    2, (0, 255, 0), 3)
            if checkHandsJoined(frame, results)[1] == 'Hands Joined':
                counter += 1
                if counter == num_of_frames:
                    if not(game_started):
                        game_started = True
                        left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame_height)
                        right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame_height)
                        MID_Y = abs(right_y + left_y) // 2
                    else:
                        pyautogui.press('space')
                    counter = 0
            else:
                counter = 0
            if MID_Y:
                frame, posture = checkJumpCrouch(frame, results, MID_Y, draw=True)
                if posture == 'Jumping' and y_pos_index == 1:
                    
                    pyautogui.press(up)
                    y_pos_index += 1 
                elif posture == 'Crouching' and y_pos_index == 1:
                   
                    pyautogui.press(down)
                    y_pos_index -= 1
                elif posture == 'Standing' and y_pos_index   != 1:
                    y_pos_index = 1
        else:
            counter = 0
        time2 = time()
        if (time2 - time1) > 0:
            frames_per_second = 1.0 / (time2 - time1)
            cv2.putText(frame, 'FPS: {}'.format(int(frames_per_second)), (10, 30),cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
        time1 = time2
        cv2.imshow('PlayConnect', frame)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            print('Quitting...')
            break
    camera_video.release()
    cv2.destroyAllWindows()
    cv2.imshow("PlayConnect", frame)
def display_jump():
            string= entry.get()
            global up
            up = string
            print(up)
def display_left():
            string= entry2.get()
            global left
            left = string
            print(left)
def display_right():
            string= entry3.get()
            global right
            right = string
            print(right)
def display_squat():
            string= entry4.get()
            global down
            down = string
            print(down)
def display_space():
            string= entry5.get()
            global space
            space = string
            print(space)
entry= ttk.Entry(gui, textvariable=up, width= 40)
print (up)
entry.focus_set()
entry.pack()
ttk.Button(gui, text= "Keybind for Jump",width= 20, command= display_jump).pack(pady=20)
entry2= ttk.Entry(gui, width= 40)
entry2.focus_set()
entry2.pack()
ttk.Button(gui, text= "Keybind for Left",width= 20, command= display_left).pack(pady=20)
entry3= ttk.Entry(gui, width= 40)
entry3.focus_set()
entry3.pack()
ttk.Button(gui, text= "Keybind for Right",width= 20, command= display_right).pack(pady=20)
entry4= ttk.Entry(gui, width= 40)
entry4.focus_set()
entry4.pack()
ttk.Button(gui, text= "Keybind for Squat",width= 20, command= display_squat).pack(pady=20)
entry5= ttk.Entry(gui, width= 40)
entry5.focus_set()
entry5.pack()
ttk.Button(gui, text= "Keybind to Start the Game",width= 20, command= display_space).pack(pady=20)
button3 = ttk.Button(gui, text ="Go to Pose Detection",
                    command = start)

button3.pack()
gui.mainloop()

