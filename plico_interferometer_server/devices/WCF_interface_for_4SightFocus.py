import json
import os
import h5py
import datetime
import glob
import numpy as np
import urllib
from plico_interferometer_server.devices.abstract_interferometer import \
    AbstractInterferometer
from plico.utils.logger import Logger
from plico.utils.decorator import override


class WCFInterfacer(AbstractInterferometer):
    """ This class allows interfacing with the 4Sight Focus or 4DInSpec software server.
    """
    LAMBDA_IN_M = 632.8e-9

    def __init__(self,
                 ipaddr, port, burst_folder_name_4D_PC,
                 name='PhaseCam6110'):
        self._name = name
        self.ipaddr = 'localhost'
        self.logger = Logger.of('PhaseCam6110')
        self._ip = ipaddr
        self._port = port
        self._burstFolderName4DPc = burst_folder_name_4D_PC
        #self._ping(self._ip)

        self._dataServiceAddress = 'http://%s:%i/DataService/' % (self._ip, self._port)
        self._systemServiceAddress = 'http://%s:%i/SystemService/' % (self._ip, self._port)
        self._frameBurstServiceAddress = 'http://%s:%i/FrameBurstService/' % (self._ip, self._port)

    def _ping(self, host):
        import platform
        import subprocess
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, '1', host]
        if subprocess.call(command) != 0:
            raise HostNotFoundException('Interferometer PC did not ansewer to ping!')
        

### per classe astratta ###
    @override
    def name(self):
        return self._name

    @override
    def deinitialize(self):
        pass

    @override
    def wavefront(self, how_many=1):
        '''
        Parameters
        ----------
        how_many: int
            numbers of frame to acquire

        Returns
        -------
        masked_ima: numpy masked array
            image or mean of the images required
        '''
        if how_many == 1:
            width, height, pixel_size_in_microns, data_array = \
                self.take_single_measurement()
            masked_ima = self._fromDataArrayToMaskedArray(
                width, height, data_array * self.LAMBDA_IN_M)
        else:
            image_list = []
            for i in range(how_many):
                width, height, pixel_size_in_microns, data_array = \
                    self.take_single_measurement()
                masked_ima = self._fromDataArrayToMaskedArray(
                    width, height, data_array * self.LAMBDA_IN_M)
                image_list.append(masked_ima)
            images = np.ma.dstack(image_list)
            masked_ima = np.ma.mean(images, axis=2)

        return masked_ima

    def _fromDataArrayToMaskedArray(self, width, height, data_array):
        data = np.reshape(data_array, (width, height))
        idx, idy = np.where(np.isnan(data))
        mask = np.zeros((data.shape[0], data.shape[1]))
        mask[idx, idy] = 1
        masked_ima = np.ma.masked_array(data, mask=mask.astype(bool))
        return masked_ima

    @override
    def burst_and_return_average(self, how_many=1):
        mean_ima = self.meanImageFromBurst(how_many, None)
        return mean_ima

    def meanImageFromBurst(self, numberOfFrames, folder_name=None):
        if folder_name is None:
            folder_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.burst_frames_to_specific_directory(os.path.join(self._burstFolderName4DPc,
                                                        folder_name), numberOfFrames)
        self.convert_raw_frames_in_directory_to_measurements_in_destination_directory(
            os.path.join(self._burstFolderName4DPc, folder_name),
            os.path.join(self._burstFolderName4DPc, folder_name))
        
        listtot = glob.glob(os.path.join(self._burstFolderName4DPc, folder_name, '*.4D'))
        listtot.sort()
        image_list = []
        for ima_name in listtot:
            masked_ima = self._readPhaseCameWFCData(ima_name)
            image_list.append(masked_ima)
        images = np.ma.dstack(image_list)
        mean_ima = np.ma.mean(images, 2)
        return mean_ima

    def _readPhaseCameWFCData(self, i4dfilename):
        with h5py.File(i4dfilename, 'r') as ff:
            data = ff.get('/Measurement/SurfaceInWaves/Data')
            meas = data[()]
            mask = np.invert(np.isfinite(meas))

        image = np.ma.masked_array(meas * self.LAMBDA_IN_M, mask=mask)
        return image


