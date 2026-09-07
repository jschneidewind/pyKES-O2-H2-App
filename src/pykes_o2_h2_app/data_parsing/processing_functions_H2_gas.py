from pathlib import Path

from pyKES.utilities.unit_handler import Quantity

from pykes_o2_h2_app.data_parsing.raw_data_reading_functions import reading_H2_file
from pykes_o2_h2_app.data_parsing.general_processing_functions import processing_data, convert_Pa_to_mol

def raw_data_reading_function_H2_gas(directory: Path, metadata_dict: dict) -> dict:
    '''
    Reads raw H2 gas phase data from a file.

    Parameters
    ----------
    directory : Path
        Path to the directory containing the raw data file.
    metadata_dict : dict
        Dictionary containing the metadata, as returned by the metadata retrieval function.
    
    Returns
    -------
    raw_data_dict : dict
        Dictionary containing the raw data, as returned by the raw data reading function.  
    '''

    # Checking that the measured analyte and phase is correct
    assert metadata_dict['Measured Analyte [O2 or H2]'] == 'H2', \
    f"Expected measured analyte 'H2', but got '{metadata_dict['Measured Analyte [O2 or H2]']}'"
    assert metadata_dict['Measurement phase [liquid/gas]'] == 'gas', \
    f"Expected measurement phase 'gas', but got '{metadata_dict['Measurement phase [liquid/gas]']}'"

    file_H2 = directory / metadata_dict['File name H2']
    raw_data_H2 = reading_H2_file(file_H2, mode = 'gas')

    return raw_data_H2

def processing_function_H2_gas(raw_data_dict: dict, metadata_dict : dict) -> dict:
    '''
    Processes raw H2 gas phase data.
    Assumes that raw data is provided in the unit Pa[H2]

    Parameters
    ----------
    raw_data_dict : dict
        Dictionary containing the raw data, as returned by the raw data reading function.
    metadata_dict : dict
        Dictionary containing the metadata, as returned by the metadata retrieval function.

    Returns
    -------
    processed_H2 : dict
        Dictionary containing the processed data and max rate, as returned by the processing function.
    '''

    data_quantity = convert_Pa_to_mol(raw_data_dict['measurement_raw'],
                                      gas_phase_volume_ml = metadata_dict['Gas phase volume [mL]'],
                                      temperature_celsius = raw_data_dict['temperature'])

    time_quantity = Quantity(raw_data_dict['time_s'], 's')

    processed_H2 = processing_data(
        time = time_quantity,
        data = data_quantity,
        start = Quantity(metadata_dict['Unisense Irradiation start [s]'], 's'),
        end = Quantity(metadata_dict['Unisense Irradiation end [s]'], 's'),
        metadata_dict = metadata_dict,
        electron_transfer_per_reaction = 2,  # H2 evolution involves 2 electrons
    )

    return processed_H2

def testing():

    import pandas as pd
    from pykes_o2_h2_app.data_parsing.general_processing_functions import metadata_retrival_function
    import pprint as pp
    import matplotlib.pyplot as plt


    overview_df = pd.read_excel('Untracked/data/H2_gas/EA-613_Metadata_Placeholder.xlsx', sheet_name = 'Sheet1')

    metadata_dict = metadata_retrival_function('EA-613', overview_df)
    raw_data_dict = raw_data_reading_function_H2_gas(Path('Untracked/data/H2_gas/'), metadata_dict)
    processed_data_dict = processing_function_H2_gas(raw_data_dict, metadata_dict)

    plt.plot(raw_data_dict['time_s'], raw_data_dict['measurement_raw'])
    #plt.plot(processed_data_dict['time_reaction_s'], processed_data_dict['data_reaction_umol'])
    # plt.plot(processed_data_dict['time_reaction_s'], processed_data_dict['smoothed_gaussian_umol'], 'o-')
    plt.plot(processed_data_dict['time_reaction_s'], processed_data_dict['rate_gaussian_umol_s'])
    plt.plot(processed_data_dict['max_rate_time_s'], processed_data_dict['max_rate_umol_s'], 'ro')

    pp.pprint(processed_data_dict)

    plt.show()




if __name__ == "__main__":
    testing()