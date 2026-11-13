# PIN audit: eval (seed 0)

## INPUTS
```
PIN path:                 instances/I4/eval.parquet (release asset)
Decoy marker:             Label == -1 (proteins prefixed 'decoy_'; label/prefix mismatches: 0)
Entrapment marker:        protein accession prefix 'entrap_ATH_'; rows on 'entrap_' proteins without 'entrap_ATH_' (and decoys derived from them) excluded before competition: class X
Entrapment type:          foreign species (Arabidopsis thaliana proteome)
r (entrapment/target db): 0.666 (peptide level)
Primary score column:     mlp_score
Spectrum key columns:     ScanNr, ExpMass
Scorer-banned features:   none known
```

Parquet sha256 d254b2b8271cd0f7d745e6161113da874f6e110bcd603b0948b41daded871100 (655 MB); raw 1096705 rows x 126 cols; rows without score 0. Boosted model: lightgbm 3.3.5 LGBMClassifier defaults (n_jobs=8, verbose=-1). Logistic: mean-impute + standardize (train fold), L2 logistic regression with sklearn's default objective (C=1) solved by Newton to max|step| < 1e-3 (max 30 iterations). Folds: 5, grouped by I/L bare sequence, seeded group permutation (seed 0). Total runtime 5.4 min.

## Phase 0
| class | rows | peptides |
|---|---|---|
| T | 246983 | 181172 |
| E | 129089 | 100067 |
| D | 331613 | 250718 |
| B | 0 | excluded |
| X | 389020 | excluded |

Spectra after (ScanNr, ExpMass) competition: 642852. Wall-clock per phase (s): phase0 16.3, phase1 10.6, phase2 17.6, phase5 2.4, phase6 0.8, phase4 163.3, phase7 29.8, phase3 83.5

## Phase 1 (primary score, peptide-level TDC q=(D+1)/(T+E))
| q | N_T | N_E | N_D | lower FDP [95%] | combined FDP [95%] |
|---|---|---|---|---|---|
| 0.1% | 19424 | 0 | 18 | 0.000% [0.000, 0.020] | 0.000% [0.000, 0.049] |
| 0.5% | 33101 | 19 | 164 | 0.057% [0.037, 0.090] | 0.144% [0.092, 0.224] |
| 1.0% | 35871 | 57 | 358 | 0.159% [0.122, 0.205] | 0.397% [0.306, 0.514] |
| 2.0% | 37679 | 160 | 755 | 0.423% [0.362, 0.493] | 1.058% [0.906, 1.234] |
| 5.0% | 39451 | 641 | 2003 | 1.599% [1.481, 1.726] | 3.999% [3.704, 4.318] |

