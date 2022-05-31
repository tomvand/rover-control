// Motor definitions
#define M1_PWM 5
#define M1_DIR 4
#define M2_PWM 6
#define M2_DIR 7

#define WATCHDOG_PERIOD_MS 500


union xint8_t {
  uint8_t u;
  int8_t  s;
};


static struct rover_t {
  union xint8_t cmd[10];  // Extra space for invalid characters
  unsigned long watchdog_time;
} rover;


static void apply_command(int8_t left, int8_t right) {
  digitalWrite(M1_DIR, left < 0);
  digitalWrite(M2_DIR, right >= 0);
  analogWrite(M1_PWM, abs(left));
  analogWrite(M2_PWM, abs(right));
}


void setup() {
  rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS;
  Serial.begin(9600);
}

void loop() {
  // Check serial data available
  if (Serial.available() >= 3) {
    int n = Serial.readBytesUntil(-128, (uint8_t*)rover.cmd, sizeof(rover.cmd));
    if (n == 2) {
      // Valid command
      Serial.print("Left command: ");
      Serial.print(rover.cmd[0].s);
      Serial.print(", right command: ");
      Serial.println(rover.cmd[1].s);
      apply_command(rover.cmd[0].s, rover.cmd[1].s);
      rover.watchdog_time = millis() + WATCHDOG_PERIOD_MS; 
    } else {
      // Invalid command length
      Serial.print("Invalid command length: ");
      Serial.println(n);
    }
  } else {
    if (millis() > rover.watchdog_time) {
      apply_command(0, 0);
      Serial.println("Watchdog time exceeded!");
    }
  }
}
