# Standard Olfactometer


Teensy baudrate is set to 115200, parses incoming strings from the serial port using Serial.read()  
Also you can talk directly to it using the Arduino Serial Monitor if you want to send these strings directly for debugging or whatever

##  Strings for commands


### Set flowrate

slaveindex = internal to Teensy/ValveController code (probably)  (actually omg this might be the DIP switch on the ValveController that we set during ValveController flashing)  
arduino port = RJ jack the MFC is connected to  


**alicat_digital:**  
*DMFC + slaveindex + arduino port + MFC address + flownum*  

`DMFC 1 2 A32000    // Set (200cc capacity) MFC to 100cc`  
`DMFC 1 2 A16000    // Set (200cc capacity) MFC to 50cc`  
`DMFC 1 2 A8000     // Set (200cc capacity) MFC to 25cc`  

flownum = (flowrate / mfc capacity) * 32000  
MFC address = A (99% of the time) (can be changed on the MFC itself)

<br>

 *** *Note:* Current version of the standard olf GUI does not include functions for sending/receiving messages on analog, the below  section is just for comprehensive documentation purposes 

 *** *Secondary note: I know this math doesn't make sense, need to check what's up here -ST 5/31/2024*

<br>

**analog:**  
*MFC + slaveindex + arduino port + flownum*  

`MFC 1 2 .5         // Set 200cc capacity MFC to 100cc`  
`MFC 1 2 .25        // Set 200cc capacity MFC to 50cc`  
`MFC 1 2 .05        // Set 200cc capacity MFC to 10cc`  

flownum = flowrate / mfc capacity  


### Vial open
*vialOn + slaveindex + vialNum*  

`vialOn 1 5     // Opens vial 5`  
`vialOn 1 5     // Opens vial 6`


### Vial close
*vialOff + slaveindex + vialNum*  

`vialOff 1 5    // Closes vial 5`  
`vialOff 1 5    // Closes vial 6`  


<br>
<br>

##
##
##

Note for me (Shannon):  
No idea if dummy valve commands are needed in olfa_driver_original.py, since we don't have a separate dummy valve widget in the GUI (as we do in the original GUI). Seems that opening/closing of the dummy valve when vials are opened is built into the Teensy/ValveController somewhere, since only a single command is sent out (from Python) when the vials are opened/closed

