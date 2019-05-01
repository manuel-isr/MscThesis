#HERE WILL BE the v1, but organized in a good fashion
import ArucoInfoGetter
import rospy
import algos
import pickler as pickle
from sensor_msgs.msg import Image

import cv2
import open3d
import numpy as np
import visu
import matmanip as mmnip

#import snapper

def main():
    showVideo = 1
    calc = 0  #0 is R 1 is t

    

    cameraName = "abretesesamo"

    rospy.init_node('my_name_is_jeff', anonymous=True)

    camInfo = pickle.Out("static/CameraInfo 20-04-2019.pickle")


    ig = ArucoInfoGetter.ArucoInfoGetter(camInfo['K'],camInfo['D'],showVideo,calc)
     
    #snapper.Start(ig.GetImg)

    # all of the parameters
    cb_params =	{}
     # all of the functions
    cb_functions = []

    

    rospy.Subscriber(cameraName+"/rgb/image_color", Image, ig.callback,(cb_params,cb_functions))


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shut")

    cv2.destroyAllWindows()
    


    print("global1")
    rotSols = algos.RProbSolv1(ig.ATA,3,ig.Nmarkers)    
    visu.ViewRefs(rotSols)


    
    pickle.In("ArucoRot","Rglob",rotSols)

    
    print("local1")
    
    rr = mmnip.genRotRel(rotSols)
    visu.ViewRefs(rr)

    pickle.In("ArucoRot","Rloc",rr)
    
    print("localleft1")
    rr = mmnip.globalRotateRotsl(rotSols)
    visu.ViewRefs(rr)

    pickle.In("ArucoRot","Rlocleft",rr)

    print("localweird mode")

    Rrelations = []

    #generate R between each things
    for j in range(0,len(rotSols)):
        Rrelations.append(np.dot(rotSols[j].T,rotSols[0])) #Rw2*R1w' = R12

    
    visu.ViewRefs(Rrelations)




if __name__ == '__main__':
    main()