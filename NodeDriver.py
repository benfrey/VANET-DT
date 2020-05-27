# -*- coding: utf-8 -*-
"""
The purpose of this file is to set N nodes in a user defined square simulation
space. These nodes will then move around for a user defined time value within
the simulation space. The movement of the nodes will be random, and will 
change every timestep (also user defined). The node's new direction will be
semi-arbitrary, governed by finding a random accel, summing these to find a 
random velocity, then summing these velocities to find a position.

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
import matplotlib.pyplot as plt
# Critical line that changes path of access to ffmpeg!
plt.rcParams['animation.ffmpeg_path'] = '/usr/local/bin/ffmpeg'
import matplotlib.animation as animation
import Nodes as nd
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300
import pandas as pd
import TCLWriter

def main():
    # Global vars used across simulation
    global box, rect, ax, undividuals, init_state, df, dt, timeSpace, frames
    
    #------------------------------------------------------------
    # USER DEFINED VALUES FOR SIMULATION. (CHANGE AS YOU LIKE)
    
    N = 20 # N amount of nodes for simulation space. 
           # Can have min amount of 20 to work with Ns-3 networking software.
    length = 1500.0 # Length (float) of square simulation space (meters).
    size = 2.0 # Size of the vehicle (m)
    fps = 10 # Frames per second of the video
    frames = 20 * fps # Length of the video (seconds * fps)
    maxVel = 30 # Max velocity a node can travel m/s
    maxAccel = 3 # Max acceleration a node can undergo m/s^2
    np.random.seed(0); # Consistent randomness (paradox? lol)
    cmap = mpl.cm.get_cmap('brg') # colormap used for scatter plot
    
    #------------------------------------------------------------
    # INTERNAL VARIABLE DECLARATIONS. (DO NOT CHANGE)
    
    # Main setup of the node matrix, fit with all of our attributes
    print("Running...")
    # Set up Nx8 matrix of values [node, ax, ay, vx, vy, px, py, refX, refY]
    init_state = np.zeros((N, 8))
    # Set random position somewhere in box for first timestep
    init_state[:, :4] = 0
    init_state[:, 4:6] = (-0.50 + np.random.random((N, 2)))*length
    init_state[:, 6:] = 1
    
    # Dimension of simulation space
    bounds = [-length/2, length/2, -length/2, length/2]
    
    # Timestep width, we need to adjust maxVel and maxAccel to reflect this
    dt = 1. / fps
    maxVel = maxVel * dt 
    maxAccel = maxAccel * dt

    # Create dataframe to hold information we will throw into XML
    df = pd.DataFrame({"node":[],
                       "time":[],
                       "px":[],
                       "py":[],
                       "speed":[]})

    # Create time space
    timeSpace = np.linspace(0, frames/fps, frames)
    
    # definition of the class
    box = nd.Nodes(init_state, bounds, size=size/100, 
                      fps = fps, frames = frames, N = N, maxVel = maxVel, maxAccel = maxAccel)

    #------------------------------------------------------------
    # SETUP FIGURE FOR ANIMATION. (DO NOT CHANGE)
    
    # Set up figure for scatter plot
    fig = plt.figure(figsize=(4,4))
    grid = plt.GridSpec(4, 4, hspace=0.05, wspace=0.05, 
                        top=0.90, bottom = 0.1,
                        right = 0.98, left = 0.1)
    ax = fig.add_subplot(grid[:, :], aspect='equal', autoscale_on=False,
                        xlim=(-length/2-0.2, length/2+0.2), ylim=(-length/2-0.4, length/2+0.4))
    plt.title(f'Simulated Nodes = {N}')
    #ax.set_axis_off()
    
    # Invert the y axis so 0,0 is at upper left corner.
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
    
    # Undividuals holds the locations for each timestep (change in pos)
    undividuals = ax.scatter([], [], s = size*3, 
                           cmap = cmap, vmin = 0.0, vmax = 1.0)
    
    # Rect is artist element for the box edge outline (we turned axis off)
    rect = plt.Rectangle(box.bounds[::2],
                         box.bounds[1] - box.bounds[0],
                         box.bounds[3] - box.bounds[2],
                         ec='none', lw=2, fc='none')
    ax.add_patch(rect)
    
    # Creating the simulation from this animation function 
    ani = animation.FuncAnimation(fig, animate, frames=frames,
                              interval=10, blit=True)#, init_func=init)
    
    # Save the animation as an mp4. This requires ffmpeg or mencoder to be
    # installed. The extra_args ensure that the x264 codec is used, so that
    # the video can be embedded in html5.You may need to adjust this for
    # your system: for more information, see
    # http://matplotlib.sourceforge.net/api/animation_api.html
    FFwriter = animation.FFMpegWriter(fps=fps, extra_args=['-vcodec', 'libx264'])
    ani.save(f'Nodes_{N}.mp4', writer = FFwriter)

    # Show the plot, not really necesary because we only care about animation.
    plt.show()
        
    # Create a TCL file using the TCLWriter class.
    TCLWriter.writeToTCL(df, N, mps = 10, fps = fps)
    
    # Inform user of output files
    print("Simulation success! You can expect two output files saved to your working directory:")
    print("1.) Animation video titled '"+f'Nodes_{N}.mp4'+"'")
    print("2.) Trace file for use with Ns-3 software titled 'mobility.tcl'")

def init():
    """
    Initialize animation by setting initial node positions and artist drawings.
    """
    # set the initial positions of the nodes
    undividuals.set_offsets(init_state[:, 4:6])
    rect.set_edgecolor('none')
    tm = ax.text(200, -500, 'Time = 0.0s')

    
    # Return these artist objects to be redrawn in mp4
    return undividuals, rect, tm

def animate(i):
    """
    Performs specific animation at step 'i'. This method is responsible
    for the continued update of the 'time' indicator, redraw of each node
    for the mp4 output video, and update of Pandas dataframe to include
    updated node positions.
    
    Parameters
    ----------
    i : int
        Step of simulation 
    
    Returns
    ----------
    None
    """ 
    # Access global scope 
    global df
    
    # Perform simulation step on box
    box.step(dt)
    
    # Output progress to user
    if ((100*float(i+1)/frames)%10 == 0):
        if (i+1 == frames):
            print(str(100*float(i+1)/frames)+"%", end ="\n")
        else:
            print(str(100*float(i+1)/frames)+"%", end =" ")
        

    # Update time label for simulation.
    for txt in ax.texts:
        txt.set_visible(False)
    tm = ax.text(200, -500, 'Time = %.1fs' % timeSpace[i])
    
    # Add all of the data from each timestep to a dataframe.
    dTemp = box.getdf()
    df = df.append(dTemp, ignore_index = True) 

    # Update nodes of the animation
    rect.set_edgecolor('k')
    undividuals.set_offsets(box.state[:, :2])
    
    # Return these artist objects to be redrawn in mp4
    return undividuals, rect, tm

if __name__=="__main__":
    main()