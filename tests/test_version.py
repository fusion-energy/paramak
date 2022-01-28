import pytest
import paramak


def test_version():
    """Check that __version__ exists and is correctly formatted"""
    version = paramak.__version__
    # Ensure it is given as a string
    assert isinstance(version, str)
    # Ensure is has at least three parts -- major, minor and patch -- separated by '.'

    # develop is used as the default version name in the dockerfile
    if version != "develop":
        version_bits = version.split(".")
        assert len(version_bits) >= 3
        # Ensure each of the first three parts is convertable to int
        # (The fourth part, if it exists, may be a development version)
        for bit in version_bits[:3]:
            assert bit.isdigit()
