import sys, os, time, numpy
import cv2
import math
from threading import Thread

import pygame
from djitellopy import Tello

tello = Tello()

from pygame.locals import *
pygame.init()


pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print("Connected controller: ", joystick.get_name())


axis0 = 0 # left(-1) - right(+1)
axis1 = 0 # front(-1) - back(+1)
axis2 = 0 # speed up(-1) - down(+1)
axis3 = 0 # spin left(-1) - right(+1)
axis4 = 0 # 

def showAxis():
    # clearConsole()
    print(tello.get_battery(), " ", tello.get_temperature())
    print("Axis0:", axis0)
    print("Axis1:", axis1)
    print("Axis2:", axis2)
    print("Axis3:", axis3)
    print("Axis4:", axis4)
    print("\n")

def normalize(value, minimum, maximum):
    if (value < minimum):
        value = minimum
    if (value > maximum):
        value = maximum
    if (value == 0):
        value = 0
    return value

try:
    tello.connect()
except:
    print("Could not connect to Tello")
    sys.exit()

tello.set_speed(100)


def getVideo():
    
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    fontScale              = 0.5
    fontColor              = (0, 0, 50)
    thickness              = 1
    lineType               = 2
    first = True
    
    
    global runStream
    global queuePicture
    global free
    free = False
    runStream = False
    queuePicture = False
    while True:
        if runStream == True:
            if first:
                tello.streamon()
                time.sleep(5)
                frame_read = tello.get_frame_read()
                first = False
            while runStream:
                if free:
                    break
                if queuePicture:
                        cv2.imwrite(str(time.time()) + ".png", frame_read.frame)
                        queuePicture = False
                img = frame_read.frame
                cv2.putText(img, 'Battery: ' + str(tello.get_battery()) + '%', (5, 30), font, fontScale,fontColor,thickness,lineType)
                cv2.putText(img, 'Temperature: ' + str(tello.get_temperature()) + 'C', (5, 50), font, fontScale,fontColor,thickness,lineType)
                cv2.putText(img, 'Height: ' + str(tello.get_height()) + 'm', (5, 70), font, fontScale,fontColor,thickness,lineType)
                cv2.putText(img, 'Barometer: ' + str(tello.get_barometer()) + 'm', (5, 90), font, fontScale,fontColor,thickness,lineType)
                cv2.putText(img, 'Flight time: ' + str(tello.get_flight_time()) + 's', (5, 110), font, fontScale,fontColor,thickness,lineType)
                cv2.imshow("drone", img)
                time.sleep(1/60)
                key = cv2.waitKey(1) & 0xff
            cv2.destroyAllWindows()
        if free:
            break
        time.sleep(3)

video = Thread(target=getVideo)
video.start()



while True:


    for event in pygame.event.get():
        # if event.type == JOYBUTTONDOWN:
            # print(event)

        if event.type == JOYBUTTONUP:
            # print(event)
            if event.button == 1:
                tello.emergency()
            if event.button == 10:
                tello.takeoff()
            if event.button == 11:
                tello.land()
            if event.button == 8:
                runStream = True
            if event.button == 9:
                runStream = False
            if event.button == 0:
                queuePicture = True
            if event.button == 2:
                free = True
                # video.join()
                pygame.quit()
                sys.exit()
            
        if event.type == JOYAXISMOTION:
            # print(event)
            if event.axis == 0: # left(-1) - right(+1)
                axis0 = event.value
                axis0 = normalize(axis0, -1, 1)
                axis0 = int(axis0 * 100)
            if event.axis == 1: # front(-1) - back(+1)
                axis1 = event.value * -1
                axis1 = normalize(axis1, -1, 1)
                axis1 = int(axis1 * 100)
            if event.axis == 2: # speed up(-1) - down(+1)
                axis2 = event.value * -1
                axis2 = normalize(axis2, -1, 1)
                axis2 = int(axis2 * 100)
            if event.axis == 3: # spin left(-1) - right(+1)
                axis3 = event.value
                axis3 = normalize(axis3, -1, 1)
                axis3 = int(axis3 * 100)
            if event.axis == 4: #
                axis4 = event.value
                axis4 = normalize(axis4, -1, 1)
                axis4 = int(axis4 * 100)
            # showAxis()
            tello.send_rc_control(axis0, axis1, axis2, axis3)
        if event.type == JOYHATMOTION:
            # <Event(1538-JoyHatMotion {'joy': 0, 'instance_id': 0, 'hat': 0, 'value': (0, 1)})>
            if event.joy == 0:
                if(event.value == (0, 1)):
                    tello.flip_forward()
                if(event.value == (0, -1)):
                    tello.flip_back()
                if(event.value == (-1, 0)):
                    tello.flip_left()
                if(event.value == (1, 0)):
                    tello.flip_right() 

        if event.type == JOYDEVICEADDED:
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            # for joystick in joysticks:
                # print(joystick.get_name())

        if event.type == JOYDEVICEREMOVED:
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

    time.sleep(0.05)
