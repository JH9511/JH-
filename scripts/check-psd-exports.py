"""Compare PhotoCraft exports with external corpus files using psd-tools."""

import sys
from pathlib import Path

import numpy as np
from psd_tools import PSDImage
from psd_tools.constants import Resource


def compare(source, exported):
    assert (source.size, source.depth, source.color_mode) == (
        exported.size, exported.depth, exported.color_mode
    ), "document metadata"
    assert source.version == exported.version, "PSD/PSB version"
    assert source.image_resources.get_data(Resource.ICC_PROFILE) == exported.image_resources.get_data(
        Resource.ICC_PROFILE
    ), "ICC profile"
    before, after = list(source.descendants()), list(exported.descendants())
    assert len(before) == len(after), "layer count"
    source_parents = {id(layer): i for i, layer in enumerate([source, *before])}
    export_parents = {id(layer): i for i, layer in enumerate([exported, *after])}
    for original, actual in zip(before, after, strict=True):
        label = original.name
        for key in ("name", "kind", "opacity", "visible", "blend_mode", "clipping"):
            assert getattr(original, key) == getattr(actual, key), f"{label}: {key}"
        assert source_parents[id(original.parent)] == export_parents[id(actual.parent)], f"{label}: group"
        if not original.is_group():
            assert original.bbox == actual.bbox, f"{label}: bounds"
        assert original.has_mask() == actual.has_mask(), f"{label}: mask presence"
        if original.has_mask():
            for key in ("bbox", "disabled", "background_color", "parameters"):
                assert getattr(original.mask, key) == getattr(actual.mask, key), f"{label}: mask {key}"
        for channel in ("color", "shape", "mask"):
            expected, observed = original.numpy(channel), actual.numpy(channel)
            # An absent alpha channel and an explicitly opaque one are equivalent.
            if channel == "shape" and (expected is None or observed is None):
                if expected is not None or observed is not None:
                    np.testing.assert_array_equal(expected if observed is None else observed, 1)
                continue
            assert (expected is None) == (observed is None), f"{label}: {channel} presence"
            if expected is not None:
                np.testing.assert_array_equal(observed, expected, err_msg=f"{label}: {channel}")
    # Decode the composite too, but layer samples above remain the fidelity oracle.
    exported.numpy()


def main():
    root = Path(__file__).resolve().parents[1]
    output = Path(sys.argv[1])
    files = sorted(path for path in output.rglob("*") if path.suffix in (".psd", ".psb"))
    assert files, "no exported fixtures"
    for path in files:
        name = path.relative_to(output)
        try:
            compare(PSDImage.open(root / "corpus" / name), PSDImage.open(path))
        except Exception as error:
            raise AssertionError(f"{name}: {error}") from error
        print(f"PASS {name}")
    print(f"Independent PSD interoperability: {len(files)} fixtures passed")


if __name__ == "__main__":
    main()
