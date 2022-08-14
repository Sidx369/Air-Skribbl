# import the necessary packages
import numpy as np
import cv2
import imutils
import time
from datetime import datetime
import random
from urllib.request import urlopen

url = ''

word = 'random'
putword = ' '.join('_' for i in word if i!=' ')
ind = -1

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)


cap = cv2.VideoCapture(0)

# allow the camera or video file to warm up
time.sleep(2.0)

# Load these 2 images and resize them to the same size.
pen_img = cv2.resize(cv2.imread('pen.png',1), (50, 50))
eraser_img = cv2.resize(cv2.imread('eraser.jpg',1), (50, 50))
dustbin_img = cv2.resize(cv2.imread('dustbin.png',1), (50, 50))

# Making window size adjustable
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

# This is the canvas on which we will draw upon
canvas = None

# Create a background subtractor Object
backgroundobject = cv2.createBackgroundSubtractorMOG2(detectShadows = False)

# This threshold determines the amount of disruption in the background.
background_threshold = 600

# A variable which tells you if you're using a pen or an eraser.
switch = 'Eraser'

# With this variable we will monitor the time between previous switch.
last_switch = time.time()
last_switchd = time.time()

# Initilize x1,y1 points
x1,y1=0,0

# Threshold for wiper, the size of the contour must be bigger than this for # us to clear the canvas
wiper_thresh = 40000

# A variable which tells when to clear canvas
clear = False

# Game counters
sstartTime = 0
startTime = 0
skey = False
startCounter = False
nSecond = 0
totalSec = 60
prevno = -1
list2 = [30, 45]
wordset = set(list2)

