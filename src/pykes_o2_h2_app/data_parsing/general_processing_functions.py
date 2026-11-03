import numpy as np
from scipy.ndimage import median_filter

from pyKES.utilities.offset_correction import offset_correction
from pyKES.utilities.unit_handler import Quantity
from pyKES.utilities.max_rate import extract_max_rate
from pyKES.utilities.calculate_efficiency import calculate_apparent_quantum_yield, light_to_hydrogen_efficiency

from pykes_o2_h2_app.parameters import PROCESSING_PARAMETERS

UNIVERSAL_GAS_CONSTANT = 8.31446261815324 # m3 * Pa / (K * mol)

# -----------------------------------------------------------------------------
# Baseline correction
# -----------------------------------------------------------------------------

# Shortest accepted dark period for the baseline fit. Without a dark period the
# leakage, and with it the validity of the experiment, cannot be judged.
MINIMUM_BASELINE_DURATION_S = 60

# Converts a median absolute deviation into a standard deviation (Gaussian noise)
MAD_TO_STANDARD_DEVIATION = 1.4826

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

def convert_vol_percent_to_Pa(data_vol_percent: np.ndarray,
                              pressure_mbar: float = 1013.25):

    '''
    Convert gas phase measurement in vol% to Pa.
    
    Parameters
    ----------
    data_vol_percent : np.ndarray
        Gas phase measurement in vol%.
    pressure_mbar : float, optional
        Pressure in mbar. Default is 1013.25 hPa/mbar (standard atmospheric pressure).
    
    Returns
    -------
    data_pa : np.ndarray
        Gas phase measurement in Pa.
    '''

    data_hPa = data_vol_percent / 100 * pressure_mbar  # Convert vol% to hPa
    data_quantity = Quantity(data_hPa, 'hPa')  # Create a Quantity object in hPa

    return data_quantity.unit['Pa']

def convert_Pa_to_mol(data_pa: np.ndarray,
                      gas_phase_volume_ml: float,
                      temperature_celsius: float | np.ndarray):
    '''
    Convert gas phase measurement in Pa to mol.

    Parameters
    ----------
    data : np.ndarray
        Gas phase measurement in Pa.
    gas_phase_volume : float
        Gas phase volume in mL.
    temperature : float or np.ndarray
        Temperature in Celsius.

    Returns
    -------
    amount : Quantity
        Amount of gas (quantity object, substance)
    '''

    data_quantity = Quantity(data_pa, 'Pa')
    gas_phase_volume_quantity = Quantity(gas_phase_volume_ml, 'mL')
    temperature_quantity = Quantity(temperature_celsius, 'degC')

    amount = Quantity(data_quantity.unit['Pa'] 
                      * gas_phase_volume_quantity.unit['m3']
                      / (UNIVERSAL_GAS_CONSTANT
                         * temperature_quantity.unit['K']
                         ),
                      'mol')
                        
    return amount

def convert_umol_L_to_mol(data_umol_L: np.ndarray,
                          liquid_phase_volume_ml: float):
    '''
    Convert liquid phase measurement in umol/L to mol.

    Parameters
    ----------
    data_umol_L : np.ndarray
        Liquid phase measurement in umol/L.
    liquid_phase_volume_ml : float
        Liquid phase volume in mL.
    
    Returns
    -------
    amount : Quantity
        Amount of substance (quantity object, substance)
    '''

    data_quantity = Quantity(data_umol_L, 'umol/L')
    liquid_phase_volume_quantity = Quantity(liquid_phase_volume_ml, 'mL')

    amount = Quantity(data_quantity.unit['umol/L']
                      * liquid_phase_volume_quantity.unit['L'],
                      'umol')

    return amount

