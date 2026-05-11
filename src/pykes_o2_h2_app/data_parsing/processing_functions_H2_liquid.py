from pathlib import Path

from pykes_o2_h2_app.data_parsing.raw_data_reading_functions import reading_H2_file
from pykes_o2_h2_app.data_parsing.general_processing_functions import processing_data
from pykes_o2_h2_app.parameters import PROCESSING_PARAMETERS

def raw_data_reading_function_H2_liquid(directory: Path, metadata_dict):
    '''
    Reads raw H2 liquid phase data from a file.
    '''

    # Checking that the measured analyte and phase is correct
    assert metadata_dict['Measured Analyte [O2 or H2]'] == 'H2', \
    f"Expected measured analyte 'H2', but got '{metadata_dict['Measured Analyte [O2 or H2]']}'"
    assert metadata_dict['Measurement phase [liquid/gas]'] == 'liquid', \
    f"Expected measurement phase 'liquid', but got '{metadata_dict['Measurement phase [liquid/gas]']}'"

    file_H2 = directory / metadata_dict['File name H2']
    raw_data_H2 = reading_H2_file(file_H2, mode = 'liquid')

    return raw_data_H2

def processing_function_H2_liquid(raw_data_dict, metadata_dict):
    '''
    Processes raw H2 liquid phase data.
    '''
    
    processed_H2 = processing_data(
        time = raw_data_dict['H2_time_s'],
        data = raw_data_dict['H2_umol_L'],
        start = metadata_dict['Unisense Irradiation start [s]'],
        end = metadata_dict['Unisense Irradiation end [s]'],
        prefix = 'H2_liquid',
        **PROCESSING_PARAMETERS['H2_liquid_processing_parameters']
    )

    return processed_H2