## Phase 2 (decoy vs entrapment; 111 features; composition by name regex `(?i)^(len|length|peplen|charge\d*|calcmass|pepmass|missed_cleavages|n_mods|enzn|enzc|enzint|ntt)$`)
| feature | comp | KS | KS p | SMD | AUC E/D | AUC T/D |
|---|---|---|---|---|---|---|
| residue_bias_idx |  | 0.1055 | 0.0e+00 | 0.258 | 0.5700 | 0.4935 |
| frag_rank_tail |  | 0.0333 | 2.7e-69 | 0.086 | 0.5212 | 0.5553 |
| retentiontime |  | 0.0296 | 1.1e-54 | 0.065 | 0.5184 | 0.4925 |
| rt_refined_signed |  | 0.0215 | 4.1e-29 | -0.045 | 0.4864 | 0.4885 |
| rt_signed |  | 0.0182 | 4.8e-21 | -0.034 | 0.4902 | 0.4920 |
| rt_z |  | 0.0180 | 1.8e-20 | -0.040 | 0.4878 | 0.4916 |
| shadow_y_missing_per_residue |  | 0.0144 | 3.1e-13 | 0.026 | 0.5073 | 0.4411 |
| n_mods | C | 0.0139 | 1.9e-12 | 0.034 | 0.5071 | 0.4887 |
| intact_b_used_per_residue |  | 0.0130 | 5.9e-11 | -0.027 | 0.4932 | 0.5300 |
| shadow_b_used_per_residue |  | 0.0125 | 3.8e-10 | -0.026 | 0.4933 | 0.5318 |
| shadow_all_used_fraction |  | 0.0121 | 1.7e-09 | -0.029 | 0.4920 | 0.5614 |
| intact_y_missing_per_residue |  | 0.0117 | 5.6e-09 | 0.025 | 0.5069 | 0.4420 |
| delta_RT_loess |  | 0.0117 | 6.9e-09 | -0.017 | 0.4939 | 0.4515 |
| intact_all_used_fraction |  | 0.0109 | 8.4e-08 | -0.026 | 0.4929 | 0.5607 |
| shadow_all_used_per_residue |  | 0.0106 | 2.2e-07 | -0.026 | 0.4936 | 0.5598 |
| rank_mean |  | 0.0101 | 8.4e-07 | -0.018 | 0.4945 | 0.4825 |
| missed_cleavages | C | 0.0101 | 9.1e-07 | 0.019 | 0.5053 | 0.4659 |
| frac_intensity |  | 0.0099 | 1.6e-06 | 0.013 | 0.5044 | 0.5315 |
| n_peaks |  | 0.0098 | 2.2e-06 | -0.014 | 0.4954 | 0.5134 |
| intact_all_used_per_residue |  | 0.0095 | 5.4e-06 | -0.023 | 0.4946 | 0.5591 |
| joint_fraction |  | 0.0094 | 5.8e-06 | -0.007 | 0.5036 | 0.5657 |
| joint_log_fraction |  | 0.0094 | 5.8e-06 | 0.011 | 0.5036 | 0.5657 |
| frag_good_frac |  | 0.0093 | 7.9e-06 | -0.026 | 0.4933 | 0.5614 |
| shadow_y_used_fraction |  | 0.0089 | 2.2e-05 | -0.017 | 0.4949 | 0.5632 |
| pred_matched_fraction |  | 0.0088 | 2.8e-05 | -0.019 | 0.4957 | 0.5650 |
| intact_all_explained_prediction |  | 0.0088 | 2.8e-05 | -0.019 | 0.4957 | 0.5650 |
| intact_y_explained_prediction |  | 0.0087 | 3.9e-05 | -0.022 | 0.4945 | 0.5635 |
| shadow_y_explained_prediction |  | 0.0087 | 4.2e-05 | -0.022 | 0.4947 | 0.5642 |
| intact_b_angle |  | 0.0086 | 5.1e-05 | 0.014 | 0.5038 | 0.5473 |
| shadow_all_missing_per_residue |  | 0.0085 | 7.1e-05 | 0.023 | 0.5060 | 0.4396 |
| CalcMass | C | 0.0083 | 9.8e-05 | 0.017 | 0.5053 | 0.4763 |
| b_angle |  | 0.0082 | 1.2e-04 | 0.012 | 0.5034 | 0.5444 |
| shadow_all_explained_prediction |  | 0.0081 | 1.7e-04 | -0.020 | 0.4957 | 0.5655 |
| intact_all_missing_per_residue |  | 0.0081 | 1.8e-04 | 0.022 | 0.5058 | 0.4404 |
| shadow_b_angle |  | 0.0078 | 3.4e-04 | 0.013 | 0.5035 | 0.5478 |
| longest_series |  | 0.0074 | 7.7e-04 | -0.014 | 0.4957 | 0.5515 |
| len | C | 0.0074 | 7.8e-04 | 0.014 | 0.5043 | 0.4760 |
| comp_pairs |  | 0.0073 | 9.3e-04 | -0.019 | 0.4962 | 0.5544 |
| frag_llr_presence |  | 0.0072 | 1.1e-03 | -0.019 | 0.4955 | 0.5640 |
| intact_y_used_fraction |  | 0.0072 | 1.3e-03 | -0.015 | 0.4956 | 0.5622 |
| frag_int_resid_mean |  | 0.0071 | 1.4e-03 | 0.013 | 0.5036 | 0.5113 |
| frag_wgood |  | 0.0071 | 1.4e-03 | -0.017 | 0.4965 | 0.5634 |
| frag_int_resid_sd |  | 0.0070 | 1.8e-03 | -0.011 | 0.4966 | 0.4615 |
| frag_log_ions |  | 0.0067 | 3.0e-03 | -0.006 | 0.4985 | 0.5475 |
| shadow_y_coverage_angle |  | 0.0066 | 4.1e-03 | -0.017 | 0.4962 | 0.5646 |
| frag_llr |  | 0.0065 | 4.8e-03 | -0.007 | 0.4959 | 0.5633 |
| frac_linear |  | 0.0064 | 5.9e-03 | 0.010 | 0.5035 | 0.5330 |
| spectral_contrast_angle |  | 0.0063 | 6.4e-03 | 0.003 | 0.5022 | 0.5564 |
| ambiguity |  | 0.0063 | 6.5e-03 | 0.013 | 0.5032 | 0.4965 |
| joint_shadow_angle |  | 0.0059 | 1.3e-02 | 0.013 | 0.5033 | 0.5541 |
| charge | C | 0.0059 | 1.4e-02 | 0.018 | 0.5044 | 0.4712 |
| n_matched |  | 0.0059 | 1.4e-02 | -0.016 | 0.4960 | 0.5538 |
| shadow_all_angle |  | 0.0059 | 1.5e-02 | 0.002 | 0.5020 | 0.5620 |
| intact_b_used_fraction |  | 0.0058 | 1.5e-02 | -0.011 | 0.4968 | 0.5381 |
| score_surprise |  | 0.0058 | 1.6e-02 | -0.008 | 0.4976 | 0.5566 |
| resid_mean |  | 0.0058 | 1.8e-02 | 0.006 | 0.5019 | 0.4948 |
| intact_all_angle |  | 0.0057 | 1.8e-02 | 0.002 | 0.5018 | 0.5565 |
| shadow_all_coverage_angle |  | 0.0057 | 1.9e-02 | -0.017 | 0.4977 | 0.5655 |
| joint_drop_gain |  | 0.0057 | 2.0e-02 | -0.005 | 0.5026 | 0.5615 |
| shadow_y_used_per_residue |  | 0.0055 | 2.5e-02 | -0.014 | 0.4969 | 0.5631 |
| shadow_y_angle |  | 0.0055 | 2.6e-02 | -0.014 | 0.4975 | 0.5585 |
| explained_intensity |  | 0.0054 | 3.1e-02 | 0.006 | 0.5023 | 0.5394 |
| intact_y_coverage_angle |  | 0.0054 | 3.2e-02 | -0.014 | 0.4972 | 0.5623 |
| intact_all_coverage_angle |  | 0.0054 | 3.3e-02 | -0.015 | 0.4982 | 0.5634 |
| n_cands |  | 0.0054 | 3.3e-02 | -0.012 | 0.4964 | 0.5002 |
| hyperscore |  | 0.0053 | 3.4e-02 | -0.009 | 0.4975 | 0.5515 |
| shadow_b_used_fraction |  | 0.0053 | 3.8e-02 | -0.010 | 0.4970 | 0.5395 |
| ms1_cycles |  | 0.0051 | 4.5e-02 | -0.009 | 0.4982 | 0.5366 |
| intact_all_error_rms_ppm |  | 0.0051 | 5.0e-02 | 0.004 | 0.5012 | 0.4738 |
| log_tic |  | 0.0051 | 5.1e-02 | -0.006 | 0.4982 | 0.5149 |
| ms1_log_intensity |  | 0.0050 | 5.2e-02 | -0.001 | 0.4985 | 0.5349 |
| ms1_isotope_kl |  | 0.0050 | 5.8e-02 | 0.008 | 0.5017 | 0.4999 |
| envelope_cos |  | 0.0049 | 6.0e-02 | -0.006 | 0.4984 | 0.5471 |
| unweighted_spectral_entropy |  | 0.0049 | 6.1e-02 | -0.009 | 0.4987 | 0.5642 |
| frag_good |  | 0.0049 | 6.8e-02 | -0.016 | 0.4963 | 0.5622 |
| frag_top6_good |  | 0.0048 | 7.1e-02 | -0.014 | 0.4964 | 0.5628 |
| y_angle |  | 0.0047 | 8.7e-02 | -0.012 | 0.4982 | 0.5528 |
| shadow_all_error_rms_ppm |  | 0.0047 | 8.9e-02 | 0.003 | 0.5008 | 0.4750 |
| rank |  | 0.0046 | 9.8e-02 | 0.006 | 0.5018 | 0.4432 |
| top_hits |  | 0.0046 | 9.8e-02 | 0.010 | 0.5028 | 0.5288 |
| intact_y_angle |  | 0.0046 | 1.0e-01 | -0.011 | 0.4983 | 0.5528 |
| score_rank_aux |  | 0.0045 | 1.1e-01 | -0.008 | 0.4977 | 0.5491 |
| intact_y_used_per_residue |  | 0.0045 | 1.1e-01 | -0.011 | 0.4980 | 0.5624 |
| primary_score |  | 0.0045 | 1.1e-01 | -0.010 | 0.4974 | 0.5570 |
| delta_next |  | 0.0043 | 1.5e-01 | 0.002 | 0.5011 | 0.5410 |
| intact_b_error_rms_ppm |  | 0.0042 | 1.7e-01 | -0.000 | 0.4989 | 0.4873 |
| frag_llr_mass |  | 0.0041 | 1.7e-01 | 0.001 | 0.4987 | 0.5453 |
| pearson_corr |  | 0.0041 | 1.8e-01 | 0.005 | 0.5017 | 0.5491 |
| shadow_y_error_rms_ppm |  | 0.0041 | 1.9e-01 | 0.001 | 0.4997 | 0.4892 |
| joint_interference |  | 0.0037 | 3.0e-01 | 0.000 | 0.5002 | 0.4517 |
| shadow_b_error_rms_ppm |  | 0.0036 | 3.0e-01 | -0.001 | 0.4988 | 0.4888 |
| rt_refined_abs |  | 0.0036 | 3.2e-01 | -0.004 | 0.5003 | 0.4419 |
| frag_z2_mean |  | 0.0035 | 3.5e-01 | -0.002 | 0.5008 | 0.4927 |
| intact_b_missing_per_residue |  | 0.0035 | 3.5e-01 | 0.001 | 0.4999 | 0.4633 |
| joint_log_intensity |  | 0.0034 | 4.0e-01 | 0.004 | 0.5011 | 0.5639 |
| ms1_coelution |  | 0.0032 | 4.5e-01 | -0.002 | 0.4995 | 0.5408 |
| shadow_b_missing_per_residue |  | 0.0032 | 4.7e-01 | 0.001 | 0.4997 | 0.4623 |
| shadow_b_coverage_angle |  | 0.0030 | 5.5e-01 | 0.003 | 0.5006 | 0.5488 |
| intact_y_error_rms_ppm |  | 0.0030 | 5.5e-01 | 0.001 | 0.5000 | 0.4861 |
| matched_ppm_rms |  | 0.0030 | 5.5e-01 | 0.000 | 0.5004 | 0.4725 |
| intact_b_coverage_angle |  | 0.0028 | 6.2e-01 | 0.004 | 0.5006 | 0.5477 |
| shadow_b_explained_prediction |  | 0.0028 | 6.3e-01 | 0.002 | 0.5005 | 0.5435 |
| intact_b_explained_prediction |  | 0.0027 | 6.6e-01 | 0.001 | 0.5003 | 0.5421 |
| resid_sd |  | 0.0025 | 7.6e-01 | 0.001 | 0.5001 | 0.4709 |
| delta_mass_ppm |  | 0.0025 | 7.7e-01 | 0.001 | 0.4998 | 0.4976 |
| ms1_apex_delta |  | 0.0021 | 9.1e-01 | 0.001 | 0.5001 | 0.5097 |
| purity |  | 0.0016 | 9.9e-01 | 0.001 | 0.5000 | 0.5409 |
| frag_iso_frac |  | 0.0014 | 1.0e+00 | 0.004 | 0.5003 | 0.5066 |
| unexplained_max |  | 0.0010 | 1.0e+00 | -0.003 | 0.4996 | 0.4886 |
| joint_untyped_prediction_fraction |  | 0.0002 | 1.0e+00 | 0.004 | 0.4999 | 0.4999 |
| precursor_missing |  | 0.0001 | 1.0e+00 | -0.000 | 0.4999 | 0.4764 |

