"""Tests for the package skeleton: typing marker and runtime dependencies."""

from importlib import metadata, resources
import re


def test_nfr012_package_ships_py_typed_marker() -> None:
    """NFR-012: the package marks itself as typed (PEP 561)."""
    assert resources.files("slf_snow").joinpath("py.typed").is_file()


def test_nfr002_aiohttp_is_only_runtime_dependency() -> None:
    """NFR-002, ADR-002: aiohttp is the only runtime dependency, with a lower bound only."""
    requirements = metadata.requires("slf-snow") or []
    names = {
        re.split(r"[\s<>=!~;\[]", req, maxsplit=1)[0].lower() for req in requirements
    }
    assert names == {"aiohttp"}
    assert all("<" not in req for req in requirements)
