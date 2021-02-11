#!/usr/bin/env python3

"""
Load Glacier One (GL1) DEM and abalation information

Orginially in Matlab. Translated by andrewdnolan in Jan 2021
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

plt.rcParams['text.usetex'] = True

def load_ablation_data(fp):
    '''Read in raw ablation data and format nicely'''

    # load the DEM where will get N, E, Elev. info from.
    DEM = np.loadtxt('raw_data/GL1_dem30_zmc.asc')

    # Load the actual ablation data
    raw_data  = np.loadtxt(fp, delimiter=',')
    index     = raw_data[:,0].astype(int)
    start_day = raw_data[:,1]
    end_day   = raw_data[:,2]
    ablation  = raw_data[:,3]

    # Get the info from the DEM
    Northing  = DEM[index,1]
    Easting   = DEM[index,0]
    Elevation = DEM[index,2]

    # Calculate ablation rates (cm/day) for the stake array
    ablation_rate = 100 * ablation / (end_day-start_day)

    # Make a matrix of the read in data
    data_matrix = np.vstack((Northing, Easting, Elevation, ablation_rate)).T
    # These are the column names of our dataframe
    col_names   = ['Northing', 'Easting', 'Elevation', 'ablation_rate']
    # Lets make the actual dataframe
    df = pd.DataFrame(data_matrix, columns=col_names)

    return df

def make_visual(DEM, extent, GL1_outline, ABL_data_2009, ABL_data_2012):
    '''Plotting function to visulaize all the data'''

    fig = plt.figure(figsize=(9,5))
    gs1 = fig.add_gridspec(nrows=1, ncols=2, wspace=0.05, left=0.075, right=0.40, width_ratios=[1,0.1])
    ax0 = fig.add_subplot(gs1[0,0])
    ax1 = fig.add_subplot(gs1[0,1])
    gs2 = fig.add_gridspec(nrows=1, ncols=1, wspace=0.05, left=0.475, right=0.95)
    ax2 = fig.add_subplot(gs2[0,0])

    # Subplot 0: Plot the DEM
    cont = ax0.contourf(DEM, levels=20, cmap='plasma', extent=extent)
    # Plot the DEM contours
    ax0.contour(DEM, colors='k', extent=[lower, right, bottom, top], levels=20)
    # Plot the glacier outline
    ax0.plot(GL1_outline[:,0], GL1_outline[:,1], color='#e41a1c',label='Glacier 1 Outline')
    #plot ablation stake locations
    ax0.scatter(ABL_data_2009['Easting'],ABL_data_2009['Northing'], label='2009 Stakes' ,color='#377eb8', zorder=5,)
    ax0.scatter(ABL_data_2012['Easting'],ABL_data_2012['Northing'], label='2012 Stakes', color='#4daf4a', zorder=5, marker='x')
    # Make the plot nice, with all the bells and whistles
    ax0.set_ylabel('UTM Northing (m)')
    ax0.set_xlabel('UTM Easting (m)')
    ax0.ticklabel_format(axis='both',style='sci',scilimits=(1,4))
    # Add a legend to subolot 0
    ax0.legend()

    # Add a colorbar for DEM plot (this is ax1)
    cbar= plt.colorbar(cont, cax=ax1,shrink=0.75,ax=ax0,pad=-10,orientation='vertical')
    cbar.set_label('Surface Elevation (m.a.s.l.)', labelpad=15,rotation=270)

    # Subplot 1: Scatterplots of the abalation rates
    ax2.scatter(ABL_data_2009['Elevation'],ABL_data_2009['ablation_rate'],label='2009', color='#377eb8')
    ax2.scatter(ABL_data_2012['Elevation'],ABL_data_2012['ablation_rate'],label='2012', color='#4daf4a', marker='x')
    # Make the plot nice, with all the bells and whistles
    ax2.set_ylabel('Ablation rate (cm w.e.q. d$^{-1}$)',rotation=270,labelpad=15)
    ax2.set_xlabel('Elevation (m.a.s.l.)')
    # Have Subplot 1's y-axis on the right to clutter with the colorbar
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    # Add a legend to subolot 1
    ax2.legend()

if __name__ == "__main__":
    #############################################################
    # Load all the raw data, clean, and reshape
    #############################################################

    # Relative filepaths (fp) to the ablation data
    GL1_ABL_2009_fp = 'raw_data/GL1_stake_ablation_2009_Firn550.asc'
    GL1_ABL_2012_fp = 'raw_data/GL1_stake_ablation_2012_Firn550.asc'
    # Load the 2009 Ablation data
    ABL_data_2009 = load_ablation_data(GL1_ABL_2009_fp)
    # Load the 2012 Ablation data
    ABL_data_2012 = load_ablation_data(GL1_ABL_2012_fp)
    # load the DEM file
    surface_DEM = np.loadtxt('raw_data/GL1_surface_DEM_Final_30.asc')
    # load the coordinates of the glacier outline
    GL1_outline = np.loadtxt('raw_data/GL1_outline.asc')

    # Grid Cell Spacing (dx) in meters
    dx = 30
    # Get the extent of the DEM
    lower, right = (surface_DEM[:,1].min(), surface_DEM[:,1].max())
    bottom, top  = (surface_DEM[:,0].min(), surface_DEM[:,0].max())
    # Get the number of rows (m) and columns (n) in the DEM
    m, n = (int(((right+dx) - lower) / dx), int(((top+dx) - bottom) / dx))
    # Reshape the DEM for a single collpase column to an (m x n) matrix
    DEM = surface_DEM[:,2].reshape((m,n)).T

    #############################################################
    # Make a plot visualizing the Data
    #############################################################
    make_visual(DEM, [lower, right, bottom, top], GL1_outline,ABL_data_2009,ABL_data_2012)

    #plt.show()

    #############################################################
    # Write the cleaned ablation data to easily readable csv file
    #############################################################
    ABL_data_2009.to_csv('GL1_stake_ablation_2009.csv')
    ABL_data_2012.to_csv('GL1_stake_ablation_2012.csv')
