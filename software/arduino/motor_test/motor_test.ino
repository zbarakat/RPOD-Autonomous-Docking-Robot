/* RPOD standalone Nano motor bench test — RECONSTRUCTED FROM CHAT.
 * IMPORTANT: This is NOT claimed to be identical to the sketch last flashed.
 * Pololu Romi #3543 DIR/PWM two-channel motor board.
 * Verify every physical wire, power rail, and polarity before energizing.
 * Wheels must be lifted. Motor board may receive motor power independently
 * of the Nano USB. Avoid VREG/USB 5V backfeeding.
 *
 * L = robot turns LEFT (right wheel only)
 * R = robot turns RIGHT (left wheel only)
 * F = both motors at low PWM; S = stop.
 * A command runs 350 ms and then automatically stops.
 * Future Arduino code should add a real deadman/watchdog to all modes.
 */
const int L_DIR = 7;
const int L_PWM = 5;
const int R_DIR = 9;
const int R_PWM = 6;
const int TEST_PWM = 50;
const unsigned long TEST_MS = 350;

void stopMotors() {
  analogWrite(L_PWM, 0);
  analogWrite(R_PWM, 0);
}

void setup() {
  digitalWrite(L_PWM, LOW);
  digitalWrite(R_PWM, LOW);
  digitalWrite(L_DIR, LOW);
  digitalWrite(R_DIR, LOW);
  pinMode(L_PWM, OUTPUT);
  pinMode(R_PWM, OUTPUT);
  pinMode(L_DIR, OUTPUT);
  pinMode(R_DIR, OUTPUT);
  stopMotors();
  Serial.begin(115200);
  Serial.println("RPOD bench motor test (reconstructed)");
  Serial.println("L=robot left, R=robot right, F=both, S=stop");
}

void loop() {
  if (!Serial.available()) return;
  const char command = Serial.read();
  if (command == '\r' || command == '\n') return;
  stopMotors();
  switch (command) {
    case 'L': case 'l':
      digitalWrite(R_DIR, LOW);
      analogWrite(R_PWM, TEST_PWM);
      break;
    case 'R': case 'r':
      digitalWrite(L_DIR, LOW);
      analogWrite(L_PWM, TEST_PWM);
      break;
    case 'F': case 'f':
      digitalWrite(L_DIR, LOW);
      digitalWrite(R_DIR, LOW);
      analogWrite(L_PWM, TEST_PWM);
      analogWrite(R_PWM, TEST_PWM);
      break;
    case 'S': case 's':
      Serial.println("Stopped");
      return;
    default:
      Serial.println("Unknown command");
      return;
  }
  delay(TEST_MS);
  stopMotors();
  Serial.println("Test complete; motors stopped");
}
