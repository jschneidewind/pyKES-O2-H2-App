from pathlib import Path

from pykes_o2_h2_app.data_parsing.raw_data_reading_functions import reading_O2_file
from pykes_o2_h2_app.data_parsing.general_processing_functions import processing_data, convert_gases_to_mmol
from pykes_o2_h2_app.parameters import PROCESSING_PARAMETERS

def raw_data_reading_function_O2_gas(directory: Path, metadata_dict):
    '''
    Reads raw O2 gas phase data from a file.
    '''

    # Checking that the measured analyte and phase is correct
    assert metadata_dict['Measured Analyte [O2 or H2]'] == 'O2', \
    f"Expected measured analyte 'O2', but got '{metadata_dict['Measured Analyte [O2 or H2]']}'"
    assert metadata_dict['Measurement phase [liquid/gas]'] == 'gas', \
    f"Expected measurement phase 'gas', but got '{metadata_dict['Measurement phase [liquid/gas]']}'"

    file_O2 = directory / metadata_dict['File name O2']
    raw_data_O2 = reading_O2_file(file_O2, channel = metadata_dict['Pyroscience Channel'])

    return raw_data_O2

def processing_function_O2_gas(raw_data_dict, metadata_dict):
    '''
    Processes raw O2 gas phase data.
    '''

    data_mmol = convert_gases_to_mmol(raw_data_dict['O2_data'], 
                                      gas_phase_volume = metadata_dict['Gas phase volume [mL]'],
                                      H2 = False)   

    processed_O2 = processing_data(
        time = raw_data_dict['O2_time_s'],
        data = data_mmol,
        start = metadata_dict['Pyroscience Irradiation start [s]'],
        end = metadata_dict['Pyroscience Irradiation end [s]'],
        prefix = 'O2_gas',
        **PROCESSING_PARAMETERS['O2_gas_processing_parameters']
    )

    catalyst_mass_g = metadata_dict['Catalyst concentration [g/L]'] * metadata_dict['Liquid phase volume [mL]'] * (1/1000) # Convert from g/L and mL to g
    processed_O2['O2_gas_max_rate'] = processed_O2['O2_gas_max_rate'] / catalyst_mass_g * 3600 # convert from mmol s^-1 to mmol g^-1 h^-1

    return processed_O2