# keep looping
while True:
        #For using Phone as Camera
        #imgResp = urlopen(url)
        #imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        #frame = cv2.imdecode(imgNp, -1)

        #For using webcam as Camera
        ret, frame = cap.read()
        #print(ret)
        frame = cv2.flip(frame, 1 )
        
	# grab the current frame
	#frame = vs.read()

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
        if frame is None:
                break

	# Initilize the canvas as a black image
        if canvas is None:
                canvas = np.zeros_like(frame)

        # Take the top left of the frame and apply the background subtractor
        # there
        top_left = frame[0: 50, 0: 50]
        fgmask = backgroundobject.apply(top_left)

        # Note the number of pixels that are white, this is the level of 
        # disruption.
        switch_thresh = np.sum(fgmask==255)

        if switch_thresh>background_threshold and (time.time()-last_switch) > 1:

                # Save the time of the switch. 
                last_switch = time.time()
                
                if switch == 'Pen':
                        switch = 'Eraser'
                else:
                        switch = 'Pen'
        
        # DUSTBIN  
        # Take the top right of the frame and apply the background subtractor
        # there
        #top_right = frame[0: 50, 550: 600]
        #fgmasktr = backgroundobject.apply(top_right)

        # Note the number of pixels that are white, this is the level of 
        # disruption.
        #switch_threshtr = np.sum(fgmasktr==255)

        #if switch_threshtr>background_threshold and (time.time()-last_switchd) > 1:
                # Save the time of the switch. 
                #last_switchd = time.time()
                # Clear Canvas
                #canvas = np.zeros_like(frame)

        # resize the Canvas to match the frame
        canvas = imutils.resize(canvas, width=600)
	# resize the frame, blur it, and convert it to the HSV
	# color space
        frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
	
	# only proceed if at least one contour was found
        if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
                c = max(cnts, key=cv2.contourArea)
                x2,y2,w,h = cv2.boundingRect(c)
		
		# Get the area of the contour
                area = cv2.contourArea(c)
                
		
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                  
		# only proceed if the radius meets a minimum size
                if radius > 10:
                        if x1 == 0 and y1 == 0:
                            x1,y1= int(x), int(y)
            
                        else:
                            if switch == 'Pen':
                                # draw the circle and centroid on the frame,
                                # then update the list of tracked points
                                cv2.circle(frame, (int(x), int(y)), int(radius),
                                        (0, 255, 255), 2)
                                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                      
                                # Draw the line on the canvas
                                canvas = cv2.line(canvas, (x1,y1),
                                (int(x), int(y)), [255,0,0], 5)
                            else:
                                cv2.circle(frame, (int(x), int(y)), int(radius),
                                        (0, 255, 255), 2)
                                cv2.circle(canvas, (int(x), int(y)), 20,
                                (0,0,0), -1)

                        # After the line is drawn the new points become the previous points.
                        x1,y1= int(x), int(y)

                        # Now if the area is greater than the wiper threshold then set the 
                        # clear variable to True
                        if area > wiper_thresh:
                           cv2.putText(canvas,'Clearing Canvas',(200, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                           clear = True

        else:
                # If there were no contours detected then make x1,y1 = 0
                x1,y1 =0,0

                              
	# Switch the images depending upon what we're using, pen or eraser.
        if switch != 'Pen':
                cv2.circle(frame, (x1, y1), 20, (255,255,255), -1)
                frame[0: 50, 0: 50] = eraser_img
        else:
                frame[0: 50, 0: 50] = pen_img
        #frame[0: 50, 550: 600] = dustbin_img

        # CONTROLS
        k = cv2.waitKey(5) & 0xFF
        # Clear canvas if pressed C
        if k == ord('c'):
                canvas = np.zeros_like(frame)

        # Start the game
        if k == ord('s'):
                canvas = np.zeros_like(frame)
                skey = True
                nSecond = 0
                startTime = datetime.now()
                sstartTime = datetime.now()
                wordset = set(list2)
                
                startCounter = True
                switch = 'Pen'
        #       print 'startTime: {}'.format(startTime)
        #       print 'keyPressTime: {}'.format(keyPressTime)

        # Display START
        if skey:
                if (datetime.now() - sstartTime).total_seconds() < 2:
                        cv2.putText(canvas, 'START',(190, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255, 0), 3, cv2.LINE_AA)
                else:
                        canvas = np.zeros_like(frame)
                        skey = False
        
        # Display counter on screen before saving a frame
        if startCounter:
                if nSecond < totalSec: 
                        # draw the Nth second on each frame 
                        # till one second passes  
                        cv2.putText(img = frame,
                                text = str(totalSec - nSecond),
                                org = (550, 30), 
                                fontFace = cv2.FONT_HERSHEY_DUPLEX,
                                fontScale = 1, 
                                color = (255,255,255),
                                thickness = 2, 
                                lineType = cv2.LINE_AA)

                        cv2.putText(img = frame,
                                text = putword,
                                org = (160, 60), 
                                fontFace = cv2.FONT_HERSHEY_DUPLEX,
                                fontScale = 1, 
                                color = (255,255,255),
                                thickness = 2, 
                                lineType = cv2.LINE_AA)

                        timeElapsed = (datetime.now() - startTime).total_seconds()
                #       print 'timeElapsed: {}'.format(timeElapsed)

                        if timeElapsed >= 1:
                                nSecond += 1
                        #       print 'nthSec:{}'.format(nSecond)
                                timeElapsed = 0
                                startTime = datetime.now()

                        if nSecond in wordset:
                                no = random.randrange(0, len(putword), 2)
                                while(no==prevno or word[int(no/2)]==' '):
                                        no = random.randrange(0, len(putword), 2)
                                prevno = no
                                list1 = list(putword)
                                list1[no] = word[int(no/2)]
                                putword = ''.join(list1)
                                wordset.remove(nSecond)
                                print(int(no/2))

                else:
                        startCounter = False
                        nSecond = 0
                        text = 'The word was "' + word + '"'
                        cv2.putText(canvas, text,(100, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 2, cv2.LINE_AA)
                        putword = ' '.join('_' for i in word if i!=' ')
                        if ind!=-1:
                                putword = putword[:ind*2]+ "  " + putword[ind*2:]
                        wordset = set(list2)
                   
        # Enter word if pressed e
        if k == ord('e'):
                word = ''
                putword = ''
                while(True):
                        k = cv2.waitKey(5) & 0xFF
                        #exit entering if pressed backspace
                        if k == 8:
                                break
                        word+=chr(k)
                word = ''.join(filter(lambda ch: ch != 'ÿ', word))
                ind = word.find(' ')
                putword = ' '.join('_' for i in word if i!=' ') #''.join('_ ' for i in word if i != 'ÿ')
                if ind!=-1:
                        putword = putword[:ind*2]+ "  " + putword[ind*2:]

        # Put word if pressed p
        if k == ord('p'):
                text = 'The word was "' + word + '"'
                cv2.putText(canvas, text,(80, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 2, cv2.LINE_AA)

        # Exit if pressed esc
        if k == 27:
                break

        #print("frame shape: ", frame.shape)
        #print("canvas shape: ", canvas.shape)

        # Now this piece of code is just for smooth drawing.
        _ , mask = cv2.threshold(cv2.cvtColor (canvas, cv2.COLOR_BGR2GRAY), 20, 
        255, cv2.THRESH_BINARY)
        foreground = cv2.bitwise_and(canvas, canvas, mask = mask)
        background = cv2.bitwise_and(frame, frame,
        mask = cv2.bitwise_not(mask))
        frame = cv2.add(foreground, background)
        cv2.imshow('image',frame)

        # Clear the canvas after 1 second, if the clear variable is true
        if clear == True: 
                time.sleep(1)
                canvas = None
        
                # And then set clear to false
                clear = False

#print(''.join(filter(lambda ch: ch != 'ÿ', word)))

# close all windows
cv2.destroyAllWindows()
cap.release()      
