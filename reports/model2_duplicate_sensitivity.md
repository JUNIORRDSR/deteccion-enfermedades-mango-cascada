# M2 duplicate sensitivity (AMENDMENT-04)

Principal estimand: `image_weighted` (weight 1 per file of the frozen test). Predefined secondaries on the same predictions: `exact_sha_dedup` (minimum image_id per SHA256) and `cluster_weighted` (1/n per cluster). No scheme is selected by performance.

Predictions `experiments\model2\EXP-R03\predictions.jsonl` sha256 `e3700dbfd429001039af1572cc0ee33f6e6b92cfd95d8ab0705d6dedf7fd321d`; manifest `data\manifests\model2_frozen_manifest.csv` sha256 `cd4f0d0e428fc3015268b7df541bf705261893c4b5cba0a7ef274e17d0680d92`.

Structure: 219 images, 208 unique SHA256, 203 clusters, 203 groups. n clusters and n groups describe operational dependence; they are not demonstrated biological independence nor an effective sample size.

| scheme | accuracy % | CI95 | macro F1 % | CI95 |
|---|---|---|---|---|
| image_weighted | 90.87 | 86.88 to 94.62 (0 undefined) | 90.95 | 86.94 to 94.47 (0 undefined) |
| exact_sha_dedup | 90.38 | 86.19 to 94.29 (0 undefined) | 90.64 | 86.46 to 94.30 (0 undefined) |
| cluster_weighted | 90.15 | 85.71 to 94.09 (0 undefined) | 90.45 | 86.16 to 94.23 (0 undefined) |

| secondary - principal | accuracy pp | CI95 pp | macro F1 pp | CI95 pp |
|---|---|---|---|---|
| exact_sha_dedup | -0.48 | -0.83 to -0.22 (0 undefined) | -0.30 | -0.60 to -0.09 (0 undefined) |
| cluster_weighted | -0.72 | -1.24 to -0.33 (0 undefined) | -0.50 | -0.95 to -0.17 (0 undefined) |

Bootstrap: group_id resampled with replacement, seed 42, 2000 draws shared by every scheme and delta, percentiles 2.5/97.5 over defined draws. Draws sha256 `b525b2bbc4deb77922f040723a765284cb17c5e40f1983522b039060857535d8`.

Undefined values:

- none
