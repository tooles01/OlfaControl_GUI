# Alicat BASIS2 serial communication


BASIS2_communication.ino is for communicating with an Alicat BASIS2 using an Arduino mega.

User sends a string over the serial port (9600 baud). String should be one of the commands for the BASIS2. Arduino prints out the response from the BASIS2.

Full command list found in [BASIS2 manual](https://documents.alicat.com/manuals/DOC-MANUAL-BASIS2.pdf)


## Connections

BASIS2 TX --> Arduino 10 (RX)  
BASIS2 RX --> Arduino 11 (TX)


## Frequently used commands

Commands & examples using MFC with unit_id 'A'.

### Request current flow value
*unit_id***DV 1**  

`aDV 1`

### Send setpoint
(setpoint range 0-1 for 1000cc MFCs)  

*unit_id***S** *setpoint*  

`aS 0.5`

### Request entire data frame
*unit_id*  

`a`

### Read setpoint source
*unit_id***LSS**  

`aLSS`

#### Setpoint sources:
"a" --> analog (will not accept digital commands)  
"s" --> saved digital (no need to use this)  
"u" --> unsaved digital (analog input is disconnected from the setpoint)  

### Set setpoint source to analog
*unit_id***LSS a**  

`aLSS a`

### Set setpoint source to digital
*unit_id***LSS u**  

`aLSS u`

### Read the baud rate
*unit_id***NCB**  

`aNCB`

### Set the baud rate
*unit_id***NCB** *baud_rate*

`aNCB 19200`

