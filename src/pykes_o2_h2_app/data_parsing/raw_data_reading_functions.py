import pandas as pd
import io

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

    # Column labels carry the channel in brackets, so match on the stable parts of the name
    time_column = next(column for column in table.columns if 'dt (s)' in column and 'Main' in column)
    value_column = next(column for column in table.columns if 'Oxygen' in column and 'Main' in column)
    temperature_column = next(column for column in table.columns if 'CompT' in column and 'Temp' in column)

    raw_data_dict = {
        'time_s': table[time_column].to_numpy(float),
        'time_unit': 's',
        'measurement_raw': table[value_column].to_numpy(float),
        'temperature': table[temperature_column].to_numpy(float),
    }

    if mode == 'liquid':
        raw_data_dict['measurement_unit'] = 'umol/L'
    elif mode == 'gas':
        raw_data_dict['measurement_unit'] = 'vol%'
    else:
        raise ValueError("Mode must be either 'liquid' or 'gas'.")

    return raw_data_dict

