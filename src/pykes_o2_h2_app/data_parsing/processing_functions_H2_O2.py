from pathlib import Path

from pykes_o2_h2_app.data_parsing.raw_data_reading_functions import reading_H2_file, reading_O2_file
from pykes_o2_h2_app.data_parsing.processing_functions_H2_liquid import processing_function_H2_liquid
from pykes_o2_h2_app.data_parsing.processing_functions_O2_liquid import processing_function_O2_liquid
from pykes_o2_h2_app.data_parsing.processing_functions_H2_gas import processing_function_H2_gas
from pykes_o2_h2_app.data_parsing.processing_functions_O2_gas import processing_function_O2_gas

# -----------------------------------------------------------------------------
# Combined H2 + O2 experiments
# -----------------------------------------------------------------------------

# Value of the 'Measured Analyte [O2 or H2]' column for an overview row whose
# H2 and O2 traces were recorded during the same experiment
COMBINED_ANALYTE = 'H2+O2'

# Single-analyte pipelines reused for each trace, selected by measurement phase
PROCESSING_FUNCTIONS = {
    'H2': {'liquid': processing_function_H2_liquid, 'gas': processing_function_H2_gas},
    'O2': {'liquid': processing_function_O2_liquid, 'gas': processing_function_O2_gas},
}

def get_measurement_phase(metadata_dict: dict, analyte: str) -> str:
    '''
    Returns the measurement phase of one trace of a combined experiment.

    Both traces currently share the 'Measurement phase [liquid/gas]' column.
    Mixed phases (e.g. H2 liquid, O2 gas) only require reading a per-analyte
    phase column here.

    Parameters
    ----------
    metadata_dict : dict
        Dictionary containing the metadata, as returned by the metadata retrieval function.
    analyte : str
        Analyte of the trace, 'H2' or 'O2'.

    Returns
    -------
    phase : str
        Measurement phase, 'liquid' or 'gas'.
    '''

    return metadata_dict['Measurement phase [liquid/gas]']

def raw_data_reading_function_H2_O2(directory: Path, metadata_dict: dict) -> dict:
    '''
    Reads the raw H2 and O2 data of a combined experiment.

    Parameters
    ----------
    directory : Path
        Path to the directory containing both raw data files.
    metadata_dict : dict
        Dictionary containing the metadata, as returned by the metadata retrieval function.

    Returns
    -------
    raw_data_dict : dict
        Raw data of both traces under the keys 'H2' and 'O2', each as returned
        by the single-analyte raw data reading functions.
    '''

    assert metadata_dict['Measured Analyte [O2 or H2]'] == COMBINED_ANALYTE, \
    f"Expected measured analyte '{COMBINED_ANALYTE}', but got '{metadata_dict['Measured Analyte [O2 or H2]']}'"

    raw_data_H2 = reading_H2_file(directory / metadata_dict['File name H2'],
                                  mode = get_measurement_phase(metadata_dict, 'H2'))
    raw_data_O2 = reading_O2_file(directory / metadata_dict['File name O2'],
                                  mode = get_measurement_phase(metadata_dict, 'O2'))

    return {'H2': raw_data_H2, 'O2': raw_data_O2}

def processing_function_H2_O2(raw_data_dict: dict, metadata_dict: dict) -> dict:
    '''
    Processes the H2 and O2 traces of a combined experiment with the
    single-analyte pipelines matching their measurement phase.

    Parameters
    ----------
    raw_data_dict : dict
        Raw data of both traces, as returned by raw_data_reading_function_H2_O2.
    metadata_dict : dict
        Dictionary containing the metadata, as returned by the metadata retrieval function.

    Returns
    -------
    processed_data_dict : dict
        Processed data of both traces under the keys 'H2' and 'O2', each as
        returned by the single-analyte processing functions.
    '''

    processing_function_H2 = PROCESSING_FUNCTIONS['H2'][get_measurement_phase(metadata_dict, 'H2')]
    processing_function_O2 = PROCESSING_FUNCTIONS['O2'][get_measurement_phase(metadata_dict, 'O2')]

    return {'H2': processing_function_H2(raw_data_dict['H2'], metadata_dict),
            'O2': processing_function_O2(raw_data_dict['O2'], metadata_dict)}

def test_function():
    '''
    Processes the AE-904 example (one H2 and one O2 file in a single overview
    row) and prints the maximum rate of both traces.
    '''

    import pandas as pd
    from pykes_o2_h2_app.data_parsing.general_processing_functions import metadata_retrival_function

    overview_df = pd.read_excel('Untracked/data/H2_O2/AE-904.xlsx', sheet_name = 'Sheet1')

    metadata_dict = metadata_retrival_function('AE-904', overview_df)
    raw_data_dict = raw_data_reading_function_H2_O2(Path('Untracked/data/H2_O2/'), metadata_dict)
    processed_data_dict = processing_function_H2_O2(raw_data_dict, metadata_dict)

    for analyte, processed_data in processed_data_dict.items():
        print(f"{analyte}: max rate {processed_data['max_rate_umol_s']:.4g} umol/s")

if __name__ == "__main__":
    test_function()