## Phase 3 (boosted decoy vs entrapment, 5-fold grouped)
| features | n | AUC [95%] | bits/row below chance (SE) | total bits | significant |
|---|---|---|---|---|---|
| all | 111 | 0.5948 [0.5927, 0.5969] | 0.02581 (0.00105) | 9052.8 | True |
| minus_composition | 106 | 0.5945 [0.5923, 0.5966] | 0.02542 (0.00105) | 8918.6 | True |
| minus_composition_and_top5 | 101 | 0.5234 [0.5213, 0.5255] | 0.00063 (0.00102) | 221.1 | False |

Joint leak: False. Carriers: none. Permutation importance (AUC drop, minus_composition_and_top5): rt_z 0.0109±0.0020, rt_refined_abs 0.0072±0.0014, delta_RT_loess 0.0059±0.0015, shadow_y_explained_prediction 0.0017±0.0001, shadow_y_missing_per_residue 0.0017±0.0007, ambiguity 0.0016±0.0003, joint_shadow_angle 0.0014±0.0006, intact_b_used_per_residue 0.0013±0.0008

## Phase 4 (rescoring T+E vs D, OOF; A = 101 features)
| cond | model | feature | N_T | N_E | N_D | lower FDP | combined FDP [95%] |
|---|---|---|---|---|---|---|---|
| A | LR | - | 29178 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| A | GB | - | 34539 | 62 | 345 | 0.179% | 0.45% [0.35, 0.57] |
| B | LR | residue_bias_idx | 29183 | 66 | 291 | 0.226% | 0.56% [0.44, 0.72] |
| C | LR | residue_bias_idx | 29161 | 68 | 291 | 0.233% | 0.58% [0.46, 0.74] |
| B | GB | residue_bias_idx | 34515 | 67 | 344 | 0.194% | 0.48% [0.38, 0.62] |
| C | GB | residue_bias_idx | 34580 | 61 | 345 | 0.176% | 0.44% [0.34, 0.57] |
| B | LR | frag_rank_tail | 29632 | 73 | 296 | 0.246% | 0.61% [0.49, 0.77] |
| C | LR | frag_rank_tail | 29160 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| B | GB | frag_rank_tail | 35469 | 1012 | 363 | 2.774% | 6.94% [6.53, 7.37] |
| C | GB | frag_rank_tail | 34453 | 62 | 344 | 0.180% | 0.45% [0.35, 0.58] |
| B | LR | retentiontime | 29190 | 68 | 291 | 0.232% | 0.58% [0.46, 0.74] |
| C | LR | retentiontime | 29167 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| B | GB | retentiontime | 34598 | 66 | 345 | 0.190% | 0.48% [0.37, 0.61] |
| C | GB | retentiontime | 34490 | 66 | 344 | 0.191% | 0.48% [0.38, 0.61] |
| B | LR | rt_refined_signed | 29149 | 65 | 291 | 0.222% | 0.56% [0.44, 0.71] |
| C | LR | rt_refined_signed | 29156 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| B | GB | rt_refined_signed | 34513 | 65 | 344 | 0.188% | 0.47% [0.37, 0.60] |
| C | GB | rt_refined_signed | 34513 | 61 | 344 | 0.176% | 0.44% [0.34, 0.57] |
| B | LR | rt_signed | 29159 | 65 | 291 | 0.222% | 0.56% [0.44, 0.71] |
| C | LR | rt_signed | 29150 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| B | GB | rt_signed | 34609 | 65 | 345 | 0.187% | 0.47% [0.37, 0.60] |
| C | GB | rt_signed | 34654 | 66 | 346 | 0.190% | 0.48% [0.37, 0.60] |
| B | LR | rt_z | 29192 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| C | LR | rt_z | 29163 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| B | LR | shadow_y_missing_per_residue | 29178 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| C | LR | shadow_y_missing_per_residue | 29152 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| B | LR | n_mods | 29173 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| C | LR | n_mods | 29170 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| B | LR | intact_b_used_per_residue | 29180 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| C | LR | intact_b_used_per_residue | 29222 | 69 | 291 | 0.236% | 0.59% [0.47, 0.75] |
| B | LR | shadow_b_used_per_residue | 29180 | 67 | 291 | 0.229% | 0.57% [0.45, 0.73] |
| C | LR | shadow_b_used_per_residue | 29209 | 68 | 291 | 0.232% | 0.58% [0.46, 0.74] |
| B/C | GB | rt_z | boosted: skipped (time) | | | | |
| B/C | GB | shadow_y_missing_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | n_mods | boosted: skipped (time) | | | | |
| B/C | GB | intact_b_used_per_residue | boosted: skipped (time) | | | | |
| B/C | GB | shadow_b_used_per_residue | boosted: skipped (time) | | | | |

