# Olfactometry module

Updated version of Rinberg lab [olfactometry](https://github.com/olfa-lab/olfactometry/tree/master) package for use with Python3 and PyQt5.

<br>

## Setup

1. Download/clone this folder.
    - It is highly recommended to do so via [Github Desktop](https://docs.github.com/en/desktop/installing-and-authenticating-to-github-desktop/installing-github-desktop) in order to pull new commits (bug fixes/updates) in real time.
    - If not using GitHub Desktop:
        - Click the green "<>Code" button above
        - Click "Download ZIP"
        - Save the folder to a directory on your computer.
2. Open the command prompt and navigate to the directory this folder is stored in.
3. *Optional:* Create & activate a virtual environment
4. Install the required packages by entering: ``` pip install -r requirements_standard_olf.txt ``` into the command prompt.

<br>

## JSON configuration file
The configuration of the gui and devices is driven by a new JSON formatted configuration file. Its presence is necessary
for the program to run. Specs are specified in the [config readme](json_specs.md). An example is present in the
project as: [olfa_config.json](olfa_config.json).

The default file location for the config file is C:\\voyeur_rig_config\\olfa_config.json, but this location can be changed
by passing the file location to the instantiating classes.

<br>

## Basic use

[JSON configuration file](docs/json_specs.md) must be present in the current directory.

GUI can be run from a python prompt:


```
>>> import olfactometry
>>> config_filename = "C:\\your_config_dir\\your_config_name.json"
>>> olfactometery.main(config_filename)
>>> # if no filename is passed, it will use the default (C:\\voyeur_rig_config\\olfa_config.json)
```



To use the package in a larger program is simple too:
```python
import olfactometry


class MyGui(YourFavoriteQtGuiPackage):  # this works with Enthought's Traits when used in Qt mode.
    def __init__(self, ...):
        self.olfas = olfactometry.Olfactometers(parent=self)  # this will NOT activate the gui.

    def show_olfa_gui(self):
        self.olfas.show()  # just like any QWidget, this will make the olfactometers gui visible.
```