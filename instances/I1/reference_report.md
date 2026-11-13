# PIN audit: eval (seed 0)

## INPUTS
```
PIN path:                 instances/I1/eval.parquet (release asset)
Decoy marker:             Label == -1 (proteins prefixed 'decoy_'; label/prefix mismatches: 0)
Entrapment marker:        protein accession prefix 'entrap_ATH_'; rows on 'entrap_' proteins without 'entrap_ATH_' (and decoys derived from them) excluded before competition: class X
Entrapment type:          foreign species (Arabidopsis thaliana proteome)
r (entrapment/target db): 0.666 (peptide level)
Primary score column:     mlp_score
Spectrum key columns:     ScanNr, ExpMass
Scorer-banned features:   none known
```

Parquet sha256 6f9cbe94462fd1e599e58c7dcdfd8b37467daea8480eea8cea647cf0eb8c0106 (735 MB); raw 1120111 rows x 132 cols; rows without score 0. Boosted model: lightgbm 3.3.5 LGBMClassifier defaults (n_jobs=8, verbose=-1). Logistic: mean-impute + standardize (train fold), L2 logistic regression with sklearn's default objective (C=1) solved by Newton to max|step| < 1e-3 (max 30 iterations). Folds: 5, grouped by I/L bare sequence, seeded group permutation (seed 0). Total runtime 7.7 min.

## Phase 0
| class | rows | peptides |
|---|---|---|
| T | 254638 | 189083 |
| E | 133490 | 105199 |
| D | 328644 | 258419 |
| B | 0 | excluded |
| X | 403339 | excluded |

Spectra after (ScanNr, ExpMass) competition: 672479. Wall-clock per phase (s): phase0 16.6, phase1 15.2, phase2 19.5, phase5 6.1, phase6 0.9, phase4 220.9, phase7 70.1, phase3 114.3

## Phase 1 (primary score, peptide-level TDC q=(D+1)/(T+E))
| q | N_T | N_E | N_D | lower FDP [95%] | combined FDP [95%] |
|---|---|---|---|---|---|
| 0.1% | 34502 | 30 | 33 | 0.087% [0.061, 0.124] | 0.217% [0.152, 0.310] |
| 0.5% | 37915 | 140 | 189 | 0.368% [0.312, 0.434] | 0.920% [0.780, 1.085] |
| 1.0% | 38615 | 225 | 387 | 0.579% [0.509, 0.660] | 1.449% [1.272, 1.651] |
| 2.0% | 39375 | 404 | 794 | 1.016% [0.922, 1.119] | 2.541% [2.306, 2.799] |
| 5.0% | 40717 | 1018 | 2085 | 2.439% [2.296, 2.592] | 6.102% [5.742, 6.483] |