## Phase 5 (third null: 50 primary-score quantile bins with D/(T+E) within 5% of 1; band N_T 111300, N_E 78009, N_D 193699, 36 of 50 bins)
| feature | KS D vs T(band) | p | AUC | KS D vs E(band) | AUC D vs E(band) | agrees with Phase 2 |
|---|---|---|---|---|---|---|
| residue_bias_idx | 0.0739 | 0.0e+00 | 0.4504 | 0.1062 | 0.5703 | True |
| frag_rank_tail | 0.0335 | 3.7e-69 | 0.5205 | 0.0317 | 0.5194 | True |
| retentiontime | 0.0193 | 2.9e-23 | 0.4896 | 0.0285 | 0.5177 | True |
| rt_refined_signed | 0.0092 | 1.3e-05 | 0.5043 | 0.0215 | 0.4860 | False |
| rt_signed | 0.0051 | 5.3e-02 | 0.5025 | 0.0188 | 0.4899 | False |
| rt_z | 0.0057 | 2.1e-02 | 0.5032 | 0.0192 | 0.4875 | False |
| shadow_y_missing_per_residue | 0.0090 | 2.1e-05 | 0.4942 | 0.0147 | 0.5074 | True |
| n_mods | 0.0048 | 7.8e-02 | 0.4975 | 0.0158 | 0.5081 | False |
| intact_b_used_per_residue | 0.0083 | 1.1e-04 | 0.4949 | 0.0117 | 0.4941 | True |
| shadow_b_used_per_residue | 0.0084 | 8.6e-05 | 0.4950 | 0.0115 | 0.4942 | True |

