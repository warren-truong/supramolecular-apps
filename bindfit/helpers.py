"""
" Miscellaneous helper functions, mostly for data munging
"""

from __future__ import division
from __future__ import print_function

import numpy as np
import numpy.matlib as ml

def cov(data, residuals, total=False):
    cov = np.var(residuals, axis=1)/np.var(data, axis=1)

    if total:
        return sum(cov)/len(cov)
    else:
        return cov

def rms(residuals, total=False):
    """
    Calculate RMS errors from residuals

    Arguments:
        residuals: array  3D array of residuals corresponding to each input
                          dataset

    Returns:
        array  2D array of RMS values for each fit
    """

    r = np.array(residuals)
    rms = np.sqrt(np.sum(np.square(r), axis=1))

    if total:
        return sum(rms)/len(rms) 
    else:
        return rms 

def normalise(data):
    """ 
    Normalise a 2D array of observations.

    Arguments:
        data: ndarray  n x m array of n dependent variables, m observations

    Returns:
        ndarray  n x m array of normalised input data
    """

    # Create matrix of initial values to subtract from original matrix
    initialmat = ml.repmat(data.T[0,:], len(data.T), 1).T
    data_norm = data - initialmat
    return data_norm

def denormalise(data, data_norm):
    """
    Denormalise a normalised dataset given original non-normalised input data

    Arguments:
        data:      ndarray  original n x m array
        data_norm: ndarray  normalised n x m array
    
    Returns:
        ndarray  n x m array of denormalised input data_norm
    """
    # Create matrix of initial data values to add to fit 
    initialmat = ml.repmat(data[:,0][np.newaxis].T, 1, data.shape[1])
    # De-normalize normalised data (add initial values back)
    data_denorm = data_norm + initialmat
    return data_denorm 

def dilute(xdata, ydata):
    """
    Apply dilution factor to a dataset

    Arguments:
        xdata: ndarray  x x m array of m observations of independent variables
        ydata: ndarray  y x m array of non-normalised observations of dependent
                      variables

    Returns:
        ndarray  y x m array of input data with dilution factor applied
    """

    h0 = xdata[0]
    # PLACEHOLDER this only calculates dilution for the first dataset
    y = ydata

    dilfac = h0/h0[0]
    dilmat = ml.repmat(dilfac, y.shape[0], 1)
    y_dil = (y*dilmat)[np.newaxis]
    return y_dil