
import numpy as np

import synth

import rospy

import pickler as pickle

import matmanip as mmnip

import visu 

import ArucoInfoGetterv2 as ArucoInfoGetter

import random

import probdefs
import algos

import observationgenner as obsGen

import img_gatherer as gather

import cv2

import visu



from sensor_msgs.msg import Image

def main():

    #Load aruco Model
    arucoModel = pickle.Out("static/ArucoModel 23-04-2019 13-45-37.pickle")

     

    showVideo = 1
    calc = 0  #0 is R 1 is t 2 is R for cameras, 4 is t for cameras


    camsName = ["abretesesamo","ervilhamigalhas"]

    #create gather class
    g = gather.img_gather(len(camsName),arucoModel)

    rospy.init_node('my_name_is_jeff', anonymous=True)

    camInfo = pickle.Out("static/CameraInfo 20-04-2019.pickle")

    arucoGetters=[]

    # all of the parameters
    cb_params =	{}
    # all of the functions
    cb_functions = []

    for i in range(0,len(camsName)):

        #initialize class for each camera
        ig = ArucoInfoGetter.ArucoInfoGetter(camInfo['K'],camInfo['D'],showVideo,calc,None,i,g)

        #saves it for some reason
        arucoGetters.append(ig)

        #subscribe to each camera
        rospy.Subscriber(camsName[i] + "/rgb/image_color", Image, ig.callback,(cb_params,cb_functions))


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shut")

    cv2.destroyAllWindows()


    
    rotsols = algos.TotalLeastSquares(g.ATA,3,g.N_cams)


    #visu.ViewRefs(rotsols)
    
    Rrel = mmnip.genRotRel(rotsols)

    #visu.ViewRefs(Rrel)


















if __name__ == '__main__':
    main()