## Phase 2 (decoy vs entrapment; 120 features; composition by name regex `(?i)^(len|length|peplen|charge\d*|calcmass|pepmass|missed_cleavages|n_mods|enzn|enzc|enzint|ntt)$`)
| feature | comp | KS | KS p | SMD | AUC E/D | AUC T/D |
|---|---|---|---|---|---|---|
| protein_support_n |  | 0.0621 | 6.6e-251 | -0.162 | 0.4626 | 0.6110 |
| frag_tail_ratio |  | 0.0305 | 5.5e-61 | 0.128 | 0.5147 | 0.5234 |
| retentiontime |  | 0.0303 | 3.3e-60 | 0.068 | 0.5192 | 0.4935 |
| rt_z |  | 0.0197 | 1.1e-25 | -0.038 | 0.4885 | 0.4915 |
| rt_refined_signed |  | 0.0187 | 4.0e-23 | -0.041 | 0.4879 | 0.4896 |
| rt_signed |  | 0.0179 | 3.8e-21 | -0.031 | 0.4911 | 0.4911 |
| shadow_y_missing_per_residue |  | 0.0147 | 1.8e-14 | 0.033 | 0.5091 | 0.4451 |
| shadow_all_missing_per_residue |  | 0.0136 | 1.8e-12 | 0.032 | 0.5090 | 0.4455 |
| mass_per_residue |  | 0.0131 | 1.2e-11 | 0.005 | 0.4988 | 0.5032 |
| intact_y_missing_per_residue |  | 0.0131 | 1.6e-11 | 0.029 | 0.5080 | 0.4452 |
| intact_all_missing_per_residue |  | 0.0120 | 1.0e-09 | 0.029 | 0.5080 | 0.4455 |
| delta_RT_loess |  | 0.0118 | 1.8e-09 | -0.017 | 0.4935 | 0.4504 |
| b_angle |  | 0.0110 | 3.3e-08 | 0.020 | 0.5057 | 0.5439 |
| joint_fraction |  | 0.0102 | 3.1e-07 | 0.008 | 0.5054 | 0.5659 |
| joint_log_fraction |  | 0.0102 | 3.1e-07 | 0.019 | 0.5054 | 0.5659 |
| frac_intensity |  | 0.0102 | 3.5e-07 | 0.016 | 0.5048 | 0.5319 |
| intact_b_angle |  | 0.0096 | 2.1e-06 | 0.016 | 0.5044 | 0.5452 |
| n_peaks |  | 0.0090 | 1.2e-05 | -0.011 | 0.4963 | 0.5127 |
| rank_mean |  | 0.0088 | 2.1e-05 | -0.018 | 0.4948 | 0.4817 |
| explained_intensity |  | 0.0087 | 2.3e-05 | 0.016 | 0.5051 | 0.5409 |
| joint_drop_gain |  | 0.0084 | 4.8e-05 | 0.000 | 0.5037 | 0.5609 |
| shadow_b_angle |  | 0.0081 | 1.0e-04 | 0.014 | 0.5039 | 0.5457 |
| seq_prior_ll |  | 0.0078 | 2.0e-04 | 0.005 | 0.5045 | 0.5204 |
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
| log_tic |  | 0.0048 | 6.7e-02 | -0.005 | 0.4985 | 0.5144 |
| pred_matched_fraction |  | 0.0047 | 7.2e-02 | -0.006 | 0.4990 | 0.5653 |
| intact_all_explained_prediction |  | 0.0047 | 7.2e-02 | -0.006 | 0.4990 | 0.5653 |
| intact_b_used_per_residue |  | 0.0047 | 7.6e-02 | -0.004 | 0.4989 | 0.5343 |
| intact_b_coverage_angle |  | 0.0047 | 7.7e-02 | 0.005 | 0.5022 | 0.5461 |
| n_cands |  | 0.0047 | 7.7e-02 | -0.011 | 0.4969 | 0.4995 |
| pair_ctx_v |  | 0.0046 | 8.0e-02 | -0.002 | 0.4996 | 0.4997 |
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
| n_matched |  | 0.0035 | 3.1e-01 | -0.007 | 0.4986 | 0.5536 |
| intact_y_error_rms_ppm |  | 0.0035 | 3.2e-01 | 0.001 | 0.5005 | 0.4867 |
| intact_all_error_rms_ppm |  | 0.0034 | 3.4e-01 | 0.005 | 0.5014 | 0.4746 |
| intact_b_used_fraction |  | 0.0034 | 3.6e-01 | -0.005 | 0.4986 | 0.5375 |
| shadow_y_used_per_residue |  | 0.0033 | 3.8e-01 | 0.005 | 0.5014 | 0.5651 |
| CalcMass | C | 0.0033 | 4.0e-01 | 0.003 | 0.5011 | 0.4736 |
| shadow_all_error_rms_ppm |  | 0.0033 | 4.0e-01 | 0.005 | 0.5013 | 0.4759 |
| frag_llr_presence |  | 0.0033 | 4.1e-01 | 0.006 | 0.5015 | 0.5665 |
| frag_llr_mass |  | 0.0032 | 4.1e-01 | -0.001 | 0.5002 | 0.5442 |
| resid_mean |  | 0.0031 | 4.5e-01 | 0.002 | 0.5008 | 0.4937 |
| ion_skew_by |  | 0.0031 | 4.6e-01 | 0.002 | 0.5010 | 0.5008 |
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
| ion_skew_b |  | 0.0027 | 6.3e-01 | 0.000 | 0.4999 | 0.5007 |
| pair_ctx_u |  | 0.0027 | 6.5e-01 | -0.001 | 0.4998 | 0.4998 |
| frag_top6_good |  | 0.0027 | 6.6e-01 | -0.003 | 0.4989 | 0.5624 |
| ms1_coelution |  | 0.0026 | 7.1e-01 | 0.002 | 0.5006 | 0.5396 |
| shadow_y_error_rms_ppm |  | 0.0024 | 7.8e-01 | -0.001 | 0.4998 | 0.4894 |
| pearson_corr |  | 0.0024 | 7.9e-01 | -0.001 | 0.5000 | 0.5463 |
| ion_skew_y |  | 0.0023 | 8.0e-01 | -0.003 | 0.4995 | 0.4997 |
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
| all | 120 | 0.6880 [0.6860, 0.6899] | 0.07142 (0.00099) | 25968.5 | True |
| minus_composition | 115 | 0.7613 [0.7594, 0.7631] | 0.12989 (0.00096) | 47231.9 | True |
| minus_composition_and_top5 | 110 | 0.8137 [0.8120, 0.8154] | 0.18590 (0.00090) | 67597.6 | True |

