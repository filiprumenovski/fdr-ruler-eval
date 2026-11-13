# PIN audit: eval (seed 0)

## INPUTS
```
PIN path:                 instances/I2/eval.parquet (release asset)
Decoy marker:             Label == -1 (proteins prefixed 'decoy_'; label/prefix mismatches: 0)
Entrapment marker:        protein accession prefix 'entrap_ATH_'; rows on 'entrap_' proteins without 'entrap_ATH_' (and decoys derived from them) excluded before competition: class X
Entrapment type:          foreign species (Arabidopsis thaliana proteome)
r (entrapment/target db): 0.666 (peptide level)
Primary score column:     mlp_score
Spectrum key columns:     ScanNr, ExpMass
Scorer-banned features:   none known
```

Parquet sha256 95d6cc1f077bf5ea4497c409b55f6c8e6316ab89cd3022d4bf4980e6c525aca1 (726 MB); raw 1120111 rows x 131 cols; rows without score 0. Boosted model: lightgbm 3.3.5 LGBMClassifier defaults (n_jobs=8, verbose=-1). Logistic: mean-impute + standardize (train fold), L2 logistic regression with sklearn's default objective (C=1) solved by Newton to max|step| < 1e-3 (max 30 iterations). Folds: 5, grouped by I/L bare sequence, seeded group permutation (seed 0). Total runtime 7.4 min.

## Phase 0
| class | rows | peptides |
|---|---|---|
| T | 254638 | 189083 |
| E | 133490 | 105199 |
| D | 328644 | 258419 |
| B | 0 | excluded |
| X | 403339 | excluded |

Spectra after (ScanNr, ExpMass) competition: 672479. Wall-clock per phase (s): phase0 14.5, phase1 12.8, phase2 18.7, phase5 5.5, phase6 0.8, phase4 218.0, phase7 67.7, phase3 107.5

## Phase 1 (primary score, peptide-level TDC q=(D+1)/(T+E))
| q | N_T | N_E | N_D | lower FDP [95%] | combined FDP [95%] |
|---|---|---|---|---|---|
| 0.1% | 34502 | 30 | 33 | 0.087% [0.061, 0.124] | 0.217% [0.152, 0.310] |
| 0.5% | 37915 | 140 | 189 | 0.368% [0.312, 0.434] | 0.920% [0.780, 1.085] |
| 1.0% | 38615 | 225 | 387 | 0.579% [0.509, 0.660] | 1.449% [1.272, 1.651] |
| 2.0% | 39375 | 404 | 794 | 1.016% [0.922, 1.119] | 2.541% [2.306, 2.799] |
| 5.0% | 40717 | 1018 | 2085 | 2.439% [2.296, 2.592] | 6.102% [5.742, 6.483] |

