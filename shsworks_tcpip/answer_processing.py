"""contains decode methods for answer string processing to enable unit tests.
"""
#%% imports
from pathlib import Path
from .shsworks_error import SHSWorksError, UnexpectedAnswerFormatError
from typing import Union


def _to_float(value_str: str) -> float:
    """Converts input value to float and checks for equality with the
    placeholder for an undefined variable.

    Args:
        value_str (str): value obtained from SHSworks.

    Returns:
        float: float(value_str)
    """
    value_str = value_str.replace(',', '.')
    if value_str == 'NaN':
        return float('nan')
    else:
        return float(value_str)

def _to_number(value_str: str) -> Union[int, float]:
    value_str = value_str.replace(',', '.')
    try:
        return int(value_str)
    except ValueError:
        pass
    try:
        return _to_float(value_str)
    except ValueError:
        raise ValueError(f'Expected number, got {value_str} instead.')

def _split_answer(answer: str) -> list:
    """Splits answer at '|', replaces commas with points and strips linebreak.

    Args:
        answer (str)  # SHSworks format answer

    Returns:
        list(str)

    Example:
        >>> split_answer('Stop|JID=000|OP=;ST=;SN=|1=Ok|1\\r\\n')
        ['Stop', 'JID=000', 'OP=;ST=;SN=', '1=Ok', '1']
    """
    answer_str = answer.replace('\r\n', '').replace(',', '.')
    return answer_str.split('|')

def _cam_par_dict_from_str(cam_par_str: str) -> dict:
    """ Helper function for `Client.get_cam_settings()`.
    Creates a  dictionary from a string as returned from MID 9.

    Args:
        cam_par_str (str)  # part of string returned from SHSWorks

    Example:
        >>> cam_par_str = ("BUS=0;CAM=0;TRI=3;ASH=0;AVE=8;SHU=275;BRI=40;"
        >>>                "GAI=1.000;TEM=n.a.;CN=SHS")
        >>> _cam_par_dict_from_str(cam_par_str)
        {'BUS': 0,
        'CAM': 0,
        'TRI': 3,
        'ASH': 0,
        'AVE': 8,
        'SHU': 275.0,
        'BRI': 40.0,
        'GAI': 1.0,
        'TEM': nan,
        'CN': 'SHS'}
    """
    cam_par_str = cam_par_str.replace('n.a.', 'nan')
    splitPars = cam_par_str.split(';')
    out_dict = {}
    sDTypes = {'BUS': int,  # the bus/grabber number
               'CAM': int,  # the camera number
               'TRI': int,  # the trigger mode.
               'ASH': int,  # the Autoshutter function. "0" is off, "1" is on.
               'AVE': int,  # the frames averaged. Valid values are 1, 2, 4, 8, …, 1024.
               'SHU': float,  # shutter time in microseconds.
               'BRI': float,   # the "Brightness" parameter
               'GAI': float,  # the "Gain" parameter
               'TEM': float,  # camera temperature for cameras which have an internal temperature sensor .
               'CN': str  # Camera name
               }
    for s in splitPars:
        key, val = s.split('=')
        out_dict[key] = sDTypes[key](val)
    return out_dict

def process_evaluation(answer: str, pf_indices: list) -> dict:
    """processes the answer to MID 04.

    Args:
        answer (str): answer from SHSWorks to 'Start|JID|04|\r\n'
        pf_indices (list): list of pass fail-indices

    Raises:
        SHSWorksError: in case evaluation went wrong

    Returns:
        dict: pf-item indices as key, their values as value.
    """
    if pf_indices == []:
        # pass fail evaluation off, or no pf-items selected.
        return {}
    out_dict = {}
    values = read_out_list(answer)
    for i, v in enumerate(values):
        key = pf_indices[i]
        try:
            out_dict[key] = _to_number(v.strip(' '))
        except ValueError:
            # print('Failed to convert to number: ', v)
            out_dict[key] = float('nan')
    return out_dict

def read_out_cam_settings(answer: str) -> dict:
    answer_split = _split_answer(answer)
    # v = answer_split[-1]
    cameras = {0: 'SHS', 1: 'VCC', 2: 'SVC'}
    out_dict = {}
    for i, cam_str in enumerate(answer_split[4:]):
        cam = cameras[i]
        if cam_str[:3] != cam:
            raise UnexpectedAnswerFormatError(
                f'answer not understood\n{answer}\n'
                f'cam: {cam} != {cam_str[:3]}')
        settings = cam_str[5:]
        out_dict[cam] = _cam_par_dict_from_str(settings)
    return out_dict

def _get_result(answer: str) -> str:
    try:
        return _split_answer(answer)[4]
    except IndexError:
        raise UnexpectedAnswerFormatError(
            f'Did not receive result. Answer: {answer}')

def read_out_list(answer: str) -> list:
    result = _get_result(answer)
    if result == "":
        return []
    return result.split(';')

def read_out_numbers(answer: str) -> list:
    str_list = read_out_list(answer)
    return [_to_number(v) for v in str_list]

def read_out_bool(answer: str) -> bool:
    result = _get_result(answer)
    if result == '0':
        return False
    if result == '1':
        return True
    raise UnexpectedAnswerFormatError(
        f'Expected 0 or 1, got {result} instead.')

def read_out_number(answer: str) -> Union[float, int]:
    result = _get_result(answer)
    return _to_number(result)

def read_out_parameter(parameter: str, answer: str) -> str:
    result = _get_result(answer)
    if parameter not in result:
        raise UnexpectedAnswerFormatError(
            f'Requested par is not contained in answer: {answer}')
    return result.split('=')[1]

def read_out_stats(answer: str):
    """Decodes statistical data returned from SHSWorks.

    Args
        answer : encoded string returned from SHSWorks.

    Returns
        dict: keys are 'XMIN', 'XMAX', 'YMIN', 'YMAX', 'MIN', 'MAX', 'MEAN',
              'PV', 'RMS'
    """
    answer_split = _split_answer(answer)
    out_dict = {}
    for res in answer_split[4:13]:
        key, val = res.split(':')
        val = val.replace(' ', '')
        undef = ['-1.79769e+308', '-nan(ind)', '-inf']
        if val not in undef:
            out_dict[key] = _to_number(val)
        else:
            out_dict[key] = float('nan')
    return out_dict