###
    def _readJsonData(self, url, data=None):
        """
        Parameters
        ----------
        url: string

        Other Parameters
        ---------------
        data:

        Returns
        -------
        json_data:

        """
        if data:
            dumped_data = json.dumps(data)
            encoded_data = dumped_data.encode('utf-8')
            content_length = len(encoded_data)
            request_headers = {'Content-type': 'application/json',
                            'Accept': 'application/json',
                            'Content-length': content_length}
            req = urllib.request.Request(url, data=encoded_data, headers=request_headers)
        else:
            req = url
        try:
            try:
                response = urllib.request.urlopen(req, timeout=50)
            except urllib.request.URLError as error:
                self._ping(self._ip)
                raise Exception('Error = %s' %str(error))

            response_contents = response.read()
            if response_contents != b'':
                json_data = json.loads(response_contents)
                return json_data
        except urllib.request.HTTPError as e:
            error_message = e.read()
            print(error_message)
            open('/tmp/out.html','w+').write(error_message.decode('utf-8'))
            raise Exception('Response error see /tmp/out.html for details')

    ### DATA PROXY ###
    def get_feature_analysis_results(self):
        '''
        Returns
        -------
        features: 
        fractionalFeatureArea: 
        numberOfFeatures: 
        totalFeatureAreaInSquareMicrons:
        '''
        url = '%s%s' % (self._dataServiceAddress, 'GetFeatureAnalysisResults')
        json_data = self._readJsonData(url)
        features = np.array(json_data['Features'])
        fractionalFeatureArea = json_data['FractionalFeatureArea']
        numberOfFeatures = json_data['NumberOfFeatures']
        totalFeatureAreaInSquareMicrons = json_data['TotalFeatureAreaInSquareMicrons']
        return features, fractionalFeatureArea, numberOfFeatures, totalFeatureAreaInSquareMicrons

    def get_first_nine_zernike_terms(self):
        '''
        Returns
        -------
        zernike_waves_terms:
        '''
        """ Return the first nine zernike of image"""
        url = '%s%s' % (self._dataServiceAddress, 'GetFirstNineZernikeTerms')
        json_data = self._readJsonData(url)
        zernike_waves_terms = np.array(json_data)
        return zernike_waves_terms

    def get_fringe_amplitude_data(self):
        """
        Returns
        -------
        data: numpy array
            vector containing image data
        height: int
            height of the image in pixel
        pixel_size_in_microns: int
        width: int
            width of the image in pixel
        """
        url = '%s%s' % (self._dataServiceAddress, 'GetFringeAmplitudeData')
        json_data = self._readJsonData(url)
        width = json_data['Width']
        height = json_data['Height']
        pixel_size_in_microns = json_data['PixelSizeInMicrons']
        data = np.array(json_data['Data'], dtype=np.float32)
        return data, height, pixel_size_in_microns, width

    def get_intensity_data(self):
        """
        Returns
        -------
        data: numpy array
            vector containing image data
        height: int
            height of the image in pixel
        pixel_size_in_microns: int
        width: int
            width of the image in pixel
        """
        url = '%s%s' % (self._dataServiceAddress, 'GetIntensityData')
        json_data = self._readJsonData(url)
        width = json_data['Width']
        height = json_data['Height']
        pixel_size_in_microns = json_data['PixelSizeInMicrons']
        data = np.array(json_data['Data'], dtype=np.float32)
        return data, height, pixel_size_in_microns, width

    def get_interferogram(self, index):
        '''
        Parameters
        ----------
        index:

        Returns
        -------
        json_data:
        '''
        url = '%s%s' % (self._dataServiceAddress, 'GetInterferogram')
        data = index
        json_data = self._readJsonData(url, data)
        return json_data

    def get_measurement_info(self):
        '''
        Returns
        -------
        averageFringeAmplitude:
        averageIntensity: 
        averageModulation: 
        fringeAmpThresholdPercentage: 
        intensityThresholdPercentage: 
        modulationThresholdPercentage: 
        numberOfSamples: 
        numberOfValidPixels: 
        pathMatchPositionInMM: 
        RMSInNM: 
        userSettingsFilePath: 
        wavelengthInNM: 
        wedge:
        '''
        url = '%s%s' % (self._dataServiceAddress, 'GetMeasurementInfo')
        json_data = self._readJsonData(url)
        averageFringeAmplitude = json_data['AverageFringeAmplitude']
        averageIntensity = json_data['AverageIntensity']
        averageModulation = json_data['AverageModulation']
        fringeAmpThresholdPercentage = json_data['FringeAmpThresholdPercentage']
        intensityThresholdPercentage = json_data['IntensityThresholdPercentage']
        modulationThresholdPercentage = json_data['ModulationThresholdPercentage']
        numberOfSamples = json_data['NumberOfSamples']
        numberOfValidPixels = json_data['NumberOfValidPixels']
        pathMatchPositionInMM = json_data['PathMatchPositionInMM']
        RMSInNM = json_data['RMSInNM']
        userSettingsFilePath = json_data['UserSettingsFilePath']
        wavelengthInNM = json_data['WavelengthInNM']
        wedge = json_data['Wedge']
        return averageFringeAmplitude, averageIntensity, averageModulation, fringeAmpThresholdPercentage, intensityThresholdPercentage, modulationThresholdPercentage, numberOfSamples, numberOfValidPixels, pathMatchPositionInMM, RMSInNM, userSettingsFilePath, wavelengthInNM, wedge

    def data_service_get_modulation_data(self):
        '''
        Returns
        -------
        width: int
            width of the image in pixel
        height: int
            height of the image in pixel
        pixel_size_in_microns: int
        data_array: numpy array
            vector containing image data
        '''
        url = '%s%s' % (self._dataServiceAddress, 'GetModulationData/')
        json_data = self._readJsonData(url)
        width = json_data['Width']
        height = json_data['Height']
        pixel_size_in_microns = json_data['PixelSizeInMicrons']
        data_list = json_data["Data"]
        data_array = np.array(data_list, dtype=np.float32)
        return width, height, pixel_size_in_microns, data_array

    def get_phase_step_calculator_results(self):
        '''
        Returns
        -------
        averagePhaseStepInDegrees: 
        height: 
        phaseStepsInDegrees: 
        width:
        '''
        url = '%s%s' % (self._dataServiceAddress, 'GetPhaseStepCalculatorResults')
        json_data = self._readJsonData(url)
        averagePhaseStepInDegrees = json_data['AveragePhaseStepInDegrees']
        height = json_data['Height']
        phaseStepsInDegrees = np.array(json_data['PhaseStepsInDegrees'])
        width = json_data['Width']
        return averagePhaseStepInDegrees, height, phaseStepsInDegrees, width

    def get_surface_data(self):
        '''
        Returns
        -------
        data: numpy array
            vector containing image data
        height: int
            height of the image in pixel
        pixel_size_in_microns: int
        width: int
            width of the image in pixel
        '''
        url = '%s%s' % (self._dataServiceAddress, 'GetSurfaceData')
        json_data = self._readJsonData(url)
        data = np.array(json_data['Data'], dtype=np.float32)
        height = json_data['Height']
        pixel_size_in_microns = json_data['PixelSizeInMicrons']
        width = json_data['Width']
        return data, height, pixel_size_in_microns, width

    def get_unprocessed_surface_data(self):
        '''
        Returns
        -------
        data: numpy array
            vector containing image data
        height: int
            height of the image in pixel
        pixel_size_in_microns: int
        width: int
            width of the image in pixel
        '''
        url = '%s%s' % (self._dataServiceAddress, 'GetUnprocessedSurfaceData')
        json_data = self._readJsonData(url)
        data = np.array(json_data['Data'], dtype=np.float32)
        height = json_data['Height']
        pixel_size_in_microns = json_data['PixelSizeInMicrons']
        width = json_data['Width']
        return data, height, pixel_size_in_microns, width

    def save_data_to_disk(self, path):
        '''
        Parameters
        ----------
        path: string
            path where to save the measurements
        '''
        url = '%s%s' % (self._dataServiceAddress, 'SaveDataToDisk/')
        data = path
        self._readJsonData(url, data)


    ### SYSTEM PROXY ###
    def take_single_measurement(self):
        '''
        Returns
        -------
        width: int
            width of the image in pixel
        height: int
            height of the image in pixel
        pixel_size_in_microns: int
        data_array: numpy array
            vector containing image data
        '''
        url = '%s%s' % (self._systemServiceAddress, 'TakeSingleMeasurement/')
        json_data = self._readJsonData(url)
        width = json_data['Width']
        height = json_data['Height']
        pixel_size_in_microns = json_data['PixelSizeInMicrons']
        data_list = json_data['Data']
        data_array = np.array(data_list, dtype=np.float32)
        return width, height, pixel_size_in_microns, data_array

    def set_detector_mask(self, mask):
        """
        Parameters
        ----------
        mask: numpy array
            numpy 2d array with np.nan in the obscured area
        """
        url = '%s%s' % (self._systemServiceAddress, 'SetDetectorMask')
        height_str = '%i' % mask.shape[0]
        width_str = '%i' % mask.shape[1]
        data = {'Height': height_str,
                'Width': width_str,
                'MaskArray': mask.flatten().tolist()}
        self._readJsonData(url, data)
        print('reload')
        return

    def get_system_info(self):
        '''
        Returns
        -------
        serialNumber:
        '''
        url = '%s%s' % (self._systemServiceAddress, 'GetSystemInfo')
        json_data = self._readJsonData(url)
        serialNumber = json_data['SystemSerialNumber']
        return serialNumber

    def convert_raw_frames_in_directory_to_measurements_in_destination_directory(self, measurementsDirectory,
                                                                        rawFramesDirectory):
        '''
        Parameters
        ----------
        measurementsDirectory: string
            path where to save the measurements converted
        rawFramesDirectory: string
            path where raw frames are located
        '''
        url = '%s%s' % (self._systemServiceAddress, 'ConvertRawFramesInDirectoryToMeasurementsInDestinationDirectory')
        data = {'MeasurementsDirectory' : measurementsDirectory,
                'RawFramesDirectory' : rawFramesDirectory
               }
        self._readJsonData(url, data)

    def set_trigger_mode(self, trigger):
        '''
        Parameters
        ----------
        trigger:
        '''
        url = '%s%s' % (self._systemServiceAddress, 'SetTriggerMode')
        data = {'CameraIsExternallyTriggered' : trigger}
        self._readJsonData(url, data)

    def take_averaged_measurement(self, numberOfSamples):
        '''
        Parameters
        ----------
        numberOfSamples: int
             numbers of measurements to average
        '''
        url = '%s%s' % (self._systemServiceAddress, 'TakeAveragedMeasurement')
        data = numberOfSamples
        self._readJsonData(url, data)

    def load_configuration(self, configurationPath):
        '''
        Parameters
        ---------
        configurationPath: string
            file path for configuration to load
        '''
        url = '%s%s' % (self._systemServiceAddress, 'LoadConfiguration')
        self._readJsonData(url, configurationPath)


    ### FRAME BURST PROXY ###
    def burst_frames_to_specific_directory(self, directory, numberOfFrames):
        '''
        Parameters
        ----------
        directory: string
            directory where to save files
        numberOfFrames: int
            number of frames to acquire
        '''
        url = '%s%s' % (self._frameBurstServiceAddress, 'BurstFramesToSpecificDirectory')
        data = {'BurstDirectory' : directory,
                'NumberOfFrames' : numberOfFrames}
        self._readJsonData(url, data)

    def burst_frames_to_disk(self, numberOfFrames):
        '''
        Parameters
        ----------
        numberOfFrames: int
            number of frames to acquire

        '''
        url = '%s%s' % (self._frameBurstServiceAddress, 'BurstFramesToDisk')
        data = numberOfFrames
        self._readJsonData(url, data)

class HostNotFoundException(Exception):
    pass