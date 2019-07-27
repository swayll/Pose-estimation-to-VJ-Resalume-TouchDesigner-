#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# [ =======       BASED ON POSE ESTIMATION BY @ILDOONET    ========= ]
# [ =======   https://github.com/ildoonet/tf-pose-estimation   ========= ]
# [ =======          PLEASE INSTALL IN BEFORE USE        ========= ]


# In[ ]:


# [ =======   IMPORT OF NECESSARY MODULES   ========= ]

import argparse, time, cv2, socket, json
import numpy as np
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
from pythonosc.udp_client import SimpleUDPClient
import pyparsing as pp
from pyparsing import *


# In[ ]:


# [ =======   LIST OF PARTS OF BODY   ========= ]

###    Nose = 0
###    Neck = 1
###    RShoulder = 2
###    RElbow = 3
###    RWrist = 4
###    LShoulder = 5
###    LElbow = 6
###    LWrist = 7
###    RHip = 8
###    RKnee = 9
###    RAnkle = 10
###    LHip = 11
###    LKnee = 12
###    LAnkle = 13
###    REye = 14
###    LEye = 15
###    REar = 16
###    LEar = 17
###    Background = 18


# In[ ]:


# [ =======   VARIABLES SECTION   ========= ]

## BODY PARTS (SEE THE LIST OF PARTS ABOVE)
first = 2 #Right eye
second = 5 #Left eye

## TF-POSE VARIABLES
w, h = 432, 368

## UDP CLIENTS VARIABLES
IP = "127.0.0.1" # Set "127.0.0.1" or "localhost" for sending data to internal host
PORT = 4444 # The port should matched with receiver port in TouchDesigner, vvvv, Resolume

## ADDRESSES IN RESOLUME
First_x = "/composition/layers/1/clips/2/video/source/lines/rotation"
Second_x = "/composition/layers/1/clips/2/video/source/lines/color/hue"

## CONFIG VARIABLES
model = 'mobilenet_thin' # Model of recognition (mobilenet_thin, mobilenet_v2_small, mobilenet_v2_large, mobilenet_v2_small)
debug = False # Prints some steps of execution of script
video = False # Open video capture screen
Resolume = True # Sent data to Resolume Arena over OSC
TouchDesigner = True # Sent data to Touch Designer over UDP

# FORMAT OF DATA FOR SENT TO TOUCH DESIGNER (PLEASE CHOOSE ONLY ONE)
JSON = True # Sent data in JSON-format
CSV = False # Sent data in CSV-format


# In[ ]:


# [ =======   FUNCTIONS SECTION   ========= ]

OSC = SimpleUDPClient(IP, PORT) # Create OSC client
UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create UDP client

def JSON_sent(id, x, y, s): #JSON format data sent
    data = {"ID":id,"coordinates":[{"x":x},{"y":y},{"s":s}]}
    if debug:
        print("JSON: {}\n".format(data))
    data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    UDP.sendto(bytes(data), (IP, PORT))
    
def CSV_sent(id, x, y, s): #CSV format data sent
    data = str(id)+", "+str(x)+", "+str(y)+", "+str(s)
    if debug:
        print("CSV: {}\n".format(data))
    data = str.encode(data)
    UDP.sendto(bytes(data), (IP, PORT))

def resalume_first_x(x):
    OSC.send_message(First_x, x)

def resalume_second_x(x):
    OSC.send_message(Second_x, x)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
              
def scale(val, src, dst): # Function of scaling of one interval of digits to another one
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
              
def parserdata(humans): # Function of parsing of data from 'humans' variable catched from TF-Pose
    digit = Word(nums)
    coordinate = Word(nums + ".-")
    x = (Suppress(Literal("-("))+coordinate+Suppress(Literal(",")))("x")
    y = (coordinate+Suppress(Literal(")")))('y')
    s = (Suppress(Literal("score="))+coordinate)('s')
    id = (Suppress(Optional(Literal("["))+Literal("BodyPart:"))+digit)("id")
    oneman = OneOrMore(Group(OneOrMore(Group(id + Group(x + y + s)))+Suppress(Optional(","))))
    humansparsed = oneman.parseString(humans)
    if debug:
        print("HUMANS RAW DATA:\n{}\n".format(humans))
        print("HUMANS PARSED DATA:\n{}\n".format(humansparsed))
    return(humansparsed)

def sendpointstoudp(humans):
    humans = parserdata(humans)
    for j in range(len(humans[0])):
        id = int(humans[0][j][0])
        x = round(float(humans[0][j][1][0]), 2)
        y = round(float(humans[0][j][1][1]), 2)
        s = round(float(humans[0][j][1][2]), 2)
        #s = round(scale(float(humans[i][j][1][2]), (-1.0, +1.0), (0.0, +1.0)), 2)
        if id == first:
            if debug:
                print("First point: id: {}, x: {}, y: {}, s: {}\n".format(id, x, y, s))
            else:
                if TouchDesigner:
                    if JSON == True and CSV == False:
                        JSON_sent(id, x, y, s)
                    elif CSV == True and JSON == False:
                        CSV_sent(id, x, y, s)
                if Resolume:
                    resalume_first_x(float(x))
        if id == second:
            if debug:
                print("Second point: id: {}, x:{}, y: {}, s: {}\n".format(id, x, y, s))
            else:
                if TouchDesigner:
                    if JSON == True and CSV == False:
                        JSON_sent(id, x, y, s)
                    elif CSV == True and JSON == False:
                        CSV_sent(id, x, y, s)
                if Resolume:
                    resalume_second_x(float(x))


# In[ ]:


# [ =======   CODE EXECUTION SECTION   ========= ]

if debug!=True:
    fps_time = 0
    e = TfPoseEstimator(get_graph_path(model), target_size=(w, h), trt_bool=str2bool('False'))
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, image = cam.read()
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=4.0)
        if video:
            image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
            cv2.putText(image,
                        "FPS: %f" % (1.0 / (time.time() - fps_time)),
                       (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
            cv2.imshow('tf-pose-estimation result', image)
            fps_time = time.time()
        humans = str(humans)
        if (humans != str("[]") and humans != str("[ ]")) and humans != str(""):
            sendpointstoudp(humans)
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()
else:
    humans = str("[BodyPart:0-(-0.86, 0.18) score=0.78 BodyPart:1-(0.91, 0.58) score=0.19 BodyPart:2-(0.74, 0.58) score=0.35 BodyPart:3-(0.73, 0.83) score=0.23 BodyPart:14-(0.82, 0.16) score=0.81 BodyPart:15-(0.89, 0.14) score=0.83, BodyPart:16-(0.80, 0.23) score=0.78 BodyPart:17-(0.94, 0.17) score=0.73, BodyPart:0-(0.86, 0.18) score=0.78]")
    sendpointstoudp(humans)


# In[ ]:


cam.release() # Camera stop


# In[ ]:





# In[ ]:




