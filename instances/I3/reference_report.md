# PIN audit: eval (seed 0)

## INPUTS
```
PIN path:                 instances/I3/eval.parquet (release asset)
Decoy marker:             Label == -1 (proteins prefixed 'decoy_'; label/prefix mismatches: 0)
Entrapment marker:        protein accession prefix 'entrap_ATH_'; rows on 'entrap_' proteins without 'entrap_ATH_' (and decoys derived from them) excluded before competition: class X
Entrapment type:          foreign species (Arabidopsis thaliana proteome)
r (entrapment/target db): 0.666 (peptide level)
Primary score column:     mlp_score
Spectrum key columns:     ScanNr, ExpMass
Scorer-banned features:   none known
```

Parquet sha256 dc1fa7725e9e445c96f1c943fa553a9473135b98d2c1ac97e3c22b0151f7153e (622 MB); raw 1067039 rows x 123 cols; rows without score 0. Boosted model: lightgbm 3.3.5 LGBMClassifier defaults (n_jobs=8, verbose=-1). Logistic: mean-impute + standardize (train fold), L2 logistic regression with sklearn's default objective (C=1) solved by Newton to max|step| < 1e-3 (max 30 iterations). Folds: 5, grouped by I/L bare sequence, seeded group permutation (seed 0). Total runtime 5.8 min.

## Phase 0
| class | rows | peptides |
|---|---|---|
| T | 250409 | 184795 |
| E | 133273 | 105450 |
| D | 303303 | 232670 |
| B | 0 | excluded |
| X | 380054 | excluded |

Spectra after (ScanNr, ExpMass) competition: 633126. Wall-clock per phase (s): phase0 15.0, phase1 13.9, phase2 17.1, phase5 0.8, phase6 0.8, phase4 200.6, phase7 0.0, phase3 98.0

## Phase 1 (primary score, peptide-level TDC q=(D+1)/(T+E))
| q | N_T | N_E | N_D | lower FDP [95%] | combined FDP [95%] |
|---|---|---|---|---|---|
| 0.1% | 32084 | 19 | 31 | 0.059% [0.038, 0.092] | 0.148% [0.095, 0.231] |
| 0.5% | 37026 | 80 | 184 | 0.216% [0.173, 0.268] | 0.539% [0.433, 0.671] |
| 1.0% | 38003 | 156 | 380 | 0.409% [0.350, 0.478] | 1.023% [0.875, 1.196] |
| 2.0% | 39055 | 379 | 787 | 0.961% [0.869, 1.062] | 2.404% [2.175, 2.657] |
| 5.0% | 40410 | 978 | 2068 | 2.363% [2.221, 2.514] | 5.911% [5.556, 6.288] |

