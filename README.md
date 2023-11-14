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

----
### Note:
This is a personal project, in which I test and save pyqgis code that I consider useful or I think I will need to remember later. There are no stable releases or anything like that. Use it at your own risk.