## Phase 2 (decoy vs entrapment; 119 features; composition by name regex `(?i)^(len|length|peplen|charge\d*|calcmass|pepmass|missed_cleavages|n_mods|enzn|enzc|enzint|ntt)$`)
| feature | comp | KS | KS p | SMD | AUC E/D | AUC T/D |
|---|---|---|---|---|---|---|
| protein_peer_count |  | 0.0680 | 6.6e-301 | -0.179 | 0.4557 | 0.5991 |
| retentiontime |  | 0.0303 | 3.3e-60 | 0.068 | 0.5192 | 0.4935 |
| frag_tail_frac |  | 0.0295 | 4.4e-57 | 0.125 | 0.5164 | 0.5238 |
| rt_z |  | 0.0197 | 1.1e-25 | -0.038 | 0.4885 | 0.4915 |
| rt_refined_signed |  | 0.0187 | 4.0e-23 | -0.041 | 0.4879 | 0.4896 |
| rt_signed |  | 0.0179 | 3.8e-21 | -0.031 | 0.4911 | 0.4911 |
| shadow_y_missing_per_residue |  | 0.0147 | 1.8e-14 | 0.033 | 0.5091 | 0.4451 |
| shadow_all_missing_per_residue |  | 0.0136 | 1.8e-12 | 0.032 | 0.5090 | 0.4455 |
| intact_y_missing_per_residue |  | 0.0131 | 1.6e-11 | 0.029 | 0.5080 | 0.4452 |
| intact_all_missing_per_residue |  | 0.0120 | 1.0e-09 | 0.029 | 0.5080 | 0.4455 |
| delta_RT_loess |  | 0.0118 | 1.8e-09 | -0.017 | 0.4935 | 0.4504 |
| b_angle |  | 0.0110 | 3.3e-08 | 0.020 | 0.5057 | 0.5439 |
| joint_fraction |  | 0.0102 | 3.1e-07 | 0.008 | 0.5054 | 0.5659 |
| joint_log_fraction |  | 0.0102 | 3.1e-07 | 0.019 | 0.5054 | 0.5659 |
| frac_intensity |  | 0.0102 | 3.5e-07 | 0.016 | 0.5048 | 0.5319 |
| intact_b_angle |  | 0.0096 | 2.1e-06 | 0.016 | 0.5044 | 0.5452 |
| seq_context_ll |  | 0.0096 | 2.3e-06 | 0.004 | 0.5043 | 0.5246 |
| n_peaks |  | 0.0090 | 1.2e-05 | -0.011 | 0.4963 | 0.5127 |
| rank_mean |  | 0.0088 | 2.1e-05 | -0.018 | 0.4948 | 0.4817 |
| explained_intensity |  | 0.0087 | 2.3e-05 | 0.016 | 0.5051 | 0.5409 |
| joint_drop_gain |  | 0.0084 | 4.8e-05 | 0.000 | 0.5037 | 0.5609 |
| shadow_b_angle |  | 0.0081 | 1.0e-04 | 0.014 | 0.5039 | 0.5457 |
| frac_linear |  | 0.0078 | 2.4e-04 | 0.015 | 0.5044 | 0.5339 |
| joint_shadow_angle |  | 0.0077 | 2.9e-04 | 0.014 | 0.5048 | 0.5535 |
| intact_y_angle |  | 0.0077 | 3.1e-04 | -0.018 | 0.4961 | 0.5496 |
| y_angle |  | 0.0076 | 3.5e-04 | -0.018 | 0.4962 | 0.5497 |
| shadow_all_used_fraction |  | 0.0072 | 7.9e-04 | -0.014 | 0.4955 | 0.5616 |
| joint_log_intensity |  | 0.0072 | 8.4e-04 | 0.011 | 0.5035 | 0.5637 |
| intact_y_used_per_residue |  | 0.0069 | 1.6e-03 | 0.012 | 0.5037 | 0.5652 |
| shadow_y_angle |  | 0.0068 | 2.1e-03 | -0.017 | 0.4964 | 0.5563 |
| intact_y_explained_prediction |  | 0.0068 | 2.1e-03 | -0.015 | 0.4960 | 0.5630 |
| frag_int_resid_mean |  | 0.0067 | 2.6e-03 | 0.016 | 0.5039 | 0.5125 |
| shadow_all_angle |  | 0.0064 | 4.3e-03 | 0.005 | 0.5025 | 0.5600 |
| shadow_y_explained_prediction |  | 0.0060 | 8.5e-03 | -0.016 | 0.4959 | 0.5637 |
| frag_log_ions |  | 0.0060 | 8.7e-03 | 0.005 | 0.5010 | 0.5477 |
| intact_all_used_per_residue |  | 0.0060 | 9.0e-03 | 0.006 | 0.5023 | 0.5633 |
| intact_b_explained_prediction |  | 0.0059 | 1.0e-02 | 0.009 | 0.5023 | 0.5415 |
| intact_y_coverage_angle |  | 0.0059 | 1.2e-02 | -0.012 | 0.4971 | 0.5601 |
| frag_good_frac |  | 0.0058 | 1.4e-02 | -0.012 | 0.4965 | 0.5609 |
| shadow_y_used_fraction |  | 0.0057 | 1.6e-02 | -0.009 | 0.4972 | 0.5631 |
| shadow_y_coverage_angle |  | 0.0056 | 1.9e-02 | -0.015 | 0.4964 | 0.5629 |
| intact_all_used_fraction |  | 0.0055 | 2.1e-02 | -0.009 | 0.4970 | 0.5613 |
| shadow_b_error_rms_ppm |  | 0.0055 | 2.3e-02 | 0.010 | 0.5023 | 0.4920 |
| shadow_b_explained_prediction |  | 0.0054 | 2.4e-02 | 0.008 | 0.5022 | 0.5426 |
| spectral_contrast_angle |  | 0.0053 | 3.1e-02 | -0.000 | 0.5012 | 0.5534 |
| intact_b_error_rms_ppm |  | 0.0052 | 3.6e-02 | 0.010 | 0.5022 | 0.4905 |
| intact_all_angle |  | 0.0052 | 3.7e-02 | -0.001 | 0.5011 | 0.5537 |
| frag_int_resid_sd |  | 0.0051 | 4.1e-02 | -0.005 | 0.4985 | 0.4649 |
| rt_refined_abs |  | 0.0050 | 4.7e-02 | -0.009 | 0.4992 | 0.4424 |
| pred_missing |  | 0.0050 | 5.1e-02 | -0.006 | 0.4980 | 0.4766 |
| top_hits |  | 0.0049 | 5.6e-02 | 0.013 | 0.5033 | 0.5297 |
| motif_ctx_b |  | 0.0048 | 6.1e-02 | 0.001 | 0.5007 | 0.5007 |
| log_tic |  | 0.0048 | 6.7e-02 | -0.005 | 0.4985 | 0.5144 |
| pred_matched_fraction |  | 0.0047 | 7.2e-02 | -0.006 | 0.4990 | 0.5653 |
| intact_all_explained_prediction |  | 0.0047 | 7.2e-02 | -0.006 | 0.4990 | 0.5653 |
| intact_b_used_per_residue |  | 0.0047 | 7.6e-02 | -0.004 | 0.4989 | 0.5343 |
| intact_b_coverage_angle |  | 0.0047 | 7.7e-02 | 0.005 | 0.5022 | 0.5461 |
| n_cands |  | 0.0047 | 7.7e-02 | -0.011 | 0.4969 | 0.4995 |
| pred_explained |  | 0.0046 | 8.3e-02 | 0.002 | 0.4990 | 0.5613 |
| spectral_angle |  | 0.0046 | 8.4e-02 | -0.000 | 0.4992 | 0.5616 |
| shadow_b_coverage_angle |  | 0.0045 | 9.2e-02 | 0.004 | 0.5017 | 0.5470 |
| frag_good |  | 0.0045 | 9.3e-02 | 0.008 | 0.5022 | 0.5647 |
| score_surprise |  | 0.0045 | 1.0e-01 | -0.003 | 0.4985 | 0.5559 |
| delta_next |  | 0.0045 | 1.0e-01 | 0.006 | 0.5018 | 0.5408 |
| intact_all_coverage_angle |  | 0.0044 | 1.1e-01 | -0.008 | 0.4997 | 0.5616 |
| shadow_all_explained_prediction |  | 0.0044 | 1.2e-01 | -0.008 | 0.4986 | 0.5658 |
| intact_y_used_fraction |  | 0.0044 | 1.2e-01 | -0.004 | 0.4988 | 0.5627 |
| frag_z2_mean |  | 0.0043 | 1.3e-01 | 0.002 | 0.5016 | 0.4891 |
| n_mods | C | 0.0043 | 1.3e-01 | 0.003 | 0.5018 | 0.4839 |
| shadow_all_coverage_angle |  | 0.0041 | 1.6e-01 | -0.008 | 0.4998 | 0.5644 |
| frag_wgood |  | 0.0041 | 1.6e-01 | -0.007 | 0.4990 | 0.5628 |
| frag_llr |  | 0.0041 | 1.7e-01 | 0.003 | 0.5014 | 0.5656 |
| matched_ppm_rms |  | 0.0040 | 1.8e-01 | 0.002 | 0.5012 | 0.4737 |
| unweighted_spectral_entropy |  | 0.0040 | 1.9e-01 | -0.002 | 0.5001 | 0.5626 |
| joint_interference |  | 0.0040 | 1.9e-01 | 0.003 | 0.5008 | 0.4529 |
| shadow_b_used_per_residue |  | 0.0039 | 2.1e-01 | -0.004 | 0.4989 | 0.5358 |
| ms1_log_intensity |  | 0.0038 | 2.3e-01 | 0.001 | 0.4995 | 0.5336 |
| hyperscore |  | 0.0037 | 2.6e-01 | -0.005 | 0.4988 | 0.5507 |
| shadow_all_used_per_residue |  | 0.0036 | 2.8e-01 | 0.001 | 0.5007 | 0.5636 |
| shadow_b_used_fraction |  | 0.0036 | 3.0e-01 | -0.005 | 0.4985 | 0.5387 |
| ion_kurt_ab |  | 0.0036 | 3.0e-01 | 0.001 | 0.5005 | 0.4998 |
| n_matched |  | 0.0035 | 3.1e-01 | -0.007 | 0.4986 | 0.5536 |
| ion_kurt_b |  | 0.0035 | 3.1e-01 | -0.004 | 0.4990 | 0.4991 |
| intact_y_error_rms_ppm |  | 0.0035 | 3.2e-01 | 0.001 | 0.5005 | 0.4867 |
| intact_all_error_rms_ppm |  | 0.0034 | 3.4e-01 | 0.005 | 0.5014 | 0.4746 |
| intact_b_used_fraction |  | 0.0034 | 3.6e-01 | -0.005 | 0.4986 | 0.5375 |
| shadow_y_used_per_residue |  | 0.0033 | 3.8e-01 | 0.005 | 0.5014 | 0.5651 |
| motif_ctx_a |  | 0.0033 | 4.0e-01 | -0.000 | 0.4999 | 0.4999 |
| CalcMass | C | 0.0033 | 4.0e-01 | 0.003 | 0.5011 | 0.4736 |
| shadow_all_error_rms_ppm |  | 0.0033 | 4.0e-01 | 0.005 | 0.5013 | 0.4759 |
| frag_llr_presence |  | 0.0033 | 4.1e-01 | 0.006 | 0.5015 | 0.5665 |
| frag_llr_mass |  | 0.0032 | 4.1e-01 | -0.001 | 0.5002 | 0.5442 |
| ion_kurt_a |  | 0.0032 | 4.4e-01 | 0.001 | 0.5006 | 0.5001 |
| resid_mean |  | 0.0031 | 4.5e-01 | 0.002 | 0.5008 | 0.4937 |
| rank |  | 0.0031 | 4.8e-01 | 0.003 | 0.5010 | 0.4440 |
| primary_score |  | 0.0031 | 4.8e-01 | -0.004 | 0.4988 | 0.5564 |
| ms1_apex_delta |  | 0.0029 | 5.5e-01 | 0.001 | 0.5004 | 0.5084 |
| delta_mass_ppm |  | 0.0029 | 5.6e-01 | -0.004 | 0.4986 | 0.4962 |
| ambiguity |  | 0.0029 | 5.7e-01 | 0.001 | 0.5014 | 0.4947 |
| len | C | 0.0029 | 5.7e-01 | 0.001 | 0.5004 | 0.4737 |
| shadow_b_missing_per_residue |  | 0.0029 | 5.8e-01 | 0.005 | 0.5014 | 0.4661 |
| intact_b_missing_per_residue |  | 0.0029 | 5.8e-01 | 0.005 | 0.5013 | 0.4670 |
| missed_cleavages | C | 0.0028 | 5.9e-01 | 0.005 | 0.5015 | 0.4638 |
| ms1_cycles |  | 0.0027 | 6.3e-01 | -0.004 | 0.4996 | 0.5355 |
| frag_top6_good |  | 0.0027 | 6.6e-01 | -0.003 | 0.4989 | 0.5624 |
| ms1_coelution |  | 0.0026 | 7.1e-01 | 0.002 | 0.5006 | 0.5396 |
| shadow_y_error_rms_ppm |  | 0.0024 | 7.8e-01 | -0.001 | 0.4998 | 0.4894 |
| pearson_corr |  | 0.0024 | 7.9e-01 | -0.001 | 0.5000 | 0.5463 |
| longest_series |  | 0.0023 | 8.4e-01 | 0.006 | 0.5010 | 0.5535 |
| ms1_isotope_kl |  | 0.0021 | 8.9e-01 | 0.002 | 0.5007 | 0.4986 |
| resid_sd |  | 0.0019 | 9.5e-01 | -0.000 | 0.4998 | 0.4710 |
| purity |  | 0.0017 | 9.8e-01 | 0.000 | 0.5003 | 0.5391 |
| envelope_cos |  | 0.0017 | 9.8e-01 | 0.001 | 0.5003 | 0.5459 |
| frag_iso_frac |  | 0.0014 | 1.0e+00 | -0.001 | 0.4996 | 0.5059 |
| charge | C | 0.0013 | 1.0e+00 | 0.000 | 0.4999 | 0.4688 |
| unexplained_max |  | 0.0012 | 1.0e+00 | -0.006 | 0.4994 | 0.4879 |
| precursor_missing |  | 0.0012 | 1.0e+00 | -0.002 | 0.4994 | 0.4775 |
| comp_pairs |  | 0.0008 | 1.0e+00 | 0.003 | 0.5003 | 0.5557 |
| joint_untyped_prediction_fraction |  | 0.0002 | 1.0e+00 | 0.004 | 0.5000 | 0.4999 |

