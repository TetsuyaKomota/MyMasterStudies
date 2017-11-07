import cv2
import numpy as np
import pykinect
from pykinect import nui
#import thread
import sys

# Video
def video_frame_ready( frame ):
    if videoDisplay == False: return

    video = np.empty( ( 480, 640, 4 ), np.uint8 )
    frame.image.copy_bits( video.ctypes.data )
    #cv2.imshow( 'video', video )
    cv2.imshow( 'frame', video )

# Depth
def depth_frame_ready( frame ):
    if videoDisplay == True: return

    depth = np.empty( ( 240, 320, 1 ), np.uint16 )
    frame.image.copy_bits( depth.ctypes.data )
    #cv2.imshow( 'depth', depth )
    cv2.imshow( 'frame', depth )

if __name__ == '__main__':
    #screenLock = thread.allocate()

    videoDisplay = False

    kinect = nui.Runtime()

    kinect.video_frame_ready += video_frame_ready
    kinect.depth_frame_ready += depth_frame_ready

    kinect.video_stream.open( nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color )
    kinect.depth_stream.open( nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth )

    '''
    cv2.namedWindow( 'video', cv2.WINDOW_AUTOSIZE )
    cv2.namedWindow( 'depth', cv2.WINDOW_AUTOSIZE )
    '''
    cv2.namedWindow( 'frame', cv2.WINDOW_AUTOSIZE )

    #
    while True:
        #waitKey() は ASCIIコードを返す
        key = cv2.waitKey(33)
        if key == 27: # ESC
            break
        elif key == 118: # 'v'
            print >> sys.stderr, "Video stream activated"
            videoDisplay = True
        elif key == 100: # 'd'
            print >> sys.stderr, "Depth stream activated"
            videoDisplay = False

    cv2.destroyAllWindows()
    kinect.close()
