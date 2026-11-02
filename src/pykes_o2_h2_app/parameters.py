# Parameters used during data processing
PROCESSING_PARAMETERS = {
    'processing_parameters': { 
                        'offset': 60,
                    },
}

# Mapping of metadata columns to dataset groups (for visualisation)
GROUP_MAPPING = {
        'Reference': None,
        }

# Instruction for time series plotting (mapping of plot labels to dataset paths)
# and kinetic results plotting (mapping of result labels to dataset paths and units)
PLOTTING_INSTRUCTIONS = {
    'time_series_instructions': {
                    'Raw': {
                        'x': 'raw_data/time_s',
                        'y': 'raw_data/measurement_raw',
                        'unit_x': 'raw_data/time_unit',
                        'unit_y': 'raw_data/measurement_unit',
                        },
                    'Reaction': {
                        'x': 'processed_data/time_reaction_s',
                        'y': 'processed_data/data_reaction_umol',
                        'unit_x': 'processed_data/time_unit',
                        'unit_y': 'processed_data/data_unit',
                        },
                    'Smoothed': {
                        'x': 'processed_data/time_reaction_s',
                        'y': 'processed_data/smoothed_gaussian_umol',
                        'unit_x': 'processed_data/time_unit',
                        'unit_y': 'processed_data/smoothed_gaussian_unit',
                        },
                    'Rate': {
                        'x': 'processed_data/time_reaction_s',
                        'y': 'processed_data/rate_gaussian_umol_s',
                        'x_point': 'processed_data/max_rate_time_s',
                        'y_point': 'processed_data/max_rate_umol_s',
                        'unit_x': 'processed_data/time_unit',
                        'unit_y': 'processed_data/rate_gaussian_unit',
                        },
                    # Combined 'H2+O2' experiments keep each trace under its analyte
                    'Raw (H2)': {
                        'x': 'raw_data/H2/time_s',
                        'y': 'raw_data/H2/measurement_raw',
                        'unit_x': 'raw_data/H2/time_unit',
                        'unit_y': 'raw_data/H2/measurement_unit',
                        },
                    'Raw (O2)': {
                        'x': 'raw_data/O2/time_s',
                        'y': 'raw_data/O2/measurement_raw',
                        'unit_x': 'raw_data/O2/time_unit',
                        'unit_y': 'raw_data/O2/measurement_unit',
                        },
                    'Reaction (H2)': {
                        'x': 'processed_data/H2/time_reaction_s',
                        'y': 'processed_data/H2/data_reaction_umol',
                        'unit_x': 'processed_data/H2/time_unit',
                        'unit_y': 'processed_data/H2/data_unit',
                        },
                    'Reaction (O2)': {
                        'x': 'processed_data/O2/time_reaction_s',
                        'y': 'processed_data/O2/data_reaction_umol',
                        'unit_x': 'processed_data/O2/time_unit',
                        'unit_y': 'processed_data/O2/data_unit',
                        },
                    'Smoothed (H2)': {
                        'x': 'processed_data/H2/time_reaction_s',
                        'y': 'processed_data/H2/smoothed_gaussian_umol',
                        'unit_x': 'processed_data/H2/time_unit',
                        'unit_y': 'processed_data/H2/smoothed_gaussian_unit',
                        },
                    'Smoothed (O2)': {
                        'x': 'processed_data/O2/time_reaction_s',
                        'y': 'processed_data/O2/smoothed_gaussian_umol',
                        'unit_x': 'processed_data/O2/time_unit',
                        'unit_y': 'processed_data/O2/smoothed_gaussian_unit',
                        },
                    'Rate (H2)': {
                        'x': 'processed_data/H2/time_reaction_s',
                        'y': 'processed_data/H2/rate_gaussian_umol_s',
                        'x_point': 'processed_data/H2/max_rate_time_s',
                        'y_point': 'processed_data/H2/max_rate_umol_s',
                        'unit_x': 'processed_data/H2/time_unit',
                        'unit_y': 'processed_data/H2/rate_gaussian_unit',
                        },
                    'Rate (O2)': {
                        'x': 'processed_data/O2/time_reaction_s',
                        'y': 'processed_data/O2/rate_gaussian_umol_s',
                        'x_point': 'processed_data/O2/max_rate_time_s',
                        'y_point': 'processed_data/O2/max_rate_umol_s',
                        'unit_x': 'processed_data/O2/time_unit',
                        'unit_y': 'processed_data/O2/rate_gaussian_unit',
                        },
                },

    'kinetic_results_instructions': {
        'Max rate': {'Value': 'processed_data/max_rate_umol_s',
                              'Unit': 'Rate / umol/s'},
        'Max rate (H2)': {'Value': 'processed_data/H2/max_rate_umol_s',
                          'Unit': 'Rate / umol/s'},
        'Max rate (O2)': {'Value': 'processed_data/O2/max_rate_umol_s',
                          'Unit': 'Rate / umol/s'},
    },

    'results_table_instructions': {
        'Max. rate (umol/s)': {'result': 'processed_data/max_rate_umol_s'},
        'Max. rate crosscheck (umol/s)': {'result': 'processed_data/max_rate_crosscheck_umol_s'},
        'Apparent quantum yield (%)': {'result': 'processed_data/apparent_quantum_yield',
                                       'format': '.5f'},
        'Light-to-hydrogen efficiency (%)': {'result': 'processed_data/light_to_hydrogen_efficiency',
                                             'format': '.5f'},
        'Mass normalized activity (umol/g/h)': {'result': 'processed_data/mass_normalized_activity',
                                                'format': '.5f'},
        'H2 max. rate (umol/s)': {'result': 'processed_data/H2/max_rate_umol_s'},
        'O2 max. rate (umol/s)': {'result': 'processed_data/O2/max_rate_umol_s'},
        'H2 max. rate crosscheck (umol/s)': {'result': 'processed_data/H2/max_rate_crosscheck_umol_s'},
        'O2 max. rate crosscheck (umol/s)': {'result': 'processed_data/O2/max_rate_crosscheck_umol_s'},
        'H2 apparent quantum yield (%)': {'result': 'processed_data/H2/apparent_quantum_yield',
                                          'format': '.5f'},
        'O2 apparent quantum yield (%)': {'result': 'processed_data/O2/apparent_quantum_yield',
                                          'format': '.5f'},
        'H2 light-to-hydrogen efficiency (%)': {'result': 'processed_data/H2/light_to_hydrogen_efficiency',
                                                'format': '.5f'},
        'O2 light-to-hydrogen efficiency (%)': {'result': 'processed_data/O2/light_to_hydrogen_efficiency',
                                                'format': '.5f'},
        'H2 mass normalized activity (umol/g/h)': {'result': 'processed_data/H2/mass_normalized_activity',
                                                   'format': '.5f'},
        'O2 mass normalized activity (umol/g/h)': {'result': 'processed_data/O2/mass_normalized_activity',
                                                   'format': '.5f'},
    },
}