import pytest
import paramak


def test_version():
    """Check that __version__ exists and is correctly formatted"""
    version = paramak.__version__
    # Ensure it is given as a string
    assert isinstance(version, str)
    # Ensure is has at least two parts -- major and minor version -- separated by '.'
    # Ideally we would aim for major.minor.patch, but this has a tendency to break
    # CI tests for unknown reasons.

    # develop is used as the default version name in the dockerfile
    if version != "develop":
        version_bits = version.split(".")
        assert len(version_bits) >= 2, "Version number is %s" % version
        # Ensure each of the first three parts is convertable to int
        # (The fourth part, if it exists, may be a development version)
        for bit in version_bits[:2]:
            assert bit.isdigit(), "Version number is %s" % version