Joint leak: True. Carriers: ['ion_skew_by', 'ion_skew_b', 'ion_skew_y']. Permutation importance (AUC drop, minus_composition_and_top5): ion_skew_by 0.3114±0.0049, ion_skew_b 0.2005±0.0048, ion_skew_y 0.1992±0.0054, mass_per_residue 0.0015±0.0001, rt_signed 0.0007±0.0001, rt_refined_abs 0.0005±0.0001, delta_RT_loess 0.0003±0.0001, intact_y_used_per_residue 0.0003±0.0001

## Phase 4 (rescoring T+E vs D, OOF; A = 107 features)
| cond | model | feature | N_T | N_E | N_D | lower FDP | combined FDP [95%] |
|---|---|---|---|---|---|---|---|
| A | LR | - | 32441 | 119 | 324 | 0.365% | 0.91% [0.76, 1.09] |
| A | GB | - | 37174 | 189 | 372 | 0.506% | 1.27% [1.10, 1.46] |
| B | LR | protein_support_n | 35026 | 61 | 349 | 0.174% | 0.43% [0.34, 0.56] |
| C | LR | protein_support_n | 32447 | 123 | 324 | 0.378% | 0.94% [0.79, 1.13] |
| B | GB | protein_support_n | 40647 | 65 | 406 | 0.160% | 0.40% [0.31, 0.51] |
| C | GB | protein_support_n | 37176 | 187 | 372 | 0.500% | 1.25% [1.09, 1.44] |
| B | LR | frag_tail_ratio | 32412 | 129 | 324 | 0.396% | 0.99% [0.83, 1.18] |
| C | LR | frag_tail_ratio | 32433 | 121 | 324 | 0.372% | 0.93% [0.78, 1.11] |
| B | GB | frag_tail_ratio | 41323 | 3208 | 444 | 7.204% | 18.02% [17.43, 18.63] |
| C | GB | frag_tail_ratio | 37183 | 192 | 372 | 0.514% | 1.29% [1.12, 1.48] |
| B | LR | retentiontime | 32440 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | retentiontime | 32433 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| B | GB | retentiontime | 37161 | 188 | 372 | 0.503% | 1.26% [1.09, 1.45] |
| C | GB | retentiontime | 37155 | 192 | 372 | 0.514% | 1.29% [1.12, 1.48] |
| B | LR | rt_z | 32431 | 118 | 324 | 0.363% | 0.91% [0.76, 1.09] |
| C | LR | rt_z | 32439 | 119 | 324 | 0.366% | 0.91% [0.76, 1.09] |
| B | GB | rt_z | 37189 | 195 | 372 | 0.522% | 1.30% [1.13, 1.50] |
| C | GB | rt_z | 37202 | 188 | 372 | 0.503% | 1.26% [1.09, 1.45] |
| B | LR | rt_refined_signed | 32434 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| C | LR | rt_refined_signed | 32443 | 120 | 324 | 0.369% | 0.92% [0.77, 1.10] |
| B | GB | rt_refined_signed | 37137 | 183 | 372 | 0.490% | 1.23% [1.06, 1.42] |
| C | GB | rt_refined_signed | 37232 | 201 | 373 | 0.537% | 1.34% [1.17, 1.54] |
| B | LR | rt_signed | 32427 | 119 | 324 | 0.366% | 0.91% [0.76, 1.09] |
| C | LR | rt_signed | 32440 | 119 | 324 | 0.365% | 0.91% [0.76, 1.09] |
| B | LR | shadow_y_missing_per_residue | 32414 | 118 | 324 | 0.363% | 0.91% [0.76, 1.09] |
| C | LR | shadow_y_missing_per_residue | 32412 | 117 | 324 | 0.360% | 0.90% [0.75, 1.08] |
| B | LR | shadow_all_missing_per_residue | 32441 | 119 | 324 | 0.365% | 0.91% [0.76, 1.09] |
| C | LR | shadow_all_missing_per_residue | 32418 | 118 | 324 | 0.363% | 0.91% [0.76, 1.09] |
| B | LR | mass_per_residue | 32451 | 121 | 324 | 0.371% | 0.93% [0.78, 1.11] |
| C | LR | mass_per_residue | 32407 | 117 | 324 | 0.360% | 0.90% [0.75, 1.08] |
| B | LR | intact_y_missing_per_residue | 32414 | 118 | 324 | 0.363% | 0.91% [0.76, 1.09] |
| C | LR | intact_y_missing_per_residue | 32422 | 118 | 324 | 0.363% | 0.91% [0.76, 1.09] |
| B | LR | {ion_skew_by+ion_skew_b+ion_skew_y} | 32442 | 118 | 324 | 0.362% | 0.91% [0.76, 1.09] |
| C | LR | {ion_skew_by+ion_skew_b+ion_skew_y} | 32430 | 118 | 324 | 0.363% | 0.91% [0.76, 1.09] |
| B | GB | {ion_skew_by+ion_skew_b+ion_skew_y} | 39503 | 1811 | 412 | 4.384% | 10.97% [10.48, 11.47] |
| C | GB | {ion_skew_by+ion_skew_b+ion_skew_y} | 37204 | 198 | 373 | 0.529% | 1.32% [1.15, 1.52] |
| B/C | GB | rt_signed | boosted: skipped (time) | | | | |
| B/C | GB | shadow_y_missing_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | shadow_all_missing_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | mass_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | intact_y_missing_per_residue | boosted: skipped (time) | | | | |

