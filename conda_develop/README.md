This folder contains a development version of Paramak that is used for testing.

One of the differences between this conda build and the main conda build is that
this version makes use of CaDQuery master instead of a stable version of
CadQuery. This allows us to check the Paramak continues to work with the latest
version of CadQuery before it is released.

This can be built with

```bash
 conda-build conda_develop/ -c cadquery -c conda-forge --croot /tmp/conda-build-develop --config-file conda_develop/conda_build_config.yaml
 ```
 