# EMBER2024 raw dataset inventory

Inspection date: 2026-09-20  
Inspected path: `C:\Users\saiga\Documents\Master of AAI - Sandiego\AAI-540\project\data\raw\ember2024`

This was a read-only inspection. No raw dataset file was changed, moved, renamed, or deleted. This inventory does **not** perform EDA, feature engineering, resplitting, training, or SageMaker work.

## Executive summary

The download contains only the `Win64` (64-bit Windows PE) subset of EMBER2024: 52 weekly train shards and 12 weekly test shards. There is no challenge partition and none of the other five official file types (`Win32`, `.NET`, `APK`, `ELF`, `PDF`) are present.

The weekly filenames preserve the official temporal train/test boundary. However, two independent spot checks (the first train and first test shards) found **20,000 JSONL rows per week**, whereas the official documentation specifies **10,000 Win64 files per week**. The aggregate local size, 31.24 GiB, is likewise about twice the official published Win64 size (15.4 GB, train plus test). Treat this Kaggle copy as a likely row-doubled/non-canonical derivative until its provenance and duplicates are verified.

## Directory and file structure

```text
data/raw/ember2024/
+-- Win64_train/                         # 52 JSONL weekly shards
|   +-- 2023-09-24_2023-09-30_Win64_train.jsonl
|       through 2024-09-15_2024-09-21_Win64_train.jsonl
+-- Win64_test/                          # 12 JSONL weekly shards
    +-- 2024-09-22_2024-09-28_Win64_test.jsonl
        through 2024-12-08_2024-12-14_Win64_test.jsonl
```

Every intervening weekly Sunday-to-Saturday interval is present, with no gap in either inclusive range. All 64 files are uncompressed newline-delimited JSON (`.jsonl`); no archives, vectorized `.dat` files, manifests, checksums, or documentation files are included locally.

### Partition inventory and sizes

| Local directory | Purpose | Shards | Inclusive weekly coverage | Bytes | MiB | GiB |
|---|---:|---:|---|---:|---:|---:|
| `Win64_train` | official temporal training period | 52 | 2023-09-24 through 2024-09-21 | 28,129,977,467 | 26,826.84 | 26.20 |
| `Win64_test` | official temporal test period | 12 | 2024-09-22 through 2024-12-14 | 5,418,976,619 | 5,168.89 | 5.05 |
| **Total** | Win64 subset only | **64** | 2023-09-24 through 2024-12-14 | **33,548,954,086** | **31,995.73** | **31.24** |

Per-file sizes vary by week. Train shards are 390.82--661.17 MiB; test shards are 387.83--460.04 MiB. Exact file names and byte sizes can be reproduced read-only with:

```powershell
Get-ChildItem -LiteralPath 'C:\Users\saiga\Documents\Master of AAI - Sandiego\AAI-540\project\data\raw\ember2024' -File -Recurse |
  Sort-Object FullName |
  Select-Object FullName, Length
```

## Partitions, types, and record counts

| Partition | Present locally? | Official Win64 expectation | Local observation |
|---|---:|---:|---|
| Train | Yes (`Win64_train`) | 52 × 10,000 = 520,000 records | First weekly shard has **20,000** rows; 52 shards would imply ~1,040,000 rows if this holds throughout. |
| Test | Yes (`Win64_test`) | 12 × 10,000 = 120,000 records | First weekly shard has **20,000** rows; 12 shards would imply ~240,000 rows if this holds throughout. |
| Challenge | No | 814 Win64 malicious challenge files (within the official 6,315-file multi-type challenge set) | No `challenge` directory or files. |

The 20,000-row counts were obtained by direct newline counts on:

- `Win64_train/2023-09-24_2023-09-30_Win64_train.jsonl`
- `Win64_test/2024-09-22_2024-09-28_Win64_test.jsonl`

An exhaustive row/label count was intentionally not completed during this inspection because it requires scanning 31.24 GiB of raw JSONL. Before preprocessing, perform a streaming all-shard count and hash-level duplicate audit; do not assume the inferred totals are unique-file counts.

**File/malware type:** all observed records have `file_type: "Win64"`. These are raw static-feature records for Windows 64-bit Portable Executable files, with enriched metadata and labels/tags. They are not PE binaries themselves.

## JSONL schema

Each line is one JSON object. The sampled train and test records share this 32-field top-level schema:

```text
md5, sha1, sha256, tlsh,
first_submission_date, last_analysis_date, detection_ratio, label, file_type,
family, family_confidence, behavior, file_property, packer, exploit, group,
histogram, byteentropy, strings, general, header, section, imports, exports,
datadirectories, richheader, authenticode, pefilewarnings, week_id,
caps, ttps, mbc
```

