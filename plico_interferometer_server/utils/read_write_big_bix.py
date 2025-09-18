# -*- coding: utf-8 -*-
"""Defines methods for imports and exports of *.big and *.bix files.
"""
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from pathlib import Path
from ctypes import c_byte, c_short, c_long, c_float, c_double

# define dict with data types corresponding to keys provided
# by 3rd binary short in *.big / *.bix files
DTYPE_DICT = {1: np.int8,  # 0001 hex = BYTE
              2: np.int16,  # 0002 hex = short int (2 Bytes)
              4: np.int32,  # 0004 hex = long (4 Bytes),
              20: np.float32,  # 0014 hex = float (4 Bytes),
              24: np.float64}  # 0018 hex = double (8 Bytes),

# dict for writing big and bix files
CTYPE_DICT = {1: c_byte,  # 0001 hex = BYTE
              2: c_short,  # 0002 hex = short int (2 Bytes)
              4: c_long,  # 0004 hex = long (4 Bytes),
              20: c_float,  # 0014 hex = float (4 Bytes),
              24: c_double}  # 0018 hex = double (8 Bytes),

UNBELEGT_DICT = {1: 0,  # 0001 hex = BYTE
                 2: -32768,  # 0002 hex = short int (2 Bytes)
                 4: -2147483648,  # 0004 hex = long (4 Bytes),
                 20: - 3.402823466e+38,  # 0014 hex = float (4 Bytes),
                 24: -1.7976931348623157e+308}

UNEDEFINED_DICT = {1: 255,  # 0001 hex = BYTE
                   2: 32767,  # 0002 hex = short int (2 Bytes)
                   4: 2147483647,  # 0004 hex = long (4 Bytes),
                   20: 3.402823466e+38,  # 0014 hex = float (4 Bytes),
                   24: 1.7976931348623157e+308}


def get_dtype_key(dtype):
    """ function returns the datatype key as it
    is used in exported bix / big files
    ## Args:
        array (numpy.ndarray)
    """
    if dtype == np.int8:
        return 1
    if dtype == np.int16:
        return 2
    if dtype == np.int32:
        return 4
    if dtype == np.float32:
        return 20
    if dtype in [np.float64, np.double]:
        return 24


def read_big(fname, printInfo=False):
    """ reads in a *.big file and returns the values as
    a masked array for dtype float / double
    and as a numpy array without mask for dtype int.
    """
    p = Path(fname)
    if p.suffix != '.big':
        raise TypeError("Input file was not of data type '.big'.")
    with open(fname, 'rb') as f:
        if printInfo:
            print('Reading in *.big file:')
            print(fname)

        # read in header
        nx, ny, dTypeKey = np.fromfile(f, dtype=np.short, count=3)
        if printInfo:
            print('nx = {0:0}, ny = {1:0}, dTypeKey = {2:0}'.format(
                nx, ny, dTypeKey))

        testNull = np.fromfile(f, dtype=np.int_, count=1)[
            0]  # np.int_ == c_long
        if printInfo:
            print('testNull = {0}'.format(testNull))
        if (testNull != 0):
            raise TypeError(
                'The big does not have the shape it should have.'
                ' the long at pos. 4 is unequal to 0.')

        # conversion of short to int to prevent overflow
        data = np.fromfile(f,
                           dtype=DTYPE_DICT[dTypeKey],
                           count=int(nx) * int(ny))
    data2d = data.reshape(ny, nx)

    unbelegt = UNBELEGT_DICT[dTypeKey]
    mask2d = (data2d == unbelegt)
    if (dTypeKey in [20, 24]):
        data2d[mask2d] = np.nan
    masked = ma.masked_array(data=data2d,
                             mask=mask2d
                             )
    return masked


