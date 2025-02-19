# mochila
_pyqgis_ personal toolbox. Run inside QGIS through [puentes plugin](https://github.com/caprieldeluca/puentes).

-----
- Clone this repository.
- Write the code you want to run in a `casco.py` file.
- Set a `CASCO` environment variable with the absolute path to your `casco.py` file (if not, the default `casco.py` file of the *mochila's* package will be run).
- Start *QGIS* and configure _puentes_ plugin to run the *mochila's* `mosqueton.py` file.
- Run *puentes*.

All modules will be accesible as a package. For instance:

````python
from mochila.vector import remove_spikes

remove_spikes.test()
````

----
### Note:
This is a personal project, in which I test and save pyqgis code that I consider useful or I think I will need to remember later. There are no stable releases or anything like that. Use it at your own risk.
