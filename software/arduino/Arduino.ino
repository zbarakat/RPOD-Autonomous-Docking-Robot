
#include <stdio.h>
#include <string.h>

// Desired wheel speeds (RPM)
int targetLeftRPM = 0;
int targetRightRPM = 0;

// Communication safety
const unsigned long TIMEOUT_MS = 2000;
unsigned long lastCommandTime = 0;

// Serial input buffer
char input[48];
byte inputIndex = 0;

void stopRobot() {
  targetLeftRPM = 0;
  targetRightRPM = 0;
  digitalWrite(LED_BUILTIN, LOW);
}

void processCommand(char* command) {

  if (strcmp(command, "PING") == 0) {
    Serial.println(F("PONG"));
    return;
  }

  if (strcmp(command, "STOP") == 0) {
    stopRobot();
    Serial.println(F("ROBOT STOPPED"));
    return;
  }

  if (strcmp(command, "STATUS") == 0) {
    Serial.print(F("LEFT RPM: "));
    Serial.println(targetLeftRPM);

    Serial.print(F("RIGHT RPM: "));
    Serial.println(targetRightRPM);
    return;
  }

  int left, right;
  char extra;

  if (sscanf(command, "SET %d %d %c",
             &left, &right, &extra) == 2) {

    if (left < -120 || left > 120 ||
        right < -120 || right > 120) {
      Serial.println(F("ERROR: RPM OUT OF RANGE"));
      return;
    }

    targetLeftRPM = left;
    targetRightRPM = right;
    lastCommandTime = millis();

    Serial.print(F("COMMAND ACCEPTED: "));
    Serial.print(targetLeftRPM);
    Serial.print(F(", "));
    Serial.println(targetRightRPM);
    return;
  }

  Serial.println(F("UNKNOWN COMMAND"));
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  stopRobot();
  Serial.println(F("ROMI CONTROLLER READY"));
}

void loop() {

  // Read incoming serial commands
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\r') continue;

    if (c == '\n') {
      input[inputIndex] = '\0';
      processCommand(input);
      inputIndex = 0;
    }
    else if (inputIndex < sizeof(input) - 1) {
      input[inputIndex++] = c;
    }
    else {
      inputIndex = 0;
      Serial.println(F("ERROR: COMMAND TOO LONG"));
    }
  }

  // Automatically stop if commands stop arriving
  if ((targetLeftRPM != 0 || targetRightRPM != 0) &&
      millis() - lastCommandTime > TIMEOUT_MS) {

    stopRobot();
    Serial.println(F("TIMEOUT: ROBOT STOPPED"));
  }

  // Temporary indicator until motors are connected
  digitalWrite(LED_BUILTIN,
    (targetLeftRPM != 0 || targetRightRPM != 0)
    ? HIGH : LOW);
}
