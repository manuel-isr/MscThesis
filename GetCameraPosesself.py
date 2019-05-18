import sys,getopt
import rospy
from optparse import OptionParser
import json
import rosinterface
import numpy as np

import datetime

import pickler2 as pickle

import message_filters

from sensor_msgs.msg import Image
import random

import CamPoseGetter1


import algos
import cv2

import FileIO

import matmanip as mmnip

import commandline

import StateManager

import visu

def main(argv):

    freq=50

    arucoData, arucoModel,settings,camNames = ParsingInputs(argv)

    #fetch K of existing cameras on the files
    intrinsics = FileIO.getKDs(camNames)

    #has all states that may change
    stateru = StateManager.State(len(camNames),"realtime")

    

    rospy.init_node('do_u_kno_di_wae', anonymous=True)

    #Load aruco Model
    arucoModel = FileIO.getJsonFromFile("./static/arucoModel manatee 18-05-2019 17:25:02.json")

    #sets class where image thread will run
    camposegetter=CamPoseGetter1.CamPoseGetter(camNames,arucoData,arucoModel,intrinsics,stateru)



    #sets thread where state changer will be
    commandline.Start(stateru,rospy)

    camSub = []

    #getting subscirpters to use message fitlers on
    for name in camNames:
        camSub.append(message_filters.Subscriber(name+"/rgb/image_color", Image))

    ts = message_filters.ApproximateTimeSynchronizer(camSub,20, 1.0/freq, allow_headerless=True)
    ts.registerCallback(camposegetter.callback)

    print("Fetching Messages")    
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shut")


    cv2.destroyAllWindows()

    print("Finished Elegantly")

    stateru.R2 = stateru.R2/stateru.count

    stateru.t = stateru.t2/stateru.count

    stateru.R = algos.procrustesMatlabJanky(stateru.R2,np.eye(3))

    print("R is:")
    print(stateru.R)

    print("t is:")
    print(stateru.t)

    #SaveCameraPoses(stateru.R,stateru.t,camNames,"cameras")

def SaveCameraPoses(R,t,camNames,objectname="cameras"):


    f=open("static/names.json","r")

    arr = json.load(f)

    filename = random.choice(arr)
    f.close()

    fullfile={}
    fullfile[objectname]=[]

    for RR,tt,cc in zip(R,t,camNames):
        fullfile[objectname].append({"R":RR.tolist(),"t":tt.tolist(),"name":cc})

    saveName = filename+" " +  datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    f = open("./scenes/"+saveName+".json","w")



    json.dump(fullfile,f)
    
    f.close()

    print("Saved File: "+str(saveName))





def ParsingInputs(argv):
    parser = OptionParser()
    parser.add_option("-a", "--aruco")
    parser.add_option("-m", "--arucomodel")
    parser.add_option("-s", "--settings")
    parser.add_option("-c", "--cameras",action="append")

    (options, args) = parser.parse_args()

    #for opt in options:
    #    print(opt)
    print(options)
    f=None
    options = options.__dict__
    #aruco data

    if options['aruco'] is not None:
        f=open(options['aruco'],"r")
    else:
        f=open("./static/ArucoWand.json","r")
    
    arucoData = json.load(f)

    f.close()

    #settings

    if options['settings'] is not None:
        f=open(options['settings'],"r")
    else:
        f=open("./static/obsconfig_default.json","r")
    
    settings = json.load(f)

    f.close()

    #aruco model

    if options['arucomodel'] is not None:
        f=open(options['arucomodel'],"r")
    else:
        print("CREATE DEFAULT ARUCO MODEL")#f=open("./static/obsconfig_default.json","r")
    
    print("not loading model right now")
    #arucoModel = json.load(f)
    arucoModel = None

    f.close()    

    #cameras
    #print(options['cameras'])

    return arucoData , arucoModel,settings,options['cameras']

if __name__ == '__main__':
    main(sys.argv[1:])