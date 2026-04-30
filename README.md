# Simultaneous detection O2/H2

This repository contains the code for the project "Insights into overall photocatalytic water splitting through simultaneous in situ H2 and O2 measurements". It requires the library "pyKES", which is available at https://github.com/jschneidewind/pyKES. 

## Workflow

1. Completing overview Excel sheet, selecting active/inactive experiments
2. Running "parsing_O2_H2_data.py" to generate dataset
3. Visualize dataset in pyKES Streamlit app
4. Analysing rate: selecting experiments and x-axis, exporting data as JSON
5. Fitting gas/liquid kinetic model using "fitting_liquid_gas_phase.py", saving new dataset with fitting results
6. Creating figure for liquid/gas model with new dataset
7. Creating workflow figure with dataset
8. Creating results figure with downloaded JSON files
9. Creating data plots using dataset

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.