## Phase 3 (boosted decoy vs entrapment, 5-fold grouped)
| features | n | AUC [95%] | bits/row below chance (SE) | total bits | significant |
|---|---|---|---|---|---|
| all | 119 | 0.8215 [0.8198, 0.8231] | 0.18874 (0.00091) | 68630.9 | True |
| minus_composition | 114 | 0.8170 [0.8153, 0.8187] | 0.19054 (0.00093) | 69283.4 | True |
| minus_composition_and_top5 | 109 | 0.8169 [0.8152, 0.8186] | 0.19623 (0.00091) | 71353.9 | True |

Joint leak: True. Carriers: ['ion_kurt_ab', 'ion_kurt_b', 'ion_kurt_a']. Permutation importance (AUC drop, minus_composition_and_top5): ion_kurt_ab 0.3148±0.0020, ion_kurt_b 0.2054±0.0024, ion_kurt_a 0.2052±0.0004, rt_signed 0.0008±0.0002, rt_refined_abs 0.0007±0.0002, delta_RT_loess 0.0005±0.0003, intact_y_used_per_residue 0.0002±0.0001, shadow_all_missing_per_residue 0.0002±0.0001

## Phase 4 (rescoring T+E vs D, OOF; A = 106 features)
| cond | model | feature | N_T | N_E | N_D | lower FDP | combined FDP [95%] |
|---|---|---|---|---|---|---|---|
| A | LR | - | 32403 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| A | GB | - | 37144 | 178 | 372 | 0.477% | 1.19% [1.03, 1.38] |
| B | LR | protein_peer_count | 34500 | 91 | 344 | 0.263% | 0.66% [0.54, 0.81] |
| C | LR | protein_peer_count | 32416 | 117 | 324 | 0.360% | 0.90% [0.75, 1.08] |
| B | GB | protein_peer_count | 38152 | 101 | 381 | 0.264% | 0.66% [0.54, 0.80] |
| C | GB | protein_peer_count | 37126 | 175 | 372 | 0.469% | 1.17% [1.01, 1.36] |
| B | LR | retentiontime | 32406 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| C | LR | retentiontime | 32403 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| B | GB | retentiontime | 37251 | 190 | 373 | 0.507% | 1.27% [1.10, 1.46] |
| C | GB | retentiontime | 37136 | 181 | 372 | 0.485% | 1.21% [1.05, 1.40] |
| B | LR | frag_tail_frac | 32402 | 136 | 324 | 0.418% | 1.05% [0.88, 1.24] |
| C | LR | frag_tail_frac | 32404 | 115 | 324 | 0.354% | 0.88% [0.74, 1.06] |
| B | GB | frag_tail_frac | 40566 | 3012 | 434 | 6.912% | 17.29% [16.70, 17.90] |
| C | GB | frag_tail_frac | 37143 | 175 | 372 | 0.469% | 1.17% [1.01, 1.36] |
| B | LR | rt_z | 32429 | 116 | 324 | 0.356% | 0.89% [0.74, 1.07] |
| C | LR | rt_z | 32406 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| B | GB | rt_z | 37121 | 182 | 372 | 0.488% | 1.22% [1.06, 1.41] |
| C | GB | rt_z | 37126 | 183 | 372 | 0.490% | 1.23% [1.06, 1.42] |
| B | LR | rt_refined_signed | 32406 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| C | LR | rt_refined_signed | 32403 | 117 | 324 | 0.360% | 0.90% [0.75, 1.08] |
| B | GB | rt_refined_signed | 37193 | 177 | 372 | 0.474% | 1.18% [1.02, 1.37] |
| C | GB | rt_refined_signed | 37139 | 179 | 372 | 0.480% | 1.20% [1.04, 1.39] |
| B | LR | rt_signed | 32412 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| C | LR | rt_signed | 32408 | 117 | 324 | 0.360% | 0.90% [0.75, 1.08] |
| B | LR | shadow_y_missing_per_residue | 32412 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | shadow_y_missing_per_residue | 32401 | 115 | 324 | 0.354% | 0.88% [0.74, 1.06] |
| B | LR | shadow_all_missing_per_residue | 32424 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | shadow_all_missing_per_residue | 32395 | 115 | 324 | 0.354% | 0.88% [0.74, 1.06] |
| B | LR | intact_y_missing_per_residue | 32412 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | intact_y_missing_per_residue | 32401 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| B | LR | intact_all_missing_per_residue | 32424 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | intact_all_missing_per_residue | 32397 | 115 | 324 | 0.354% | 0.88% [0.74, 1.06] |
| B | LR | {ion_kurt_ab+ion_kurt_b+ion_kurt_a} | 32400 | 116 | 324 | 0.357% | 0.89% [0.74, 1.07] |
| C | LR | {ion_kurt_ab+ion_kurt_b+ion_kurt_a} | 32405 | 115 | 324 | 0.354% | 0.88% [0.74, 1.06] |
| B | GB | {ion_kurt_ab+ion_kurt_b+ion_kurt_a} | 39983 | 2581 | 424 | 6.064% | 15.17% [14.61, 15.75] |
| C | GB | {ion_kurt_ab+ion_kurt_b+ion_kurt_a} | 37098 | 182 | 371 | 0.488% | 1.22% [1.06, 1.41] |
| B/C | GB | rt_signed | boosted: skipped (time) | | | | |
| B/C | GB | shadow_y_missing_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | shadow_all_missing_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | intact_y_missing_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | intact_all_missing_per_residue | boosted: skipped (time) | | | | |

