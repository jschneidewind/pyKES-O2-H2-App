import numpy as np
import pandas as pd
import io

# PyroScience column labels carry their channel in brackets, so columns are
# matched on the stable parts of the label

# Channel of a Workbench 'Recalculate Oxygen' process step, e.g. '%O2 [P1 Recalc O2]'
RECALCULATED_O2_CHANNEL = 'Recalc O2]'

# PT100 temperature sensor logged as its own channel, e.g. 'Sample Temp. (°C) [ T1]'
TEMPERATURE_SENSOR_CHANNEL = 'T1]'

def reading_H2_file(file_H2, mode = 'liquid'):
    '''
    Reading data from UniAmp H2 sensor files.
    '''

    raw_data = pd.read_csv(file_H2, sep = ';')
    
    time_s = raw_data['Time since start (s)'].to_numpy()

    try:
        H2_temp = raw_data['Sensor 2 - TEMP-UNIAMP (°C)'].to_numpy()
    except KeyError:
        H2_temp = 0

    raw_data_dict = {
            'time_s': time_s,
            'time_unit': 's',
            'temperature': H2_temp}
    
    if mode == 'liquid':
        H2_umol_L = raw_data['Sensor 1 - H2 (μmol/L)'].to_numpy()
        raw_data_dict['measurement_raw'] = H2_umol_L
        raw_data_dict['measurement_unit'] = 'umol/L'

    elif mode == 'gas':
        H2_Pa = raw_data['Sensor 1 - H2 (Pa)'].to_numpy()
        raw_data_dict['measurement_raw'] = H2_Pa
        raw_data_dict['measurement_unit'] = 'Pa'

    else:
        raise ValueError("Mode must be either 'liquid' or 'gas'.")

    return raw_data_dict


def reading_O2_file(file_O2, mode = 'liquid'):
    """
    Load a PyroScience Workbench oxygen log.

    Reads both direct logs of the sensor channel and exports of a Workbench
    'Recalculate Oxygen' process step.

    Parameters
    ----------
    file_O2 : Path
        Name of the .txt file.
    mode : str, optional
        Mode of the O2 measurement, either 'liquid' or 'gas'. Default is 'liquid'.
        'Liquid' assumes data in unit umol[O2]/L, 
        while 'gas' assumes data in vol%[O2].

    Returns
    -------
    raw_data_dict : dict
        Dictionary containing the time and oxygen data.
    """
    with open(file_O2, encoding='ISO8859') as data_file:
        lines = data_file.readlines()

    # The file starts with ~25 lines of instrument metadata prefixed by '#';
    # the measurement table begins at the line starting with 'Date'.
    header_index = next(i for i, line in enumerate(lines) if line.startswith('Date'))
    table = pd.read_csv(io.StringIO(''.join(lines[header_index:])), sep='\t')

    if any(RECALCULATED_O2_CHANNEL in column for column in table.columns):
        raw_data_dict = read_recalculated_O2_table(table)
    else:
        raw_data_dict = read_logged_O2_table(table)

    if mode == 'liquid':
        raw_data_dict['measurement_unit'] = 'umol/L'
    elif mode == 'gas':
        raw_data_dict['measurement_unit'] = 'vol%'
    else:
        raise ValueError("Mode must be either 'liquid' or 'gas'.")

    return raw_data_dict


def read_logged_O2_table(table: pd.DataFrame) -> dict:
    """
    Extract the O2 trace from a direct log of the oxygen sensor channel.

    The oxygen values are in the sensor's main channel ('Oxygen (%O2) [A Ch.1 Main]'),
    with the compensation temperature sampled alongside ('[A Ch.1 CompT]').

    Parameters
    ----------
    table : pd.DataFrame
        Measurement table of the PyroScience file.

    Returns
    -------
    raw_data_dict : dict
        Time, oxygen and temperature data, without the measurement unit.
    """
    time_column = next(column for column in table.columns if 'dt (s)' in column and 'Main' in column)
    value_column = next(column for column in table.columns if 'Oxygen' in column and 'Main' in column)
    temperature_column = next(column for column in table.columns if 'CompT' in column and 'Temp' in column)

    # Interrupted logs end with rows lacking the main channel (empty rows, extra
    # samples of other channels), which would otherwise become NaN measurements
    table = table.dropna(subset = [time_column])

    return {
        'time_s': table[time_column].to_numpy(float),
        'time_unit': 's',
        'measurement_raw': table[value_column].to_numpy(float),
        'temperature': table[temperature_column].to_numpy(float),
    }


def read_recalculated_O2_table(table: pd.DataFrame) -> dict:
    """
    Extract the O2 trace from the export of a Workbench 'Recalculate Oxygen' process step.

    The recalculated oxygen values have their own channel ('%O2 [P1 Recalc O2]').
    The temperature comes from the PT100 sensor channel ('[ T1]'), which logs on
    its own clock (twice per O2 sample in AE-918), so its rows do not line up
    with the O2 rows and it is interpolated onto the O2 times.

    Parameters
    ----------
    table : pd.DataFrame
        Measurement table of the PyroScience file.

    Returns
    -------
    raw_data_dict : dict
        Time, oxygen and temperature data, without the measurement unit.
    """
    recalculated_columns = [column for column in table.columns if RECALCULATED_O2_CHANNEL in column]
    time_column = next(column for column in recalculated_columns if 'dt (s)' in column)

    # Besides the oxygen values the channel only holds their date, time and dt (s),
    # so the value column is found without depending on the exported unit
    value_column = next(column for column in recalculated_columns
                        if not column.lstrip().startswith(('Date', 'Time', 'dt (s)')))

    temperature_time_column = next(column for column in table.columns
                                   if 'dt (s)' in column and TEMPERATURE_SENSOR_CHANNEL in column)
    temperature_column = next(column for column in table.columns
                              if 'Temp' in column and TEMPERATURE_SENSOR_CHANNEL in column)

    # Each channel leaves its cells empty once its own samples run out
    oxygen = table[[time_column, value_column]].dropna()
    temperature = table[[temperature_time_column, temperature_column]].dropna()

    time_s = oxygen[time_column].to_numpy(float)

    return {
        'time_s': time_s,
        'time_unit': 's',
        'measurement_raw': oxygen[value_column].to_numpy(float),
        'temperature': np.interp(time_s,
                                 temperature[temperature_time_column].to_numpy(float),
                                 temperature[temperature_column].to_numpy(float)),
    }

