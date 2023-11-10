# mochila
_pyqgis_ personal toolbox. Run inside QGIS through [puentes plugin](https://github.com/caprieldeluca/puentes).

-----
- Clone this repository.

- Configure _puentes_ plugin to run `mosqueton.py` file.

- Write the code you want to run in `casco.py` file.

All modules will be accesible as a package. For instance:

````python
from mochila.vector import remove_spikes

remove_spikes.test()
````
