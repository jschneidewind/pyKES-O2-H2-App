from pyKES.streamlit_app.config_interface import (
    PyKESStreamlitConfig,
    HomeConfig,
    DataUploadConfig,
    FileUploadHandler,
)

from pykes_o2_h2_app.data_parsing.general_processing_functions import metadata_retrival_function

from pykes_o2_h2_app.data_parsing.processing_functions_O2_liquid import (
    raw_data_reading_function_O2_liquid,
    processing_function_O2_liquid   
)

from pykes_o2_h2_app.data_parsing.processing_functions_H2_liquid import (
    raw_data_reading_function_H2_liquid,
    processing_function_H2_liquid
)

from pykes_o2_h2_app.data_parsing.processing_functions_O2_gas import (
    raw_data_reading_function_O2_gas,
    processing_function_O2_gas
)

from pykes_o2_h2_app.parameters import (
    PROCESSING_PARAMETERS,
    GROUP_MAPPING,
    PLOTTING_INSTRUCTIONS,
)

# -----------------------------------------------------------------------------
# File Handler Config
# -----------------------------------------------------------------------------

file_handler_O2_liquid =  FileUploadHandler(
                            label = "📊 O2 (liquid phase) - Upload Raw Data",
                            file_type = ["csv", "txt"],
                            help_text = "Upload O2 liquid phase measurement raw data files (CSV or TXT).",
                            overview_df_experiment_column = "Experiment",
                            metadata_retrival_function = metadata_retrival_function,
                            raw_data_reading_function = raw_data_reading_function_O2_liquid,
                            processing_function = processing_function_O2_liquid,
                            )

file_handler_H2_liquid =  FileUploadHandler(
                            label = "📊 H2 (liquid phase) - Upload Raw Data",
                            file_type = ["csv", "txt"],
                            help_text = "Upload H2 liquid phase measurement raw data files (CSV or TXT).",
                            overview_df_experiment_column = "Experiment",
                            metadata_retrival_function = metadata_retrival_function,
                            raw_data_reading_function = raw_data_reading_function_H2_liquid,
                            processing_function = processing_function_H2_liquid,
                            )

file_handler_O2_gas =  FileUploadHandler(
                            label = "📊 O2 (gas phase) - Upload Raw Data",
                            file_type = ["csv", "txt"],
                            help_text = "Upload O2 gas phase measurement raw data files (CSV or TXT).",
                            overview_df_experiment_column = "Experiment",
                            metadata_retrival_function = metadata_retrival_function,
                            raw_data_reading_function = raw_data_reading_function_O2_gas,
                            processing_function = processing_function_O2_gas,
                            )

# -----------------------------------------------------------------------------
# Data Upload and Home Configuration
# -----------------------------------------------------------------------------

DATA_UPLOAD_CONFIG = DataUploadConfig(

    file_handlers = [file_handler_O2_liquid, 
                     file_handler_H2_liquid, 
                     file_handler_O2_gas],

    metadata_excel_experiment_column="Experiment",

    group_mapping=GROUP_MAPPING,
    plotting_instruction=PLOTTING_INSTRUCTIONS,
    processing_parameters=PROCESSING_PARAMETERS,
)

HOME_CONFIG = HomeConfig()

# -----------------------------------------------------------------------------
# Top-level app configuration
# -----------------------------------------------------------------------------

PYKES_CONFIG = PyKESStreamlitConfig(
    home_config = HOME_CONFIG,
    data_upload_config = DATA_UPLOAD_CONFIG,
    app_title = "Photocatalysis Data Analysis System",
    app_icon = ":test_tube:",
)



