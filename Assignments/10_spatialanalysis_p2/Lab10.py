#!/usr/bin/env python3

import numpy as np

def semivariogram(x, y, z, s=1):
    '''Calaculate the semivariance as:

    ..math: \gamma_i (h) = \frac{1}{2} \left( z_{x_i} -  z_{x_i+h} \right)^2

    Parameters:
    ----------
        x : array_like
            x-coordinate vector
        y : array_like
            y-coordinate array
        z : array_like
            z-vector at point(x,y) to calculate the semivariance of
        s : int or float
            scale factor in computing the lag distance between bins
    Reutrns:
    -------
        mean_lag : array_like
            lag distance bins
        vario :
            semivariance within the corresponding bin
        varz :
            variance of the the full dataset z
    '''

    # Grid the input data in it's observed grid
    X1, X2 = np.meshgrid(x,x)
    Y1, Y2 = np.meshgrid(y,y)
    Z1, Z2 = np.meshgrid(z,z)

    # Compute distance matrix and replace zeros along the diagonal with NaNs
    D  = np.sqrt((X1-X2)**2 + (Y1-Y2)**2)
    D += D*np.diag((x*np.nan))

    # Compute the semivariance between points
    G = (1/2)*(Z1 - Z2)**2

    lag      = s*0.5*np.mean(np.nanmin(D, axis=0)) # compute lag distance
    hmd      = np.nanmax(D)/2                      # Find max distance between points/2
    num_lags = np.floor(hmd/lag)                   # compute number of lags

    # Bin the data with the calculate lag length
    all_lags = np.ceil(D/lag)

    # Initalize empty vectors to be populated in for loop below
    mean_lag  = np.zeros(int(num_lags))            # Lag vector
    num_pairs = np.zeros(int(num_lags))            # Pair counts
    vario     = np.zeros(int(num_lags))            # Variance at lag

    # iterate over the lags
    for i in range(int(num_lags)):
        selection    = all_lags == (i+1)                 # select points in bin (1 = true)
        mean_lag[i]  = np.mean(D[selection])             # compute mean lag distance
        num_pairs[i] = np.sum(selection.astype(int))/ 2  # count pairs
        vario[i]     = np.mean(G[selection])             # populate variogram

    # Compute variance of original data
    varz = np.var(z)

    return mean_lag, vario, varz

def ordinary_krig(x, y, z, model = 'linear', nugget=0.0, sill=None, slope=0.9, range=50):
    '''Function to compute Ordinary Kirging

    Parameters:
    ----------
        x : array_like
            x-coordinate vector
        y : array_like
            y-coordinate array
        z : array_like
            z-vector at point(x,y) to be kriged
        model : string
                Type of model used to compute the semivariance matrix (W)
        nugget : float, optional
                 Offset to force semivariogram through origin
        sill : float
               default value np.var(z, ddof=1)
        range : int, optional (required for "exponential" and "spherical" models)
                Lag (distance) at which semivariance=> variance, measure of correlation distance

    Reutrns:
    -------
        Z : array_like (2D)
            predicted value on a regularly spaced grid
        S2 : array_like (2D)
            Kriging variance on our regularly spaced grid
        X : array_like (2D)
            X grid of kriged points
        Y : array_like (2D)
            Y grid of kriged points
    '''
    models = ['linear', 'exponential', 'spherical']

    if model not in models:
        raise ValueError('Invalid model specified. Model must be "{}", "{}" or "{}"'.format(*models))


    X1, X2 = np.meshgrid(x,x)
    Y1, Y2 = np.meshgrid(y,y)
    Z1, Z2 = np.meshgrid(z,z)

    # Calculate the distance between points
    D = np.sqrt((X1-X2)**2 + (Y1-Y2)**2)

    if sill == None:
        # Compute variance of original data
        sill = np.var(z)

    # Populate semivariance matrix W
    if model == 'linear':
        W = nugget + slope*D
    else:
        raise NotImplementedError('Model not supported yet. Add functionality yourself!!')

    # Add extra row and column to W for Lagrange multiplier
    m, n     = W.shape
    W        = np.append(W,np.ones((1,m)),  axis=0)  # Add final column of ones
    W        = np.append(W,np.ones((n+1,1)),axis=1)  # Add final row of ones
    W[-1,-1] = 0

    # Invert W for later, this is ill-conditioned but oh-well
    # this can be very computationally expensive so only want to do it once
    Winv = np.linalg.inv(W)

    #  Construct regular grid over which interpolated values are required
    xgrid = np.linspace(x.min(),x.max(),len(x))
    ygrid = np.linspace(y.min(),y.max(),len(y))
    X, Y  = np.meshgrid(xgrid,ygrid)

    # Convert arrays to single vectors:
    Xvec = X.flatten()
    Yvec = Y.flatten()

    # Initalize vairable solved for
    Zvec  = 99999.*np.ones((Xvec.shape[0],1))
    S2vec = 99999.*np.ones((Xvec.shape[0],1))

    # Compute the Kriged estimate at each point
    for i in np.arange(Xvec.shape[0]):
        # calculate distances between point of interest and all observations:
        D0 = np.sqrt( (x - Xvec[i])**2 + (y - Yvec[i])**2 )

        # calculate B (RHS) based on distances above and variogram model
        if model == 'linear':
            B = nugget + slope*D0

        # Add final element for Lagrange multiplier
        B = np.append(B,1)

        # Compute kriging weights and lagrange multiplier with matrix multiplication
        Lambda   = np.dot(Winv,B)

        # Compute kriging estimate at point of interest as weighted sum of obs
        Zvec[i]  = np.dot(z.T,Lambda[:n])

        # Compute kriging variance at point of interest
        S2vec[i] = np.dot(B.T,Lambda)

    # Reshape from flattened vectors to MxM matrix
    M  = xgrid.shape[0]
    Z  = Zvec.reshape(M,M)
    S2 = S2vec.reshape(M,M)

    return Z, S2, xgrid, ygrid
