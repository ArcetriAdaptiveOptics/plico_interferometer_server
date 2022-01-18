import numpy as np
from plico.utils.logger import Logger
from plico.utils.decorator import override
from plico_interferometer_server.devices.abstract_interferometer import \
    AbstractInterferometer
from plico_interferometer_server.devices.i4d_6110 import I4D_6110


class PhaseCam6110(AbstractInterferometer):
    '''
    4D Technology PhaseCam 6110
    '''

    def __init__(self,
                 ipaddr,
                 port=23,
                 timeout=2,
                 name='PhaseCam6110',
                 **_):
        self._name = name
        self.ipaddr = ipaddr
        self.port = port
        self._i4d = I4D_6110(ipaddr, port)
        self.timeout = timeout
        self.logger = Logger.of('PhaseCam6110')

    @override
    def name(self):
        return self._name

    @override
    def wavefront(self, how_many=1):
        if how_many == 1:
            width, height, pixel_size_in_microns, data_array = \
                self._i4d.takeSingleMeasurement()
        else:
            cube_list = []
            for i in range(how_many):
                width, height, pixel_size_in_microns, data_array = \
                    self._i4d.takeSingleMeasurement()
                cube_list.append(data_array)
            cube = np.dstack(cube_list)
            data_array = np.ma.mean(cube, axis=2)
        data = np.reshape(data_array, (width, height))
        idx, idy = np.where(np.isnan(data))
        mask = np.zeros((data.shape[0], data.shape[1]))
        mask[idx, idy] = 1
        masked_ima = np.ma.masked_array(data, mask=mask.astype(bool))
        return masked_ima

    @override
    def deinitialize(self):
        pass
