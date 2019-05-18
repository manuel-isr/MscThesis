"""
CamPoseGetter.py

This module contains the a class receives all the images and observations of the cameras, and calculates stuff with it
"""

import numpy as np
import cv2
import aruco
import probdefs
import observationgenner as obsGen
import rosinterface as IRos


class CamPoseGetter(object):
    def __init__(self,camNames,arucoData,arucoModel,intrinsics,stateru):
        
        self.state = stateru

        self.R2=np.zeros((3,3))


        self.t2=np.zeros((3,1))

        #number of camera
        self.N_cams = len(camNames)

        self.camNames = camNames

        #Array where several camera images will be concatenated into
        self.images =  np.zeros((480,640*self.N_cams,3),dtype=np.uint8)

        #list of empty lists where observations will be saved (first dim tells camera, second dim is the observations for that cam)
        self.Allobs = [ [] for i in range(self.N_cams) ]

        #intrinsic Params
        self.intrinsics = intrinsics

        self.arucoData=arucoData

        self.R = []
        self.t = []

        for marker in arucoModel['markers']:
            #get aruco model

            RR = np.asarray(marker['R'])
            tt = np.squeeze(np.asarray(marker['t']))

            self.R.append(RR)
            self.t.append(tt)

        #self.R= np.asarray(self.R)
        #self.t= np.asarray(self.t)


        self.count = 0

        #for tt in arucoModel['t']:
        #    self.t.append(np.squeeze(tt))

        #Array where several camera images will be concatenated into
        self.images =  np.zeros((480,640*self.N_cams,3),dtype=np.uint8)

       


        #A.T b initialized
        self.ATb = np.zeros((self.N_cams*3,1)) 


        self.lol=np.zeros((3,3))

        self.arucoData['idmap'] = self.markerIdMapper(arucoData['ids'])
        
    def markerIdMapper(self,arr):

        IdMap={}
       
        for i in range(0,len(arr)):
            IdMap[str(arr[i])]=i
       
        return IdMap
    
    def callback(self,*args):

        #print("callback: "+str(self.count))
        #print(self.state.readyToCapture)
        if(self.state.readyToCapture==False):
            return

        self.count = self.count + 1
        #print(self.N_cams)
        #print(len(args))
        #print(self.state.stateDict)

        #iterate throguh cameras
        for camId in range(0,self.N_cams):
            img = IRos.rosImg2RGB(args[camId])

            #get observations of this camera, and image with the detected markers and referentials shown
            obs, img = obsGen.Cam2ArucoObsMaker2(img,self.intrinsics['K'][self.camNames[camId]],self.intrinsics['D'][self.camNames[camId]],self.arucoData)

            #print("obslen "+str(len(obs)))
            #if camId==0 and len(obs)>0:
            #    print(obs[0]['t'])

            #set image
            self.images[0:480,camId*640:camId*640+640,0:3]=img

            #get new observations of that camera
            self.Allobs[camId]=obs  # WRONG SHOULD IT BE concantenate lists OR =?

        #Generate Pairs from all of the camera observations
        obsR , obsT = obsGen.GenerateCameraPairObsSelf(self.Allobs,self.R,self.t)

        rrr=np.zeros((3,3))
        ttt=np.zeros((3,))
        for oR,oT in zip(obsR,obsT):
            
            ttt=oT['t']+ttt
            rrr=oR['R']+rrr


        self.state.R2 = self.state.R2 + rrr
        self.state.count=self.state.count+len(obsT)
        self.state.t2 = self.state.t2 + ttt

            


        #clear observations
        self.Allobs = [ [] for i in range(self.N_cams) ]

        if self.state.showImg==True:
            self.showImg(self.state.detectionMode)

        if(self.state.detectionMode=="snap"):
            self.state.readyToCapture=False


    def showImg(self,mode):
        '''Displays images from all cameras
        '''
        
        cv2.imshow("Image window ",self.images)           
        
        if(mode=="snap"):
            cv2.waitKey(0)

        if mode=="realtime":
            cv2.waitKey(1)

        if(mode=="snap"):
            cv2.destroyAllWindows()
        



        



    



            

            
            
        
        




   