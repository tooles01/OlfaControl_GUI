/*
 * BASIS2_communication_2.ino
 * 
 * Communicate with Alicat BASIS2 over the serial line
 * Connect MFC serial pins to corresponding Arduino serial pins
 * MFC baud rate must be set to 38400 for communication to work
 * 
 * 
 * yellow TX --> Arduino 10 (RX)
 * green  RX --> Arduino 11 (TX)
 * 
 * Send command to Alicat BASIS2 (using SoftwareSerial library)
 * Print response from BASIS2
 * 
 * Use the commands from the BASIS2 manual
 * Enter them on the serial line
 * 
 * Note: When sending setpoint, BASIS sends back the entire data frame
 *
 * 
 * ST 1/16/2026
 */


#include <SoftwareSerial.h>

SoftwareSerial alicatSerial(10, 11, true); // RX, TX, inverse_logic

String toSend = "";

void setup() {
  Serial.begin(9600);
  alicatSerial.begin(38400);
  Serial.println("Testing SoftwareSerial...");
}

void loop() {

  // If the user sent something
  if (Serial.available()) {
    // Read the string in
    toSend = Serial.readString();

    // Send to BASIS
    toSend = toSend + " \r";  // need carriage return
    Serial.print("Sending: ");  Serial.println(toSend);
    alicatSerial.print(toSend); // don't use newline    
  }  

  // Read whatever the Alicat sent
  String received_str = ""; // need to define type here or else it receives the message in parts
  while (alicatSerial.available() > 0 ) {
    delayMicroseconds(20);
    char inByte = alicatSerial.read();
    received_str += inByte;
  }
  if (received_str.length() > 0) {
    Serial.print("received: "); Serial.println(received_str);
  }

}
