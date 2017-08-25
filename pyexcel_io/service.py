"""
    pyexcel_io.service
    ~~~~~~~~~~~~~~~~~~~

    provide service code to downstream projects

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import re
import math
import datetime

from pyexcel._compact import PY2


def has_no_digits_in_float(value):
    """check if a float value had zero value in digits"""
    return value == math.floor(value)


def detect_date_value(cell_text):
    """
    Read the date formats that were written by csv.writer
    """
    ret = None
    try:
        if len(cell_text) == 10:
            ret = datetime.datetime.strptime(
                cell_text,
                "%Y-%m-%d")
            ret = ret.date()
        elif len(cell_text) == 19:
            ret = datetime.datetime.strptime(
                cell_text,
                "%Y-%m-%d %H:%M:%S")
        elif len(cell_text) > 19:
            ret = datetime.datetime.strptime(
                cell_text[0:26],
                "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        pass
    return ret


def detect_float_value(cell_text):
    try:
        should_we_skip_it = (cell_text.startswith('0') and
                             cell_text.startswith('0.') is False)
        if should_we_skip_it:
            # do not convert if a number starts with 0
            # e.g. 014325
            return None
        else:
            return float(cell_text)
    except ValueError:
        return None


def detect_int_value(cell_text):
    if cell_text.startswith('0') and len(cell_text) > 1:
        return None
    try:
        return int(cell_text)
    except ValueError:
        pattern = '([0-9]+,)*[0-9]+$'
        if re.match(pattern, cell_text):
            integer_string = cell_text.replace(',', '')
            return int(integer_string)
        else:
            return None


def float_value(value):
    """convert a value to float"""
    ret = float(value)
    return ret


def date_value(value):
    """convert to data value accroding ods specification"""
    ret = "invalid"
    try:
        # catch strptime exceptions only
        if len(value) == 10:
            ret = datetime.datetime.strptime(
                value,
                "%Y-%m-%d")
            ret = ret.date()
        elif len(value) == 19:
            ret = datetime.datetime.strptime(
                value,
                "%Y-%m-%dT%H:%M:%S")
        elif len(value) > 19:
            ret = datetime.datetime.strptime(
                value[0:26],
                "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass
    if ret == "invalid":
        raise Exception("Bad date value %s" % value)
    return ret


def time_value(value):
    """convert to time value accroding the specification"""
    import re
    results = re.match('PT(\d+)H(\d+)M(\d+)S', value)
    if results and len(results.groups()) == 3:
        hour = int(results.group(1))
        minute = int(results.group(2))
        second = int(results.group(3))
        if hour < 24:
            ret = datetime.time(hour, minute, second)
        else:
            ret = datetime.timedelta(hours=hour,
                                     minutes=minute,
                                     seconds=second)
    else:
        ret = None
    return ret


def boolean_value(value):
    """get bolean value"""
    if value == "true":
        ret = True
    else:
        ret = False
    return ret


ODS_FORMAT_CONVERSION = {
    "float": float,
    "date": datetime.date,
    "time": datetime.time,
    'timedelta': datetime.timedelta,
    "boolean": bool,
    "percentage": float,
    "currency": float
}


ODS_WRITE_FORMAT_COVERSION = {
    float: "float",
    int: "float",
    str: "string",
    datetime.date: "date",
    datetime.time: "time",
    datetime.timedelta: "timedelta",
    bool: "boolean"
}

if PY2:
    ODS_WRITE_FORMAT_COVERSION[unicode] = "string"

VALUE_CONVERTERS = {
    "float": float_value,
    "date": date_value,
    "time": time_value,
    "timedelta": time_value,
    "boolean": boolean_value,
    "percentage": float_value
}


VALUE_TOKEN = {
    "float": "value",
    "date": "date-value",
    "time": "time-value",
    "boolean": "boolean-value",
    "percentage": "value",
    "currency": "value",
    "timedelta": "time-value"
}