## Phase 5 (third null: 50 primary-score quantile bins with D/(T+E) within 5% of 1; band N_T 145090, N_E 101851, N_D 250489, 45 of 50 bins)
| feature | KS D vs T(band) | p | AUC | KS D vs E(band) | AUC D vs E(band) | agrees with Phase 2 |
|---|---|---|---|---|---|---|
| protein_peer_count | 0.1930 | 0.0e+00 | 0.6232 | 0.0684 | 0.4555 | True |
| retentiontime | 0.0160 | 7.1e-21 | 0.4911 | 0.0304 | 0.5195 | True |
| frag_tail_frac | 0.0289 | 4.3e-67 | 0.5148 | 0.0295 | 0.5162 | True |
| rt_z | 0.0078 | 3.2e-05 | 0.5047 | 0.0196 | 0.4886 | False |
| rt_refined_signed | 0.0099 | 3.4e-08 | 0.5061 | 0.0184 | 0.4880 | True |
| rt_signed | 0.0061 | 2.0e-03 | 0.5036 | 0.0179 | 0.4911 | False |
| shadow_y_missing_per_residue | 0.0076 | 4.6e-05 | 0.4965 | 0.0148 | 0.5094 | True |
| shadow_all_missing_per_residue | 0.0022 | 7.7e-01 | 0.5005 | 0.0139 | 0.5094 | False |
| intact_y_missing_per_residue | 0.0078 | 2.9e-05 | 0.4960 | 0.0134 | 0.5083 | True |
| intact_all_missing_per_residue | 0.0023 | 7.4e-01 | 0.5001 | 0.0126 | 0.5085 | False |
| {ion_kurt_ab+ion_kurt_b+ion_kurt_a} | nan | nan | 0.8223 | nan | nan | True |

