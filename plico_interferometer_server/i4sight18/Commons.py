# @File: Commons.py
# Set of commons info needed by Pyro Server and Client.
# @

import os.path

class Constants:
    
    # Pyro controller object name: used by both server and client
    I4D_CONTROLLER_NAME = "I4D_Controller"
    
    
    # Timeout used for TCP connection between Client and Server, used by
    # InterferometerCtrl (actually by Python/Pyro library) and 4Sight 
    # Python/Pyro Server.
    #
    # This is the upper bound for every communication, so don't set it too low!!!
    # NOTE: it doesn't seems to work in case of communication problems, i.e
    #        Server is down.
    #
    # TODO Evaluate better timeout problem
    I4D_CONNECTION_CLIENT_TIMEOUT_S = 60
    I4D_CONNECTION_SERVER_TIMEOUT_S = 30
    
    
    ######################## Server ########################
    # Parameters about the remote interferometer server
    # All these parameter can/should be loaded from a config file
    
    # Configuration file
    I4D_CONFIG_FILE_DIR = 'C:/4D/config'
    I4D_DEFAULT_CONFIG_FILE = 'default.ini'
    
    
    # Absolute data path for data
    # Data are stored in:
    #    - I4D_SINGLE_MEAS_FOLDER: all the single measurements
    #    - I4D_FOLD_PREFIX_yyyymmdd_hhmmss: burst with auto-folder naming
    #    - User defined burst folder
    I4D_DATA_PATH = "D:/4D/Data"
    
    # Sub-folders
    I4D_RAW_DATA_PATH = 'raw'
    I4D_CALIB_DATA_PATH = 'calibrated'
    I4D_HDF5_DATA_PATH = 'hdf5'
    I4D_FITS_DATA_PATH = 'fits'
    
    # Single measurement destination folder
    I4D_SINGLE_MEAS_FOLDER = "SINGLE_MEAS"
    
    # Prefix for the 'automatic' burst folder: the full folder name 
    # will be I4D_FOLD_PREFIX_yyyymmdd_hhmmss.
    # The 'automatic' prefix is only used when a burst destination
    # is not specified
    I4D_FOLD_PREFIX = "BURST"
    
    # Prefix for a measurement file: the full file name will be
    # I4D_MEAS_PREFIX_nnnn.dat
    I4D_MEAS_PREFIX = "MEAS"
    
    ### Calibration ###
    # Force or not calibration after straeming to disk
    I4D_CALIBRATE_RAW_FRAMES = 1
    # Remove raw frames after calibrating them
    I4D_REMOVE_RAW_FRAMES = 0
    
    ### Post processing ###
    # Default value for hdf5 files creation
    I4D_POSTPROCESS = "HDF5"  # Available values: NONE, HDF5

    I4D_DISK    = 'D:/4D/Data/'
    I4D_ERROR   = '4derror'
    I4D_IMGDIR  = 'Z:/4D'
    I4D_DATADIR = I4D_DISK+'Zcopy'
    I4D_LOGDIR  = I4D_DISK+'4Dlog'
    I4D_LOGFILE = '4Dlog.out'
    I4D_FLAT    = 'flat'
    I4D_IMAGENAMES    ='img'
    I4D_EXCHANGE_FILE ='track.txt'
    I4D_SIMULATOR = 0
    I4D_SAMPLING = 2
