# OlfaControl_GUI

GUI for testing the new 8-line olfactometer

<br>

## Python versions

Update 4/29/2024: GUI is compatible with Python 3.9, 3.10, 3.12

~~As of 1/23/2024, we know that: Python 3.9 and 3.10 work, Python 3.12 does not work~~

<br><br>

# Setup

1. Download/clone the whole folder
2. Open the command prompt and navigate to this folder
3. Optional:
    - Create a virtual environment (instructions below)
    - Once created, activate the virtual environment
    
        ```
        <name of environment>\scripts\activate.bat
        ```
4. Install the required packages
    ```
    pip install -r requirements.txt
    ```
5. Run the GUI
    
    Olfactometer only:
    ```
    python olfa_driver_48line.py
    ```
    Big Program for running automated stuff/adding PID:
    ```
    python main.py
    ```

<br>

#
## Once you open the GUI:
- Connect to the olfactometer (Connect to Arduino)
- Load olfa config (*.json) file. (This file contains the names of the calibration tables to use for each flow sensor, plus the maximum capacity of each flow sensor.)  
<br>

*Note: Calibration tables should be located in a folder called **calibration_tables** within the OlfaControl_GUI folder. Calibration tables must be in decreasing sequential order, or the interpolation will get all messed up.*

<br>
<br>

#
### To create a virtual environment:
1. Open the command prompt and navigate to where you want the environment created.
2. Create the environment
    ```
    python -m venv <name of environment>\
    ```

    example:
    ```
    python -m venv venv1\
    ```
    <br>

    If you want to create the environment using a specific python version, use:
    ```
    <path to python version> -m venv <name of environment>\
    ```

