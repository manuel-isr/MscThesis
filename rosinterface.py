"""
rosinterface.py

This module contains functions fetch data from the kinects using the ROS
"""

import rospy
from cv_bridge import CvBridge
import numpy as np
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo
import struct
import matmanip as mnip
import pointclouder

def FetchDepthRegisteredRGB(cameraName,topicRGB = "/rgb/image_color", topicDepth ="/depth_registered/image_raw"):
    '''Gets rgb + depth (REGISTERED) of a certain camera
    Registered means - the dpeth is already aligned with the RGB

    Args:
        cameraName (str): camera to capture
        topicRGB (str,optional): topic where the rgb image is
        topicDepth (str,optional): topic where the registered depth image is

    Returns:
        rgb (ROS.Image): rgb Image
        depth_registered (ROS.Image): depth Image 
    '''

    #Create a ROS node
    rospy.init_node('my_name_is_jeff', anonymous=True)

    #Gets the next rgb and depth, that ros returned
    rgb = rospy.wait_for_message(cameraName + topicRGB, Image)
    depth_registered = rospy.wait_for_message(cameraName + topicDepth, Image)
    
    return rgb,depth_registered

def camCalib(cameraName="abretesesamo"):
    ''' Gets the camera intrinsic matrix and the distortion parameters

    Args:
        cameraName(str): camera to get the parameters from

    Returns:
        K [3x3]: intrisic camera matrix
        D []: distortion parameters array 

    ''' 
    rospy.init_node('Do_U_KNO_DA_WAE', anonymous=True)


    #fetch intrinsic parameters
    camInfo = rospy.wait_for_message("/"+cameraName + "/rgb/camera_info", CameraInfo)        

    #transform K
    K = np.asarray(camInfo.K).reshape((3,3))

    return K,camInfo.D

def rgbmatrixfix(rgb):
    '''
    THIS was being used when i forgot to do bgr8 on the rosImg2RGB function
    '''

    r=rgb[:,:,0]

    g=rgb[:,:,1]

    b=rgb[:,:,2]

    #switches channels ordent
    newrgb = np.array([b,g,r])

    newrgb = np.transpose(newrgb,[1,2,0])

    return newrgb


def rosImg2RGB(rosimg):
    '''
    Converts from  ros image to rgn matrix

    Args:
        rosimg (ROS.image): rgb ros image 
    
    Returns:
        rgb [480,640,3] int numpy array: rgb image matrix
    '''

    
    br = CvBridge()

    #converts it
    rgb = br.imgmsg_to_cv2(rosimg, desired_encoding= "bgr8")

    return rgb

def rosDepth2RGB(depthros):
    '''
    Converts from  ros image to depth matrix

    Args:
        depthros (ROS.image): depth ros image 
    
    Returns:
        depth [480,640,1] int numpy array: depth image matrix
    '''
    br = CvBridge()

    #converts it
    depth = br.imgmsg_to_cv2(depthros, desired_encoding="passthrough")

    return depth

def rosCam2RGB(rgbros,depthros):
    '''
    Converts from  ros images to rgb and depth matrix

    Args:
        rgbros (ROS.image): rgb ros image
        depthros (ROS.image): depth ros image 
    
    Returns:
        rgb [480,640,3] int numpy array: rgb image matrix
        depth [480,640,1] int numpy array: depth image matrix
    '''
    
    #bridge to convert ROS image into numpy array
    br = CvBridge()

    #converts'em
    rgb = br.imgmsg_to_cv2(rgbros, "bgr8")
    depth = br.imgmsg_to_cv2(depthros, desired_encoding="passthrough")

    return rgb,depth

#GETS IT THROGUH REGISTERES
def GetPointCloudRGBD(cameraName,K):
    rgb,depth_reg = GetRGBD(cameraName)
   
    points = mnip.depthimg2xyz(depth_reg,K)
    points = points.reshape((480*640, 3))
    

    rgb1 = rgb.reshape((480*640, 3))

    pc = pointclouder.Points2Cloud(points,rgb1)
    
    return pc,rgb,depth_reg

def GetRGBD(cameraName):
    '''Gets rgb + depth (REGISTERED) of a certain camera
    Registered means - the dpeth is already aligned with the RGB

    Args:
        cameraName (str): camera to capture
    
    Returns:
        rgb [480,640,3] int numpy array: rgb image matrix
        depth [480,640,1] int numpy array: depth image matrix
    '''

    #gets it
    rgbros,depthros = FetchDepthRegisteredRGB(cameraName)

    #converts it
    rgb,depth = rosCam2RGB(rgbros,depthros)

    return rgb,depth

def pcROS2rgbpos(msg):

    r=[]
    g=[]
    b=[]
    
    x1=[]
    y1=[]
    z1=[]
    for i in range(0, msg.height*msg.width):

        x = msg.data[i*msg.point_step:i*msg.point_step+4]
        y = msg.data[i*msg.point_step+4:i*msg.point_step+4+4]
        z = msg.data[i*msg.point_step+4+4:i*msg.point_step+4+4+4]
        rgb = msg.data[i*msg.point_step+4+4+4+4:i*msg.point_step+4+4+4+4+4]
        
        [xx] = struct.unpack('f', x)
        [yy] = struct.unpack('f',y)
        [zz] = struct.unpack('f',z)
        #print("x",xx)
        #print("y",yy)
        #print("z",zz)
        #print("c",rgb)

        #boi = struct.unpack('!f', mss)
        #print("fetched",boi)
        x1.append(xx)
        y1.append(yy)
        z1.append(zz)
        
        b.append(255-ord(rgb[0])) #com ou sem 255-
        g.append(255- ord(rgb[1]))
        r.append(255 -ord(rgb[2]))
        #alpha.append(ord(rgb[3  ]))

    rgb = np.vstack((r,g,b))
    pos = np.vstack((x1,y1,z1))
    print(rgb.shape)

    return rgb,pos