## Phase 5 (third null: 50 primary-score quantile bins with D/(T+E) within 5% of 1; band N_T 145090, N_E 101851, N_D 250489, 45 of 50 bins)
| feature | KS D vs T(band) | p | AUC | KS D vs E(band) | AUC D vs E(band) | agrees with Phase 2 |
|---|---|---|---|---|---|---|
| protein_support_n | 0.2100 | 0.0e+00 | 0.6348 | 0.0624 | 0.4623 | True |
| frag_tail_ratio | 0.0302 | 2.1e-73 | 0.5148 | 0.0305 | 0.5149 | True |
| retentiontime | 0.0160 | 7.1e-21 | 0.4911 | 0.0304 | 0.5195 | True |
| rt_z | 0.0078 | 3.2e-05 | 0.5047 | 0.0196 | 0.4886 | False |
| rt_refined_signed | 0.0099 | 3.4e-08 | 0.5061 | 0.0184 | 0.4880 | True |
| rt_signed | 0.0061 | 2.0e-03 | 0.5036 | 0.0179 | 0.4911 | False |
| shadow_y_missing_per_residue | 0.0076 | 4.6e-05 | 0.4965 | 0.0148 | 0.5094 | True |
| shadow_all_missing_per_residue | 0.0022 | 7.7e-01 | 0.5005 | 0.0139 | 0.5094 | False |
| mass_per_residue | 0.0099 | 3.4e-08 | 0.5008 | 0.0132 | 0.4987 | True |
| intact_y_missing_per_residue | 0.0078 | 2.9e-05 | 0.4960 | 0.0134 | 0.5083 | True |
| {ion_skew_by+ion_skew_b+ion_skew_y} | nan | nan | 0.8203 | nan | nan | True |

## Phase 6 (Spearman rho with passing peptides on same protein, baseline q<=1%)
| feature | rho | flag |
|---|---|---|
| protein_support_n | 0.921 | True |
| frag_tail_ratio | 0.069 | False |
| retentiontime | 0.021 | False |
| rt_z | -0.026 | False |
| rt_refined_signed | -0.031 | False |
| rt_signed | -0.030 | False |
| shadow_y_missing_per_residue | -0.401 | True |
| shadow_all_missing_per_residue | -0.413 | True |
| mass_per_residue | 0.012 | False |
| intact_y_missing_per_residue | -0.389 | True |
| {ion_skew_by+ion_skew_b+ion_skew_y} | 0.006 | False |

## Phase 7 (LR for candidates with LR B combined FDP above A's upper bound; LR and GB for priority features)
Condition-A solve wall-clock: LR 3.7 s, GB 17.4 s.

| feature | combined FDP at 0/25/50/75/100% permuted | monotone |
|---|---|---|
| frag_tail_ratio (GB) | 18.021% / 3.524% / 1.313% / 1.260% / 1.285% | True |
| {ion_skew_by+ion_skew_b+ion_skew_y} (GB) | 10.965% / 1.721% / 1.309% / 1.265% / 1.324% | False |

