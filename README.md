# OlfaControl_GUI

Python GUI for using the new 8-line olfactometer and mixing chamber  

([Hardware Setup](https://github.com/tooles01/OlfaControl_Electronics))  
<br>

## Python versions

Update 4/29/2024: GUI is currently compatible with Python 3.9, 3.10, 3.12  
<br>

## Setup

1. Download/clone this folder.
    - It is highly recommended to do so via [Github Desktop](https://docs.github.com/en/desktop/installing-and-authenticating-to-github-desktop/installing-github-desktop) in order to pull new commits (bug fixes/updates) in real time.
    - If not using GitHub Desktop:
        - Click the green "<>Code" button above
        - Click "Download ZIP"
        - Save the folder to a directory on your computer.
2. Open the command prompt and navigate to the directory this folder is stored in.
3. *Optional:* Create & activate a virtual environment (instructions below)
4. Install the required packages by entering: ``` pip install -r requirements.txt ``` into the command prompt.
5. Run the GUI: ```python olfa_driver_48line.py```  
    (Big Program for running automated stuff/adding PID: ```python main.py```)  
<br>

## Quick Start:

1. Activate virtual environment  
2. Run GUI: `python olfa_driver_48line.py`  
3. Connect to Arduino  
4. Load config file  
5. Optional: Connect to ZMQ server  
<br>

## ZMQ
The olfa driver has a ZMQ subscriber socket, allowing it to receive messages from a ZMQ publisher. The default address is "tcp://127.0.0.1:5556" (can be manually edited in the heading of *olfa_driver_48line.py*).  

Strings received from a ZMQ publisher are sent directly to the master Arduino and **MUST** match the format outlined at [OlfaControl_Arduino](https://github.com/tooles01/OlfaControl_Arduino/blob/master/README.md), with the exception of setpoint updates.  Setpoint updates can be sent as SCCM values - they are parsed and converted into integer values within the olfa driver.  
<br>

Example of setpoint update sent from ZMQ publisher:
```
S_Sp_50_A1      // Set A1 setpoint to 50 SCCM (olfa driver converts from SCCM to integer before sending to master Arduino)
```
Example of setpoint update sent directly to master Arduino:  
```
S_Sp_547_A1     // Set A1 setpooint to 547 (integer value)
```
<br>

## Calibration tables & Config files
### Calibration tables

To read from each flow sensor, the GUI uses a calibration table to convert the data from voltage to flow rate.  
<p align="center"> <img src="images/Flow Sensor-GUI-Calibration table.png" width="50%"></p>

Each flow sensor has a slightly different calibration, so it is recommended to use the calibration table specific to each individual sensor to ensure accurate flow control. (Further information on calibrating flow sensors can be found [here](https://github.com/tooles01/OlfaControl_Electronics/blob/master/8-line%20Olfactometer/Flow_Sensor_Calibration_Protocol.md).)  

***Note:*** Calibration tables need to be in a folder called **calibration_tables** within the OlfaControl_GUI folder.  
### Config files

To easily load these calibration tables into the GUI, you can use a config file that lists the miniMFCs on your olfactometer and their corresponding calibration tables.  

This allows for quickly loading all calibration tables into the GUI all at once (as opposed to manually entering them into the Vial Details box for each line).  
*<p align="center"> *Example config file:*  </p>*
<p align="center"> <img src="images/setup_GUI_03_configFile.png" width="30%"></p>

With the GUI open, click "Load config file" and select the config file. (This must be done each time the GUI is closed and reopened.)  
<p align="center"> <img src="images/setup_GUI_02_loadConfig.png" width="70%"></p>

To confirm that the config file loaded correctly, open up one of the Vial Details boxes and check that the intended calibration table for that miniMFC is selected.  
<p align="center"> <img src="images/setup_GUI_vialDetails.png" width="70%"></p>
<br>

<!--
# Using the Olfactometer:
- Connect to the olfactometer (Connect to Arduino)
<p align="center"> <img src="images/setup_GUI_01_connect.png" width="70%"> </p>

- Load olfa config (*.json) file.
    - This file is specific to your olfactometer, and contains the names of the calibration tables and maximum capacity for each flow sensor.
    - This step is optional, but allows for quickly loading that information into the GUI all at once, instead of manually entering it for each of the 8 vial lines.

<p align="center"> <img src="images/setup_GUI_02_loadConfig.png" width="70%"> </p>

*<p align="center"> *Example config file:* </p>*
<p align="center"> <img src="images/setup_GUI_03_exampleConfigFile.png" width="35%"> </p>

<br>
-->

#
## Creating a virtual environment:

A virtual environment is a space separate from your main python install, where you can install just the packages needed for this project (without affecting your global python packages).  

It's not necessary to create one in order to use this GUI, but if you choose to, don't forget to activate it **each time** before running the GUI, or it may not run properly.  
<br>

1. Open the command prompt and navigate to the directory where you want the environment created. (For this circumstance, you'll probably want that to be the folder that these files are stored in, "OlfaControl_GUI".)  

    <img src="images/setup_venv_01.png" width="80%">

2. Create the environment:  
    ``` python -m venv <name of environment>\ ```  
    
    To create an environment using a specific python version:  
    ``` <path to python version> -m venv <name of environment>\ ```  
    
    <img src="images/setup_venv_02.png" width="80%">

3. Activate the virtual environment:  
    ```<name of environment>\scripts\activate.bat```
    
    <img src="images/setup_venv_03.png" width="80%">

Once in the environment, you'll have access to all of the packages specifically installed there.