def write_big(path, data, dTypeKey=None):
    """Writes *.big file to path.

    ## Parameters
        path (str / Path)  # output path
        dTypeKey (int)  # key for the data type
                1: c_byte    # 0001 hex = BYTE
                2: c_short   # 0002 hex = short int (2 Bytes)
                4: c_long    # 0004 hex = long (4 Bytes),
                20: c_float  # 0014 hex = float (4 Bytes),
                24: c_double # 0018 hex = double (8 Bytes),
        data (2d numpy array)  # contains data to be exported.
    """
    if dTypeKey is None:
        dTypeKey = get_dtype_key(data.dtype)
    p = Path(path)
    ny, nx = data.shape
    assert p.suffix == '.big', ("Extension of path for write_big"
                                " function needs to be '.big.'")
    if isinstance(data, ma.MaskedArray):
        outdata = data.data
        outdata[data.mask] = UNBELEGT_DICT[dTypeKey]
    else:
        outdata = data

    with open(path, 'wb') as f:  # 'wb' is binary mode
        f.write(c_short(nx))
        f.write(c_short(ny))
        f.write(c_short(dTypeKey))
        f.write(c_long(0))
        # flatten makes data 1dimensional
        f.write(outdata.flatten().astype(CTYPE_DICT[dTypeKey]))


def read_bix(fname, printInfo=False, getRef=False):
    """ reads in a *.bix file
    ## Arguments:
        fname (str / Path)  # must end with suffix '.bix'
        printInfo: bool  # if True, read in meta data is printed
        getRef: bool  # if True, the Reference is also returned, in case
                      # there is a reference saved in the bix to be opened.
    ## Returns:
        data2d: (masked array)  # data2d.shape = (ny, nx)
        x: (numpy array, dtype('double'))  # contains x-coordinates in mm.
        y: (numpy array, dtype('double'))  # contains y-coordinates in mm.
        comment: str
        reference: {masked array}  # if reference is returned,
                                   # it has the same dimensions as data2d.
    ## Example:
    ```python
    data2d, x, y, comment = read_bix(fname) # no reference
    data2d, x, y, comment, ref = read_bix(fname, getRef = True)
    ```
    """
    p = Path(fname)
    if p.suffix != '.bix':
        raise TypeError("Input file was not of data type '.bix'.")
    with open(fname, 'rb') as f:
        if printInfo:
            print('Reading in *.bix file:')
            print(fname)

        # read in header
        nx, ny, dTypeKey = np.fromfile(f, dtype=np.short, count=3)
        if printInfo:
            print('nx = {0:0}, ny = {1:0}, dTypeKey = {2:0}'.format(
                nx, ny, dTypeKey))

#        testNull = np.fromfile(f, dtype=np.int_, count=1)[
#            0]  # np.int_ == c_long
        testNull = np.fromfile(f, dtype='>i4', count=1)[
            0]  # np.int_ == c_long
        if printInfo:
            print('testNull = {0}'.format(testNull))
        if (testNull != 0):
            raise TypeError(
                'The big does not have the shape it should have.'
                ' the long at pos. 4 is unequal to 0.')

        # conversion from short to int to prevent overflow
        data = np.fromfile(f,
                           dtype=DTYPE_DICT[dTypeKey],
                           count=int(nx) * int(ny))
        data2d = data.reshape(ny, nx)

        unbelegt = UNBELEGT_DICT[dTypeKey]
        mask2d = (data2d == unbelegt)
        if (dTypeKey in [20, 24]):
            data2d[mask2d] = np.nan
        masked = ma.masked_array(data=data2d, mask=mask2d)

        x = np.fromfile(f, dtype=np.double, count=int(nx))
        y = np.fromfile(f, dtype=np.double, count=int(ny))

        # read in comment (ends with terminating zero-byte: b'\x00')
        lastbyte = b''
        comment = ''
        while lastbyte != b'\x00':
            comment += lastbyte.decode('ascii')
            lastbyte = f.read(1)

        if printInfo:
            print("Comment = '" + comment + "'")
        refFlag = np.fromfile(f, dtype=np.short, count=1)
        refmasked = ma.array([])
        if refFlag and getRef:
            if printInfo:
                print('Reference flag was recognized!')
            # conversion from short to int to prevent overflow
            reference = np.fromfile(f,
                                    dtype=DTYPE_DICT[dTypeKey],
                                    count=int(nx) * int(ny))
            reference2d = reference.reshape(ny, nx)
            refmask2d = (data2d == unbelegt)
            if (dTypeKey in [20, 24]):
                reference2d[refmask2d] = np.nan
            refmasked = ma.masked_array(data=reference2d,
                                        mask=refmask2d
                                        )

    if getRef:
        # alternatively one could stack reference and data,
        # but it seems more inconvenient to me.
        # masked = ma.dstack((masked, refmasked))
        return masked, x, y, comment, refmasked
    else:
        return masked, x, y, comment