## Candidates
| feature | KS | FDP A (LR/GB) | FDP B (LR/GB) | FDP C (LR/GB) | third-null KS | entrapment-blind flag | linear vs boosted inflation (B-A, pp) | dose monotone | peptides lost if dropped (LR/GB) |
|---|---|---|---|---|---|---|---|---|---|
| protein_support_n | 0.0621 | 0.91% / 1.27% | 0.43% / 0.40% | 0.94% / 1.25% | 0.2100 | Y | -0.48 / -0.87 | n/a / n/a | 2585 / 3473 |
| frag_tail_ratio | 0.0305 | 0.91% / 1.27% | 0.99% / 18.02% | 0.93% / 1.29% | 0.0302 | N | +0.08 / +16.76 | n/a / y | -29 / 4149 |
| retentiontime | 0.0303 | 0.91% / 1.27% | 0.92% / 1.26% | 0.92% / 1.29% | 0.0160 | N | +0.01 / -0.01 | n/a / n/a | -1 / -13 |
| rt_z | 0.0197 | 0.91% / 1.27% | 0.91% / 1.30% | 0.91% / 1.26% | 0.0078 | N | -0.01 / +0.04 | n/a / n/a | -10 / 15 |
| rt_refined_signed | 0.0187 | 0.91% / 1.27% | 0.92% / 1.23% | 0.92% / 1.34% | 0.0099 | N | +0.01 / -0.04 | n/a / n/a | -7 / -37 |
| rt_signed | 0.0179 | 0.91% / 1.27% | 0.91% / skip | 0.91% / skip | 0.0061 | N | +0.00 / skip | n/a / n/a | -14 / skip |
| shadow_y_missing_per_residue | 0.0147 | 0.91% / 1.27% | 0.91% / skip | 0.90% / skip | 0.0076 | Y | -0.01 / skip | n/a / n/a | -27 / skip |
| shadow_all_missing_per_residue | 0.0136 | 0.91% / 1.27% | 0.91% / skip | 0.91% / skip | 0.0022 | Y | +0.00 / skip | n/a / n/a | 0 / skip |
| mass_per_residue | 0.0131 | 0.91% / 1.27% | 0.93% / skip | 0.90% / skip | 0.0099 | N | +0.02 / skip | n/a / n/a | 10 / skip |
| intact_y_missing_per_residue | 0.0131 | 0.91% / 1.27% | 0.91% / skip | 0.91% / skip | 0.0078 | Y | -0.01 / skip | n/a / n/a | -27 / skip |
| {ion_skew_by+ion_skew_b+ion_skew_y} | 0.0031 | 0.91% / 1.27% | 0.91% / 10.97% | 0.91% / 1.32% | nan | N | -0.01 / +9.70 | n/a / n | 1 / 2329 |

## Verdicts
- CONFIRMED: frag_tail_ratio
- REJECTED: retentiontime (causal-), rt_z (causal-, third-null-), rt_refined_signed (causal-), rt_signed (causal-, third-null-), mass_per_residue (causal-)
- UNRESOLVED: protein_support_n, shadow_y_missing_per_residue, shadow_all_missing_per_residue, intact_y_missing_per_residue, {ion_skew_by+ion_skew_b+ion_skew_y}

## CHARACTERIZATION
Baseline: combined FDP at nominal 1% is 1.45% [1.27, 1.65], so the baseline is anti-conservative (interval above 1%). Single features: the largest Phase 2 KS is 0.062 (protein_support_n); CONFIRMED: frag_tail_ratio (B combined 18.02%). UNRESOLVED: protein_support_n, shadow_y_missing_per_residue, shadow_all_missing_per_residue, intact_y_missing_per_residue, {ion_skew_by+ion_skew_b+ion_skew_y}; Phase 6 flags protein_support_n, shadow_y_missing_per_residue, shadow_all_missing_per_residue, intact_y_missing_per_residue (|rho| 0.92, 0.40, 0.41, 0.39). Combinations: the joint decoy-vs-entrapment classifier reaches AUC 0.688 on all features and 0.814 after both removals (joint signal; carriers ion_skew_by, ion_skew_b, ion_skew_y). Learner: condition A gives combined FDP 0.91% [0.76, 1.09] with logistic regression and 1.27% [1.10, 1.46] with boosting, so the boosted learner runs hotter on the same features.
