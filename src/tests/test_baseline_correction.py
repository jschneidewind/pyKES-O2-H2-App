import numpy as np
import pytest

from pykes_o2_h2_app.data_parsing.general_processing_functions import (
    determine_baseline_window,
    measure_baseline_curvature,
    check_baseline,
    get_baseline_window,
)
from pykes_o2_h2_app.data_parsing.processing_functions_O2_liquid import processing_function_O2_liquid

# -----------------------------------------------------------------------------
# Synthetic liquid-phase O2 experiment with leakage
# -----------------------------------------------------------------------------

# O2 evolution during irradiation and constant leakage throughout; the leak is
# a quarter of the evolution rate, as in AE-915
PRODUCTION_RATE_UMOL_L_S = 0.02
LEAKAGE_RATE_UMOL_L_S = 0.005

# Sensor settling after the log start, decayed before the baseline window starts
SETTLING_AMPLITUDE_UMOL_L = -0.5
SETTLING_TIME_CONSTANT_S = 30

TIME_STEP_S = 2
DURATION_S = 3000
IRRADIATION_START_S = 600
IRRADIATION_END_S = 2400

# White sensor noise and its seed, so the test is deterministic
NOISE_STANDARD_DEVIATION_UMOL_L = 0.02
RANDOM_SEED = 915

# Spike from touching the setup near the end of the baseline window, where it
# tilts a plain fit most: two samples about 1500 times the noise above the
# trace (like a 160 mV H2 spike in the liquid phase), then a short undershoot
SPIKE_START_S = 540
SPIKE_AMPLITUDE_UMOL_L = 30
SPIKE_SAMPLES = 2
UNDERSHOOT_AMPLITUDE_UMOL_L = -3
UNDERSHOOT_SAMPLES = 3

LIQUID_PHASE_VOLUME_ML = 30
MILLILITRES_PER_LITRE = 1000

# Tolerated deviation of the extracted rates from the true ones
RATE_RELATIVE_TOLERANCE = 0.05

# The discrete samples make the window halves only nearly symmetric
CURVATURE_RELATIVE_TOLERANCE = 0.01

def build_metadata() -> dict:
    '''
    Builds the overview row of the synthetic liquid-phase O2 experiment.

    Returns
    -------
    metadata_dict : dict
        Metadata as returned by the metadata retrieval function.
    '''

    return {
        'Liquid phase volume [mL]': LIQUID_PHASE_VOLUME_ML,
        'Catalyst concentration [g/L]': 0.5,
        'Irradiance A [mW/cm2]': 10,
        'Irradiance B [mW/cm2]': 0,
        'Pyroscience Irradiation start [s]': IRRADIATION_START_S,
        'Pyroscience Irradiation end [s]': IRRADIATION_END_S,
    }

def simulate_raw_data() -> dict:
    '''
    Simulates a PyroScience O2 trace with sensor settling, constant leakage and
    constant O2 evolution during irradiation.

    Returns
    -------
    raw_data_dict : dict
        Raw data as returned by the O2 raw data reading function.
    '''

    random_generator = np.random.default_rng(RANDOM_SEED)
    time_s = np.arange(0, DURATION_S, TIME_STEP_S, dtype = float)

    settling = SETTLING_AMPLITUDE_UMOL_L * np.exp(-time_s / SETTLING_TIME_CONSTANT_S)
    leakage = LEAKAGE_RATE_UMOL_L_S * time_s
    irradiated_time_s = np.clip(time_s - IRRADIATION_START_S, 0, IRRADIATION_END_S - IRRADIATION_START_S)
    noise = random_generator.normal(0, NOISE_STANDARD_DEVIATION_UMOL_L, time_s.size)

    return {
        'time_s': time_s,
        'time_unit': 's',
        'measurement_raw': settling + leakage + PRODUCTION_RATE_UMOL_L_S * irradiated_time_s + noise,
        'measurement_unit': 'umol/L',
    }

def convert_to_umol_s(rate_umol_L_s: float) -> float:
    '''
    Converts a concentration rate into an amount rate in the liquid phase.

    Parameters
    ----------
    rate_umol_L_s : float
        Concentration rate.

    Returns
    -------
    rate_umol_s : float
        Amount rate.
    '''

    return rate_umol_L_s * LIQUID_PHASE_VOLUME_ML / MILLILITRES_PER_LITRE

def test_linear_leakage_is_removed_from_the_rate():
    processed_data_dict = processing_function_O2_liquid(simulate_raw_data(), build_metadata())

    assert processed_data_dict['baseline_slope_umol_s'] == pytest.approx(convert_to_umol_s(LEAKAGE_RATE_UMOL_L_S),
                                                                         rel = RATE_RELATIVE_TOLERANCE)
    assert processed_data_dict['max_rate_umol_s'] == pytest.approx(convert_to_umol_s(PRODUCTION_RATE_UMOL_L_S),
                                                                   rel = RATE_RELATIVE_TOLERANCE)
    assert processed_data_dict['baseline_check'].startswith('OK')