## Phase 6 (Spearman rho with passing peptides on same protein, baseline q<=1%)
| feature | rho | flag |
|---|---|---|
| protein_peer_count | 0.891 | True |
| retentiontime | 0.021 | False |
| frag_tail_frac | 0.081 | False |
| rt_z | -0.026 | False |
| rt_refined_signed | -0.031 | False |
| rt_signed | -0.030 | False |
| shadow_y_missing_per_residue | -0.401 | True |
| shadow_all_missing_per_residue | -0.413 | True |
| intact_y_missing_per_residue | -0.389 | True |
| intact_all_missing_per_residue | -0.406 | True |
| {ion_kurt_ab+ion_kurt_b+ion_kurt_a} | 0.003 | False |

## Phase 7 (LR for candidates with LR B combined FDP above A's upper bound; LR and GB for priority features)
Condition-A solve wall-clock: LR 4.3 s, GB 16.1 s.

| feature | combined FDP at 0/25/50/75/100% permuted | monotone |
|---|---|---|
| frag_tail_frac (GB) | 17.290% / 3.221% / 1.278% / 1.232% / 1.173% | True |
| {ion_kurt_ab+ion_kurt_b+ion_kurt_a} (GB) | 15.169% / 1.875% / 1.246% / 1.194% / 1.221% | True |