## Phase 2 (decoy vs entrapment; 111 features; composition by name regex `(?i)^(len|length|peplen|charge\d*|calcmass|pepmass|missed_cleavages|n_mods|enzn|enzc|enzint|ntt)$`)
| feature | comp | KS | KS p | SMD | AUC E/D | AUC T/D |
|---|---|---|---|---|---|---|
| retentiontime |  | 0.0401 | 6.3e-102 | 0.090 | 0.5253 | 0.4996 |
| rt_refined_signed |  | 0.0231 | 6.1e-34 | -0.046 | 0.4860 | 0.4859 |
| missed_cleavages | C | 0.0211 | 1.4e-28 | 0.043 | 0.5118 | 0.4724 |
| n_mods | C | 0.0179 | 1.5e-20 | 0.047 | 0.5092 | 0.4913 |
| shadow_y_missing_per_residue |  | 0.0175 | 7.9e-20 | 0.034 | 0.5096 | 0.4451 |
| rank_mean |  | 0.0171 | 6.5e-19 | -0.037 | 0.4890 | 0.4773 |
| rt_z |  | 0.0166 | 1.0e-17 | -0.037 | 0.4893 | 0.4902 |
| frac_intensity |  | 0.0158 | 3.4e-16 | 0.023 | 0.5077 | 0.5342 |
| intact_y_missing_per_residue |  | 0.0153 | 3.3e-15 | 0.030 | 0.5084 | 0.4453 |
| rt_signed |  | 0.0153 | 3.7e-15 | -0.025 | 0.4927 | 0.4910 |
| intact_b_angle |  | 0.0153 | 4.1e-15 | 0.031 | 0.5088 | 0.5501 |
| n_peaks |  | 0.0147 | 4.8e-14 | -0.026 | 0.4920 | 0.5100 |
| joint_shadow_angle |  | 0.0147 | 5.8e-14 | 0.028 | 0.5095 | 0.5579 |
| b_angle |  | 0.0145 | 9.4e-14 | 0.029 | 0.5081 | 0.5469 |
| shadow_b_angle |  | 0.0145 | 1.3e-13 | 0.030 | 0.5084 | 0.5504 |
| joint_drop_gain |  | 0.0144 | 1.6e-13 | 0.004 | 0.5080 | 0.5649 |
| joint_fraction |  | 0.0137 | 2.8e-12 | 0.015 | 0.5082 | 0.5680 |
| joint_log_fraction |  | 0.0137 | 2.8e-12 | 0.028 | 0.5082 | 0.5680 |
| spectral_contrast_angle |  | 0.0133 | 1.3e-11 | 0.017 | 0.5069 | 0.5601 |
| delta_next |  | 0.0133 | 1.4e-11 | 0.023 | 0.5071 | 0.5458 |
| frac_linear |  | 0.0132 | 2.1e-11 | 0.023 | 0.5080 | 0.5369 |
| delta_RT_loess |  | 0.0130 | 3.8e-11 | -0.019 | 0.4928 | 0.4499 |
| intact_all_angle |  | 0.0129 | 7.6e-11 | 0.017 | 0.5068 | 0.5602 |
| explained_intensity |  | 0.0124 | 4.7e-10 | 0.023 | 0.5078 | 0.5423 |
| n_matched |  | 0.0116 | 7.2e-09 | -0.026 | 0.4927 | 0.5502 |
| top_hits |  | 0.0115 | 1.1e-08 | 0.026 | 0.5071 | 0.5330 |
| n_cands |  | 0.0112 | 2.5e-08 | -0.024 | 0.4924 | 0.4959 |
| len | C | 0.0110 | 4.1e-08 | -0.023 | 0.4935 | 0.4681 |
| shadow_b_explained_prediction |  | 0.0109 | 6.1e-08 | 0.019 | 0.5055 | 0.5467 |
| intact_all_missing_per_residue |  | 0.0109 | 6.3e-08 | 0.021 | 0.5054 | 0.4429 |
| shadow_all_missing_per_residue |  | 0.0107 | 1.1e-07 | 0.025 | 0.5065 | 0.4428 |
| intact_b_explained_prediction |  | 0.0107 | 1.1e-07 | 0.019 | 0.5055 | 0.5456 |
| frag_int_resid_sd |  | 0.0100 | 9.1e-07 | -0.021 | 0.4938 | 0.4598 |
| intact_all_coverage_angle |  | 0.0099 | 1.4e-06 | 0.009 | 0.5050 | 0.5669 |
| ambiguity |  | 0.0098 | 1.8e-06 | 0.028 | 0.5049 | 0.4982 |
| pearson_corr |  | 0.0097 | 2.1e-06 | 0.013 | 0.5044 | 0.5526 |
| shadow_b_coverage_angle |  | 0.0096 | 3.3e-06 | 0.021 | 0.5057 | 0.5512 |
| matched_ppm_rms |  | 0.0096 | 3.3e-06 | -0.025 | 0.4936 | 0.4675 |
| CalcMass | C | 0.0094 | 5.1e-06 | -0.019 | 0.4948 | 0.4685 |
| frag_int_resid_mean |  | 0.0093 | 7.3e-06 | 0.018 | 0.5049 | 0.5111 |
| intact_b_coverage_angle |  | 0.0092 | 8.4e-06 | 0.022 | 0.5059 | 0.5504 |
| shadow_y_error_rms_ppm |  | 0.0091 | 1.2e-05 | -0.016 | 0.4954 | 0.4856 |
| shadow_all_error_rms_ppm |  | 0.0090 | 1.5e-05 | -0.016 | 0.4953 | 0.4710 |
| shadow_all_angle |  | 0.0085 | 5.7e-05 | 0.014 | 0.5050 | 0.5633 |
| unweighted_spectral_entropy |  | 0.0083 | 1.0e-04 | 0.012 | 0.5042 | 0.5671 |
| intact_all_error_rms_ppm |  | 0.0081 | 1.6e-04 | -0.014 | 0.4960 | 0.4706 |
| resid_sd |  | 0.0080 | 1.7e-04 | -0.015 | 0.4956 | 0.4672 |
| intact_y_used_per_residue |  | 0.0080 | 2.0e-04 | 0.014 | 0.5043 | 0.5663 |
| intact_y_error_rms_ppm |  | 0.0077 | 3.3e-04 | -0.015 | 0.4957 | 0.4831 |
| ms1_log_intensity |  | 0.0077 | 3.5e-04 | -0.003 | 0.4975 | 0.5334 |
| frag_good |  | 0.0077 | 3.5e-04 | -0.013 | 0.4961 | 0.5608 |
| log_tic |  | 0.0077 | 3.6e-04 | -0.012 | 0.4966 | 0.5148 |
| shadow_b_missing_per_residue |  | 0.0076 | 4.7e-04 | -0.006 | 0.4974 | 0.4622 |
| frag_llr |  | 0.0076 | 5.0e-04 | 0.012 | 0.5039 | 0.5678 |
| frag_llr_mass |  | 0.0076 | 5.1e-04 | 0.009 | 0.5036 | 0.5467 |
| intact_y_explained_prediction |  | 0.0075 | 5.4e-04 | -0.014 | 0.4967 | 0.5643 |
| frag_log_ions |  | 0.0074 | 6.5e-04 | 0.008 | 0.5025 | 0.5494 |
| frag_z2_mean |  | 0.0074 | 7.3e-04 | -0.007 | 0.4965 | 0.4868 |
| frag_llr_presence |  | 0.0073 | 9.4e-04 | 0.008 | 0.5028 | 0.5679 |
| intact_b_missing_per_residue |  | 0.0071 | 1.2e-03 | -0.006 | 0.4973 | 0.4630 |
| joint_log_intensity |  | 0.0071 | 1.4e-03 | 0.012 | 0.5036 | 0.5651 |
| pred_missing |  | 0.0071 | 1.4e-03 | 0.011 | 0.5031 | 0.4790 |
| shadow_b_error_rms_ppm |  | 0.0070 | 1.5e-03 | -0.007 | 0.4974 | 0.4879 |
| shadow_b_used_per_residue |  | 0.0069 | 1.8e-03 | -0.005 | 0.4974 | 0.5349 |
| resid_mean |  | 0.0069 | 2.0e-03 | 0.013 | 0.5037 | 0.4974 |
| hyperscore |  | 0.0069 | 2.0e-03 | -0.013 | 0.4962 | 0.5501 |
| intact_b_used_per_residue |  | 0.0068 | 2.4e-03 | -0.005 | 0.4977 | 0.5335 |
| charge | C | 0.0068 | 2.5e-03 | -0.015 | 0.4958 | 0.4655 |
| spectral_angle |  | 0.0066 | 3.7e-03 | 0.009 | 0.5025 | 0.5646 |
| intact_y_angle |  | 0.0066 | 3.9e-03 | 0.002 | 0.5028 | 0.5566 |
| y_angle |  | 0.0065 | 4.4e-03 | 0.002 | 0.5027 | 0.5566 |
| shadow_y_explained_prediction |  | 0.0065 | 4.5e-03 | -0.015 | 0.4962 | 0.5646 |
| intact_b_error_rms_ppm |  | 0.0064 | 4.9e-03 | -0.006 | 0.4977 | 0.4867 |
| shadow_y_used_fraction |  | 0.0064 | 5.3e-03 | -0.006 | 0.4978 | 0.5640 |
| frag_wgood |  | 0.0061 | 9.3e-03 | 0.004 | 0.5025 | 0.5667 |
| pred_explained |  | 0.0060 | 1.1e-02 | 0.007 | 0.5024 | 0.5643 |
| shadow_all_used_fraction |  | 0.0060 | 1.2e-02 | -0.008 | 0.4971 | 0.5632 |
| rt_refined_abs |  | 0.0059 | 1.3e-02 | -0.005 | 0.5010 | 0.4439 |
| shadow_all_coverage_angle |  | 0.0058 | 1.6e-02 | 0.005 | 0.5027 | 0.5674 |
| ms1_cycles |  | 0.0058 | 1.6e-02 | -0.011 | 0.4978 | 0.5352 |
| longest_series |  | 0.0054 | 2.7e-02 | -0.009 | 0.4968 | 0.5513 |
| joint_interference |  | 0.0054 | 3.0e-02 | 0.007 | 0.5022 | 0.4508 |
| intact_y_coverage_angle |  | 0.0049 | 6.3e-02 | 0.001 | 0.5017 | 0.5645 |
| intact_all_used_fraction |  | 0.0048 | 6.7e-02 | -0.002 | 0.4989 | 0.5632 |
| shadow_y_used_per_residue |  | 0.0047 | 8.5e-02 | 0.007 | 0.5019 | 0.5662 |
| intact_b_used_fraction |  | 0.0043 | 1.4e-01 | 0.007 | 0.5013 | 0.5406 |
| rank |  | 0.0041 | 1.7e-01 | -0.004 | 0.4989 | 0.4420 |
| intact_all_used_per_residue |  | 0.0039 | 2.1e-01 | 0.008 | 0.5020 | 0.5637 |
| purity |  | 0.0039 | 2.3e-01 | -0.007 | 0.4989 | 0.5388 |
| delta_mass_ppm |  | 0.0039 | 2.3e-01 | -0.006 | 0.4978 | 0.4958 |
| shadow_b_used_fraction |  | 0.0038 | 2.4e-01 | 0.006 | 0.5012 | 0.5417 |
| shadow_all_explained_prediction |  | 0.0038 | 2.5e-01 | -0.006 | 0.4988 | 0.5666 |
| intact_y_used_fraction |  | 0.0037 | 2.6e-01 | -0.001 | 0.4992 | 0.5636 |
| frag_top6_good |  | 0.0035 | 3.3e-01 | 0.005 | 0.5019 | 0.5655 |
| frag_iso_frac |  | 0.0035 | 3.5e-01 | -0.007 | 0.4984 | 0.5049 |
| envelope_cos |  | 0.0033 | 3.9e-01 | 0.001 | 0.5002 | 0.5476 |
| pred_matched_fraction |  | 0.0029 | 5.6e-01 | -0.004 | 0.4995 | 0.5667 |
| intact_all_explained_prediction |  | 0.0029 | 5.6e-01 | -0.004 | 0.4995 | 0.5667 |
| shadow_y_coverage_angle |  | 0.0029 | 5.7e-01 | -0.005 | 0.4989 | 0.5655 |
| shadow_y_angle |  | 0.0029 | 5.7e-01 | -0.006 | 0.4994 | 0.5597 |
| score_surprise |  | 0.0028 | 6.2e-01 | -0.001 | 0.4997 | 0.5574 |
| ms1_isotope_kl |  | 0.0026 | 7.0e-01 | -0.002 | 0.4995 | 0.4982 |
| primary_score |  | 0.0026 | 7.1e-01 | 0.000 | 0.5000 | 0.5582 |
| shadow_all_used_per_residue |  | 0.0023 | 8.6e-01 | 0.003 | 0.5003 | 0.5639 |
| ms1_coelution |  | 0.0022 | 8.7e-01 | -0.002 | 0.4997 | 0.5399 |
| frag_good_frac |  | 0.0021 | 9.0e-01 | -0.001 | 0.5001 | 0.5641 |
| ms1_apex_delta |  | 0.0021 | 9.1e-01 | 0.001 | 0.5002 | 0.5094 |
| comp_pairs |  | 0.0020 | 9.3e-01 | 0.008 | 0.5011 | 0.5568 |
| unexplained_max |  | 0.0019 | 9.6e-01 | -0.010 | 0.4991 | 0.4877 |
| joint_untyped_prediction_fraction |  | 0.0002 | 1.0e+00 | 0.002 | 0.4999 | 0.4999 |
| precursor_missing |  | 0.0001 | 1.0e+00 | 0.000 | 0.5001 | 0.4770 |