## Phase 6 (Spearman rho with passing peptides on same protein, baseline q<=1%)
| feature | rho | flag |
|---|---|---|
| residue_bias_idx | 0.012 | False |
| frag_rank_tail | 0.211 | True |
| retentiontime | 0.031 | False |
| rt_refined_signed | -0.018 | False |
| rt_signed | -0.008 | False |
| rt_z | -0.008 | False |
| shadow_y_missing_per_residue | -0.384 | True |
| n_mods | 0.052 | False |
| intact_b_used_per_residue | 0.208 | True |
| shadow_b_used_per_residue | 0.211 | True |

## Phase 7 (LR for candidates with LR B combined FDP above A's upper bound; LR and GB for priority features)
Condition-A solve wall-clock: LR 4.4 s, GB 14.7 s.

| feature | combined FDP at 0/25/50/75/100% permuted | monotone |
|---|---|---|
| frag_rank_tail (GB) | 6.939% / 1.584% / 0.569% / 0.491% / 0.449% | True |

## Candidates
| feature | KS | FDP A (LR/GB) | FDP B (LR/GB) | FDP C (LR/GB) | third-null KS | entrapment-blind flag | linear vs boosted inflation (B-A, pp) | dose monotone | peptides lost if dropped (LR/GB) |
|---|---|---|---|---|---|---|---|---|---|
| residue_bias_idx | 0.1055 | 0.57% / 0.45% | 0.56% / 0.48% | 0.58% / 0.44% | 0.0739 | N | -0.01 / +0.04 | n/a / n/a | 5 / -24 |
| frag_rank_tail | 0.0333 | 0.57% / 0.45% | 0.61% / 6.94% | 0.57% / 0.45% | 0.0335 | Y | +0.04 / +6.49 | n/a / y | 454 / 930 |
| retentiontime | 0.0296 | 0.57% / 0.45% | 0.58% / 0.48% | 0.57% / 0.48% | 0.0193 | N | +0.01 / +0.03 | n/a / n/a | 12 / 59 |
| rt_refined_signed | 0.0215 | 0.57% / 0.45% | 0.56% / 0.47% | 0.57% / 0.44% | 0.0092 | N | -0.02 / +0.02 | n/a / n/a | -29 / -26 |
| rt_signed | 0.0182 | 0.57% / 0.45% | 0.56% / 0.47% | 0.57% / 0.48% | 0.0051 | N | -0.02 / +0.02 | n/a / n/a | -19 / 70 |
| rt_z | 0.0180 | 0.57% / 0.45% | 0.57% / skip | 0.57% / skip | 0.0057 | N | -0.00 / skip | n/a / n/a | 14 / skip |
| shadow_y_missing_per_residue | 0.0144 | 0.57% / 0.45% | 0.57% / skip | 0.57% / skip | 0.0090 | Y | +0.00 / skip | n/a / n/a | 0 / skip |
| n_mods | 0.0139 | 0.57% / 0.45% | 0.57% / skip | 0.57% / skip | 0.0048 | N | +0.00 / skip | n/a / n/a | -5 / skip |
| intact_b_used_per_residue | 0.0130 | 0.57% / 0.45% | 0.57% / skip | 0.59% / skip | 0.0083 | Y | -0.00 / skip | n/a / n/a | 2 / skip |
| shadow_b_used_per_residue | 0.0125 | 0.57% / 0.45% | 0.57% / skip | 0.58% / skip | 0.0084 | Y | -0.00 / skip | n/a / n/a | 2 / skip |

