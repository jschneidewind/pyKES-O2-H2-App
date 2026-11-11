from pathlib import Path

import numpy as np
import pandas as pd

from pykes_o2_h2_app.data_parsing.raw_data_reading_functions import reading_O2_file

# -----------------------------------------------------------------------------
# Synthetic export of a Workbench 'Recalculate Oxygen' process step
# -----------------------------------------------------------------------------

# Recalculated O2 at 1 Hz, PT100 temperature at 2 Hz as in AE-918
O2_SAMPLES = 20
O2_TIME_STEP_S = 1.0
TEMPERATURE_TIME_STEP_S = 0.5

O2_RATE_VOL_PERCENT_S = 0.001

# Temperature ramp, so pairing the rows instead of the times gives wrong values
TEMPERATURE_START_CELSIUS = 20
TEMPERATURE_RAMP_CELSIUS_S = 0.1

def write_recalculated_O2_file(file_path: Path) -> np.ndarray:
    '''
    Writes an O2 trace in the layout of a Workbench 'Recalculate Oxygen' export.

    Parameters
    ----------
    file_path : Path
        Target file.

    Returns
    -------
    time_s : np.ndarray
        Times of the O2 samples.
    '''

    time_s = np.arange(O2_SAMPLES) * O2_TIME_STEP_S
    temperature_time_s = np.arange(2 * O2_SAMPLES) * TEMPERATURE_TIME_STEP_S

    # The O2 channel runs out of samples halfway down the table, leaving empty cells
    def pad(values: np.ndarray) -> np.ndarray:
        return np.concatenate([values, np.full(temperature_time_s.size - values.size, np.nan)])

    table = pd.DataFrame({
        'Date [ P1]': pad(np.zeros(O2_SAMPLES)),
        ' dt (s) [ P1]': pad(time_s),
        'Pressure (mbar) [ P1]': pad(np.full(O2_SAMPLES, 1010.0)),
        'Date [ T1]': '05-11-2026',
        ' dt (s) [ T1]': temperature_time_s,
        'Sample Temp. (°C) [ T1]': TEMPERATURE_START_CELSIUS + TEMPERATURE_RAMP_CELSIUS_S * temperature_time_s,
        'Date [P1 Recalc O2]': pad(np.zeros(O2_SAMPLES)),
        ' dt (s) [P1 Recalc O2]': pad(time_s),
        '%O2 [P1 Recalc O2]': pad(O2_RATE_VOL_PERCENT_S * time_s),
    }).to_csv(sep = '\t', index = False)

    file_path.write_text('#--- Process Step ---\n#Recalculate Oxygen [P1]\n' + table, encoding = 'ISO8859')

    return time_s

def test_recalculated_O2_export_is_read_on_the_O2_times(tmp_path):
    file_path = tmp_path / 'synthetic-recalculated-O2.txt'
    time_s = write_recalculated_O2_file(file_path)

    raw_data_dict = reading_O2_file(file_path, mode = 'gas')

    np.testing.assert_allclose(raw_data_dict['time_s'], time_s)
    np.testing.assert_allclose(raw_data_dict['measurement_raw'], O2_RATE_VOL_PERCENT_S * time_s)
    np.testing.assert_allclose(raw_data_dict['temperature'],
                               TEMPERATURE_START_CELSIUS + TEMPERATURE_RAMP_CELSIUS_S * time_s)
    assert raw_data_dict['measurement_unit'] == 'vol%'
