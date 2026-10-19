'''
HTTP server for 4Sight 2.23 and 2.4, to be run inside 4Sight.

It replaces the Pyro server (Server.py) with a subset of the 4Sight Focus
web service, so that 4Sight 2.23 can be used directly by the
plico_interferometer 4SightFocus client (and by opticalib) without a
plico_interferometer_server and without Pyro:

    GET /SystemService/TakeSingleMeasurement/
        {"Width": rows, "Height": cols, "PixelSizeInMicrons": p,
         "Data": [...]}  wavefront in waves, row-major, NaN where masked
    GET /SystemService/GetSystemInfo
        {"SystemSerialNumber": name}

Width is the number of rows, as the client reshapes Data to
(Width, Height).

The Python embedded in 4Sight 2.23 is old and has a reduced standard
library, so only socket, threading and numpy are used and the syntax is
kept valid for old Python 2 and for Python 3.
'''
import socket
import sys
import threading

import numpy

MEASURE_PATH = '/SystemService/TakeSingleMeasurement'
INFO_PATH = '/SystemService/GetSystemInfo'


def _measure_4sight():
    from Scripting.Measurements import Measure
    ret = Measure().GetDataset().GetArray()
    return ret.data, ret.mask


def measurement_json(data, mask, pixel_size_in_microns=0.0):
    '''JSON string of a wavefront in the 4Sight Focus format'''
    data = numpy.asarray(data, dtype=numpy.float64)
    rows, cols = data.shape
    bad = numpy.logical_or(numpy.asarray(mask, dtype=bool),
                           numpy.logical_not(numpy.isfinite(data))).ravel()
    values = ['%.7g' % v for v in data.ravel().tolist()]
    # repr/format of NaN is not portable on old Windows Pythons ('1.#QNAN')
    for i in numpy.nonzero(bad)[0].tolist():
        values[i] = 'NaN'
    return '{"Width": %d, "Height": %d, "PixelSizeInMicrons": %r, ' \
        '"Data": [%s]}' % (rows, cols, float(pixel_size_in_microns),
                           ', '.join(values))


def _error_json(message):
    message = message.replace('\\', '\\\\').replace('"', '\\"')
    return '{"Error": "%s"}' % message.replace('\n', ' ')


class Server(threading.Thread):
    '''
    Serves the HTTP requests one at a time in a daemon thread.

    Parameters
    ----------
    port: int
        TCP port, 8011 as the 4Sight Focus web service by default
    host: str
        address to bind, all interfaces by default
    name: str
        returned as SystemSerialNumber
    pixel_size_in_microns: float
        returned as PixelSizeInMicrons
    measure: callable
        returns (data, mask) of a single measurement; 4Sight Measure()
        by default
    '''

    def __init__(self, port=8011, host='', name='Wyko4100',
                 pixel_size_in_microns=0.0, measure=None):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.name4d = name
        self.pixel_size_in_microns = pixel_size_in_microns
        if measure is None:
            measure = _measure_4sight
        self._measure = measure
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._sock.listen(5)
        self.port = self._sock.getsockname()[1]
        self._running = True

    def log(self, message):
        print('I4D HTTP server: %s' % message)

    def run(self):
        self.log('listening on port %d' % self.port)
        while self._running:
            try:
                conn = self._sock.accept()[0]
            except socket.error:
                break
            try:
                try:
                    self._handle(conn)
                except Exception:
                    self.log('error: %s' % str(sys.exc_info()[1]))
            finally:
                conn.close()
        self.log('stopped')

    def stop(self):
        self._running = False
        self._sock.close()

    def _read_request_line(self, conn):
        conn.settimeout(10)
        request = ''
        while '\r\n\r\n' not in request and len(request) < 65536:
            chunk = conn.recv(4096)
            if not chunk:
                break
            request = request + chunk.decode('latin-1')
        return request.split('\r\n')[0]

    def _reply(self, conn, status, body):
        header = 'HTTP/1.0 %s\r\nContent-Type: application/json\r\n' \
            'Content-Length: %d\r\nConnection: close\r\n\r\n' % (
                status, len(body))
        conn.sendall((header + body).encode('ascii'))

    def _handle(self, conn):
        parts = self._read_request_line(conn).split()
        if len(parts) < 2 or parts[0] != 'GET':
            self._reply(conn, '400 Bad Request', _error_json('GET only'))
            return
        path = parts[1].rstrip('/')
        if path == MEASURE_PATH:
            try:
                data, mask = self._measure()
                body = measurement_json(data, mask,
                                        self.pixel_size_in_microns)
            except Exception:
                message = str(sys.exc_info()[1])
                self.log('measurement failed: %s' % message)
                self._reply(conn, '500 Internal Server Error',
                            _error_json(message))
                return
            self._reply(conn, '200 OK', body)
        elif path == INFO_PATH:
            self._reply(conn, '200 OK',
                        '{"SystemSerialNumber": "%s"}' % self.name4d)
        else:
            self._reply(conn, '404 Not Found', _error_json(parts[1]))