## Verdicts
- CONFIRMED: none
- REJECTED: residue_bias_idx (causal-), retentiontime (causal-), rt_refined_signed (causal-, third-null-), rt_signed (causal-, third-null-), rt_z (causal-, third-null-), n_mods (causal-, third-null-)
- UNRESOLVED: frag_rank_tail, shadow_y_missing_per_residue, intact_b_used_per_residue, shadow_b_used_per_residue

## CHARACTERIZATION
Baseline: combined FDP at nominal 1% is 0.40% [0.31, 0.51], so the baseline is conservative (interval below 1%). Single features: the largest Phase 2 KS is 0.105 (residue_bias_idx); no candidate is CONFIRMED. UNRESOLVED: frag_rank_tail, shadow_y_missing_per_residue, intact_b_used_per_residue, shadow_b_used_per_residue; Phase 6 flags frag_rank_tail, shadow_y_missing_per_residue, intact_b_used_per_residue, shadow_b_used_per_residue (|rho| 0.21, 0.38, 0.21, 0.21). Combinations: the joint decoy-vs-entrapment classifier reaches AUC 0.595 on all features and 0.523 after both removals (below the joint-signal criterion). Learner: condition A gives combined FDP 0.57% [0.45, 0.73] with logistic regression and 0.45% [0.35, 0.57] with boosting, so the two learners agree within intervals.