def test_spike_in_dark_period_is_removed_from_the_baseline():
    raw_data_dict = simulate_raw_data()
    spike_start = int(SPIKE_START_S / TIME_STEP_S)
    undershoot_start = spike_start + SPIKE_SAMPLES
    raw_data_dict['measurement_raw'][spike_start:undershoot_start] += SPIKE_AMPLITUDE_UMOL_L
    raw_data_dict['measurement_raw'][undershoot_start:undershoot_start + UNDERSHOOT_SAMPLES] += UNDERSHOOT_AMPLITUDE_UMOL_L

    processed_data_dict = processing_function_O2_liquid(raw_data_dict, build_metadata())

    assert processed_data_dict['max_rate_umol_s'] == pytest.approx(convert_to_umol_s(PRODUCTION_RATE_UMOL_L_S),
                                                                   rel = RATE_RELATIVE_TOLERANCE)
    assert f"{SPIKE_SAMPLES + UNDERSHOOT_SAMPLES} spike points removed" in processed_data_dict['baseline_check']

def test_curvature_of_parabola_equals_window_length():
    # A line fitted to t^2 over symmetric samples has slope 2 * mean(t), so the
    # slope change between the halves equals the window length
    time_s = np.arange(0, DURATION_S, TIME_STEP_S, dtype = float)
    start_s, end_s = determine_baseline_window(IRRADIATION_START_S)

    curvature = measure_baseline_curvature(time_s, time_s ** 2, start_s, end_s)

    assert curvature == pytest.approx(end_s - start_s, rel = CURVATURE_RELATIVE_TOLERANCE)

def test_check_flags_only_curved_baselines():
    assert check_baseline(5.0).startswith('OK')
    assert check_baseline(-15.0).startswith('Check baseline')

def test_short_dark_period_is_rejected():
    with pytest.raises(ValueError, match = 'dark period'):
        determine_baseline_window(irradiation_start_s = 200)

# -----------------------------------------------------------------------------
# Operator-set baseline window
# -----------------------------------------------------------------------------

# Extra drift at the start of the dark period (e.g. a slow sensor recovery) that
# stops before irradiation, tilting the automatic window (180-570 s)
EXTRA_DRIFT_UMOL_L_S = 0.01
EXTRA_DRIFT_END_S = 360

# Operator windows: the undisturbed rest of the dark period before irradiation,
# and the dark period after it
WINDOW_BEFORE_IRRADIATION_S = (400, 570)
WINDOW_AFTER_IRRADIATION_S = (2450, 2990)

def with_baseline_window(start_s, end_s) -> dict:
    '''
    Builds the overview row of the synthetic experiment with an operator-set baseline window.
    '''

    return {**build_metadata(),
            'Pyroscience Baseline start [s]': start_s,
            'Pyroscience Baseline end [s]': end_s}

def simulate_raw_data_with_early_drift() -> dict:
    '''
    Simulates the synthetic experiment with an extra drift at the start of the dark period.
    '''

    raw_data_dict = simulate_raw_data()
    raw_data_dict['measurement_raw'] += EXTRA_DRIFT_UMOL_L_S * np.minimum(raw_data_dict['time_s'], EXTRA_DRIFT_END_S)

    return raw_data_dict

def test_operator_window_avoids_a_disturbed_dark_period():
    automatic = processing_function_O2_liquid(simulate_raw_data_with_early_drift(), build_metadata())
    operator = processing_function_O2_liquid(simulate_raw_data_with_early_drift(),
                                             with_baseline_window(*WINDOW_BEFORE_IRRADIATION_S))

    # The drift makes the automatic baseline wrong, which the operator window avoids
    assert automatic['baseline_slope_umol_s'] != pytest.approx(convert_to_umol_s(LEAKAGE_RATE_UMOL_L_S),
                                                               rel = RATE_RELATIVE_TOLERANCE)
    assert operator['baseline_slope_umol_s'] == pytest.approx(convert_to_umol_s(LEAKAGE_RATE_UMOL_L_S),
                                                              rel = RATE_RELATIVE_TOLERANCE)
    assert operator['max_rate_umol_s'] == pytest.approx(convert_to_umol_s(PRODUCTION_RATE_UMOL_L_S),
                                                        rel = RATE_RELATIVE_TOLERANCE)
    assert operator['baseline_window'] == '400-570 s (operator)'

def test_operator_window_may_follow_the_irradiation():
    processed_data_dict = processing_function_O2_liquid(simulate_raw_data(),
                                                        with_baseline_window(*WINDOW_AFTER_IRRADIATION_S))

    assert processed_data_dict['baseline_slope_umol_s'] == pytest.approx(convert_to_umol_s(LEAKAGE_RATE_UMOL_L_S),
                                                                         rel = RATE_RELATIVE_TOLERANCE)
    assert processed_data_dict['max_rate_umol_s'] == pytest.approx(convert_to_umol_s(PRODUCTION_RATE_UMOL_L_S),
                                                                   rel = RATE_RELATIVE_TOLERANCE)

def test_empty_window_cells_keep_the_automatic_window():
    processed_data_dict = processing_function_O2_liquid(simulate_raw_data(), with_baseline_window(np.nan, np.nan))

    assert processed_data_dict['baseline_window'] == '180-570 s (automatic)'

def test_window_overlapping_the_irradiation_is_rejected():
    with pytest.raises(ValueError, match = 'overlaps the irradiation'):
        processing_function_O2_liquid(simulate_raw_data(), with_baseline_window(500, 700))

def test_window_with_too_little_logged_data_is_rejected():
    with pytest.raises(ValueError, match = 'logged data'):
        processing_function_O2_liquid(simulate_raw_data(), with_baseline_window(2950, 3100))

def test_half_set_window_is_rejected():
    with pytest.raises(ValueError, match = 'Set both'):
        get_baseline_window(with_baseline_window(400, np.nan), 'Pyroscience')