## Phase 3 (boosted decoy vs entrapment, 5-fold grouped)
| features | n | AUC [95%] | bits/row below chance (SE) | total bits | significant |
|---|---|---|---|---|---|
| all | 111 | 0.5715 [0.5694, 0.5737] | 0.01029 (0.00093) | 3477.6 | True |
| minus_composition | 106 | 0.5555 [0.5534, 0.5576] | 0.00616 (0.00093) | 2084.5 | True |
| minus_composition_and_top5 | 103 | 0.5420 [0.5398, 0.5441] | 0.00341 (0.00092) | 1153.0 | True |

Joint leak: True. Carriers: ['rt_z', 'rt_refined_abs', 'delta_RT_loess', 'rt_signed']. Permutation importance (AUC drop, minus_composition_and_top5): rt_z 0.0143±0.0013, rt_refined_abs 0.0116±0.0010, delta_RT_loess 0.0085±0.0011, rt_signed 0.0069±0.0011, ambiguity 0.0039±0.0006, intact_y_used_per_residue 0.0034±0.0006, intact_y_missing_per_residue 0.0022±0.0006, frag_good 0.0018±0.0004

## Phase 4 (rescoring T+E vs D, OOF; A = 99 features)
| cond | model | feature | N_T | N_E | N_D | lower FDP | combined FDP [95%] |
|---|---|---|---|---|---|---|---|
| A | LR | - | 31893 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| A | GB | - | 35502 | 173 | 355 | 0.485% | 1.21% [1.05, 1.41] |
| B | LR | retentiontime | 31815 | 115 | 318 | 0.360% | 0.90% [0.75, 1.08] |
| C | LR | retentiontime | 31883 | 119 | 319 | 0.372% | 0.93% [0.78, 1.11] |
| B | GB | retentiontime | 35395 | 172 | 354 | 0.484% | 1.21% [1.04, 1.40] |
| C | GB | retentiontime | 35516 | 177 | 355 | 0.496% | 1.24% [1.07, 1.44] |
| B | LR | rt_refined_signed | 31997 | 122 | 320 | 0.380% | 0.95% [0.80, 1.13] |
| C | LR | rt_refined_signed | 31888 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| B | GB | rt_refined_signed | 36524 | 151 | 365 | 0.412% | 1.03% [0.88, 1.21] |
| C | GB | rt_refined_signed | 35472 | 173 | 355 | 0.485% | 1.21% [1.05, 1.41] |
| B | LR | missed_cleavages | 31802 | 118 | 318 | 0.370% | 0.92% [0.77, 1.11] |
| C | LR | missed_cleavages | 31895 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| B | GB | missed_cleavages | 35568 | 174 | 356 | 0.487% | 1.22% [1.05, 1.41] |
| C | GB | missed_cleavages | 35416 | 166 | 354 | 0.467% | 1.17% [1.00, 1.36] |
| B | LR | n_mods | 31944 | 121 | 319 | 0.377% | 0.94% [0.79, 1.13] |
| C | LR | n_mods | 31898 | 119 | 319 | 0.372% | 0.93% [0.78, 1.11] |
| B | GB | n_mods | 35548 | 184 | 356 | 0.515% | 1.29% [1.12, 1.49] |
| C | GB | n_mods | 35518 | 171 | 355 | 0.479% | 1.20% [1.03, 1.39] |
| B | LR | shadow_y_missing_per_residue | 31893 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | shadow_y_missing_per_residue | 31867 | 117 | 318 | 0.366% | 0.92% [0.76, 1.10] |
| B | GB | shadow_y_missing_per_residue | 35478 | 172 | 355 | 0.482% | 1.21% [1.04, 1.40] |
| C | GB | shadow_y_missing_per_residue | 35476 | 163 | 355 | 0.457% | 1.14% [0.98, 1.33] |
| B | LR | rank_mean | 31864 | 118 | 318 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | rank_mean | 31885 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| B | LR | rt_z | 31933 | 122 | 319 | 0.381% | 0.95% [0.80, 1.14] |
| C | LR | rt_z | 31886 | 119 | 319 | 0.372% | 0.93% [0.78, 1.11] |
| B | LR | frac_intensity | 32011 | 122 | 320 | 0.380% | 0.95% [0.80, 1.13] |
| C | LR | frac_intensity | 31889 | 117 | 319 | 0.366% | 0.91% [0.76, 1.10] |
| B | LR | intact_y_missing_per_residue | 31893 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | intact_y_missing_per_residue | 31890 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| B | LR | rt_signed | 31952 | 120 | 319 | 0.374% | 0.94% [0.78, 1.12] |
| C | LR | rt_signed | 31887 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| B | LR | {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} | 32146 | 124 | 321 | 0.384% | 0.96% [0.81, 1.15] |
| C | LR | {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} | 31898 | 118 | 319 | 0.369% | 0.92% [0.77, 1.10] |
| B | GB | {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} | 36643 | 160 | 367 | 0.435% | 1.09% [0.93, 1.27] |
| C | GB | {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} | 35478 | 172 | 355 | 0.482% | 1.21% [1.04, 1.40] |
| B/C | GB | rank_mean | boosted: skipped (time) | | | | |
| B/C | GB | rt_z | boosted: skipped (time) | | | | |
| B/C | GB | frac_intensity | boosted: skipped (time) | | | | |
| B/C | GB | intact_y_missing_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | rt_signed | boosted: skipped (time) | | | | |

