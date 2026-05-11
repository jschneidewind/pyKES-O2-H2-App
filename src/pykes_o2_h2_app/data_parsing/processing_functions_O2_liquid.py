from pathlib import Path

from pykes_o2_h2_app.data_parsing.raw_data_reading_functions import reading_O2_file
from pykes_o2_h2_app.data_parsing.general_processing_functions import processing_data
from pykes_o2_h2_app.parameters import PROCESSING_PARAMETERS

def raw_data_reading_function_O2_liquid(directory: Path, metadata_dict):
    '''
    Reads raw O2 liquid phase data from a file.
    '''

    # Checking that the measured analyte and phase is correct
    assert metadata_dict['Measured Analyte [O2 or H2]'] == 'O2', \
    f"Expected measured analyte 'O2', but got '{metadata_dict['Measured Analyte [O2 or H2]']}'"
    assert metadata_dict['Measurement phase [liquid/gas]'] == 'liquid', \
    f"Expected measurement phase 'liquid', but got '{metadata_dict['Measurement phase [liquid/gas]']}'"

    file_O2 = directory / metadata_dict['File name O2']
    raw_data_O2 = reading_O2_file(file_O2, channel = metadata_dict['Pyroscience Channel'])

    return raw_data_O2

def processing_function_O2_liquid(raw_data_dict, metadata_dict):
    '''
    Processes raw O2 liquid phase data.
    '''
    
    processed_O2 = processing_data(
        time = raw_data_dict['O2_time_s'],
        data = raw_data_dict['O2_data'],
        start = metadata_dict['Pyroscience Irradiation start [s]'],
        end = metadata_dict['Pyroscience Irradiation end [s]'],
        prefix = 'O2_liquid',
        **PROCESSING_PARAMETERS['O2_liquid_processing_parameters']
    )

    return processed_O2