# Parameters used during data processing
PROCESSING_PARAMETERS = {
    'O2_liquid_processing_parameters': { 
                        'offset': 60,
                        'savgol_window': 10,
                        'savgol_polyorder': 3,
                        'poly_order': 4,
                    },

    'H2_liquid_processing_parameters': {
                        'offset': 60,
                        'savgol_window': 30,
                        'savgol_polyorder': 1,
                        'poly_order': 4,
                    },

    'H2_gas_processing_parameters': {
                        'offset': 60,
                        'savgol_window': 30,
                        'savgol_polyorder': 1,
                        'poly_order': 3,
                    },

    'O2_gas_processing_parameters': { 
                        'offset': 60,
                        'savgol_window': 10,
                        'savgol_polyorder': 3,
                        'poly_order': 3,
                    }, 
}

# Mapping of metadata columns to dataset groups (for visualisation)
GROUP_MAPPING = {
        'Reference': None,
        'Intensity': 'metadata/Irradiance [mW/cm2]',
        'Loading': 'metadata/Catalyst loading [wt% Rh/Cr]',
        'D2O': 'metadata/D2O',
        'Temperature': 'metadata/Temperature [°C]',
        'Gas phase': None,
        'Gas phase D2O': 'metadata/D2O',
        }

# Instruction for time series plotting (mapping of plot labels to dataset paths)
# and kinetic results plotting (mapping of result labels to dataset paths and units)
PLOTTING_INSTRUCTIONS = {
    
    'time_series_instructions': {
                    'Raw (H2, liquid phase)': {
                        'x': 'raw_data/H2_time_s',
                        'y': 'raw_data/H2_umol_L'
                        },
                    'Raw (O2, liquid phase)': {
                        'x': 'raw_data/O2_time_s',
                        'y': 'raw_data/O2_data'
                        },
                    'Raw (H2, gas phase)': {
                        'x': 'raw_data/H2_time_s',
                        'y': 'raw_data/H2_Pa'
                        },
                    'Raw (O2, gas phase)': {
                        'x': 'raw_data/O2_time_s',
                        'y': 'raw_data/O2_data'
                        },
                    'Reaction (H2, liquid phase)': {
                        'x': 'processed_data/H2_liquid_time_reaction',
                        'y': 'processed_data/H2_liquid_data_reaction'
                        },
                    'Reaction (O2, liquid phase)': {
                        'x': 'processed_data/O2_liquid_time_reaction',
                        'y': 'processed_data/O2_liquid_data_reaction'
                        },
                    'Reaction (H2, gas phase)': {
                        'x': 'processed_data/H2_gas_time_reaction',
                        'y': 'processed_data/H2_gas_data_reaction'
                        },
                    'Reaction (O2, gas phase)': {
                        'x': 'processed_data/O2_gas_time_reaction',
                        'y': 'processed_data/O2_gas_data_reaction'
                        },
                    'Poly fit (H2, liquid phase)': {
                        'x': 'processed_data/H2_liquid_time_reaction',
                        'y': 'processed_data/H2_liquid_poly_fit'
                        },
                    'Poly fit (O2, liquid phase)': {
                        'x': 'processed_data/O2_liquid_time_reaction',
                        'y': 'processed_data/O2_liquid_poly_fit'
                        },
                    'Poly fit (H2, gas phase)': {
                        'x': 'processed_data/H2_gas_time_reaction',
                        'y': 'processed_data/H2_gas_poly_fit'
                        },
                    'Poly fit (O2, gas phase)': {
                        'x': 'processed_data/O2_gas_time_reaction',
                        'y': 'processed_data/O2_gas_poly_fit'   
                        },
                    'Smoothed (H2, liquid phase)': {
                        'x': 'processed_data/H2_liquid_time_reaction',
                        'y': 'processed_data/H2_liquid_data_smoothed'
                        },
                    'Smoothed (O2, liquid phase)': {
                        'x': 'processed_data/O2_liquid_time_reaction',
                        'y': 'processed_data/O2_liquid_data_smoothed'
                        },
                    'Rate (H2, liquid phase)': {
                        'x': 'processed_data/H2_liquid_time_diff',
                        'y': 'processed_data/H2_liquid_data_diff'
                        },
                    'Rate (O2, liquid phase)': {
                        'x': 'processed_data/O2_liquid_time_diff',
                        'y': 'processed_data/O2_liquid_data_diff'
                        },
                    'Rate (H2, gas phase)': {
                        'x': 'processed_data/H2_gas_time_diff',
                        'y': 'processed_data/H2_gas_data_diff'
                        },
                    'Rate (O2, gas phase)': {
                        'x': 'processed_data/O2_gas_time_diff',
                        'y': 'processed_data/O2_gas_data_diff'
                        },
                    'Rate poly fit (H2, liquid phase)': {
                        'x': 'processed_data/H2_liquid_time_diff',
                        'y': 'processed_data/H2_liquid_poly_fit_diff'
                        },
                    'Rate poly fit (O2, liquid phase)': {
                        'x': 'processed_data/O2_liquid_time_diff',
                        'y': 'processed_data/O2_liquid_poly_fit_diff'
                        },
                    'Rate poly fit (H2, gas phase)': {
                        'x': 'processed_data/H2_gas_time_diff',
                        'y': 'processed_data/H2_gas_poly_fit_diff'
                        },
                    'Rate poly fit (O2, gas phase)': {
                        'x': 'processed_data/O2_gas_time_diff',
                        'y': 'processed_data/O2_gas_poly_fit_diff'
                        },
                },

    'kinetic_results_instructions': {
        'Max rate (H2, liquid phase)': {'Value': 'processed_data/H2_liquid_max_rate',
                                        'Unit': 'Rate / umol L^-1 s^-1'},

        'Max rate (O2, liquid phase)': {'Value': 'processed_data/O2_liquid_max_rate',
                                        'Unit': 'Rate / umol L^-1 s^-1'},

        'Max rate (H2, gas phase)': {'Value': 'processed_data/H2_gas_max_rate',
                                     'Unit': 'Rate / mmol g^-1 h^-1'},

        'Max rate (O2, gas phase)': {'Value': 'processed_data/O2_gas_max_rate',
                                     'Unit': 'Rate / mmol g^-1 h^-1'},
    },
}