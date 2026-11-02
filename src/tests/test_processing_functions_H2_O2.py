from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pykes_o2_h2_app.data_parsing.processing_functions_H2_O2 import (
    raw_data_reading_function_H2_O2,
    processing_function_H2_O2,
)

# -----------------------------------------------------------------------------
# Synthetic combined experiment
# -----------------------------------------------------------------------------

# Concentration increase during irradiation, H2 at twice the O2 rate as in
# overall water splitting
RATES_UMOL_L_S = {'H2': 0.025, 'O2': 0.0125}

# Logging interval and duration shared by both sensors
TIME_STEP_S = 2
DURATION_S = 2400

IRRADIATION_START_S = 300
IRRADIATION_END_S = 2100

# White sensor noise and its seed, so the test is deterministic
NOISE_STANDARD_DEVIATION_UMOL_L = 0.02
RANDOM_SEED = 904

SAMPLE_TEMPERATURE_CELSIUS = 20
LIQUID_PHASE_VOLUME_ML = 30
MILLILITRES_PER_LITRE = 1000

H2_FILE_NAME = 'synthetic-H2.csv'
O2_FILE_NAME = 'synthetic-O2.txt'

# Tolerated deviation of the extracted maximum rate from the true constant rate
RATE_RELATIVE_TOLERANCE = 0.05

def build_metadata() -> dict:
    '''
    Builds the overview row of a liquid-phase combined H2 + O2 experiment.

    Returns
    -------
    metadata_dict : dict
        Metadata as returned by the metadata retrieval function.
    '''

    return {
        'Experiment': 'synthetic',
        'Measured Analyte [O2 or H2]': 'H2+O2',
        'Measurement phase [liquid/gas]': 'liquid',
        'File name H2': H2_FILE_NAME,
        'File name O2': O2_FILE_NAME,
        'Liquid phase volume [mL]': LIQUID_PHASE_VOLUME_ML,
        'Catalyst concentration [g/L]': 0.5,
        'Irradiance A [mW/cm2]': 10,
        'Irradiance B [mW/cm2]': 0,
        'Unisense Irradiation start [s]': IRRADIATION_START_S,
        'Unisense Irradiation end [s]': IRRADIATION_END_S,
        'Pyroscience Irradiation start [s]': IRRADIATION_START_S,
        'Pyroscience Irradiation end [s]': IRRADIATION_END_S,
    }

def simulate_concentration(time_s: np.ndarray, rate_umol_L_s: float, random_generator) -> np.ndarray:
    '''
    Simulates a concentration rising at a constant rate during irradiation only.

    Parameters
    ----------
    time_s : np.ndarray
        Measurement times.
    rate_umol_L_s : float
        Concentration increase during irradiation.
    random_generator : np.random.Generator
        Source of the sensor noise.

    Returns
    -------
    concentration_umol_L : np.ndarray
        Noisy concentration trace.
    '''

    irradiated_time_s = np.clip(time_s - IRRADIATION_START_S, 0, IRRADIATION_END_S - IRRADIATION_START_S)
    noise = random_generator.normal(0, NOISE_STANDARD_DEVIATION_UMOL_L, time_s.size)

    return rate_umol_L_s * irradiated_time_s + noise

def write_H2_file(file_path: Path, time_s: np.ndarray, concentration_umol_L: np.ndarray):
    '''
    Writes a trace in the Unisense UniAmp CSV layout.

    Parameters
    ----------
    file_path : Path
        Target file.
    time_s : np.ndarray
        Measurement times.
    concentration_umol_L : np.ndarray
        H2 concentration.
    '''

    pd.DataFrame({
        'Time since start (s)': time_s,
        'Sensor 1 - H2 (μmol/L)': concentration_umol_L,
        'Sensor 2 - TEMP-UNIAMP (°C)': SAMPLE_TEMPERATURE_CELSIUS,
    }).to_csv(file_path, sep = ';', index = False)

def write_O2_file(file_path: Path, time_s: np.ndarray, concentration_umol_L: np.ndarray):
    '''
    Writes a trace in the PyroScience Workbench TXT layout.

    Parameters
    ----------
    file_path : Path
        Target file.
    time_s : np.ndarray
        Measurement times.
    concentration_umol_L : np.ndarray
        O2 concentration.
    '''

    table = pd.DataFrame({
        'Date [A Ch.1 Main]': '02-11-2026',
        ' dt (s) [A Ch.1 Main]': time_s,
        'Oxygen (µmol/L) [A Ch.1 Main]': concentration_umol_L,
        'Sample Temp. (°C) [A Ch.1 CompT]': SAMPLE_TEMPERATURE_CELSIUS,
    }).to_csv(sep = '\t', index = False)

    file_path.write_text('#Synthetic PyroScience log\n' + table, encoding = 'ISO8859')

def write_raw_data_files(directory: Path):
    '''
    Writes the H2 and O2 files of the synthetic experiment.

    Parameters
    ----------
    directory : Path
        Target directory.
    '''

    random_generator = np.random.default_rng(RANDOM_SEED)
    time_s = np.arange(0, DURATION_S, TIME_STEP_S, dtype = float)

    write_H2_file(directory / H2_FILE_NAME, time_s,
                  simulate_concentration(time_s, RATES_UMOL_L_S['H2'], random_generator))
    write_O2_file(directory / O2_FILE_NAME, time_s,
                  simulate_concentration(time_s, RATES_UMOL_L_S['O2'], random_generator))

def test_combined_experiment_recovers_both_rates(tmp_path):
    write_raw_data_files(tmp_path)
    metadata_dict = build_metadata()

    raw_data_dict = raw_data_reading_function_H2_O2(tmp_path, metadata_dict)
    processed_data_dict = processing_function_H2_O2(raw_data_dict, metadata_dict)

    for analyte, rate_umol_L_s in RATES_UMOL_L_S.items():
        expected_rate_umol_s = rate_umol_L_s * LIQUID_PHASE_VOLUME_ML / MILLILITRES_PER_LITRE
        assert processed_data_dict[analyte]['max_rate_umol_s'] == pytest.approx(expected_rate_umol_s,
                                                                                 rel = RATE_RELATIVE_TOLERANCE)

def test_combined_reader_rejects_single_analyte_rows(tmp_path):
    metadata_dict = build_metadata() | {'Measured Analyte [O2 or H2]': 'H2'}

    with pytest.raises(AssertionError, match = r"H2\+O2"):
        raw_data_reading_function_H2_O2(tmp_path, metadata_dict)
