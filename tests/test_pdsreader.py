"""Tests for `pyuvis.io.PDSReader`.

Network-dependent tests fetch real UVIS PDS3 products via planetarypy and
are gated behind `@pytest.mark.network`. Run them with:

    pytest -m network

The default `pytest` invocation skips them so CI stays deterministic when
no PDS data is available on the runner.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from pyuvis.io import PDSReader


# Two real archive products that exercise the QUBE and SPECTRUM code paths.
# Same observation campaign (interplanetary H/He survey, 2004 day 18, SOLAR
# WIND target, 25-second integrations, full slit binned to 1 spatial pixel),
# but the SPECTRUM file recorded only one integration so the PDS3 pipeline
# wrote it as `OBJECT = SPECTRUM` instead of a `QUBE`.
QUBE_PID = "EUV2004_018_01_12"
SPECTRUM_PID = "EUV2004_018_10_08"


@pytest.fixture(scope="module")
def qube_path() -> Path:
    """Fetch the QUBE-type product and yield its .DAT path."""
    from planetarypy.catalog import fetch_product

    res = fetch_product("cassini.uvis.edr", QUBE_PID, files=[f"{QUBE_PID}.DAT"])
    fetch_product("cassini.uvis.edr", QUBE_PID)  # ensure label too
    return next(f for f in res.files if f.suffix == ".DAT")


@pytest.fixture(scope="module")
def spectrum_path() -> Path:
    """Fetch the SPECTRUM-type product and yield its .DAT path."""
    from planetarypy.catalog import fetch_product

    res = fetch_product("cassini.uvis.edr", SPECTRUM_PID, files=[f"{SPECTRUM_PID}.DAT"])
    fetch_product("cassini.uvis.edr", SPECTRUM_PID)
    return next(f for f in res.files if f.suffix == ".DAT")


@pytest.mark.network
def test_qube_decodes_to_3d(qube_path: Path) -> None:
    r = PDSReader(qube_path)
    assert r.data.shape == (128, 1, 1279)
    assert r.data.dtype == np.uint16
    assert r.band_range == [0, 128]
    assert r.line_range == [0, 64]
    assert hasattr(r.label, "QUBE")


@pytest.mark.network
def test_spectrum_decodes_to_degenerate_3d(spectrum_path: Path) -> None:
    r = PDSReader(spectrum_path)
    # SPECTRUM presents as a degenerate (binned_bands, 1, 1) array so callers
    # can keep treating PDSReader.data as 3-D regardless of object type.
    assert r.data.shape == (128, 1, 1)
    assert r.data.dtype == np.uint16
    assert r.band_range == [0, 128]
    assert r.line_range == [0, 64]
    assert hasattr(r.label, "SPECTRUM")

    # Values must match a raw uint16-BE read of the first ROWS*COLUMNS items
    raw = np.fromfile(spectrum_path, dtype=">u2", count=128).astype(np.uint16)
    np.testing.assert_array_equal(r.data.ravel(), raw)


@pytest.mark.network
def test_str_path_is_accepted(spectrum_path: Path) -> None:
    # Regression: PDSReader used to crash with `'str' has no attribute
    # 'with_suffix'` when the datapath was passed as a string.
    r = PDSReader(str(spectrum_path))
    assert r.data.shape == (128, 1, 1)


def test_unsupported_object_raises_valueerror(tmp_path: Path) -> None:
    # Synthesize a minimal TIME_SERIES label + dummy .DAT to confirm the
    # error path returns a clear ValueError rather than the old
    # AttributeError. No network needed.
    lbl = tmp_path / "FAKE.LBL"
    dat = tmp_path / "FAKE.DAT"
    lbl.write_text(
        "PDS_VERSION_ID = PDS3\n"
        "RECORD_TYPE = FIXED_LENGTH\n"
        "RECORD_BYTES = 256\n"
        "FILE_RECORDS = 1\n"
        "OBJECT = TIME_SERIES\n"
        "  ROWS = 10\n"
        "END_OBJECT = TIME_SERIES\n"
        "END\n"
    )
    dat.write_bytes(b"\x00" * 256)

    with pytest.raises(ValueError) as excinfo:
        PDSReader(dat)
    msg = str(excinfo.value)
    assert "QUBE" in msg
    assert "SPECTRUM" in msg
    assert "issues/10" in msg
