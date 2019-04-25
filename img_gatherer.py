import rosinterface as roscv
import numpy as np
import cv2
import aruco
import probdefs
import observationgenner as obsGen


class img_gather(object):
    def __init__(self,N_cams,arucoModel):
      
        self.N_cams = N_cams

        self.gatherCounter = [0]*N_cams

        self.gatherReady = np.zeros((N_cams),dtype=np.uint8)

        self.images =  np.zeros((480,640*N_cams,3),dtype=np.uint8)

        self.Allobs = [ [] for i in range(self.N_cams) ]

        print(self.Allobs)

        self.R = arucoModel['R']
        self.t = arucoModel['t']

        self.ATA = np.zeros((N_cams*3,N_cams*3))

        #print("obs")
        #print(self.Allobs)
        
    def showImg(self):
        cv2.imshow("Image window ",self.images)           
        cv2.waitKey(1)
        #print(self.gatherCounter)

    def GatherImg(self,camId,img,obs):
        #print("on gather img")
        self.images[0:480,camId*640:camId*640+640,0:3]=img
        
        #print(np.sum(img-self.images[0:480,camId*640:camId*640+640,0:3]))
        self.gatherCounter[camId] = self.gatherCounter[camId] +1
        
        self.gatherReady[camId]=1

        self.Allobs[camId]=self.Allobs[camId] +obs  # WRONG SHOULD IT BE concantenate lists OR =?

        print("afteradding")
        print(self.Allobs)

        if(np.sum(self.gatherReady)== self.N_cams):
            

            #Generate Pairs
            obsR , _ = obsGen.GenerateCameraPairObs(self.Allobs,self.R,self.t)

            ATA = probdefs.rotationProbDef(obsR,self.N_cams)

            self.ATA = self.ATA + ATA

            #cleanse
            self.gatherReady = np.zeros((self.N_cams),dtype=np.uint8)

            #clear observations
            self.Allobs = [ [] for i in range(self.N_cams) ]
        



    



            

            
            
        
        




   