def calculate_efficiency(metadata_dict: dict, 
                         reaction_rate: Quantity,
                         electron_transfer_per_reaction: int) -> Quantity:
    '''
    Calculate the apparent quantum yield and light-to-hydrogen efficiency 
    based on the reaction rate and metadata from the overview sheet.

    Parameters
    ----------
    metadata_dict : dict
        Metadata of the experiment, as returned by the metadata retrieval function.
    reaction_rate : Quantity
        The reaction rate (Quantity, substance / time)

    Returns
    -------
    apparent_quantum_yield : Quantity
        The apparent quantum yield (Quantity, dimensionless)
    lth_efficiency : Quantity
        The light-to-hydrogen efficiency (Quantity, dimensionless)
    '''

    apparent_quantum_yield = Quantity(0, '-')
    lth_efficiency = Quantity(0, '-')

    total_irradiance = Quantity(metadata_dict['Irradiance A [mW/cm2]']
                                + metadata_dict['Irradiance B [mW/cm2]'], 
                                'mW/cm2')

    if "Irradiated area [cm2]" in metadata_dict:
        lth_efficiency = light_to_hydrogen_efficiency(
                                        Quantity(metadata_dict['Irradiated area [cm2]'], 'cm2'),
                                        total_irradiance,
                                        reaction_rate,
                                        electron_transfer_per_reaction = electron_transfer_per_reaction)

    if "Irradiated area [cm2]" in metadata_dict and "Fraction of photons reaching inside [-]" in metadata_dict:
        apparent_quantum_yield = calculate_apparent_quantum_yield(
                                    Quantity(metadata_dict['Irradiation wavelength A [nm]'], 'nm'),
                                    Quantity(metadata_dict['Irradiated area [cm2]'], 'cm2'),
                                    Quantity(metadata_dict['Irradiance A [mW/cm2]'], 'mW/cm2'),
                                    reaction_rate,
                                    Quantity(metadata_dict['Fraction of photons reaching inside [-]'], '-'),
                                    electron_transfer_per_reaction = electron_transfer_per_reaction)

    return apparent_quantum_yield, lth_efficiency

def fit_line(time_s: np.ndarray,
             data: np.ndarray,
             start_s: float,
             end_s: float) -> tuple:
    '''
    Fits a straight line to the data points within a time window.

    Parameters
    ----------
    time_s : np.ndarray
        Time of each data point in s.
    data : np.ndarray
        Data points.
    start_s : float
        Window start in s (inclusive).
    end_s : float
        Window end in s (exclusive).

    Returns
    -------
    slope : float
        Slope in data units per s.
    intercept : float
        Value of the line at time zero.
    '''

    in_window = (time_s >= start_s) & (time_s < end_s)
    slope, intercept = np.polyfit(time_s[in_window], data[in_window], 1)

    return slope, intercept

def remove_spikes(data: np.ndarray) -> tuple:
    '''
    Replaces spikes (e.g. from touching the setup) by the running median.

    A point is a spike when it deviates from the median of the points around
    it by more than the spike threshold in noise standard deviations. The
    noise is the larger of two robust estimates, from the deviations and from
    the point-to-point steps; the latter keeps smooth traces, which follow
    their running median exactly, from a zero noise estimate.

    Parameters
    ----------
    data : np.ndarray
        Data points.

    Returns
    -------
    despiked_data : np.ndarray
        Data points with spikes replaced by the running median.
    is_spike : np.ndarray
        True for every replaced data point.
    '''

    parameters = PROCESSING_PARAMETERS['processing_parameters']
    running_median = median_filter(data, size = parameters['spike_window'], mode = 'nearest')
    deviation = data - running_median
    steps = np.diff(data)

    noise = MAD_TO_STANDARD_DEVIATION * max(np.median(np.abs(deviation)),
                                            np.median(np.abs(steps - np.median(steps))) / np.sqrt(2))
    is_spike = np.abs(deviation) > parameters['spike_threshold'] * noise

    return np.where(is_spike, running_median, data), is_spike