| Field group | Structure observed |
|---|---|
| Identity and time | `md5`, `sha1`, `sha256`, `tlsh` strings; Unix-epoch `first_submission_date` and `last_analysis_date`; string `detection_ratio`; integer `week_id`; string `file_type`. |
| Primary and taxonomy labels | Integer `label`; nullable `family` and `family_confidence`; arrays `behavior`, `file_property`, `packer`, `exploit`, and `group`. |
| Byte/string statistics | `histogram` and `byteentropy`: 256-element numeric arrays. `strings`: `{numstrings, avlength, printabledist[96], printables, entropy, string_counts{...}}`. `general`: `{size, entropy, is_pe, start_bytes}`. |
| PE headers | `header.coff` (timestamp, machine, section/symbol/header counts and characteristics); `header.optional` (PE version, subsystem, code/image/memory/alignment/checksum fields and DLL characteristics); `header.dos` (DOS-header fields). |
| PE layout/imports | `section`: `{entry, sections[] {name, size, entropy, vsize, size_ratio, vsize_ratio, props[]}, overlay {size, size_ratio, entropy}}`; `imports` is a DLL-name keyed object whose values vary by DLL; `exports` array; `datadirectories` array (17 observed); `richheader` numeric array. |
| Signing and parsing | `authenticode`: `{num_certs, self_signed, empty_program_name, no_countersigner, parse_error, chain_max_depth, latest_signing_time, signing_time_diff}`; `pefilewarnings` array. |
| Capa enrichment | `caps[]` objects such as `{Capability, Namespace, Addrs[]}`; `ttps[]` objects `{Tactic, Technique}`; `mbc[]` objects `{Objective, Behavior}`. |

Fields such as `imports`, `string_counts`, PE section lists, exports, warnings, tag arrays, and Capa outputs are sparse and variable-length/dynamic by design. `family` and `family_confidence` can be null (as in the sampled benign records). A schema should therefore not be inferred from a fixed rectangular set of JSON keys without appropriate missing/variable-length handling.

## Labels and targets

The default target is the integer `label`, used by the official vectorization workflow for malicious/benign detection (observed value `0` in sampled records; expected binary encoding is benign `0`, malicious `1`). `detection_ratio` is provenance/AV metadata, not the supervised target.

EMBER2024 also provides six other target/tag categories: `family`, `behavior`, `file_property`, `packer`, `exploit`, and `group`. The official documentation states these families/tags are assigned through ClarAVy. The latter five are multi-label arrays; `family` is nullable and `family_confidence` accompanies it. `caps`, `ttps`, and `mbc` are Capa-derived enrichments, not among the seven documented vectorization label types.

## Temporal information and split preservation

Temporal information is preserved in two ways:

1. Shard names encode contiguous weekly intervals.
2. Each record includes Unix timestamps `first_submission_date` and `last_analysis_date`, plus `week_id` (sampled train: 0; sampled test: 52).

The directories retain the official temporal split exactly at the filename boundary: the first 52 weeks (2023-09-24--2024-09-21) are train and the last 12 weeks (2024-09-22--2024-12-14) are test. The official source describes that division as a deliberate future/generalization evaluation split, not a random split.

## Consistency with official EMBER2024

**Consistent:**

- The weekly dates, 52/12 train/test organization, `Win64` naming, feature-version-3-style raw JSONL fields, label/tag fields, and Capa fields are consistent with the official EMBER2024 README.
- The sample schema includes the documented additions to feature version 3: DOS/Rich headers, data directories, Authenticode, PE-file warnings, and Capa results for Win64.

**Not demonstrably canonical / likely inconsistent:**

- Official documentation specifies 10,000 Win64 files per week (520,000 train; 120,000 test). Two local shard counts are 20,000 rows each.
- Official published sizes are 12.9 GB for Win64 train and 2.5 GB for Win64 test (15.4 GB total). The local copy is 26.20 GiB train and 5.05 GiB test (31.24 GiB total), approximately double.
- This pattern is consistent with a known EMBER2024 row-doubling concern, but cannot establish whether every row is duplicated without a full hash-level audit.
- The dataset came from Kaggle rather than the official Hugging Face download path, and no local provenance/checksum/manifest identifies the Kaggle source version.

Official references: [EMBER2024 README](https://github.com/FutureComputing4AI/EMBER2024/blob/main/README.md) and [EMBER2024 paper](https://arxiv.org/abs/2506.05074).

## Concerns and required clarification before preprocessing

1. **Resolve apparent duplication first.** Confirm the Kaggle dataset URL/version and run a streaming per-shard and global `sha256` duplicate audit. Decide whether duplicate rows must be removed or a clean official download must replace this copy. Do not use the present record count as an independent-sample count.
2. **Confirm intended scope.** This download is Win64 only. It cannot support a six-file-type EMBER2024 experiment or an official all-type challenge evaluation without acquiring the missing types and challenge set.
3. **Challenge set is missing.** Obtain the official challenge files if evasive-malware evaluation is required.
4. **Preserve the temporal protocol.** Keep the supplied weeks intact; do not perform a random train/test split. Any validation strategy should be specified separately and remain temporally defensible.
5. **Specify the learning target.** Confirm whether the task is binary `label`, `family`, or one/more multi-label taxonomies. Family/tag nulls, sparsity, cardinality filtering, and Capa-field eligibility require task-specific handling.
6. **Validate timestamp semantics.** The included timestamps are Unix epochs, but downstream work should explicitly choose `first_submission_date` versus filename/week assignment and account for `last_analysis_date` occurring later (potential temporal leakage if used as a feature).
7. **Do not rely on sampled schema alone.** Before building a parser, scan all JSONL records for optional/missing fields, type deviations, and dynamic-object patterns.
