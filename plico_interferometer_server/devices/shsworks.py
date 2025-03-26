from plico.utils.logger import Logger
from plico.utils.decorator import override
from plico_interferometer_server.devices.abstract_interferometer import \
    AbstractInterferometer
from shsworks_tcpip.client import ShsClient
import numpy as np
from pathlib import Path
import os


class OptocraftSHS(AbstractInterferometer):
    '''
    Optocraft SHS Wavefront Sensor implementation
    '''
    # Field constants
    MEASUREMENT_FIELD = 33
    DARK_MEASUREMENT_FIELD = 34
    MEAS_MINUS_DARK_MEASUREMENT_FIELD = 35
    SPOT_DISPLACEMENT_X_FIELD = 38
    SPOT_DISPLACEMENT_Y_FIELD = 39
    ERROR_FUNCTION_FIELD = 41
    WAVEFRONT_FIELD = 42
    CORRECTED_WAVEFRONT_FIELD = 43
    ZERNIKE_EVALUATION_FIELD = 44

    MODEL_NAME = 'optocraft_shs_works'

    def __init__(self, name='OptocraftSHS', **kwargs):
        self._name = name
        self.logger = Logger.of('OptocraftSHS')
        self._sh = None
        
        # Get temp folder from config or use default
        if 'temp_folder' in kwargs:
            self.TEMP_FOLDER = Path(kwargs['temp_folder'])
        else:
            self.TEMP_FOLDER = Path(r"C:\Users\Public\tmp")
        
        # Ensure temp folder exists
        os.makedirs(self.TEMP_FOLDER, exist_ok=True)

        # Try to connect to SHSWorks
        try:
            self._sh = ShsClient()
            self._sh.connect()
            version = self._sh.get_shsworks_version()
            self.logger.notice(f"Connected to SHSWorks version {version}")
        except Exception as e:
            raise Exception(
                "Couldn't connect to SHSWorks. "
                "Is the software running? (%s)" % str(e))

    @override
    def name(self):
        return self._name

    @override
    def deinitialize(self):
        if self._sh:
            self._sh.close()

    @override
    def wavefront(self, how_many=1):
        self.logger.notice("Getting wavefront")
        temp_file = self.TEMP_FOLDER / 'temp_wavefront.bix'
        
        try:
            self._sh.select_field(self.MEASUREMENT_FIELD)
            self._sh.grab_org()
            try:
                self._sh.evaluation()
            except Exception as e:
                # Ensure we're using warn not warning
                self.logger.warn(f"Evaluation failed, continuing anyway: {str(e)}")
                
            self._sh.select_field(self.CORRECTED_WAVEFRONT_FIELD)
            self._sh.save_file(temp_file, "ORG")
            
            # Read the data
            data2d, _, _, _ = self._load_bix(temp_file)
            return np.ma.array(data=data2d)
            
        finally:
            # Cleanup
            if temp_file.exists():
                os.remove(temp_file)

    def _load_bix(self, fname):
        from membranemirror.read_write_big_bix import read_bix
        return read_bix(fname, printInfo=False)

    def get_field_stats(self, fieldId):
        self._sh.select_field(fieldId)
        return self._sh.get_field_stats(fieldId)

    @override
    def acquire_burst(self, how_many=1):
        self.logger.warn('The acquire_burst method is not implemented yet!')
        raise Exception('To be implemented!')
    
    @override
    def load_burst(self, tn):
        self.logger.warn('The load_burst method is not implemented yet!')
        raise Exception('To be implemented!')

    @override
    def delete_burst(self, tn):
        self.logger.warn('The delete_burst method is not implemented yet!')
        raise Exception('To be implemented!')
    
    @override
    def list_available_burst(self):
        self.logger.warn('The list_available_burst method is not implemented yet!')
        raise Exception('To be implemented!')