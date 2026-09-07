from pathlib import Path

from pyKES.utilities.unit_handler import Quantity

from pykes_o2_h2_app.data_parsing.raw_data_reading_functions import reading_O2_file
from pykes_o2_h2_app.data_parsing.general_processing_functions import processing_data, convert_umol_L_to_mol

def raw_data_reading_function_O2_liquid(directory: Path, metadata_dict):
    '''
    Reads raw O2 liquid phase data from a file.

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
    assert metadata_dict['Measured Analyte [O2 or H2]'] == 'O2', \
    f"Expected measured analyte 'O2', but got '{metadata_dict['Measured Analyte [O2 or H2]']}'"
    assert metadata_dict['Measurement phase [liquid/gas]'] == 'liquid', \
    f"Expected measurement phase 'liquid', but got '{metadata_dict['Measurement phase [liquid/gas]']}'"

    file_O2 = directory / metadata_dict['File name O2']
    raw_data_O2 = reading_O2_file(file_O2, mode = 'liquid')

    return raw_data_O2

def processing_function_O2_liquid(raw_data_dict, metadata_dict):
    '''
    Processes raw O2 liquid phase data.
    Assumes that raw data is provided in the unit umol[O2]/L
    
    Parameters
    ----------
    raw_data_dict : dict
        Dictionary containing the raw data, as returned by the raw data reading function.
    metadata_dict : dict
        Dictionary containing the metadata, as returned by the metadata retrieval function.

    Returns
    -------
    processed_O2 : dict
        Dictionary containing the processed data and max rate, as returned by the processing function.
    '''

    data_quantity = convert_umol_L_to_mol(raw_data_dict['measurement_raw'],
                                          liquid_phase_volume_ml = metadata_dict['Liquid phase volume [mL]'])
    time_quantity = Quantity(raw_data_dict['time_s'], 's')

    processed_O2 = processing_data(
        time = time_quantity,
        data = data_quantity,
        start = Quantity(metadata_dict['Pyroscience Irradiation start [s]'], 's'),
        end = Quantity(metadata_dict['Pyroscience Irradiation end [s]'], 's'),
        metadata_dict = metadata_dict,
        electron_transfer_per_reaction = 4,  # O2 evolution involves 4 electrons
    )

    return processed_O2

def testing():

    import pandas as pd
    from pykes_o2_h2_app.data_parsing.general_processing_functions import metadata_retrival_function
    import pprint as pp
    import matplotlib.pyplot as plt


    overview_df = pd.read_excel('Untracked/data/O2_liquid/SrTiO3_Photocatalysis_VSA-118.xlsx', sheet_name = 'Sheet1')

    metadata_dict = metadata_retrival_function('VSA-118', overview_df)
    raw_data_dict = raw_data_reading_function_O2_liquid(Path('Untracked/data/O2_liquid/'), metadata_dict)
    processed_data_dict = processing_function_O2_liquid(raw_data_dict, metadata_dict)

    plt.plot(raw_data_dict['time_s'], raw_data_dict['measurement_raw'])

    #plt.plot(processed_data_dict['time_reaction_s'], processed_data_dict['rate_gaussian_umol_s'])
    #plt.plot(processed_data_dict['max_rate_time_s'], processed_data_dict['max_rate_umol_s'], 'ro')
    plt.show()

    pp.pprint(processed_data_dict)

if __name__ == "__main__":
    testing()