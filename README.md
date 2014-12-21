# ShapefileImport

## Description
`ShapefileImport` takes the most recent version of the [NWB](http://www.jigsaw.nl/nwb/) and gives you plain CSV output with all the fields needed to create a query based on `road + milemarker` or `latitude + longitude`. 

The GPS coordinates present in the NWB are `EPSG:28992 (Amersfoort / RD New)` and will be translated to the `EPSG:4326 WGS84` LatLon with WGS84 datum used by GPS units and Google Earth.

## How to run this application
1. The script has to be run with a Python 2 interpreter. Such an interpreter is usually installed by default as the `python` command on Apple and Linux systems. If you do not have a Python 2 interpreter, you can get one from [the Python website](https://www.python.org/) (choose the button labeled "Download Python 2.7.X").
2. Install [PIP](https://pip.pypa.io/en/latest/installing.html) (The PyPA recommended tool for installing and managing Python packages.)
3. It is recommended to install [virtualenv](http://virtualenv.readthedocs.org/en/latest/) by running ```pip install virtualenv``` and optionally [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/install.html) (A set of extensions to Ian Bicking’s virtualenv tool.) to make working with virtualenvs easier. If you do, create a virtualenv and activate it.
4. Run ```pip install -r requirements.txt```
5. Download the most recent version of the NWB from [here](http://www.jigsaw.nl/nwb/) and extract the contents of the .zip file to a folder named `input` in your `project root`. After this step, the `input` folder in your `project root` should contain 2 directories (`Hectopunten` and `Wegvakken`) and their content.
6. Run ```python app.py``` to start the processing.
7. After processing, the `output` folder in the `project root` will contain 3 CSV files (`Hectopunten.csv`, `merged.csv` and `Wegvakken.csv`). 
8. `merged.csv` will be the file one will generally use to import into an Relational Database or for other kinds of querying.