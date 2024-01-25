#!/usr/bin/env python
import os
import tempfile
import unittest
import logging
from plico.utils.logger import Logger
from plico_interferometer_server.devices.WCF_interface_for_4SightFocus import WCFInterfacer


class WCFInterfacerTest(unittest.TestCase):

    def setUp(self):
        self._setUpLogging()
        self._ip = '123.345.456.123'
        self._port = 1111
        burst_folder = os.path.join(tempfile.gettempdir(), 'eeesss')
        self._interferometer = WCFInterfacer(
            self._ip, self._port, burst_folder, name='MyInterf')

        # Bad Hack to substitute calls to real hw
        # with a dummy one
        self._interferometer._readJsonData = self._my_readJsonData

        self._calls = []

    def _expected_url_TakeSingleMeasurement(self):
        return 'http://%s:%i/SystemService/TakeSingleMeasurement/' % (
            self._ip, self._port)

    def _my_readJsonData(self, url, data=None, timeout=None):
        '''
        This one register the calls to the WFC and return the proper
        structure according to the requested url
        '''
        this_call = {'url': url, 'data': data, 'timeout': timeout}
        self._logger.notice("Got call %s" % this_call)
        self._calls.append(this_call)
        # parse url to mimick proper return values
        if url == self._expected_url_TakeSingleMeasurement():
            ret = {}
            ret['Width'] = 2
            ret['Height'] = 3
            ret['PixelSizeInMicrons'] = 12.3
            ret['Data'] = (12, 13, 14, 15, 16, 17)
            return ret
        else:
            self._logger.warn("unknown url %s" % this_call)
            return

    def tearDown(self):
        pass

    def _setUpLogging(self):
        FORMAT = '%(asctime)s %(levelname)s %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self._logger = Logger.of(self.__class__.__name__)

    def test_wavefront_single(self):
        wv = self._interferometer.wavefront(how_many=1)
        wanted_url = self._expected_url_TakeSingleMeasurement()
        self.assertEqual(self._calls[-1]['url'], wanted_url)


if __name__ == "__main__":
    unittest.main()
