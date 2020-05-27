#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use node information (such as position and velocity) to create output in the
form of a TCL file. This TCL file can then be processed by Ns-3.

Author: Ben Frey
Email: ben.frey@stthomas.edu; freynben@gmail.com
Last revision: 27-05-2020

***License***:

This file is part of VANET-DT.

VANET-DT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

VANET-DT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>
"""

import numpy as np
import os

def writeToTCL(dataframe, nodes, mps, fps):
    """Class to make TXT file of node locations.
    
    Parameters
    ----------
    dataframe : Pandas Dataframe
        Contains locations of all nodes at all simulations steps. 
    nodes : int
        Amount of nodes in the simulation
    mps : int
        Movements per second we want to observe.
    fps : int
        Frames per second of simulation.

    Returns
    -------
        None
    """
    
    # Choose filename to save trace information under.
    fileName = "mobility"
    
    # Modify dataframe such that we eleminate frames we do want and we can 
    # get our ideal mps.
    posX = dataframe['px'].values
    posY = dataframe['py'].values
    time = dataframe['time'].values
    speed = dataframe['speed'].values
    
    fileString = fileName+".txt"
    fileRef  = open(fileString, "w+") 
    
    # Change np precision when printing to string.
    np.set_printoptions(precision=3)
    
    # Setup node initial conditions.
    for i in range(nodes):
        outString = "$node_("+str(i)+") set X_ "+str(np.around(posX[i], decimals=2))+"\n"+"$node_("+str(i)+") set Y_ "+str(np.around(posY[i], decimals=2))+"\n"+"$node_("+str(i)+") set Z_ 0\n"        
        fileRef.write(outString)

    # Go through entire dataframe, updating positions.
    for i in range(1,int((time[-1]))+1):
        for j in range(nodes):
            outString = "$ns_ at "+str(np.around(float(time[i*nodes])/10, decimals=1))+' "$node_('+str(j)+') setdest '+str(np.around(posX[(i*nodes)+j], decimals=2))+' '+str(np.around(posY[(i*nodes)+j], decimals=2))+' '+str(np.around(20*speed[(i*nodes)+j], decimals=2))+'"\n'   
            fileRef.write(outString)       
            
    #$ns_ at 0.0 "$node_(0) setdest 523.92 536.11 0.00"
    
    # Finalize file and close
    fileRef.close() 
    
    # Change file referenece extension
    base = os.path.splitext(fileString)[0]
    os.rename(fileString, base + '.tcl')
