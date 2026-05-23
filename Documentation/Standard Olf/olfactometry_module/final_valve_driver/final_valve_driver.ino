// Arduino Mega 2560
// Serial over USB at 9600 baud
// Pin 7 output with non-blocking timer logic

#define OUTPUT_PIN     7
#define ON_DURATION    3000   // 3 seconds in milliseconds

String        inputString    = "";
bool          stringComplete = false;

bool          pinIsOn        = false;
unsigned long onStartTime    = 0;

void setup() {
  Serial.begin(9600);              // USB serial at 9600 baud

  pinMode(OUTPUT_PIN, OUTPUT);
  digitalWrite(OUTPUT_PIN, LOW);

  inputString.reserve(16);         // Pre-allocate string buffer
  Serial.println("Ready. Send 'on' or 'off'...");
}

void loop() {

  // ── 1. Read incoming serial bytes ────────────────────────────────────────
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {  // Newline = end of command
      if (inputString.length() > 0) {
        stringComplete = true;
      }
    } else {
      inputString += c;
    }
  }

  // ── 2. Process complete command ───────────────────────────────────────────
  if (stringComplete) {
    inputString.trim();            // Strip any whitespace / CR / LF
    inputString.toLowerCase();     // Case-insensitive comparison

    Serial.print("Received: ");
    Serial.println(inputString);

    if (inputString == "on") {
      digitalWrite(OUTPUT_PIN, HIGH);
      onStartTime = millis();
      pinIsOn     = true;
      Serial.println("Pin 7 → HIGH (3s timer started)");

    } else if (inputString == "off") {
      digitalWrite(OUTPUT_PIN, LOW);
      pinIsOn = false;             // Cancel timer immediately
      Serial.println("Pin 7 → LOW (timer cancelled)");

    } else {
      Serial.println("Unknown command. Use 'on' or 'off'.");
    }

    // Reset for next command
    inputString    = "";
    stringComplete = false;
  }

  // ── 3. Non-blocking auto-off after 3s ────────────────────────────────────
  if (pinIsOn && (millis() - onStartTime >= ON_DURATION)) {
    digitalWrite(OUTPUT_PIN, LOW);
    pinIsOn = false;
    Serial.println("Pin 7 → LOW (3s timer expired)");
  }
}