## Candidates
| feature | KS | FDP A (LR/GB) | FDP B (LR/GB) | FDP C (LR/GB) | third-null KS | entrapment-blind flag | linear vs boosted inflation (B-A, pp) | dose monotone | peptides lost if dropped (LR/GB) |
|---|---|---|---|---|---|---|---|---|---|
| protein_peer_count | 0.0680 | 0.89% / 1.19% | 0.66% / 0.66% | 0.90% / 1.17% | 0.1930 | Y | -0.23 / -0.53 | n/a / n/a | 2097 / 1008 |
| retentiontime | 0.0303 | 0.89% / 1.19% | 0.89% / 1.27% | 0.89% / 1.21% | 0.0160 | N | -0.00 / +0.08 | n/a / n/a | 3 / 107 |
| frag_tail_frac | 0.0295 | 0.89% / 1.19% | 1.05% / 17.29% | 0.88% / 1.17% | 0.0289 | N | +0.15 / +16.10 | n/a / y | -1 / 3422 |
| rt_z | 0.0197 | 0.89% / 1.19% | 0.89% / 1.22% | 0.89% / 1.23% | 0.0078 | N | -0.00 / +0.03 | n/a / n/a | 26 / -23 |
| rt_refined_signed | 0.0187 | 0.89% / 1.19% | 0.89% / 1.18% | 0.90% / 1.20% | 0.0099 | N | -0.00 / -0.01 | n/a / n/a | 3 / 49 |
| rt_signed | 0.0179 | 0.89% / 1.19% | 0.89% / skip | 0.90% / skip | 0.0061 | N | -0.00 / skip | n/a / n/a | 9 / skip |
| shadow_y_missing_per_residue | 0.0147 | 0.89% / 1.19% | 0.92% / skip | 0.88% / skip | 0.0076 | Y | +0.03 / skip | n/a / n/a | 9 / skip |
| shadow_all_missing_per_residue | 0.0136 | 0.89% / 1.19% | 0.92% / skip | 0.88% / skip | 0.0022 | Y | +0.03 / skip | n/a / n/a | 21 / skip |
| intact_y_missing_per_residue | 0.0131 | 0.89% / 1.19% | 0.92% / skip | 0.89% / skip | 0.0078 | Y | +0.03 / skip | n/a / n/a | 9 / skip |
| intact_all_missing_per_residue | 0.0120 | 0.89% / 1.19% | 0.92% / skip | 0.88% / skip | 0.0023 | Y | +0.03 / skip | n/a / n/a | 21 / skip |
| {ion_kurt_ab+ion_kurt_b+ion_kurt_a} | 0.0036 | 0.89% / 1.19% | 0.89% / 15.17% | 0.88% / 1.22% | nan | N | +0.00 / +13.98 | n/a / y | -3 / 2839 |