## Phase 5 (third null: 50 primary-score quantile bins with D/(T+E) within 5% of 1; band N_T 24753, N_E 17914, N_D 41001, 8 of 50 bins)
| feature | KS D vs T(band) | p | AUC | KS D vs E(band) | AUC D vs E(band) | agrees with Phase 2 |
|---|---|---|---|---|---|---|
| retentiontime | 0.0065 | 5.2e-01 | 0.4979 | 0.0418 | 0.5251 | False |
| rt_refined_signed | 0.0090 | 1.6e-01 | 0.5042 | 0.0216 | 0.4894 | False |
| missed_cleavages | 0.0220 | 6.3e-07 | 0.5136 | 0.0244 | 0.5128 | True |
| n_mods | 0.0043 | 9.3e-01 | 0.5020 | 0.0152 | 0.5075 | False |
| shadow_y_missing_per_residue | 0.0066 | 5.1e-01 | 0.5011 | 0.0237 | 0.5123 | False |
| rank_mean | 0.0098 | 1.0e-01 | 0.4973 | 0.0207 | 0.4881 | True |
| rt_z | 0.0106 | 6.0e-02 | 0.5051 | 0.0148 | 0.4923 | True |
| frac_intensity | 0.0067 | 4.9e-01 | 0.5006 | 0.0218 | 0.5090 | False |
| intact_y_missing_per_residue | 0.0071 | 4.2e-01 | 0.5011 | 0.0193 | 0.5107 | False |
| rt_signed | 0.0097 | 1.1e-01 | 0.5053 | 0.0106 | 0.4963 | True |
| {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} | nan | nan | 0.4982 | nan | nan | False |

