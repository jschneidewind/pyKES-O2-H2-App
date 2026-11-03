# Baseline correction

Every trace (H2 and O2, liquid and gas phase) is corrected for a linear baseline before the maximum rate is determined. The baseline is fitted to the dark period before irradiation and extrapolated over the whole measurement. The code lives in [`general_processing_functions.py`](../src/pykes_o2_h2_app/data_parsing/general_processing_functions.py) (`processing_data` and the helpers above it).

## Why

Air leaking into the reactor raises the O2 signal independently of the photocatalysis. Without correction this leakage is counted as evolved O2. In the first measurements it made up 7–26 % of the O2 rate of experiments that are otherwise fine (AE-904, AE-915), and more in leaking ones. H2 is not expected to drift, but is corrected the same way; its baselines are flat, so the correction there is negligible.

A linear baseline is physically justified as long as the O2 inside the reactor stays far below the 20.9 % outside: the driving force of the leak, and with it the leak rate, is then practically constant. In the gas-phase runs the inside O2 stayed below 1.1 vol%, changing the driving force by at most 5 %.

## How

1. **Baseline window.** From `baseline_start` (180 s) after the log start to `baseline_end_margin` (30 s) before irradiation start, using each sensor's own irradiation start (`Unisense Irradiation start [s]` for H2, `Pyroscience Irradiation start [s]` for O2). The first 3 min are skipped because the sensors settle after the log start; including them inflated the AE-915 O2 baseline from 26 % to 36 % of the rate.
2. **Spike removal.** Short spikes, e.g. from touching the setup, would tilt the fitted line: a single 160 mV spike of the H2 sensor shifts a gas-phase baseline by up to the whole maximum rate. Before the fit, every point that deviates from the median of the `spike_window` (31) points around it by more than `spike_threshold` (8) noise standard deviations is replaced by that median. The noise is the larger of two robust estimates, from these deviations and from the point-to-point steps (smooth traces follow their running median exactly, which would give zero noise). The threshold lies between the noise and any relevant spike: in the baseline windows of the real traces, thresholds of 5 or less marked normal noise points (9 points at 3), 6 and above none, while a 160 mV spike is 1400–2400 noise standard deviations. A spike just below 8 shifts the slope by less than its noise scatter (about 0.7 times at the window edge), and 8 is also the gross-outlier threshold of pyKES; any value from 6 to 20 gives the same results on these traces. Spikes up to about 15 samples long, including a short over- and undershoot, are removed. Only the fit uses the despiked data; the stored and plotted trace keeps the spikes.
3. **Fit and subtraction.** A straight line is fitted to the converted data (mol) in the window and subtracted from the whole trace. The offset correction and the maximum-rate extraction then run on the corrected trace, so the maximum rate drops by about the baseline slope.
4. **Minimum dark period.** If the window is shorter than 60 s, processing fails with an error: without a dark period the leakage, and with it the validity of the experiment, cannot be judged.

The window margins, the spike parameters and the curvature limit below are set in `PROCESSING_PARAMETERS` in [`parameters.py`](../src/pykes_o2_h2_app/parameters.py).

## Curvature check

The linear extrapolation is only valid if the leak is constant. The check fits the two halves of the baseline window separately and compares their slopes. The slope change, in % of the maximum rate, is reported as `Baseline check`: `OK` up to `baseline_curvature_limit` (10 %), `Check baseline` above. If spikes were removed from the window, their number is appended, e.g. `OK (-1.7 %, 1 spike point removed)`.

R² is not used on purpose: a flat baseline (no leak) has R² ≈ 0 because it contains only noise, so an R² limit would flag every good H2 trace, while a strongly curved leak can still reach R² > 0.9.

## Results

| Value | Path | Shown in |
| --- | --- | --- |
| Converted trace incl. dark period | `processed_data/data_umol` | time series `Amount` |
| Fitted baseline over the whole run | `processed_data/baseline_umol` | time series `Baseline` |
| Baseline slope | `processed_data/baseline_slope_umol_s` | results table `Baseline slope (umol/s)` |
| Slope change in % of max. rate | `processed_data/baseline_curvature_percent` | part of `Baseline check` |
| Verdict and removed spike points | `processed_data/baseline_check` | results table `Baseline check` |

Combined `H2+O2` experiments store the same values under `processed_data/H2/...` and `processed_data/O2/...`, shown as `Amount (H2)`, `Baseline (O2)`, `O2 baseline check` and so on. Plotting `Amount` together with `Baseline` shows how well the line follows the dark period and where it is extrapolated.

## Validation

Real data with the default parameters (baseline slope in % of the uncorrected maximum rate, slope change in % of the corrected maximum rate):

| Experiment | Phase | O2 baseline | O2 check | H2 baseline | H2 check |
| --- | --- | --- | --- | --- | --- |
| AE-904 | liquid | 7.5 % | OK (−3.9 %) | 0.0 % | OK (−0.1 %) |
| AE-915 | gas | 26.4 % | OK (−3.3 %) | −0.4 % | OK (−1.7 %) |
| AE-902 | liquid | 29.1 % | Check baseline (22.1 %) | 0.0 % | OK (0.1 %) |
| AE-914 | gas | 62.9 % | Check baseline (91.9 %) | −2.0 % | OK (−3.9 %) |

- No spike points were removed in these runs. A 160 mV spike added to the AE-915 H2 dark period leaves the maximum rate unchanged (7.2667 → 7.2669·10⁻⁴ µmol/s); without spike removal it shifts the baseline by up to 120 % of the rate.
- In AE-915 the leak before irradiation (3.8·10⁻⁴ vol%/min) matches the slope after irradiation (3.7·10⁻⁴ vol%/min), and the corrected H2:O2 rate ratio is 2.11 instead of 1.55 uncorrected, close to the expected 2.
- AE-914 keeps rising at the same slope after the lamp is off; its leak during irradiation is about a third faster than before. AE-902 (liquid) still accelerates at irradiation start, because the leaked O2 reaches the liquid only with a delay. Neither can be corrected reliably, and both are flagged.

The tests in [`src/tests/test_baseline_correction.py`](../src/tests/test_baseline_correction.py) check on synthetic data that a known leak (plus a sensor settling transient) is removed from the rate, that a spike with undershoot in the dark period does not change the rate and is reported, that the curvature measure is exact for a parabola, that the check flags only curved baselines and that a too-short dark period is rejected.

## Limitations

- The baseline is extrapolated over the whole irradiation (9–19 times the window length in the runs above); a leak that changes during irradiation is only caught if it already changes in the dark period.
- In the liquid phase the leaked O2 dissolves with a delay, so the liquid baseline bends upwards at first; strongly leaking liquid-phase runs are therefore underestimated and usually flagged.
- Disturbances longer than about 15 samples (e.g. a slow sensor recovery) are not removed as spikes.
- Periodic disturbances with a period around the window length (about 2–20 min) shift the slope and are only partly caught by the check; faster ones average out, much slower ones look like a leak.