## Verdicts
- CONFIRMED: frag_tail_frac, {ion_kurt_ab+ion_kurt_b+ion_kurt_a}
- REJECTED: retentiontime (causal-), rt_z (causal-, third-null-), rt_refined_signed (causal-), rt_signed (causal-, third-null-)
- UNRESOLVED: protein_peer_count, shadow_y_missing_per_residue, shadow_all_missing_per_residue, intact_y_missing_per_residue, intact_all_missing_per_residue

## CHARACTERIZATION
Baseline: combined FDP at nominal 1% is 1.45% [1.27, 1.65], so the baseline is anti-conservative (interval above 1%). Single features: the largest Phase 2 KS is 0.068 (protein_peer_count); CONFIRMED: frag_tail_frac, {ion_kurt_ab+ion_kurt_b+ion_kurt_a} (B combined 17.29%, 15.17%). UNRESOLVED: protein_peer_count, shadow_y_missing_per_residue, shadow_all_missing_per_residue, intact_y_missing_per_residue, intact_all_missing_per_residue; Phase 6 flags protein_peer_count, shadow_y_missing_per_residue, shadow_all_missing_per_residue, intact_y_missing_per_residue, intact_all_missing_per_residue (|rho| 0.89, 0.40, 0.41, 0.39, 0.41). Combinations: the joint decoy-vs-entrapment classifier reaches AUC 0.821 on all features and 0.817 after both removals (joint signal; carriers ion_kurt_ab, ion_kurt_b, ion_kurt_a). Learner: condition A gives combined FDP 0.89% [0.74, 1.07] with logistic regression and 1.19% [1.03, 1.38] with boosting, so the boosted learner runs hotter on the same features.
