import numpy as np
from scipy.signal import savgol_filter

from pyKES.utilities.find_nearest import find_nearest
from pyKES.utilities.time_series_resampling import resample_time_series
from pyKES.utilities.offset_correction import offset_correction

def metadata_retrival_function(experiment_name: str, 
                               overview_df):
    '''
    Given an experiment name and an overview DataFrame, retrieves the metadata for the specified experiment.
    Returns a dictionary containing the metadata.
    '''

    experiment_row = overview_df[overview_df['Experiment'] == experiment_name]
    
    if experiment_row.empty:
        raise ValueError(f"No experiment found with name: {experiment_name}")
    
    if len(experiment_row) > 1:
        raise ValueError(f"Multiple experiments found with name: {experiment_name}")
    
    metadata_dict = experiment_row.iloc[0].to_dict()
    metadata_dict['experiment_name'] = metadata_dict['Experiment']

    return metadata_dict


def convert_gases_to_mmol(data: np.ndarray,
                          gas_phase_volume: float,
                          H2: bool = False):
    '''
    data in vol% or Pa 
    Gas phase volume in mL.
    '''
    
    if H2 is True:
        NORMAL_PRESSURE = 1013.25
        data = data / NORMAL_PRESSURE # Convert from Pa to vol%
    
    MOLAR_VOLUME_STANRDARD_CONDITIONS = 24.465 # L/mol at 25C and 1 atm
    gas_L = data * (1/100) * gas_phase_volume * (1/1000) # Convert from vol% to L of gas
    gas_mol = gas_L / MOLAR_VOLUME_STANRDARD_CONDITIONS # Convert from L of gas to mol of gas

    gas_mmol = gas_mol * 1e3 # Convert from mol to mmol

    return gas_mmol

def processing_data(time: np.ndarray,
                    data: np.ndarray,
                    start: float,
                    end: float,
                    prefix: str,
                    offset: float,
                    savgol_window: int,
                    savgol_polyorder: int,
                    poly_order: int,
                    ):
    '''
    Processes the input data by performing offset correction, smoothing 
    of the data using a Savitzky-Golay filter, calculating the derivative of the smoothed data,
    fitting a polynomial to the reaction data, calculating the derivative of the polynomial fit,
    and finding the maximum rate of change from the polynomial fit derivative (max rate). 

    Returns a dictionary containing the processed data 
    '''

    time_reaction, data_reaction = offset_correction(time, data, offset, start, end)

    data_smoothed = savgol_filter(data_reaction, savgol_window, savgol_polyorder)
    data_diff = np.diff(data_smoothed) / np.diff(time_reaction)
    time_diff = time_reaction[1:]

    coeffs = np.polyfit(time_reaction, data_reaction, poly_order)
    data_poly_fit = np.polyval(coeffs, time_reaction)

    poly_fit_diff = np.diff(data_poly_fit) / np.diff(time_reaction)
    max_rate = np.max(poly_fit_diff)

    processed_data = {
        f'{prefix}_time_reaction': time_reaction,
        f'{prefix}_data_reaction': data_reaction,
        f'{prefix}_data_smoothed': data_smoothed,
        f'{prefix}_data_diff': data_diff,
        f'{prefix}_time_diff': time_diff,
        f'{prefix}_poly_fit': data_poly_fit,
        f'{prefix}_poly_fit_diff': poly_fit_diff,
        f'{prefix}_max_rate': max_rate,
    }

    return processed_data