## Phase 6 (Spearman rho with passing peptides on same protein, baseline q<=1%)
| feature | rho | flag |
|---|---|---|
| retentiontime | 0.020 | False |
| rt_refined_signed | -0.036 | False |
| missed_cleavages | -0.022 | False |
| n_mods | 0.040 | False |
| shadow_y_missing_per_residue | -0.401 | True |
| rank_mean | -0.316 | True |
| rt_z | -0.027 | False |
| frac_intensity | 0.311 | True |
| intact_y_missing_per_residue | -0.393 | True |
| rt_signed | -0.031 | False |
| {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} | -0.123 | False |

## Phase 7 (LR for candidates with LR B combined FDP above A's upper bound; LR and GB for priority features)
Condition-A solve wall-clock: LR 4.1 s, GB 14.1 s.

| feature | combined FDP at 0/25/50/75/100% permuted | monotone |
|---|---|---|
| none | | |

## Candidates
| feature | KS | FDP A (LR/GB) | FDP B (LR/GB) | FDP C (LR/GB) | third-null KS | entrapment-blind flag | linear vs boosted inflation (B-A, pp) | dose monotone | peptides lost if dropped (LR/GB) |
|---|---|---|---|---|---|---|---|---|---|
| retentiontime | 0.0401 | 0.92% / 1.21% | 0.90% / 1.21% | 0.93% / 1.24% | 0.0065 | N | -0.02 / -0.00 | n/a / n/a | -78 / -107 |
| rt_refined_signed | 0.0231 | 0.92% / 1.21% | 0.95% / 1.03% | 0.92% / 1.21% | 0.0090 | N | +0.03 / -0.18 | n/a / n/a | 104 / 1022 |
| missed_cleavages | 0.0211 | 0.92% / 1.21% | 0.92% / 1.22% | 0.92% / 1.17% | 0.0220 | N | +0.00 / +0.00 | n/a / n/a | -91 / 66 |
| n_mods | 0.0179 | 0.92% / 1.21% | 0.94% / 1.29% | 0.93% / 1.20% | 0.0043 | N | +0.02 / +0.08 | n/a / n/a | 51 / 46 |
| shadow_y_missing_per_residue | 0.0175 | 0.92% / 1.21% | 0.92% / 1.21% | 0.92% / 1.14% | 0.0066 | Y | +0.00 / -0.01 | n/a / n/a | 0 / -24 |
| rank_mean | 0.0171 | 0.92% / 1.21% | 0.92% / skip | 0.92% / skip | 0.0098 | Y | +0.00 / skip | n/a / n/a | -29 / skip |
| rt_z | 0.0166 | 0.92% / 1.21% | 0.95% / skip | 0.93% / skip | 0.0106 | N | +0.03 / skip | n/a / n/a | 40 / skip |
| frac_intensity | 0.0158 | 0.92% / 1.21% | 0.95% / skip | 0.91% / skip | 0.0067 | Y | +0.03 / skip | n/a / n/a | 118 / skip |
| intact_y_missing_per_residue | 0.0153 | 0.92% / 1.21% | 0.92% / skip | 0.92% / skip | 0.0071 | Y | +0.00 / skip | n/a / n/a | 0 / skip |
| rt_signed | 0.0153 | 0.92% / 1.21% | 0.94% / skip | 0.92% / skip | 0.0097 | N | +0.01 / skip | n/a / n/a | 59 / skip |
| {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} | 0.0166 | 0.92% / 1.21% | 0.96% / 1.09% | 0.92% / 1.21% | nan | N | +0.04 / -0.13 | n/a / n/a | 253 / 1141 |