def determine_baseline_window(irradiation_start_s: float) -> tuple:
    '''
    Determines the dark period before irradiation used for the baseline fit.

    The window skips the sensor settling after the log start and ends shortly
    before irradiation start; both margins are set in PROCESSING_PARAMETERS.

    Parameters
    ----------
    irradiation_start_s : float
        Irradiation start in s after the log start.

    Returns
    -------
    start_s : float
        Window start in s.
    end_s : float
        Window end in s.
    '''

    parameters = PROCESSING_PARAMETERS['processing_parameters']
    start_s = parameters['baseline_start']
    end_s = irradiation_start_s - parameters['baseline_end_margin']

    if end_s - start_s < MINIMUM_BASELINE_DURATION_S:
        raise ValueError(f"Baseline window {start_s:g}-{end_s:g} s is shorter than {MINIMUM_BASELINE_DURATION_S} s: "
                         f"irradiation start at {irradiation_start_s:g} s leaves too little dark period "
                         f"to determine the leakage baseline.")

    return start_s, end_s

def measure_baseline_curvature(time_s: np.ndarray,
                               data: np.ndarray,
                               start_s: float,
                               end_s: float) -> float:
    '''
    Measures how much the baseline slope changes within the baseline window.

    A leakage that speeds up or slows down cannot be extrapolated linearly
    into the irradiation period; the slope change between the two window
    halves quantifies this.

    Parameters
    ----------
    time_s : np.ndarray
        Time of each data point in s.
    data : np.ndarray
        Data points.
    start_s : float
        Baseline window start in s.
    end_s : float
        Baseline window end in s.

    Returns
    -------
    slope_change : float
        Slope of the second half minus slope of the first half, in data units per s.
    '''

    middle_s = (start_s + end_s) / 2
    slope_first_half, _ = fit_line(time_s, data, start_s, middle_s)
    slope_second_half, _ = fit_line(time_s, data, middle_s, end_s)

    return slope_second_half - slope_first_half

def check_baseline(curvature_percent: float,
                   spike_count: int = 0) -> str:
    '''
    Judges whether the baseline is straight enough for a linear correction.

    Parameters
    ----------
    curvature_percent : float
        Baseline slope change within the window in % of the maximum rate.
    spike_count : int
        Number of spike points removed from the baseline window.

    Returns
    -------
    verdict : str
        'OK' or 'Check baseline', followed by the curvature and, if any, the
        number of removed spike points.
    '''

    limit_percent = PROCESSING_PARAMETERS['processing_parameters']['baseline_curvature_limit']
    verdict = 'OK' if abs(curvature_percent) <= limit_percent else 'Check baseline'

    details = f"{curvature_percent:.1f} %"
    if spike_count:
        details += f", {spike_count} spike point{'s' if spike_count > 1 else ''} removed"

    return f"{verdict} ({details})"

