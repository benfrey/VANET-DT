#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file controls the movement of node objects around the simulation space.
Given certain attributes such as simulation space size and amount of nodes
to simulate, we can iterate through the simulation and move these node
objects around.

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
import pandas as pd

class Nodes():
    """Class of Nodes, this deals with all the nodes that move around sim space.
    
    Parameters
    ----------
    init_state : np array of floats
        Nx8 array 

    Returns
    -------
        Tot energy of planet (U and KE).
    """
    def __init__(self, init_state, bounds, size, fps, N, frames, maxVel, maxAccel):
        self.init_state = np.asarray(init_state, dtype=float)
        self.size = size
        self.state = self.init_state.copy()
        self.time_elapsed = 0
        self.bounds = bounds
        self.N = N
        self.fps = fps
        self.maxVel = maxVel
        self.maxAccel = maxAccel
        self.frames = frames   
        self.r = self.init_state.copy()
        self.dTemp = pd.DataFrame({"node":[], "time":[],
                       "px":[],"py":[],"speed":[]})

    def step(self, dt):
        """step once by dt seconds"""
        # Ensure that the step count does not exceed our amount of frames.
        step = int(self.time_elapsed/dt)
        if (step) == self.frames:
            return
        self.time_elapsed += dt

        # Reset dTemp dataframe
        self.dTemp = pd.DataFrame({"node":[], "time":[],
                       "px":[],"py":[],"speed":[]})

        # Iterate through this loop so that every node is updated.
        for node in range(self.N):
            # Get random x and y acceleration val (under user limit)
            newAx = 100000
            newAy = 100000
            while (np.sqrt(np.square(newAx)+np.square(newAy)) > self.maxAccel):
                newAx = (-0.5 + np.random.random())
                newAy = (-0.5 + np.random.random())
            refX = self.r[node, 6]
            refY = self.r[node, 7]
            
            # Update accelerations of random values
            self.r[node, 0] = newAx
            self.r[node, 1] = newAy
            
            # Check to make sure we can implement new vel
            newVx = np.sum([newAx, self.r[node, 2]])
            newVy = np.sum([newAy, self.r[node, 3]])
            if (np.sqrt(np.square(newVx)+np.square(newVy))) <= self.maxVel:
                self.r[node, 2] = newVx
                self.r[node, 3] = newVy
            
            # Critical line, add negative velocity to the position to reflect.
            self.r[node, 4] = np.sum([refX*self.r[node, 2], self.r[node, 4]])
            self.r[node, 5] = np.sum([refY*self.r[node, 3], self.r[node, 5]])

            #print("<"+str(self.r[node, 4])+","+str(self.r[node, 5])+","+str(self.r[node, 6])+","+str(self.r[node, 7])+">")
            #print(self.r)
            
            # Information for the datafram, start with time.
            time = 1.0*step
            
            # Get speed from existing r array.
            speed = np.sqrt(np.square(self.r[node, 2])+np.square(self.r[node, 3]))
            
            xHalfLen = self.bounds[1]
            posX = xHalfLen+self.r[node, 4]
            yHalfLen = self.bounds[3]
            posY = yHalfLen+self.r[node, 5]

            dTempNode = pd.DataFrame({"node":[node],
                                  "time":[time],
                                  "px":[posX],
                                  "py":[posY],
                                  "speed":[speed]})
            
            self.dTemp = self.dTemp.append(dTempNode,  ignore_index = True) 
                        
        # update positions
        self.state[:, :2] = self.r[:, 4:6]

        # check for crossing boundary
        crossed_x1 = (self.r[:, 4] < self.bounds[0] + self.size)
        crossed_x2 = (self.r[:, 4] > self.bounds[1] - self.size)
        crossed_y1 = (self.r[:, 5] < self.bounds[2] + self.size)
        crossed_y2 = (self.r[:, 5] > self.bounds[3] - self.size)

        # Flip the variable refX and refY so that the node doesn't leave box.
        self.r[crossed_x1, 6] *= -1
        self.r[crossed_x2, 6] *= -1
        self.r[crossed_y1, 7] *= -1
        self.r[crossed_y2, 7] *= -1
        
    def getdf(self):
        return self.dTemp
    