def write_bix(path, data, x, y, dTypeKey=None, comment='', refData=None):
    """Writes *.bix file to path.

    ## Parameters
    ```python
    path (str / Path): output path
    dTypeKey (int): key for the data type
            1: c_byte    # 0001 hex = BYTE
            2: c_short   # 0002 hex = short int (2 Bytes)
            4: c_long    # 0004 hex = long (4 Bytes),
            20: c_float  # 0014 hex = float (4 Bytes),
            24: c_double # 0018 hex = double (8 Bytes),
    data (2d numpy array)  # contains data to be exported.
    x (1d numpy array)  # x-coordinates
    y (1d numpy array)  # y-coordinates
    comment='' (str)  # comment string
    refData (2d numpy array)  # same shape as data, contains reference frame.
    ```
    """
    if dTypeKey is None:
        dTypeKey = get_dtype_key(data.dtype)
    p = Path(path)
    ny, nx = data.shape
    assert p.suffix == '.bix', ("Extension of path for write_bix"
                                " function needs to be '.bix.'")
    if refData is not None:
        assert refData.shape
    if isinstance(data, ma.MaskedArray):
        outdata = data.data
        outdata[data.mask] = UNBELEGT_DICT[dTypeKey]
    else:
        outdata = data

    with open(path, 'wb') as f:  # 'wb' is binary mode
        f.write(c_short(nx))
        f.write(c_short(ny))
        f.write(c_short(dTypeKey))
        f.write(c_long(0))
        # flatten makes data 1dimensional
        f.write(outdata.flatten().astype(CTYPE_DICT[dTypeKey]))

        f.write(x.astype(c_double))
        f.write(y.astype(c_double))

        # comment ends with terminating zero-byte: b'\x00'
        f.write(comment.encode('ascii') + b'\x00')

        refFlag = (refData is not None)
        f.write(c_short(refFlag))
        if refFlag:
            f.write(refData.flatten().astype(CTYPE_DICT[dTypeKey]))


# testskript
if __name__ == '__main__':
    fname = Path.cwd() / 'test.bix'
    masked, x, y, comment = read_bix(fname, printInfo=True)
    # print("Comment = '" + comment + "'")
    plt.figure(dpi=100)
    plt.title('original bix')
    plt.imshow(masked,
               cmap='jet',
               extent=(x.min(), x.max(), y.min(), y.max())
               )
    plt.colorbar(label=r'wavefront [um]')

    outname = Path.cwd() / 'test_out.bix'

    # # rotateData = np.rot90(masked.data)
    # # rotateMask = np.rot90(masked.mask)
    # # rotated = ma.MaskedArray(data=rotateData, mask=rotateMask)
    mirrored = np.fliplr(masked)

    write_bix(outname, mirrored, x, y)
    masked2, x2, y2, comment2 = read_bix(outname, printInfo=True)
    plt.figure(dpi=100)
    plt.imshow(masked2,
               cmap='jet',
               extent=(x.min(), x.max(), y.min(), y.max())
               )
    plt.title('saved, mirrored, re-imported')
    plt.colorbar(label=r'wavefront [um]')
