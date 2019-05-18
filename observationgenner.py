"""
observationgenner.py

This module contains functions that make pairs of observations
"""
import numpy as np
import matmanip as mmnip
import aruco
import cv2

import visu


def ObsViewer(obs,key="R",fro="from",to="to",pause=True,show=False):
    
    for o in obs:
        print("from:" + str(o[fro])+" to:"+str(o[to]))
        print("Det is:" + str(np.linalg.det(o[key])))
        print(o[key])
        if show:
            visu.ViewRefs([np.eye(3),o[key]])
        if pause:
            raw_input()



def Cam2ArucoObsMaker(img,K,D,markerIDoffset,Nmarkers):
    '''
    this function creates observations between this camera and every aruco marker it sees

    if the camera sees markers 1 2 and 3

    it will generate Rcam_1 Rcam_2 and Rcam_3

    THIS FUNCTION WILL GENERATE SAMPLES FOR A SINGLE CAMERA
    
    Args:
        K - intrinsic camera matrix
        D - distortion parameters
        det_corners - all detected corners
        hello - image that has the aruco detections added to it on top
        ids - all detected ids

    Returns:
        observations (dict array):All marker observations made by this camera
            obsId: observed aruco marker
            t: translation from obsId to camera (marker position in world coordinates)
            R: rotation from camera to obsId
    '''
    
    #fetches detected markers
    det_corners, ids, rejected = aruco.FindMarkers(img, K)

    #changes image
    hello = img.astype(np.uint8).copy() 
    hello = cv2.aruco.drawDetectedMarkers(hello,det_corners,ids)
    
    #list of all observations generated
    observations =[]

    #if more than one marker was detected
    if  ids is not None and len(ids)>1:

        #finds rotations and vectors and draws referentials on image
        rots,tvecs,img = aruco.FindPoses(K,D,det_corners,hello,len(ids),arucoData['size'])

        #squeeze
        ids = ids.squeeze()


        #generates samples
        for i in range(0,len(ids)):                
                 
                 #only valid markers
                if ids[i] not in arucoData['ids']:
                    print("Invalid marker id: "+str(ids[i]))
                    continue 

                #initializes observation
                o ={"obsId":arucoData['idmap'][str(ids[i])]}

                #generate R observations
                o['R']=rots[i]

                #generate t observations
                o['t']=np.squeeze(tvecs[i]) #WRONG - Not sure if this is the correct t
                
                observations.append(o)
 
    return observations ,img



def Cam2ArucoObsMaker2(img,K,D,arucoData):
    '''
    this function creates observations between this camera and every aruco marker it sees

    if the camera sees markers 1 2 and 3

    it will generate Rcam_1 Rcam_2 and Rcam_3

    THIS FUNCTION WILL GENERATE SAMPLES FOR A SINGLE CAMERA
    
    Args:
        K - intrinsic camera matrix
        D - distortion parameters
        det_corners - all detected corners
        hello - image that has the aruco detections added to it on top
        ids - all detected ids

    Returns:
        observations (dict array):All marker observations made by this camera
            obsId: observed aruco marker
            t: translation from obsId to camera (marker position in world coordinates)
            R: rotation from camera to obsId
    '''
    
    #fetches detected markers
    det_corners, ids, rejected = aruco.FindMarkers(img, K)

    #changes image
    hello = img.astype(np.uint8).copy() 
    hello = cv2.aruco.drawDetectedMarkers(hello,det_corners,ids)
    
    #list of all observations generated
    observations =[]

    #if at least one marker is detected
    if  ids is not None and len(ids)>0:

        #finds rotations and vectors and draws referentials on image
        rots,tvecs,img = aruco.FindPoses(K,D,det_corners,hello,len(ids),arucoData['size'])

        #squeeze
        ids = ids.squeeze()

        #special 1 element case
        ids = ids.tolist()
        if(type(ids)==int):
            ids=[ids]

        #generates samples
        for i in range(0,len(ids)):                
                 
                 #only valid markers
                if ids[i] not in arucoData['ids']:
                    print("Invalid marker id: "+str(ids[i]))
                    continue 

                #initializes observation
                o ={"obsId":arucoData['idmap'][str(ids[i])]}

                #generate R observations
                o['R']=rots[i]


                #generate t observations
                o['t']=np.squeeze(tvecs[i]) #WRONG - Not sure if this is the correct t
                
                observations.append(o)
 
    return observations ,img


def GenerateCameraPairObs(camsObs,R,t):
    '''
    Generate observations between 2 cameras, by doing Transformations throught the aruco

    camObs (list of list of dicts) - first list dimensions tells us the camera, the second list is all the observations for that camera
    R - rotations of the aruco model
    t - translation of the aruco model
    '''

    #initialize observation lists
    obsR = []
    obsT = []


    #this double for loop makes all camera combinations
    #between one camera
    for i in range(0,len(camsObs)):
        #and another camera
        for j in range(i+1,len(camsObs)):
            
            #this double loop matches every possible observation in each camera        
            #go through all the obs of one camera
            for obsiR in camsObs[i]:
                #and through all the obs of the other
                for obsjR in camsObs[j]:
                
                    #confusing as fuck i, know
                    # pretty much we have Rcam_i -> obsId_i and Rcam_j -> obsId_j   - to what each camera is observating is alwaying
                    # 'ObsId' = 'to' , and the cameraId on the array is the 'from'
                    
                    #print("from camera:"+str(j)+" to camera:"+str(i))
                    #print(np.linalg.multi_dot([obsiR['R'].T,R[obsiR['obsId']],R[obsjR['obsId']].T,obsjR['R']]))
                    #raw_input()

                    obsR.append({"from":j,"to":i,"R": np.linalg.multi_dot([obsiR['R'],R[obsiR['obsId']].T,R[obsjR['obsId']],obsjR['R'].T])})
                    
                    #print("obsJ")
                    #print(obsjR['t'])

                    #print("obsI")
                    #print(obsiR['t'])

                    #Get aruco transformation parameters
                    Rbetweenaruco = np.dot(R[obsjR['obsId']].T,R[obsiR['obsId']])
                    tbetweenaruco = np.dot(R[obsjR['obsId']].T, t[obsiR['obsId']] - t[obsjR['obsId']])
                   
                    #print("Tbetween aruco")
                    #print(tbetweenaruco)

                    #transform from marker1  coordinates to marker2 coordinates
                    new_t =  mmnip.Transform(mmnip.InvertT(obsiR['R'], obsiR['t']),Rbetweenaruco, tbetweenaruco)

                    #print("new_T")
                    #print(new_t)

                    #print("new_T")
                    #print( obsjR['t'])

                    
                    #transform from marker2 coordinates to camera j coordinates                    
                    tij = mmnip.Transform(new_t, obsjR['R'], obsjR['t'] )

                    #print(tij)

                    #quit()

                    obsT.append({"from":i,"to":j,"t": tij})

    return obsR,obsT