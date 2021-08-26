import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="paramak",
    version="0.5.0",
    author="The Paramak Development Team",
    author_email="mail@jshimwell.com",
    description="Create 3D fusion reactor CAD models based on input parameters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fusion-energy/paramak",
    packages=setuptools.find_packages(),
    classifiers=[
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    tests_require=[
        "pytest-cov>=2.12.1",
        "pytest-runner>=5.3.1",
        "nbformat>=5.1.3",
        "nbconvert>=6.1.0",
    ],
    python_requires='>=3.6',
    install_requires=[
        "plotly>=5.1.0",
        "scipy>=1.7.0",
        "sympy>=1.8",
        "numpy>=1.21.1",
        "matplotlib>=3.4.2",
        "plasmaboundaries>=0.1.8",
        "jupyter-client<7",
        "jupyter-cadquery>=2.2.0",
    ])
