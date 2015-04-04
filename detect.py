import cv2
import numpy as np
import subprocess
import threading
import time
import image
import motor

sides=6

def match_img(flann, scene, needle):
    matches = flann.knnMatch(needle.descriptors,scene.descriptors,k=2)
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)
    if len(good) >= 9:
        src_pts = np.float32([ needle.keypoints[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([  scene.keypoints[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matches_mask = mask.ravel().tolist()

        h,w,depth = needle.img.shape
        pts = np.float32([[0,0], [0,h-1], [w-1,h-1], [w-1,0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts, M)

        drawn = scene.img
        cv2.polylines(drawn, [np.int32(dst)], True, 255, 3, cv2.CV_AA)

        return (True,  M,    drawn,     mask, good)
    else:
        return (False, None, scene.img, None, good)

def detect_side(dice, img):
    global disp_img
    global cv_display

    image.process(sift, img)
    num = [ 0 for i in range(sides) ]
    for i in range(sides):
        rv, M, img.img, mask, good = match_img(flann, img, dice[i])
        if rv:
            num[i] += len(good)

    ret = -1
    if sum(num) != 0:
        for n in range(sides):
            if num[n]*3 >= sum(num)*2:
                ret = n
                break

    if ret != -1:
        img.img[0:dice[ret].img.shape[0],
                0:dice[ret].img.shape[1]] = dice[ret].img

    cv_display.acquire()
    disp_img = img.img
    cv_display.notify()
    cv_display.release()
    print(num)

    return ret, img

cv_shake   = threading.Condition()
cv_grab    = threading.Condition()
cv_process = threading.Condition()
grabbed_image = None

cv_display = threading.Condition()
disp_img = None

do_shake = False
do_grab = False
do_process = False

running = True

def shake_thread():
    print("Shake thread started")
    global do_shake
    global do_grab
    global running
    while running:
        cv_shake.acquire()
        if do_shake == False:
            cv_shake.wait()
        
        motor.shake()
        do_shake = False
        
        cv_grab.acquire()
        do_grab = True
        cv_grab.notify()
        cv_grab.release()
        
        cv_shake.release()

def grab_thread():
    global grabbed_image
    global do_shake
    global do_grab
    global do_process
    global running
    print("Grab thread started")
    while running:
        cv_grab.acquire()
        if do_grab == False:
            cv_grab.wait()
        
        tmp = image.grab_image()
        do_grab = False
        
        cv_shake.acquire()
        do_shake = True
        cv_shake.notify()
        cv_shake.release()
        
        cv_process.acquire()
        do_process = True
        grabbed_image = tmp
        cv_process.notify()
        cv_process.release()

        cv_grab.release()

def display_thread():
    global cv_display
    global disp_img
    global running

    i = None
    while running and i == None:
        cv_display.acquire()
        cv_display.wait()
        if disp_img != None:
            i = disp_img
            cv2.imshow('frame', i)
            disp_img = None
        cv_display.release()
    
    while running:
        cv_display.acquire()
        if disp_img != None:
            i = disp_img
            cv2.imshow('frame', i)
            disp_img = None
        cv_display.release()
        key = cv2.waitKey(20) & 0xFF
        if key == ord('q'):
            running = False

cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

sift = cv2.SIFT()

dice = [ image.open_image("%d.jpg" % (i,), i) for i in range(1, sides + 1) ]

[ image.process(sift, i) for i in dice ]

FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

motor.init("/dev/ttyUSB0", 9600)

threading.Thread(target = shake_thread).start()
threading.Thread(target = grab_thread).start()
threading.Thread(target = display_thread).start()

cv_shake.acquire()
cv_shake.notify()
cv_shake.release()

num = [0 for i in range(sides) ]
nums = []
added = 0
log = open('log', 'a')

while running:
    cv_process.acquire()
    print("Acquired process lock")
    if do_process == False:
        print("Wait for image")
        cv_process.wait()
            
    tmp = grabbed_image
    do_process = False
    print("Processing")
    n, img = detect_side(dice, tmp)
    cv_process.release()
    print("Released process lock\n")
        
    if n != -1:
        num[n] += 1
        log.write("%d\n" % (n, ))
        log.flush()
        added += 1
    else:
        cv2.imwrite("failure.png", img.img)
    if added > 0:
        print(n, [int(n * 100. / added) for n in num])

