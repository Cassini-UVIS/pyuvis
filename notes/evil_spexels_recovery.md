# Evil-Spexels Recovery — Working Note

**Status:** Scoping / principled feasibility complete. No code yet.
**Branch:** `claude/evil-spexels-recovery-lKVHS`
**Author of note:** drafted in a Claude Code on-web session for handoff to a
local Claude terminal session that has access to additional Cassini-UVIS
repositories (notably `cassini-uvis/tools`, which is not reachable from the
web sandbox).

---

## 1. Problem statement

The Cassini UVIS detector has a set of spexels (spatial-by-spectral pixels)
flagged as **evil** based on pre-launch lab characterization. The on-board
processor sums adjacent spexels into bins; **if a single evil spexel falls
inside a bin, the entire bin is written out as NaN**. For binned
observations this destroys the signal from every good spexel that shared the
bin — a large, structural loss of information for the mission.

The goal: develop a principled recovery method that uses statistics from
**unbinned** observations to estimate (with uncertainties) the physical flux
that should have appeared in those NaN'd bins.

---

## 2. Current state of the `pyuvis` codebase (audited 2026-05-27)

A targeted code search across `src/`, `docs/`, `archive/`, `tests/` found:

- **No evil-pixel list ingested.** No mask file, no lookup table, no
  pre-launch lab definitions referenced anywhere in the repo.
- **No bin-geometry abstraction.** `io.py` reads `BAND_BIN` / `BIN_SPATIAL`
  from PDS3 labels but there is no object that maps a bin index to its
  constituent spexels.
- **No recovery code.** Nothing attempts to estimate values for NaN'd bins.
- **Defensive NaN masking only**, at:
  - `src/pyuvis/calib/steffl.py:70` — `data.where(np.isfinite(data), other=np.nan)`
  - `src/pyuvis/calib/steffl.py:240` — `data.where(data > 0, other=np.nan)`