## Verdicts
- CONFIRMED: none
- REJECTED: retentiontime (causal-, third-null-), rt_refined_signed (causal-, third-null-), missed_cleavages (causal-), n_mods (causal-, third-null-), rt_z (causal-), rt_signed (causal-), {rt_z+rt_refined_abs+delta_RT_loess+rt_signed} (causal-, third-null-)
- UNRESOLVED: shadow_y_missing_per_residue, rank_mean, frac_intensity, intact_y_missing_per_residue

## CHARACTERIZATION
Baseline: combined FDP at nominal 1% is 1.02% [0.87, 1.20], so the baseline is calibrated (interval includes 1%). Single features: the largest Phase 2 KS is 0.040 (retentiontime); no candidate is CONFIRMED. UNRESOLVED: shadow_y_missing_per_residue, rank_mean, frac_intensity, intact_y_missing_per_residue; Phase 6 flags shadow_y_missing_per_residue, rank_mean, frac_intensity, intact_y_missing_per_residue (|rho| 0.40, 0.32, 0.31, 0.39). Combinations: the joint decoy-vs-entrapment classifier reaches AUC 0.572 on all features and 0.542 after both removals (joint signal; carriers rt_z, rt_refined_abs, delta_RT_loess, rt_signed). Learner: condition A gives combined FDP 0.92% [0.77, 1.10] with logistic regression and 1.21% [1.05, 1.41] with boosting, so the boosted learner runs hotter on the same features.
