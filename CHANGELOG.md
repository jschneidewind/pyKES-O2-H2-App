# Changelog

## [Unreleased]

### Added

- H2 and O2 data recorded in the same experiment can be processed together from one metadata row (measured analyte `H2+O2`) via the new H2 + O2 uploader, with separate plots and results per trace.
- Tests in `src/tests/` on synthetic data with known rates.
- PyroScience exports of a Workbench "Recalculate Oxygen" process step (channel `[P1 Recalc O2]`, e.g. AE-918) are read alongside direct sensor logs; their separately logged PT100 temperature (`[ T1]`) is interpolated onto the O2 times.
- Linear baseline (leakage) correction of all traces, fitted to the dark period before irradiation after removing short spikes, with a curvature check (`Baseline check`, incl. the number of removed spike points) and the time-series curves `Amount` and `Baseline` (see `docs/baseline_correction.md`).

### Changed

- Maximum rates and the values derived from them are baseline-corrected; experiments with less than 60 s of usable dark period before irradiation are rejected.

### Fixed

- PyroScience files of interrupted logs (rows without main-channel data) no longer produce NaN measurements.
