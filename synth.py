"""
synth.py

This module contains functions to:
-Generate Synthetic Observations in a set of Referentials
-Generate Synthetic scenes and models (Sets of Referantials)
-Generate Synthetic Observations between a Set of Referantials(Cameras) that are observing another set (Aruco)
"""

import numpy as np
import random
import matmanip as mmnip
   

def SampleGenerator(R,t,samples=1000,noise = 0.00001,noiset=0.0001):
    ''' Generates observations(Rotations and translations) between a set of Referentials

    Args:
        R: List of rotations of the referentials
        t: List of translations of the referentials
        samples: Approximated number of samples to generate
        noise: Noise scale in degrees that will be added to the rotations observed
        noiset: Noise scale in degrees that will be added to the tranlations observed

    Returns:
        obsR: Dictionary with the Rotation Observations. Each Observations Contains
            -from: Where the rotation comes from
            -to: Where the rotation is going to
            -R: The rotation itself
        obst: Dictionary with the Translation Observations. Each Observations Contains
            -from: Where the rotation comes from
            -to: Where the rotation is going to
            -t: The translation itself
    '''

    #initializes array that tells if this rotation r[i] has atleast one observation
    r = np.zeros([len(R),1])  

    #for a while (this loop only occurs 1 time if we are lucky)
    while True:

        obsR = []
        obst = []

        #generates samples
        for i in range(0,samples):

            #for each observation        

            #pick 2 different ids
            r1 =  random.randint(0, len(R)-1)
            r2 = r1
            while r2==r1:
                r2 = random.randint(0, len(R)-1)
            


            t1w = t[r1] #translation of referantial 1 in world coordinates
            t2w = t[r2] #translation of referantial 2 in world coordinates
                        
            t12 =np.dot(R[r2].T, t1w - t2w) #translation of referantial 1 in referantial 2's coordinates
            
            #generate a R observation w/ noise
            obsR.append({"from":r2,"to":r1,"R":np.dot(mmnip.genRandRotMatrix(noise),np.dot(R[r1],R[r2].T))})
            
            #generate a t observation  w/ noise
            obst.append({"from":r1,"to":r2,"t":t12+np.random.rand(3)*noiset}) #*noiset
            
            #sets this cameras as having observations
            r[r1]=1
            r[r2]=1


        #there is at least one observation per marker then, exit, else generate more samples
        if sum(r)==len(R):
            break

    return obsR,obst





def MultiCamSampleGeneratorFixed(Rcam,tcam,R,t,nObs=5,noise = 0.01,noiset = 0.01):
    '''
    Simulates one single time instance and generates Synthetic Observations
    between a Set of Referantials(Cameras) that are observing another set (Aruco)
    
    Every rotation received comes from world coordinates  w -> i
    Every translation received is to world coordinates  i -> w

    Args:
        Rcam: List of rotations of every camera
        tcam: List of translations  of every camera
        R: List of rotations of the aruco model that both cameras see
        t: List of translations  of the aruco model that both cameras see
        nObs: Number of Markers that each camera sees,
        noise: Noise added to the rotations
        noiset: Noise added to the translations
    '''

    #number of observations of a camera in a certain frame, prevent it from being bigger than all markers
    if(nObs>len(tcam)):
        print("Warning: Number of observations requested higher than total markers")
        nObs=len(tcam)-1


    camsObs = []        #list of all observations
    
    #generate samples for each camera
    for i in range(0,len(Rcam)):
        
        #pick random aruco markers, #noBs of them
        rnds = random.sample(range(1, len(R)), nObs)

        obs=[]  #list of Observations
        
        #For each observed marker
        for r in rnds:
            

            tcr =np.dot(Rcam[i].T, t[r] - tcam[i]) # t from observation r to camera i  


            #generate the samples  'from' Camera i 'to' sample i
            #'ObsId' = 'to'                 #'camId = to ObsId = 'from'
            #assign them to each camera
            o ={ "obsId":r,"R": np.dot(mmnip.genRotMat(np.squeeze([np.random.rand(3,1)*noise])), np.dot(R[r],Rcam[i].T)),'t':tcr}
            obs.append(o)
            
        camsObs.append(obs)



    return camsObs

def Scenev1():
    '''
    Generate a scene with 3 cameras
    '''

    R=[]
    t=[]

    R.append(mmnip.genRotMat([0,180,0]))
    R.append(mmnip.genRotMat([0,-90,0]))
    R.append(mmnip.genRotMat([0,0,0]))

    t.append(np.array([0,0,0]))
    t.append(np.array([50,0,-50]))
    t.append(np.array([0,0,-100]))

    return R,t

def FakeArucoRotated():
    '''Generate aruco model with 4 markers'''

    R=[]
    t=[]

    R.append(mmnip.genRotMat([90,180,0]))
    R.append(mmnip.genRotMat([90,90,0]))
    R.append(mmnip.genRotMat([90,0,0]))
    R.append(mmnip.genRotMat([90,-90,0]))
    
    t.append(np.array([0,10,0]))
    t.append(np.array([10,0,0]))
    t.append(np.array([0,-10,0]))
    t.append(np.array([-10,0,0]))

    return R,t


def FakeAruco():
    '''Generate aruco model with 4 markers'''

    R=[]
    t=[]

    R.append(mmnip.genRotMat([0,0,0]))
    R.append(mmnip.genRotMat([0,90,0]))
    R.append(mmnip.genRotMat([0,180,0]))
    R.append(mmnip.genRotMat([0,270,0]))
    
    t.append(np.array([0,0,10]))
    t.append(np.array([10,0,0]))
    t.append(np.array([0,0,-10]))
    t.append(np.array([-10,0,0]))

    return R,t

   
def FakeArucoReal():
    '''Generate aruco model with 12 markers'''

    R=[]
    t=[]

    R.append(mmnip.genRotMat([0,0,0]))
    R.append(mmnip.genRotMat([0,0,0]))
    R.append(mmnip.genRotMat([0,0,0]))

    R.append(mmnip.genRotMat([0,90,0]))
    R.append(mmnip.genRotMat([0,90,0]))
    R.append(mmnip.genRotMat([0,90,0]))
    
    R.append(mmnip.genRotMat([0,180,0]))
    R.append(mmnip.genRotMat([0,180,0]))
    R.append(mmnip.genRotMat([0,180,0]))

    R.append(mmnip.genRotMat([0,270,0]))
    R.append(mmnip.genRotMat([0,270,0]))
    R.append(mmnip.genRotMat([0,270,0]))
    
    t.append(np.array([0,0,10]))
    t.append(np.array([0,30,10]))
    t.append(np.array([0,50,10]))

    t.append(np.array([10,0,0]))
    t.append(np.array([10,30,0]))
    t.append(np.array([10,50,0]))

    t.append(np.array([0,0,-10]))
    t.append(np.array([0,30,-10]))
    t.append(np.array([0,50,-10]))

    t.append(np.array([-10,0,0]))
    t.append(np.array([-10,30,0]))
    t.append(np.array([-10,50,0]))

    return R,t