- **The conceptual problem is acknowledged in the Row2Row notebook**
  (`docs/tutorials/07_calib_row2row.ipynb`, Bob's open comment): the
  effective flatfield for a binned pixel is source-dependent because it
  depends on which individual spexels fall in the bin and on the spectrum
  inside the bin. No solution implemented.
- **HSP_CALIBRATION.TXT** contains only radiometric factors, no pixel
  quality info.

What this means: the recovery work needs to introduce three things the
repo doesn't have — an evil-pixel mask, a bin-geometry helper, and the
recovery routine itself.

---

## 3. The principled answer: yes, partial recovery is possible

**Do not try to recover the on-board bin value `B_k`.** That number would
have always included the evil spexel's bogus signal. Recover the **physical
flux** in the bin's wavelength interval instead. The evil spexel's
"missing" contribution is fictitious; what was actually lost is the *good*
spexels' contribution that the onboard NaN'ing threw away with the
bath water.

### 3.1 Forward model

For bin `k` spanning spexels `{i, j, l, m}` with spexel `j` evil:

$$\mathbb{E}[s_i] = f_i \cdot \int_{\Delta\lambda_i} \phi(\lambda)\,d\lambda$$

where
- `f_i` = per-spexel sensitivity (lab + Row2Row + Steffl on-orbit work)
- `φ(λ)` = physical spectral flux density (the unknown of interest)
- `Δλ_i` = that spexel's bandpass

Define the **good-pixel fraction** for bin `k`:

$$\rho_k = \frac{\sum_{\text{good } i \in k} f_i\,\Delta\lambda_i}{\sum_{\text{all } i \in k} f_i\,\Delta\lambda_i}$$

If `φ` is approximately flat over `Δλ_k` (a few nm; true for continuum,
false for narrow emission lines), `ρ_k` is a *constant for the bin
geometry*, computable from calibration alone. The salvageable signal is

$$S_k^{\text{good}} = \rho_k \cdot \left(\sum_{i \in k} f_i\,\Delta\lambda_i\right)\cdot \langle\phi\rangle_k.$$

### 3.2 Three independent uses of unbinned data

1. **Calibrate `ρ_k` accurately on-orbit.** Lab `f_i` values drift; use
   unbinned observations of smooth-spectrum stars (the stars in
   `src/pyuvis/calib/stars_list.txt`) to measure current `f_i` ratios.
   The Row2Row / Steffl work is the right framework for this.
2. **Learn a spectral prior `p(φ)`.** Unbinned observations of the same
   *scene type* (icy moon, ring, atmosphere, …) give the empirical
   covariance of `φ` across bins. That covariance becomes the prior for
   interpolating across NaN'd bins.
3. **Validation.** Take real unbinned observations, *simulate* the
   onboard bin-and-NaN, run recovery, measure residuals. Produces a
   real, data-driven error budget instead of a theoretical one.

### 3.3 Recovery procedure (sketch)

Given good neighbor bins `{B_{k'}}` and learned spectral covariance:

$$\hat{\phi}(\lambda_k)\ \big|\ \{B_{k'}\}_{k'\neq k}\ \sim\ \text{GP posterior with kernel from (2)}$$

then

$$\hat{S}_k^{\text{good}} = \left(\sum_{\text{good } i} f_i\,\Delta\lambda_i\right)\cdot \hat{\phi}(\lambda_k)$$

with uncertainty propagated from:
- GP posterior variance (interpolation uncertainty)
- `f_i` flatfield error budget
- **Bob's source-dependence term** — non-zero when `φ` has structure
  inside `Δλ_k` *and* the evil spexel sits asymmetrically in the bin.
  This is irreducible without external spectral info.

### 3.4 Regime table

| Scene / situation | Recovery quality |
|---|---|
| Smooth continuum, isolated NaN bin | Excellent — often < 1% |
| Smooth continuum, consecutive NaN bins | Degrades ~ gap²; useful for ≤ 2–3 bins |
| Sharp emission/absorption line inside NaN bin | Cannot recover the line; large reported uncertainty |
| Faint targets, Poisson-limited | Floored by photon noise on neighbors |

### 3.5 Bottom line

Recovery is possible in principle with two preconditions, both close to
hand:
1. Trustworthy per-spexel sensitivity `f_i` (Row2Row / Steffl work).
2. Library of unbinned observations to train `ρ_k` and the spectral
   prior.

Missing in the repo: (i) the evil-pixel list, (ii) a bin-geometry helper,
(iii) the GP / Bayesian interpolation step.

---

## 4. Next steps for the picking-up agent

The user has told us that **Greg Holsclaw's IDL calibration code in
`cassini-uvis/tools` contains the bad-pixel list**. The on-web session
could not reach that repo (it is not public, and the GitHub MCP scope was
locked to `pyuvis`). The local session has it.

### 4.1 Immediate

1. **Locate the bad-pixel list** in `cassini-uvis/tools`. Likely forms:
   - an IDL `.sav` (readable via `scipy.io.readsav`; see existing
     `src/pyuvis/idlsav.py`)
   - a `.pro` file with a hard-coded array of `[row, col]` pairs
   - a `.txt` / `.dat` lookup table
2. **Note the convention.** Confirm:
   - Indexing: 0-based vs 1-based, row vs column ordering
   - Coordinate system: detector pixel grid (1024 × 1024 for FUV/EUV,
     check) — which axis is spatial, which is spectral
   - Per-channel split: FUV vs EUV (likely separate lists)
   - Does the list cover *both* truly dead pixels and "evil" (noisy /
     non-linear / hot) pixels? Are they categorized?
3. **Translate to a stable artifact.** Suggested: a CSV or FITS table
   shipped in `src/pyuvis/calib/` (e.g., `evil_spexels_fuv.csv`,
   `evil_spexels_euv.csv`) with columns `(row, col, category, source)`.
   Keep the original IDL file untouched in `tools` — pyuvis just imports
   a verbatim translation.

### 4.2 First module to add

Sketch: `src/pyuvis/calib/evil.py`

```
class EvilSpexelMask:
    """Boolean mask of evil spexels for one UVIS channel (FUV or EUV)."""
    def __init__(self, channel: str): ...
    @property
    def mask(self) -> np.ndarray: ...           # shape (n_spatial, n_spectral)
    def for_bin_geometry(self, bin_geom) -> "BinEvilMap":
        """Which bins contain ≥1 evil spexel; per-bin good-pixel fraction ρ_k."""

class BinGeometry:
    """Maps bin index → list of constituent spexel indices.
    Built from PDS3 BAND_BIN / BIN_SPATIAL keywords already parsed in io.py."""
```

### 4.3 First validation experiment

Before writing any recovery code:

1. Pick one well-understood unbinned UVIS observation (e.g., a star from
   `stars_list.txt`).
2. Simulate the onboard binning (sum) and apply the NaN rule.
3. Compare the simulated NaN'd binned spectrum against a real binned
   observation of the same star where one exists.
4. This sanity-checks the bad-pixel list, the bin geometry, and the
   flatfield model — *before* introducing any GP / Bayesian machinery.

### 4.4 Then build recovery

Only after 4.3 succeeds:

1. `src/pyuvis/recovery/` module with the GP-based estimator from §3.3.
2. Scene-type-specific kernels trained from the unbinned archive.
3. Add a new tutorial `docs/tutorials/09_evil_recovery.ipynb` walking
   through a worked example with uncertainties.
4. CHANGELOG + bump.

---

## 5. Open questions for the user (kmichael.aye@gmail.com)

- Is the evil-pixel list **time-varying**? I.e., does Greg's IDL code
  account for additional pixels going bad in flight, or is it strictly
  the pre-launch lab list? This changes whether the mask needs a date
  parameter.
- Are FUV and EUV evil-spexel populations roughly comparable in
  fractional area? This sets expectations for how much data is
  recoverable per channel.
- For the spectral prior: do we want a *single* prior fit across all
  observations, or scene-type-conditional priors (rings vs. icy moons
  vs. occultation atmospheres)? My recommendation: scene-conditional —
  the spectral correlation structures are very different.

---

## 6. References inside the repo

- `src/pyuvis/io.py:67,94,117,275-283` — PDS3 binning keyword parsing
- `src/pyuvis/calib/steffl.py` — Row2Row flatfield and Col2Col correction
- `src/pyuvis/calib/greg.py` — star observation metadata lookup
- `src/pyuvis/calib/stars_list.txt` — calibration star catalog
- `docs/tutorials/07_calib_row2row.ipynb` — Bob's binned-flatfield comment
- `docs/tutorials/08_stats.ipynb` — existing stats playground
- `src/pyuvis/idlsav.py` — IDL `.sav` reader (useful for ingesting Greg's
  list if it's in that format)
