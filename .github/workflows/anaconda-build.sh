name: anaconda-publish-develop

on:
  pull_request:
    branches:
      - develop
      - main
    paths:
      - "**.py"
      - "**.yml"

jobs:
  build:
    runs-on: ubuntu-latest
    container: continuumio/miniconda3:4.10.3

    steps:
      - uses: actions/checkout@v2

      - name: Set up conda
        run: |
            apt-get --allow-releaseinfo-change update
            apt install -y libgl1-mesa-glx
            conda install -y anaconda-client conda-build
            conda config --set anaconda_upload no
            conda install boa -c conda-forge
      - name: Build conda package
        run: |
            conda mambabuild conda_dev -c fusion-energy -c cadquery -c conda-forge --config-file conda_dev/conda_build_config.yaml
            conda convert /opt/conda/conda-bld/linux-64/*.tar.bz2 --platform osx-64
            conda convert /opt/conda/conda-bld/linux-64/*.tar.bz2 --platform win-64