def processing_data(time: Quantity,
                    data: Quantity,
                    start: Quantity,
                    end: Quantity,
                    metadata_dict: dict,
                    electron_transfer_per_reaction: int,) -> dict:
    '''
    Processing the data and determining the max rate

    A linear baseline fitted to the dark period before irradiation (leakage)
    is subtracted before the reaction window is cut out. Spikes are removed
    for the baseline fit only.

    Parameters
    ----------
    time : Quantity
        Time data (quantity object, time)
    data : Quantity
        Measurement data (quantity object, substance [mol])
    start : Quantity
        Start time of the reaction (quantity object, time)
    end : Quantity
        End time of the reaction (quantity object, time)
    metadata_dict : dict
        Metadata of the experiment, as returned by the metadata retrieval function.
    electron_transfer_per_reaction : int
        Number of electrons transferred per reaction (e.g., 4 for O2 evolution, 2 for H2 evolution)

    Returns
    -------
    processed_data_dict : dict
        Dictionary containing the processed data and max rate    
    '''

    if 'Offset' in metadata_dict:
        offset = Quantity(metadata_dict['Offset'], 's')
    else:
        offset = Quantity(PROCESSING_PARAMETERS['processing_parameters']['offset'], 's')

    time_s = time.unit['s']
    data_mol = data.unit['mol']

    baseline_start_s, baseline_end_s = determine_baseline_window(start.unit['s'])
    data_despiked_mol, is_spike = remove_spikes(data_mol)
    baseline_spike_count = np.count_nonzero(is_spike[(time_s >= baseline_start_s) & (time_s < baseline_end_s)])
    baseline_slope, baseline_intercept = fit_line(time_s, data_despiked_mol, baseline_start_s, baseline_end_s)
    baseline_mol = baseline_slope * time_s + baseline_intercept
    baseline_curvature = measure_baseline_curvature(time_s, data_despiked_mol, baseline_start_s, baseline_end_s)

    time_reaction, data_reaction = offset_correction(time_s,
                                                     data_mol - baseline_mol,
                                                     offset.unit['s'],
                                                     start.unit['s'],
                                                     end.unit['s'])

    time_reaction_quantity = Quantity(time_reaction, 's')
    data_reaction_quantity = Quantity(data_reaction, 'mol')

    result = extract_max_rate(time_reaction_quantity,
                              data_reaction_quantity)

    apparent_quantum_yield, lth_efficiency = calculate_efficiency(metadata_dict, 
                                                                  result.max_rate,
                                                                  electron_transfer_per_reaction)

    liquid_volume = Quantity(metadata_dict['Liquid phase volume [mL]'], 'mL')
    concentration = Quantity(metadata_dict['Catalyst concentration [g/L]'], 'g/L')
    catalyst_mass = Quantity(liquid_volume.unit['L'] 
                             * concentration.unit['g/L'], 'g')

    mass_normalized_activity = Quantity(result.max_rate.unit['umol/h']
                                        / catalyst_mass.unit['g'], 
                                        'umol/g/h')

    baseline_curvature_percent = Quantity(baseline_curvature / result.max_rate.unit['mol/s'], '-').unit['%']

    processed_data_dict = {'time_reaction_s': time_reaction_quantity.unit['s'],
                           'time_unit': 's',
                           'data_reaction_umol': data_reaction_quantity.unit['umol'],
                           'data_unit': 'umol',
                           'smoothed_gaussian_umol': result.smooth.unit['umol'],
                           'smoothed_gaussian_unit': 'umol',
                           'rate_gaussian_umol_s': result.rate.unit['umol/s'],
                           'rate_gaussian_unit': 'umol/s',
                           'max_rate_umol_s': result.max_rate.unit['umol/s'],
                           'max_rate_unit': 'umol/s',
                           'max_rate_crosscheck_umol_s': result.max_rate_crosscheck.unit['umol/s'],
                           'max_rate_crosscheck_unit': 'umol/s',
                           'max_rate_time_s': result.t_max_rate.unit['s'],
                           'max_rate_time_unit': 's',
                           'apparent_quantum_yield': apparent_quantum_yield.unit['%'],
                           'apparent_quantum_yield_unit': '%',
                           'light_to_hydrogen_efficiency': lth_efficiency.unit['%'],
                           'light_to_hydrogen_efficiency_unit': '%',
                           'mass_normalized_activity': mass_normalized_activity.unit['umol/g/h'],
                           'mass_normalized_activity_unit': 'umol/g/h',
                           'data_umol': data.unit['umol'],
                           'baseline_umol': Quantity(baseline_mol, 'mol').unit['umol'],
                           'baseline_slope_umol_s': Quantity(baseline_slope, 'mol/s').unit['umol/s'],
                           'baseline_slope_unit': 'umol/s',
                           'baseline_curvature_percent': baseline_curvature_percent,
                           'baseline_curvature_unit': '%',
                           'baseline_check': check_baseline(baseline_curvature_percent, baseline_spike_count),
                           }

    return processed_data_dict