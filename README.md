# pytheriak
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7945482.svg?style=flat)](https://doi.org/10.5281/zenodo.7945482)

Python wrapper functions for Theriak-Domino.

## Installation
[![PyPI](https://img.shields.io/pypi/v/pytheriak.svg?style=flat)](https://pypi.python.org/pypi/pytheriak)
[![Compatible Python Versions](https://img.shields.io/pypi/pyversions/pytheriak.svg?style=flat)](https://pypi.python.org/pypi/pytheriak/)

You can install the package from pypi.org.
Run the following to install:

```python
pip install pytheriak
```

## Usage

### Run theriak from your python script

Import the wrapper module.

```python
from pytheriak import wrapper
```
First, create a TherCaller-object.\
The `programs_dir` must be set to the Programs directory of your Theriak-Domino installation. Specify the database (ensure that you correctly specify the file extension e.g., .txt or .bs). Specify your version of Theriak-Domino for completeness.\
To run Theriak from Python, the database file should be in the same directory as your python script. On Windows you must also have a theriak.ini in the directory.
```python
theriak = wrapper.TherCaller(programs_dir="..\Programs",
                             database="a database file",
                             theriak_version="v2023.01.02beta")
```
As input for Theriak define:\
1. Pressure in bars.
```python
pressure = 4000
```
2. Temperature in degree celsius.
```python
temperature = 550
```
3. Bulk composition following the Theriak-Domino format: Elements in uppercase followed by (number of moles).
```python
bulk = "AL(2)SI(1)O(?)"
```
Then call minimisation() on the TherCaller-object.
```python
rock, element_list = theriak.minimisation(pressure, temperature, bulk)
```
This method returns a Rock-object containing all the properties of the minimised system and an element list. The list acts as an element - index lookup table for all compositional vectors of the Rock (bulk and phase compositions).

### Access the properties of the Rock-object

An easy way to checkout all accessible properties is looking at the object's attributes using ...
```python
dir(rock)
```
Useful rock properties are:
```python
rock.g_system                   # Gibbs free energy of the system [J]
rock.bulk_composition_moles     # Bulk composition [mol]
rock.mineral_assemblage         # List of stable solid phases
...
```
Mineral (and fluid) assemblage contain Mineral- and Fluid-Objects which hold the phase related properties.
```python
mineral = rock.mineral_assemblage[i]

mineral.name                    # Phase name from database
mineral.n                       # Amount of phase [mol]
mineral.composition_apfu        # Mineral composition [apfu]
...
```
A quick, easy and pythonic way to retrieve properties is using list comprehensions.
```python
[mineral.name for mineral in rock.mineral_assemblage]
[mineral.composition_apfu for mineral in rock.mineral_assemblage]
```

## Cite pytheriak

The pytheriak package is registered on Zenodo. If you use pytheriak in your research, please cite it using the following DOI:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7945482.svg?style=flat)](https://doi.org/10.5281/zenodo.7945482)

## License

Theriak-Domino/pytheriak is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for more details.
