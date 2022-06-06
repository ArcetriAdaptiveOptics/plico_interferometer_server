
# import all 4D libraries
from Scripting.App import *
from Scripting.Modify import *
from Scripting.Data import *
from Scripting.Config import *
from Scripting.Measurements import *
from Scripting.Show import *

import time

import Pyro.util

from Commons import Constants
import FastAcqLoad
import FastAcqMeasure
import FastAcqProcess

from I4D import comm4d

# @Class: Controller
# Wrapper around the 4D python library to control the interferometer
#
# NOTE: it works in the local interferometer host
# @
class Controller:
    
    def __init__(self):
        self.logSource = "CONTROLLER I4D"
        self.userLog = Pyro.util.UserLogger()
        
        # Initialize the interferometer with a default config file
        self.loadConfig(Constants.I4D_DEFAULT_CONFIG_FILE)
        
    def ping(self):
         self.log("Pinged from remote client")


    def loadConfig(self, configFile):
        self.log("Loading config file %s..." % configFile)
        ret = OpenConfigFile(Constants.I4D_CONFIG_FILE_DIR + '/' + configFile)
        if ret:
            self.log("Config file loaded!")
        else:
            self.log("Config file loading failed")
        return ret


    def setTrigger(self, enabled):
        self.log("Setting trigger to %d" % enabled)
        FastAcqMeasure.setTrigger(enabled)
        if enabled:
            self.log("Trigger enabled")
        else:
            self.log("Trigger disabled")
            
            
    def setPostProcessing(self, ppType):
        self.log("Setting Post-processing to %s" % ppType)
        Constants.I4D_POSTPROCESS = ppType
        self.log("Post-processing set to %s" %  Constants.I4D_POSTPROCESS)
        

    # Log using the Pyro logger
    # The log file is define in Pyro config file (Pyro_Server.conf)
    def log(self, message):
        self.userLog.msg(self.logSource, message)

    #def log(self, message):
    #    print "%s: %s" %(self.logSource, message)    


    # Takes a single measurement directly to DISK, and store it to a predefined 
    # folder (Constants.I4D_SINGLE_MEAS_FOLDER)
    # Return destination filename
    #
    # i.e. returns "SINGLE_MEAS/measPrefix_0000.dat"
    def GetMeasurementToDisk(self, measPrefix):
        try:
            destPath = Constants.I4D_SINGLE_MEAS_FOLDER
            destFilePrefix = measPrefix
            
            self.log("")
            self.log("Acquiring single measurement to disk... (dest: %s, prefix: %s)" %(destPath, destFilePrefix))
            (frameInfo, camInfo) = FastAcqMeasure.acquire(1, destPath, destFilePrefix)
            self.log("Single measurements succesfully acquired!")
            if len(frameInfo) != 1:
                raise Exception, 'missing frame'
            
            # Process data (optional)
            if Constants.I4D_POSTPROCESS != "NONE":
                destFileName = self.PostProcess(destPath, destFilePrefix, 1)
            elif Constants.I4D_CALIBRATE_RAW_FRAMES:
                destFileName = "%s/calibrated/%s_0000.dat" % (destPath, measPrefix)
            else:
                destFileName = "%s/raw/%s_0000.dat" % (destPath, measPrefix)
                
            self.log("Single measurements succesfully saved to %s" % destFileName)
            return destFileName
        except Exception, e:
            self.log("Single measurement failed: %s" % str(e))
            raise
        
    # Takes a single measurement to RAM and store it to a predefined folder 
    # (Constants.I4D_SINGLE_MEAS_FOLDER)
    # Return destination filename
    #
    # i.e. returns "SINGLE_MEAS/measPrefix_0000.dat"
    def GetMeasurementToRam(self, measPrefix):
        try:
            destPath = Constants.I4D_SINGLE_MEAS_FOLDER
            destFilePrefix = measPrefix
            
            self.log("")
            self.log("Acquiring single measurement to ram... (dest: %s, prefix: %s)" %(destPath, destFilePrefix))
            meas = Measure()
                
            if meas == None:
                raise Exception, 'missing frame'
                
            self.log("Single measurements succesfully acquired to RAM!")
            
            # Process data (optional)
            if Constants.I4D_POSTPROCESS == "HDF5":
                data = meas.GetDataset("analyzed", "dataset")
                destFileName = "%s/%s/%s_0000.h5" % (destPath, Constants.I4D_HDF5_DATA_PATH, measPrefix)
                SaveMeasurement(data, Constants.I4D_DATA_PATH + "/" + destFileName)
            elif Constants.I4D_CALIBRATE_RAW_FRAMES:
                destFileName = "%s/%s/%s_0000.dat" % (destPath, Constants.I4D_CALIB_DATA_PATH, measPrefix)
                SaveMeasurement(meas, Constants.I4D_DATA_PATH + "/" + destFileName)
            else:
                destFileName = "%s/%s/%s_0000.dat" % (destPath, Constants.I4D_RAW_DATA_PATH, measPrefix)
                SaveMeasurement(meas, Constants.I4D_DATA_PATH + "/" + destFileName)
            self.log("Single measurements succesfully saved to %s" % destFileName)
            return destFileName
        except Exception, e:
            self.log("Single measurement failed: %s" % str(e))
            raise
        

    # Takes a number of measures (burst measure) and store them to server's disk
    # Return some info about destination path, camera and measures
    #
    # i.e. returns "BURST_20080416_123456", and the contained files are 'MEAS_nnnn.dat'
    def GetBurstToDisk(self, nMeas, destPath = None):
        try:
            # If folder not provided, use date and time to have unique 
            # folder name
            if destPath == None:
                dateAndTime = time.localtime()
                dateAndTimeStr = "%4d%02d%02d_%02d%02d%02d" % (dateAndTime[0], dateAndTime[1], dateAndTime[2], dateAndTime[3], dateAndTime[4], dateAndTime[5]) 
                destPath = Constants.I4D_FOLD_PREFIX + "_" + dateAndTimeStr
            # Use default meas prefix
            destFilePrefix = Constants.I4D_MEAS_PREFIX
            
            self.log("")
            self.log("Acquiring %d burst measurements to disk..." % nMeas)
            (frameInfo, camInfo) = FastAcqMeasure.acquire(nMeas, destPath, destFilePrefix)
            if len(frameInfo) != nMeas:
                raise Exception, 'missing frames (acquired %d/%d)' % (len(frameInfo), nMeas)
       
            # Process data (optional)
            if Constants.I4D_POSTPROCESS != "NONE":
                destPath = self.PostProcess(destPath, destFilePrefix, nMeas)
            elif Constants.I4D_CALIBRATE_RAW_FRAMES:
                destPath = destPath + '/calibrated'
            else:
                destPath = destPath + '/raw'
            
            self.log("Burst measurements succesfully acquired to %s" % destPath)
            #return (destPath, frameInfo, camInfo)
            return (destPath, None, None)
        except Exception, e:
            self.log("Burst measurements failed: %s" % str(e))
            raise
        
    # Process raw (or calibrated) data 
    # Returns the destination path (for a burst) or filename (for a 
    # single meas) or propagate the exception generated by FastAcqProcess.datToH5
    def PostProcess(self, sourceDir, sourceFilePrefix, nMeas):
        self.log("Post-processing type: %s" %  Constants.I4D_POSTPROCESS)
        # HDF5 processing
        if Constants.I4D_POSTPROCESS == "HDF5":
            self.log('Generating hdf5 files for %d measurements...' %nMeas)
            try:
                FastAcqProcess.datToH5(sourceDir, sourceFilePrefix, nMeas)
            except Exception, e:
                self.log("HDF5 generation failed (%s)" % str(e))
                raise Exception, "HDF5 generation failed"
            if nMeas == 1:
                destFileName = sourceDir + '/' + Constants.I4D_HDF5_DATA_PATH + '/' + sourceFilePrefix + '_0000.h5'
                return destFileName
            else:
                sourceDir = sourceDir + '/' + Constants.I4D_HDF5_DATA_PATH
                return sourceDir
        # No other processing defined
        else:
            return '' 
    

    # Test an acquisition to disk and show the plot
    def testAcquire(self):
        self.log("I4D Server acquiring measurement...")
        self.GetMeasurementToDisk("TEST_MEAS")
        
        # Define source directory
        sourceAbsoluteDir = Constants.I4D_DATA_PATH + '/SINGLE_MEAS/' 
        if Constants.I4D_CALIBRATE_RAW_FRAMES: 
            sourceAbsoluteDir += Constants.I4D_CALIB_DATA_PATH
        else:
            sourceAbsoluteDir += Constants.I4D_RAW_DATA_PATH
        
        # Check source directory
        if not os.path.exists(sourceAbsoluteDir):
           raise Exception, "Source directory doesn't exist"
        
        # Define destination directory  
        destAbsoluteDir = Constants.I4D_DATA_PATH + '/SINGLE_MEAS/hdf5'
        
        if not os.path.exists(destAbsoluteDir):
            os.mkdir(destAbsoluteDir)
            
        meas = FastAcqLoad.MeasurementFromDisk(sourceAbsoluteDir + '/TEST_MEAS_0000.dat')
        if meas:
            dataset = meas.GetDataset('analyzed', 'dataset')
            Show(dataset)

    # Capture
    def capture(self, n, name=None, ext=None):
        self.log("I4D Server capturing...")
        try:
            comm4d.capture(n, name, ext);
        except Exception, e:
            self.log("Single measurement failed: %s" % str(e))
            raise


    # Produce
    def produce(self, name):
       self.log("I4D Server producing...")
       try:
           comm4d.produce(name);
       except Exception, e:
           self.log("Failed data reduction" % str(e))
           raise